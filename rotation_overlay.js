/**
 * ShortFactory Rotation Overlay v5
 * - LIVE VISITOR HEADS: retro 1UP extra-lives style viewer count
 * - SHARED RATINGS: server-side star ratings everyone can see
 * - BIG YELLOW PAUSE BUTTON - stops rotation for engaged viewers
 * - STAR RATINGS: Purple (worth), Blue (boring), Yellow (want more)
 * - Screen counter (X of N) - clickable to skip
 * - NEXT button flashing red/yellow
 * - Countdown timer (30s)
 * - ENGAGEMENT TRACKING: records how long viewers stay, when they skip
 * - AUTO-REORDERS rotation: most engaging screens first, boring ones last
 * - ADMIN VIEW: unloved pages shown with grey warning overlay + ratings
 *
 * Data stored in localStorage + server via /api_pulse.php
 */

(function() {
    var STORAGE_KEY = 'sf_engagement';
    var RATINGS_KEY = 'sf_ratings';
    var pageLoadTime = Date.now();

    function init() {
        if (typeof ROTATION_CONFIG === 'undefined' || typeof getNextScreen !== 'function') {
            setTimeout(init, 200);
            return;
        }

        var screens = ROTATION_CONFIG.screens;
        var total = screens.length;
        var currentPath = window.location.pathname;
        var currentIndex = screens.findIndex(function(s) {
            return currentPath === s.url || currentPath.endsWith(s.url) || s.url.includes(currentPath);
        });
        if (currentIndex === -1) currentIndex = 0;
        var currentUrl = screens[currentIndex].url;
        var screenNum = currentIndex + 1;

        // Load data
        var engagement = loadEngagement();
        var allRatings = loadRatings();
        var pageRatings = allRatings[currentUrl] || {};

        // Check if admin
        var isAdmin = false;
        try { isAdmin = localStorage.getItem('admin_authenticated') === 'true'; } catch(e) {}

        // Get ranked order
        var ranked = getRankedScreens(screens, engagement);
        var currentRank = ranked.findIndex(function(s) { return s.url === currentUrl; }) + 1;

        // Pause state
        var paused = false;

        // Inject CSS
        var style = document.createElement('style');
        style.textContent = [
            "@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');",
            // Star rating bar
            ".rot-stars-bar { position:fixed; top:0; left:0; width:100%; z-index:10000; background:rgba(0,0,0,0.9); padding:10px 15px 8px; text-align:center; font-family:'Press Start 2P',monospace; border-bottom:2px solid #333; opacity:0; transform:translateY(-100%); transition:all 0.6s ease; }",
            ".rot-stars-bar.rot-visible { opacity:1; transform:translateY(0); }",
            ".rot-stars-cta { font-size:clamp(0.35rem,1vw,0.5rem); color:#aaa; margin-bottom:8px; line-height:1.6; letter-spacing:0.5px; }",
            ".rot-stars-cta b { color:#fff; }",
            ".rot-stars-row { display:flex; justify-content:center; gap:clamp(8px,3vw,25px); flex-wrap:wrap; }",
            ".rot-stars-group { display:flex; align-items:center; gap:3px; }",
            ".rot-stars-label { font-size:clamp(0.3rem,0.8vw,0.4rem); margin-right:4px; transition:all 0.3s; }",
            ".rot-star { font-size:clamp(1rem,2.5vw,1.4rem); cursor:pointer; transition:transform 0.15s,color 0.15s; user-select:none; -webkit-tap-highlight-color:transparent; }",
            ".rot-star:hover { transform:scale(1.4); }",
            ".rot-stars-thanks { font-size:0.4rem; color:#0f0; margin-top:6px; opacity:0; transition:opacity 0.3s; }",
            ".rot-stars-thanks.rot-show { opacity:1; }",
            // Pause button
            ".rot-pause-btn { position:fixed; bottom:20px; left:20px; z-index:9999; font-family:'Press Start 2P',monospace; font-size:clamp(1rem,2.5vw,1.6rem); color:#000; background:#ffd700; border:4px solid #b8960f; border-radius:15px; padding:clamp(12px,3vw,20px) clamp(18px,4vw,30px); cursor:pointer; user-select:none; text-shadow:1px 1px 0 #b8960f; box-shadow:0 0 30px rgba(255,215,0,0.4),0 6px 0 #b8960f,inset 0 2px 0 rgba(255,255,255,0.3); transition:all 0.15s; -webkit-tap-highlight-color:transparent; }",
            ".rot-pause-btn:hover { transform:scale(1.08); box-shadow:0 0 50px rgba(255,215,0,0.6),0 6px 0 #b8960f,inset 0 2px 0 rgba(255,255,255,0.3); }",
            ".rot-pause-btn:active { transform:scale(0.95) translateY(3px); box-shadow:0 0 20px rgba(255,215,0,0.3),0 2px 0 #b8960f,inset 0 2px 0 rgba(255,255,255,0.3); }",
            ".rot-pause-btn.rot-paused { background:#ff4444; border-color:#aa0000; color:#fff; text-shadow:1px 1px 0 #aa0000; box-shadow:0 0 30px rgba(255,50,50,0.5),0 6px 0 #aa0000,inset 0 2px 0 rgba(255,255,255,0.3); animation:pausePulse 1.5s ease-in-out infinite; }",
            "@keyframes pausePulse { 0%,100% { box-shadow:0 0 30px rgba(255,50,50,0.5),0 6px 0 #aa0000,inset 0 2px 0 rgba(255,255,255,0.3); } 50% { box-shadow:0 0 60px rgba(255,50,50,0.8),0 6px 0 #aa0000,inset 0 2px 0 rgba(255,255,255,0.3); } }",
            // Fist / Fuck This button
            ".rot-fist-btn { position:fixed; bottom:100px; left:20px; z-index:9999; font-family:'Press Start 2P',monospace; font-size:clamp(1.8rem,5vw,3rem); color:#fff; background:linear-gradient(180deg,#cc0000,#880000); border:4px solid #ff0000; border-radius:50%; width:clamp(60px,15vw,90px); height:clamp(60px,15vw,90px); display:flex; align-items:center; justify-content:center; cursor:pointer; user-select:none; box-shadow:0 0 25px rgba(255,0,0,0.5),0 6px 0 #550000,inset 0 2px 0 rgba(255,255,255,0.2); transition:all 0.15s; -webkit-tap-highlight-color:transparent; }",
            ".rot-fist-btn:hover { transform:scale(1.15) rotate(-10deg); box-shadow:0 0 50px rgba(255,0,0,0.8),0 6px 0 #550000,inset 0 2px 0 rgba(255,255,255,0.2); }",
            ".rot-fist-btn:active { transform:scale(0.9) rotate(15deg); box-shadow:0 0 15px rgba(255,0,0,0.3),0 2px 0 #550000; }",
            ".rot-fist-label { position:fixed; bottom:80px; left:20px; z-index:9999; font-family:'Press Start 2P',monospace; font-size:clamp(0.3rem,0.8vw,0.45rem); color:#f00; text-shadow:0 0 10px rgba(255,0,0,0.5),2px 2px 0 #000; text-align:center; width:clamp(60px,15vw,90px); pointer-events:none; }",
            ".rot-fist-flash { position:fixed; inset:0; background:rgba(255,0,0,0.6); z-index:10001; pointer-events:none; opacity:0; transition:opacity 0.1s; }",
            ".rot-fist-flash.rot-flash-active { opacity:1; }",
            // Counter
            ".rot-overlay-counter { position:fixed; top:50%; right:20px; transform:translateY(-50%); z-index:9999; text-align:center; cursor:pointer; transition:transform 0.3s; font-family:'Press Start 2P',monospace; user-select:none; }",
            ".rot-overlay-counter:hover { transform:translateY(-50%) scale(1.15); }",
            ".rot-overlay-number { font-size:clamp(3rem,8vw,6rem); color:#0f0; text-shadow:0 0 30px #0f0,0 0 60px #0f0,4px 4px 0 #000; line-height:1; }",
            ".rot-overlay-total { font-size:clamp(0.6rem,1.5vw,1rem); color:#0ff; text-shadow:0 0 10px #0ff,2px 2px 0 #000; margin-top:10px; }",
            ".rot-overlay-next { font-size:0.7rem; margin-top:12px; font-weight:bold; animation:nextFlash 0.6s ease-in-out infinite; }",
            "@keyframes nextFlash { 0%,100% { color:#f00; text-shadow:0 0 15px #f00,0 0 30px #f00; } 50% { color:#ff0; text-shadow:0 0 15px #ff0,0 0 30px #ff0; } }",
            // Countdown
            ".rot-overlay-countdown { position:fixed; bottom:20px; right:20px; z-index:9999; font-family:'Press Start 2P',monospace; font-size:clamp(1.5rem,4vw,3rem); color:#0f0; text-shadow:0 0 20px #0f0,0 0 40px #0f0,4px 4px 0 #000; background:rgba(0,0,0,0.8); padding:15px 25px; border-radius:15px; border:3px solid #0f0; box-shadow:0 0 30px rgba(0,255,0,0.5); font-weight:900; transition:all 0.3s; }",
            ".rot-overlay-countdown.rot-paused { color:#ffd700; border-color:#ffd700; text-shadow:0 0 20px #ffd700,0 0 40px #ffd700,4px 4px 0 #000; box-shadow:0 0 30px rgba(255,215,0,0.5); }",
            // Visitor heads (1UP extra lives style)
            ".rot-visitors { position:fixed; top:8px; right:15px; z-index:10001; display:flex; align-items:center; gap:3px; font-family:'Press Start 2P',monospace; opacity:0; transition:opacity 0.5s; }",
            ".rot-visitors.rot-visible { opacity:1; }",
            ".rot-visitor-head { display:inline-block; width:18px; height:18px; line-height:18px; text-align:center; font-size:12px; background:radial-gradient(circle at 50% 35%, #7fff7f 20%, #00cc00 70%, #008800 100%); border-radius:50% 50% 40% 40%; box-shadow:0 0 6px rgba(0,255,0,0.5),0 1px 0 #004400; border:1px solid #00aa00; position:relative; }",
            ".rot-visitor-head::after { content:''; position:absolute; top:5px; left:4px; width:3px; height:2px; background:#004; border-radius:50%; box-shadow:6px 0 0 #004; }",
            ".rot-visitor-count { font-size:0.45rem; color:#0f0; text-shadow:0 0 8px #0f0,1px 1px 0 #000; margin-left:5px; }",
            ".rot-visitor-label { font-size:0.3rem; color:#0a0; text-shadow:0 0 4px rgba(0,255,0,0.3); margin-left:2px; letter-spacing:0.5px; }",
            // Average ratings from other viewers
            ".rot-avg { font-size:0.3rem; color:#666; margin-top:2px; text-align:center; letter-spacing:0.3px; }",
            ".rot-avg b { color:#aaa; }",
            // Admin
            ".rot-overlay-rank { font-size:0.45rem; color:#888; margin-top:6px; }",
            ".rot-admin-unloved { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(100,100,100,0.5); z-index:9998; pointer-events:none; display:flex; align-items:center; justify-content:center; }",
            ".rot-admin-unloved-text { font-family:'Press Start 2P',monospace; font-size:clamp(1rem,3vw,2rem); color:#f00; text-shadow:0 0 20px #f00,4px 4px 0 #000; background:rgba(0,0,0,0.8); padding:20px 30px; border:3px solid #f00; border-radius:15px; pointer-events:none; text-align:center; line-height:2; }"
        ].join('\n');
        document.head.appendChild(style);

        // Remove hardcoded counters
        var existing = document.querySelectorAll('.screen-counter, .rotation-countdown');
        existing.forEach(function(el) { el.remove(); });

        // ========== STAR RATING BAR ==========
        var categories = [
            { key: 'worth', label: 'WORTH IT?', color: '#a855f7', glow: 'rgba(168,85,247,0.6)' },
            { key: 'boring', label: 'BORING?', color: '#00bfff', glow: 'rgba(0,191,255,0.6)' },
            { key: 'curious', label: 'WANT MORE?', color: '#ffd700', glow: 'rgba(255,215,0,0.6)' }
        ];

        var starsBar = document.createElement('div');
        starsBar.className = 'rot-stars-bar';

        var cta = document.createElement('div');
        cta.className = 'rot-stars-cta';
        cta.innerHTML = 'please click to help us improve - <b>make ShortFactory your home!</b>';
        starsBar.appendChild(cta);

        var row = document.createElement('div');
        row.className = 'rot-stars-row';

        var thanksEl = document.createElement('div');
        thanksEl.className = 'rot-stars-thanks';
        thanksEl.textContent = 'THANKS FOR RATING!';

        categories.forEach(function(cat) {
            var group = document.createElement('div');
            group.className = 'rot-stars-group';

            var label = document.createElement('span');
            label.className = 'rot-stars-label';
            label.style.color = cat.color;
            label.style.textShadow = '0 0 8px ' + cat.glow;
            label.textContent = cat.label;
            group.appendChild(label);

            var savedVal = pageRatings[cat.key] || 0;

            for (var i = 1; i <= 5; i++) {
                var star = document.createElement('span');
                star.className = 'rot-star';
                star.dataset.cat = cat.key;
                star.dataset.val = i;
                star.textContent = i <= savedVal ? '\u2605' : '\u2606';
                star.style.color = i <= savedVal ? cat.color : '#333';
                star.style.textShadow = i <= savedVal ? '0 0 10px ' + cat.glow : 'none';

                (function(starEl, val, catObj, groupEl, labelEl) {
                    starEl.addEventListener('mouseenter', function() {
                        var stars = groupEl.querySelectorAll('.rot-star');
                        for (var j = 0; j < stars.length; j++) {
                            var v = parseInt(stars[j].dataset.val);
                            if (v <= val) {
                                stars[j].style.color = catObj.color;
                                stars[j].style.textShadow = '0 0 10px ' + catObj.glow;
                                stars[j].textContent = '\u2605';
                            }
                        }
                    });
                    starEl.addEventListener('mouseleave', function() {
                        var saved = (loadRatings()[currentUrl] || {})[catObj.key] || 0;
                        var stars = groupEl.querySelectorAll('.rot-star');
                        for (var j = 0; j < stars.length; j++) {
                            var v = parseInt(stars[j].dataset.val);
                            stars[j].style.color = v <= saved ? catObj.color : '#333';
                            stars[j].style.textShadow = v <= saved ? '0 0 10px ' + catObj.glow : 'none';
                            stars[j].textContent = v <= saved ? '\u2605' : '\u2606';
                        }
                    });
                    starEl.addEventListener('click', function(e) {
                        e.stopPropagation();
                        saveRating(currentUrl, catObj.key, val);
                        sendRatingToServer(currentUrl, catObj.key, val);
                        var stars = groupEl.querySelectorAll('.rot-star');
                        for (var j = 0; j < stars.length; j++) {
                            var v = parseInt(stars[j].dataset.val);
                            stars[j].style.color = v <= val ? catObj.color : '#333';
                            stars[j].style.textShadow = v <= val ? '0 0 10px ' + catObj.glow : 'none';
                            stars[j].textContent = v <= val ? '\u2605' : '\u2606';
                        }
                        var origText = labelEl.textContent;
                        labelEl.textContent = '\u2713 RATED!';
                        labelEl.style.color = '#0f0';
                        labelEl.style.textShadow = '0 0 10px rgba(0,255,0,0.6)';
                        setTimeout(function() {
                            labelEl.textContent = origText;
                            labelEl.style.color = catObj.color;
                            labelEl.style.textShadow = '0 0 8px ' + catObj.glow;
                        }, 1200);
                        thanksEl.classList.add('rot-show');
                        setTimeout(function() { thanksEl.classList.remove('rot-show'); }, 2000);
                        // Refresh avg ratings from server
                        setTimeout(function() {
                            fetchLiveData(currentUrl, function(res) {
                                if (res && res.ratings) renderAvgRatings(res.ratings);
                            });
                        }, 500);
                        console.log('Star rated:', catObj.key, '=', val, 'for', currentUrl);
                    });
                })(star, i, cat, group, label);

                group.appendChild(star);
            }
            row.appendChild(group);
        });

        starsBar.appendChild(row);
        starsBar.appendChild(thanksEl);
        document.body.appendChild(starsBar);

        // Slide in after 1.5s
        setTimeout(function() { starsBar.classList.add('rot-visible'); }, 1500);

        // ========== VISITOR HEADS (1UP extra lives) ==========
        var visitorsEl = document.createElement('div');
        visitorsEl.className = 'rot-visitors';
        document.body.appendChild(visitorsEl);

        function renderVisitorHeads(total) {
            visitorsEl.innerHTML = '';
            if (total <= 0) return;
            // Show up to 8 heads, then number
            var showHeads = Math.min(total, 8);
            for (var h = 0; h < showHeads; h++) {
                var head = document.createElement('span');
                head.className = 'rot-visitor-head';
                visitorsEl.appendChild(head);
            }
            var countEl = document.createElement('span');
            countEl.className = 'rot-visitor-count';
            countEl.textContent = total > 8 ? 'x' + total : '';
            visitorsEl.appendChild(countEl);
            var labelEl = document.createElement('span');
            labelEl.className = 'rot-visitor-label';
            labelEl.textContent = '1UP';
            visitorsEl.appendChild(labelEl);
            visitorsEl.classList.add('rot-visible');
        }

        // Add avg rating display elements under each star group
        var avgEls = {};
        var starGroups = row.querySelectorAll('.rot-stars-group');
        starGroups.forEach(function(g, idx) {
            var avgDiv = document.createElement('div');
            avgDiv.className = 'rot-avg';
            avgDiv.textContent = '';
            g.appendChild(avgDiv);
            avgEls[categories[idx].key] = avgDiv;
        });

        function renderAvgRatings(serverRatings) {
            if (!serverRatings) return;
            categories.forEach(function(cat) {
                var el = avgEls[cat.key];
                var r = serverRatings[cat.key];
                if (el && r && r.n > 0) {
                    el.innerHTML = '<b>' + r.avg + '</b>/5 (' + r.n + ' vote' + (r.n > 1 ? 's' : '') + ')';
                }
            });
        }

        // Heartbeat + fetch live data
        function pulse() {
            sendHeartbeat(currentUrl, function(res) {
                if (res && typeof res.total === 'number') {
                    renderVisitorHeads(res.total);
                }
            });
        }

        // Initial fetch
        fetchLiveData(currentUrl, function(res) {
            if (res) {
                renderVisitorHeads(res.total || 0);
                renderAvgRatings(res.ratings);
            }
        });

        // Heartbeat every 30s
        pulse();
        setInterval(pulse, 30000);

        // ========== SCREEN COUNTER ==========
        var counter = document.createElement('div');
        counter.className = 'rot-overlay-counter';
        var rankText = '';
        if (isAdmin) {
            var stats = engagement[currentUrl];
            var ratingInfo = '';
            if (pageRatings.worth || pageRatings.boring || pageRatings.curious) {
                ratingInfo = ' | W' + (pageRatings.worth||0) + ' B' + (pageRatings.boring||0) + ' C' + (pageRatings.curious||0);
            }
            if (stats && stats.views > 2) {
                rankText = '<div class="rot-overlay-rank">RANK ' + currentRank + '/' + total + ' | ' + Math.round(stats.skipRate * 100) + '% SKIP' + ratingInfo + '</div>';
            }
        }
        counter.innerHTML = '<div class="rot-overlay-number">' + screenNum + '</div>' +
            '<div class="rot-overlay-total">OF ' + total + ' SCREENS</div>' +
            '<div class="rot-overlay-next">NEXT</div>' +
            rankText;
        counter.addEventListener('click', function() { recordAndGoNext(true); });
        document.body.appendChild(counter);

        // ========== COUNTDOWN ==========
        var countdown = document.createElement('div');
        countdown.className = 'rot-overlay-countdown';
        countdown.textContent = '30';
        document.body.appendChild(countdown);

        // ========== PAUSE BUTTON ==========
        var pauseBtn = document.createElement('div');
        pauseBtn.className = 'rot-pause-btn';
        pauseBtn.textContent = 'PAUSE';
        pauseBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            paused = !paused;
            if (paused) {
                pauseBtn.textContent = 'PLAY';
                pauseBtn.classList.add('rot-paused');
                countdown.classList.add('rot-paused');
                countdown.textContent = '\u275A\u275A ' + timeLeft;
                // PAUSE = love this page. Massive engagement boost (opposite of fist)
                var data = loadEngagement();
                if (!data[currentUrl]) {
                    data[currentUrl] = { views: 0, skips: 0, totalTime: 0, avgTime: 0, skipRate: 0, score: 0 };
                }
                // Add 5 full views with 120s average time, zero skips - rockets the score
                data[currentUrl].views += 5;
                data[currentUrl].totalTime += 600;
                data[currentUrl].avgTime = data[currentUrl].totalTime / data[currentUrl].views;
                data[currentUrl].skipRate = data[currentUrl].skips / data[currentUrl].views;
                data[currentUrl].score = data[currentUrl].avgTime * (1 - data[currentUrl].skipRate);
                data[currentUrl].paused = (data[currentUrl].paused || 0) + 1;
                data[currentUrl].lastSeen = Date.now();
                saveEngagement(data);
                console.log('PAUSED (LOVED):', currentUrl, '| Pause count:', data[currentUrl].paused, '| Score boosted to:', Math.round(data[currentUrl].score));
            } else {
                pauseBtn.textContent = 'PAUSE';
                pauseBtn.classList.remove('rot-paused');
                countdown.classList.remove('rot-paused');
                countdown.textContent = '' + timeLeft;
            }
        });
        document.body.appendChild(pauseBtn);

        // ========== FIST / FUCK THIS BUTTON ==========
        var fistBtn = document.createElement('div');
        fistBtn.className = 'rot-fist-btn';
        fistBtn.textContent = '\uD83D\uDC4A';

        var fistLabel = document.createElement('div');
        fistLabel.className = 'rot-fist-label';
        fistLabel.textContent = 'FUCK THIS';

        var fistFlash = document.createElement('div');
        fistFlash.className = 'rot-fist-flash';

        fistBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            clearInterval(interval);
            // Red flash
            fistFlash.classList.add('rot-flash-active');
            // Play sound
            try {
                var snd = new Audio('/trump/fatality.mp3');
                snd.volume = 0.8;
                snd.play().catch(function(){});
            } catch(ex) {}
            // Record heavy negative engagement (counts as 5 skips, 0 time)
            var data = loadEngagement();
            if (!data[currentUrl]) {
                data[currentUrl] = { views: 0, skips: 0, totalTime: 0, avgTime: 0, skipRate: 0, score: 0 };
            }
            data[currentUrl].views += 5;
            data[currentUrl].skips += 5;
            data[currentUrl].avgTime = data[currentUrl].totalTime / data[currentUrl].views;
            data[currentUrl].skipRate = data[currentUrl].skips / data[currentUrl].views;
            data[currentUrl].score = data[currentUrl].avgTime * (1 - data[currentUrl].skipRate);
            data[currentUrl].fisted = (data[currentUrl].fisted || 0) + 1;
            data[currentUrl].lastSeen = Date.now();
            saveEngagement(data);
            console.log('FISTED:', currentUrl, '| Fist count:', data[currentUrl].fisted, '| Score tanked to:', data[currentUrl].score);
            // Navigate after brief flash
            setTimeout(function() {
                fistFlash.classList.remove('rot-flash-active');
                navigate();
            }, 600);
        });

        document.body.appendChild(fistFlash);
        document.body.appendChild(fistBtn);
        document.body.appendChild(fistLabel);

        // Admin: grey overlay on unloved pages
        if (isAdmin) {
            var stats = engagement[currentUrl];
            if (stats && stats.views >= 5 && stats.skipRate > 0.7) {
                var grey = document.createElement('div');
                grey.className = 'rot-admin-unloved';
                grey.innerHTML = '<div class="rot-admin-unloved-text">UNLOVED PAGE<br>' +
                    Math.round(stats.skipRate * 100) + '% SKIP RATE<br>' +
                    'AVG ' + Math.round(stats.avgTime) + 's WATCH TIME<br>' +
                    'RANK ' + currentRank + ' OF ' + total + '</div>';
                document.body.appendChild(grey);
                setTimeout(function() {
                    grey.style.transition = 'opacity 2s';
                    grey.style.opacity = '0';
                    setTimeout(function() { grey.remove(); }, 2000);
                }, 3000);
            }
        }

        // Countdown timer
        var timeLeft = 30;
        var interval = setInterval(function() {
            if (paused) return;
            timeLeft--;
            countdown.textContent = timeLeft;
            if (timeLeft <= 10) {
                countdown.style.color = '#f00';
                countdown.style.borderColor = '#f00';
                countdown.style.textShadow = '0 0 20px #f00, 0 0 40px #f00, 4px 4px 0 #000';
                countdown.style.boxShadow = '0 0 30px rgba(255,0,0,0.8)';
            }
            if (timeLeft <= 0) {
                clearInterval(interval);
                recordAndGoNext(false);
            }
        }, 1000);

        // Record engagement and navigate
        function recordAndGoNext(wasManualSkip) {
            clearInterval(interval);
            var timeSpent = Math.round((Date.now() - pageLoadTime) / 1000);
            recordEngagement(currentUrl, timeSpent, wasManualSkip);
            navigate();
        }

        // Navigate
        function navigate() {
            if (typeof rotateWithScatter === 'function') {
                rotateWithScatter();
            } else {
                var rankedNext = getNextRankedScreen(currentUrl, screens, engagement);
                window.location.href = rankedNext.url;
            }
        }

        console.log('Rotation Overlay v4: Screen ' + screenNum + '/' + total +
            (isAdmin ? ' [ADMIN] Rank ' + currentRank : '') + ' - PAUSE + Stars + 30s countdown');
    }

    // --- ENGAGEMENT DATA ---

    function loadEngagement() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
        } catch(e) { return {}; }
    }

    function saveEngagement(data) {
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch(e) {}
    }

    function recordEngagement(url, timeSpent, wasSkip) {
        var data = loadEngagement();
        if (!data[url]) {
            data[url] = { views: 0, skips: 0, totalTime: 0, avgTime: 0, skipRate: 0, score: 0 };
        }
        var s = data[url];
        s.views++;
        if (wasSkip) s.skips++;
        s.totalTime += timeSpent;
        s.avgTime = s.totalTime / s.views;
        s.skipRate = s.skips / s.views;
        s.score = s.avgTime * (1 - s.skipRate);
        s.lastSeen = Date.now();
        data[url] = s;
        saveEngagement(data);
        console.log('Engagement:', url, '| Time:', timeSpent + 's', wasSkip ? '(SKIPPED)' : '(FULL)', '| Score:', Math.round(s.score * 10) / 10);
    }

    // --- STAR RATINGS ---

    function loadRatings() {
        try {
            return JSON.parse(localStorage.getItem(RATINGS_KEY)) || {};
        } catch(e) { return {}; }
    }

    function saveRating(url, category, value) {
        var data = loadRatings();
        if (!data[url]) data[url] = {};
        data[url][category] = value;
        data[url].timestamp = Date.now();
        try { localStorage.setItem(RATINGS_KEY, JSON.stringify(data)); } catch(e) {}
        var eng = loadEngagement();
        if (!eng[url]) eng[url] = { views: 0, skips: 0, totalTime: 0, avgTime: 0, skipRate: 0, score: 0 };
        if (!eng[url].ratings) eng[url].ratings = {};
        eng[url].ratings[category] = value;
        saveEngagement(eng);
    }

    // --- RANKING ---

    function getRankedScreens(screens, engagement) {
        var scored = screens.map(function(s) {
            var e = engagement[s.url];
            return { url: s.url, name: s.name, score: e ? e.score : 15, views: e ? e.views : 0 };
        });
        scored.sort(function(a, b) { return b.score - a.score; });
        return scored;
    }

    function getNextRankedScreen(currentUrl, screens, engagement) {
        var ranked = getRankedScreens(screens, engagement);
        var currentRankIdx = ranked.findIndex(function(s) { return s.url === currentUrl; });
        if (currentRankIdx === -1) currentRankIdx = 0;
        var nextIdx = (currentRankIdx + 1) % ranked.length;
        var nextUrl = ranked[nextIdx].url;
        var nextScreen = screens.find(function(s) { return s.url === nextUrl; });
        return nextScreen || screens[0];
    }

    // --- SESSION ID ---
    function getSessionId() {
        var sid = '';
        try { sid = sessionStorage.getItem('sf_sid'); } catch(e) {}
        if (!sid) {
            sid = 'v' + Date.now().toString(36) + Math.random().toString(36).substr(2, 6);
            try { sessionStorage.setItem('sf_sid', sid); } catch(e) {}
        }
        return sid;
    }

    // --- SERVER API ---
    var API_URL = '/api_pulse.php';

    function sendHeartbeat(page, callback) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', API_URL, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.onload = function() {
                if (xhr.status === 200 && callback) {
                    try { callback(JSON.parse(xhr.responseText)); } catch(e) {}
                }
            };
            xhr.send(JSON.stringify({ action: 'heartbeat', session: getSessionId(), page: page }));
        } catch(e) {}
    }

    function sendRatingToServer(page, category, stars) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', API_URL, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({ action: 'rate', session: getSessionId(), page: page, category: category, stars: stars }));
        } catch(e) {}
    }

    function fetchLiveData(page, callback) {
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', API_URL + '?page=' + encodeURIComponent(page), true);
            xhr.onload = function() {
                if (xhr.status === 200 && callback) {
                    try { callback(JSON.parse(xhr.responseText)); } catch(e) {}
                }
            };
            xhr.send();
        } catch(e) {}
    }

    // --- INIT ---
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { setTimeout(init, 300); });
    } else {
        setTimeout(init, 300);
    }
})();
