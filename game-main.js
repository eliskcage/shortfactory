/* ==================== MAIN GAME LOGIC ====================
 * Initialization, display updates, game flow
 */

// ==================== INITIALIZATION ====================

// Flag to prevent game end check on initial load
let gameInitialized = false;

// Performance mode flag - set to true on slower devices
let performanceMode = false;

// DOM element cache to avoid repeated queries
const DOM = {};

document.addEventListener('DOMContentLoaded', () => {
  // Cache frequently accessed DOM elements
  DOM.phone = document.getElementById('phone');
  DOM.gameHint = document.getElementById('game-hint');
  DOM.blackopsAlertIcon = document.getElementById('blackops-alert-icon');
  DOM.blackopsAlertText = document.getElementById('blackops-alert-text');
  DOM.advisorOverlay = document.getElementById('advisor-overlay');
  DOM.advisorInfoBtn = document.getElementById('advisor-info-btn');
  DOM.mapSection = document.getElementById('map-section');
  DOM.tallyOverlay = document.getElementById('tally-overlay');
  DOM.trumpHotspot = document.getElementById('trump-hotspot');

  // Auto-detect device performance and enable lite mode if needed
  detectPerformanceMode();

  // Hard reset on long-hold of STATS button
  const statsBtn = document.getElementById('stats-btn');
  let holdTimer = null;
  let holdStartTime = 0;

  const startHold = (e) => {
    holdStartTime = Date.now();
    holdTimer = setTimeout(() => {
      // Confirm hard reset
      if (confirm('🔥 HARD RESET 🔥\n\nThis will:\n- Clear all game data\n- Delete all cookies\n- Clear cache\n- Reset everything\n\nContinue?')) {
        // Clear localStorage
        localStorage.clear();

        // Clear sessionStorage
        sessionStorage.clear();

        // Clear cookies
        document.cookie.split(";").forEach(c => {
          document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });

        // Show reset message
        alert('💀 GAME DATA NUKED 💀\n\nReloading...');

        // Hard reload with cache clear
        window.location.href = window.location.pathname + '?v=fresh&t=' + Date.now();
      }
    }, 2000); // 2 second hold
  };

  const endHold = () => {
    clearTimeout(holdTimer);
  };

  if (statsBtn) {
    statsBtn.addEventListener('mousedown', startHold);
    statsBtn.addEventListener('mouseup', endHold);
    statsBtn.addEventListener('mouseleave', endHold);
    statsBtn.addEventListener('touchstart', startHold);
    statsBtn.addEventListener('touchend', endHold);
    statsBtn.addEventListener('touchcancel', endHold);
  }

  // Check for URL parameters to set initial game state
  const urlParams = new URLSearchParams(window.location.search);

  // Fresh start / cache bust parameter
  if (urlParams.has('v') && (urlParams.get('v') === '99' || urlParams.get('v') === 'fresh')) {
    localStorage.clear();
    sessionStorage.clear();
    console.log('Fresh start: cleared all storage');
  }

  const urlPurity = urlParams.get('purity');
  const urlHP = urlParams.get('hp');
  const urlRound = urlParams.get('round');

  // Try to load saved game state
  const hadSave = loadGameState();
  if (hadSave) {
    console.log('Loaded saved game - Round', G.round, 'Purity', G.purity);
  }

  // Override with URL parameters if present (takes priority over saved game)
  if (urlPurity !== null) {
    G.purity = Math.max(0, Math.min(200, parseFloat(urlPurity))); // Allow up to 200% for future features
    console.log('URL override: Purity set to', G.purity);

    // If purity >= 50, skip Term 1 tally screen for testing
    if (G.purity >= 50) {
      G.term1Complete = true;
      G.term = 2;
      console.log('URL override: Skipped to Term 2 (purity >= 50)');
    }
  }
  if (urlHP !== null) {
    G.trumpHP = Math.max(0, Math.min(100, parseFloat(urlHP)));
    console.log('URL override: HP set to', G.trumpHP);
  }
  if (urlRound !== null) {
    G.round = Math.max(1, parseInt(urlRound));
    console.log('URL override: Round set to', G.round);
  }

  // Check Trump unlock
  if (G.trumpUnlocked) {
    document.getElementById('trump-hotspot').classList.add('unlocked');
  }
  // Check Hitler unlock
  if (G.hitlerUnlocked) {
    const hs = document.getElementById('hitler-hotspot');
    if (hs) hs.classList.add('unlocked');
  }

  // Setup black ops buttons — first one free, rest cost $10T surplus each
  const opsScroll = document.getElementById('blackops-scroll');
  ASSETS.blackops.forEach((op, i) => {
    const btn = document.createElement('button');
    btn.className = 'blackops-btn';
    btn.dataset.opsIndex = i;
    btn.innerHTML = `<img src="${op.gif}">`;
    if (i === 0) {
      // First one is always free
      btn.onclick = () => startPipeBombSequence(i);
    } else {
      // Greyed out — costs $10T * i surplus to unlock
      btn.style.opacity = '0.25';
      btn.style.filter = 'grayscale(1)';
      btn.style.pointerEvents = 'none';
      btn.onclick = () => startPipeBombSequence(i);
    }
    btn.oncontextmenu = (e) => { e.preventDefault(); return false; };
    opsScroll.appendChild(btn);
  });

  // Black ops unlock names — Dan's vision
  const OPS_UNLOCK_NAMES = [
    null, // index 0: always free
    '🦟 SPY TEC MOSQUITO CAMERAS UNLOCKED!',
    '💣 BOMB NECKLACE TOOL UNLOCKED!',
    '🎯 RACIST MISSION UNLOCKED!',
    '🛸 JEWISH SPACE LAZERS UNLOCKED!',
    '🔪 WETWORK ASSASSIN KIT UNLOCKED!',
    '👤 SHADOW COUP PROTOCOL UNLOCKED!'
  ];
  const opsUnlocked = [true, false, false, false, false, false, false]; // track which have been shown

  // Update black ops button locks based on surplus
  window.updateBlackOpsLocks = function() {
    if (!G) return;
    const surplus = G.debt <= 0 ? Math.abs(G.debt) : 0;
    const btns = document.querySelectorAll('#blackops-scroll .blackops-btn');
    btns.forEach((btn, i) => {
      if (i === 0) return; // first always free
      const cost = i * 10; // $10T per button index
      if (surplus >= cost) {
        btn.style.opacity = '1';
        btn.style.filter = 'none';
        btn.style.pointerEvents = 'auto';
        // Show unlock message once
        if (!opsUnlocked[i] && OPS_UNLOCK_NAMES[i]) {
          opsUnlocked[i] = true;
          showOpsUnlockMsg(OPS_UNLOCK_NAMES[i], i);
        }
      } else {
        btn.style.opacity = '0.25';
        btn.style.filter = 'grayscale(1)';
        btn.style.pointerEvents = 'none';
      }
    });
  };

  // Big flashy unlock notification for black ops
  function showOpsUnlockMsg(text, idx) {
    const phone = document.getElementById('phone');
    const msg = document.createElement('div');
    msg.style.cssText = 'position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) scale(0);z-index:9999;pointer-events:none;text-align:center;width:90%';
    msg.innerHTML = '<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#00ff88;text-shadow:0 0 10px #00ff88,0 0 20px #0f0,2px 2px 0 #000;padding:12px;background:rgba(0,20,0,0.9);border:2px solid #00ff88;border-radius:10px;box-shadow:0 0 30px rgba(0,255,136,0.5);animation:opsUnlockPulse 0.5s ease-out">'
      + '<div style="font-size:5px;color:#ffd700;margin-bottom:4px;letter-spacing:2px">BLACK OPS INTEL</div>'
      + '<div>' + text + '</div>'
      + '<div style="font-size:4px;color:#666;margin-top:4px">SURPLUS: $' + (idx * 10) + 'T ACHIEVED</div>'
      + '</div>';
    phone.appendChild(msg);
    // Animate in
    requestAnimationFrame(() => {
      msg.style.transition = 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      msg.style.transform = 'translate(-50%,-50%) scale(1)';
    });
    // Flash screen green
    flashScreen('green');
    vibrate(VIBES.success);
    if (typeof showNews === 'function') showNews(text);
    // Remove after 3 seconds
    setTimeout(() => {
      msg.style.transition = 'transform 0.3s ease-in, opacity 0.3s ease-in';
      msg.style.transform = 'translate(-50%,-50%) scale(0.5)';
      msg.style.opacity = '0';
      setTimeout(() => { if (msg.parentNode) msg.remove(); }, 300);
    }, 3000);
  }

  // Button listeners
  document.querySelectorAll('.game-btn').forEach(btn => {
    btn.addEventListener('contextmenu', (e) => { e.preventDefault(); return false; });

    let holdTimer;
    let holdTriggered = false;

    // Single click handler - check if hold was triggered
    btn.addEventListener('click', (e) => {
      if (holdTriggered) {
        e.preventDefault();
        return;
      }
      handleButtonClick(btn);
    });

    btn.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      holdTriggered = false;
      holdTimer = setTimeout(() => {
        holdTriggered = true;
        handleButtonHold(btn);
      }, 800);
    });
    btn.addEventListener('mouseup', () => {
      clearTimeout(holdTimer);
      // Reset hold flag after a short delay
      setTimeout(() => { holdTriggered = false; }, 50);
    });
    btn.addEventListener('mouseleave', () => {
      clearTimeout(holdTimer);
      setTimeout(() => { holdTriggered = false; }, 50);
    });

    btn.addEventListener('touchstart', e => {
      e.preventDefault();
      holdTriggered = false;
      holdTimer = setTimeout(() => {
        holdTriggered = true;
        handleButtonHold(btn);
      }, 800);
    });
    btn.addEventListener('touchend', e => {
      e.preventDefault();
      clearTimeout(holdTimer);
      if (!holdTriggered) handleButtonClick(btn);
    });
  });

  // OIL LONG-HOLD CHARGE MECHANIC (3x multiplier)
  const oilBtn = document.querySelector('[data-action="oil"]');
  if (oilBtn) {
    let oilChargeTimer = null;
    let oilSoundATimer = null;
    let oilChargeLevel = 0; // 0 = normal, 1 = charging, 2 = fully charged
    let oilFirstClick = true; // Track first ever click
    const soundA = document.getElementById('longhold-charge-a');
    const soundB = document.getElementById('longhold-charge-b');
    const oilIdx = parseInt(oilBtn.dataset.idx);

    const shouldUseChargeChanic = () => {
      // Don't use charge if: first click, or powerup active
      if (oilFirstClick) return false;
      if (oilBtn.classList.contains('glow-powerup')) return false;
      if (oilBtn.classList.contains('throb-powerup')) return false;
      return true;
    };

    const startOilCharge = () => {
      oilChargeLevel = 1;

      // Add supercharging animation
      oilBtn.classList.add('supercharging');

      // Add screen shake during charge
      const phoneFrame = document.getElementById('phone');
      if (phoneFrame) {
        phoneFrame.classList.add('charging-shake');
      }

      // Play sound A at 1 second (LOUD!)
      oilSoundATimer = setTimeout(() => {
        if (soundA && oilChargeLevel === 1) {
          soundA.volume = 0.9; // Boost volume from 50% to 90%
          soundA.currentTime = 0;
          soundA.play().catch(() => {});
        }
      }, 1000);

      // Full charge at 2 seconds
      oilChargeTimer = setTimeout(() => {
        oilChargeLevel = 2;
        // Change to fully charged animation
        oilBtn.classList.remove('supercharging');
        oilBtn.classList.add('fully-charged');
        // Remove screen shake
        if (phoneFrame) {
          phoneFrame.classList.remove('charging-shake');
        }
        setTimeout(() => oilBtn.classList.remove('fully-charged'), 300);
      }, 2000);
    };

    const cancelOilCharge = (executeAction = false) => {
      const wasFullyCharged = oilChargeLevel === 2;

      clearTimeout(oilChargeTimer);
      clearTimeout(oilSoundATimer);

      // Remove animations and screen shake
      oilBtn.classList.remove('supercharging', 'fully-charged');
      const phoneFrame = document.getElementById('phone');
      if (phoneFrame) {
        phoneFrame.classList.remove('charging-shake');
      }

      // Stop sound A if it's playing and we're canceling
      if (soundA && !wasFullyCharged) {
        soundA.pause();
        soundA.currentTime = 0;
      }

      if (executeAction) {
        if (wasFullyCharged) {
          // Play sound B on successful charge (LOUD!)
          if (soundB) {
            soundB.volume = 0.9; // Boost volume
            soundB.currentTime = 0;
            soundB.play().catch(() => {});
          }
          // 3x multiplier for charged oil - NO video (video only for powerup)
          doAction('oil', 3, false);
          showNews('⚡ CHARGED OIL! 3X CASH! ⚡');
        } else {
          // Normal oil action - no video
          doAction('oil', 1, false);
        }
      }

      oilChargeLevel = 0;
    };

    // Override oil button's default behavior
    oilBtn.addEventListener('mousedown', (e) => {
      if (e.button !== 0 || oilBtn.classList.contains('locked')) return;

      // Allow default for first click or powerup
      if (!shouldUseChargeChanic()) return;

      // Start charge mechanic
      e.preventDefault();
      e.stopPropagation();
      startOilCharge();
    }, true);

    oilBtn.addEventListener('mouseup', (e) => {
      if (oilChargeLevel > 0) {
        e.preventDefault();
        e.stopPropagation();
        cancelOilCharge(true);
      }
    }, true);

    oilBtn.addEventListener('mouseleave', () => {
      if (oilChargeLevel > 0) {
        cancelOilCharge(false);
      }
    }, true);

    oilBtn.addEventListener('touchstart', (e) => {
      if (oilBtn.classList.contains('locked')) return;

      // Allow default for first click or powerup
      if (!shouldUseChargeChanic()) return;

      // Start charge mechanic
      e.preventDefault();
      e.stopPropagation();
      startOilCharge();
    }, true);

    oilBtn.addEventListener('touchend', (e) => {
      if (oilChargeLevel > 0) {
        e.preventDefault();
        e.stopPropagation();
        cancelOilCharge(true);
      }
    }, true);

    // Track when oil is clicked (for first click detection)
    oilBtn.addEventListener('click', () => {
      if (oilFirstClick) {
        oilFirstClick = false;
      }
    });
  }

  // Block right-click on game
  document.getElementById('phone').addEventListener('contextmenu', (e) => {
    e.preventDefault();
    return false;
  });

  // Fullscreen on first tap (mobile)
  document.body.addEventListener('click', requestFullscreen, { once: true });
  document.body.addEventListener('touchstart', requestFullscreen, { once: true });

  // Secret reset: long hold on ROUND pill
  const roundPill = document.getElementById('pill-round');
  let resetHoldTimer;
  roundPill.addEventListener('mousedown', () => {
    resetHoldTimer = setTimeout(() => {
      resetGame();
    }, 2000); // 2 second hold
  });
  roundPill.addEventListener('mouseup', () => clearTimeout(resetHoldTimer));
  roundPill.addEventListener('mouseleave', () => clearTimeout(resetHoldTimer));
  roundPill.addEventListener('touchstart', (e) => {
    resetHoldTimer = setTimeout(() => {
      resetGame();
    }, 2000);
  });
  roundPill.addEventListener('touchend', () => clearTimeout(resetHoldTimer));

  // Secret litigation: long hold on DEBT pill
  const debtPill = document.getElementById('pill-debt');
  let litigationHoldTimer;
  debtPill.addEventListener('mousedown', () => {
    litigationHoldTimer = setTimeout(() => {
      toggleLitigation();
      vibrate(VIBES.success);
    }, 1500); // 1.5 second hold
  });
  debtPill.addEventListener('mouseup', () => clearTimeout(litigationHoldTimer));
  debtPill.addEventListener('mouseleave', () => clearTimeout(litigationHoldTimer));
  debtPill.addEventListener('touchstart', (e) => {
    litigationHoldTimer = setTimeout(() => {
      toggleLitigation();
      vibrate(VIBES.success);
    }, 1500);
  });
  debtPill.addEventListener('touchend', () => clearTimeout(litigationHoldTimer));

  // Start game
  updateTrumpVideo();
  updateMapVideo();
  updateDisplay();

  // Start threat meter rotation
  startThreatRotation();

  // Start icon rotations (feminism & tradwife)
  startIconRotations();

  // Start stereotype carousel
  startStereotypeCarousel();

  // Delay game end checks until after initial load settles
  setTimeout(() => {
    gameInitialized = true;
  }, 1000);

  showAdvisorSelect();
});

// ==================== FULLSCREEN ====================

function requestFullscreen() {
  // Only go fullscreen on mobile devices (narrow screens)
  if (window.innerWidth > 500) return;

  const elem = document.documentElement;
  if (elem.requestFullscreen) {
    elem.requestFullscreen().catch(() => {});
  } else if (elem.webkitRequestFullscreen) {
    elem.webkitRequestFullscreen();
  } else if (elem.msRequestFullscreen) {
    elem.msRequestFullscreen();
  }
}

// ==================== VOICE ANNOUNCEMENTS ====================

let previousRound = 1;
let previousCash = 0;

const CASH_PHRASES = [
  "fuck that's dope",
  "money money money",
  "cha-ching baby",
  "stack it up",
  "fuck yeah",
  "we rich now",
  "that's what I'm talking about",
  "hell yeah"
];

function speak(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.1;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;
    speechSynthesis.cancel(); // Cancel any ongoing speech
    speechSynthesis.speak(utterance);
  }
}

function announceRound(round) {
  if (round !== previousRound && round > 1) {
    speak(`Round ${round}`);
    previousRound = round;
  }
}

function announceCash(newCash) {
  // Only announce BIG cash increases (by 50 or more = $50M+)
  if (newCash > previousCash + 49) {
    const phrase = CASH_PHRASES[Math.floor(Math.random() * CASH_PHRASES.length)];
    speak(phrase);
    previousCash = newCash;
  }
}

// ==================== DISPLAY UPDATES ====================

let wealthResetTimer = null;

function updateWealthStack() {
  try {
    const wealthStack = document.getElementById('wealth-stack');
    if (!wealthStack) {
      console.error('wealth-stack element not found!');
      return;
    }

    // ALWAYS clear existing first
    wealthStack.innerHTML = '';

    // Show OIL DROPS (click to convert to cash)
    const barrels = Math.floor(Math.max(0, G.oilBarrels));
    const cash = Math.floor(Math.max(0, G.oilCash));
    console.log('updateWealthStack: barrels=' + barrels + ', cash=$' + cash + 'M');

    // Show oil if we have any - MAKE IT SUPER OBVIOUS AND CLICKABLE
    if (barrels > 0) {
      console.log('Creating oil display for ' + barrels + ' barrels');

      // Create ONE clickable oil pile instead of many
      const oilPile = document.createElement('div');
      oilPile.id = 'oil-sell-button';
      oilPile.style.position = 'absolute';
      oilPile.style.top = '10px';
      oilPile.style.left = '10px';
      oilPile.style.cursor = 'pointer';
      oilPile.style.padding = '8px';
      oilPile.style.background = 'rgba(0, 0, 0, 0.8)';
      oilPile.style.borderRadius = '8px';
      oilPile.style.border = '3px solid #0f0';
      oilPile.style.zIndex = '999';
      oilPile.style.pointerEvents = 'auto';
      oilPile.title = 'CLICK TO SELL ' + barrels + ' OIL FOR $' + (barrels * 500) + 'M';

      // Oil emoji and count
      const oilText = document.createElement('div');
      oilText.style.fontSize = '18px';
      oilText.style.color = '#0f0';
      oilText.style.fontWeight = 'bold';
      oilText.style.textAlign = 'center';
      oilText.style.pointerEvents = 'none';
      oilText.textContent = '⚫ x' + barrels;
      oilPile.appendChild(oilText);

      // Oil price display - SNES style!
      const priceText = document.createElement('div');
      priceText.style.fontSize = '10px';
      priceText.style.fontFamily = "'Press Start 2P', monospace";
      priceText.style.fontWeight = 'bold';
      priceText.style.textAlign = 'center';
      priceText.style.pointerEvents = 'none';
      priceText.style.marginTop = '3px';

      const mult = G.oilPrice;
      if (mult >= 1.5) {
        priceText.style.color = '#00ff00';
        priceText.style.textShadow = '2px 2px 0 #006600';
        priceText.style.animation = 'priceGoodPulse 0.8s infinite';
      } else if (mult < 0.8) {
        priceText.style.color = '#ff0000';
        priceText.style.textShadow = '2px 2px 0 #660000';
      } else {
        priceText.style.color = '#ffff00';
        priceText.style.textShadow = '2px 2px 0 #ff0000';
      }
      priceText.textContent = 'x' + mult.toFixed(1);
      oilPile.appendChild(priceText);

      const sellText = document.createElement('div');
      sellText.style.fontSize = '8px';
      sellText.style.color = '#fff';
      sellText.style.fontWeight = 'bold';
      sellText.style.textAlign = 'center';
      sellText.style.pointerEvents = 'none';
      sellText.style.marginTop = '2px';
      sellText.textContent = 'CLICK SELL';
      oilPile.appendChild(sellText);

      // Click handler - convert ALL oil to cash (with price multiplier!)
      const handleOilClick = (e) => {
        console.log('=== OIL CLICKED ===');
        console.log('Current barrels:', G.oilBarrels);
        console.log('Current cash:', G.oilCash);
        console.log('Oil price:', G.oilPrice + 'x');

        if (G.oilBarrels <= 0) {
          console.log('No oil to sell!');
          return;
        }

        const barrelsSold = G.oilBarrels;
        console.log('Barrels being sold:', barrelsSold);
        console.log('Will trigger tally?', barrelsSold >= 10);
        const baseValue = G.oilBarrels * 500;
        const cashValue = Math.floor(baseValue * G.oilPrice);
        const startCash = G.oilCash;
        G.oilBarrels = 0;

        console.log('Sold for $' + cashValue + 'M (base: $' + baseValue + 'M x ' + G.oilPrice.toFixed(2) + ')');

        // BIG SCORE TALLY for 10+ barrels!
        if (barrelsSold >= 10) {
          console.log('BIG SCORE! Starting tally animation...');

          // Create visual counter overlay - SNES style with GROW animation!
          const counterOverlay = document.createElement('div');
          counterOverlay.id = 'tally-counter-overlay';
          counterOverlay.style.position = 'fixed';
          counterOverlay.style.top = '50%';
          counterOverlay.style.left = '50%';
          counterOverlay.style.transform = 'translate(-50%, -50%) scale(0.3)';
          counterOverlay.style.zIndex = '10000';
          counterOverlay.style.fontSize = '48px';
          counterOverlay.style.fontFamily = "'Press Start 2P', monospace";
          counterOverlay.style.color = '#ffff00';
          counterOverlay.style.textShadow = '4px 4px 0 #ff0000, -2px -2px 0 #000';
          counterOverlay.style.pointerEvents = 'none';
          counterOverlay.style.textAlign = 'center';
          counterOverlay.style.padding = '20px';
          counterOverlay.style.background = 'rgba(0, 0, 0, 0.8)';
          counterOverlay.style.border = '4px solid #ffff00';
          counterOverlay.style.boxShadow = '0 0 30px rgba(255, 255, 0, 0.8)';
          counterOverlay.style.transition = 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
          counterOverlay.innerHTML = '+$0M';
          document.body.appendChild(counterOverlay);

          // Trigger grow animation after a tiny delay for dopamine hit!
          setTimeout(() => {
            counterOverlay.style.transform = 'translate(-50%, -50%) scale(1)';
          }, 50);

          // TALLY SOUND!
          let tallySound;
          try {
            tallySound = new Audio('https://www.shortfactory.shop/trump/arcadecounter.mp3');
            tallySound.volume = 0.5;
            tallySound.loop = true; // Loop during counting
            tallySound.play().catch(e => console.log('Tally sound play failed:', e));
          } catch (e) {
            console.log('Tally sound creation failed:', e);
          }

          // Dramatic counter animation - 2.5 seconds for big scores
          const duration = 2500;
          const steps = 50; // Lots of steps for smooth counting
          const increment = cashValue / steps;
          let currentStep = 0;
          let accumulatedCash = 0;

          const tallyInterval = setInterval(() => {
            currentStep++;
            accumulatedCash += increment;

            if (currentStep >= steps) {
              // Final step - set exact value
              G.oilCash = startCash + cashValue;
              clearInterval(tallyInterval);
              if (tallySound) {
                tallySound.pause();
                tallySound.currentTime = 0;
              }

              // Flash final amount with SCALE PULSE!
              counterOverlay.innerHTML = '+$' + cashValue.toLocaleString() + 'M';
              counterOverlay.style.color = '#00ff00';
              counterOverlay.style.textShadow = '4px 4px 0 #006600, -2px -2px 0 #000';
              counterOverlay.style.transform = 'translate(-50%, -50%) scale(1.2)';

              // Bounce back to normal size
              setTimeout(() => {
                counterOverlay.style.transform = 'translate(-50%, -50%) scale(1)';
              }, 150);

              // Remove overlay after a moment
              setTimeout(() => {
                counterOverlay.remove();
              }, 800);

              showNews('SOLD ' + barrelsSold + ' OIL: +$' + cashValue + 'M! (x' + G.oilPrice.toFixed(1) + ')');
              console.log('Tally complete! New cash total: $' + G.oilCash + 'M');
              vibrate([100, 50, 100]); // Big finale vibration
            } else {
              // Increment during tally - update visual counter!
              const currentAmount = Math.floor(accumulatedCash);
              G.oilCash = Math.floor(startCash + accumulatedCash);
              counterOverlay.innerHTML = '+$' + currentAmount.toLocaleString() + 'M';
              vibrate(15);
            }

            updateDisplay();
          }, duration / steps);
        } else {
          // Small sale - instant cash, no tally
          G.oilCash += cashValue;
          showNews('SOLD OIL: +$' + cashValue + 'M! (x' + G.oilPrice.toFixed(1) + ')');
          updateDisplay();
          vibrate([50, 50, 50]);
        }
      };

      // Add multiple event listeners to catch any type of click
      oilPile.addEventListener('click', (e) => {
        console.log('Click event fired');
        e.stopPropagation();
        handleOilClick(e);
      }, true);

      oilPile.addEventListener('mousedown', (e) => {
        console.log('Mousedown event fired');
        e.stopPropagation();
      }, true);

      oilPile.addEventListener('touchstart', (e) => {
        console.log('Touchstart event fired');
        e.stopPropagation();
        e.preventDefault();
      }, true);

      oilPile.addEventListener('touchend', (e) => {
        console.log('Touchend event fired');
        e.stopPropagation();
        e.preventDefault();
        handleOilClick(e);
      }, true);

      wealthStack.appendChild(oilPile);
      console.log('Oil display added to DOM');
    }

    // NO CASH DISPLAY - user doesn't want emojis
    // Cash amount is tracked in G.oilCash and shown elsewhere in UI
  } catch (error) {
    console.error('Wealth stack error:', error);
  }
}

// Rotating threat display - weighted rotation favoring Muslim/Feminist
let currentThreatDisplay = 0;
let threatRotationTimer = null;
const THREAT_ROTATION_SEQUENCE = [
  { type: 0, duration: 25000 }, // Muslim - 25 seconds
  { type: 2, duration: 25000 }, // Feminist - 25 seconds
  { type: 0, duration: 25000 }, // Muslim again - 25 seconds
  { type: 1, duration: 15000 }, // Israel - 15 seconds
  { type: 2, duration: 25000 }, // Feminist again - 25 seconds
  { type: 3, duration: 8000 }   // Christianity - 8 seconds (quick count animation)
];
let rotationIndex = 0;

function startThreatRotation() {
  if (threatRotationTimer) clearTimeout(threatRotationTimer);

  function nextRotation() {
    const current = THREAT_ROTATION_SEQUENCE[rotationIndex];
    currentThreatDisplay = current.type;
    updateThreatMeters();

    rotationIndex = (rotationIndex + 1) % THREAT_ROTATION_SEQUENCE.length;
    threatRotationTimer = setTimeout(nextRotation, current.duration);
  }

  nextRotation();
}

// Global cycle function — lets user tap threat-meters to cycle through factions
window.cycleThreatDisplay = function() {
  if (threatRotationTimer) clearTimeout(threatRotationTimer);
  currentThreatDisplay = (currentThreatDisplay + 1) % 4; // 0=muslim 1=israel 2=feminist 3=christian
  updateThreatMeters();
  // Resume auto-rotation after 30 seconds of no tapping
  threatRotationTimer = setTimeout(function() { startThreatRotation(); }, 30000);
};

// Feminism icon rotation (a/b different hair)
let currentFeminismIcon = 0;
const FEMINISM_ICONS = [
  'icons/feminism-threata.jpg',
  'icons/feminism-threatb.jpg'
];

// Tradwife icon rotation (a/b)
let currentTradwifeIcon = 0;
const TRADWIFE_ICONS = [
  'icons/tradwife.jpg',
  'icons/tradwifeb.jpg'
];

function startIconRotations() {
  // Rotate feminism icon every 3 seconds
  setInterval(() => {
    const femIcon = document.getElementById('feminism-icon');
    if (femIcon) {
      currentFeminismIcon = (currentFeminismIcon + 1) % 2;
      femIcon.src = FEMINISM_ICONS[currentFeminismIcon];
    }
  }, 3000);

  // Rotate tradwife icon every 3 seconds (offset by 1.5s)
  setTimeout(() => {
    setInterval(() => {
      const tradIcon = document.getElementById('tradwife-icon');
      if (tradIcon) {
        currentTradwifeIcon = (currentTradwifeIcon + 1) % 2;
        tradIcon.src = TRADWIFE_ICONS[currentTradwifeIcon];
      }
    }, 3000);
  }, 1500);
}

// ==================== STEREOTYPE CAROUSEL ====================
let currentSpecimen = 0;
let carouselAutoScroll = null;

function startStereotypeCarousel() {
  const scroll = document.getElementById('groups-scroll');
  const cards = Array.from(document.querySelectorAll('.group-card'));

  if (!scroll || cards.length === 0) return;

  // Clear any existing interval
  if (carouselAutoScroll) clearInterval(carouselAutoScroll);

  // Clone cards to create seamless infinite loop
  const originalCardsCount = cards.length;
  cards.forEach(card => {
    const clone = card.cloneNode(true);
    clone.classList.add('cloned');
    scroll.appendChild(clone);
  });

  // Get all cards including clones
  const allCards = Array.from(document.querySelectorAll('.group-card'));
  const singleSetWidth = cards.reduce((sum, card) => sum + card.offsetWidth, 0);

  // Infinite doomscroll - continuous smooth scroll
  let scrollSpeed = 0.5; // pixels per frame
  let isPaused = false;

  function doomScroll() {
    if (!isPaused && scroll) {
      scroll.scrollLeft += scrollSpeed;

      // Seamless loop - when reaching end of first set, reset to beginning
      if (scroll.scrollLeft >= singleSetWidth) {
        scroll.scrollLeft = 0;
      }
    }
    requestAnimationFrame(doomScroll);
  }

  // Start the infinite doomscroll
  doomScroll();

  // Hover to pause
  scroll.addEventListener('mouseenter', () => isPaused = true);
  scroll.addEventListener('mouseleave', () => isPaused = false);

  // Touch to pause
  scroll.addEventListener('touchstart', () => isPaused = true);
  scroll.addEventListener('touchend', () => setTimeout(() => isPaused = false, 2000));

  // Auto-select specimens as they scroll through
  carouselAutoScroll = setInterval(() => {
    if (!isPaused) {
      allCards.forEach(card => card.classList.remove('selected'));
      currentSpecimen = (currentSpecimen + 1) % originalCardsCount;
      // Select both original and clone
      cards[currentSpecimen].classList.add('selected');
      allCards[currentSpecimen + originalCardsCount].classList.add('selected');
    }
  }, 2000);

  // Click to select a specimen and show their video
  allCards.forEach((card, index) => {
    card.addEventListener('click', () => {
      const actualIndex = index % originalCardsCount;
      allCards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      currentSpecimen = actualIndex;
      isPaused = true;

      // Get character name and show their video page
      const label = card.querySelector('.group-label')?.textContent;
      const statsKey = LABEL_TO_STATS_MAP[label];
      if (statsKey && G.groupStats && G.groupStats[statsKey]) {
        showCharacterPage(statsKey, G.groupStats[statsKey]);
      }

      setTimeout(() => isPaused = false, 3000);
    });
  });
}

function resetCarousel() {
  const cards = document.querySelectorAll('.group-card');
  const scroll = document.getElementById('groups-scroll');

  // Clear selection and reset position
  cards.forEach(card => card.classList.remove('selected'));
  currentSpecimen = 0;
  if (scroll) scroll.scrollTo({ left: 0, behavior: 'smooth' });

  // Restart carousel
  if (carouselAutoScroll) clearInterval(carouselAutoScroll);
  startStereotypeCarousel();
}

// Map card labels to groupStats keys
const LABEL_TO_STATS_MAP = {
  'JIHAD': 'muslim',
  'FEMINISTS': 'feminist',
  'ISRAEL': 'israel',
  'SOYBOY': 'soy',
  'GIGACHAD': 'christianity',
  'CHAD': 'chad',
  'TRADWIFE': 'tradwife',
  'WOJAK': 'wojak',
  'CUCK NORMY': 'soy',
  'DUMPTRUCK': 'dumptruck'
};

function updateCharacterStats() {
  // Safety check - don't run if stats aren't open
  if (!statsOpen) return;

  const cards = document.querySelectorAll('.group-card');
  if (!cards || cards.length === 0) return;

  cards.forEach(card => {
    if (!card) return;

    const label = card.querySelector('.group-label')?.textContent;
    if (!label) return;

    const statsKey = LABEL_TO_STATS_MAP[label];
    if (!statsKey || !G || !G.groupStats || !G.groupStats[statsKey]) return;

    const stats = G.groupStats[statsKey];

    // Check if bars already exist
    let barsContainer = card.querySelector('.stat-bars');
    if (!barsContainer) {
      // Create bars container - SMALL, below image
      barsContainer = document.createElement('div');
      barsContainer.className = 'stat-bars';
      barsContainer.style.width = '90%';
      barsContainer.style.margin = '4px auto';
      barsContainer.style.display = 'flex';
      barsContainer.style.flexDirection = 'column';
      barsContainer.style.gap = '2px';
      barsContainer.style.pointerEvents = 'none'; // Don't interfere with card clicks
      barsContainer.style.padding = '0 5%';
      barsContainer.style.boxSizing = 'border-box';

      // Insert after group-icon (image), before group-label
      const groupIcon = card.querySelector('.group-icon');
      if (groupIcon && groupIcon.nextSibling) {
        card.insertBefore(barsContainer, groupIcon.nextSibling);
      } else {
        card.appendChild(barsContainer);
      }

      // Add click handler to show character's personal page
      card.style.cursor = 'pointer';
      card.addEventListener('click', () => {
        showCharacterPage(statsKey, stats);
      });
    }

    // Create or update the three bars (SMALL)
    barsContainer.innerHTML = '';

    // Psychological bar (RED)
    const psychBar = createStatBar(stats.psychological, 100, '#ff0000', '🧠', true);
    barsContainer.appendChild(psychBar);

    // Financial bar (GREEN)
    const finBar = createStatBar(stats.financial, 100, '#00ff00', '💰', true);
    barsContainer.appendChild(finBar);

    // Spiritual bar (WHITE)
    const spirBar = createStatBar(stats.spiritual, 100, '#ffffff', '✨', true);
    barsContainer.appendChild(spirBar);

    // Event counters (like rainbow hearts, poops)
    if (statsKey === 'feminist' && stats.eventCounters.rainbowHearts > 0) {
      const counter = document.createElement('div');
      counter.style.fontSize = '7px';
      counter.style.color = '#ff00ff';
      counter.style.textAlign = 'center';
      counter.style.fontFamily = "'Press Start 2P', monospace";
      counter.style.textShadow = '1px 1px 0 #000';
      counter.textContent = '💖x' + stats.eventCounters.rainbowHearts;
      barsContainer.appendChild(counter);
    }

    // Poop counter for Muslim threat
    if (statsKey === 'muslim' && G.poopThreat > 0) {
      const poopCounter = document.createElement('div');
      poopCounter.style.fontSize = '7px';
      poopCounter.style.color = '#ff8800';
      poopCounter.style.textAlign = 'center';
      poopCounter.style.fontFamily = "'Press Start 2P', monospace";
      poopCounter.style.textShadow = '1px 1px 0 #000';
      poopCounter.textContent = '💩'.repeat(Math.min(6, G.poopThreat));
      barsContainer.appendChild(poopCounter);
    }
  });
}

// Update bottom health meter strip
function updateHealthMeterStrip() {
  if (!statsOpen || !G || !G.groupStats) return;

  // Update Muslim/Jihad health
  const muslimHealth = document.getElementById('health-muslim');
  if (muslimHealth && G.groupStats.muslim) {
    const avg = (G.groupStats.muslim.psychological + G.groupStats.muslim.financial + G.groupStats.muslim.spiritual) / 3;
    muslimHealth.style.width = avg + '%';
  }

  // Update Israel/Jew health
  const israelHealth = document.getElementById('health-israel');
  if (israelHealth && G.groupStats.israel) {
    const avg = (G.groupStats.israel.psychological + G.groupStats.israel.financial + G.groupStats.israel.spiritual) / 3;
    israelHealth.style.width = avg + '%';
  }

  // Update Feminist health
  const feministHealth = document.getElementById('health-feminist');
  if (feministHealth && G.groupStats.feminist) {
    const avg = (G.groupStats.feminist.psychological + G.groupStats.feminist.financial + G.groupStats.feminist.spiritual) / 3;
    feministHealth.style.width = avg + '%';
  }

  // Update Christian health (christianity is the main stat)
  const christianHealth = document.getElementById('health-christian');
  if (christianHealth && G.christianity !== undefined) {
    christianHealth.style.width = G.christianity + '%';
  }
}

// Show character's personal page with their movie
function showCharacterPage(statsKey, stats) {
  console.log('Opening character page:', statsKey);

  // Create fullscreen overlay
  const overlay = document.createElement('div');
  overlay.id = 'character-page-overlay';
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100vw';
  overlay.style.height = '100vh';
  overlay.style.background = 'rgba(0, 0, 0, 0.95)';
  overlay.style.zIndex = '20000';
  overlay.style.display = 'flex';
  overlay.style.flexDirection = 'column';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';
  overlay.style.padding = '20px';
  overlay.style.boxSizing = 'border-box';

  // Character name title
  const title = document.createElement('div');
  title.style.fontFamily = "'Press Start 2P', monospace";
  title.style.fontSize = '20px';
  title.style.color = '#ffff00';
  title.style.textShadow = '3px 3px 0 #ff0000';
  title.style.marginBottom = '20px';
  title.style.textAlign = 'center';
  title.textContent = 'AMERICA WEIRDOES';
  overlay.appendChild(title);

  // Video container - MOBILE PHONE SIZE
  const videoContainer = document.createElement('div');
  videoContainer.style.position = 'relative'; // For absolute positioning of stats
  videoContainer.style.width = '360px';
  videoContainer.style.maxWidth = '90vw';
  videoContainer.style.height = '640px';
  videoContainer.style.maxHeight = '70vh';
  videoContainer.style.background = '#000';
  videoContainer.style.border = '4px solid #ffff00';
  videoContainer.style.boxShadow = '0 0 20px rgba(255, 255, 0, 0.5)';
  videoContainer.style.marginBottom = '20px';
  videoContainer.style.display = 'flex';
  videoContainer.style.alignItems = 'center';
  videoContainer.style.justifyContent = 'center';
  videoContainer.style.borderRadius = '20px';
  videoContainer.style.overflow = 'hidden';

  // Get ALL videos from ALL character types - America weirdoes showcase
  const availableVideos = [];
  if (ASSETS.weirdoes) {
    Object.keys(ASSETS.weirdoes).forEach(characterType => {
      if (ASSETS.weirdoes[characterType] && ASSETS.weirdoes[characterType].length > 0) {
        ASSETS.weirdoes[characterType].forEach(videoUrl => {
          availableVideos.push({
            url: videoUrl,
            character: characterType
          });
        });
      }
    });
  }

  const avgHealth = (stats.psychological + stats.financial + stats.spiritual) / 3;

  if (availableVideos.length === 0) {
    videoContainer.innerHTML = `<div style="color: #fff; font-family: 'Press Start 2P', monospace; font-size: 14px; text-align: center; padding: 20px;">NO VIDEOS<br/><br/>${statsKey}<br/><br/>Health: ${avgHealth.toFixed(0)}%</div>`;
  } else {
    // Horizontal scrolling carousel
    const carousel = document.createElement('div');
    carousel.style.display = 'flex';
    carousel.style.width = '100%';
    carousel.style.height = '100%';
    carousel.style.transition = 'transform 0.5s ease';
    carousel.style.position = 'relative';

    let currentIndex = 0;

    // Create video elements for each video
    availableVideos.forEach((videoData, index) => {
      const videoSlide = document.createElement('div');
      videoSlide.style.minWidth = '100%';
      videoSlide.style.height = '100%';
      videoSlide.style.display = 'flex';
      videoSlide.style.flexDirection = 'column';
      videoSlide.style.alignItems = 'center';
      videoSlide.style.justifyContent = 'center';
      videoSlide.style.background = '#000';
      videoSlide.style.position = 'relative';

      // Character label at top
      const label = document.createElement('div');
      label.style.position = 'absolute';
      label.style.top = '10px';
      label.style.left = '50%';
      label.style.transform = 'translateX(-50%)';
      label.style.fontFamily = "'Press Start 2P', monospace";
      label.style.fontSize = '10px';
      label.style.color = '#ffff00';
      label.style.textShadow = '2px 2px 0 #000';
      label.style.background = 'rgba(0, 0, 0, 0.7)';
      label.style.padding = '5px 10px';
      label.style.borderRadius = '5px';
      label.style.zIndex = '10';
      label.textContent = videoData.character.toUpperCase();
      videoSlide.appendChild(label);

      const video = document.createElement('video');
      video.src = videoData.url;
      video.style.width = '100%';
      video.style.height = '100%';
      video.style.objectFit = 'cover';
      video.loop = false;
      video.muted = false;
      video.playsInline = true;

      // Auto-play first video only
      if (index === 0) {
        video.autoplay = true;
      }

      // When video ends, swipe to next
      video.onended = () => {
        setTimeout(() => {
          currentIndex = (currentIndex + 1) % availableVideos.length;
          carousel.style.transform = `translateX(-${currentIndex * 100}%)`;

          // Rumble on swipe
          if (typeof vibrate === 'function') {
            vibrate([100, 50, 100]);
          }

          // Play the next video
          const nextVideo = carousel.children[currentIndex].querySelector('video');
          if (nextVideo) nextVideo.play().catch(()=>{});
        }, 500);
      };

      video.onerror = () => {
        videoSlide.innerHTML = `<div style="color: #fff; font-family: 'Press Start 2P', monospace; font-size: 12px; text-align: center; padding: 20px;">VIDEO ERROR<br/>${videoData.url}</div>`;
      };

      videoSlide.appendChild(video);
      carousel.appendChild(videoSlide);
    });

    // Touch swipe support
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
    });

    carousel.addEventListener('touchend', (e) => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    });

    function handleSwipe() {
      const swipeThreshold = 50;
      let swiped = false;

      if (touchEndX < touchStartX - swipeThreshold) {
        // Swipe left - next video
        currentIndex = (currentIndex + 1) % availableVideos.length;
        swiped = true;
      } else if (touchEndX > touchStartX + swipeThreshold) {
        // Swipe right - previous video
        currentIndex = (currentIndex - 1 + availableVideos.length) % availableVideos.length;
        swiped = true;
      }

      if (swiped) {
        carousel.style.transform = `translateX(-${currentIndex * 100}%)`;

        // Rumble on manual swipe
        if (typeof vibrate === 'function') {
          vibrate([100, 50, 100]);
        }

        // Pause all videos and play current
        carousel.querySelectorAll('video').forEach((v, i) => {
          if (i === currentIndex) {
            v.currentTime = 0;
            v.play().catch(()=>{});
          } else {
            v.pause();
          }
        });
      }
    }

    videoContainer.appendChild(carousel);
  }

  // Stats display - INSIDE VIDEO at bottom
  const statsDisplay = document.createElement('div');
  statsDisplay.style.position = 'absolute';
  statsDisplay.style.bottom = '10px';
  statsDisplay.style.left = '0';
  statsDisplay.style.right = '0';
  statsDisplay.style.fontFamily = "'Press Start 2P', monospace";
  statsDisplay.style.fontSize = '8px';
  statsDisplay.style.color = '#fff';
  statsDisplay.style.textAlign = 'center';
  statsDisplay.style.background = 'rgba(0, 0, 0, 0.8)';
  statsDisplay.style.padding = '8px';
  statsDisplay.style.textShadow = '1px 1px 0 #000';
  statsDisplay.style.pointerEvents = 'none';
  statsDisplay.innerHTML = `
    🧠 ${stats.psychological}% 💰 ${stats.financial}% ✨ ${stats.spiritual}% | 👤 ${(G.usPopulation / 1000000).toFixed(1)}M
  `;
  videoContainer.appendChild(statsDisplay);

  overlay.appendChild(videoContainer);

  // Close button
  const closeBtn = document.createElement('button');
  closeBtn.textContent = 'CLOSE';
  closeBtn.style.fontFamily = "'Press Start 2P', monospace";
  closeBtn.style.fontSize = '14px';
  closeBtn.style.padding = '10px 20px';
  closeBtn.style.background = 'linear-gradient(135deg, #ff0000, #cc0000)';
  closeBtn.style.color = '#fff';
  closeBtn.style.border = '3px solid #ffff00';
  closeBtn.style.cursor = 'pointer';
  closeBtn.style.boxShadow = '0 4px 0 #000, 0 0 15px rgba(255, 255, 0, 0.5)';
  closeBtn.onclick = () => {
    // Pause all videos in carousel
    overlay.querySelectorAll('video').forEach(v => v.pause());
    overlay.remove();
  };
  overlay.appendChild(closeBtn);

  // Click overlay background to close
  overlay.onclick = (e) => {
    if (e.target === overlay) {
      // Pause all videos in carousel
      overlay.querySelectorAll('video').forEach(v => v.pause());
      overlay.remove();
    }
  };

  document.body.appendChild(overlay);
}

function createStatBar(value, max, color, emoji, small = false) {
  const container = document.createElement('div');
  container.style.display = 'flex';
  container.style.alignItems = 'center';
  container.style.gap = small ? '2px' : '4px';

  // Emoji icon
  const icon = document.createElement('span');
  icon.textContent = emoji;
  icon.style.fontSize = small ? '6px' : '10px';
  icon.style.filter = 'drop-shadow(1px 1px 0 #000)';
  container.appendChild(icon);

  // Bar background
  const barBg = document.createElement('div');
  barBg.style.flex = '1';
  barBg.style.height = small ? '4px' : '8px';
  barBg.style.background = '#222';
  barBg.style.border = '1px solid #666';
  barBg.style.position = 'relative';
  barBg.style.boxShadow = 'inset 0 1px 2px rgba(0,0,0,0.5)';

  // Bar fill
  const barFill = document.createElement('div');
  barFill.style.width = Math.max(0, Math.min(100, (value / max) * 100)) + '%';
  barFill.style.height = '100%';
  barFill.style.background = color;
  barFill.style.boxShadow = '0 0 3px ' + color;
  barFill.style.transition = 'width 0.3s ease';

  // Low health warning flash
  if (value < 20) {
    barFill.style.animation = 'lowHealthFlash 1s infinite';
  }

  barBg.appendChild(barFill);
  container.appendChild(barBg);

  return container;
}

function updateThreatMeters() {
  try {
    const feministMeter = document.getElementById('feminist-meter');
    const muslimMeter = document.getElementById('muslim-meter');
    if (!feministMeter || !muslimMeter) {
      console.error('Threat meter elements not found');
      return;
    }

    // Hide both meters first and restore original labels
    feministMeter.classList.add('hidden');
    muslimMeter.classList.add('hidden');

    // Restore original labels
    const femLabel = feministMeter.querySelector('.threat-label');
    const muslimLabel = muslimMeter.querySelector('.threat-label');
    if (femLabel) {
      femLabel.textContent = '♀';
      femLabel.style.color = '#ff69b4';
      femLabel.style.textShadow = '0 0 8px rgba(255, 105, 180, 1)';
    }
    if (muslimLabel) {
      muslimLabel.textContent = '☪️';
      muslimLabel.style.color = '#00ff00';
      muslimLabel.style.textShadow = '0 0 8px rgba(0, 255, 0, 1)';
    }

    // Show current rotation display
    if (currentThreatDisplay === 0 && G.muslimThreat > 0) {
      // Muslim poop emojis (PERFECT - don't change)
      muslimMeter.classList.remove('hidden');
      const poopCount = Math.ceil(G.muslimThreat / 20);
      const container = muslimMeter.querySelector('.threat-hearts');
      container.innerHTML = '';
      for (let i = 0; i < poopCount; i++) {
        const poop = document.createElement('span');
        poop.textContent = '💩';
        poop.className = 'threat-poop';
        container.appendChild(poop);
      }
    }
    else if (currentThreatDisplay === 1 && G.israelGDP > 400) {
      // Israel shekels (use muslim meter, change label)
      muslimMeter.classList.remove('hidden');
      const label = muslimMeter.querySelector('.threat-label');
      const container = muslimMeter.querySelector('.threat-hearts');

      // Temporarily change label to Star of David
      label.textContent = '✡';
      label.style.color = '#4d94ff';
      label.style.textShadow = '0 0 8px rgba(77, 148, 255, 1)';

      container.innerHTML = '';
      const shekelCount = Math.min(3, Math.ceil(G.israelGDP / 250));
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
    else if (currentThreatDisplay === 2 && G.feminism > 0) {
      // Feminism rainbow hearts (PERFECT - don't change)
      feministMeter.classList.remove('hidden');
      const container = feministMeter.querySelector('.threat-hearts');
      container.innerHTML = '';
      const heartCount = Math.ceil(G.feminism / 20);
      for (let i = 0; i < heartCount; i++) {
        const heart = document.createElement('img');
        heart.src = 'https://www.shortfactory.shop/trump/heart.png';
        heart.className = 'threat-heart';
        container.appendChild(heart);
      }
    }
    else if (currentThreatDisplay === 3 && G.christianity > 0) {
      // Christianity crosses (PERFECT - don't change)
      feministMeter.classList.remove('hidden');
      const label = feministMeter.querySelector('.threat-label');
      const container = feministMeter.querySelector('.threat-hearts');

      // Temporarily change label to cross
      label.textContent = '✝';
      label.style.color = '#ffffff';
      label.style.textShadow = '0 0 10px rgba(255, 255, 255, 1)';

      container.innerHTML = '';
      const crossCount = Math.min(5, Math.ceil(G.christianity / 20));

      // Animate crosses appearing one by one like counting
      for (let i = 0; i < crossCount; i++) {
        setTimeout(() => {
          const cross = document.createElement('span');
          cross.textContent = '✝';
          cross.className = 'threat-cross cross-counting';
          cross.style.fontSize = '22px';
          cross.style.color = '#ffffff';
          cross.style.textShadow = '0 0 15px rgba(255, 255, 255, 1), 0 0 25px rgba(255, 215, 0, 0.9)';
          cross.style.animation = 'crossCount 0.5s ease-out';
          container.appendChild(cross);
          vibrate(15); // Tiny vibrate for each cross counted
        }, i * 700); // 700ms delay between each cross appearing
      }
    }
  } catch (error) {
    console.error('Threat meter error:', error);
  }
}

function updateDisplay() {
  document.getElementById('disp-purity').textContent = Math.round(G.purity) + '%';
  document.getElementById('disp-debt').textContent = '$' + G.debt.toFixed(1) + 'T';
  document.getElementById('disp-round').textContent = G.round;
  document.getElementById('round-display').textContent = G.round;
  document.getElementById('disp-moves').textContent = G.moves;
  // Oil cash now displayed as emoji wealth stack (see updateWealthStack)

  // Population display with color coding
  const popDisplay = document.getElementById('population-display');
  if (popDisplay) {
    const popChange = G.usPopulation - G.prevPopulation;
    const popMillions = (G.usPopulation / 1000000).toFixed(1);

    let color = '#fff'; // White = stable
    if (popChange > 10000) {
      color = '#0f0'; // Green = growing
    } else if (popChange < -10000) {
      color = '#f00'; // Red = dying
    }

    popDisplay.style.color = color;
    popDisplay.textContent = '👤 ' + popMillions + 'M';

    // Update previous population for next comparison
    G.prevPopulation = G.usPopulation;
  }

  // HP bar - supports up to 200% from litigation
  const hpFill = document.getElementById('trump-hp-fill');
  const hpText = document.getElementById('trump-hp-text');
  const hpPercent = Math.min(100, G.trumpHP); // Cap visual at 100%
  hpFill.style.width = hpPercent + '%';

  // Show actual HP number
  const hpValue = Math.round(G.trumpHP);
  if (G.trumpHP > 100) {
    hpText.textContent = hpValue + '% OVERSHIELD';
    hpText.style.color = '#0ff';
  } else {
    hpText.textContent = hpValue + '%';
    hpText.style.color = '#fff';
  }

  // Overshield glow when HP > 100% - with message
  if (G.trumpHP > 100) {
    hpFill.style.background = 'linear-gradient(90deg, #0f0, #0ff, #0f0)';
    hpFill.style.boxShadow = '0 0 15px #0ff, 0 0 30px #0f0';
    hpFill.style.animation = 'overshieldPulse 1s infinite';
  } else {
    hpFill.style.background = '';
    hpFill.style.boxShadow = '';
    hpFill.style.animation = '';
  }

  document.getElementById('ds-fill').style.width = G.deepStateHP + '%';

  // Progressive endgame glow - intensity increases from 90% to 96% purity
  // Glow stays at max intensity from 96% to 200% for future features
  // DISABLED on slower devices for performance
  const phoneFrame = document.getElementById('phone');
  const mapSection = document.getElementById('map-section');

  if (G.purity >= 90 && !performanceMode) {
    // Calculate glow intensity (0 at 90%, 1 at 96%+)
    const glowProgress = Math.min(1, (G.purity - 90) / 6);
    phoneFrame.classList.add('endgame-glow');
    phoneFrame.style.setProperty('--glow-intensity', glowProgress);

    // Add map glow too
    mapSection.classList.add('endgame-map-glow');
    mapSection.style.setProperty('--glow-intensity', glowProgress);
  } else {
    phoneFrame.classList.remove('endgame-glow');
    phoneFrame.style.removeProperty('--glow-intensity');
    mapSection.classList.remove('endgame-map-glow');
    mapSection.style.removeProperty('--glow-intensity');
  }

  // Stats overlay - traditional stats
  document.getElementById('stat-oil').textContent = G.oilReserves + 'B BBL';
  document.getElementById('stat-birth').textContent = G.birthrate.toFixed(2);
  document.getElementById('stat-age').textContent = G.trumpAge.toFixed(1);
  // Israel GDP with color coding
  const israelStat = document.getElementById('stat-israel');
  israelStat.textContent = '$' + G.israelGDP + 'B';
  // Remove previous classes
  israelStat.classList.remove('israel-high', 'israel-critical');
  // Add warning colors based on GDP level
  if (G.israelGDP > 700) {
    israelStat.classList.add('israel-critical'); // Red + flashing
  } else if (G.israelGDP > 500) {
    israelStat.classList.add('israel-high'); // Red
  }
  document.getElementById('stat-optics').textContent = G.optics;
  document.getElementById('stat-ds').textContent = G.deepStateHP + '%';

  // Stereotype group stats
  document.getElementById('stat-deadbodies').textContent = G.deadBodies + ' 💀';
  document.getElementById('stat-israel-aid').textContent = '$' + Math.floor(G.israelGDP / 10) + 'B';
  document.getElementById('stat-abortions').textContent = G.abortions + ' ☠️';
  document.getElementById('stat-babies').textContent = G.babies + ' 👶';

  // Voice announcements
  announceRound(G.round);
  announceCash(G.oilCash);

  // Update wealth stack and threat meters (with error isolation)
  try { updateWealthStack(); } catch (e) { console.error('Wealth update failed:', e); }
  try { updateThreatMeters(); } catch (e) { console.error('Threat update failed:', e); }
  try { updateCharacterStats(); } catch (e) { console.error('Character stats update failed:', e); }
  try { updateHealthMeterStrip(); } catch (e) { console.error('Health meter strip update failed:', e); }

  // Danger warning - show which stat is critical (priority order)
  const dangerWarning = document.getElementById('danger-warning');
  const dangerStat = document.getElementById('danger-stat');
  let dangerMessage = '';

  if (G.trumpHP <= 25) {
    dangerMessage = '💀 TRUMP HP CRITICAL';
  } else if (G.purity <= 15) {
    dangerMessage = '🔥 PURITY CRITICAL';
  } else if (G.deepStateHP >= 80) {
    dangerMessage = '👁️ DEEP STATE RISING';
  } else if (G.israelGDP > 500) {
    dangerMessage = '✡️ ISRAEL GDP HIGH - 2X DAMAGE!';
  } else if (G.feminism >= 70) {
    dangerMessage = '♀️ FEMINISM RISING - USE PSYOP!';
  } else if (G.deepStateHP >= 50) {
    dangerMessage = '💰 DEEP STATE SKIMMING OIL!';
  }

  if (dangerMessage && !statsOpen) {
    dangerStat.textContent = dangerMessage;
    dangerWarning.classList.add('show');
  } else {
    dangerWarning.classList.remove('show');
  }

  // Critical state - Tiered emergency system
  const trumpBox = document.getElementById('trump-box');
  const btnLitigation = document.getElementById('btn-litigation');
  const alertIcon = document.getElementById('blackops-alert-icon');
  const alertText = document.getElementById('blackops-alert-text');
  const mapVid = document.getElementById('map-video');

  // Determine which emergency tier is available
  let activeTier = 0;
  let tierText = '';
  let tierEmoji = '';

  if (G.trumpHP <= 20 && !G.nukeUsed) {
    activeTier = 3;
    tierText = 'NUCLEAR OPTION AVAILABLE';
    tierEmoji = '☢️';
  } else if (G.trumpHP <= 30 && !G.wheelUsed) {
    activeTier = 2;
    tierText = 'WHEEL OF DOOM AVAILABLE';
    tierEmoji = '☸️';
  } else if (G.trumpHP <= 50 && !G.blackopsUsed && G.debt <= 0) {
    activeTier = 1;
    tierText = 'BLACK OPS AVAILABLE';
    tierEmoji = '🎯';
  }

  // Show emergency alert if a tier is active
  if (activeTier > 0 && G.emergencyTier !== activeTier) {
    G.emergencyTier = activeTier;

    // DISABLED: Flashing alert system removed - it gets in the way
    // alertIcon.textContent = tierEmoji;
    // alertIcon.classList.add('show');
    // alertText.textContent = tierText;
    // alertText.classList.add('show');
    // startAlertAlternation(tierEmoji, tierText);

    // Play black.webm in map zone
    if (!mapVid.src.includes('black.webm')) {
      mapVid.src = BASE + 'map/black.webm';
      mapVid.loop = true;
      mapVid.load();
      mapVid.play().catch(() => {});
    }

    // Litigation button removed - no longer used
    // btnLitigation.classList.add('visible');

    // Expand map section during emergency
    document.getElementById('map-section').classList.add('emergency-active');

    // Critical visual at 20%
    if (G.trumpHP <= 20) {
      if (!trumpBox.classList.contains('critical')) {
        vibrate(VIBES.warning);
      }
      trumpBox.classList.add('critical');
    } else {
      trumpBox.classList.remove('critical');
    }
  } else if (activeTier === 0) {
    // No emergency tier active - hide everything
    G.emergencyTier = 0;
    stopAlertAlternation();
    alertIcon.classList.remove('show');
    alertText.classList.remove('show');
    trumpBox.classList.remove('critical');
    // btnLitigation.classList.remove('visible');
    document.getElementById('map-section').classList.remove('emergency-active');
  }

  // Show emergency button when a tier is active
  const btnEmergency = document.getElementById('btn-emergency');
  if (activeTier > 0) {
    btnEmergency.classList.add('visible');
    btnEmergency.textContent = tierEmoji;
  } else {
    btnEmergency.classList.remove('visible');
  }

  // Emergency dropdown can appear randomly or from good Trump cards
  // Don't auto-hide it here anymore

  // Dice roll available
  const pillMoves = document.getElementById('pill-moves');
  if (G.moves === 1) pillMoves.classList.add('clickable');
  else pillMoves.classList.remove('clickable');

  updateButtonUnlocks();
  checkGameEnd();

  // Check if we should show a hint
  if (typeof checkForHint === 'function') {
    checkForHint();
  }

  // Stock market unlock check + UI refresh
  try {
    if (typeof checkStockMarketUnlock === 'function') checkStockMarketUnlock();
    if (typeof updateStockMarketUI === 'function') updateStockMarketUI();
  } catch(e) { console.warn('Stock market UI error:', e); }

  // Auto-save after each update — never save a dead/lost game state
  if (gameInitialized && G.purity > 0 && G.trumpHP > 0 && G.deepStateHP < 100 && G.impeachmentCount < 3) {
    saveGameState();
  }
}

function updateButtonUnlocks() {
  document.querySelectorAll('.game-btn').forEach(btn => {
    const cost = parseInt(btn.dataset.cost) || 0;
    if (cost === 0 || G.oilCash >= cost) {
      btn.classList.remove('locked');
    } else {
      btn.classList.add('locked'); // Lock if can't afford
    }
  });
}

function updateTrumpVideo() {
  const vid = document.getElementById('trump-video');
  const rawIdx = Math.floor((100 - G.trumpHP) / 10);
  const idx = Math.max(0, Math.min(9, rawIdx));

  // Warn if bounds clamping occurred
  if (rawIdx !== idx) {
    console.warn(`Trump video index clamped: ${rawIdx} -> ${idx} (HP: ${G.trumpHP})`);
  }

  const newSrc = getVideo(ASSETS.trump[idx]);

  // Only reload if video source actually changed
  if (vid.src === newSrc || vid.src.endsWith(newSrc.split('/').pop())) {
    return; // Same video, no need to reload
  }

  vid.src = newSrc;
  vid.onerror = () => {
    console.error('Failed to load Trump video:', ASSETS.trump[idx]);
    // Asset validation available: call validateAssets() from console to check CDN health
  };
  vid.load();
  vid.play().catch(err => {
    // Silently handle autoplay blocks - expected behavior
    vid.muted = true;
    vid.play().catch(() => {});
  });
}

function updateMapVideo() {
  const vid = document.getElementById('map-video');
  const rawIdx = Math.floor(G.purity / 10);
  const idx = Math.max(0, Math.min(10, rawIdx));

  // Warn if bounds clamping occurred
  if (rawIdx !== idx) {
    console.warn(`Map video index clamped: ${rawIdx} -> ${idx} (Purity: ${G.purity})`);
  }

  const newSrc = ASSETS.maps[idx];

  // Only reload if video source actually changed
  if (vid.src === newSrc || vid.src.endsWith(newSrc.split('/').pop())) {
    return; // Same video, no need to reload
  }

  vid.src = newSrc;
  vid.onerror = () => {
    console.error('Failed to load map video:', ASSETS.maps[idx]);
  };
  vid.load();
  vid.play().catch(err => {
    // Silently handle autoplay blocks - expected behavior
    vid.muted = true;
    vid.play().catch(() => {});
  });
}

function showNews(txt) {
  const el = document.getElementById('news-text');
  el.textContent = txt;
  setTimeout(() => el.textContent = 'YOUR MOVE', 1500); // Messages fuck off faster
}

function flashScreen(color) {
  const flash = document.getElementById('flash');
  flash.className = 'screen-flash ' + color;
  setTimeout(() => flash.className = 'screen-flash', 500);
}

function shakeScreen() {
  document.getElementById('phone').classList.add('shake');
  setTimeout(() => document.getElementById('phone').classList.remove('shake'), 500);
}

// SNES-style round number flash - shows briefly when round changes
function showRoundFlash(roundNum) {
  const roundDisplay = document.getElementById('round-display');
  if (!roundDisplay) return;

  // Update the text
  roundDisplay.textContent = roundNum;

  // Trigger the SNES animation
  roundDisplay.classList.add('show');

  // NO SOUND - removed to avoid confusion with button clicks
  // Vibrate for impact
  vibrate(VIBES.powerup);

  // Remove the show class after animation completes (1.5s)
  setTimeout(() => {
    roundDisplay.classList.remove('show');
  }, 1500);
}

// Continuous emergency rumble for major disasters - world falling apart!
let rumbleInterval = null;
function startEmergencyRumble(duration) {
  // Clear any existing rumble
  if (rumbleInterval) {
    clearInterval(rumbleInterval);
    rumbleInterval = null;
  }

  const phone = document.getElementById('phone');
  const endTime = Date.now() + duration;

  // Shake every 400ms for continuous rumble effect
  rumbleInterval = setInterval(() => {
    if (Date.now() >= endTime) {
      clearInterval(rumbleInterval);
      rumbleInterval = null;
      phone.classList.remove('shake');

      // Stop shaking tally counter if it exists
      const tally = document.getElementById('tally-counter-overlay');
      if (tally) {
        tally.style.animation = tally.style.animation.replace('bioRumble 0.1s infinite, ', '');
      }
      return;
    }

    // Add shake class, remove after 350ms to create rumble rhythm
    phone.classList.add('shake');
    setTimeout(() => phone.classList.remove('shake'), 350);

    // Also shake tally counter if it's visible
    const tally = document.getElementById('tally-counter-overlay');
    if (tally) {
      // Add shake animation to whatever animation is already running
      if (!tally.style.animation.includes('bioRumble')) {
        tally.style.animation = 'bioRumble 0.1s infinite, ' + tally.style.animation;
      }
    }

    // Emergency vibration pattern
    vibrate([100, 50, 100]);
  }, 400);
}

// ==================== VIDEO PLAYBACK ====================

function playFullscreenVideo(src, onEnd, options = {}) {
  // Hide hints when video plays - they should fuck off
  const gameHint = document.getElementById('game-hint');
  if (gameHint && gameHint.classList.contains('show')) {
    dismissHint();
  }

  const overlay = document.getElementById('fullscreen-video');
  const vid = document.getElementById('fs-vid');
  vid.src = src;
  vid.muted = false;

  // Add tutorial class for narrower video
  if (options.tutorial || src.includes('how.webm')) {
    vid.classList.add('tutorial-video');
  } else {
    vid.classList.remove('tutorial-video');
  }

  overlay.classList.add('show');
  vid.play().catch(() => { vid.muted = true; vid.play().catch(() => {}); });

  // Cleanup helper to remove all event listeners
  const cleanup = () => {
    vid.onended = null;
    vid.onerror = null;
    overlay.onclick = null;
  };

  vid.onended = () => {
    overlay.classList.remove('show');
    vid.classList.remove('tutorial-video');
    cleanup();
    if (onEnd) onEnd();
  };

  // Error handler - call callback if video fails to load
  vid.onerror = () => {
    console.error('Video failed to load:', src);
    overlay.classList.remove('show');
    vid.classList.remove('tutorial-video');
    cleanup();
    if (onEnd) onEnd();
  };

  // Allow skipping unless unskippable
  if (options.unskippable) {
    overlay.onclick = null;
  } else {
    overlay.onclick = () => {
      vid.pause();
      overlay.classList.remove('show');
      vid.classList.remove('tutorial-video');
      cleanup();
      if (onEnd) onEnd();
    };
  }
}

// ==================== RESET GAME ====================

function resetGame() {
  if (confirm('Reset all progress? This will clear your unlocks and start fresh.')) {
    try {
      localStorage.clear();
    } catch (e) {
      console.warn('Could not clear storage:', e);
    }
    location.reload();
  }
}

// Purge game data after finale - keeps unlocks so player can pick new advisor
function purgeForFreshStart() {
  // Increment NG+ loop counter BEFORE the purge
  const currentLoop = parseInt(localStorage.getItem('ngPlusLoop') || '0');
  localStorage.setItem('ngPlusLoop', String(currentLoop + 1));

  // Keys to preserve (unlocks + admin + NG+ loop)
  const keepKeys = ['hitlerUnlocked', 'trumpUnlocked', 'cortex_unlocks', 'sf_auth_9k3x', 'completedEndings', 'disable_highscores', 'ngPlusLoop'];
  const preserved = {};
  keepKeys.forEach(key => {
    try {
      const val = localStorage.getItem(key);
      if (val !== null) preserved[key] = val;
    } catch (e) { /* ignore */ }
  });

  // Nuke everything
  try { localStorage.clear(); } catch (e) { /* ignore */ }
  try { sessionStorage.clear(); } catch (e) { /* ignore */ }

  // Clear cookies
  document.cookie.split(';').forEach(c => {
    document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/');
  });

  // Restore unlock keys
  Object.keys(preserved).forEach(key => {
    try { localStorage.setItem(key, preserved[key]); } catch (e) { /* ignore */ }
  });

  console.log('🧹 Game data purged - unlocks preserved for fresh start');
}

// ==================== ADVISOR ====================

function showAdvisorSelect() {
  // Clear any existing timer first
  clearInterval(advisorTimer);

  const overlay = document.getElementById('advisor-overlay');
  overlay.classList.add('show');

  // PHASE 2: Preload early game assets during 10-second countdown
  if (typeof preloadPhase2 === 'function') {
    preloadPhase2();
  }

  if (G.trumpUnlocked) {
    const advisorImg = document.getElementById('advisor-img');
    advisorImg.src = BASE + 'advisor/advisor2.jpg';
    advisorImg.onerror = () => {
      console.error('Failed to load advisor image');
      advisorImg.src = getFallbackAsset('image');
    };
    document.getElementById('trump-hotspot').classList.add('unlocked');
  }

  if (G.hitlerUnlocked) {
    const hitlerSpot = document.getElementById('hitler-hotspot');
    if (hitlerSpot) hitlerSpot.classList.add('unlocked');
  }

  let countdown = 10;
  document.getElementById('advisor-countdown').textContent = countdown;

  advisorTimer = setInterval(() => {
    countdown--;
    document.getElementById('advisor-countdown').textContent = countdown;
    if (countdown <= 0) {
      clearInterval(advisorTimer);
      if (G.trumpUnlocked) {
        // Bonus unlocked: default to character 6
        selectAdvisor(6);
      } else {
        // Fresh game: play default advisor video
        playDefaultAdvisor();
      }
    }
  }, 1000);
}

function playDefaultAdvisor() {
  document.getElementById('advisor-overlay').classList.remove('show');
  G.advisor = 1; // Default advisor

  playFullscreenVideo(BASE + 'advisor/advisor.webm', () => {
    playFullscreenVideo('pages/how.webm', () => {
      showNews('ADVISOR SELECTED!');
      if (G.ngPlusLoop > 0) setTimeout(() => showNews('NG+ LOOP ' + G.ngPlusLoop + '! ' + (G.ngPlusLoop * 30) + '% HARDER!'), 2000);

      // Show game elements now that advisor is done
      document.getElementById('phone').classList.remove('game-loading');

      // Wake up hint system 7 seconds after advisor videos finish
      hintDismissed = true;
      setTimeout(() => {
        hintDismissed = false;
      }, 7000);

      maybeActivatePowerup();
      startRandomInfoButton();
    });
  });
}

function selectAdvisor(num) {
  clearInterval(advisorTimer);
  G.advisor = num;

  // PHASE 3: Preload action assets while advisor video plays
  if (typeof preloadPhase3 === 'function') {
    preloadPhase3();
  }

  playFullscreenVideo(ASSETS.advisorPlay[num - 1], () => {
    document.getElementById('advisor-overlay').classList.remove('show');

    // Play the how.webm tutorial video for advisors 1-5
    if (num <= 5) {
      playFullscreenVideo('pages/how.webm', () => {
        showNews('ADVISOR ' + num + ' SELECTED!');
        if (G.ngPlusLoop > 0) setTimeout(() => showNews('NG+ LOOP ' + G.ngPlusLoop + '! ' + (G.ngPlusLoop * 30) + '% HARDER!'), 2000);

        // Show game elements now that advisor is done
        document.getElementById('phone').classList.remove('game-loading');

        // PHASE 4: Background load mid-game assets now that game has started
        if (typeof preloadPhase4 === 'function') {
          setTimeout(() => preloadPhase4(), 2000); // Wait 2 seconds then start background loading
        }

        // Wake up hint system 7 seconds after play1-5.webm finishes
        hintDismissed = true;
        setTimeout(() => {
          hintDismissed = false;
        }, 7000);

        maybeActivatePowerup();
        startRandomInfoButton();
      });
    } else {
      showNews('ADVISOR ' + num + ' SELECTED!');
      if (G.ngPlusLoop > 0) setTimeout(() => showNews('NG+ LOOP ' + G.ngPlusLoop + '! ' + (G.ngPlusLoop * 30) + '% HARDER!'), 2000);

      // Show game elements now that advisor is done
      document.getElementById('phone').classList.remove('game-loading');

      // PHASE 4: Background load mid-game assets now that game has started
      if (typeof preloadPhase4 === 'function') {
        setTimeout(() => preloadPhase4(), 2000); // Wait 2 seconds then start background loading
      }

      // Wake up hint system 7 seconds after play6.webm finishes
      hintDismissed = true;
      setTimeout(() => {
        hintDismissed = false;
      }, 7000);

      maybeActivatePowerup();
      startRandomInfoButton();
    }
  });
}

function startRandomInfoButton() {
  scheduleNextInfoAppearance();
}

function scheduleNextInfoAppearance() {
  // 20% more frequent than before (reduced delay)
  const delay = 12000 + Math.random() * 24000;
  infoButtonTimer = setTimeout(() => {
    showInfoButton();
  }, delay);
}

function showInfoButton() {
  const btn = document.getElementById('advisor-info-btn');
  btn.classList.add('visible');

  setTimeout(() => {
    btn.classList.remove('visible');
    scheduleNextInfoAppearance();
  }, 5000);
}

function playAdvisorInfo() {
  document.getElementById('advisor-info-btn').classList.remove('visible');

  const adviceArr = ASSETS.advisorAdvice[G.advisor] || ASSETS.advisorAdvice[0];
  const video = getVideo(adviceArr[Math.floor(Math.random() * adviceArr.length)]);

  // Play advisor video in Trump's head area instead of fullscreen
  const trumpVid = document.getElementById('trump-video');
  const originalSrc = trumpVid.src;

  trumpVid.src = video;
  trumpVid.muted = false;
  trumpVid.loop = false;
  trumpVid.load();
  trumpVid.play().catch(() => { trumpVid.muted = true; trumpVid.play().catch(() => {}); });

  trumpVid.onended = () => {
    // Restore original Trump video
    trumpVid.src = originalSrc;
    trumpVid.muted = true;
    trumpVid.loop = true;
    trumpVid.load();
    trumpVid.play().catch(() => {});
    trumpVid.onended = null;

    if (Math.random() < 0.3 && !G.meanTweetMode) enableMeanTweet();
    scheduleNextInfoAppearance();
  };
}

// ==================== GAME FLOW ====================

let _pausedAudioState = [];

function pauseGameSounds() {
  if (powerupInterval) clearInterval(powerupInterval);
  if (infoButtonTimer) clearTimeout(infoButtonTimer);
  stopRandomMeanTweet();
  document.getElementById('advisor-info-btn').classList.remove('visible');
  // Pause ALL audio/video elements and store their state
  _pausedAudioState = [];
  document.querySelectorAll('audio, video').forEach(el => {
    if (!el.paused) {
      _pausedAudioState.push({ el: el, time: el.currentTime, vol: el.volume });
      el.pause();
    }
  });
  // Stop geiger if running
  if (typeof stopGeiger === 'function') stopGeiger();
}

function resumeGameSounds() {
  maybeActivatePowerup();
  startRandomInfoButton();
  if (G.round >= 2) startRandomMeanTweet();
  // Resume all audio/video that were playing before pause
  _pausedAudioState.forEach(s => {
    try { s.el.currentTime = s.time; s.el.volume = s.vol; s.el.play().catch(()=>{}); } catch(e){}
  });
  _pausedAudioState = [];
}

function endOfTurn() {
  vibrate(VIBES.roundEnd);

  const gnVid = getVideo(ASSETS.goodnight[Math.floor(Math.random() * ASSETS.goodnight.length)]);
  playFullscreenVideo(gnVid, () => {
    showNews('TRUMP NAPPING...');
    deepStateTurn();
  });
}

function deepStateTurn() {
  const scale = getDifficultyScale();
  // Deep State fights back harder — base 5 + bonus from current HP
  G.deepStateHP += ((5 + Math.floor(G.deepStateHP / 10)) * G.difficultyMult) / scale;
  G.debt += ((1 + Math.random() * 2) * G.difficultyMult) / scale;
  G.trumpAge += 0.1 / scale;

  // Feminism creeps up each turn - need psyop to fight it
  G.feminism = Math.min(100, G.feminism + (3 * G.difficultyMult) / scale);

  // Israel GDP grows each turn - need to cut aid to control it
  G.israelGDP += Math.floor((10 + Math.random() * 20) / scale);

  // Check if Trump hit 98 - play old.webm
  if (G.trumpAge >= 98 && !G.oldVideoPlayed) {
    G.oldVideoPlayed = true;
    playFullscreenVideo(SPECIAL_VIDEOS.trumpOld, () => {
      showNews('TRUMP IS ANCIENT!');
      const dsVid = getVideo(ASSETS.deepstate[Math.floor(Math.random() * ASSETS.deepstate.length)]);
      playFullscreenVideo(dsVid, () => {
        showNews('DEEPSTATE STRIKES!');
        newRound();
      });
    });
    return;
  }

  const dsVid = getVideo(ASSETS.deepstate[Math.floor(Math.random() * ASSETS.deepstate.length)]);
  playFullscreenVideo(dsVid, () => {
    showNews('DEEPSTATE STRIKES!');
    newRound();
  });
}

function newRound() {
  G.round++;

  // PHASE 5: Preload endgame assets at round 5
  if (G.round === 5 && typeof preloadPhase5 === 'function') {
    preloadPhase5();
  }

  // Show SNES-style round number flash
  if (G.round > 1) {
    showRoundFlash(G.round);
  }

  // Passive damage from Deep State influence each round
  const passiveDmg = typeof PASSIVE_DAMAGE_PER_ROUND !== 'undefined' ? PASSIVE_DAMAGE_PER_ROUND : 3;
  const rawDsDamage = passiveDmg + Math.floor(G.deepStateHP / 20); // More DS = more damage
  const dsDamage = Math.min(rawDsDamage, 10); // Cap at 10 to prevent extreme damage
  G.trumpHP -= dsDamage;
  if (G.round > 1) {
    showNews('DEEP STATE DRAINS ' + dsDamage + ' HP!');
  }

  // Feminism passive creep + damage when high
  G.feminism = Math.min(100, G.feminism + 2);
  if (G.feminism >= 60) {
    const femDmg = Math.floor((G.feminism - 50) / 10);
    G.trumpHP -= femDmg;
    if (femDmg > 0 && G.round > 1) {
      showNews('WOKE MOB ATTACKS! -' + femDmg + ' HP!');
    }
  }

  if (G.round === 2) {
    G.purity = 10;
    vibrate(VIBES.warning);
    showNews('PURITY RESET TO 10%!');
  }

  if (G.diceTurns > 0) {
    G.moves = G.baseMoves;
    G.diceTurns--;
    if (G.diceTurns === 0) G.baseMoves = 5;
  } else {
    G.moves = G.term === 2 ? 3 : 5;
  }

  clearAllPowerups();
  disableMeanTweet();
  maybeActivatePowerup();

  if (G.round >= 2) {
    startRandomMeanTweet();
  }

  if (G.round !== 2) showNews('ROUND ' + G.round + '!');

  // Stock market round tick (prices + DS trades + auto trades + settlement)
  try { if (typeof stockMarketRoundTick === 'function') stockMarketRoundTick(); }
  catch(e) { console.warn('Stock market tick error:', e); }

  updateDisplay();
}

function startRandomMeanTweet() {
  if (meanTweetTimer) clearTimeout(meanTweetTimer);
  scheduleMeanTweetToggle();
}

function scheduleMeanTweetToggle() {
  const delay = 8000 + Math.random() * 12000;
  meanTweetTimer = setTimeout(() => {
    if (!G.meanTweetMode && G.moves > 0) {
      enableMeanTweet();
      const hideDelay = 6000 + Math.random() * 6000;
      setTimeout(() => {
        if (G.meanTweetMode) {
          disableMeanTweet();
          scheduleMeanTweetToggle();
        }
      }, hideDelay);
    } else {
      scheduleMeanTweetToggle();
    }
  }, delay);
}

function stopRandomMeanTweet() {
  if (meanTweetTimer) {
    clearTimeout(meanTweetTimer);
    meanTweetTimer = null;
  }
}

// ==================== DICE ====================

function tryDiceRoll() {
  if (G.moves !== 1) return;

  // Don't allow dice roll if other overlays are showing
  const blockingOverlays = ['nuke-overlay', 'wheel-overlay', 'blackops-overlay', 'fullscreen-video', 'emergency-drop'];
  for (const id of blockingOverlays) {
    const el = document.getElementById(id);
    if (el && el.classList.contains('show')) {
      console.log('Dice roll blocked by active overlay:', id);
      return;
    }
  }

  const pillMoves = document.getElementById('pill-moves');
  if (!pillMoves.classList.contains('clickable')) return;
  pillMoves.classList.remove('clickable');

  const dice = ASSETS.dice[Math.floor(Math.random() * ASSETS.dice.length)];

  document.getElementById('dice-overlay').classList.add('show');
  document.getElementById('phone').classList.add('dice-active');
  document.getElementById('dice-result').textContent = '🎲';
  document.getElementById('dice-text').textContent = 'Rolling...';

  playFullscreenVideo(dice.v, () => {
    const resultEl = document.getElementById('dice-result');
    resultEl.textContent = dice.n;

    // SNES style with attitude - bigger number = bigger size, red if < 7
    const fontSize = 50 + (dice.n * 15); // Scales from 50px (0) to 170px (8)
    resultEl.style.fontSize = fontSize + 'px';
    resultEl.style.fontFamily = "'Press Start 2P', 'Courier New', monospace";

    if (dice.n < 7) {
      resultEl.style.color = '#ff0000';
      resultEl.style.textShadow = '4px 4px 0 #ffff00, 0 0 20px #ff0000';
    } else {
      resultEl.style.color = '#ffff00';
      resultEl.style.textShadow = '4px 4px 0 #ff0000, 0 0 30px #ffff00';
    }

    document.getElementById('dice-text').textContent = dice.n === 0 ? 'BAD LUCK!' : '+' + dice.n + ' MOVES!';

    G.moves += dice.n;
    if (dice.n > 0) {
      G.baseMoves = dice.n;
      G.diceTurns = 1;
    }

    setTimeout(() => {
      document.getElementById('dice-overlay').classList.remove('show');
      document.getElementById('phone').classList.remove('dice-active');
      updateDisplay();
    }, 2000);
  });
}

// ==================== STATS TOGGLE ====================

function toggleStats() {
  statsOpen = !statsOpen;
  document.getElementById('stats-overlay').classList.toggle('show', statsOpen);
  document.getElementById('map-section').classList.toggle('expanded', statsOpen);

  // Stop slot machine when leaving map
  if (statsOpen && typeof stopSlotMachine === 'function') {
    stopSlotMachine();
  }

  // Hide/show emergency alert when stats is toggled
  // DISABLED: Alert system removed
  // const alertIcon = document.getElementById('blackops-alert-icon');
  // const alertText = document.getElementById('blackops-alert-text');

  if (statsOpen) {
    // Hide danger warning while stats is open
    document.getElementById('danger-warning').classList.remove('show');
    // Kill the wheel if it's showing — wheel is map-only
    document.getElementById('wheel-overlay').classList.remove('show');
    if (typeof wheelTimer !== 'undefined') clearInterval(wheelTimer);
    // Refresh stats display when opening overlay
    updateDisplay();
  }
}

// ==================== PERFORMANCE DETECTION ====================

function detectPerformanceMode() {
  // Check if already stored in localStorage
  const stored = safeGetLocal('performanceMode');
  if (stored !== null) {
    performanceMode = stored === 'true';
    if (performanceMode) {
      console.log('Performance Mode: ON (mobile device - no glow)');
    }
    return;
  }

  // Disable glow on ALL mobile devices (desktop-only feature)
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  performanceMode = isMobile;
  safeSetLocal('performanceMode', performanceMode.toString());

  if (performanceMode) {
    console.log('Performance Mode: ON (mobile device - glow disabled)');
  } else {
    console.log('Performance Mode: OFF (desktop - glow enabled)');
  }
}

// ==================== GAME END ====================

// Determine ending type using priority-based ENDING_DEFS from config.js
function determineEnding() {
  // Sort by priority (lowest number = highest priority)
  const sorted = ENDING_DEFS.slice().sort((a, b) => a.priority - b.priority);
  for (const def of sorted) {
    if (!def.condition || def.condition(G)) return def.id;
  }
  return 'peaceful'; // ultimate fallback
}

function checkGameEnd() {
  // Don't check during initial load
  if (!gameInitialized) {
    return;
  }

  // Don't trigger endings while litigation is open or just returned
  const litOverlay = document.getElementById('litigation-overlay');
  if (litOverlay && litOverlay.classList.contains('show')) {
    return;
  }

  // Grace period after returning from litigation - don't end game immediately
  if (window.litigationCooldown) {
    return;
  }

  // Don't interrupt fullscreen videos - wait for them to finish
  const fsOverlay = document.getElementById('fullscreen-video');
  if (fsOverlay && fsOverlay.classList.contains('show')) {
    // Video is playing, check again after it ends
    setTimeout(checkGameEnd, 500);
    return;
  }

  // Don't interrupt Trump cards - wait for them to finish
  const cardOverlay = document.getElementById('trump-card-overlay');
  if (cardOverlay && cardOverlay.classList.contains('show')) {
    // Trump card is showing, check again after it ends
    setTimeout(checkGameEnd, 500);
    return;
  }

  // ===== DANGER WARNINGS before game-ending scenarios =====
  if (G.trumpHP > 0 && G.trumpHP <= 20 && !window._warnedHP) {
    window._warnedHP = true;
    showNews('⚠️ TRUMP HP CRITICAL: ' + Math.round(G.trumpHP) + '%!');
    setTimeout(() => { window._warnedHP = false; }, 15000);
  }
  if (G.deepStateHP >= 80 && G.deepStateHP < 100 && !window._warnedDS) {
    window._warnedDS = true;
    showNews('⚠️ DEEP STATE AT ' + Math.round(G.deepStateHP) + '% — DANGER!');
    setTimeout(() => { window._warnedDS = false; }, 15000);
  }
  if (G.purity > 0 && G.purity <= 8 && !window._warnedPur) {
    window._warnedPur = true;
    showNews('⚠️ PURITY CRITICALLY LOW: ' + G.purity.toFixed(1) + '!');
    setTimeout(() => { window._warnedPur = false; }, 15000);
  }
  if (G.impeachmentCount === 2 && !window._warnedImp) {
    window._warnedImp = true;
    showNews('⚠️ 2/3 IMPEACHMENTS — ONE MORE = GAME OVER!');
  }

  if (!G.term1Complete && G.term === 1 && (G.purity >= 50 || G.round >= 15)) {
    G.term1Complete = true;
    showTallyScreen();
    return;
  }

  if (G.purity >= 96) {
    // Route through finale system (highscore → narration → ending)
    startFinale();
  } else if (G.trumpHP <= 0 || G.deepStateHP >= 100 || G.purity <= 0 || G.impeachmentCount >= 3) {
    // Log which condition triggered game over
    let reason = 'UNKNOWN';
    if (G.trumpHP <= 0) reason = 'TRUMP HP = 0 (HP:' + G.trumpHP.toFixed(0) + ')';
    else if (G.deepStateHP >= 100) reason = 'DEEP STATE HIT 100% (DS:' + G.deepStateHP.toFixed(0) + ')';
    else if (G.purity <= 0) reason = 'PURITY HIT 0 (Pur:' + G.purity.toFixed(1) + ')';
    else if (G.impeachmentCount >= 3) reason = 'IMPEACHED 3x';
    console.warn('GAME OVER REASON:', reason, JSON.stringify({trumpHP:G.trumpHP,deepStateHP:G.deepStateHP,purity:G.purity,impeach:G.impeachmentCount,round:G.round}));
    if (typeof showNews === 'function') showNews('GAME OVER: ' + reason);
    addDeathOverlay();
  }
}

// ==================== FINALE SYSTEM ====================
// Orchestrates: highscore entry → AI narration → win video → ending screen

let finaleActive = false;

// Mute ALL game audio/video during AI narration
function muteAllGameAudio() {
  document.querySelectorAll('audio, video').forEach(el => {
    el.dataset.finaleVol = el.volume;
    el.dataset.finaleMuted = el.muted;
    el.muted = true;
    el.volume = 0;
  });
}

// Restore all game audio/video after narration
function unmuteAllGameAudio() {
  document.querySelectorAll('audio, video').forEach(el => {
    if (el.dataset.finaleVol !== undefined) {
      el.volume = parseFloat(el.dataset.finaleVol);
      el.muted = el.dataset.finaleMuted === 'true';
      delete el.dataset.finaleVol;
      delete el.dataset.finaleMuted;
    }
  });
}

// Pick the right win video based on playstyle
function getWinVideo() {
  if (G.nukeUsed || G.usedAggressive) return BASE + 'win_aggressive.webm';
  return BASE + 'win_no_hostile.webm';
}

function startFinale() {
  if (finaleActive) return; // Prevent double-trigger
  finaleActive = true;
  pauseGameSounds();

  // Play completion sound
  const completionSound = new Audio(BASE + 'asset/completion.mp3');
  completionSound.id = 'completion-sound';
  completionSound.volume = 0.8;
  completionSound.play().catch(() => {});

  // Slowly fade entire page to greyscale over the MP3 duration (128s)
  document.documentElement.style.transition = 'filter 128s linear';
  requestAnimationFrame(() => {
    document.documentElement.style.filter = 'grayscale(100%)';
  });

  // When MP3 ends: page is fully grey, purge data for fresh start
  completionSound.onended = () => {
    purgeForFreshStart();
  };

  // Check if highscore entry should show first
  const purity = Math.round(G.purity);
  const wealth = (typeof getPlayerWealth === 'function') ? getPlayerWealth() : 0;
  const hasRecorded = (typeof recordedMilestones !== 'undefined') ? recordedMilestones.has(purity) : true;
  const qualifies = purity >= 97 && !hasRecorded && (typeof showNameEntry === 'function');

  if (qualifies) {
    // Show highscore entry - callback triggers narration after
    if (typeof recordedMilestones !== 'undefined') recordedMilestones.add(purity);
    showNameEntry(purity);
    // Set callback for when highscore is done (submit or skip)
    window.onFinaleHighScoreDone = () => {
      window.onFinaleHighScoreDone = null;
      setTimeout(() => narrateFinale(), 800);
    };
  } else {
    // Skip straight to narration
    narrateFinale();
  }
}

function narrateFinale() {
  // Mute ALL game audio so the AI voice is the only thing playing
  muteAllGameAudio();

  const lines = [];
  const h = G.gameHistory || {};
  const acts = h.actions || {};
  const p = Math.round(G.purity);

  // === OPENING ===
  lines.push("Ladies and gentlemen! The results are in! Let's review this absolute masterpiece of political strategy!");

  // === PURITY RESULT ===
  if (p >= 100) {
    lines.push("One hundred percent purity! Flawless! Immaculate! The deep state didn't just lose, it ceased to exist!");
  } else if (p >= 98) {
    lines.push(p + " percent purity! The founding fathers are literally rising from their graves to applaud!");
  } else {
    lines.push(p + " percent purity! The swamp? Drained. The deep state? Destroyed. America? Great again!");
  }

  // === ACTION BREAKDOWN - most used action ===
  const actionNames = Object.keys(acts);
  if (actionNames.length > 0) {
    const sorted = actionNames.sort((a, b) => acts[b] - acts[a]);
    const topAction = sorted[0];
    const topCount = acts[topAction];

    if (topAction === 'oil' && topCount >= 10) {
      lines.push("You clicked oil " + topCount + " times! You were absolutely addicted to that black gold! Drill baby drill!");
    } else if (topAction === 'oil') {
      lines.push("Oil was your go-to move! " + topCount + " times you went back to the well! Classic petro-state strategy!");
    } else if (topAction === 'war' && topCount >= 5) {
      lines.push("War! " + topCount + " times! You basically turned the Oval Office into the Pentagon!");
    } else if (topAction === 'war') {
      lines.push(topCount + " wars declared! Each one more questionable than the last! Beautiful!");
    } else if (topAction === 'drone') {
      lines.push(topCount + " drone strikes! You never even left the couch! Peak efficiency!");
    } else if (topAction === 'psyop') {
      lines.push(topCount + " psyops! You were running a full propaganda machine! Goebbels would be proud!");
    } else if (topAction === 'audit') {
      lines.push(topCount + " audits! You weaponized the IRS! That's some next level bureaucratic warfare!");
    } else if (topAction === 'aid') {
      lines.push(topCount + " times cutting aid! You basically told the world to figure it out themselves!");
    } else if (topAction === 'home') {
      lines.push(topCount + " email campaigns! You spammed more than a Nigerian prince!");
    } else if (topAction === 'loan') {
      lines.push(topCount + " Elon loans! Musk was basically your personal ATM!");
    } else {
      lines.push(topAction + " was your favourite move! " + topCount + " times! You really committed to that strategy!");
    }

    // Second most used if interesting
    if (sorted.length >= 2 && acts[sorted[1]] >= 3) {
      const second = sorted[1];
      lines.push("And " + second + " " + acts[second] + " times as your backup plan! Diversified chaos!");
    }
  }

  // === NUKE HISTORY - THE GOLD ===
  if (h.nukes && h.nukes.length > 0) {
    if (h.nukes.length === 1) {
      lines.push("You nuked " + h.nukes[0].target + "! " + h.nukes[0].tagline + "! One nuke! That's all it took!");
    } else {
      lines.push("Oh my god! You launched " + h.nukes.length + " nuclear weapons!");

      // Check for duplicate targets
      const targetCounts = {};
      h.nukes.forEach(n => { targetCounts[n.target] = (targetCounts[n.target] || 0) + 1; });
      const dupes = Object.entries(targetCounts).filter(([_, c]) => c > 1);

      if (dupes.length > 0) {
        dupes.forEach(([target, count]) => {
          lines.push("You nuked " + target + " " + count + " times! In the same spot! What did they do to you?! There's nothing left to nuke!");
        });
      }

      // List unique targets
      const uniqueTargets = [...new Set(h.nukes.map(n => n.target))];
      if (uniqueTargets.length > 2) {
        lines.push("The nuclear tour included " + uniqueTargets.slice(0, -1).join(", ") + " and " + uniqueTargets[uniqueTargets.length - 1] + "! Basically the world map but with more craters!");
      }
    }
  }

  // === WHEEL OF DISASTER ===
  if (h.wheelSpins && h.wheelSpins.length > 0) {
    const badSpins = h.wheelSpins.filter(s => !s.good);
    const goodSpins = h.wheelSpins.filter(s => s.good);

    if (badSpins.length > 0 && goodSpins.length === 0) {
      lines.push("You spun the wheel " + h.wheelSpins.length + " times and got nothing but disasters! " + badSpins.map(s => s.name).join("! ") + "! Worst luck in presidential history!");
    } else if (goodSpins.length > 0 && badSpins.length === 0) {
      lines.push("You spun the wheel and actually won! " + goodSpins.map(s => s.name).join(" and ") + "! You lucky bastard!");
    } else {
      lines.push("The wheel gave you " + badSpins.length + " disasters and " + goodSpins.length + " miracles! A real emotional rollercoaster!");
      if (badSpins.length > 0) {
        lines.push(badSpins[0].name + " hit you like a truck! But did you care? No!");
      }
    }
  }

  // === BLACK OPS ===
  if (h.blackOps && h.blackOps.length > 0) {
    if (h.blackOps.length === 1) {
      lines.push("One covert " + h.blackOps[0].name + " operation! Surgical! In and out! Nobody saw a thing!");
    } else {
      lines.push(h.blackOps.length + " black ops missions! " + h.blackOps.map(b => b.name).join(", ") + "! You were basically running the CIA!");
      if (h.blackOps.length >= 4) {
        lines.push("At this point it's not even covert anymore! Everyone knows it's you!");
      }
    }
  }

  // === MEAN TWEETS ===
  const mt = h.meanTweets || { wins: 0, losses: 0 };
  if (mt.wins + mt.losses > 0) {
    if (mt.wins > 0 && mt.losses === 0) {
      lines.push(mt.wins + " mean tweets sent and every single one landed! Undefeated on Twitter! The keyboard warrior supreme!");
    } else if (mt.losses > mt.wins) {
      lines.push(mt.wins + " tweet wins and " + mt.losses + " fails! Your tweet game needs work! Maybe hire a ghostwriter!");
    } else if (mt.wins > 0 && mt.losses > 0) {
      lines.push(mt.wins + " successful mean tweets! " + mt.losses + " that flopped! Nobody bats a thousand!");
    }
  }

  // === SPEED BONUSES ===
  const sp = h.speedBonuses || { blazing: 0, fast: 0, quick: 0 };
  const totalSpeed = sp.blazing + sp.fast + sp.quick;
  if (sp.blazing >= 5) {
    lines.push(sp.blazing + " blazing speed bonuses! Your fingers were a blur! Were you even reading the screen or just mashing buttons?!");
  } else if (totalSpeed >= 10) {
    lines.push(totalSpeed + " speed bonuses total! You played this game like your mortgage depended on it!");
  } else if (sp.blazing >= 2) {
    lines.push(sp.blazing + " blazing combos! Lightning fast! Somebody call a doctor, those fingers are on fire!");
  }

  // === POWERUP MULTIPLIERS ===
  if (h.powerupMultipliers && h.powerupMultipliers.length > 0) {
    const maxMult = Math.max(...h.powerupMultipliers);
    if (maxMult >= 10) {
      lines.push("You hit a ten X multiplier! Maximum power! You tapped that button like it owed you money!");
    } else if (maxMult >= 5) {
      lines.push("A " + maxMult + "X powerup multiplier! Those rapid taps paid off big time!");
    }
  }

  // === DEEP STATE ATTACKS SURVIVED ===
  if (h.attacksSurvived >= 10) {
    lines.push("The deep state threw " + h.attacksSurvived + " attacks at you! Media lies! Antifa! Big tech! You just kept tanking hits like a champion!");
  } else if (h.attacksSurvived >= 5) {
    lines.push(h.attacksSurvived + " deep state attacks survived! They tried everything and you're still standing!");
  }

  // === NEAR DEATH EXPERIENCE ===
  if (h.lowestHP !== undefined && h.lowestHP <= 15) {
    lines.push("At one point Trump was down to " + Math.round(h.lowestHP) + " percent health! Death was knocking! But you pulled through! What a comeback story!");
  }

  // === BODY COUNT ===
  if (G.deadBodies >= 20) {
    lines.push(G.deadBodies + " total casualties! That's not a presidency, that's a war crime tribunal waiting to happen!");
  } else if (G.deadBodies >= 5) {
    lines.push(G.deadBodies + " bodies! Collateral damage! The price of freedom, some would say!");
  }

  // === FEMINISM/CHRISTIANITY ===
  if (G.feminism <= 5) {
    lines.push("Feminism at " + Math.round(G.feminism) + " percent! You didn't just push back, you obliterated it! The patriarchy sends its regards!");
  } else if (G.feminism >= 60) {
    lines.push("Feminism at " + Math.round(G.feminism) + " percent though! They got stronger! You might have won but they're coming back!");
  }

  if (G.christianity >= 95) {
    lines.push("Christianity at " + Math.round(G.christianity) + "! One nation under God! The churches are overflowing!");
  }

  // === BABIES ===
  if (G.babies >= 10) {
    lines.push(G.babies + " babies born! Population boom! The future of America is secured!");
  }

  // === TRUMP HEALTH ===
  if (G.trumpHP >= 95) {
    lines.push("Trump finished at " + Math.round(G.trumpHP) + " percent health! Barely a scratch! Built like a tank wrapped in kevlar!");
  } else if (G.trumpHP <= 25) {
    lines.push("Trump limping across the finish line at " + Math.round(G.trumpHP) + " percent health! A survivor! Rocky Balboa would be impressed!");
  }

  // === ROUNDS & AGE ===
  if (G.round <= 8) {
    lines.push("And you did it all in just " + G.round + " rounds! A speed run! Any percent world record!");
  } else if (G.round >= 40) {
    lines.push(G.round + " rounds! This wasn't a presidency, it was a dynasty! An epoch!");
  } else {
    lines.push(G.round + " rounds of pure political chaos!");
  }

  if (G.trumpAge >= 95) {
    lines.push("Trump is " + G.trumpAge + " years old and still going! He'll outlive us all!");
  } else if (G.trumpAge >= 85) {
    lines.push("At " + G.trumpAge + " years old! The oldest president in history! Fueled by diet coke and pure spite!");
  }

  // === OIL FORTUNE ===
  if (G.oilCash >= 10000) {
    lines.push("And sitting on " + Math.round(G.oilCash) + " million in oil money! You're not a president anymore, you're an oil baron!");
  }

  // === HITLER ADVISOR UNLOCK ===
  if (!G.hitlerUnlocked || (G.gameHistory && G.gameHistory.actions && Object.keys(G.gameHistory.actions).length > 0)) {
    // First win ever - Hitler gets unlocked
    if (!G.hitlerUnlocked) {
      lines.push("And because of this historic victory, you've unlocked a brand new advisor! Adolf Hitler has entered the chat! Use him wisely! Or don't! We're not judging!");
    }
  }

  // === GRAND CLOSING ===
  lines.push("What a strategy! What a performance! The greatest political game ever played!");

  // Speak each line, then play win video, then ending
  speakSequence(lines, 0, () => {
    // Narration done - restore audio for the win video
    unmuteAllGameAudio();

    // Play the appropriate win video as the finale cap
    const winVid = getWinVideo();
    playFullscreenVideo(winVid, () => {
      // Win video done - proceed to stats/ending
      if (G.purity > 96 && !G.statsVideoShown) {
        G.statsVideoShown = true;
        showStatsAreWrongVideo();
      } else {
        showEndingScreen(determineEnding());
      }
    });
  });
}

function speakSequence(lines, index, onComplete) {
  if (index >= lines.length) {
    if (onComplete) onComplete();
    return;
  }

  if (!('speechSynthesis' in window)) {
    // No speech support - skip to end
    if (onComplete) onComplete();
    return;
  }

  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(lines[index]);
  utterance.rate = 1.05;
  utterance.pitch = 0.85;
  utterance.volume = 0.9;

  // Try to get a good male voice
  const voices = speechSynthesis.getVoices();
  const preferred = voices.find(v => v.name.includes('Male') && v.lang.includes('en')) ||
                    voices.find(v => v.name.includes('Google') && v.lang.includes('en-US')) ||
                    voices.find(v => v.lang.includes('en-US')) ||
                    voices.find(v => v.lang.includes('en'));
  if (preferred) utterance.voice = preferred;

  // Fallback if speech gets stuck
  const timeout = setTimeout(() => {
    speakSequence(lines, index + 1, onComplete);
  }, 8000);

  utterance.onend = () => {
    clearTimeout(timeout);
    setTimeout(() => speakSequence(lines, index + 1, onComplete), 400);
  };

  speechSynthesis.speak(utterance);
}

// Add grey death overlay when Trump HP reaches 0
function addDeathOverlay() {
  // KILL ALL SOUNDS — game is over, total silence
  pauseGameSounds();
  if (typeof stopGeiger === 'function') stopGeiger();
  // Force-stop every audio/video element on the page
  document.querySelectorAll('audio, video').forEach(el => {
    el.pause();
    el.currentTime = 0;
    el.volume = 0;
  });
  // Clear any running intervals/timers that might make noise
  if (powerupInterval) { clearInterval(powerupInterval); powerupInterval = null; }
  if (advisorTimer) { clearInterval(advisorTimer); advisorTimer = null; }
  if (rumbleInterval) { clearInterval(rumbleInterval); rumbleInterval = null; }

  // Remove existing death overlay if any
  const existing = document.getElementById('death-overlay');
  if (existing) existing.remove();

  const overlay = document.createElement('div');
  overlay.id = 'death-overlay';
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100vw';
  overlay.style.height = '100vh';
  overlay.style.background = 'rgba(100, 100, 100, 0)';
  overlay.style.zIndex = '9998';
  overlay.style.pointerEvents = 'auto';
  overlay.style.transition = 'background 2s ease-in';
  overlay.style.backdropFilter = 'grayscale(0%)';
  overlay.style.webkitBackdropFilter = 'grayscale(0%)';
  overlay.style.display = 'flex';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';

  document.body.appendChild(overlay);

  // Animate to grey
  setTimeout(() => {
    overlay.style.background = 'rgba(100, 100, 100, 0.6)';
    overlay.style.backdropFilter = 'grayscale(100%)';
    overlay.style.webkitBackdropFilter = 'grayscale(100%)';
  }, 100);

  // Game over video
  const videoContainer = document.createElement('div');
  videoContainer.style.position = 'relative';
  videoContainer.style.zIndex = '9999';
  videoContainer.style.maxWidth = '80%';
  videoContainer.style.maxHeight = '80%';

  const video = document.createElement('video');
  video.src = 'https://www.shortfactory.shop/trump/gameover.webm'; // Game over video
  video.style.width = '100%';
  video.style.height = 'auto';
  video.style.border = '4px solid #000';
  video.style.boxShadow = '0 0 30px rgba(0, 0, 0, 0.8)';
  video.muted = false;
  video.volume = 0.7;
  video.playsInline = true;

  // Auto-play with promise catch
  videoContainer.appendChild(video);
  overlay.appendChild(videoContainer);
  var playP = video.play();
  if(playP && playP.catch) playP.catch(function(){
    video.muted = true;
    video.play().catch(function(){});
  });

  // DEMO MODE banner — appears after video ends
  video.onended = () => {
    console.log('Game over video ended, showing demo screen...');
    videoContainer.style.transition = 'opacity 1s';
    videoContainer.style.opacity = '0';
    setTimeout(() => {
      videoContainer.remove();
      // Build arcade demo screen
      var demo = document.createElement('div');
      demo.style.cssText = 'text-align:center;animation:demoFadeIn .8s ease;';
      demo.innerHTML = '<div style="font-family:\'Press Start 2P\',monospace;font-size:11px;color:#ff4444;letter-spacing:4px;text-shadow:0 0 15px rgba(255,0,0,0.6);margin-bottom:18px;animation:demoBlink 1.2s ease-in-out infinite;">&#9632; DEMO MODE &#9632;</div>'
        + '<div style="font-family:\'Press Start 2P\',monospace;font-size:18px;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,0.5);margin-bottom:12px;">GAME OVER</div>'
        + '<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#aaa;letter-spacing:2px;margin-bottom:30px;">v2.9 — CORPS vs PEOPLE</div>'
        + '<div id="coin-prompt" style="font-family:\'Press Start 2P\',monospace;font-size:10px;color:#0f0;letter-spacing:3px;margin-bottom:35px;animation:coinPulse 1.5s ease-in-out infinite;cursor:pointer;" onclick="safeRemoveLocal(\'trumpGameSave\');location.reload();">&#9654; INSERT COIN TO PLAY &#9664;</div>'
        + '<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">'
        + '<button onclick="safeRemoveLocal(\'trumpGameSave\');location.reload();" style="font-family:\'Press Start 2P\',monospace;font-size:9px;background:linear-gradient(135deg,#ff4444,#cc0000);color:#fff;border:2px solid rgba(255,255,255,0.3);border-radius:6px;padding:14px 24px;cursor:pointer;letter-spacing:1px;box-shadow:0 0 15px rgba(255,0,0,0.4);">CONTINUE?</button>'
        + '<button onclick="window.location.href=\'/\'" style="font-family:\'Press Start 2P\',monospace;font-size:9px;background:linear-gradient(135deg,#daa520,#b8860b);color:#000;border:2px solid rgba(255,255,255,0.3);border-radius:6px;padding:14px 24px;cursor:pointer;letter-spacing:1px;box-shadow:0 0 15px rgba(218,165,32,0.4);">HOME</button>'
        + '</div>'
        + '<div style="font-family:\'Press Start 2P\',monospace;font-size:6px;color:#555;margin-top:25px;letter-spacing:2px;">SHORTFACTORY.SHOP &#169; 2026</div>';
      overlay.appendChild(demo);
    }, 1000);
  };

  // Fallback if video fails to load — show demo screen directly
  video.onerror = () => {
    console.error('Game over video failed to load');
    videoContainer.remove();
    var demo = document.createElement('div');
    demo.style.cssText = 'text-align:center;';
    demo.innerHTML = '<div style="font-family:\'Press Start 2P\',monospace;font-size:11px;color:#ff4444;letter-spacing:4px;text-shadow:0 0 15px rgba(255,0,0,0.6);margin-bottom:18px;animation:demoBlink 1.2s ease-in-out infinite;">&#9632; DEMO MODE &#9632;</div>'
      + '<div style="font-family:\'Press Start 2P\',monospace;font-size:18px;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,0.5);margin-bottom:12px;">GAME OVER</div>'
      + '<div id="coin-prompt" style="font-family:\'Press Start 2P\',monospace;font-size:10px;color:#0f0;letter-spacing:3px;margin-bottom:35px;animation:coinPulse 1.5s ease-in-out infinite;cursor:pointer;" onclick="safeRemoveLocal(\'trumpGameSave\');location.reload();">&#9654; INSERT COIN TO PLAY &#9664;</div>'
      + '<button onclick="safeRemoveLocal(\'trumpGameSave\');location.reload();" style="font-family:\'Press Start 2P\',monospace;font-size:9px;background:linear-gradient(135deg,#ff4444,#cc0000);color:#fff;border:2px solid rgba(255,255,255,0.3);border-radius:6px;padding:14px 24px;cursor:pointer;letter-spacing:1px;box-shadow:0 0 15px rgba(255,0,0,0.4);">CONTINUE?</button>';
    overlay.appendChild(demo);
  };

}

// Inject demo mode keyframe animations
(function(){
  var s = document.createElement('style');
  s.textContent = '@keyframes demoBlink{0%,100%{opacity:1;}50%{opacity:0.3;}}@keyframes coinPulse{0%,100%{transform:scale(1);text-shadow:0 0 10px rgba(0,255,0,0.4);}50%{transform:scale(1.05);text-shadow:0 0 25px rgba(0,255,0,0.8);}}@keyframes demoFadeIn{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}';
  document.head.appendChild(s);
})();

function showTallyScreen() {
  pauseGameSounds();

  const overlay = document.getElementById('tally-overlay');
  const iframe = document.getElementById('tally-iframe');

  const params = new URLSearchParams({
    round: G.round,
    purity: Math.round(G.purity),
    debt: G.debt.toFixed(1),
    trumpHP: G.trumpHP,
    deepStateHP: G.deepStateHP,
    oilCash: G.oilCash
  });

  iframe.src = 'pages/tallyscreen.html?' + params.toString();
  overlay.classList.add('show');

  window.addEventListener('message', handleTallyMessage);
}

function handleTallyMessage(e) {
  if (e.data === 'tally-continue') {
    window.removeEventListener('message', handleTallyMessage);
    closeTallyScreen();
  }
}

// Listen for ending screen messages
window.addEventListener('message', function(e) {
  if (e.data === 'ending-restart') {
    closeEndingScreen();
    // Reset and restart the game
    setTimeout(() => {
      safeRemoveLocal('trumpGameSave');
      location.reload();
    }, 600);
  }
});

function closeTallyScreen() {
  const overlay = document.getElementById('tally-overlay');
  overlay.classList.add('fade-out');

  setTimeout(() => {
    overlay.classList.remove('show', 'fade-out');
    document.getElementById('tally-iframe').src = '';
    startTerm2();
  }, 500);
}

function startTerm2() {
  const loopMult = 1 + (G.ngPlusLoop * 0.3);
  G.term = 2;
  G.difficultyMult = 2 * loopMult;
  G.cardFreqMult = Math.max(0.1, 0.5 / loopMult);
  G.baseMoves = Math.max(2, Math.floor(3 / loopMult));
  G.moves = G.baseMoves;

  // Reset emergency tier flags for fresh term
  G.diceTurns = 0;
  G.wheelUsed = false;
  G.blackopsUsed = false;
  G.nukeUsed = false;
  G.emergencyTier = 0;

  resumeGameSounds();

  showNews('TERM 2 BEGINS! DIFFICULTY DOUBLED!');
  updateDisplay();
}

function showStatsAreWrongVideo() {
  // Pause game sounds
  pauseGameSounds();

  // Create fullscreen overlay
  const overlay = document.createElement('div');
  overlay.id = 'stats-wrong-overlay';
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100vw';
  overlay.style.height = '100vh';
  overlay.style.background = 'rgba(0, 0, 0, 0.95)';
  overlay.style.zIndex = '9999';
  overlay.style.display = 'flex';
  overlay.style.alignItems = 'center';
  overlay.style.justifyContent = 'center';

  // Create video element
  const video = document.createElement('video');

  // Random video selection: statsarewrong.webm or statsarewrong(a-z).webm
  // Picks a random letter (a-z) or no letter (base version)
  const letters = ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'];
  const randomLetter = letters[Math.floor(Math.random() * letters.length)];
  const videoUrl = `https://www.shortfactory.shop/trump/statsarewrong${randomLetter}.webm`;

  video.src = videoUrl;
  video.style.maxWidth = '90%';
  video.style.maxHeight = '90%';
  video.style.width = 'auto';
  video.style.height = 'auto';
  video.style.border = '4px solid #ff0000';
  video.style.boxShadow = '0 0 40px rgba(255, 0, 0, 0.8)';
  video.muted = false;
  video.volume = 0.8;
  video.playsInline = true;

  // If video fails to load (404), fall back to base version
  video.onerror = () => {
    console.log(`Failed to load ${videoUrl}, falling back to base version`);
    video.src = 'https://www.shortfactory.shop/trump/statsarewrong.webm';
  };

  // YMCA plays alongside the video - plays to the END, never cut short
  const ymca = new Audio('asset/ymca.mp3');
  ymca.volume = 0.6;

  // After video ends, show ending screen but YMCA keeps playing
  video.onended = () => {
    overlay.remove();
    showEndingScreen(determineEnding());
  };

  // Click to skip video but YMCA keeps playing
  overlay.onclick = () => {
    video.pause();
    overlay.remove();
    showEndingScreen(determineEnding());
  };

  overlay.appendChild(video);
  document.body.appendChild(overlay);

  // Play video WITH sound - no muted fallback
  video.play().catch(function(){});
  ymca.play().catch(function(){});
}

function showEndingScreen(type) {
  pauseGameSounds();

  const overlay = document.getElementById('ending-overlay');
  const iframe = document.getElementById('ending-iframe');

  const power = Math.min(100, Math.max(0, G.purity + (100 - G.deepStateHP) / 2));
  const spirit = Math.min(100, Math.max(0, G.trumpHP + G.christianity - G.feminism));
  const intelligence = Math.min(100, Math.max(0, 50 + G.totalMoves - G.debt));

  const completedEndings = JSON.parse(safeGetLocal('completedEndings', '[]'));
  if (!completedEndings.includes(type)) {
    completedEndings.push(type);
    safeSetLocal('completedEndings', JSON.stringify(completedEndings));
  }

  // Trump advisor unlock (existing)
  if (type !== 'tyrant' && !G.trumpUnlocked) {
    G.trumpUnlocked = true;
    safeSetLocal('trumpUnlocked', 'true');
  }

  // Hitler advisor unlock - first non-tyrant win
  let hitlerJustUnlocked = false;
  if (type !== 'tyrant' && !G.hitlerUnlocked) {
    hitlerJustUnlocked = true;
    G.hitlerUnlocked = true;
    safeSetLocal('hitlerUnlocked', 'true');
    // Grant GAME_MODDER in cortex_unlocks (ties into Cortex gatekeeping)
    try {
      const unlocks = JSON.parse(safeGetLocal('cortex_unlocks', '{}'));
      unlocks.GAME_MODDER = true;
      safeSetLocal('cortex_unlocks', JSON.stringify(unlocks));
    } catch (e) { /* ignore */ }
  }

  const params = new URLSearchParams({
    type: type,
    power: Math.round(power),
    spirit: Math.round(spirit),
    intelligence: Math.round(intelligence),
    round: G.round,
    purity: Math.round(G.purity),
    aggressive: G.usedAggressive,
    hitlerJustUnlocked: hitlerJustUnlocked,
    completedEndings: completedEndings.join(',')
  });

  iframe.src = 'pages/trump-endings.html?' + params.toString();
  overlay.classList.add('show');
}

function closeEndingScreen() {
  const overlay = document.getElementById('ending-overlay');
  overlay.classList.add('fade-out');

  setTimeout(() => {
    overlay.classList.remove('show', 'fade-out');
    document.getElementById('ending-iframe').src = '';
  }, 500);
}

// ==================== ALERT ALTERNATION ====================
// Alternates between emergency tier icon and litigation icon

function startAlertAlternation(tierEmoji, tierText) {
  // Prevent duplicate timers for same tier
  const alertIcon = document.getElementById('blackops-alert-icon');
  if (!alertIcon) return;
  if (alertIcon.dataset.tierEmoji === tierEmoji && alertAlternateTimer) {
    return; // Already running with same tier
  }

  // Clear any existing timer
  stopAlertAlternation();

  const alertText = document.getElementById('blackops-alert-text');

  // Store the tier values for alternation
  alertIcon.dataset.tierEmoji = tierEmoji;
  alertIcon.dataset.tierText = tierText;

  currentAlertPhase = 'emergency';
  let alternateCount = 0;

  // Start rapid - gets slower over time to be catchable
  function getInterval() {
    // First 10 alternations are rapid (150-250ms), then slows to 400-600ms
    if (alternateCount < 10) {
      return 150 + Math.random() * 100;
    } else if (alternateCount < 20) {
      return 250 + Math.random() * 150;
    } else {
      return 400 + Math.random() * 200;
    }
  }

  function alternate() {
    alternateCount++;

    if (currentAlertPhase === 'emergency') {
      // Switch to litigation
      currentAlertPhase = 'litigation';
      alertIcon.textContent = (typeof LITIGATION_EMOJI !== 'undefined') ? LITIGATION_EMOJI : '⚖️';
      alertIcon.classList.add('litigation-phase');
      alertText.textContent = 'LITIGATION AVAILABLE';
    } else {
      // Switch back to emergency
      currentAlertPhase = 'emergency';
      alertIcon.textContent = alertIcon.dataset.tierEmoji;
      alertIcon.classList.remove('litigation-phase');
      alertText.textContent = alertIcon.dataset.tierText;
    }

    // Schedule next alternation with variable timing
    alertAlternateTimer = setTimeout(alternate, getInterval());
  }

  // Start alternating after initial display
  alertAlternateTimer = setTimeout(alternate, getInterval());
}

function stopAlertAlternation() {
  if (alertAlternateTimer) {
    clearTimeout(alertAlternateTimer);
    alertAlternateTimer = null;
  }
  currentAlertPhase = 'emergency';

  const alertIcon = document.getElementById('blackops-alert-icon');
  if (alertIcon) {
    alertIcon.classList.remove('litigation-phase');
  }
}

// Handle alert icon click - route to correct action based on phase
function handleAlertClick() {
  if (currentAlertPhase === 'litigation') {
    // Open litigation panel
    stopAlertAlternation();
    document.getElementById('blackops-alert-icon').classList.remove('show');
    document.getElementById('blackops-alert-text').classList.remove('show');
    toggleLitigation();
    showNews('LITIGATION MODE!');
    vibrate(VIBES.success);
  } else {
    // Activate the current emergency tier
    activateEmergencyTier();
  }
}

// ==================== GAME HINTS ====================
// Show helpful tips until player gets the hang of it

const GAME_HINTS = [
  { id: 'start', text: '★ START ★', sub: 'Build up cash to unlock more actions!', condition: () => G.round === 1 && G.oilCash < 500 && !hintsShown.start },
  { id: 'unlock', text: '★ UNLOCK NEW ACTIONS ★', sub: 'Use oil money to unlock locked buttons!', condition: () => G.oilCash >= 1000 && !hintsShown.unlock },
  { id: 'moves', text: '★ OUT OF MOVES? ★', sub: 'Tap MOVES pill to roll dice for more!', condition: () => G.moves === 1 && !hintsShown.moves },
  { id: 'purity', text: '★ RAISE PURITY TO WIN ★', sub: 'Get purity to 96% to complete the game!', condition: () => G.round >= 3 && G.purity < 20 && !hintsShown.purity },
  { id: 'hp', text: '★ HEALTH LOW! ★', sub: 'Use LOAN or wait for powerups to heal!', condition: () => G.trumpHP <= 30 && !hintsShown.hp },
  { id: 'deepstate', text: '★ DEEP STATE RISING ★', sub: 'Use AUDIT to fight back the swamp!', condition: () => G.deepStateHP >= 60 && !hintsShown.deepstate },
  { id: 'litigation', text: '★ TRY LITIGATION ★', sub: 'Long hold DEBT pill to enter court battle!', condition: () => G.round >= 5 && !hintsShown.litigation },
  { id: 'blackops', text: '★ BLACK OPS AVAILABLE ★', sub: 'Clear debt + surplus to unlock black ops at 50% HP!', condition: () => G.trumpHP <= 55 && G.trumpHP > 45 && G.debt <= 0 && !hintsShown.blackops },
  { id: 'litcombo', text: '★ ADVISOR TIP: LITIGATION COMBO ★', sub: 'Alternate SUE and EXECUTIVE ORDER for fast health bonus!', condition: () => G.ngPlusLoop >= 1 && G.trumpHP <= 50 && !hintsShown.litcombo },
  { id: 'litrecovery', text: '★ ADVISOR TIP: USE LITIGATION ★', sub: 'Hold DEBT pill to enter court. Siphon HP from opponents!', condition: () => G.ngPlusLoop >= 1 && G.trumpHP <= 40 && G.round >= 3 && !hintsShown.litrecovery },
  { id: 'ngplushard', text: '★ NG+ IS HARDER ★', sub: 'Litigation is your lifeline. Master SUE+EXEC combo to survive!', condition: () => G.ngPlusLoop >= 2 && G.round === 1 && !hintsShown.ngplushard },
  { id: 'impeach', text: '★ IMPEACHMENT RISK ★', sub: 'Keep purity above 20% and deep state below 50 to avoid impeachment!', condition: () => G.deepStateHP >= 50 && G.purity < 20 && !hintsShown.impeach }
];

let hintsShown = {};
let hintDismissed = true; // Block hints until after advisor selection
let currentHint = null;

function checkForHint() {
  // Don't show hints if one is already showing or recently dismissed
  if (hintDismissed || document.getElementById('game-hint').classList.contains('show')) return;

  // Don't show during overlays
  if (document.getElementById('litigation-overlay')?.classList.contains('show')) return;
  if (document.getElementById('advisor-overlay')?.classList.contains('show')) return;

  // Find first matching hint
  for (const hint of GAME_HINTS) {
    if (hint.condition() && !hintsShown[hint.id]) {
      showHint(hint);
      return;
    }
  }
}

let hintAutoHideTimer = null;

function showHint(hint) {
  currentHint = hint;
  document.getElementById('hint-text').textContent = hint.text;
  document.getElementById('hint-sub').textContent = hint.sub;
  document.getElementById('game-hint').classList.add('show');

  // Speak the hint using text-to-speech!
  speakHint(hint.text.replace(/★/g, '') + '. ' + hint.sub);

  // Auto-dismiss after 2 seconds - very sensitive
  if (hintAutoHideTimer) clearTimeout(hintAutoHideTimer);
  hintAutoHideTimer = setTimeout(() => {
    dismissHint();
  }, 2000);
}

// SNES-style text-to-speech for hints
function speakHint(text) {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech and wait for it to stop
    if (speechSynthesis.speaking || speechSynthesis.pending) {
      speechSynthesis.cancel();
      // Brief delay to ensure cancellation completes
      setTimeout(() => speakHint(text), 100);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 0.8; // Lower pitch for dramatic effect
    utterance.volume = 0.8;

    // Try to get a good voice
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(v =>
      v.name.includes('Google') || v.name.includes('Daniel') || v.name.includes('Male')
    );
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    speechSynthesis.speak(utterance);
  }
}

function dismissHint() {
  if (currentHint) {
    hintsShown[currentHint.id] = true;
  }
  document.getElementById('game-hint').classList.remove('show');
  hintDismissed = true;

  // Stop any speech
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel();
  }

  // Allow new hints after 30 seconds
  setTimeout(() => {
    hintDismissed = false;
  }, 30000);
}

// ==================== EMERGENCY DROP ====================
// ⚠️ DO NOT DELETE - SLOT MACHINE SINGLE ICON (SATIRICAL GAMBLING CRITIQUE) ⚠️

let emergDropTimer = null;
let slotCycleTimeout = null;
let slotMachineActive = false;

// Slot machine - single icon cycling through options (fast -> slow -> fast)
function startSlotMachine() {
  // Don't start if stats/stocks view is open — roulette is MAP ONLY
  if (statsOpen) return;
  const slotIcon = document.getElementById('slot-machine-icon');
  const icons = ['☢️', '⚖️', '🎯', '☸️'];
  const actions = ['nuke', 'litigation', 'blackops', 'wheel'];

  let currentIndex = 0;
  let cycleSpeed = 60; // Start fast
  let speedDirection = 1; // 1 = slowing down, -1 = speeding up
  let minSpeed = 60;
  let maxSpeed = 350;

  slotIcon.classList.add('active');
  slotIcon.dataset.currentAction = actions[currentIndex];
  slotMachineActive = true;

  // Play roulette sound
  const rouletteSound = new Audio('https://www.shortfactory.shop/trump/roulette.mp3');
  rouletteSound.volume = 0.6;
  rouletteSound.loop = true;
  rouletteSound.play().catch(e => console.log('Audio play failed:', e));

  // Store audio reference for stopping later (always overwrite - old one may be stale)
  if (window.slotMachineAudio) { try { window.slotMachineAudio.pause(); } catch(e){} }
  window.slotMachineAudio = rouletteSound;

  function cycleNext() {
    if (!slotMachineActive) return;

    // Change the icon
    slotIcon.textContent = icons[currentIndex];
    slotIcon.dataset.currentAction = actions[currentIndex];

    // Move to next icon
    currentIndex = (currentIndex + 1) % icons.length;

    // Adjust speed (slot machine effect)
    if (speedDirection === 1) {
      // Slowing down
      cycleSpeed += 35;
      if (cycleSpeed >= maxSpeed) {
        speedDirection = -1; // Start speeding up
      }
    } else {
      // Speeding up
      cycleSpeed -= 35;
      if (cycleSpeed <= minSpeed) {
        speedDirection = 1; // Start slowing down again
      }
    }

    // Continue cycling
    slotCycleTimeout = setTimeout(cycleNext, cycleSpeed);
  }

  // Start the cycle
  cycleNext();
}

function stopSlotMachine() {
  if (slotCycleTimeout) {
    clearTimeout(slotCycleTimeout);
    slotCycleTimeout = null;
  }

  slotMachineActive = false;
  const slotIcon = document.getElementById('slot-machine-icon');
  slotIcon.classList.remove('active');

  // Stop roulette sound
  if (window.slotMachineAudio) {
    try {
      window.slotMachineAudio.pause();
      window.slotMachineAudio.currentTime = 0;
      window.slotMachineAudio = null;
    } catch (e) {
      console.log('Audio stop failed:', e);
    }
  }
}

function slotMachineClick() {
  const slotIcon = document.getElementById('slot-machine-icon');
  const action = slotIcon.dataset.currentAction;

  stopSlotMachine();

  // Trigger the action
  if (action === 'nuke') {
    activateNuke();
  } else if (action === 'litigation') {
    toggleLitigation();
  } else if (action === 'blackops') {
    activateBlackOps();
  } else if (action === 'wheel') {
    activateWheel();
  }

  vibrate(VIBES.success);
}

function showEmergencyDrop(reason = 'random') {
  // Don't show if stats/stocks view is open — MAP ONLY
  if (statsOpen) return;
  // Start slot machine instead of dropdown
  startSlotMachine();

  // Show notification based on reason
  if (reason === 'trump-card') {
    showNews('🎰 SPIN THE WHEEL OF FATE! 🎰');
  } else if (reason === 'random') {
    showNews('🎲 TRY YOUR LUCK! 🎲');
  }

  vibrate(VIBES.success);

  // Auto-hide after 15 seconds
  if (emergDropTimer) clearTimeout(emergDropTimer);
  emergDropTimer = setTimeout(() => {
    stopSlotMachine();
  }, 15000);
}

// ⚠️ END PROTECTED SECTION ⚠️

function emergLitigation() {
  // Stop slot machine cycle
  stopSlotMachine();

  // Hide the dropdown
  document.getElementById('emergency-drop').classList.remove('show');
  if (emergDropTimer) clearTimeout(emergDropTimer);

  // Open litigation
  toggleLitigation();
  vibrate(VIBES.success);
}

// Dismiss hint on any key press
document.addEventListener('keydown', () => {
  if (document.getElementById('game-hint').classList.contains('show')) {
    dismissHint();
  }
});

// Check for hints periodically
setInterval(checkForHint, 5000);

// Load voices when available (for speech synthesis)
if ('speechSynthesis' in window) {
  speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
}

// ==================== DEBUG ====================
window.G = G;
window.testCard = showTrumpCard;
window.testAttack = triggerDeepStateAttack;
window.testPowerup = activateRandomPowerup;
window.testNotification = (type) => showNotification({
  type: type || 'email',
  title: 'TEST ALERT',
  message: 'This is a test notification',
  sender: 'Test Sender',
  hpChange: -10,
  dsChange: 5,
  video: ASSETS.notificationVideos[0]
});

// ==================== CLAUDE LOGO VOICE MESSAGE ====================

function speakClaudeMessage() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();

    const messages = [
      "Hey! Claude here. Hope you're enjoying the game! Remember, I just write code - any controversial content is purely satirical game mechanics, not my views!",
      "Claude AI reporting for duty! I helped build this wild game. The code's real, the politics are parody. Have fun!",
      "Greetings from Claude! I'm an AI assistant that helped code this game. It's all satire, folks! Enjoy the chaos!",
      "Claude speaking! Just your friendly neighborhood AI. I coded the features, the humans made it crazy. Game on!",
      "Hi! This is Claude. I assisted with the technical implementation. The game's content is pure satire. Play responsibly!"
    ];

    const message = messages[Math.floor(Math.random() * messages.length)];
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;

    window.speechSynthesis.speak(utterance);
    console.log('Claude says:', message);
  } else {
    console.log('Speech synthesis not supported');
    alert('Claude says: Thanks for playing! 🤖');
  }
}
