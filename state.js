/* ==================== SAFE STORAGE HELPERS ====================
 * Wrap localStorage to handle private browsing mode and storage disabled
 */

function safeGetLocal(key, defaultValue = null) {
  try {
    return localStorage.getItem(key);
  } catch (e) {
    console.warn('localStorage unavailable:', e.message);
    return defaultValue;
  }
}

function safeSetLocal(key, value) {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch (e) {
    console.warn('localStorage unavailable:', e.message);
    return false;
  }
}

function safeRemoveLocal(key) {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (e) {
    console.warn('localStorage unavailable:', e.message);
    return false;
  }
}

/* ==================== GAME STATE ====================
 * All game variables in one place
 * This makes it easy to save/load games and debug
 *
 * DESIGN NOTE: G is intentionally a global object for simplicity and
 * accessibility across all modules. Alternative approaches (class-based
 * state management or parameter passing) would require significant
 * refactoring of the entire codebase. The global approach works well
 * for this single-page game with no module conflicts.
 */

let G = {
  // NG+ loop tracking
  ngPlusLoop: parseInt(safeGetLocal('ngPlusLoop', '0')),

  // Core stats
  purity: 6,
  debt: 38,
  round: 1,
  moves: 5,
  baseMoves: 5,
  trumpHP: 100,
  deepStateHP: 30,
  impeachmentCount: 0,

  // Advisor
  advisor: null,

  // Economy
  oilBarrels: 0,
  oilCash: 0,
  oilReserves: 145,
  oilPrice: 1.0,

  // World stats
  birthrate: 1.64,
  muslimThreat: 10,
  trumpAge: 78,
  israelGDP: 564,
  feminism: 20,
  christianity: 80,
  optics: 'GOOD',

  // Group-specific stats for stereotype icons
  deadBodies: 0,     // Jihadi kills
  abortions: 0,      // Feminist abortions
  babies: 0,         // Christian babies born

  // US Population tracking
  usPopulation: 335000000,  // 335 million starting population
  prevPopulation: 335000000, // Track previous for color changes
  poopThreat: Math.floor(Math.random() * 5) + 3,  // 💩 emoji count (3-7 random) - represents death threat level

  // Character stats - psychological, financial, spiritual bars
  groupStats: {
    muslim: {
      psychological: 50,  // Red bar - mental health
      financial: 30,      // Green bar - money/resources
      spiritual: 70,      // White bar - willpower/faith
      eventCounters: {
        kills: 0          // Dead bodies counter
      }
    },
    feminist: {
      psychological: 60,  // Start with 6 hearts total
      financial: 80,
      spiritual: 40,
      eventCounters: {
        rainbowHearts: 0,  // Goes up when feminist cards appear
        abortions: 0
      }
    },
    israel: {
      psychological: 80,
      financial: 90,
      spiritual: 60,
      eventCounters: {
        shekels: 0
      }
    },
    christianity: {
      psychological: 70,
      financial: 40,
      spiritual: 95,
      eventCounters: {
        crosses: 0,
        babies: 0
      }
    },
    chad: {
      psychological: 90,
      financial: 70,
      spiritual: 85,
      eventCounters: {
        gains: 0
      }
    },
    tradwife: {
      psychological: 80,
      financial: 50,
      spiritual: 90,
      eventCounters: {
        meals: 0
      }
    },
    soy: {
      psychological: 20,
      financial: 45,
      spiritual: 10,
      eventCounters: {
        soyProducts: 0
      }
    },
    wojak: {
      psychological: 15,
      financial: 25,
      spiritual: 30,
      eventCounters: {
        sadMoments: 0
      }
    },
    dumptruck: {
      psychological: 10,
      financial: 80,
      spiritual: 40,
      eventCounters: {
        dumps: 0
      }
    }
  },

  // Unlocks
  trumpUnlocked: safeGetLocal('trumpUnlocked') === 'true',
  hitlerUnlocked: safeGetLocal('hitlerUnlocked') === 'true',

  // Game flags
  usedAggressive: false,
  diceTurns: 0,
  meanTweetMode: false,
  totalMoves: 0,
  oldVideoPlayed: false,

  // Emergency tier tracking
  emergencyTier: 0,        // 0=none, 1=50% blackops, 2=30% wheel, 3=20% nuke
  blackopsUsed: false,     // Used blackops at 50%
  wheelUsed: false,        // Used wheel at 30%
  nukeUsed: false,         // Used nuke at 20%

  // Term system
  term: 1,
  term1Complete: false,
  statsVideoShown: false,  // Shown "stats are wrong" video for purity > 96%
  difficultyMult: 1,  // 2x in Term 2
  cardFreqMult: 1,    // 0.5x in Term 2

  // Play-by-play action history for finale narration
  gameHistory: {
    actions: {},        // { oil: 5, war: 3, drone: 2, ... } count per action type
    nukes: [],          // [{ target: 'AFGHANISTAN', tagline: 'MISSION ACCOMPLISHED' }, ...]
    wheelSpins: [],     // [{ name: 'ZOMBIE PLAGUE', good: false }, ...]
    blackOps: [],       // [{ name: 'WETWORK' }, ...]
    speedBonuses: { blazing: 0, fast: 0, quick: 0 },
    meanTweets: { wins: 0, losses: 0 },
    powerupMultipliers: [],  // [10, 5, 7, ...] multipliers achieved
    highestMult: 1,     // Biggest single multiplier hit
    attacksSurvived: 0, // Deep state attacks weathered
    peakPurity: 0,      // Highest purity reached
    lowestHP: 100       // Lowest Trump HP reached
  }
};

// ==================== UI STATE ====================
let statsOpen = false;
let litOpen = false;
let emergActive = false;
let wheelSpinning = false;
let wheelSpinRAF = null; // requestAnimationFrame ID for wheel spin cleanup

// ==================== TIMERS ====================
// Consolidated timer management to avoid global variable pollution
const TIMERS = {
  emerg: null,
  nuke: null,
  wheel: null,
  ops: null,
  advisor: null,
  tweet: null,
  tweetDecay: null,
  powerup: null,
  infoButton: null,
  meanTweet: null,
  alertAlternate: null
};

// Legacy timer variables for backward compatibility (will be deprecated)
let emergTimer = null, nukeTimer = null, wheelTimer = null, opsTimer = null, advisorTimer = null;
let tweetTimer = null, tweetDecayTimer = null;
let powerupInterval = null;
let infoButtonTimer = null;
let meanTweetTimer = null;
let alertAlternateTimer = null;

// ==================== ALERT ALTERNATION ====================
// Tracks which alert phase is showing: 'emergency' or 'litigation'
let currentAlertPhase = 'emergency';
const LITIGATION_EMOJI = '⚖️';

// ==================== MINI-GAME STATE ====================
let tweetTaps = 0;
let tweetProgress = 0;
let tweetGameActive = false;
let currentTapPower = 8;

// Powerup tap game state
let powerupTapActive = false;
let powerupTapProgress = 0;
let powerupTapAction = '';
let powerupTapIdx = 0;
let powerupTapTimer = null;
let powerupTapDecayTimer = null;
let boostsUsedThisGame = 0;
const MAX_BOOSTS_PER_GAME = 2;

// Speed bonus tracking
let lastActionTime = 0;
const SPEED_THRESHOLDS = {
  blazing: 1000,   // Under 1 second = 3x
  fast: 2000,      // Under 2 seconds = 2x
  quick: 3500      // Under 3.5 seconds = 1.5x
};

// ==================== POWERUPS ====================
let powerups = {};
let trumpCardActive = false;

// ==================== TRACKING ====================
let videosPlayed = {};

// ==================== STATE HELPERS ====================

function resetGameState() {
  boostsUsedThisGame = 0; // Reset boost counter for new game
  lastActionTime = 0; // Reset speed bonus timer
  const ngLoop = parseInt(safeGetLocal('ngPlusLoop', '0'));
  const loopMult = 1 + (ngLoop * 0.3); // 1.0, 1.3, 1.6, 1.9...
  G = {
    ngPlusLoop: ngLoop,
    purity: 6,
    debt: 38,
    round: 1,
    moves: Math.max(3, Math.floor(5 / loopMult)),
    baseMoves: Math.max(3, Math.floor(5 / loopMult)),
    trumpHP: 100,
    deepStateHP: 30,
    impeachmentCount: 0,
    advisor: null,
    oilBarrels: 0,
    oilCash: 0,
    oilReserves: 145,
    oilPrice: 1.0,
    birthrate: 1.64,
    muslimThreat: 10,
    trumpAge: 78,
    israelGDP: 564,
    feminism: 20,
    christianity: 80,
    optics: 'GOOD',
    deadBodies: 0,
    abortions: 0,
    babies: 0,
    usPopulation: 335000000,
    prevPopulation: 335000000,
    poopThreat: Math.floor(Math.random() * 5) + 3,  // 3-7 random
    groupStats: {
      muslim: { psychological: 50, financial: 30, spiritual: 70, eventCounters: { kills: 0 } },
      feminist: { psychological: 40, financial: 60, spiritual: 20, eventCounters: { rainbowHearts: 0, abortions: 0 } },
      israel: { psychological: 80, financial: 90, spiritual: 60, eventCounters: { shekels: 0 } },
      christianity: { psychological: 70, financial: 40, spiritual: 95, eventCounters: { crosses: 0, babies: 0 } },
      chad: { psychological: 90, financial: 70, spiritual: 85, eventCounters: { gains: 0 } },
      tradwife: { psychological: 80, financial: 50, spiritual: 90, eventCounters: { meals: 0 } },
      soy: { psychological: 20, financial: 45, spiritual: 10, eventCounters: { soyProducts: 0 } },
      wojak: { psychological: 15, financial: 25, spiritual: 30, eventCounters: { sadMoments: 0 } },
      dumptruck: { psychological: 10, financial: 80, spiritual: 40, eventCounters: { dumps: 0 } }
    },
    trumpUnlocked: safeGetLocal('trumpUnlocked') === 'true',
    hitlerUnlocked: safeGetLocal('hitlerUnlocked') === 'true',
    usedAggressive: false,
    diceTurns: 0,
    meanTweetMode: false,
    totalMoves: 0,
    oldVideoPlayed: false,
    emergencyTier: 0,
    blackopsUsed: false,
    wheelUsed: false,
    nukeUsed: false,
    term: 1,
    term1Complete: false,
    statsVideoShown: false,
    difficultyMult: loopMult,
    cardFreqMult: Math.max(0.1, 1 / loopMult),
    gameHistory: {
      actions: {},
      nukes: [],
      wheelSpins: [],
      blackOps: [],
      speedBonuses: { blazing: 0, fast: 0, quick: 0 },
      meanTweets: { wins: 0, losses: 0 },
      powerupMultipliers: [],
      highestMult: 1,
      attacksSurvived: 0,
      peakPurity: 0,
      lowestHP: 100
    }
  };
}

function saveGameState() {
  safeSetLocal('trumpGameSave', JSON.stringify(G));
}

function loadGameState() {
  const saved = safeGetLocal('trumpGameSave');
  if (saved) {
    try {
      G = JSON.parse(saved);

      // Migrate old saves that don't have new fields
      if (G.oilPrice === undefined) G.oilPrice = 1.0;
      if (G.deadBodies === undefined) G.deadBodies = 0;
      if (G.abortions === undefined) G.abortions = 0;
      if (G.babies === undefined) G.babies = 0;
      if (G.usPopulation === undefined) G.usPopulation = 335000000;
      if (G.prevPopulation === undefined) G.prevPopulation = G.usPopulation;
      if (G.poopThreat === undefined) G.poopThreat = 4;
      if (G.statsVideoShown === undefined) G.statsVideoShown = false;
      if (G.hitlerUnlocked === undefined) G.hitlerUnlocked = safeGetLocal('hitlerUnlocked') === 'true';
      if (G.ngPlusLoop === undefined) G.ngPlusLoop = parseInt(safeGetLocal('ngPlusLoop', '0'));
      if (G.impeachmentCount === undefined) G.impeachmentCount = 0;
      // Sanitise NaN values from corrupt saves
      if (!G.moves || isNaN(G.moves)) G.moves = 5;
      if (!G.baseMoves || isNaN(G.baseMoves)) G.baseMoves = 5;
      if (isNaN(G.purity)) G.purity = 6;
      if (isNaN(G.trumpHP)) G.trumpHP = 100;
      if (!G.gameHistory) {
        G.gameHistory = {
          actions: {}, nukes: [], wheelSpins: [], blackOps: [],
          speedBonuses: { blazing: 0, fast: 0, quick: 0 },
          meanTweets: { wins: 0, losses: 0 },
          powerupMultipliers: [], highestMult: 1,
          attacksSurvived: 0, peakPurity: 0, lowestHP: 100
        };
      }
      if (!G.groupStats) {
        G.groupStats = {
          muslim: { psychological: 50, financial: 30, spiritual: 70, eventCounters: { kills: 0 } },
          feminist: { psychological: 40, financial: 60, spiritual: 20, eventCounters: { rainbowHearts: 0, abortions: 0 } },
          israel: { psychological: 80, financial: 90, spiritual: 60, eventCounters: { shekels: 0 } },
          christianity: { psychological: 70, financial: 40, spiritual: 95, eventCounters: { crosses: 0, babies: 0 } },
          chad: { psychological: 90, financial: 70, spiritual: 85, eventCounters: { gains: 0 } },
          tradwife: { psychological: 80, financial: 50, spiritual: 90, eventCounters: { meals: 0 } },
          soy: { psychological: 20, financial: 45, spiritual: 10, eventCounters: { soyProducts: 0 } },
          wojak: { psychological: 15, financial: 25, spiritual: 30, eventCounters: { sadMoments: 0 } },
          dumptruck: { psychological: 10, financial: 80, spiritual: 40, eventCounters: { dumps: 0 } }
        };
      }

      return true;
    } catch (e) {
      console.error('Failed to parse saved game:', e);
      return false;
    }
  }
  return false;
}

// ==================== VIBRATION HELPER ====================

// Load rumble setting from localStorage (default: ON)
let rumbleEnabled = safeGetLocal('rumbleEnabled') !== 'false'; // Default ON unless explicitly disabled

function vibrate(pattern) {
  if (!rumbleEnabled) {
    console.log('🔇 Vibration blocked - rumbleEnabled is OFF');
    return;
  }

  // Direct vibration call
  if (navigator.vibrate) {
    try {
      const success = navigator.vibrate(pattern);
      if (!success) {
        console.warn('⚠️ Vibration failed - check phone settings or browser permissions');
      } else {
        console.log('✅ Vibration triggered:', pattern);
      }
    } catch (e) {
      console.error('❌ Vibration error:', e);
    }
  } else {
    console.warn('⚠️ navigator.vibrate not supported on this device/browser');
  }
}

function toggleRumble(enabled) {
  rumbleEnabled = enabled;

  // Save to localStorage
  safeSetLocal('rumbleEnabled', enabled.toString());

  // Strong test vibration when enabling
  if (enabled && navigator.vibrate) {
    // Try direct vibration call with strong pattern
    navigator.vibrate([200, 100, 200, 100, 400]);
    console.log('🔊 Direct vibration test: [200, 100, 200, 100, 400]');

    // Tiny screen shake for visual feedback
    const phone = document.getElementById('phone');
    if (phone) {
      phone.classList.add('rumble-shake');
      setTimeout(() => {
        phone.classList.remove('rumble-shake');
      }, 500);
    }
  }

  console.log('🔊 RUMBLE:', enabled ? 'ON ✅' : 'OFF 🔇', '| Supports vibrate:', !!navigator.vibrate);

  // Show notification
  showRumbleNotification(enabled);

  // ALTERNATE: Logo VIVID when rumble ON, names DROP DOWN when rumble OFF
  const logo = document.querySelector('.claude-logo');
  const credits = document.querySelector('.game-credits');

  if (logo) {
    if (enabled) {
      // Rumble ON = Logo VIVID
      logo.classList.add('vivid');
      console.log('Claude logo: VIVID (rumble ON)');
    } else {
      // Rumble OFF = Logo hidden
      logo.classList.remove('vivid');
      console.log('Claude logo: HIDDEN (rumble OFF)');
    }
  }

  if (credits) {
    if (enabled) {
      // Rumble ON = Names hidden
      credits.classList.remove('dropdown');
      console.log('Names: HIDDEN (rumble ON)');
    } else {
      // Rumble OFF = Names DROP DOWN
      credits.classList.add('dropdown');
      console.log('Names: DROPDOWN (rumble OFF)');
    }
  }

  // Update rumble label text
  const rumbleLabel = document.querySelector('.rumble-label');
  const rumbleText = document.querySelector('.rumble-text');
  const rumbleState = document.querySelector('.rumble-state');

  if (rumbleLabel && rumbleText && rumbleState) {
    if (enabled) {
      // ON: hide label completely
      rumbleLabel.style.display = 'none';
    } else {
      // OFF: show just "OFF" (small) in green
      rumbleLabel.style.display = 'flex';
      rumbleText.style.display = 'none';
      rumbleState.textContent = 'OFF';
      rumbleLabel.classList.add('off');
    }
  }
}

function showRumbleNotification(enabled) {
  // Remove existing notification
  const existing = document.getElementById('rumble-notification');
  if (existing) existing.remove();

  const notification = document.createElement('div');
  notification.id = 'rumble-notification';
  notification.style.position = 'fixed';
  notification.style.bottom = '60px';
  notification.style.left = '50%';
  notification.style.transform = 'translateX(-50%) translateY(-100px)';
  notification.style.fontFamily = "'Press Start 2P', monospace";
  notification.style.fontSize = '16px';
  notification.style.color = enabled ? '#0f0' : '#f00';
  notification.style.textShadow = enabled ? '2px 2px 0 #060' : '2px 2px 0 #600';
  notification.style.zIndex = '10000';
  notification.style.pointerEvents = 'none';
  notification.style.opacity = '0';
  notification.style.transition = 'all 0.5s ease';
  notification.textContent = enabled ? 'RUMBLE ON' : 'RUMBLE OFF';
  document.body.appendChild(notification);

  // Animate down
  setTimeout(() => {
    notification.style.transform = 'translateX(-50%) translateY(0)';
    notification.style.opacity = '1';
  }, 50);

  // Fade out and remove
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(-50%) translateY(50px)';
    setTimeout(() => notification.remove(), 500);
  }, 2000);
}

// Initialize logo/credits state on page load
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('rumble-toggle');
  if (toggle && toggle.checked) {
    // Rumble starts ON by default - show logo vivid, hide names
    const logo = document.querySelector('.claude-logo');
    const credits = document.querySelector('.game-credits');
    if (logo) logo.classList.add('vivid');
    if (credits) credits.classList.remove('dropdown');
  }
});

// Export for debugging
window.G = G;

// Expose vibrate and rumble controls for manual testing in console
window.testVibrate = function(pattern = 200) {
  console.log('Testing vibration manually...');
  if (!navigator.vibrate) {
    console.error('Vibration not supported on this device/browser');
    return false;
  }
  const result = navigator.vibrate(pattern);
  console.log('Vibration result:', result);
  return result;
};

window.toggleRumble = toggleRumble;
window.checkRumble = function() {
  console.log('🔊 Rumble Status:', rumbleEnabled ? 'ON ✅' : 'OFF 🔇');
  console.log('📱 Browser supports vibrate:', !!navigator.vibrate);
  console.log('💾 localStorage rumbleEnabled:', safeGetLocal('rumbleEnabled'));
  return rumbleEnabled;
};

// Log rumble status on load
console.log('🎮 Game loaded - Rumble:', rumbleEnabled ? 'ON ✅' : 'OFF 🔇', '| navigator.vibrate:', !!navigator.vibrate);
