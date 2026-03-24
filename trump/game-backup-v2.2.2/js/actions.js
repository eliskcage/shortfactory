/* ==================== GAME ACTIONS ====================
 * All player actions and game mechanics
 */

// DOM element cache to avoid repeated queries
// Initialized lazily on first access after DOM ready
const CACHED_DOM = {
  get disasterOverlay() { return this._disasterOverlay || (this._disasterOverlay = document.getElementById('disaster-overlay')); },
  get blackopsAlertIcon() { return this._blackopsAlertIcon || (this._blackopsAlertIcon = document.getElementById('blackops-alert-icon')); },
  get blackopsAlertText() { return this._blackopsAlertText || (this._blackopsAlertText = document.getElementById('blackops-alert-text')); },
  get mapVideo() { return this._mapVideo || (this._mapVideo = document.getElementById('map-video')); },
  get emergencyDrop() { return this._emergencyDrop || (this._emergencyDrop = document.getElementById('emergency-drop')); },
  get wheelOverlay() { return this._wheelOverlay || (this._wheelOverlay = document.getElementById('wheel-overlay')); },
  get blackopsOverlay() { return this._blackopsOverlay || (this._blackopsOverlay = document.getElementById('blackops-overlay')); },
  get phone() { return this._phone || (this._phone = document.getElementById('phone')); },
  get fullscreenVideo() { return this._fullscreenVideo || (this._fullscreenVideo = document.getElementById('fullscreen-video')); }
};

// ==================== SPEED BONUS ====================

function getSpeedBonus() {
  const now = Date.now();
  const timeSinceLastAction = now - lastActionTime;

  // First action of the game - no bonus
  if (lastActionTime === 0) {
    lastActionTime = now;
    return { mult: 1, label: '' };
  }

  lastActionTime = now;

  if (timeSinceLastAction < SPEED_THRESHOLDS.blazing) {
    if (G.gameHistory) G.gameHistory.speedBonuses.blazing++;
    return { mult: 3, label: 'BLAZING! 3X' };
  } else if (timeSinceLastAction < SPEED_THRESHOLDS.fast) {
    if (G.gameHistory) G.gameHistory.speedBonuses.fast++;
    return { mult: 2, label: 'FAST! 2X' };
  } else if (timeSinceLastAction < SPEED_THRESHOLDS.quick) {
    if (G.gameHistory) G.gameHistory.speedBonuses.quick++;
    return { mult: 1.5, label: 'QUICK! 1.5X' };
  }

  return { mult: 1, label: '' };
}

function showSpeedBonus(label) {
  if (!label) return;

  const boostAnnounce = document.getElementById('boost-announce');
  const boostText = document.getElementById('boost-text');
  if (!boostAnnounce || !boostText) return;
  boostText.textContent = '⚡ ' + label + ' ⚡';
  boostAnnounce.classList.add('show');

  // Play speed sound
  const clickSfx = document.getElementById('drone-sound');
  if (clickSfx) { clickSfx.currentTime = 0; clickSfx.play().catch(() => {}); }

  // Trump laughs on blazing speed! (3x bonus)
  if (label.includes('BLAZING')) {
    setTimeout(() => playTrumpLaugh(3), 500);
  }

  setTimeout(() => {
    boostAnnounce.classList.remove('show');
  }, 1000);
}

// ==================== SOUND HELPERS ====================

function playClickSound(action) {
  let sfxId = 'click-sound'; // Default sound for most buttons

  // Drone button gets special sound
  if (action === 'drone') {
    sfxId = 'drone-sound';
  }
  // Home (email) button and wheel get breath sound
  else if (action === 'home' || action === 'wheel') {
    sfxId = 'breath-sound';
  }

  const sfx = document.getElementById(sfxId);
  if (sfx) {
    sfx.currentTime = 0;
    sfx.play().catch(() => {});
  }
}

// ==================== ARCADE POPUP ====================

function showArcadePopup(text, color, soundType) {
  // Get or create popup element
  let popup = document.getElementById('arcade-popup');
  if (!popup) {
    popup = document.createElement('div');
    popup.id = 'arcade-popup';
    popup.className = 'arcade-popup';
    document.getElementById('phone').appendChild(popup);
  }

  // Set text and color
  popup.textContent = text;
  popup.style.color = color === 'green' ? '#0f0' : '#f00';
  popup.classList.remove('show');

  // Force reflow to restart animation
  void popup.offsetWidth;

  popup.classList.add('show');

  // Play appropriate sound
  let sfx;
  if (soundType === 'sneaky') {
    // Fast x5 click - use success sound
    sfx = document.getElementById('success-sound');
  } else if (soundType === 'lightning') {
    // x10 powerup - use drone sound (has that electric/power quality)
    sfx = document.getElementById('drone-sound');
  }

  if (sfx) {
    sfx.currentTime = 0;
    sfx.volume = 1.0;
    sfx.play().catch(() => {});
  }

  // Remove after animation
  setTimeout(() => {
    popup.classList.remove('show');
  }, 2000);
}

// ==================== BUTTON ACTIONS ====================

function handleButtonClick(btn) {
  if (btn.classList.contains('locked')) return;

  const action = btn.dataset.action;
  const idx = parseInt(btn.dataset.idx);

  vibrate(VIBES.tap);
  playClickSound(action);

  // Check for glow powerup - starts tap mini-game for up to 10x (max 2 per game)
  if (powerups[idx] === 'glow') {
    if (boostsUsedThisGame >= MAX_BOOSTS_PER_GAME) {
      // Out of boosts - just do normal action and clear powerup
      clearPowerup(idx);
      showNews('NO BOOSTS LEFT!');
      doAction(action, 1, false);
      return;
    }
    startPowerupTapGame(action, idx);
    return;
  }

  if (action === 'meantweet') {
    startMeanTweets();
    return;
  }

  // Quick tap = action only, NO video
  doAction(action, 1, false);
}

// ==================== POWERUP TAP GAME ====================

function startPowerupTapGame(action, idx) {
  // Clear any existing timers
  clearInterval(powerupTapTimer);
  clearInterval(powerupTapDecayTimer);

  powerupTapActive = true;
  powerupTapProgress = 0;
  powerupTapAction = action;
  powerupTapIdx = idx;

  const overlay = document.getElementById('powerup-tap-overlay');
  if (!overlay) return;
  overlay.classList.add('show');

  const tapAction = document.getElementById('powerup-tap-action');
  const tapFill = document.getElementById('powerup-tap-fill');
  const tapMult = document.getElementById('powerup-tap-mult');
  const tapTimer = document.getElementById('powerup-tap-timer');
  if (tapAction) tapAction.textContent = action.toUpperCase();
  if (tapFill) tapFill.style.width = '0%';
  if (tapMult) tapMult.textContent = '1';

  let timeLeft = 3;
  if (tapTimer) tapTimer.textContent = timeLeft;

  // Decay the progress bar
  powerupTapDecayTimer = setInterval(() => {
    if (!powerupTapActive) return;

    // Pause decay during fullscreen video playback
    const fsVideo = document.getElementById('fullscreen-video');
    if (fsVideo && fsVideo.classList.contains('show')) return;

    powerupTapProgress = Math.max(0, powerupTapProgress - 2);
    updatePowerupTapBar();
  }, 50);

  // Countdown timer
  powerupTapTimer = setInterval(() => {
    // Pause countdown during fullscreen video playback
    const fsVideo = document.getElementById('fullscreen-video');
    if (fsVideo && fsVideo.classList.contains('show')) return;

    timeLeft--;
    document.getElementById('powerup-tap-timer').textContent = timeLeft;
    if (timeLeft <= 0) {
      endPowerupTapGame();
    }
  }, 1000);

  vibrate(VIBES.powerup);
}

// George Floyd "I can't breathe" - fires on ANY george.png tap
let georgeTapCount = 0;
let georgeSpeechReady = false;
const georgeLines = [
  "I can't breathe",
  "I can't breathe man",
  "please",
  "I can't breathe",
  "mama",
  "I can't breathe",
  "please man",
  "they're gonna kill me",
  "I can't breathe"
];

// Mobile needs speech unlocked on first user gesture
document.addEventListener('touchstart', function unlockSpeech() {
  if (window.speechSynthesis) {
    const dummy = new SpeechSynthesisUtterance('');
    dummy.volume = 0;
    window.speechSynthesis.speak(dummy);
    georgeSpeechReady = true;
  }
  document.removeEventListener('touchstart', unlockSpeech);
}, { once: true });

// Also unlock on click for desktop
document.addEventListener('click', function unlockSpeechClick() {
  if (window.speechSynthesis && !georgeSpeechReady) {
    const dummy = new SpeechSynthesisUtterance('');
    dummy.volume = 0;
    window.speechSynthesis.speak(dummy);
    georgeSpeechReady = true;
  }
  document.removeEventListener('click', unlockSpeechClick);
}, { once: true });

function georgeSpeak() {
  if (!window.speechSynthesis) return;

  // Chrome bug: speech can get stuck, resume it
  window.speechSynthesis.cancel();
  window.speechSynthesis.resume();

  const line = georgeLines[georgeTapCount % georgeLines.length];
  georgeTapCount++;

  const utter = new SpeechSynthesisUtterance(line);
  utter.pitch = 0.4 + Math.random() * 0.4;  // Low pitch, slight variation
  utter.rate = 0.7 + Math.random() * 0.3;   // Slow, gasping
  utter.volume = 1.0;
  window.speechSynthesis.speak(utter);
}

// Global listener: click on george.png triggers speech (except wheel george)
document.addEventListener('click', (e) => {
  const img = e.target.closest('img[src*="george"], .george-btn');
  if (img && !img.closest('.wheel-overlay')) georgeSpeak();
});

// Long-press george button in wheel = close wheel
(function() {
  let wheelGeorgeTimer = null;
  function getWheelGeorge(e) {
    const t = e.target.closest('.george-btn');
    return (t && t.closest('.wheel-overlay')) ? t : null;
  }
  document.addEventListener('mousedown', (e) => {
    if (getWheelGeorge(e)) {
      if (wheelGeorgeTimer) clearTimeout(wheelGeorgeTimer);
      wheelGeorgeTimer = setTimeout(() => {
        clearInterval(wheelTimer);
        document.getElementById('wheel-overlay').classList.remove('show');
        wheelGeorgeTimer = null;
      }, 800);
    }
  });
  document.addEventListener('touchstart', (e) => {
    if (getWheelGeorge(e)) {
      if (wheelGeorgeTimer) clearTimeout(wheelGeorgeTimer);
      wheelGeorgeTimer = setTimeout(() => {
        clearInterval(wheelTimer);
        document.getElementById('wheel-overlay').classList.remove('show');
        wheelGeorgeTimer = null;
      }, 800);
    }
  });
  document.addEventListener('mouseup', () => { if (wheelGeorgeTimer) clearTimeout(wheelGeorgeTimer); });
  document.addEventListener('touchend', () => { if (wheelGeorgeTimer) clearTimeout(wheelGeorgeTimer); });
})();

function tapPowerup() {
  if (!powerupTapActive) return;

  powerupTapProgress = Math.min(100, powerupTapProgress + 12);
  updatePowerupTapBar();
  vibrate(VIBES.tap);

  // Hit max - end immediately with full bonus
  if (powerupTapProgress >= 100) {
    endPowerupTapGame();
  }
}

function updatePowerupTapBar() {
  document.getElementById('powerup-tap-fill').style.width = powerupTapProgress + '%';

  // Calculate multiplier based on progress (1x to 10x)
  let mult = 1;
  if (powerupTapProgress >= 90) mult = 10;
  else if (powerupTapProgress >= 70) mult = 7;
  else if (powerupTapProgress >= 50) mult = 5;
  else if (powerupTapProgress >= 30) mult = 3;
  else if (powerupTapProgress >= 10) mult = 2;

  const multEl = document.getElementById('powerup-tap-mult');
  multEl.textContent = mult;

  // Color based on multiplier
  if (mult >= 10) multEl.style.color = '#00ff88';
  else if (mult >= 7) multEl.style.color = '#88ff00';
  else if (mult >= 5) multEl.style.color = '#ffff00';
  else if (mult >= 3) multEl.style.color = '#ffaa00';
  else multEl.style.color = '#ff4444';
}

function endPowerupTapGame() {
  clearInterval(powerupTapTimer);
  clearInterval(powerupTapDecayTimer);
  powerupTapActive = false;

  // Kill any pending George speech
  if (window.speechSynthesis) window.speechSynthesis.cancel();

  // Calculate final multiplier (100% = guaranteed 10x)
  let mult = 1;
  if (powerupTapProgress >= 90) mult = 10;
  else if (powerupTapProgress >= 70) mult = 7;
  else if (powerupTapProgress >= 50) mult = 5;
  else if (powerupTapProgress >= 30) mult = 3;
  else if (powerupTapProgress >= 10) mult = 2;

  // Track powerup multiplier in history
  if (G.gameHistory && mult > 1) G.gameHistory.powerupMultipliers.push(mult);

  // Clear the powerup and count boost used
  clearPowerup(powerupTapIdx);
  boostsUsedThisGame++;

  // Hide tap overlay
  document.getElementById('powerup-tap-overlay').classList.remove('show');

  // Check for first-time powerup discovery!
  const isFirstBoost = !localStorage.getItem('firstBoostUsed');
  if (isFirstBoost && mult >= 2) {
    localStorage.setItem('firstBoostUsed', 'true');
  }

  // Show SNES-style boost announcement
  const boostAnnounce = document.getElementById('boost-announce');
  const boostText = document.getElementById('boost-text');

  if (isFirstBoost && mult >= 2) {
    // First time bonus message!
    boostText.textContent = '🎮 YOU GET THIS GAME! 🎮';
    G.purity += 10; // Bonus purity for discovering the feature!
  } else {
    boostText.textContent = mult + 'X BOOST!';
  }
  boostAnnounce.classList.add('show');

  // Play success sound
  const successSfx = document.getElementById('success-sound');
  if (successSfx) {
    successSfx.currentTime = 0;
    successSfx.volume = 1.0;
    successSfx.play().catch(() => {});
  }

  // Hide announcement after animation
  setTimeout(() => {
    boostAnnounce.classList.remove('show');
  }, 1500);

  // Execute the action with earned multiplier
  const boostsLeft = MAX_BOOSTS_PER_GAME - boostsUsedThisGame;

  if (isFirstBoost && mult >= 2) {
    // First-time discovery bonus!
    vibrate(VIBES.success);
    showNews('WELCOME PATRIOT! +10 PURITY BONUS!');
    // Trump laughs at your discovery!
    setTimeout(() => playTrumpLaugh(5), 1000);
  } else if (mult >= 5) {
    vibrate(VIBES.success);
    showNews(powerupTapAction.toUpperCase() + ' x' + mult + '! (' + boostsLeft + ' BOOSTS LEFT)');
    // Show arcade-style popup for fast x5+ clicks
    if (powerupTapAction === 'oil') {
      showArcadePopup('x' + mult, 'green', 'sneaky');
    }
  } else {
    vibrate(VIBES.fail);
    showNews('x' + mult + ' ONLY! (' + boostsLeft + ' BOOSTS LEFT)');
  }

  // Never play video for fast clicks - arcade popup instead
  doAction(powerupTapAction, mult, false);
}

function handleButtonHold(btn) {
  if (btn.classList.contains('locked')) return;

  const action = btn.dataset.action;
  const idx = parseInt(btn.dataset.idx);

  vibrate(VIBES.powerup);
  playClickSound(action);

  // Long hold base multiplier is 3x (heavy attack)
  let multiplier = 3;

  // Check for throb powerup (long hold = 10x on top)
  if (powerups[idx] === 'throb') {
    multiplier = 10;
    clearPowerup(idx);
    const successSfx = document.getElementById('success-sound');
    if (successSfx) { successSfx.currentTime = 0; successSfx.play().catch(() => {}); }
    vibrate(VIBES.success);

    // Show red x10 popup for powerup cash
    if (action === 'oil') {
      showArcadePopup('x10', 'red', 'lightning');
    }
  }

  if (action === 'meantweet') {
    startMeanTweets();
    return;
  }

  // Oil uses charge mechanic - no video on long hold
  if (action === 'oil') {
    doAction(action, multiplier, false);
    return;
  }

  // Long hold = action WITH video, 3x effect
  doAction(action, multiplier, true);
}

// Update character stats based on player actions
function updateCharacterStatsFromAction(action, mult = 1) {
  if (!G.groupStats) return;

  const impact = Math.min(10, mult * 3); // Scale impact with multipliers

  // Actions affecting Muslims
  if (action === 'war' || action === 'drone') {
    G.groupStats.muslim.psychological = Math.max(0, G.groupStats.muslim.psychological - impact);
    G.groupStats.muslim.financial = Math.max(0, G.groupStats.muslim.financial - impact * 0.5);
    if (action === 'war') {
      const kills = Math.floor(mult * 100000); // War kills thousands
      G.groupStats.muslim.eventCounters.kills += Math.floor(mult);
      G.usPopulation = Math.max(0, G.usPopulation - kills);

      // Reduce poop threat when you fight back
      G.poopThreat = Math.max(0, G.poopThreat - 1);
    }
  }

  // Actions affecting Feminists
  if (action === 'psyop' || action === 'repeal') {
    G.groupStats.feminist.psychological = Math.max(0, G.groupStats.feminist.psychological - impact);
    G.groupStats.feminist.spiritual = Math.max(0, G.groupStats.feminist.spiritual - impact * 0.5);
    G.groupStats.feminist.eventCounters.rainbowHearts += Math.floor(mult); // They get more triggered
  }

  // Pro-family actions boost Christianity AND increase population (births)
  if (action === 'pro-family' || action === 'church') {
    G.groupStats.christianity.spiritual = Math.min(100, G.groupStats.christianity.spiritual + impact);
    G.groupStats.christianity.psychological = Math.min(100, G.groupStats.christianity.psychological + impact * 0.5);

    // More babies!
    const births = Math.floor(mult * 50000);
    G.usPopulation += births;
    G.groupStats.christianity.eventCounters.babies += Math.floor(mult);
  }

  // Economic actions affect financial stats
  if (action === 'tariffs' || action === 'tax-cuts') {
    G.groupStats.chad.financial = Math.min(100, G.groupStats.chad.financial + impact);
    G.groupStats.tradwife.financial = Math.min(100, G.groupStats.tradwife.financial + impact * 0.5);
  }

  // Israel aid
  if (action === 'israel-aid') {
    G.groupStats.israel.financial = Math.min(100, G.groupStats.israel.financial + impact * 2);
    G.groupStats.israel.psychological = Math.min(100, G.groupStats.israel.psychological + impact);
  }
}

function doAction(action, mult = 1, playVideo = false) {
  console.log('=== doAction called ===');
  console.log('Action:', action);
  console.log('Moves:', G.moves);
  console.log('Oil barrels before:', G.oilBarrels);

  if (G.moves <= 0) {
    showNews('NO MOVES! END TURN');
    console.log('BLOCKED: No moves - triggering end of turn');
    // Trigger end of turn if somehow we have 0 moves
    setTimeout(endOfTurn, 1000);
    return;
  }

  const cfg = ACTIONS[action];
  if (!cfg) return;

  // Check if player can afford (cash can't go below 0)
  if (cfg.cash < 0 && G.oilCash + cfg.cash < 0) {
    showNews('NOT ENOUGH CASH!');
    vibrate(VIBES.fail);
    return;
  }

  // Apply difficulty scaling to all stat changes
  const scale = getDifficultyScale();

  // Speed bonus - reward fast decisions!
  const speedBonus = getSpeedBonus();
  const totalMult = mult * speedBonus.mult;
  if (speedBonus.label) {
    showSpeedBonus(speedBonus.label);
  }

  // Israel GDP danger: if too high, Trump takes double damage
  const israelDanger = G.israelGDP > 500;
  const damageMult = israelDanger ? 2 : 1;

  G.purity = Math.max(0, Math.min(100, G.purity + (cfg.p * totalMult) / scale));
  G.debt += cfg.d / scale;
  G.trumpHP = Math.max(0, Math.min(200, G.trumpHP + (cfg.t * totalMult * damageMult) / scale));
  G.deepStateHP = Math.max(0, Math.min(100, G.deepStateHP + (cfg.ds * totalMult) / scale));

  // Oil action - gives barrels AND cash, scaled by multiplier
  if (action === 'oil') {
    console.log('*** OIL ACTION x' + totalMult + ' ***');
    G.oilBarrels += Math.max(1, Math.floor(totalMult));
    G.oilCash += cfg.cash * totalMult;
    console.log('Barrels: +' + Math.floor(totalMult) + ', Cash: +$' + Math.floor(cfg.cash * totalMult) + 'M');
  } else if (action === 'drone') {
    // Drone removes dictators - random oil boost!
    const randomBoost = Math.floor((100 + Math.random() * 900) * totalMult); // Speed bonus on oil!
    G.oilCash = Math.max(0, G.oilCash + cfg.cash + randomBoost);
    showNews('DICTATOR DOWN! +$' + randomBoost + ' OIL BOOST!');
  } else if (action === 'psyop') {
    // Psyop reduces feminism
    G.feminism = Math.max(0, G.feminism - (15 * totalMult) / scale);
    G.oilCash += cfg.cash * totalMult;

    // Show feminist hearts dropping with demotion sound (same as mean tweets)
    const feministMeter = document.getElementById('feminist-meter');
    if (feministMeter && G.groupStats && G.groupStats.feminist) {
      feministMeter.classList.remove('hidden');
      updateFeministHearts();

      // Deduct 1 heart after video starts
      setTimeout(() => {
        G.groupStats.feminist.psychological = Math.max(0, G.groupStats.feminist.psychological - 10);
        const loseSound = new Audio('https://www.shortfactory.shop/trump/looseaheart.mp3');
        loseSound.volume = 0.8;
        loseSound.play().catch(() => {});
        updateDisplay();
        updateFeministHearts(true);
        showNews('-1 ♀ HEART! PSYOP\'D!');

        // Hide meter after 2 seconds
        setTimeout(() => {
          if (feministMeter) feministMeter.classList.add('hidden');
        }, 2000);
      }, 1500);
    }
  } else if (action === 'aid') {
    // Cut aid reduces Israel GDP
    G.israelGDP = Math.max(100, G.israelGDP - (50 * totalMult));
    showNews('ISRAEL AID CUT! GDP -$' + Math.floor(50 * totalMult) + 'B');

    // Show shekel meter dropping with demotion sound
    const muslimMeter = document.getElementById('muslim-meter');
    if (muslimMeter) {
      muslimMeter.classList.remove('hidden');
      showIsraelShekels();

      // Drop a shekel after 1.5s with demotion sound
      setTimeout(() => {
        const loseSound = new Audio('https://www.shortfactory.shop/trump/looseaheart.mp3');
        loseSound.volume = 0.8;
        loseSound.play().catch(() => {});
        showIsraelShekels(true); // Animate shekel pop out
        showNews('-₪ SHEKEL DOWN!');

        // Hide meter after 2 seconds
        setTimeout(() => {
          if (muslimMeter) muslimMeter.classList.add('hidden');
          // Restore muslim label for next rotation
          const label = muslimMeter.querySelector('.threat-label');
          if (label) {
            label.textContent = '☪️';
            label.style.color = '';
            label.style.textShadow = '';
          }
        }, 2000);
      }, 1500);
    }
  } else if (action === 'audit') {
    // Audit the fed - reduces deep state's oil skimming
    G.oilCash += cfg.cash * totalMult;
  } else {
    G.oilCash += cfg.cash * totalMult;
  }

  // Ensure cash never goes below 0
  G.oilCash = Math.max(0, G.oilCash);

  // Muslim threat reduction (war/drone attacks)
  if (cfg.muslim) {
    G.muslimThreat = Math.max(0, Math.min(100, G.muslimThreat + (cfg.muslim * totalMult) / scale));
  }

  G.moves--;
  G.totalMoves++;

  // Track action in game history
  if (G.gameHistory) {
    G.gameHistory.actions[action] = (G.gameHistory.actions[action] || 0) + 1;
    if (totalMult > G.gameHistory.highestMult) G.gameHistory.highestMult = totalMult;
    if (G.purity > G.gameHistory.peakPurity) G.gameHistory.peakPurity = G.purity;
    if (G.trumpHP < G.gameHistory.lowestHP) G.gameHistory.lowestHP = G.trumpHP;
  }

  if (action === 'war') G.usedAggressive = true;

  if (playVideo && cfg.v) {
    playFullscreenVideo(cfg.v);
  }

  // Update character stats based on action
  updateCharacterStatsFromAction(action, totalMult);

  updateTrumpVideo();
  updateMapVideo();
  updateDisplay();

  showNews(mult > 1 ? action.toUpperCase() + ' x' + mult + '!' : action.toUpperCase() + '!');

  // Trump card every 10 moves
  if (G.totalMoves % 10 === 0 && Math.random() < G.cardFreqMult) {
    setTimeout(showTrumpCard, 2000);
  }

  // Random deepstate attack
  if (Math.random() < 0.25 * G.difficultyMult) {
    setTimeout(triggerDeepStateAttack, 2500);
  }

  // Random emergency drop appearance (10% chance)
  if (Math.random() < 0.1 && typeof showEmergencyDrop === 'function') {
    setTimeout(() => showEmergencyDrop('random'), 3000);
  }

  // End of turn
  if (G.moves <= 0) {
    setTimeout(endOfTurn, playVideo ? 3000 : 1500);
  }
}

// ==================== MEAN TWEETS ====================

function enableMeanTweet() {
  G.meanTweetMode = true;
  const btn = document.querySelector('[data-action="loan"]');
  if (!btn) return;
  btn.classList.add('mean-tweet-mode');
  btn.dataset.action = 'meantweet';
  const img = document.getElementById('btn-loan-img');
  if (img) img.src = BASE + 'rollover/9.gif';
  showNews('MEAN TWEET MODE!');
}

function disableMeanTweet() {
  G.meanTweetMode = false;
  const btn = document.querySelector('[data-action="meantweet"]');
  if (btn) {
    btn.classList.remove('mean-tweet-mode');
    btn.dataset.action = 'loan';
    document.getElementById('btn-loan-img').src = BASE + 'rollover/6.gif';
  }
}

function startMeanTweets() {
  // Clear any existing timers first
  clearInterval(tweetTimer);
  clearInterval(tweetDecayTimer);

  const overlay = document.getElementById('mean-tweets-overlay');
  if (!overlay) return;
  overlay.classList.add('show');
  tweetProgress = 0;
  tweetTaps = 0;
  tweetGameActive = true;

  // Hide game buttons during tweet game
  const phone = document.getElementById('phone');
  if (phone) phone.classList.add('tweet-game-active');

  // Hide slot machine icon during tweet game
  const slotIcon = document.getElementById('slot-machine-icon');
  if (slotIcon) slotIcon.style.display = 'none';

  const easyFactor = 1 + Math.random() * 1.3;
  let timer = Math.floor(7 * easyFactor);
  const decayRate = 3 / easyFactor;
  currentTapPower = Math.floor(8 * easyFactor);

  document.getElementById('tweet-timer').textContent = timer;
  document.getElementById('tweet-count').textContent = '0';
  document.getElementById('tweet-progress-fill').style.width = '0%';

  tweetDecayTimer = setInterval(() => {
    if (!tweetGameActive) return;
    tweetProgress = Math.max(0, tweetProgress - decayRate);
    updateTweetBar();
  }, 50);

  tweetTimer = setInterval(() => {
    timer--;
    document.getElementById('tweet-timer').textContent = timer;
    if (timer <= 0) {
      clearInterval(tweetTimer);
      clearInterval(tweetDecayTimer);
      tweetGameActive = false;
      endMeanTweets(false);
    }
  }, 1000);
}

function tapTweet() {
  if (!tweetGameActive) return;
  tweetTaps++;
  tweetProgress = Math.min(100, tweetProgress + currentTapPower);
  document.getElementById('tweet-count').textContent = tweetTaps;
  updateTweetBar();
  vibrate(VIBES.tap);

  if (tweetProgress >= 100) {
    clearInterval(tweetDecayTimer);
    clearInterval(tweetTimer);
    tweetGameActive = false;
    vibrate(VIBES.success);
    endMeanTweets(true);
  }
}

function updateTweetBar() {
  const bar = document.getElementById('tweet-progress-fill');
  const btn = document.getElementById('tweet-btn');

  bar.style.width = tweetProgress + '%';
  if (tweetProgress < 30) bar.style.background = 'linear-gradient(90deg,#f00,#f66)';
  else if (tweetProgress < 70) bar.style.background = 'linear-gradient(90deg,#f60,#ff0)';
  else bar.style.background = 'linear-gradient(90deg,#0f0,#0ff)';

  // Update button glow based on progress
  btn.classList.remove('glow-25', 'glow-50', 'glow-75', 'glow-100');
  if (tweetProgress >= 90) btn.classList.add('glow-100');
  else if (tweetProgress >= 65) btn.classList.add('glow-75');
  else if (tweetProgress >= 40) btn.classList.add('glow-50');
  else if (tweetProgress >= 20) btn.classList.add('glow-25');
}

// ⚠️ DO NOT DELETE - Update feminist hearts display for tweet game
// Hearts honestly represent psychological health: 1 heart = 10 points
function updateFeministHearts(animate = false) {
  const feministMeter = document.getElementById('feminist-meter');
  if (!feministMeter || !G.groupStats || !G.groupStats.feminist) return;

  const container = feministMeter.querySelector('.threat-hearts');
  if (!container) return;

  // Calculate ACTUAL heart count based on psychological health (each heart = 10 points)
  const heartCount = Math.floor(G.groupStats.feminist.psychological / 10);

  // If animating and we have fewer hearts than before, animate the last one out
  if (animate && container.children.length > heartCount) {
    const lastHeart = container.children[container.children.length - 1];
    if (lastHeart) {
      lastHeart.classList.add('heart-pop');
      setTimeout(() => {
        if (lastHeart.parentNode) lastHeart.parentNode.removeChild(lastHeart);
      }, 500);
      return;
    }
  }

  // Rebuild hearts to match ACTUAL psychological percentage
  container.innerHTML = '';
  for (let i = 0; i < heartCount; i++) {
    const heart = document.createElement('img');
    heart.src = 'https://www.shortfactory.shop/trump/heart.png';
    heart.classList.add('threat-heart');
    heart.style.width = '24px';
    heart.style.height = '24px';
    heart.style.margin = '0 2px';
    container.appendChild(heart);
  }
}

// Show Israel shekels in muslim-meter (reuses same meter with ✡ label)
function showIsraelShekels(animate = false) {
  const muslimMeter = document.getElementById('muslim-meter');
  if (!muslimMeter) return;

  const label = muslimMeter.querySelector('.threat-label');
  const container = muslimMeter.querySelector('.threat-hearts');
  if (!label || !container) return;

  // Switch label to Star of David
  label.textContent = '✡';
  label.style.color = '#4d94ff';
  label.style.textShadow = '0 0 8px rgba(77, 148, 255, 1)';

  const shekelCount = Math.min(3, Math.ceil(G.israelGDP / 250));

  // Animate last shekel out if count dropped
  if (animate && container.children.length > shekelCount) {
    const last = container.children[container.children.length - 1];
    if (last) {
      last.classList.add('heart-pop');
      setTimeout(() => { if (last.parentNode) last.parentNode.removeChild(last); }, 500);
      return;
    }
  }

  // Rebuild shekels
  container.innerHTML = '';
  for (let i = 0; i < shekelCount; i++) {
    const shekel = document.createElement('span');
    shekel.textContent = '₪';
    shekel.className = 'threat-shekel';
    shekel.style.fontSize = '20px';
    shekel.style.animation = 'shekelPulse 2s ease-in-out infinite';
    shekel.style.animationDelay = (i * 0.3) + 's';

    if (G.israelGDP > 700) {
      shekel.style.color = '#ff0000';
      shekel.style.textShadow = '0 0 8px rgba(255, 0, 0, 1)';
    } else if (G.israelGDP > 500) {
      shekel.style.color = '#ff4444';
      shekel.style.textShadow = '0 0 6px rgba(255, 68, 68, 0.8)';
    } else {
      shekel.style.color = '#4d94ff';
      shekel.style.textShadow = '0 0 6px rgba(77, 148, 255, 0.8)';
    }
    container.appendChild(shekel);
  }
}

function endMeanTweets(success) {
  tweetGameActive = false;

  // Track mean tweet result in history
  if (G.gameHistory) {
    if (success) G.gameHistory.meanTweets.wins++;
    else G.gameHistory.meanTweets.losses++;
  }

  // Restore game buttons
  document.getElementById('phone').classList.remove('tweet-game-active');

  // Restore slot machine icon
  const slotIcon = document.getElementById('slot-machine-icon');
  if (slotIcon) slotIcon.style.display = '';

  setTimeout(() => {
    document.getElementById('mean-tweets-overlay').classList.remove('show');
  }, 100);

  if (success) {
    const overlay = document.getElementById('fullscreen-video');
    const vid = document.getElementById('fs-vid');
    vid.src = BASE + 'success.webm';
    vid.muted = false;
    overlay.classList.add('show');
    overlay.onclick = null;
    vid.play().catch(() => { vid.muted = true; vid.play().catch(() => {}); });

    vid.onended = () => {
      overlay.classList.remove('show');
      overlay.onclick = () => { vid.pause(); overlay.classList.remove('show'); };
      const s = getDifficultyScale();
      G.feminism = Math.max(0, G.feminism - 45/s);
      G.christianity = Math.min(100, G.christianity + 45/s);
      G.deepStateHP = Math.max(0, G.deepStateHP - 20/s);
      G.purity += 10/s;
      updateDisplay();
      showNews('TWEET SUCCESS!');

      // Show feminist hearts meter so user can see them disappear
      const feministMeter = document.getElementById('feminist-meter');
      if (feministMeter && G.groupStats && G.groupStats.feminist) {
        feministMeter.classList.remove('hidden');
        updateFeministHearts();
      }

      // Deduct 2 hearts from feminists with 1 second delays
      if (G.groupStats && G.groupStats.feminist) {
        // Wait 1 second after movie ends
        setTimeout(() => {
          // First heart deducted
          G.groupStats.feminist.psychological = Math.max(0, G.groupStats.feminist.psychological - 10);
          const loseHeart1 = new Audio('https://www.shortfactory.shop/trump/looseaheart.mp3');
          loseHeart1.volume = 0.8;
          loseHeart1.play().catch(e => console.log('Heart sound 1 failed:', e));
          updateDisplay();
          updateFeministHearts(true); // Update with pop animation

          // Wait another 1 second
          setTimeout(() => {
            // Second heart deducted
            G.groupStats.feminist.psychological = Math.max(0, G.groupStats.feminist.psychological - 10);
            const loseHeart2 = new Audio('https://www.shortfactory.shop/trump/looseaheart.mp3');
            loseHeart2.volume = 0.8;
            loseHeart2.play().catch(e => console.log('Heart sound 2 failed:', e));
            updateDisplay();
            updateFeministHearts(true); // Update with pop animation
            showNews('-2 ♀ HEARTS!');

            // Hide the meter after 2 seconds
            setTimeout(() => {
              if (feministMeter) feministMeter.classList.add('hidden');
            }, 2000);
          }, 1000);
        }, 1000);
      }

      // Trump laughs after hearts deducted
      setTimeout(() => {
        playTrumpLaugh(5);
      }, 2500);
    };
  } else {
    // Play fail video
    const overlay = document.getElementById('fullscreen-video');
    const vid = document.getElementById('fs-vid');
    vid.src = BASE + 'failed.webm';
    vid.muted = false;
    overlay.classList.add('show');
    vid.play().catch(() => {
      console.error('Failed video error:', BASE + 'failed.webm');
      vid.muted = true;
      vid.play().catch(() => {});
    });

    vid.onended = () => {
      overlay.classList.remove('show');
      showNews('TAP FASTER SNOWFLAKE!');
    };
  }
  disableMeanTweet();
}

// ==================== TRUMP CARDS ====================
// ⚠️⚠️⚠️ PROTECTED CODE - DO NOT MODIFY ⚠️⚠️⚠️
// Trump card animated overlay with fancy entrance/exit animations.
// Includes random annoying dismissal animations to punish impatient players.
// DO NOT replace with fullscreen or other simplified versions without permission!
// ⚠️⚠️⚠️ END WARNING ⚠️⚠️⚠️

// Annoying dismiss animations for impatient players
const ANNOYING_DISMISSALS = [
  'card-glitter',
  'card-spin-away',
  'card-shrink-spin',
  'card-fly-random',
  'card-melt',
  'card-explode',
  'card-flip-away',
  'card-bounce-out'
];

let currentCardData = null;
let cardEffectsApplied = false;

function showTrumpCard() {
  if (trumpCardActive) return;
  if (tweetGameActive) return; // Don't show cards during tweet game

  // Check if slot machine is active - delay card until it finishes
  const slotMachine = document.getElementById('slot-machine-icon');
  if (slotMachine && slotMachine.classList.contains('active')) {
    console.log('Trump card delayed - slot machine active');
    setTimeout(showTrumpCard, 3000); // Retry after 3 seconds
    return;
  }

  // Don't show cards when game is about to end
  if (G.purity >= 96) return; // Win condition
  if (G.trumpHP <= 0) return; // Loss condition
  if (G.deepStateHP >= 100) return; // Loss condition
  if (G.purity <= 0) return; // Loss condition

  trumpCardActive = true;

  vibrate(VIBES.cardFlip);

  const card = ASSETS.trumpCards[Math.floor(Math.random() * ASSETS.trumpCards.length)];
  currentCardData = card;

  // ⚠️ PROTECTED: Trump card animated overlay with fancy entrance/exit animations
  const overlay = document.getElementById('trump-card-overlay');
  const container = document.getElementById('trump-card-container');
  const vid = document.getElementById('trump-card-video');
  const effect = document.getElementById('trump-card-effect');

  vid.src = card.v;
  effect.textContent = card.desc;

  // Clear any previous dismiss animations
  ANNOYING_DISMISSALS.forEach(cls => container.classList.remove(cls));

  overlay.classList.add('show');
  container.classList.add('animate');

  // Dim buttons while Trump card is active
  document.getElementById('phone').classList.add('trump-card-active');

  const successSfx = document.getElementById('success-sound');
  if (successSfx) { successSfx.currentTime = 0; successSfx.play().catch(() => {}); }

  // Click to dismiss with annoying animation
  overlay.onclick = () => dismissCardAnnoying();

  // Reset shared effect guard
  cardEffectsApplied = false;
  let videoStarted = false;

  function applyCardEffect() {
    if (cardEffectsApplied) return false;
    cardEffectsApplied = true;
    card.fx();
    vibrate(VIBES.success);
    updateDisplay();
    return true;
  }

  setTimeout(() => {
    vid.play().catch(() => {});
  }, 2000);

  // Track when video starts playing
  vid.onplay = () => {
    videoStarted = true;
  };

  vid.onended = () => {
    if (!applyCardEffect()) return;
    clearTimeout(autoCloseTimer);

    // 30% chance to show emergency drop after good Trump cards
    if (Math.random() < 0.3 && typeof showEmergencyDrop === 'function') {
      setTimeout(() => showEmergencyDrop('trump-card'), 2500);
    }

    setTimeout(() => {
      overlay.classList.remove('show');
      container.classList.remove('animate');
      overlay.onclick = null;
      trumpCardActive = false;
      // Restore buttons
      document.getElementById('phone').classList.remove('trump-card-active');
    }, 1500);
  };

  // Auto-close after 8s ONLY if video hasn't started or effects haven't applied
  const autoCloseTimer = setTimeout(() => {
    if (trumpCardActive && !cardEffectsApplied) {
      applyCardEffect();

      overlay.classList.remove('show');
      container.classList.remove('animate');
      overlay.onclick = null;
      trumpCardActive = false;
      // Restore buttons
      document.getElementById('phone').classList.remove('trump-card-active');

      if (!videoStarted) {
        console.warn('Trump card video never started playing');
      }
    }
  }, 8000);
}

// ⚠️ PROTECTED: Dismissal function with random annoying animations
function dismissCardAnnoying() {
  if (!trumpCardActive) return;

  const overlay = document.getElementById('trump-card-overlay');
  const container = document.getElementById('trump-card-container');
  const vid = document.getElementById('trump-card-video');

  // Stop video
  vid.pause();

  // Apply effect (guard prevents double-fire from vid.onended)
  if (currentCardData && !cardEffectsApplied) {
    cardEffectsApplied = true;
    currentCardData.fx();
    updateDisplay();
  }

  // Random annoying animation
  const animation = ANNOYING_DISMISSALS[Math.floor(Math.random() * ANNOYING_DISMISSALS.length)];
  container.classList.remove('animate');
  container.classList.add(animation);

  vibrate([50, 30, 50, 30, 50, 30, 100]);

  // Clean up after animation
  setTimeout(() => {
    overlay.classList.remove('show');
    container.classList.remove(animation);
    overlay.onclick = null;
    trumpCardActive = false;
    currentCardData = null;
    // Restore buttons
    document.getElementById('phone').classList.remove('trump-card-active');
  }, 1000);
}

// ==================== POWERUPS ====================

function maybeActivatePowerup() {
  if (powerupInterval) clearInterval(powerupInterval);

  powerupInterval = setInterval(() => {
    if (Math.random() < 0.4) activateRandomPowerup();
  }, 3000);

  if (Math.random() < 0.5) setTimeout(activateRandomPowerup, 500);
}

function activateRandomPowerup() {
  const buttons = document.querySelectorAll('.game-btn:not(.locked)');
  if (buttons.length === 0) return;

  const btn = buttons[Math.floor(Math.random() * buttons.length)];
  const idx = parseInt(btn.dataset.idx);

  if (btn.classList.contains('glow-powerup') || btn.classList.contains('throb-powerup')) return;
  if (btn.classList.contains('mean-tweet-mode')) return;

  const type = Math.random() < 0.7 ? 'glow' : 'throb';
  btn.classList.add(type + '-powerup');
  btn.querySelector('.powerup-badge').textContent = type === 'glow' ? '5x' : '10x';
  powerups[idx] = type;

  // Play sound when powerup appears
  const clickSfx = document.getElementById('click-sound');
  if (clickSfx) { clickSfx.currentTime = 0; clickSfx.play().catch(() => {}); }

  // SPECIAL: Oil powerup voice announcement
  if (btn.dataset.action === 'oil') {
    setTimeout(() => {
      if (typeof speechSynthesis !== 'undefined') {
        speechSynthesis.cancel(); // Cancel any ongoing speech

        // First announcement
        const utterance1 = new SpeechSynthesisUtterance("SHE'S GONNA BLOW!!!");
        utterance1.rate = 1.2; // Faster, more excited
        utterance1.pitch = 1.1; // Slightly higher pitch
        utterance1.volume = 1.0; // Max volume

        // Second announcement after first completes
        utterance1.onend = () => {
          const utterance2 = new SpeechSynthesisUtterance("HOLD HER DOWN SHE'S A GUSHER!!!");
          utterance2.rate = 1.2;
          utterance2.pitch = 1.1;
          utterance2.volume = 1.0;
          speechSynthesis.speak(utterance2);
        };

        speechSynthesis.speak(utterance1);
      }
    }, 100); // Small delay for effect
  }

  setTimeout(() => {
    if (powerups[idx] === type) clearPowerup(idx);
  }, 3000); // 3 seconds - be fast!
}

function clearPowerup(idx) {
  const btn = document.querySelector(`[data-idx="${idx}"]`);
  if (btn) btn.classList.remove('glow-powerup', 'throb-powerup');
  delete powerups[idx];
}

function clearAllPowerups() {
  document.querySelectorAll('.game-btn').forEach(btn => btn.classList.remove('glow-powerup', 'throb-powerup'));
  powerups = {};
  if (powerupInterval) { clearInterval(powerupInterval); powerupInterval = null; }
}

// ==================== LITIGATION ====================

// Store paused state
let pausedTimers = {};

function pauseMainGame() {
  // Pause all videos
  const videos = document.querySelectorAll('video');
  videos.forEach(v => {
    if (!v.paused) {
      v.dataset.wasPlaying = 'true';
      v.pause();
    }
  });

  // Kill roulette sound (it's a JS Audio object, not in DOM)
  if (window.slotMachineAudio) {
    try { window.slotMachineAudio.pause(); window.slotMachineAudio.currentTime = 0; window.slotMachineAudio = null; } catch(e){}
  }

  // Store and clear all active timers
  pausedTimers = {
    emergTimer: emergTimer,
    nukeTimer: nukeTimer,
    wheelTimer: wheelTimer,
    opsTimer: opsTimer,
    advisorTimer: advisorTimer,
    tweetTimer: tweetTimer,
    tweetDecayTimer: tweetDecayTimer,
    powerupInterval: powerupInterval,
    infoButtonTimer: infoButtonTimer,
    meanTweetTimer: meanTweetTimer,
    alertAlternateTimer: alertAlternateTimer,
    powerupTapTimer: powerupTapTimer,
    powerupTapDecayTimer: powerupTapDecayTimer
  };

  // Clear all intervals/timers
  if (emergTimer) clearInterval(emergTimer);
  if (nukeTimer) clearInterval(nukeTimer);
  if (wheelTimer) clearInterval(wheelTimer);
  if (opsTimer) clearInterval(opsTimer);
  if (advisorTimer) clearInterval(advisorTimer);
  if (tweetTimer) clearInterval(tweetTimer);
  if (tweetDecayTimer) clearInterval(tweetDecayTimer);
  if (powerupInterval) clearInterval(powerupInterval);
  if (infoButtonTimer) clearTimeout(infoButtonTimer);
  if (meanTweetTimer) clearTimeout(meanTweetTimer);
  if (alertAlternateTimer) clearTimeout(alertAlternateTimer);
  if (powerupTapTimer) clearInterval(powerupTapTimer);
  if (powerupTapDecayTimer) clearInterval(powerupTapDecayTimer);

  // Null them out
  emergTimer = nukeTimer = wheelTimer = opsTimer = advisorTimer = null;
  tweetTimer = tweetDecayTimer = powerupInterval = null;
  infoButtonTimer = meanTweetTimer = alertAlternateTimer = null;
  powerupTapTimer = powerupTapDecayTimer = null;
}

function resumeMainGame() {
  // Resume videos that were playing
  const videos = document.querySelectorAll('video');
  videos.forEach(v => {
    if (v.dataset.wasPlaying === 'true') {
      v.play().catch(() => {});
      delete v.dataset.wasPlaying;
    }
  });

  // Restart key timers that don't auto-restart
  if (pausedTimers.powerupInterval && typeof maybeActivatePowerup === 'function') {
    maybeActivatePowerup();
  }
  if (pausedTimers.infoButtonTimer && typeof startRandomInfoButton === 'function') {
    startRandomInfoButton();
  }
  if (pausedTimers.meanTweetTimer && G.round >= 2 && typeof startRandomMeanTweet === 'function') {
    startRandomMeanTweet();
  }
}

function toggleLitigation() {
  if (litOpen) {
    closeLitigation();
    return;
  }
  litOpen = true;

  // Stop slot machine when opening litigation
  if (typeof stopSlotMachine === 'function') {
    stopSlotMachine();
  }

  // Pause main game to save resources
  pauseMainGame();

  // Hide emergency drop while in litigation
  const emergencyDrop = document.getElementById('emergency-drop');
  if (emergencyDrop) emergencyDrop.classList.remove('show');

  // Kill black ops if it's running
  if (opsTimer) { clearInterval(opsTimer); opsTimer = null; }
  const bopsOverlay = document.getElementById('blackops-overlay');
  if (bopsOverlay) bopsOverlay.classList.remove('show');
  const bopsAlert = document.getElementById('blackops-alert-icon');
  if (bopsAlert) bopsAlert.classList.remove('show');
  const bopsText = document.getElementById('blackops-alert-text');
  if (bopsText) bopsText.classList.remove('show');

  // Load litigation mini-game with current HP
  const iframe = document.getElementById('litigation-iframe');
  const overlay = document.getElementById('litigation-overlay');

  // Use URLSearchParams for safe URL construction
  const params = new URLSearchParams({ hp: Math.round(G.trumpHP), loop: G.ngPlusLoop || 0 });
  iframe.src = `pages/litigation.html?${params.toString()}`;
  overlay.classList.add('show');
}

function closeLitigation() {
  litOpen = false;
  const overlay = document.getElementById('litigation-overlay');
  const iframe = document.getElementById('litigation-iframe');

  overlay.classList.add('fade-out');
  setTimeout(() => {
    overlay.classList.remove('show', 'fade-out');
    iframe.src = '';

    // Resume main game
    resumeMainGame();
  }, 500);
}

// Flag to prevent game over check immediately after litigation (global for main.js access)
window.litigationCooldown = false;

// Listen for messages from litigation iframe
window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'litigation-complete') {
    const result = event.data;

    // Set cooldown to prevent immediate game over check
    window.litigationCooldown = true;
    setTimeout(() => { window.litigationCooldown = false; }, 3000); // 3 second grace period

    // Get the HP from litigation - now supports up to 200%!
    const newHP = result.returnHP || G.trumpHP;

    // Apply results from litigation
    // Litigation ONLY affects Trump HP (up to 200%) - NOT purity
    if (result.won) {
      // Victory - you earned that HP! Plus bonuses! (up to 200%)
      G.trumpHP = Math.min(200, newHP + 10);
      G.trumpMaxHP = Math.max(G.trumpMaxHP || 100, G.trumpHP);
      G.deepStateHP = Math.max(0, G.deepStateHP - 20);
      showNews('LITIGATION VICTORY! HP:' + G.trumpHP + '% -DEEPSTATE');
    } else if (result.settled) {
      // Settled - keep your HP gains (up to 200%)
      G.trumpHP = Math.min(200, newHP);
      G.trumpMaxHP = Math.max(G.trumpMaxHP || 100, G.trumpHP);
      showNews('CASE SETTLED - HP:' + G.trumpHP + '%');
    } else {
      // Loss - still keep some HP, but penalty
      G.trumpHP = Math.max(1, Math.min(200, newHP - 10));
      G.deepStateHP = Math.min(100, G.deepStateHP + 10);
      showNews('LITIGATION DEFEAT! HP:' + G.trumpHP + '%');
    }

    // Note: Purity is NOT modified by litigation - only HP changes

    // Apply 19th amendment effects
    if (result.nineteenthRepealed) {
      G.feminism = Math.max(0, G.feminism - 30);
      G.christianity = Math.min(100, G.christianity + 30);
      G.birthrate += 0.5;
      showNews('🔴 19TH AMENDMENT REPEALED! 🔴');

      // Play why-repeal first, then Lamantationz - both in fullscreen overlay
      playFullscreenVideo(BASE + 'litigation/why-repeal.webm', () => {
        // After why-repeal, play Lamantationz celebration
        playFullscreenVideo(BASE + 'litigation/Lamantationz.webm');
      });
    }

    closeLitigation();
    updateDisplay();
  }
});

function showResult(title, success, stats) {
  document.getElementById('result-title').textContent = title;
  document.getElementById('result-outcome').textContent = success ? '✅' : '❌';
  document.getElementById('result-stats').textContent = stats;
  document.getElementById('result-popup').classList.add('show');
}

function closeResult() {
  document.getElementById('result-popup').classList.remove('show');
  updateDisplay();
}

function doVoting() { const s=DIFFICULTY_SCALE||1; G.purity += 5/s; showResult('VOTING', true, '+Purity'); }
function doCongress() { const s=DIFFICULTY_SCALE||1; G.deepStateHP -= 5/s; showResult('CONGRESS', true, '-DeepState'); }
function doSupremeCourt() { const s=DIFFICULTY_SCALE||1; G.trumpHP += 10/s; showResult('SCOTUS', true, '+HP'); }
function doExecutiveOrder() { const s=DIFFICULTY_SCALE||1; G.purity += 8/s; G.deepStateHP -= 8/s; showResult('EXEC ORDER', true, '+Purity, -DS'); }

function doAmendment(num) {
  closeLitigation();
  const s = getDifficultyScale();
  if (num === '19th') {
    G.feminism = Math.max(0, G.feminism - 30/s);
    G.christianity = Math.min(100, G.christianity + 30/s);
    G.birthrate += 0.5/s;
    showResult('REPEAL 19TH', true, '-Feminism, +Birthrate');
  } else if (num === '2nd') {
    G.purity += 10/s;
    showResult('2ND AMENDMENT', true, '+Purity');
  } else if (num === '1st') {
    G.deepStateHP -= 10/s;
    showResult('1ST AMENDMENT', true, '-DeepState');
  } else if (num === '25th') {
    G.trumpHP = Math.min(200, G.trumpHP + 50/s); // Partial heal instead of full
    showResult('25TH AMENDMENT', true, '+HP');
  }
}

// ==================== EMERGENCY POWERS ====================

// Unified emergency handler - routes to correct action based on tier
function activateEmergencyTier() {
  vibrate(VIBES.emergency);

  // Hide the alert
  document.getElementById('blackops-alert-icon').classList.remove('show');
  document.getElementById('blackops-alert-text').classList.remove('show');

  // Route to correct action based on current tier
  if (G.emergencyTier === 1) {
    activateBlackOps();
  } else if (G.emergencyTier === 2) {
    activateWheel();
  } else if (G.emergencyTier === 3) {
    activateNuke();
  }
}

function triggerEmergency() {
  if (G.trumpHP > 20) {
    showNews('HP TOO HIGH FOR EMERGENCY!');
    return;
  }

  vibrate(VIBES.emergency);

  const drop = document.getElementById('emergency-drop');
  emergActive = !emergActive;
  drop.classList.toggle('show', emergActive);

  if (emergActive) {
    emergTimer = setTimeout(() => {
      drop.classList.remove('show');
      emergActive = false;
    }, 10000);
  } else {
    clearTimeout(emergTimer);
  }
}

function activateNuke() {
  // Clear any existing timer first
  clearInterval(nukeTimer);

  document.getElementById('emergency-drop').classList.remove('show');
  emergActive = false;

  // Stop slot machine
  if (typeof stopSlotMachine === 'function') stopSlotMachine();

  // Hide the flashing alert
  document.getElementById('blackops-alert-icon').classList.remove('show');
  document.getElementById('blackops-alert-text').classList.remove('show');

  vibrate(VIBES.emergency);

  playFullscreenVideo(BASE + 'map/nukeadvisor.webm', () => {
    document.getElementById('nuke-confirm').classList.add('show');

    let countdown = 10;
    document.getElementById('nuke-countdown').textContent = countdown;

    nukeTimer = setInterval(() => {
      countdown--;
      document.getElementById('nuke-countdown').textContent = countdown;
      vibrate(50);
      if (countdown <= 0) {
        clearInterval(nukeTimer);
        nukeDecision(false);
      }
    }, 1000);
  });
}

function nukeDecision(yes) {
  clearInterval(nukeTimer);
  document.getElementById('nuke-confirm').classList.remove('show');

  if (yes) {
    vibrate(VIBES.nuke);
    const phone = document.getElementById('phone');
    const nukeOverlay = document.getElementById('nuke-text-overlay');

    // Pick random target
    const nukeData = NUKE_TARGETS[Math.floor(Math.random() * NUKE_TARGETS.length)];
    document.getElementById('nuke-target').textContent = nukeData.target;
    document.getElementById('nuke-tagline').textContent = nukeData.tagline;

    // Track nuke in history
    if (G.gameHistory) G.gameHistory.nukes.push({ target: nukeData.target, tagline: nukeData.tagline });

    // Show nuke text immediately
    nukeOverlay.classList.add('show');

    // Start burn effect and glitch halfway through video (after ~2 seconds)
    setTimeout(() => {
      phone.classList.add('burn-red', 'glitch-screen');
      vibrate(VIBES.explosion);
      shakeScreen();
      // Nuclear explosion - continuous emergency rumble!
      startEmergencyRumble(10000);
    }, 2000);

    playFullscreenVideo(BASE + 'map/yes.webm', () => {
      // Hide nuke text
      nukeOverlay.classList.remove('show');
      // Fade out effects
      phone.classList.add('fade-out');
      setTimeout(() => {
        phone.classList.remove('burn-red', 'glitch-screen', 'fade-out');
      }, 1000);

      const s = getDifficultyScale();
      G.purity += 20/s;
      G.deepStateHP -= 40/s;
      G.trumpHP = Math.min(200, G.trumpHP + 25); // Health boost for nuking shithole!
      G.optics = 'BAD';
      G.usedAggressive = true;
      G.nukeUsed = true;

      vibrate(VIBES.explosion);

      updateDisplay();
      showNews('SHITHOLE NUKED! +25 HP!');

      // Trump laughs after nuking a shithole!
      setTimeout(() => playTrumpLaugh(5), 500);

      // Play world on fire then return to normal map
      playEmergencyWorldOnFire(10000);
    }, {unskippable: true});
  } else {
    playFullscreenVideo(BASE + 'map/no.webm', () => {
      showNews('NUKE CANCELLED');
    });
  }
}

function activateWheel() {
  // Clear any existing timer first
  clearInterval(wheelTimer);

  document.getElementById('emergency-drop').classList.remove('show');

  // Stop slot machine cycle
  if (typeof stopSlotMachine === 'function') stopSlotMachine();

  // Hide the flashing alert
  document.getElementById('blackops-alert-icon').classList.remove('show');
  document.getElementById('blackops-alert-text').classList.remove('show');

  document.getElementById('wheel-overlay').classList.add('show');

  let countdown = 15;
  document.getElementById('wheel-countdown').textContent = countdown;

  wheelTimer = setInterval(() => {
    countdown--;
    document.getElementById('wheel-countdown').textContent = countdown;
    if (countdown <= 0) {
      clearInterval(wheelTimer);
      document.getElementById('wheel-overlay').classList.remove('show');
      // Timeout without spin - show alert again
      document.getElementById('blackops-alert-icon').classList.add('show');
      document.getElementById('blackops-alert-text').classList.add('show');
    }
  }, 1000);
}

function spinWheel() {
  if (wheelSpinning) return;
  wheelSpinning = true;
  clearInterval(wheelTimer);

  // Cancel any existing animation frame
  if (wheelSpinRAF) {
    cancelAnimationFrame(wheelSpinRAF);
    wheelSpinRAF = null;
  }

  vibrate(VIBES.wheel);

  const wheel = document.getElementById('wheel-img');
  const spins = 3 + Math.random() * 3;
  const finalDeg = spins * 360 + Math.random() * 360;
  const duration = 3000 + Math.random() * 2000;
  const startTime = Date.now();

  function animate() {
    const elapsed = Date.now() - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    wheel.style.transform = `rotate(${finalDeg * eased}deg)`;

    if (progress < 1) {
      wheelSpinRAF = requestAnimationFrame(animate);
    } else {
      const segIdx = Math.floor((finalDeg % 360) / (360 / ASSETS.wheel.length)) % ASSETS.wheel.length;
      const outcomeName = ASSETS.wheel[segIdx].split('/').pop().replace('.webm', '');

      // Get effects from config
      const effects = WHEEL_EFFECTS[outcomeName] || { name: outcomeName.toUpperCase(), good: false, hp: -10, ds: 10, purity: -10 };
      const isGoodOutcome = effects.good;

      // Track wheel spin in history
      if (G.gameHistory) G.gameHistory.wheelSpins.push({ name: effects.name, good: isGoodOutcome });

      // Show what the wheel landed on
      document.getElementById('wheel-result').textContent = effects.name;
      console.log('Wheel landed on:', outcomeName, '| Effects:', effects);

      vibrate(isGoodOutcome ? VIBES.success : VIBES.nuke);

      setTimeout(() => {
        document.getElementById('wheel-overlay').classList.remove('show');
        const phone = document.getElementById('phone');

        // Add effect class based on outcome
        if (isGoodOutcome) {
          phone.classList.add('glow-white');
        } else {
          phone.classList.add('burn-red', 'glitch-screen');
          vibrate([100, 50, 100, 50, 100, 50, 100, 50, 200, 100, 200, 100, 300]);
        }

        // Show disaster announcement
        showDisasterAnnouncement(effects);

        // Safety cleanup: force remove disaster overlay after max duration
        const safetyCleanup = setTimeout(() => {
          document.getElementById('disaster-overlay').classList.remove('show');
          console.warn('Disaster overlay cleanup timeout - forced removal');
        }, 15000);

        try {
          playFullscreenVideo(getVideo(ASSETS.wheel[segIdx]), () => {
            // Clear safety timeout since callback executed
            clearTimeout(safetyCleanup);

            // Hide disaster announcement
            document.getElementById('disaster-overlay').classList.remove('show');

            // Apply effects to game state
            applyWheelEffects(effects);

            // Mark wheel as used
            G.wheelUsed = true;

            // Fade out visual effects
            phone.classList.add('fade-out');
            setTimeout(() => {
              phone.classList.remove('burn-red', 'glow-white', 'glitch-screen', 'fade-out');
            }, 1000);

            wheelSpinning = false;
            wheelSpinRAF = null;
            wheel.style.transform = 'rotate(0deg)';

            updateDisplay();
            showNews(effects.msg || effects.name);

            // Trump laughs on good wheel outcomes!
            if (isGoodOutcome) {
              setTimeout(() => playTrumpLaugh(5), 500);
            }

            // Major disasters trigger continuous emergency shake
            const majorDisasters = ['volcanoe', 'asteroid', 'alien', 'skynet', 'plague', 'nazi', 'chinawins', 'russiawins'];
            if (majorDisasters.includes(outcomeName)) {
              startEmergencyRumble(10000); // Rumble for 10 seconds
            }

            // BIOATTACK - Special green gas effect!
            if (outcomeName === 'plague') {
              triggerBioattackEffect(12000); // Gas for 12 seconds
            }

            // Play world on fire then return to normal map
            playEmergencyWorldOnFire(10000);
          });
        } catch (error) {
          // Cleanup on exception
          clearTimeout(safetyCleanup);
          document.getElementById('disaster-overlay').classList.remove('show');
          console.error('Wheel video playback error:', error);
          wheelSpinning = false;
          wheel.style.transform = 'rotate(0deg)';
        }
      }, 500);
    }
  }
  animate();
}

// Make spinWheel globally accessible for onclick handler
window.spinWheel = spinWheel;

// Show SNES-style disaster announcement
function showDisasterAnnouncement(effects) {
  const overlay = document.getElementById('disaster-overlay');
  const nameEl = document.getElementById('disaster-name');
  const effectsEl = document.getElementById('disaster-effects');

  // Set disaster name with color
  nameEl.textContent = effects.name;
  nameEl.className = 'disaster-name ' + (effects.good ? 'good' : 'bad');

  // Build effects list
  let html = '';
  if (effects.hp) {
    const cls = effects.hp > 0 ? 'positive' : 'negative';
    html += `<div class="disaster-stat ${cls}">HP ${effects.hp > 0 ? '+' : ''}${effects.hp}</div>`;
  }
  if (effects.ds) {
    const cls = effects.ds < 0 ? 'positive' : 'negative';
    html += `<div class="disaster-stat ${cls}">DEEPSTATE ${effects.ds > 0 ? '+' : ''}${effects.ds}</div>`;
  }
  if (effects.purity) {
    const cls = effects.purity > 0 ? 'positive' : 'negative';
    html += `<div class="disaster-stat ${cls}">PURITY ${effects.purity > 0 ? '+' : ''}${effects.purity}</div>`;
  }
  if (effects.moves) {
    html += `<div class="disaster-stat positive">MOVES +${effects.moves}</div>`;
  }
  effectsEl.innerHTML = html;

  overlay.classList.add('show');
}

// Apply wheel outcome effects to game state
// ==================== BIOATTACK GREEN GAS EFFECT ====================

function triggerBioattackEffect(duration) {
  console.log('BIOATTACK! GREEN GAS DISPERSING!');

  // Create green gas overlay
  const gasOverlay = document.createElement('div');
  gasOverlay.id = 'bioattack-gas-overlay';
  gasOverlay.style.position = 'fixed';
  gasOverlay.style.top = '0';
  gasOverlay.style.left = '0';
  gasOverlay.style.width = '100vw';
  gasOverlay.style.height = '100vh';
  gasOverlay.style.zIndex = '9999';
  gasOverlay.style.pointerEvents = 'none';
  gasOverlay.style.background = 'radial-gradient(circle, rgba(0,255,0,0.3) 0%, rgba(50,200,50,0.5) 50%, rgba(0,150,0,0.4) 100%)';
  gasOverlay.style.animation = 'gasDisperse 3s ease-in-out infinite';
  gasOverlay.style.mixBlendMode = 'screen';

  // Add animated gas clouds
  for (let i = 0; i < 8; i++) {
    const cloud = document.createElement('div');
    cloud.style.position = 'absolute';
    cloud.style.width = '300px';
    cloud.style.height = '300px';
    cloud.style.borderRadius = '50%';
    cloud.style.background = 'radial-gradient(circle, rgba(0,255,0,0.6) 0%, rgba(50,200,50,0.3) 50%, transparent 100%)';
    cloud.style.animation = `gasFloat${i % 3} ${3 + i}s ease-in-out infinite`;
    cloud.style.left = `${Math.random() * 100}%`;
    cloud.style.top = `${Math.random() * 100}%`;
    cloud.style.filter = 'blur(40px)';
    gasOverlay.appendChild(cloud);
  }

  document.body.appendChild(gasOverlay);

  // GAS GAS GAS WARNING!
  const warningBox = document.createElement('div');
  warningBox.id = 'gas-warning';
  warningBox.style.position = 'fixed';
  warningBox.style.top = '50%';
  warningBox.style.left = '50%';
  warningBox.style.transform = 'translate(-50%, -50%)';
  warningBox.style.zIndex = '10000';
  warningBox.style.fontFamily = "'Press Start 2P', monospace";
  warningBox.style.fontSize = '32px';
  warningBox.style.color = '#0f0';
  warningBox.style.textShadow = '0 0 10px #0f0, 0 0 20px #0f0, 4px 4px 0 #000';
  warningBox.style.textAlign = 'center';
  warningBox.style.animation = 'gasWarningFlash 0.5s infinite';
  warningBox.style.pointerEvents = 'none';
  warningBox.innerHTML = '☣️<br/>GAS GAS GAS<br/>☣️';
  document.body.appendChild(warningBox);

  // Page rumble
  document.body.style.animation = 'bioRumble 0.1s infinite';

  // Biohazard mask icon flashing in corner
  const maskIcon = document.createElement('div');
  maskIcon.id = 'biohazard-mask';
  maskIcon.style.position = 'fixed';
  maskIcon.style.top = '20px';
  maskIcon.style.right = '20px';
  maskIcon.style.fontSize = '60px';
  maskIcon.style.zIndex = '10001';
  maskIcon.style.animation = 'bioMaskFlash 0.3s infinite';
  maskIcon.style.filter = 'drop-shadow(0 0 20px #0f0)';
  maskIcon.textContent = '☣️';
  document.body.appendChild(maskIcon);

  // Vibrate pattern - chaotic gas dispersal
  const vibratePattern = Array(20).fill([100, 50]).flat();
  vibrate(vibratePattern);

  // Clear after duration
  setTimeout(() => {
    // Fade out gas
    gasOverlay.style.transition = 'opacity 2s';
    gasOverlay.style.opacity = '0';
    warningBox.style.transition = 'opacity 1s';
    warningBox.style.opacity = '0';
    maskIcon.style.transition = 'opacity 1s';
    maskIcon.style.opacity = '0';

    // Stop rumble
    document.body.style.animation = '';

    setTimeout(() => {
      gasOverlay.remove();
      warningBox.remove();
      maskIcon.remove();
    }, 2000);
  }, duration);
}

function applyWheelEffects(effects) {
  const scale = getDifficultyScale();
  if (effects.hp) G.trumpHP = Math.max(0, Math.min(200, G.trumpHP + effects.hp / scale));
  if (effects.ds) G.deepStateHP = Math.max(0, Math.min(100, G.deepStateHP + effects.ds / scale));
  if (effects.purity) G.purity += effects.purity / scale;
  if (effects.moves) G.moves += effects.moves; // Moves not scaled

  // WHEEL EVENTS POPULATION IMPACT
  // Bad events cause massive death tolls
  if (!effects.good) {
    // Calculate deaths based on severity (hp damage * 100k)
    const severity = Math.abs(effects.hp || 10);
    const deaths = Math.floor(severity * 100000 + Math.random() * 500000); // 100k-600k+ deaths
    G.usPopulation = Math.max(0, G.usPopulation - deaths);

    // Major disasters increase poop threat significantly
    G.poopThreat = Math.min(10, G.poopThreat + Math.floor(severity / 5));
  } else {
    // Good events might reduce poop threat
    G.poopThreat = Math.max(0, G.poopThreat - 1);
  }
}

// Play world on fire in map with red glow
function playWorldOnFire(duration) {
  const mapSection = document.getElementById('map-section');
  const mapVid = document.getElementById('map-video');

  mapVid.src = BASE + 'map/worldonfire.webm';
  mapVid.loop = true;
  mapVid.onerror = () => {
    console.error('Failed to load world on fire video');
    updateMapVideo(); // Fallback to normal map
  };
  mapVid.load();
  mapVid.play().catch(err => {
    console.warn('World on fire autoplay blocked:', err);
  });

  // Add red glow to map
  mapSection.classList.add('on-fire');

  setTimeout(() => {
    // Fade out the glow
    mapSection.classList.add('fade-out');

    setTimeout(() => {
      mapSection.classList.remove('on-fire', 'fade-out');
      updateMapVideo();
    }, 1000);
  }, duration - 1000); // Start fade 1 second before end
}

// Play a celebration video in the map area
function playCelebrationVideo(filename, duration) {
  const mapVid = document.getElementById('map-video');
  const mapSection = document.getElementById('map-section');
  const trumpStage = document.querySelector('.trump-stage');

  // Video is in the litigation folder
  mapVid.src = BASE + 'litigation/' + filename;
  mapVid.loop = false;
  mapVid.muted = false;
  mapVid.load();
  mapVid.play().catch(() => {});

  // Expand map and squash trump stage for better video viewing
  mapSection.classList.add('celebrating', 'video-playing');
  if (trumpStage) trumpStage.classList.add('squashed');

  // When video ends or timeout, restore map
  const restore = () => {
    mapSection.classList.remove('celebrating', 'video-playing');
    if (trumpStage) trumpStage.classList.remove('squashed');
    updateMapVideo();
  };

  mapVid.onended = restore;
  setTimeout(restore, duration);
}

function activateBlackOps() {
  // Clear any existing timer first
  clearInterval(opsTimer);

  document.getElementById('emergency-drop').classList.remove('show');

  // Stop slot machine cycle
  if (typeof stopSlotMachine === 'function') stopSlotMachine();

  // Hide the flashing alert (already hidden by activateEmergencyTier)
  document.getElementById('blackops-alert-icon').classList.remove('show');
  document.getElementById('blackops-alert-text').classList.remove('show');

  document.getElementById('blackops-overlay').classList.add('show');

  // black.webm should already be playing
  const mapVid = document.getElementById('map-video');
  if (!mapVid.src.includes('black.webm')) {
    mapVid.src = BASE + 'map/black.webm';
    mapVid.loop = true;
    mapVid.load();
    mapVid.play().catch(() => {});
  }

  let countdown = 15;
  document.getElementById('blackops-countdown').textContent = countdown;

  opsTimer = setInterval(() => {
    countdown--;
    document.getElementById('blackops-countdown').textContent = countdown;
    if (countdown <= 0) {
      clearInterval(opsTimer);
      document.getElementById('blackops-overlay').classList.remove('show');
      // Timeout without selection - show alert again
      document.getElementById('blackops-alert-icon').classList.add('show');
      document.getElementById('blackops-alert-text').classList.add('show');
    }
  }, 1000);
}

function playBlackOps(idx) {
  clearInterval(opsTimer);
  document.getElementById('blackops-overlay').classList.remove('show');

  vibrate(VIBES.explosion);

  const effects = BLACK_OPS_EFFECTS[idx] || BLACK_OPS_EFFECTS[0];
  const phone = document.getElementById('phone');

  // Track black ops in history
  if (G.gameHistory) G.gameHistory.blackOps.push({ name: effects.name });

  // Add tactical glitch effect
  phone.classList.add('glitch-screen');

  // Show black ops announcement
  showBlackOpsAnnouncement(effects);

  // Pick random variation using universal helper
  const webmSrc = getVideo(ASSETS.blackops[idx].webm);

  // Safety cleanup: force remove disaster overlay after max duration
  const safetyCleanup = setTimeout(() => {
    document.getElementById('disaster-overlay').classList.remove('show');
    console.warn('Disaster overlay cleanup timeout - forced removal');
  }, 15000);

  try {
    playFullscreenVideo(webmSrc, () => {
      // Clear safety timeout since callback executed
      clearTimeout(safetyCleanup);

      // Hide announcement
      document.getElementById('disaster-overlay').classList.remove('show');

      // Fade out glitch
      phone.classList.add('fade-out');
      setTimeout(() => {
        phone.classList.remove('glitch-screen', 'fade-out');
      }, 1000);

      // Apply effects with difficulty scaling
      const scale = getDifficultyScale();
      if (effects.hp) G.trumpHP = Math.max(0, Math.min(200, G.trumpHP + effects.hp / scale));
      if (effects.ds) G.deepStateHP = Math.max(0, Math.min(100, G.deepStateHP + effects.ds / scale));
      if (effects.purity) G.purity += effects.purity / scale;
      if (effects.cash) G.oilCash += effects.cash; // Cash not scaled

      // BLACK OPS POPULATION IMPACT - Lethal operations cause deaths
      if (effects.ds < 0) {
        // Lethal black ops that damage deep state also cause civilian casualties
        const deaths = Math.floor(Math.random() * 50000 + 10000); // 10k-60k deaths
        G.usPopulation = Math.max(0, G.usPopulation - deaths);

        // Increase poop threat (retaliation risk)
        G.poopThreat = Math.min(10, G.poopThreat + 1);
      }

      // Mark blackops as used for this playthrough
      G.blackopsUsed = true;

      updateDisplay();
      showNews(effects.msg);

      // Trump laughs after successful black op!
      setTimeout(() => playTrumpLaugh(3), 500);

      // Play world on fire, then return to normal
      playEmergencyWorldOnFire(8000);
    });
  } catch (error) {
    // Cleanup on exception
    clearTimeout(safetyCleanup);
    document.getElementById('disaster-overlay').classList.remove('show');
    phone.classList.remove('glitch-screen');
    console.error('BlackOps video playback error:', error);
  }
}

// Worldonfire after emergency action - returns to normal map, clears tier
function playEmergencyWorldOnFire(duration) {
  const mapSection = document.getElementById('map-section');
  const mapVid = document.getElementById('map-video');

  mapVid.src = BASE + 'map/worldonfire.webm';
  mapVid.loop = true;
  mapVid.onerror = () => {
    console.error('Failed to load emergency world on fire video');
    updateMapVideo(); // Fallback to normal map
  };
  mapVid.load();
  mapVid.play().catch(err => {
    console.warn('Emergency world on fire autoplay blocked:', err);
  });

  // Add red glow to map
  mapSection.classList.add('on-fire');

  setTimeout(() => {
    // Fade out the glow
    mapSection.classList.add('fade-out');

    setTimeout(() => {
      mapSection.classList.remove('on-fire', 'fade-out');

      // Clear emergency tier and return to normal map
      G.emergencyTier = 0;
      updateMapVideo();
      updateDisplay(); // Check if next tier should activate
    }, 1000);
  }, duration - 1000);
}

// Show SNES-style black ops announcement
function showBlackOpsAnnouncement(effects) {
  const overlay = document.getElementById('disaster-overlay');
  const nameEl = document.getElementById('disaster-name');
  const effectsEl = document.getElementById('disaster-effects');

  // Black ops are always "good" for you (tactical green)
  nameEl.textContent = effects.name;
  nameEl.className = 'disaster-name blackops';

  // Build effects list
  let html = '';
  if (effects.ds) {
    html += `<div class="disaster-stat positive">DEEPSTATE ${effects.ds}</div>`;
  }
  if (effects.purity) {
    html += `<div class="disaster-stat positive">PURITY +${effects.purity}</div>`;
  }
  if (effects.hp && effects.hp < 0) {
    html += `<div class="disaster-stat negative">HP ${effects.hp}</div>`;
  }
  if (effects.cash) {
    const cls = effects.cash > 0 ? 'positive' : 'neutral';
    html += `<div class="disaster-stat ${cls}">OIL $${effects.cash}</div>`;
  }
  effectsEl.innerHTML = html;

  overlay.classList.add('show');
}

// ==================== TRUMP LAUGH ====================
// Plays laughing video in Trump box with HP boost, then reverts to normal

function playTrumpLaugh(hpBoost = 5, callback) {
  const trumpVid = document.getElementById('trump-video');
  if (!trumpVid) {
    if (callback) callback();
    return;
  }

  // Store current state
  const wasMuted = trumpVid.muted;

  // Play the laugh video
  trumpVid.src = SPECIAL_VIDEOS.trumpLaugh;
  trumpVid.muted = false;
  trumpVid.loop = false;
  trumpVid.play().catch(() => {
    trumpVid.muted = true;
    trumpVid.play().catch(() => {});
  });

  // Add HP boost
  G.trumpHP = Math.min(200, G.trumpHP + hpBoost);
  updateDisplay();
  showNews('HAHA! +' + hpBoost + ' HP!');

  vibrate(VIBES.success);

  // When laugh ends, revert to normal Trump state
  trumpVid.onended = () => {
    trumpVid.muted = wasMuted;
    trumpVid.loop = true;
    updateTrumpVideo();
    if (callback) callback();
  };

  // Fallback in case video fails
  setTimeout(() => {
    if (trumpVid.src.includes('laughing')) {
      trumpVid.muted = wasMuted;
      trumpVid.loop = true;
      updateTrumpVideo();
      if (callback) callback();
    }
  }, 5000);
}

// ==================== PIPE BOMB NECKLACE DETONATOR ====================
// ⚠️⚠️⚠️ PROTECTED CODE - DO NOT DELETE OR MODIFY ⚠️⚠️⚠️
// This is an absolute gem - the crown jewel of the game.
// Interactive pipe bomb sequence with detonator button, countdown,
// fullscreen videos, phone shake, and world on fire finale.
// Preserve this treasure at all costs!
// ⚠️⚠️⚠️ END WARNING - TOUCH NOTHING BELOW ⚠️⚠️⚠️

let pipeBombTimer = null;
let pipeBombTimeout = null;

// ⚠️ PROTECTED: Test function for pipe bomb sequence
function testPipeBombSequence() {
  console.log('🧪 Testing pipe bomb sequence...');
  startPipeBombSequence(2); // Test with blackopps3 (index 2)
}

// ⚠️ PROTECTED: Main pipe bomb sequence - plays fullscreen videos and interactive detonator
function startPipeBombSequence(blackopsIndex = 2) {
  const BASE = 'https://www.shortfactory.shop/trump/';
  const overlay = document.getElementById('pipebomb-overlay');
  const video = document.getElementById('pipebomb-video');
  const hotspot = document.getElementById('detonator-hotspot');
  const timer = document.getElementById('detonator-timer');

  // Show overlay
  overlay.classList.add('show');

  // Store which blackops index for effects later
  overlay.dataset.blackopsIndex = blackopsIndex;

  // STEP 1: Play the blackops video FIRST (e.g., guy putting necklace on victim)
  const blackopsVideo = getVideo(ASSETS.blackops[blackopsIndex].webm);

  video.src = blackopsVideo;
  video.load();
  video.play().catch(e => console.log('Video play failed:', e));

  video.onended = () => {
    // STEP 2: Play pipebomb.webm (Trump with detonator)
    video.src = BASE + 'map/pipebomb.webm';
    video.load();
    video.play().catch(e => console.log('Video play failed:', e));

    video.onended = () => {
      // STEP 3: Play pushthebutton.webm and pause at 3 seconds
      video.src = BASE + 'map/pushthebutton.webm';
      video.load();
      video.play().catch(e => console.log('Video play failed:', e));

      // Wait for video to reach 3 seconds, then pause
      const checkTime = setInterval(() => {
        if (video.currentTime >= 3.0) {
          clearInterval(checkTime);
          video.pause();

          // Show flashing hotspot and timer
          hotspot.classList.add('show');
          timer.classList.add('show');

          // 10 second countdown
          let countdown = 10;
          timer.textContent = countdown;

          pipeBombTimer = setInterval(() => {
            countdown--;
            timer.textContent = countdown;

            if (countdown <= 0) {
              clearInterval(pipeBombTimer);
              // Timeout - stand down (no detonation)
              standDownPipeBomb();
            }
          }, 1000);
        }
      }, 100);
    };
  };
}

// ⚠️ PROTECTED: Detonation sequence - explosion video, screen shake, world on fire
function detonateNecklace() {
  const BASE = 'https://www.shortfactory.shop/trump/';
  const overlay = document.getElementById('pipebomb-overlay');
  const video = document.getElementById('pipebomb-video');
  const hotspot = document.getElementById('detonator-hotspot');
  const timer = document.getElementById('detonator-timer');
  const mapVideo = document.getElementById('map-video');

  // Clear timer
  if (pipeBombTimer) clearInterval(pipeBombTimer);

  // Hide hotspot and timer
  hotspot.classList.remove('show');
  timer.classList.remove('show');

  // RUMBLE ON BUTTON PRESS!
  vibrate([400, 200, 400, 200, 1000, 400, 2000]);

  // STEP 3: Play byebye.webm (explosion)
  video.src = BASE + 'map/byebye.webm';
  video.load();
  video.play().catch(e => console.log('Video play failed:', e));

  video.onended = () => {
    // Hide overlay
    overlay.classList.remove('show');

    // STEP 4: Change map to WORLD ON FIRE!
    if (mapVideo) {
      mapVideo.src = BASE + 'map/worldonfire.webm';

      // SHAKE THE PHONE WHILE THE WORLD BURNS!
      const phone = document.getElementById('phone');
      if (phone) phone.classList.add('shake');

      // Continuous rumble while fire burns
      const fireRumble = setInterval(() => {
        vibrate([250, 100, 250, 100, 250]);
      }, 800);

      // Stop shaking after 8 seconds
      setTimeout(() => {
        if (phone) phone.classList.remove('shake');
        clearInterval(fireRumble);
      }, 8000);
    }

    // Apply pipe bomb effects - simple and balanced
    G.trumpHP = Math.min(200, G.trumpHP + 10); // +10 HP for Trump
    G.deepStateHP = Math.max(0, G.deepStateHP - 20); // -20 HP hit to deep state
    G.purity = Math.max(0, Math.min(100, G.purity + 2)); // +2% purity

    updateDisplay();
    showNews('PIPE BOMB DETONATED - DEEP STATE HIT HARD');
    playTrumpLaugh(3);
  };
}

// ⚠️ PROTECTED: Stand down sequence - peaceful exit if player doesn't detonate
function standDownPipeBomb() {
  const overlay = document.getElementById('pipebomb-overlay');
  const video = document.getElementById('pipebomb-video');
  const hotspot = document.getElementById('detonator-hotspot');
  const timer = document.getElementById('detonator-timer');

  // Clear timer
  if (pipeBombTimer) clearInterval(pipeBombTimer);

  // Hide hotspot and timer
  hotspot.classList.remove('show');
  timer.classList.remove('show');

  // Close overlay - no explosion, mercy shown
  setTimeout(() => {
    overlay.classList.remove('show');
    video.src = '';
    showNews('STOOD DOWN - MERCY SHOWN');
  }, 1000);
}

// ⚠️ END PROTECTED SECTION ⚠️
