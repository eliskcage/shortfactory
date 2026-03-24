/**
 * CORTEX Supercharge Engine — WebGL art display + distributed brain computing
 * Fullscreen art screensaver with shader effects (GPU) and brain WebWorker (CPU)
 */

const Supercharge = (function() {
    // ─── Config ──────────────────────────────────────────────────
    const IMAGE_DURATION = 10000;       // ms between images
    const CROSSFADE_DURATION = 2000;    // ms for transitions
    const SYNC_INTERVAL = 30000;        // ms between server syncs
    const CHUNK_INTERVAL = 120000;      // ms between brain chunk refreshes (2min)
    const GPU_CREDIT_INTERVAL = 1000;   // 1 credit per second of GPU rendering
    const API_URL = '/screensaver/screensaver_api.php';

    // ─── State ───────────────────────────────────────────────────
    let canvas = null;
    let gl = null;
    let pipeline = null;
    let worker = null;
    let running = false;
    let startTime = 0;
    let gpuCreditsAccum = 0;

    // Image state
    let gallery = null;
    let activeImages = [];
    let currentImageIdx = 0;
    let currentTexture = null;
    let nextTexture = null;
    let imageTimer = null;
    let preloadQueue = [];

    // Crossfade state
    let crossfading = false;
    let crossfadeStart = 0;

    // Results buffer
    let pendingResults = [];
    let totalTasksCompleted = 0;
    let syncTimer = null;
    let chunkTimer = null;
    let gpuTimer = null;

    // Selected modes
    let selectedModes = [];

    // HUD elements
    let hudEl = null;

    // GPU intensity slider
    const GPU_INTENSITY_KEY = 'sc_gpu_intensity';
    let gpuIntensity = parseFloat(localStorage.getItem(GPU_INTENSITY_KEY)) || 1.0;

    // Swarm sidebar
    let swarmData = null;
    let swarmTimer = null;
    let swarmOpen = false;

    // API Vault
    const API_VAULT_KEY = 'sf_api_vault';

    // Flow visualization
    let flowParticles = [];
    let flowAnimId = null;
    let flowCtx = null;
    let flowFrame = 0;

    // Missions + Whistle training + Compute nodes
    const WHISTLE_INTERPS_KEY = 'sc_whistle_interpretations';
    const COMPUTE_NODES_KEY = 'sc_compute_nodes';
    let oracleGuideOpen = false;

    // ─── Satoshi Cipher (Vigenere ASCII 32-126) ────────────────
    const SatoshiCipher = {
        MAX: 95,
        charToVal: function(c) {
            var code = c.charCodeAt(0);
            if (code < 32 || code > 126) return -1;
            return code - 32 + 1;
        },
        valToChar: function(v) {
            if (v < 1 || v > 95) return '?';
            return String.fromCharCode(v + 32 - 1);
        },
        encrypt: function(text, password) {
            if (!password || !text) return text;
            var self = this;
            var passVals = Array.from(password).map(function(c) {
                var pv = self.charToVal(c); return pv < 1 ? 1 : pv;
            });
            return Array.from(text).map(function(ch, i) {
                var v = self.charToVal(ch);
                if (v < 1) return ch;
                return self.valToChar(((v - 1 + passVals[i % passVals.length]) % 95) + 1);
            }).join('');
        },
        decrypt: function(text, password) {
            if (!password || !text) return text;
            var self = this;
            var passVals = Array.from(password).map(function(c) {
                var pv = self.charToVal(c); return pv < 1 ? 1 : pv;
            });
            return Array.from(text).map(function(ch, i) {
                var v = self.charToVal(ch);
                if (v < 1) return ch;
                return self.valToChar(((v - 1 - passVals[i % passVals.length] + 190) % 95) + 1);
            }).join('');
        }
    };

    // ─── Vidman-style Motion System ─────────────────────────────
    const MOTION = {
        breathRate: 1.2,    breathAmp: 0.12,
        shakeX: 3,          shakeY: 2,
        shakeX2: 2,         shakeY2: 3,
        jitterSpeed: 30,    jitterAmp: 0.4,
        zoomBase: 108,      zoomMin: 104,    zoomMax: 116,
        zoomDrift: 0.008,   zoomChance: 0.002,
        contrastChance: 0.004,  contrastMin: -10,  contrastMax: 20,
        polaroidMin: 6000,  polaroidMax: 14000,
    };
    let breathPhase = 0;
    let zoomTarget = MOTION.zoomBase;
    let baseZoom = MOTION.zoomBase;
    let lastPolaroidTime = 0;
    let nsfwBlurActive = false;
    let containerEl = null;

    // ─── NSFW rank threshold ────────────────────────────────────
    const NSFW_RANK_MIN = 5000;  // CORPORAL level

    // Image aspect ratio for cover-fit
    let currentImageSize = [1920, 1080];

    // ─── Init ────────────────────────────────────────────────────
    function init(containerSelector, modes) {
        selectedModes = modes || ['cortex'];

        // Init player
        CortexPlayer.init();

        // Create fullscreen canvas
        const container = document.querySelector(containerSelector);
        if (!container) return false;
        containerEl = container;

        canvas = document.createElement('canvas');
        canvas.id = 'sc-canvas';
        canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;z-index:1;';
        container.appendChild(canvas);

        // Init WebGL
        gl = canvas.getContext('webgl', { alpha: false, antialias: false, preserveDrawingBuffer: true });
        if (!gl) {
            console.error('[SC] WebGL not supported');
            return false;
        }

        resize();
        pipeline = CortexShaders.initPipeline(gl);

        // Create HUD
        createHUD(container);

        // Load gallery
        loadGallery();

        // Start brain worker
        startWorker();

        // Event listeners
        window.addEventListener('resize', resize);

        // Start ambient audio
        initAudio();

        return true;
    }

    function resize() {
        if (!canvas) return;
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        if (gl && pipeline) {
            CortexShaders.resizePipeline(gl, pipeline, canvas.width, canvas.height);
        }
    }

    // ─── Gallery ─────────────────────────────────────────────────
    function loadGallery() {
        console.log('[SC] Loading gallery... modes:', selectedModes);
        fetch('/screensaver/gallery.json?t=' + Date.now())
            .then(r => r.json())
            .then(data => {
                gallery = data;
                console.log('[SC] Gallery loaded. Categories:', Object.keys(data.categories || {}));
                buildImageList();
                console.log('[SC] Active images:', activeImages.length, activeImages.slice(0,2).map(i => i.url));
                if (activeImages.length > 0) {
                    loadImage(0);
                } else {
                    console.warn('[SC] No images found for modes:', selectedModes);
                    usePlaceholder();
                }
            })
            .catch(err => {
                console.error('[SC] Gallery load failed:', err);
                usePlaceholder();
            });
    }

    function buildImageList() {
        activeImages = [];
        if (!gallery || !gallery.categories) return;

        for (const mode of selectedModes) {
            const cat = gallery.categories[mode];
            if (cat && cat.images) {
                for (const img of cat.images) {
                    activeImages.push({ ...img, category: mode });
                }
            }
        }

        // Fallback: if selected modes had no images, pull from lilleth
        if (activeImages.length === 0 && gallery.categories.lilleth && gallery.categories.lilleth.images.length > 0) {
            console.log('[SC] No images in selected modes, falling back to lilleth');
            for (const img of gallery.categories.lilleth.images) {
                activeImages.push({ ...img, category: 'lilleth' });
            }
        }

        // Shuffle
        for (let i = activeImages.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [activeImages[i], activeImages[j]] = [activeImages[j], activeImages[i]];
        }
    }

    function loadImage(index) {
        if (!activeImages.length) return;
        currentImageIdx = index % activeImages.length;
        const imgData = activeImages[currentImageIdx];

        const img = new Image();
        // img.crossOrigin = 'anonymous'; // same-origin, not needed
        img.onload = () => {
            console.log('[SC] Image loaded:', imgData.url, img.width + 'x' + img.height);
            if (currentTexture) gl.deleteTexture(currentTexture);
            currentImageSize = [img.width, img.height];
            currentTexture = CortexShaders.createImageTexture(gl, img);
            updateNsfwBlur();
            if (!running) start();
            preloadNext();
        };
        img.onerror = (e) => {
            console.error('[SC] Image FAILED:', imgData.url, e);
            // Skip broken image
            currentImageIdx = (currentImageIdx + 1) % activeImages.length;
            if (activeImages.length > 1) loadImage(currentImageIdx);
            else usePlaceholder();
        };
        console.log('[SC] Loading image:', imgData.url);
        img.src = imgData.url;
    }

    function preloadNext() {
        if (!activeImages.length) return;
        const nextIdx = (currentImageIdx + 1) % activeImages.length;
        const imgData = activeImages[nextIdx];

        const img = new Image();
        // img.crossOrigin = 'anonymous'; // same-origin, not needed
        img.onload = () => {
            nextTexture = CortexShaders.createImageTexture(gl, img);
        };
        img.src = imgData.url;
    }

    function usePlaceholder() {
        // Create a 1920x1080 gradient canvas as placeholder
        const c = document.createElement('canvas');
        c.width = 1920; c.height = 1080;
        const ctx = c.getContext('2d');

        const grad = ctx.createLinearGradient(0, 0, 1920, 1080);
        grad.addColorStop(0, '#0a0a1a');
        grad.addColorStop(0.3, '#1a0a2e');
        grad.addColorStop(0.6, '#0a1a2e');
        grad.addColorStop(1, '#050510');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 1920, 1080);

        // Add "CORTEX" text
        ctx.fillStyle = '#00ccff';
        ctx.font = 'bold 120px Orbitron, monospace';
        ctx.textAlign = 'center';
        ctx.globalAlpha = 0.15;
        ctx.fillText('CORTEX', 960, 560);
        ctx.globalAlpha = 1;

        currentTexture = CortexShaders.createImageTexture(gl, c);
        activeImages = [{ url: '', category: 'cortex', title: 'Neural Placeholder', shader: 'bloom' }];
        if (!running) start();
    }

    function advanceImage() {
        if (!activeImages.length) return;

        if (nextTexture) {
            crossfading = true;
            crossfadeStart = performance.now();

            // After crossfade, swap textures
            setTimeout(() => {
                if (currentTexture) gl.deleteTexture(currentTexture);
                currentTexture = nextTexture;
                nextTexture = null;
                crossfading = false;
                currentImageIdx = (currentImageIdx + 1) % activeImages.length;
                updateNsfwBlur();
                preloadNext();
            }, CROSSFADE_DURATION);
        } else {
            currentImageIdx = (currentImageIdx + 1) % activeImages.length;
            loadImage(currentImageIdx);
        }
    }

    // ─── Render Loop ─────────────────────────────────────────────
    function start() {
        if (running) return;
        running = true;
        startTime = performance.now();

        // Image cycling
        imageTimer = setInterval(advanceImage, IMAGE_DURATION);

        // Server sync
        syncTimer = setInterval(syncResults, SYNC_INTERVAL);

        // Brain chunk refresh
        chunkTimer = setInterval(requestChunk, CHUNK_INTERVAL);

        // GPU credits (scaled by intensity: higher power = more credits)
        gpuTimer = setInterval(() => {
            var creditsThisTick = Math.max(1, Math.round(gpuIntensity));
            CortexPlayer.addCredits(creditsThisTick, 'gpu');
            gpuCreditsAccum += creditsThisTick;
        }, GPU_CREDIT_INTERVAL);

        // Swarm polling
        swarmTimer = setInterval(fetchSwarm, 30000);
        fetchSwarm();

        requestAnimationFrame(renderFrame);
    }

    function stop() {
        running = false;
        clearInterval(imageTimer);
        clearInterval(syncTimer);
        clearInterval(chunkTimer);
        clearInterval(gpuTimer);
        clearInterval(swarmTimer);

        // Final sync
        syncResults();

        // Stop worker
        if (worker) {
            worker.postMessage({ type: 'stop' });
        }
    }

    function renderFrame(timestamp) {
        if (!running) return;

        const time = (timestamp - startTime) / 1000;

        if (gl && pipeline && currentTexture) {
            // Get shader pipeline for current image category
            const imgData = activeImages[currentImageIdx] || {};
            const category = imgData.category || 'cortex';
            const shaderPipeline = CortexShaders.PIPELINES[category] || CortexShaders.PIPELINES.cortex;
            const tint = CortexShaders.TINTS[category] || CortexShaders.TINTS.cortex;

            gl.viewport(0, 0, canvas.width, canvas.height);

            // Compute cover-fit scale (like CSS object-fit: cover)
            var canvasAspect = canvas.width / canvas.height;
            var imgAspect = currentImageSize[0] / currentImageSize[1];
            var coverScale;
            if (imgAspect > canvasAspect) {
                // Image wider than canvas — crop sides
                coverScale = [canvasAspect / imgAspect, 1.0];
            } else {
                // Image taller than canvas — crop top/bottom
                coverScale = [1.0, imgAspect / canvasAspect];
            }

            // Render through shader pipeline (intensity from GPU power slider)
            CortexShaders.renderPipeline(gl, pipeline, currentTexture, shaderPipeline, time, gpuIntensity, tint, coverScale);
        }

        // ── Vidman motion on canvas ──
        applyMotion(time, timestamp);

        // Update HUD
        if (hudEl && timestamp % 500 < 17) {
            updateHUD();
        }

        requestAnimationFrame(renderFrame);
    }

    // ─── Motion: camera shake + zoom drift + breathing + polaroid ──
    function applyMotion(time, timestamp) {
        if (!canvas) return;
        breathPhase += 0.016;

        // Camera shake (two-layer sinusoid)
        const breathShake = Math.sin(breathPhase * MOTION.breathRate) * 1.2;
        const swayX = Math.sin(time * 1.2) * MOTION.shakeX + Math.cos(time * 2.1) * MOTION.shakeX2 + breathShake;
        const swayY = Math.cos(time * 1.6) * MOTION.shakeY + Math.sin(time * 2.3) * MOTION.shakeY2 + breathShake * 0.7;

        // Micro-jitter
        const jX = Math.sin(time * MOTION.jitterSpeed) * MOTION.jitterAmp + (Math.random() - 0.5) * 0.3;
        const jY = Math.cos(time * (MOTION.jitterSpeed - 5)) * MOTION.jitterAmp + (Math.random() - 0.5) * 0.3;

        // Zoom drift
        if (Math.random() < MOTION.zoomChance) {
            zoomTarget = MOTION.zoomMin + Math.random() * (MOTION.zoomMax - MOTION.zoomMin);
        }
        baseZoom += (zoomTarget - baseZoom) * MOTION.zoomDrift;

        const tx = swayX + jX;
        const ty = swayY + jY;
        const scale = baseZoom / 100;
        canvas.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';

        // Breathing darkness overlay
        const breathCycle = Math.sin(breathPhase * MOTION.breathRate) * 0.5 + 0.5;
        const breathEl = document.getElementById('sc-breath');
        if (breathEl) breathEl.style.opacity = breathCycle * MOTION.breathAmp;

        // Random contrast flicker on canvas
        if (Math.random() < MOTION.contrastChance) {
            const cv = MOTION.contrastMin + Math.random() * (MOTION.contrastMax - MOTION.contrastMin);
            canvas.style.filter = 'contrast(' + (1 + cv / 100) + ') brightness(' + (1 + cv / 200) + ')';
        }

        // Polaroid drops
        if (timestamp - lastPolaroidTime > MOTION.polaroidMin + Math.random() * (MOTION.polaroidMax - MOTION.polaroidMin)) {
            dropPolaroid();
            lastPolaroidTime = timestamp;
        }
    }

    // ─── Polaroid snapshot drop ─────────────────────────────────
    function dropPolaroid() {
        if (!canvas) return;
        try {
            var c = document.createElement('canvas');
            var ctx = c.getContext('2d');
            c.width = 200; c.height = 200;
            ctx.drawImage(canvas, 0, 0, 200, 200);

            var wrap = document.createElement('div');
            wrap.style.cssText = 'position:fixed;pointer-events:none;z-index:5;width:140px;border:6px solid #fff;border-bottom:32px solid #fff;box-shadow:0 4px 20px rgba(0,0,0,0.6);transition:top 1.3s ease-out,opacity 4s linear;top:-220px;left:' + (Math.random() * 70) + 'vw;transform:rotate(' + (Math.random() * 20 - 10) + 'deg);opacity:1;';
            c.style.cssText = 'width:100%;display:block;';
            wrap.appendChild(c);

            var label = document.createElement('span');
            label.textContent = 'SHORTF\u25B2CTORY';
            label.style.cssText = 'position:absolute;bottom:8px;left:0;right:0;text-align:center;font-family:Orbitron,monospace;font-size:7px;color:#333;letter-spacing:2px;';
            wrap.appendChild(label);
            (containerEl || document.body).appendChild(wrap);

            requestAnimationFrame(function() {
                wrap.style.top = (50 + Math.random() * 25) + 'vh';
            });
            setTimeout(function() { wrap.style.opacity = 0; }, 4000);
            setTimeout(function() { wrap.remove(); }, 9000);
        } catch(e) {}
    }

    // ─── NSFW blur management ───────────────────────────────────
    function updateNsfwBlur() {
        const imgData = activeImages[currentImageIdx] || {};
        const stats = CortexPlayer.getStats();
        const blurEl = document.getElementById('sc-nsfw-blur');
        if (!blurEl) return;

        if (imgData.nsfw && stats.credits < NSFW_RANK_MIN) {
            blurEl.style.opacity = '1';
            nsfwBlurActive = true;
        } else {
            blurEl.style.opacity = '0';
            nsfwBlurActive = false;
        }
    }

    // ─── Ambient audio ──────────────────────────────────────────
    function initAudio() {
        var audio = document.getElementById('sc-ambient');
        if (!audio) return;
        audio.volume = 0.3;
        audio.play().catch(function() {
            // Autoplay blocked — play on first user interaction
            document.addEventListener('click', function tryPlay() {
                audio.play().catch(function(){});
                document.removeEventListener('click', tryPlay);
            }, { once: true });
        });
    }

    // ─── Brain Worker ────────────────────────────────────────────
    function startWorker() {
        try {
            worker = new Worker('/screensaver/brain-worker.js');

            worker.onmessage = function(e) {
                const msg = e.data;

                if (msg.type === 'ready') {
                    requestChunk();
                }

                if (msg.type === 'results') {
                    pendingResults = pendingResults.concat(msg.data);
                    totalTasksCompleted += msg.count;

                    // Award credits: 10 per task
                    CortexPlayer.addCredits(msg.count * 10, 'brain_task');
                }
            };

            worker.onerror = function(err) {
                console.error('[SC] Worker error:', err.message);
            };
        } catch(e) {
            console.error('[SC] Failed to start worker:', e);
        }
    }

    function requestChunk() {
        fetch(API_URL + '?action=brain-chunk')
            .then(r => r.json())
            .then(data => {
                if (data.nodes && worker) {
                    worker.postMessage({ type: 'chunk', data: data });
                }
            })
            .catch(() => {});
    }

    function syncResults() {
        if (!pendingResults.length && gpuCreditsAccum === 0) return;

        const stats = CortexPlayer.getStats();
        const body = {
            player_id: stats.id,
            results: pendingResults.slice(0, 50),
            gpu_seconds: gpuCreditsAccum,
        };

        fetch(API_URL + '?action=submit-results', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        })
        .then(r => r.json())
        .then(data => {
            if (data.ok) {
                pendingResults = pendingResults.slice(50);
                gpuCreditsAccum = 0;
            }
        })
        .catch(() => {});

        // Also sync player
        CortexPlayer.syncToServer(API_URL);

        // Heartbeat for swarm tracking
        fetch(API_URL + '?action=heartbeat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                player_id: stats.id,
                gpu_seconds: stats.gpuSeconds || 0,
                brain_tasks: stats.brainTasks || 0,
                credits: stats.credits || 0
            })
        }).catch(() => {});
    }

    // ─── HUD ─────────────────────────────────────────────────────
    function createHUD(container) {
        hudEl = document.createElement('div');
        hudEl.id = 'sc-hud';
        hudEl.style.cssText = 'position:absolute;top:0;left:0;right:0;bottom:0;z-index:10;pointer-events:none;font-family:Orbitron,\'Courier New\',monospace;color:#fff;';

        hudEl.innerHTML =
            // ── TOP BAR ──
            '<div id="sc-hud-top" style="position:absolute;top:20px;left:20px;right:20px;display:flex;justify-content:space-between;align-items:flex-start;">' +
                '<div id="sc-rank-badge" style="background:rgba(0,0,0,0.7);border:1px solid #333;padding:10px 16px;border-radius:8px;font-size:12px;line-height:1.6;">' +
                    '<div id="sc-rank-name" style="font-size:16px;font-weight:bold;letter-spacing:2px;">RECRUIT</div>' +
                    '<div id="sc-credits" style="color:#daa520;">0 CREDITS</div>' +
                    '<div id="sc-progress-bar" style="width:150px;height:4px;background:#222;border-radius:2px;margin-top:4px;">' +
                        '<div id="sc-progress-fill" style="height:100%;background:#daa520;border-radius:2px;width:0%;"></div>' +
                    '</div>' +
                '</div>' +
                '<div id="sc-task-counter" style="background:rgba(0,0,0,0.7);border:1px solid #333;padding:10px 16px;border-radius:8px;font-size:12px;text-align:right;">' +
                    '<div style="color:#00ccff;">BRAIN TASKS</div>' +
                    '<div id="sc-task-count" style="font-size:20px;font-weight:bold;">0</div>' +
                    '<div id="sc-gpu-info" style="font-size:7px;color:#555;margin-top:4px;letter-spacing:1px;"></div>' +
                '</div>' +
            '</div>' +

            // ── BOTTOM BAR ──
            '<div id="sc-hud-bottom" style="position:absolute;bottom:20px;left:20px;right:20px;display:flex;justify-content:space-between;align-items:flex-end;">' +
                '<div style="display:flex;flex-direction:column;gap:4px;">' +
                    '<div id="sc-image-title" style="background:rgba(0,0,0,0.5);padding:6px 12px;border-radius:4px;font-size:11px;color:#888;"></div>' +
                    '<div id="sc-swarm-badge" style="background:rgba(0,0,0,0.5);padding:4px 12px;border-radius:4px;font-size:8px;color:#76b900;letter-spacing:1px;">SWARM: COMPUTING | YOU GIVE = YOU GET | MERIT-BASED GPU NETWORK</div>' +
                '</div>' +
                '<div style="display:flex;gap:10px;">' +
                    '<button id="sc-moviestar-btn" style="pointer-events:auto;cursor:pointer;background:rgba(218,165,32,0.9);color:#000;border:none;padding:10px 18px;border-radius:6px;font-family:Orbitron,monospace;font-size:11px;font-weight:bold;letter-spacing:1px;" onclick="Supercharge.toggleGreenscreen()">MOVIE STAR</button>' +
                    '<button id="sc-exit-btn" style="pointer-events:auto;cursor:pointer;background:rgba(255,255,255,0.1);color:#fff;border:1px solid #333;padding:10px 18px;border-radius:6px;font-family:Orbitron,monospace;font-size:11px;letter-spacing:1px;" onclick="Supercharge.exit()">EXIT</button>' +
                '</div>' +
            '</div>' +

            // ── GPU POWER SLIDER (right edge) ──
            '<div id="sc-power-slider" style="position:absolute;right:20px;top:50%;transform:translateY(-50%);width:60px;background:rgba(0,0,0,0.8);border:1px solid #333;border-radius:8px;padding:12px 8px;display:flex;flex-direction:column;align-items:center;pointer-events:auto;gap:6px;">' +
                '<div style="font-size:7px;letter-spacing:2px;color:#76b900;text-align:center;">GPU<br>POWER</div>' +
                '<div id="sc-power-value" style="font-size:14px;font-weight:900;color:#76b900;">100%</div>' +
                '<input type="range" id="sc-power-range" min="10" max="200" value="' + Math.round(gpuIntensity * 100) + '" orient="vertical" style="-webkit-appearance:slider-vertical;writing-mode:bt-lr;width:30px;height:140px;cursor:pointer;accent-color:#76b900;">' +
                '<div id="sc-power-rate" style="font-size:7px;color:#555;text-align:center;">1x CREDITS</div>' +
            '</div>' +

            // ── SWARM TAB (left edge) ──
            '<div id="sc-swarm-tab" style="position:absolute;left:0;top:50%;transform:translateY(-50%);background:rgba(0,0,0,0.8);border:1px solid #333;border-left:none;border-radius:0 8px 8px 0;padding:8px 6px;cursor:pointer;pointer-events:auto;font-size:8px;color:#76b900;letter-spacing:2px;writing-mode:vertical-rl;text-orientation:mixed;" onclick="Supercharge.toggleSwarm()">S W A R M</div>' +

            // ── SWARM PANEL (slides from left) ──
            '<div id="sc-swarm-panel" style="position:absolute;left:0;top:0;bottom:0;width:300px;background:rgba(5,5,16,0.96);border-right:1px solid #333;transform:translateX(-100%);transition:transform 0.3s ease;pointer-events:auto;overflow-y:auto;padding:16px;font-family:\'Courier New\',monospace;font-size:11px;z-index:5;">' +
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">' +
                    '<span style="font-family:Orbitron,monospace;font-size:12px;color:#76b900;letter-spacing:3px;font-weight:900;">SWARM</span>' +
                    '<span style="cursor:pointer;color:#666;font-size:16px;" onclick="Supercharge.toggleSwarm()">&#10005;</span>' +
                '</div>' +
                '<div id="sc-swarm-stats" style="color:#888;line-height:2;"></div>' +
                '<div id="sc-swarm-roadmap" style="margin-top:16px;"></div>' +
                '<div id="sc-swarm-leaderboard" style="margin-top:16px;"></div>' +
                '<div id="sc-swarm-missions" style="margin-top:16px;"></div>' +
                '<div id="sc-swarm-whistle" style="margin-top:16px;"></div>' +
                '<div id="sc-swarm-api-health" style="margin-top:16px;"></div>' +
                '<canvas id="sc-flow-canvas" width="268" height="400" style="margin:16px 0;border:1px solid #1a1a2a;border-radius:6px;background:#050510;display:block;width:100%;"></canvas>' +
                '<div id="sc-wealth-meter" style="text-align:center;margin-top:4px;"></div>' +
            '</div>';

        container.appendChild(hudEl);

        // Wire up GPU power slider
        var slider = document.getElementById('sc-power-range');
        if (slider) {
            slider.value = Math.round(gpuIntensity * 100);
            var label = document.getElementById('sc-power-value');
            var rate = document.getElementById('sc-power-rate');
            if (label) {
                label.textContent = slider.value + '%';
                label.style.color = gpuIntensity > 1.5 ? '#ff4444' : gpuIntensity > 1.0 ? '#daa520' : '#76b900';
            }
            slider.addEventListener('input', function() {
                gpuIntensity = parseInt(this.value) / 100;
                localStorage.setItem(GPU_INTENSITY_KEY, gpuIntensity.toString());
                if (label) {
                    label.textContent = this.value + '%';
                    label.style.color = gpuIntensity > 1.5 ? '#ff4444' : gpuIntensity > 1.0 ? '#daa520' : '#76b900';
                }
                if (rate) {
                    var mult = Math.max(1, Math.round(gpuIntensity));
                    rate.textContent = mult + 'x CREDITS';
                    rate.style.color = mult > 1 ? '#daa520' : '#555';
                }
            });
        }
    }

    // ─── Swarm Sidebar ─────────────────────────────────────────
    function toggleSwarm() {
        swarmOpen = !swarmOpen;
        var panel = document.getElementById('sc-swarm-panel');
        var tab = document.getElementById('sc-swarm-tab');
        if (panel) panel.style.transform = swarmOpen ? 'translateX(0)' : 'translateX(-100%)';
        if (tab) tab.style.opacity = swarmOpen ? '0' : '1';
        if (swarmOpen && !swarmData) fetchSwarm();
        if (swarmOpen) startFlowAnimation();
        else stopFlowAnimation();
    }

    function fetchSwarm() {
        fetch(API_URL + '?action=swarm')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.ok) { swarmData = data; renderSwarmPanel(data); }
            })
            .catch(function() {});
    }

    function renderSwarmPanel(data) {
        // ── Network Stats ──
        var statsEl = document.getElementById('sc-swarm-stats');
        if (statsEl) {
            statsEl.innerHTML =
                '<div style="color:#76b900;font-family:Orbitron,monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">NETWORK STATUS</div>' +
                '<div><span style="color:#00ff88;">' + data.active + '</span> NODES ONLINE</div>' +
                '<div><span style="color:#daa520;">' + data.total_devices + '</span> TOTAL DEVICES</div>' +
                '<div><span style="color:#00ccff;">' + Math.round(data.total_gpu_seconds / 3600) + '</span> GPU HOURS</div>' +
                '<div><span style="color:#ff8c00;">' + data.total_brain_tasks + '</span> BRAIN TASKS</div>' +
                '<div><span style="color:#76b900;">' + data.total_credits.toLocaleString() + '</span> TOTAL CREDITS</div>';
        }

        // ── Rank Roadmap ──
        var roadmapEl = document.getElementById('sc-swarm-roadmap');
        if (roadmapEl) {
            var stats = CortexPlayer.getStats();
            var ranks = [
                { name: 'PRIVATE', min: 1000, color: '#888', unlock: 'Full colour site + media' },
                { name: 'CORPORAL', min: 5000, color: '#daa520', unlock: 'Exclusive content + Cortex chat' },
                { name: 'SERGEANT', min: 10000, color: '#22c55e', unlock: 'Your own AI website on SF' },
                { name: 'VETERAN', min: 20000, color: '#00ccff', unlock: 'Custom domain + SF email' },
                { name: 'COMMANDER', min: 50000, color: '#8844ff', unlock: 'AI auto-email + GPU priority' },
                { name: 'LEGENDARY', min: 100000, color: '#ff4444', unlock: 'Fight PPV + Monero payouts' },
                { name: 'GIGACHAD', min: 500000, color: '#ff0040', unlock: 'Arena booking — main event' }
            ];
            var html = '<div style="color:#daa520;font-family:Orbitron,monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">RANK ROADMAP</div>';
            for (var i = 0; i < ranks.length; i++) {
                var r = ranks[i];
                var achieved = stats.credits >= r.min;
                html += '<div style="display:flex;gap:8px;padding:4px 0;border-bottom:1px solid #111;opacity:' + (achieved ? '1' : '0.4') + ';">' +
                    '<span style="color:' + r.color + ';font-family:Orbitron,monospace;font-size:8px;font-weight:900;min-width:75px;">' + (achieved ? '&#10003; ' : '') + r.name + '</span>' +
                    '<span style="color:#666;font-size:9px;">' + r.unlock + '</span></div>';
            }
            roadmapEl.innerHTML = html;
        }

        // ── Leaderboard ──
        var lbEl = document.getElementById('sc-swarm-leaderboard');
        if (lbEl && data.devices && data.devices.length > 0) {
            var html = '<div style="color:#00ccff;font-family:Orbitron,monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">LEADERBOARD</div>';
            var myId = CortexPlayer.getStats().id;
            for (var i = 0; i < Math.min(8, data.devices.length); i++) {
                var d = data.devices[i];
                var isMe = myId.indexOf(d.id) === 0;
                html += '<div style="display:flex;justify-content:space-between;padding:3px 0;' + (isMe ? 'color:#daa520;font-weight:bold;' : 'color:#666;') + '">' +
                    '<span>#' + (i + 1) + ' ' + d.id + (isMe ? ' (YOU)' : '') + '</span>' +
                    '<span>' + d.credits.toLocaleString() + '</span></div>';
            }
            lbEl.innerHTML = html;
        }

        // ── Missions Board ──
        renderMissions();

        // ── Whistle Training ──
        renderWhistleTraining();

        // ── API Vault + Health ──
        renderApiVault();

        // ── GPU Flow Visualization ──
        initFlowCanvas(data);
        if (swarmOpen) startFlowAnimation();
    }

    // ─── API Vault ─────────────────────────────────────────────
    function renderApiVault() {
        var vaultEl = document.getElementById('sc-swarm-api-health');
        if (!vaultEl) return;

        var vault = [];
        try { vault = JSON.parse(localStorage.getItem(API_VAULT_KEY)) || []; } catch(e) {}

        var html = '<div style="color:#ff8c00;font-family:Orbitron,monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">API VAULT</div>';

        if (vault.length > 0) {
            for (var i = 0; i < vault.length; i++) {
                var api = vault[i];
                var sc = api.status === 'active' ? '#00ff88' : api.status === 'low' ? '#ff8c00' : '#ff4444';
                html += '<div style="display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #111;">' +
                    '<div style="display:flex;align-items:center;gap:6px;">' +
                        '<div style="width:8px;height:8px;background:' + sc + ';border-radius:50%;box-shadow:0 0 4px ' + sc + ';flex-shrink:0;"></div>' +
                        '<span style="color:#ccc;font-size:10px;">' + api.label + '</span>' +
                    '</div>' +
                    '<div style="display:flex;align-items:center;gap:8px;">' +
                        '<span style="font-size:7px;color:' + sc + ';letter-spacing:1px;">' + (api.status || 'ACTIVE').toUpperCase() + '</span>' +
                        '<span style="cursor:pointer;color:#ff4444;font-size:12px;" onclick="Supercharge.removeApiKey(' + i + ')">&#10005;</span>' +
                    '</div></div>';
            }
        } else {
            html += '<div style="color:#444;font-size:10px;padding:4px 0;">No API keys donated yet</div>';
        }

        // Donation form
        html += '<div style="margin-top:14px;border-top:1px solid #222;padding-top:14px;">' +
            '<div style="color:#daa520;font-family:Orbitron,monospace;font-size:8px;letter-spacing:1px;margin-bottom:8px;">DONATE AN API KEY &nbsp; <span style="color:#76b900;">+500 CREDITS</span></div>' +
            '<input id="sc-api-key" type="password" placeholder="Paste API key (sk-...)" style="width:100%;padding:7px;background:#111;border:1px solid #333;border-radius:4px;color:#fff;font-family:monospace;font-size:10px;margin-bottom:8px;outline:none;box-sizing:border-box;">' +
            '<button onclick="Supercharge.submitApiKey()" style="width:100%;padding:9px;background:linear-gradient(135deg,#daa520,#ff8c00);color:#000;border:none;border-radius:4px;font-family:Orbitron,monospace;font-size:9px;font-weight:900;letter-spacing:2px;cursor:pointer;">ENCRYPT &amp; STORE</button>' +
            '<div style="font-size:7px;color:#444;margin-top:6px;line-height:1.5;">Satoshi encrypted with your device key.<br>Never leaves your device. We use it, you get credits.</div>' +
        '</div>';

        vaultEl.innerHTML = html;
    }

    function submitApiKey() {
        var keyEl = document.getElementById('sc-api-key');
        if (!keyEl || !keyEl.value.trim()) return;

        var rawKey = keyEl.value.trim();
        var playerId = CortexPlayer.getStats().id;

        // Auto-detect label from key prefix
        var label = rawKey.startsWith('xai-') ? 'Grok' :
                    rawKey.startsWith('sk-ant-') ? 'Anthropic' :
                    rawKey.startsWith('sk-') ? 'OpenAI' :
                    rawKey.startsWith('AIza') ? 'Google' :
                    'API Key';

        // Encrypt with Satoshi cipher
        var encrypted = SatoshiCipher.encrypt(rawKey, playerId);

        var vault = [];
        try { vault = JSON.parse(localStorage.getItem(API_VAULT_KEY)) || []; } catch(e) {}

        vault.push({
            id: 'api_' + Date.now().toString(36),
            label: label,
            encrypted: encrypted,
            status: 'active',
            created: new Date().toISOString()
        });

        localStorage.setItem(API_VAULT_KEY, JSON.stringify(vault));
        CortexPlayer.addCredits(500, 'api_donation');

        keyEl.value = '';
        renderApiVault();
    }

    function removeApiKey(index) {
        var vault = [];
        try { vault = JSON.parse(localStorage.getItem(API_VAULT_KEY)) || []; } catch(e) {}
        if (index >= 0 && index < vault.length) {
            vault.splice(index, 1);
            localStorage.setItem(API_VAULT_KEY, JSON.stringify(vault));
            renderApiVault();
        }
    }

    // ─── Missions Board ─────────────────────────────────────────
    function renderMissions() {
        var el = document.getElementById('sc-swarm-missions');
        if (!el) return;

        var stats = CortexPlayer.getStats();
        var vault = [];
        try { vault = JSON.parse(localStorage.getItem(API_VAULT_KEY)) || []; } catch(e) {}
        var nodes = [];
        try { nodes = JSON.parse(localStorage.getItem(COMPUTE_NODES_KEY)) || []; } catch(e) {}

        var missions = [
            { id: 'cortex_chat', name: 'Chat with Cortex', reward: '+10 credits/msg', rc: '#00ccff', link: '/alive/studio/', icon: '&#x1F9E0;', done: false, desc: 'Talk to the split-brain AI' },
            { id: 'whistle_train', name: 'Train ALIVE Whistles', reward: '+5 credits each', rc: '#22c55e', link: '/alive/brainstem/', icon: '&#x1F3B5;', done: false, desc: 'Teach the creature language' },
            { id: 'fund_api', name: 'Fund the API', reward: '+varies', rc: '#daa520', link: '/alive/kickstarter.html', icon: '&#x26A1;', done: false, desc: 'Direct crypto (XMR/BTC)' },
            { id: 'donate_key', name: 'Donate API Key', reward: '+500 credits', rc: '#ff8c00', link: null, icon: '&#x1F511;', done: vault.length > 0, desc: 'Encrypted, never leaves device' },
            { id: 'deploy_compute', name: 'Deploy Compute Node', reward: '+1000 credits', rc: '#8844ff', link: null, icon: '&#x1F5A5;', done: nodes.length > 0, desc: 'Oracle Always Free ARM VM' }
        ];

        var html = '<div style="color:#daa520;font-family:Orbitron,monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">MISSIONS</div>';

        for (var i = 0; i < missions.length; i++) {
            var m = missions[i];
            var sc = m.done ? '#00ff88' : '#555';
            var sl = m.done ? '&#10003; DONE' : 'AVAILABLE';
            var oc = '';
            if (m.id === 'donate_key') {
                oc = 'onclick="document.getElementById(\'sc-swarm-api-health\').scrollIntoView({behavior:\'smooth\'})"';
            } else if (m.id === 'deploy_compute') {
                oc = 'onclick="Supercharge.toggleOracleGuide()"';
            } else if (m.link) {
                oc = 'onclick="window.open(\'' + m.link + '\', \'_blank\')"';
            }

            html += '<div style="display:flex;align-items:center;gap:8px;padding:8px 6px;border-bottom:1px solid #111;cursor:pointer;" ' +
                'onmouseover="this.style.background=\'rgba(255,255,255,0.03)\'" onmouseout="this.style.background=\'none\'" ' + oc + '>' +
                '<span style="font-size:14px;flex-shrink:0;">' + m.icon + '</span>' +
                '<div style="flex:1;">' +
                    '<div style="color:#ccc;font-size:10px;font-weight:bold;">' + m.name + '</div>' +
                    '<div style="color:#555;font-size:8px;margin-top:1px;">' + m.desc + '</div>' +
                '</div>' +
                '<div style="text-align:right;flex-shrink:0;">' +
                    '<div style="font-size:8px;color:' + m.rc + ';font-family:Orbitron,monospace;font-weight:700;">' + m.reward + '</div>' +
                    '<div style="font-size:7px;color:' + sc + ';letter-spacing:1px;margin-top:2px;">' + sl + '</div>' +
                '</div>' +
            '</div>';
        }

        // Oracle Cloud Guide (collapsible)
        html += '<div id="sc-oracle-guide" style="display:' + (oracleGuideOpen ? 'block' : 'none') + ';margin-top:12px;padding:12px;background:rgba(136,68,255,0.06);border:1px solid rgba(136,68,255,0.3);border-radius:6px;">' +
            '<div style="color:#8844ff;font-family:Orbitron,monospace;font-size:8px;letter-spacing:2px;margin-bottom:10px;">DEPLOY COMPUTE NODE</div>' +
            '<div style="font-size:9px;color:#aaa;line-height:1.8;">' +
                '<div style="margin-bottom:8px;"><span style="color:#8844ff;font-weight:bold;">1.</span> Sign up at <span style="color:#00ccff;cursor:pointer;" onclick="window.open(\'https://oracle.com/cloud/free\',\'_blank\')">oracle.com/cloud/free</span> (Always Free tier)</div>' +
                '<div style="margin-bottom:8px;"><span style="color:#8844ff;font-weight:bold;">2.</span> Create ARM VM: <span style="color:#daa520;">4 OCPU, 24GB RAM</span> &#8212; free forever</div>' +
                '<div style="margin-bottom:8px;"><span style="color:#8844ff;font-weight:bold;">3.</span> SSH in and run:</div>' +
                '<div style="background:#0a0a1a;border:1px solid #333;border-radius:4px;padding:8px;margin:4px 0 8px 0;font-family:monospace;font-size:9px;color:#76b900;word-break:break-all;">curl -fsSL shortfactory.shop/swarm/install.sh | bash</div>' +
                '<div style="margin-bottom:10px;"><span style="color:#8844ff;font-weight:bold;">4.</span> Paste your node ID below:</div>' +
            '</div>' +
            '<div style="display:flex;gap:6px;">' +
                '<input id="sc-node-id" type="text" placeholder="Node ID from install script" style="flex:1;padding:7px;background:#111;border:1px solid #333;border-radius:4px;color:#fff;font-family:monospace;font-size:10px;outline:none;">' +
                '<button onclick="Supercharge.submitComputeNode()" style="padding:7px 12px;background:linear-gradient(135deg,#8844ff,#6622cc);color:#fff;border:none;border-radius:4px;font-family:Orbitron,monospace;font-size:8px;font-weight:900;letter-spacing:1px;cursor:pointer;">SUBMIT</button>' +
            '</div>' +
            '<div style="font-size:7px;color:#444;margin-top:6px;">+1000 credits when node pings our swarm.</div>' +
        '</div>';

        el.innerHTML = html;
    }

    // ─── Whistle Training ────────────────────────────────────────
    function renderWhistleTraining() {
        var el = document.getElementById('sc-swarm-whistle');
        if (!el) return;

        var interps = [];
        try { interps = JSON.parse(localStorage.getItem(WHISTLE_INTERPS_KEY)) || []; } catch(e) {}

        var html = '<div style="color:#22c55e;font-family:Orbitron,monospace;font-size:9px;letter-spacing:2px;margin-bottom:8px;">WHISTLE TRAINING <span style="color:#76b900;font-size:7px;">+5 CREDITS EACH</span></div>';
        html += '<div style="font-size:9px;color:#888;line-height:1.6;margin-bottom:10px;">Type what creature sounds could mean.<br>The brainstem picks these up for learning.</div>';

        html += '<div style="display:flex;gap:6px;margin-bottom:10px;">' +
            '<input id="sc-whistle-input" type="text" placeholder="e.g. hello, warning, come here..." ' +
            'style="flex:1;padding:7px;background:#111;border:1px solid #333;border-radius:4px;color:#fff;font-family:monospace;font-size:10px;outline:none;" ' +
            'onkeydown="if(event.key===\'Enter\')Supercharge.submitWhistle()">' +
            '<button onclick="Supercharge.submitWhistle()" style="padding:7px 12px;background:linear-gradient(135deg,#22c55e,#16a34a);color:#000;border:none;border-radius:4px;font-family:Orbitron,monospace;font-size:8px;font-weight:900;letter-spacing:1px;cursor:pointer;">SUBMIT</button>' +
        '</div>';

        if (interps.length > 0) {
            html += '<div style="font-size:7px;color:#555;letter-spacing:1px;margin-bottom:4px;">RECENT (' + interps.length + ')</div>';
            var recent = interps.slice(-8).reverse();
            for (var i = 0; i < recent.length; i++) {
                var interp = recent[i];
                var ago = getTimeAgo(interp.timestamp);
                html += '<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #0a0a1a;">' +
                    '<span style="color:#22c55e;font-size:9px;">"' + escapeHtml(interp.text) + '"</span>' +
                    '<span style="color:#444;font-size:7px;">' + ago + '</span>' +
                '</div>';
            }
        }

        el.innerHTML = html;
    }

    function getTimeAgo(ts) {
        var d = Date.now() - ts;
        if (d < 60000) return 'just now';
        if (d < 3600000) return Math.floor(d / 60000) + 'm ago';
        if (d < 86400000) return Math.floor(d / 3600000) + 'h ago';
        return Math.floor(d / 86400000) + 'd ago';
    }

    function escapeHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function updateHUD() {
        const stats = CortexPlayer.getStats();

        const rankEl = document.getElementById('sc-rank-name');
        const creditsEl = document.getElementById('sc-credits');
        const progressEl = document.getElementById('sc-progress-fill');
        const taskEl = document.getElementById('sc-task-count');
        const titleEl = document.getElementById('sc-image-title');

        if (rankEl) {
            rankEl.textContent = stats.rank;
            rankEl.style.color = stats.rankColor;
        }
        if (creditsEl) creditsEl.textContent = stats.credits.toLocaleString() + ' CREDITS';
        if (progressEl) progressEl.style.width = (stats.progress * 100) + '%';
        if (taskEl) taskEl.textContent = totalTasksCompleted;

        if (titleEl && activeImages[currentImageIdx]) {
            const img = activeImages[currentImageIdx];
            var nsfwTag = nsfwBlurActive ? ' | RANK UP TO UNLOCK' : '';
            titleEl.textContent = (img.title || '') + ' | GPU rendering | CPU computing' + nsfwTag;
        }

        // GPU info + swarm badge
        var gpuEl = document.getElementById('sc-gpu-info');
        if (gpuEl && !gpuEl._detected) {
            gpuEl._detected = true;
            var gpuName = 'GPU';
            try {
                var dbg = gl.getExtension('WEBGL_debug_renderer_info');
                if (dbg) gpuName = gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) || 'GPU';
            } catch(e) {}
            gpuEl.textContent = gpuName;
        }
    }

    // ─── Greenscreen ─────────────────────────────────────────────
    let greenscreenActive = false;

    function toggleGreenscreen() {
        if (greenscreenActive) {
            // Remove greenscreen UI
            const gs = document.getElementById('sc-greenscreen');
            if (gs) gs.remove();
            greenscreenActive = false;

            // Stop camera
            if (window._scStream) {
                window._scStream.getTracks().forEach(t => t.stop());
                window._scStream = null;
            }
        } else {
            if (typeof CortexGreenscreen !== 'undefined') {
                CortexGreenscreen.init(canvas.parentElement);
                greenscreenActive = true;
            }
        }
    }

    // ─── GPU Flow Visualization ────────────────────────────────
    var flowZones = { crypto: 34, entertain: 41, games: 25 };
    var flowWealth = 0;
    var flowWealthTarget = 0;

    function initFlowCanvas(data) {
        var c = document.getElementById('sc-flow-canvas');
        if (!c) return;
        flowCtx = c.getContext('2d');
        flowParticles = [];
        flowFrame = 0;

        // Calculate zone percentages from real data
        var stats = (typeof CortexPlayer !== 'undefined') ? CortexPlayer.getStats() : { credits: 0, gpuSeconds: 0 };
        var brainPct = Math.min(45, Math.round((data.total_brain_tasks || 0) / Math.max(1, data.total_gpu_seconds || 1) * 100 * 30));
        flowZones.entertain = Math.max(20, brainPct);
        flowZones.crypto = Math.round((100 - flowZones.entertain) * 0.55);
        flowZones.games = 100 - flowZones.crypto - flowZones.entertain;

        // Wealth from credits
        flowWealthTarget = (stats.credits || 0) * 0.002;
        flowWealth = flowWealthTarget * 0.9;

        // Render wealth meter below canvas
        updateWealthMeter(stats);
    }

    function updateWealthMeter(stats) {
        var el = document.getElementById('sc-wealth-meter');
        if (!el) return;
        var w = flowWealthTarget.toFixed(2);
        var gpuH = Math.round((stats.gpuSeconds || 0) / 3600);
        var rate = gpuH > 0 ? (flowWealthTarget / gpuH).toFixed(3) : '0.000';
        el.innerHTML =
            '<div style="font-family:Orbitron,monospace;font-size:8px;color:#76b900;letter-spacing:3px;margin-bottom:4px;">YOUR FACTORY WEALTH</div>' +
            '<div style="font-size:22px;font-weight:900;color:#daa520;text-shadow:0 0 12px rgba(218,165,32,0.4);">$' + w + '</div>' +
            '<div style="font-size:9px;color:#76b900;margin-top:2px;">&#9650; $' + rate + ' / hour</div>';
    }

    function startFlowAnimation() {
        if (flowAnimId) return;
        flowAnimId = requestAnimationFrame(animateFlow);
    }

    function stopFlowAnimation() {
        if (flowAnimId) { cancelAnimationFrame(flowAnimId); flowAnimId = null; }
    }

    function animateFlow() {
        if (!swarmOpen || !flowCtx) { flowAnimId = null; return; }
        flowFrame++;
        var ctx = flowCtx;
        var W = 268, H = 400;
        ctx.clearRect(0, 0, W, H);

        // Get rank color for flow visualization
        var playerStats = CortexPlayer.getStats();
        var rankCol = playerStats.rankColor || '#666666';

        // Layout constants
        var gpuY = 30, factY = 120, factH = 60, zoneY = 260, wealthY = 360;
        var cx = W / 2;
        var zoneXs = [W * 0.17, cx, W * 0.83];
        var zoneColors = ['#ff8c00', '#ff2244', '#4488ff'];
        var zoneNames = ['CRYPTO', 'ENTERTAIN', 'GAMES'];
        var zonePcts = [flowZones.crypto, flowZones.entertain, flowZones.games];

        // ── RANK + JOB STATE (above GPU source) ──
        var pulseAlpha = 0.5 + Math.sin(flowFrame * 0.03) * 0.3;
        ctx.save();
        ctx.globalAlpha = pulseAlpha;
        ctx.font = '900 10px Orbitron, monospace';
        ctx.fillStyle = rankCol;
        ctx.textAlign = 'center';
        ctx.fillText(playerStats.rank, cx, gpuY - 14);
        ctx.font = '600 6px "Courier New", monospace';
        ctx.fillStyle = '#aaa';
        var jobState = 'IDLE';
        if (running && worker) jobState = 'GPU + BRAIN ACTIVE';
        else if (running) jobState = 'GPU RENDERING';
        ctx.fillText(jobState, cx, gpuY - 5);
        ctx.restore();

        // ── GPU SOURCE (top) ──
        var gpuPulse = 8 + Math.sin(flowFrame * 0.05) * 3;
        ctx.beginPath();
        ctx.arc(cx, gpuY, gpuPulse, 0, Math.PI * 2);
        ctx.fillStyle = hexToRgba(rankCol, 0.15);
        ctx.fill();
        // Rank glow
        ctx.save();
        ctx.shadowColor = rankCol;
        ctx.shadowBlur = 10 + Math.sin(flowFrame * 0.04) * 5;
        ctx.beginPath();
        ctx.arc(cx, gpuY, 5, 0, Math.PI * 2);
        ctx.fillStyle = rankCol;
        ctx.fill();
        ctx.restore();
        ctx.font = '700 7px Orbitron, monospace';
        ctx.fillStyle = rankCol;
        ctx.textAlign = 'center';
        ctx.fillText('YOUR GPU', cx, gpuY + 18);

        // ── Pipe: GPU → Factory ──
        ctx.beginPath();
        ctx.moveTo(cx, gpuY + 8);
        ctx.lineTo(cx, factY - 5);
        ctx.strokeStyle = hexToRgba(rankCol, 0.25);
        ctx.lineWidth = 2;
        ctx.stroke();

        // ── FACTORY CORE ──
        ctx.fillStyle = 'rgba(10,10,30,0.9)';
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        roundRect(ctx, 30, factY, W - 60, factH, 6, true, true);
        ctx.font = '900 8px Orbitron, monospace';
        ctx.fillStyle = '#555';
        ctx.textAlign = 'center';
        ctx.fillText('T H E   F A C T O R Y', cx, factY + 14);

        // Factory nodes (C, E, G)
        var nodeLabels = ['C', 'E', 'G'];
        for (var ni = 0; ni < 3; ni++) {
            var nx = 60 + ni * 75;
            var ny = factY + 35;
            var pulse = 0.5 + Math.sin(flowFrame * 0.08 + ni * 2.1) * 0.5;
            ctx.beginPath();
            ctx.arc(nx, ny, 10, 0, Math.PI * 2);
            ctx.fillStyle = hexToRgba(zoneColors[ni], 0.15 + pulse * 0.15);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(nx, ny, 6, 0, Math.PI * 2);
            ctx.fillStyle = zoneColors[ni];
            ctx.fill();
            ctx.font = '900 7px monospace';
            ctx.fillStyle = '#000';
            ctx.textAlign = 'center';
            ctx.fillText(nodeLabels[ni], nx, ny + 3);
        }

        // Circuit lines between nodes
        ctx.beginPath();
        ctx.moveTo(70, factY + 35);
        ctx.lineTo(200, factY + 35);
        ctx.strokeStyle = 'rgba(50,50,80,0.5)';
        ctx.lineWidth = 1;
        ctx.stroke();

        // ── Pipes: Factory → Zones ──
        for (var zi = 0; zi < 3; zi++) {
            ctx.beginPath();
            ctx.moveTo(60 + zi * 75, factY + factH);
            ctx.quadraticCurveTo(60 + zi * 75, factY + factH + 40, zoneXs[zi], zoneY - 10);
            ctx.strokeStyle = hexToRgba(zoneColors[zi], 0.2);
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        // ── ZONE BOXES ──
        for (var zi = 0; zi < 3; zi++) {
            var zx = zoneXs[zi] - 32;
            var zy = zoneY;
            ctx.fillStyle = hexToRgba(zoneColors[zi], 0.08);
            ctx.strokeStyle = hexToRgba(zoneColors[zi], 0.4);
            ctx.lineWidth = 1;
            roundRect(ctx, zx, zy, 64, 50, 4, true, true);

            ctx.font = '700 7px Orbitron, monospace';
            ctx.fillStyle = zoneColors[zi];
            ctx.textAlign = 'center';
            ctx.fillText(zoneNames[zi], zoneXs[zi], zy + 14);

            // Fill bar
            ctx.fillStyle = 'rgba(255,255,255,0.05)';
            ctx.fillRect(zx + 6, zy + 22, 52, 6);
            ctx.fillStyle = hexToRgba(zoneColors[zi], 0.7);
            ctx.fillRect(zx + 6, zy + 22, 52 * zonePcts[zi] / 100, 6);

            ctx.font = '700 9px monospace';
            ctx.fillStyle = zoneColors[zi];
            ctx.fillText(zonePcts[zi] + '%', zoneXs[zi], zy + 42);
        }

        // ── Pipes: Zones → Wealth ──
        for (var zi = 0; zi < 3; zi++) {
            ctx.beginPath();
            ctx.moveTo(zoneXs[zi], zoneY + 52);
            ctx.quadraticCurveTo(zoneXs[zi], wealthY - 20, cx, wealthY - 8);
            ctx.strokeStyle = hexToRgba(zoneColors[zi], 0.15);
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }

        // ── WEALTH CONVERGENCE POINT ──
        var wPulse = 6 + Math.sin(flowFrame * 0.04) * 2;
        ctx.beginPath();
        ctx.arc(cx, wealthY, wPulse, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(218,165,32,0.12)';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(cx, wealthY, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#daa520';
        ctx.fill();
        ctx.font = '700 7px Orbitron, monospace';
        ctx.fillStyle = '#daa520';
        ctx.textAlign = 'center';
        ctx.fillText('YOUR WEALTH', cx, wealthY + 16);

        // ── PARTICLES ──
        // Spawn new particles
        if (flowFrame % Math.max(3, Math.round(8 / gpuIntensity)) === 0) {
            var r = Math.random();
            var zone = r < 0.34 ? 0 : r < 0.75 ? 1 : 2;
            flowParticles.push({
                progress: 0,
                zone: zone,
                speed: 0.006 + Math.random() * 0.004 + gpuIntensity * 0.002,
                size: 1.5 + Math.random() * 1.5,
            });
        }

        // Update + draw particles
        for (var pi = flowParticles.length - 1; pi >= 0; pi--) {
            var p = flowParticles[pi];
            p.progress += p.speed;
            if (p.progress >= 1.0) { flowParticles.splice(pi, 1); continue; }

            var px, py, col;
            var t = p.progress;
            var zIdx = p.zone;

            if (t < 0.3) {
                // Stage 1: GPU → Factory (rank color)
                var st = t / 0.3;
                px = cx + Math.sin(st * 3 + pi) * 2;
                py = gpuY + 10 + st * (factY - gpuY - 10);
                col = rankCol;
            } else if (t < 0.6) {
                // Stage 2: Factory → Zone (transition to zone color)
                var st = (t - 0.3) / 0.3;
                var startX = 60 + zIdx * 75;
                px = startX + (zoneXs[zIdx] - startX) * st;
                py = factY + factH + (zoneY - factY - factH) * st;
                col = lerpColor(rankCol, zoneColors[zIdx], st);
            } else {
                // Stage 3: Zone → Wealth (zone color, converge)
                var st = (t - 0.6) / 0.4;
                px = zoneXs[zIdx] + (cx - zoneXs[zIdx]) * st;
                py = zoneY + 52 + (wealthY - zoneY - 52) * st;
                col = lerpColor(zoneColors[zIdx], '#daa520', st);
            }

            ctx.beginPath();
            ctx.arc(px, py, p.size, 0, Math.PI * 2);
            ctx.fillStyle = col;
            ctx.globalAlpha = 0.8 - t * 0.3;
            ctx.fill();
            ctx.globalAlpha = 1;
        }

        // Cap particles
        if (flowParticles.length > 60) flowParticles.splice(0, flowParticles.length - 60);

        // Smooth wealth tick-up
        if (flowWealth < flowWealthTarget) {
            flowWealth = Math.min(flowWealthTarget, flowWealth + 0.001);
        }

        flowAnimId = requestAnimationFrame(animateFlow);
    }

    // ─── Canvas Helpers ─────────────────────────────────────────
    function roundRect(ctx, x, y, w, h, r, fill, stroke) {
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + w - r, y);
        ctx.quadraticCurveTo(x + w, y, x + w, y + r);
        ctx.lineTo(x + w, y + h - r);
        ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        ctx.lineTo(x + r, y + h);
        ctx.quadraticCurveTo(x, y + h, x, y + h - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
        if (fill) ctx.fill();
        if (stroke) ctx.stroke();
    }

    function hexToRgba(hex, alpha) {
        var r = parseInt(hex.slice(1, 3), 16);
        var g = parseInt(hex.slice(3, 5), 16);
        var b = parseInt(hex.slice(5, 7), 16);
        return 'rgba(' + r + ',' + g + ',' + b + ',' + alpha + ')';
    }

    function lerpColor(a, b, t) {
        var ar = parseInt(a.slice(1, 3), 16), ag = parseInt(a.slice(3, 5), 16), ab = parseInt(a.slice(5, 7), 16);
        var br = parseInt(b.slice(1, 3), 16), bg = parseInt(b.slice(3, 5), 16), bb = parseInt(b.slice(5, 7), 16);
        var rr = Math.round(ar + (br - ar) * t);
        var rg = Math.round(ag + (bg - ag) * t);
        var rb = Math.round(ab + (bb - ab) * t);
        return '#' + ((1 << 24) + (rr << 16) + (rg << 8) + rb).toString(16).slice(1);
    }

    // ─── Whistle Interpretation Submission ─────────────────────
    function submitWhistle() {
        var inputEl = document.getElementById('sc-whistle-input');
        if (!inputEl || !inputEl.value.trim()) return;

        var text = inputEl.value.trim().substring(0, 100);
        var interps = [];
        try { interps = JSON.parse(localStorage.getItem(WHISTLE_INTERPS_KEY)) || []; } catch(e) {}

        interps.push({
            text: text,
            timestamp: Date.now(),
            playerId: CortexPlayer.getStats().id
        });

        localStorage.setItem(WHISTLE_INTERPS_KEY, JSON.stringify(interps));
        CortexPlayer.addCredits(5, 'whistle_interpretation');

        inputEl.value = '';
        renderWhistleTraining();

        inputEl.style.borderColor = '#22c55e';
        setTimeout(function() { inputEl.style.borderColor = '#333'; }, 800);
    }

    // ─── Compute Node Submission ─────────────────────────────────
    function submitComputeNode() {
        var inputEl = document.getElementById('sc-node-id');
        if (!inputEl || !inputEl.value.trim()) return;

        var nodeId = inputEl.value.trim().substring(0, 64);
        var nodes = [];
        try { nodes = JSON.parse(localStorage.getItem(COMPUTE_NODES_KEY)) || []; } catch(e) {}

        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].nodeId === nodeId) {
                inputEl.style.borderColor = '#ff4444';
                setTimeout(function() { inputEl.style.borderColor = '#333'; }, 1000);
                return;
            }
        }

        nodes.push({
            nodeId: nodeId,
            timestamp: Date.now(),
            playerId: CortexPlayer.getStats().id
        });

        localStorage.setItem(COMPUTE_NODES_KEY, JSON.stringify(nodes));
        CortexPlayer.addCredits(1000, 'compute_node');

        inputEl.value = '';
        renderMissions();

        inputEl.style.borderColor = '#8844ff';
        setTimeout(function() { inputEl.style.borderColor = '#333'; }, 800);
    }

    // ─── Oracle Guide Toggle ─────────────────────────────────────
    function toggleOracleGuide() {
        oracleGuideOpen = !oracleGuideOpen;
        var el = document.getElementById('sc-oracle-guide');
        if (el) el.style.display = oracleGuideOpen ? 'block' : 'none';
    }

    // ─── Exit ────────────────────────────────────────────────────
    function exit() {
        stop();

        // Stop audio
        var audio = document.getElementById('sc-ambient');
        if (audio) { audio.pause(); audio.currentTime = 0; }

        // Remove UI
        if (canvas) canvas.remove();
        if (hudEl) hudEl.remove();
        const gs = document.getElementById('sc-greenscreen');
        if (gs) gs.remove();

        // Exit fullscreen
        if (document.fullscreenElement) {
            document.exitFullscreen().catch(() => {}).then(function() {
                window.location.href = 'https://www.shortfactory.shop/';
            });
        } else {
            window.location.href = 'https://www.shortfactory.shop/';
        }

        canvas = null;
        gl = null;
        pipeline = null;
        hudEl = null;
        running = false;
    }

    // ─── Public API ──────────────────────────────────────────────
    return {
        init,
        start,
        stop,
        exit,
        toggleGreenscreen,
        toggleSwarm,
        submitApiKey,
        removeApiKey,
        submitWhistle,
        submitComputeNode,
        toggleOracleGuide,
        getIntensity: function() { return gpuIntensity; },
        isRunning: function() { return running; },
        getStats: function() {
            return {
                running: running,
                totalTasks: totalTasksCompleted,
                pendingResults: pendingResults.length,
                imageCount: activeImages.length,
                currentImage: currentImageIdx,
                gpuIntensity: gpuIntensity
            };
        }
    };
})();
