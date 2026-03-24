/* ==================== INTELLIGENT ASSET MANAGER ====================
 * Preloads assets based on game phase to eliminate lag
 * Uses priority queuing and background loading
 */

const AssetManager = {
  loaded: new Set(),
  loading: new Set(),
  queue: [],

  // Preload a single asset
  preload(url, priority = 5) {
    if (this.loaded.has(url) || this.loading.has(url)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      this.queue.push({ url, priority, resolve, reject });
      this.queue.sort((a, b) => a.priority - b.priority); // Lower number = higher priority
      this.processQueue();
    });
  },

  // Process the queue
  processQueue() {
    // Limit concurrent loads to avoid overwhelming the browser
    const maxConcurrent = 6;
    const currentLoading = this.loading.size;

    if (currentLoading >= maxConcurrent || this.queue.length === 0) return;

    const item = this.queue.shift();
    this.loading.add(item.url);

    const ext = item.url.split('.').pop().toLowerCase();
    const isVideo = ['webm', 'mp4', 'mov'].includes(ext);
    const isAudio = ['mp3', 'ogg', 'wav'].includes(ext);

    if (isVideo) {
      const video = document.createElement('video');
      video.preload = 'auto';
      video.onloadeddata = () => {
        this.loading.delete(item.url);
        this.loaded.add(item.url);
        item.resolve();
        this.processQueue();
      };
      video.onerror = () => {
        this.loading.delete(item.url);
        console.warn('Failed to preload video:', item.url);
        item.reject();
        this.processQueue();
      };
      video.src = item.url;
      video.load();
    } else if (isAudio) {
      const audio = new Audio();
      audio.preload = 'auto';
      audio.onloadeddata = () => {
        this.loading.delete(item.url);
        this.loaded.add(item.url);
        item.resolve();
        this.processQueue();
      };
      audio.onerror = () => {
        this.loading.delete(item.url);
        console.warn('Failed to preload audio:', item.url);
        item.reject();
        this.processQueue();
      };
      audio.src = item.url;
      audio.load();
    } else {
      // Images
      const img = new Image();
      img.onload = () => {
        this.loading.delete(item.url);
        this.loaded.add(item.url);
        item.resolve();
        this.processQueue();
      };
      img.onerror = () => {
        this.loading.delete(item.url);
        console.warn('Failed to preload image:', item.url);
        item.reject();
        this.processQueue();
      };
      img.src = item.url;
    }

    // Continue processing queue
    if (this.queue.length > 0) {
      this.processQueue();
    }
  },

  // Preload multiple assets
  preloadBatch(urls, priority = 5) {
    return Promise.all(urls.map(url => this.preload(url, priority)));
  },

  // Check if asset is loaded
  isLoaded(url) {
    return this.loaded.has(url);
  },

  // Get loading stats
  getStats() {
    return {
      loaded: this.loaded.size,
      loading: this.loading.size,
      queued: this.queue.length
    };
  }
};

/* ==================== PHASE-BASED LOADING ====================
 * Load assets intelligently based on game phase
 */

// PHASE 1: Critical assets needed for page load
function preloadPhase1() {
  console.log('📦 Phase 1: Loading advisor assets...');

  const critical = [
    'https://www.shortfactory.shop/trump/advisor/advisor.jpg',
    ...ASSETS.advisorPlay.slice(0, 3) // First 3 advisor videos
  ];

  AssetManager.preloadBatch(critical, 1).then(() => {
    console.log('✅ Phase 1 complete');
  });
}

// PHASE 2: Load during advisor countdown (10 seconds)
function preloadPhase2() {
  console.log('📦 Phase 2: Loading early game assets during countdown...');

  const earlyGame = [
    ...ASSETS.trump.slice(0, 3), // First 3 Trump videos
    ...ASSETS.maps.slice(0, 1),  // First map
    'pages/how.webm',            // Tutorial video
    'https://www.shortfactory.shop/trump/george.png' // Tap button
  ];

  AssetManager.preloadBatch(earlyGame, 2).then(() => {
    console.log('✅ Phase 2 complete');
    preloadPhase3(); // Start phase 3 in background
  });
}

// PHASE 3: Load during advisor video (5-10 seconds)
function preloadPhase3() {
  console.log('📦 Phase 3: Loading action assets during advisor video...');

  const actions = [
    ...ASSETS.dice.slice(0, 6).map(d => d.v), // Dice videos
    ...ATTACKS.slice(0, 4).map(a => a.img),   // First 4 attack videos
    ...ASSETS.trump.slice(3, 6)                // More Trump videos
  ];

  AssetManager.preloadBatch(actions, 3).then(() => {
    console.log('✅ Phase 3 complete');
  });
}

// PHASE 4: Background load during early gameplay
function preloadPhase4() {
  console.log('📦 Phase 4: Background loading mid-game assets...');

  const midGame = [
    ...ASSETS.wheel.slice(0, 6),               // Wheel videos
    ...ASSETS.blackops,                         // Black ops
    ...Object.values(ASSETS.advisorAdvice).flat().slice(0, 5), // Advisor advice
    'pages/litigation.html'                     // Litigation page
  ];

  AssetManager.preloadBatch(midGame, 4).then(() => {
    console.log('✅ Phase 4 complete');
    preloadPhase5(); // Start final phase
  });
}

// PHASE 5: Background load endgame assets
function preloadPhase5() {
  console.log('📦 Phase 5: Background loading endgame assets...');

  const endGame = [
    ...ASSETS.goodnight,           // Ending videos
    'pages/trump-endings.html',    // Endings page
    ...SPECIAL_VIDEOS.nuke || [],  // Nuke videos
    ...ASSETS.trump.slice(6)       // Remaining Trump videos
  ];

  AssetManager.preloadBatch(endGame, 5).then(() => {
    console.log('✅ Phase 5 complete - All assets loaded!');
  });
}

// Initialize on page load
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    preloadPhase1();
  });
}

// Export for use in other modules
if (typeof window !== 'undefined') {
  window.AssetManager = AssetManager;
  window.preloadPhase1 = preloadPhase1;
  window.preloadPhase2 = preloadPhase2;
  window.preloadPhase3 = preloadPhase3;
  window.preloadPhase4 = preloadPhase4;
  window.preloadPhase5 = preloadPhase5;
}
