/* ==================== GAME CONFIGURATION ====================
 * Edit this file to change game assets, balance, and constants
 * Your friend can modify these values to tune the game
 */

const BASE = 'https://www.shortfactory.shop/trump/';

// ==================== VIDEO VARIATION SYSTEM ====================

// Global variations map (loaded from server)
let VARIATIONS = {};

// Load variations manifest at game start
(async function loadVariations() {
  try {
    const response = await fetch('/scan_variations.php');
    if (response.ok) {
      VARIATIONS = await response.json();
      console.log('Variations loaded:', Object.keys(VARIATIONS).length, 'videos with variations');
    }
  } catch (e) {
    console.warn('Could not load variations:', e);
  }
})();

// Get video with random variation support
// Usage: getVideo('trump/map/blackopps3.webm') -> returns random variation if exists
function getVideo(pathOrArray) {
  // If already an array, pick random (existing behavior)
  if (Array.isArray(pathOrArray)) {
    return pathOrArray[Math.floor(Math.random() * pathOrArray.length)];
  }

  // If string, check for variations
  if (typeof pathOrArray === 'string') {
    const relativePath = pathOrArray.replace(BASE, '');
    if (VARIATIONS[relativePath]) {
      const options = VARIATIONS[relativePath];
      return BASE + options[Math.floor(Math.random() * options.length)];
    }
    return pathOrArray;
  }

  // If object with webm property (blackops format)
  if (pathOrArray && pathOrArray.webm) {
    return getVideo(pathOrArray.webm);
  }

  return pathOrArray;
}

// ==================== ASSET VALIDATION & FALLBACKS ====================

// Enable asset validation on page load (set false for production)
const VALIDATE_ASSETS_ON_LOAD = false;

// Fallback placeholder videos (1x1 transparent WebM data URL)
const FALLBACK_VIDEO = 'data:video/webm;base64,GkXfo0AgQoaBAUL3gQFC8oEEQvOBCEKCQAR3ZWJtQoeBAkKFgQIYU4BnQI0VSalmQCgq17FAAw9CQE2AQAZ3aGFtbXlXQUAGd2hhbW15RIlACECPQAAAAAAAFlSua0AxrkAu14EBY8WBAZyBACK1nEADdW5khkAFVl9WUDglhohAA1ZQOIOBAeBABrCBCLqBCB9DtnVAIueBAKNAHIEAAIAwAQCdASoAAQABAAAAAAAAAAAAAAAAAA==';
const FALLBACK_IMAGE = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect width="100" height="100" fill="%23222"/%3E%3Ctext x="50" y="50" text-anchor="middle" fill="%23888" font-family="Arial" font-size="12"%3E404%3C/text%3E%3C/svg%3E';

// Asset validation results cache
const assetValidationCache = new Map();
let assetValidationInProgress = false;

/**
 * Validate that a single asset URL is accessible
 * @param {string} url - Asset URL to validate
 * @returns {Promise<boolean>} - True if asset is accessible
 */
async function validateAsset(url) {
  // Check cache first
  if (assetValidationCache.has(url)) {
    return assetValidationCache.get(url);
  }

  try {
    const response = await fetch(url, { method: 'HEAD', cache: 'no-cache' });
    const isValid = response.ok;
    assetValidationCache.set(url, isValid);

    if (!isValid) {
      console.warn(`Asset validation failed: ${url} (${response.status})`);
    }

    return isValid;
  } catch (error) {
    console.error(`Asset validation error: ${url}`, error.message);
    assetValidationCache.set(url, false);
    return false;
  }
}

/**
 * Validate all critical game assets
 * Call this function from console or on game init for debugging
 * @returns {Promise<Object>} - Validation results summary
 */
async function validateAssets() {
  if (assetValidationInProgress) {
    console.warn('Asset validation already in progress');
    return { status: 'in_progress' };
  }

  assetValidationInProgress = true;
  console.log('Starting asset validation...');

  const results = {
    total: 0,
    valid: 0,
    invalid: 0,
    failed: []
  };

  // Validate sample assets from each category
  const criticalAssets = [
    ...ASSETS.trump.slice(0, 3),  // Sample 3 trump videos
    ...ASSETS.maps.slice(0, 3),   // Sample 3 map videos
    ASSETS.wheel[0],              // Sample wheel video
    ASSETS.dice[0].v,             // Sample dice video
    ASSETS.goodnight[0],          // Sample goodnight video
    SPECIAL_VIDEOS.trumpOld,      // Special videos
    SPECIAL_VIDEOS.trumpLaugh
  ];

  for (const assetPath of criticalAssets) {
    const url = assetPath.startsWith('http') ? assetPath : `${BASE}${assetPath}`;
    results.total++;

    const isValid = await validateAsset(url);
    if (isValid) {
      results.valid++;
    } else {
      results.invalid++;
      results.failed.push(url);
    }
  }

  assetValidationInProgress = false;

  console.log(`Asset validation complete: ${results.valid}/${results.total} valid`);
  if (results.invalid > 0) {
    console.error(`${results.invalid} assets failed validation:`, results.failed);
  }

  return results;
}

/**
 * Get fallback asset for a failed load
 * @param {string} assetType - Type of asset ('video', 'image')
 * @returns {string} - Fallback data URL
 */
function getFallbackAsset(assetType = 'video') {
  return assetType === 'image' ? FALLBACK_IMAGE : FALLBACK_VIDEO;
}

// Auto-validate assets on page load if enabled
if (typeof document !== 'undefined' && VALIDATE_ASSETS_ON_LOAD) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => validateAssets(), 2000);
    });
  } else {
    setTimeout(() => validateAssets(), 2000);
  }
}

// ==================== ENDING DEFINITIONS ====================
// Priority-based ending system - highest priority match wins
// To add a new ending: add entry here, CSS theme in trump-endings.html, category in categories object
const ENDING_DEFS = [
  { id: 'saint',      priority: 1, condition: (G) => G.purity >= 96 && !G.usedAggressive && !G.nukeUsed && G.trumpHP >= 80 },
  { id: 'old',        priority: 2, condition: (G) => G.trumpAge >= 90 },
  { id: 'aggressive', priority: 3, condition: (G) => G.usedAggressive === true },
  { id: 'peaceful',   priority: 99 } // Default fallback - no condition needed
];

// ==================== DIFFICULTY SCALING ====================
// Base difficulty for Term 1 (10x harder than original)
// Term 2 adds extra 7x for total of 17x
const BASE_DIFFICULTY = 10;
const TERM2_DIFFICULTY = 17;

// Dynamic function to get current difficulty based on term
function getDifficultyScale() {
  return (G && G.term === 2) ? TERM2_DIFFICULTY : BASE_DIFFICULTY;
}

// Special event videos
const SPECIAL_VIDEOS = {
  trumpOld: `${BASE}old.webm`,  // Plays when Trump hits 98
  trumpLaugh: `${BASE}laughing.webm`  // Plays on success moments - small HP boost
};

// ==================== ASSET PATHS ====================
const ASSETS = {
  trump: Array.from({length:10},(_,i)=>`${BASE}Trumpsnes${i+1}.webm`),
  maps: Array.from({length:11},(_,i)=>`${BASE}map/map${i}.webm`),
  wheel: ['jesus','zombie','sunami','plague','petulance','nazi','famine','alien','asteroid','biowar','locus','skynet','timetravel','volcanoe','russiawins','russialoose','chinawins','chinaloose'].map(n=>`${BASE}wheel/${n}.webm`),
  dice: [
    {v:`${BASE}dice/0.webm`,n:0},{v:`${BASE}dice/1.webm`,n:1},{v:`${BASE}dice/2.webm`,n:2},{v:`${BASE}dice/2b.webm`,n:2},
    {v:`${BASE}dice/3.webm`,n:3},{v:`${BASE}dice/4.webm`,n:4},{v:`${BASE}dice/5.webm`,n:5},{v:`${BASE}dice/8.webm`,n:8},
    {v:`${BASE}dice/8b.webm`,n:8},{v:`${BASE}dice/8c.webm`,n:8},{v:`${BASE}dice/9.webm`,n:9},{v:`${BASE}dice/9b.webm`,n:9},
    {v:`${BASE}dice/9c.webm`,n:9},{v:`${BASE}dice/10.webm`,n:10},{v:`${BASE}dice/10b.webm`,n:10},{v:`${BASE}dice/11.webm`,n:11}
  ],
  goodnight: ['endturn.webm','goodnight1.webm','goodnight2.webm','goodnight3.webm','goodnight4.webm','goodnight5.webm','goodnight6.webm','goodnight7.webm','goodnight8.webm','goodnight9.webm','goodnight10.webm'].map(n=>BASE+n),
  deepstate: Array.from({length:10},(_,i)=>`${BASE}deepstate${i+1}.webm`),
  advisorPlay: Array.from({length:6},(_,i)=>`${BASE}advisor/play${i+1}.webm`).concat([`${BASE}advisor/play6.webm`]),
  advisorAdvice: {
    0:[`${BASE}advisor/advisor6.webm`,`${BASE}advisor/advisor7.webm`],
    1:[`${BASE}advisor/advice10.webm`,`${BASE}advisor/advice11.webm`,`${BASE}advisor/advice12.webm`],
    2:[`${BASE}advisor/advisor2.webm`,`${BASE}advisor/advisor11.webm`,`${BASE}advisor/advisor5.webm`],
    3:[`${BASE}advisor/advisor9.webm`,`${BASE}advisor/advisor8.webm`],
    4:[`${BASE}advisor/advisor4.webm`,`${BASE}advisor/advisor13.webm`],
    5:[`${BASE}advisor/advice13.webm`,`${BASE}advisor/advice14.webm`],
    6:[`${BASE}advisor/advice16.webm`,`${BASE}advisor/advice17.webm`],
    7:[`${BASE}advisor/advice16.webm`,`${BASE}advisor/advice17.webm`]
  },
  // Black ops with variation support - webm can be array for random selection
  blackops: [
    {gif:`${BASE}map/blackopps1.gif`, webm:`${BASE}map/blackopps1.webm`},
    {gif:`${BASE}map/blackopps2.gif`, webm:`${BASE}map/blackopps2.webm`},
    {gif:`${BASE}map/blackopps3.gif`, webm:[`${BASE}map/blackopps3.webm`, `${BASE}map/blackopps3b.webm`]},
    {gif:`${BASE}map/blackopps4.gif`, webm:`${BASE}map/blackopps4.webm`},
    {gif:`${BASE}map/blackopps5.gif`, webm:`${BASE}map/blackopps5.webm`},
    {gif:`${BASE}map/blackopps6.gif`, webm:[`${BASE}map/blackopps6.webm`, `${BASE}map/blackopps6b.webm`]},
    {gif:`${BASE}map/blackopps7.gif`, webm:`${BASE}map/blackopps7.webm`}
  ],
  trumpCards: [
    {id:'king',v:`${BASE}king1.webm`,name:'KING TRUMP',desc:'+HP, +Purity',fx:()=>{G.trumpHP=Math.min(200,G.trumpHP+15);G.purity+=5}},
    {id:'evil',v:`${BASE}evil1.webm`,name:'FEMINISM SURGE',desc:'Feminism rises!',fx:()=>{const s=getDifficultyScale();G.feminism=Math.min(100,G.feminism+60/s);G.christianity=Math.max(0,G.christianity-60/s)}},
    {id:'blackswan',v:`${BASE}blackswan.webm`,name:'BLACK SWAN',desc:'Muslim Threat rises!',fx:()=>{const s=getDifficultyScale();G.muslimThreat=Math.min(100,G.muslimThreat+40/s);G.deepStateHP+=15/s}},
    {id:'victimwin',v:`${BASE}victimcard.webm`,name:'VICTIM CARD WIN',desc:'+Purity',fx:()=>{const s=getDifficultyScale();G.purity+=15/s;G.deepStateHP-=10/s}},
    {id:'victimlose',v:`${BASE}victimcardb.webm`,name:'VICTIM BACKFIRE',desc:'-Purity, -HP',fx:()=>{const s=getDifficultyScale();G.purity-=10/s;G.trumpHP-=15/s}},
    {id:'gaywin',v:`${BASE}gaycard.webm`,name:'GAY CARD WIN',desc:'-Feminism',fx:()=>{const s=getDifficultyScale();G.purity+=10/s;G.feminism=Math.max(0,G.feminism-20/s)}},
    {id:'gaylose',v:`${BASE}gaycardb.webm`,name:'GAY CARD BACKFIRE',desc:'+DeepState',fx:()=>{const s=getDifficultyScale();G.deepStateHP+=20/s;G.optics='BAD'}},
    {id:'race',v:`${BASE}racecard.webm`,name:'RACE CARD',desc:'-Purity, +DS',fx:()=>{const s=getDifficultyScale();G.purity-=15/s;G.deepStateHP+=25/s;G.optics='BAD'}}
  ],
  // Wide format notification videos
  notificationVideos: [
    `${BASE}sexyrape2.webm`,
    `${BASE}gay.webm`,
    `${BASE}gamergate.webm`
  ],

  // Character/Weirdo videos organized by group
  weirdoes: {
    muslim: [
      `${BASE}weirdoes/muslim/1.webm`,
      `${BASE}weirdoes/muslim/2.webm`
    ],
    feminist: [
      `${BASE}weirdoes/feminist/1.webm`,
      `${BASE}weirdoes/feminist/2.webm`
    ],
    israel: [
      `${BASE}weirdoes/israel/1.webm`
    ],
    christianity: [
      // Empty - no duplicate gigachad
    ],
    chad: [
      `${BASE}weirdoes/chad/1.webm`,
      `${BASE}weirdoes/chad/2.webm`
    ],
    tradwife: [
      `${BASE}weirdoes/tradwife/1.webm`,
      `${BASE}weirdoes/tradwife/2.webm`
    ],
    soy: [
      `${BASE}weirdoes/soy/1.webm`,
      `${BASE}weirdoes/soy/2.webm`
    ],
    wojak: [
      `${BASE}weirdoes/wojak/1.webm`
    ],
    blacknormy: [
      `${BASE}weirdoes/blacknormy/1.webm`
    ],
    dumptruck: [
      `${BASE}weirdoes/dumptruck/1.webm`
    ]
  }
};

// ==================== ACTION DEFINITIONS ====================
// p = purity, d = debt, t = trumpHP, ds = deepStateHP, cash = oil money, muslim = muslimThreat change
const ACTIONS = {
  oil:     { p:0,  d:2,  t:0,   ds:0,   v:`${BASE}oilcash.webm`,  cash:500,  muslim:0   },
  home:    { p:5,  d:1,  t:0,   ds:-5,  v:`${BASE}home.webm`,     cash:-200, muslim:0   },
  psyop:   { p:0,  d:0,  t:0,   ds:-8,  v:`${BASE}psyopp.webm`,   cash:-300, muslim:0   },
  aid:     { p:0,  d:-3, t:0,   ds:0,   v:`${BASE}defund.webm`,   cash:0,    muslim:0   },
  war:     { p:-5, d:5,  t:-5,  ds:0,   v:`${BASE}crusade.webm`,  cash:-300, muslim:-15 },
  audit:   { p:0,  d:0,  t:-5,  ds:-15, v:`${BASE}audit.webm`,    cash:0,    muslim:0   },
  drone:   { p:-3, d:0,  t:0,   ds:0,   v:`${BASE}drone.webm`,    cash:-400, muslim:-5  },
  loan:    { p:0,  d:4,  t:0,   ds:0,   v:`${BASE}elon.webm`,     cash:1000, muslim:0   },
  meantweet:{ p:0, d:0,  t:0,   ds:0,   v:`${BASE}meantweets.webm`,cash:0,   muslim:0   }
};

// ==================== DEEPSTATE ATTACKS ====================
// These trigger as random events during gameplay
// NOTE: HP damage bypasses difficulty scaling for real impact!
const ATTACKS = [
  { t:'MEDIA LIES!',      m:'Fake news strikes again!',    img:BASE+'sexyrape2.webm',  hp:-8,  ds:5,  type:'tweet'    },
  { t:'COMMIE PLOT!',     m:'Socialist agenda exposed!',   img:BASE+'rollover/5.gif',  hp:-12, ds:8,  type:'bulletin' },
  { t:'SWAMP ATTACK!',    m:'Deep state fights back!',     img:BASE+'rollover/4.gif',  hp:-10, ds:6,  type:'email'    },
  { t:'BIG PHARMA!',      m:'They want you sick!',         img:BASE+'rollover/7.gif',  hp:-6,  ds:10, type:'postit'   },
  { t:'ANTIFA RIOT!',     m:'Cities burning!',             img:BASE+'rollover/2.gif',  hp:-15, ds:7,  type:'bulletin' },
  { t:'BIG TECH!',        m:'Censorship incoming!',        img:BASE+'rollover/3.gif',  hp:-10, ds:8,  type:'tweet'    },
  { t:'FED ATTACK!',      m:'Printing more money!',        img:BASE+'rollover/6.gif',  hp:-8,  ds:6,  type:'email'    },
  { t:'OIL CRISIS!',      m:'Energy prices surge!',        img:BASE+'rollover/1.gif',  hp:-7,  ds:5,  type:'text'     },
  { t:'IMPEACHMENT!',    m:'Congress moves to impeach! -10 PURITY!', img:BASE+'rollover/5.gif', hp:-25, ds:15, type:'bulletin', impeachment:true }
];

// Passive damage per round from Deep State influence
const PASSIVE_DAMAGE_PER_ROUND = 3;

// ==================== VIBRATION PATTERNS ====================
const VIBES = {
  tap: 80,
  success: [120, 60, 120, 60, 250],
  fail: [250, 100, 250],
  attack: [120, 60, 120, 60, 120],
  nuke: [400, 200, 400, 200, 1000, 400, 2000],
  explosion: [250, 100, 400, 100, 600],
  cardFlip: [80, 100, 80, 100, 250],
  emergency: [250, 250, 250, 250, 250, 250],
  wheel: [120, 100, 120, 100, 120, 100, 120, 100, 400],
  powerup: [80, 80, 150],
  roundEnd: [250, 200, 400, 300, 800],
  warning: [400, 200, 400]
};

// ==================== NOTIFICATION SETTINGS ====================
const NOTIFICATION_CONFIG = {
  // Which notification style to use for each attack type
  // Options: 'tweet', 'email', 'text', 'postit', 'bulletin', 'legacy'
  defaultStyle: 'email',

  // Do Not Disturb mode - when true, skip popups and flash stats instead
  dndMode: false,

  // How long notifications stay visible (ms)
  displayDuration: 3000,

  // Animation style for stat flashes in DND mode
  flashDuration: 500,
  flashCount: 3
};

// ==================== WHEEL OUTCOME EFFECTS ====================
// Each wheel outcome and its impact on game stats
const WHEEL_EFFECTS = {
  jesus:        { name: 'JESUS RETURNS',   good: true,  hp: 50,  ds: -30, purity: 30,  msg: 'DIVINE INTERVENTION!' },
  timetravel:   { name: 'TIME TRAVEL',     good: true,  hp: 30,  ds: -20, purity: 20,  moves: 5, msg: 'BACK TO THE FUTURE!' },
  zombie:       { name: 'ZOMBIE PLAGUE',   good: false, hp: -25, ds: 15,  purity: -15, msg: 'THE DEAD RISE!' },
  sunami:       { name: 'MEGA TSUNAMI',    good: false, hp: -20, ds: 10,  purity: -10, msg: 'COASTAL DEVASTATION!' },
  plague:       { name: 'SUPER PLAGUE',    good: false, hp: -30, ds: 20,  purity: -20, msg: 'PANDEMIC CHAOS!' },
  petulance:    { name: 'PESTILENCE',      good: false, hp: -15, ds: 10,  purity: -10, msg: 'BIBLICAL DOOM!' },
  nazi:         { name: 'NAZI UPRISING',   good: false, hp: -20, ds: 25,  purity: -25, msg: 'HISTORY REPEATS!' },
  famine:       { name: 'GLOBAL FAMINE',   good: false, hp: -25, ds: 15,  purity: -15, msg: 'CROPS FAIL!' },
  alien:        { name: 'ALIEN INVASION',  good: false, hp: -35, ds: 30,  purity: -20, msg: 'THEY ARE HERE!' },
  asteroid:     { name: 'ASTEROID IMPACT', good: false, hp: -40, ds: 25,  purity: -30, msg: 'EXTINCTION EVENT!' },
  biowar:       { name: 'BIO WARFARE',     good: false, hp: -30, ds: 20,  purity: -15, msg: 'CHEMICAL ATTACK!' },
  locus:        { name: 'LOCUST SWARM',    good: false, hp: -15, ds: 10,  purity: -10, msg: 'CROPS DEVOURED!' },
  skynet:       { name: 'SKYNET AWAKENS',  good: false, hp: -35, ds: 35,  purity: -25, msg: 'AI TAKEOVER!' },
  volcanoe:     { name: 'SUPER VOLCANO',   good: false, hp: -30, ds: 20,  purity: -20, msg: 'YELLOWSTONE ERUPTS!' },
  russiawins:   { name: 'RUSSIA WINS',     good: false, hp: -20, ds: 30,  purity: -30, msg: 'COLD WAR LOST!' },
  russialoose:  { name: 'RUSSIA FALLS',    good: true,  hp: 10,  ds: -15, purity: 15,  msg: 'ENEMY DEFEATED!' },
  chinawins:    { name: 'CHINA WINS',      good: false, hp: -25, ds: 35,  purity: -35, msg: 'RED DAWN!' },
  chinaloose:   { name: 'CHINA FALLS',     good: true,  hp: 15,  ds: -20, purity: 20,  msg: 'TRADE WAR WON!' }
};

// ==================== BLACK OPS EFFECTS ====================
// Each covert operation and its impact - HP boost for emergency recovery!
const BLACK_OPS_EFFECTS = [
  { name: 'REGIME CHANGE',    msg: 'DICTATOR ELIMINATED! +15 HP',  hp: 15, ds: -30, purity: 15, cash: -800  },
  { name: 'ASSET EXTRACTION', msg: 'TARGET SECURED! +10 HP',       hp: 10, ds: -20, purity: 10, cash: -400  },
  { name: 'FALSE FLAG',       msg: 'BLAME SHIFTED! +18 HP',        hp: 18, ds: -35, purity: 20, cash: -600  },
  { name: 'CYBER ATTACK',     msg: 'SYSTEMS COMPROMISED! +12 HP',  hp: 12, ds: -25, purity: 12, cash: -300  },
  { name: 'DRONE STRIKE',     msg: 'TARGET NEUTRALIZED! +8 HP',    hp: 8,  ds: -28, purity: 8,  cash: -500  },
  { name: 'WETWORK',          msg: 'NO WITNESSES! +20 HP',         hp: 20, ds: -32, purity: 18, cash: -700  },
  { name: 'SHADOW COUP',      msg: 'GOVERNMENT TOPPLED! +25 HP',   hp: 25, ds: -40, purity: 25, cash: -1000 }
];

// ==================== NUKE TARGETS ====================
const NUKE_TARGETS = [
  { target: 'SOMALIA', tagline: 'NOTHING OF VALUE LOST' },
  { target: 'IRAN', tagline: 'DEMOCRACY DELIVERED' },
  { target: 'NORTH KOREA', tagline: 'PROBLEM SOLVED' },
  { target: 'SYRIA', tagline: 'FREEDOM INCOMING' },
  { target: 'VENEZUELA', tagline: 'OIL SECURED' },
  { target: 'AFGHANISTAN', tagline: 'MISSION ACCOMPLISHED' },
  { target: 'IRAQ', tagline: 'AGAIN' },
  { target: 'CHINA', tagline: 'TRADE WAR WON' },
  { target: 'RUSSIA', tagline: 'COLD WAR OVER' },
  { target: 'MEXICO', tagline: 'WALL NOT NEEDED' }
];

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    BASE,
    ASSETS,
    ACTIONS,
    ATTACKS,
    VIBES,
    NOTIFICATION_CONFIG,
    WHEEL_EFFECTS,
    BLACK_OPS_EFFECTS,
    validateAssets,
    validateAsset,
    getFallbackAsset
  };
}
