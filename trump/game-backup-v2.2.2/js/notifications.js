/* ==================== NOTIFICATION SYSTEM ====================
 * Handles all game notifications/alerts
 *
 * Your friend can edit this file to:
 * - Change how notifications appear
 * - Add new notification styles
 * - Modify the DND (Do Not Disturb) behavior
 *
 * Templates are in /templates/ folder
 */

// ==================== TEMPLATE LOADING ====================

const loadedTemplates = {};

// Persistent mute state for all DeepState popups
let deepstateMuted = false;

// Global notification mute - affects all notification types
let notificationsMuted = false;

async function loadTemplate(type) {
  if (loadedTemplates[type]) return loadedTemplates[type];

  try {
    const response = await fetch(`templates/${type}.html`);
    if (!response.ok) {
      console.warn(`Template fetch failed: ${type} - ${response.status}`);
      return null;
    }
    const html = await response.text();

    // Parse the HTML and extract the template
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');

    // Get the style element
    const style = doc.querySelector('style');
    if (style && !document.querySelector(`style[data-template="${type}"]`)) {
      style.setAttribute('data-template', type);
      document.head.appendChild(style);
    }

    // Get the template content
    const template = doc.querySelector('template');
    if (template) {
      loadedTemplates[type] = template.innerHTML;
      return loadedTemplates[type];
    }
  } catch (e) {
    console.warn(`Failed to load template: ${type}`, e);
  }

  return null;
}

// ==================== NOTIFICATION DISPLAY ====================

async function showNotification(data) {
  // Check DND mode
  if (NOTIFICATION_CONFIG.dndMode) {
    showStatFlash(data);
    return;
  }

  const type = data.type || NOTIFICATION_CONFIG.defaultStyle;
  const templateHtml = await loadTemplate(type);

  if (!templateHtml) {
    // Fallback to legacy popup
    showLegacyPopup(data);
    return;
  }

  // Replace placeholders in template
  let html = templateHtml;

  // Extra safety check (shouldn't happen due to early return above)
  if (!html || typeof html !== 'string') {
    console.error('Invalid template HTML, falling back to legacy');
    showLegacyPopup(data);
    return;
  }

  html = html.replace(/{{title}}/g, data.title || 'ALERT');
  html = html.replace(/{{message}}/g, data.message || '');
  html = html.replace(/{{sender}}/g, data.sender || 'Unknown');
  html = html.replace(/{{handle}}/g, data.handle || '@deepstate');
  html = html.replace(/{{avatar}}/g, data.avatar || '🏛️');
  html = html.replace(/{{video}}/g, data.video || '');
  html = html.replace(/{{hpChange}}/g, data.hpChange || 0);
  html = html.replace(/{{dsChange}}/g, data.dsChange || 0);
  html = html.replace(/{{code}}/g, Math.floor(Math.random() * 9999).toString().padStart(4, '0'));
  html = html.replace(/{{timestamp}}/g, new Date().toLocaleTimeString());
  html = html.replace(/{{rotation}}/g, (Math.random() * 6 - 3).toFixed(1));
  html = html.replace(/{{doodle}}/g, ['⚠️', '💀', '🐍', '👁️'][Math.floor(Math.random() * 4)]);

  // Create and add to DOM
  const container = document.createElement('div');
  container.innerHTML = html;
  const overlay = container.firstElementChild;

  document.getElementById('phone').appendChild(overlay);

  // Trigger show animation
  requestAnimationFrame(() => {
    overlay.classList.add('show');
  });

  // Play video if present with sound
  const video = overlay.querySelector('video');
  if (video) {
    video.loop = true;
    video.muted = notificationsMuted;
    video.src = ASSETS.notificationVideos[Math.floor(Math.random() * ASSETS.notificationVideos.length)];
    video.play().catch(() => {
      video.muted = true;
      video.play().catch(() => {});
    });
  }

  // Update mute button state if present
  const muteBtn = overlay.querySelector('.postit-mute, .tweet-mute, .email-mute');
  if (muteBtn && notificationsMuted) {
    muteBtn.textContent = '🔇';
    muteBtn.classList.add('muted');

    // Shorten message when muted
    const msg = overlay.querySelector('.postit-message, .tweet-text, .email-message');
    if (msg) msg.classList.add('muted-short');

    // Auto close quickly when muted
    setTimeout(() => {
      const postit = overlay.querySelector('.postit-notification');
      if (postit) {
        tearPostit(postit);
      } else {
        closeNotification(overlay.querySelector('button'));
      }
    }, 1500);
  }
}

// ==================== CLOSE NOTIFICATION ====================

function closeNotification(element) {
  const overlay = element.closest('.notification-overlay');
  if (!overlay) return;

  overlay.classList.remove('show');

  // Stop any videos
  const video = overlay.querySelector('video');
  if (video) video.pause();

  // Remove after animation
  setTimeout(() => {
    if (overlay.parentNode) {
      overlay.parentNode.removeChild(overlay);
    }
  }, 300);
}

// ==================== DND MODE - STAT FLASH ====================

function showStatFlash(data) {
  const { hpChange, dsChange } = data;

  // Flash HP if changed
  if (hpChange && hpChange !== 0) {
    const hpElement = document.getElementById('trump-hp-fill');
    const hpPill = document.querySelector('.pill-debt');

    if (hpElement) {
      hpElement.classList.add('stat-flash', hpChange < 0 ? 'damage' : '');
      setTimeout(() => {
        hpElement.classList.remove('stat-flash', 'damage');
      }, NOTIFICATION_CONFIG.flashDuration * NOTIFICATION_CONFIG.flashCount);
    }
  }

  // Flash DeepState if changed
  if (dsChange && dsChange !== 0) {
    const dsElement = document.getElementById('ds-fill');

    if (dsElement) {
      dsElement.classList.add('stat-flash');
      setTimeout(() => {
        dsElement.classList.remove('stat-flash');
      }, NOTIFICATION_CONFIG.flashDuration * NOTIFICATION_CONFIG.flashCount);
    }
  }

  // Show brief news ticker message
  showNews(`${data.title}: HP ${hpChange}, DS +${dsChange}`);
}

// ==================== TOGGLE DND MODE ====================

function toggleDND() {
  NOTIFICATION_CONFIG.dndMode = !NOTIFICATION_CONFIG.dndMode;

  const dndBtn = document.getElementById('dnd-btn');
  if (dndBtn) {
    dndBtn.classList.toggle('active', NOTIFICATION_CONFIG.dndMode);
    dndBtn.textContent = NOTIFICATION_CONFIG.dndMode ? '🔕' : '🔔';
  }

  showNews(NOTIFICATION_CONFIG.dndMode ? '🔕 DO NOT DISTURB ON' : '🔔 NOTIFICATIONS ON');

  return NOTIFICATION_CONFIG.dndMode;
}

// ==================== LEGACY POPUP (FALLBACK) ====================

function showLegacyPopup(data) {
  document.getElementById('ds-header').textContent = data.title;
  document.getElementById('ds-message').textContent = data.message;
  document.getElementById('ds-dmg-hp').textContent = data.hpChange;
  document.getElementById('ds-dmg-ds').textContent = '+' + data.dsChange;

  // Play random attack video
  const video = document.getElementById('ds-video');
  const muteBtn = document.getElementById('ds-mute-btn');
  const popup = document.getElementById('ds-popup');
  const randomVideo = ASSETS.notificationVideos[Math.floor(Math.random() * ASSETS.notificationVideos.length)];

  video.src = randomVideo;
  video.loop = false;

  // Use persistent mute state
  video.muted = deepstateMuted;
  muteBtn.textContent = deepstateMuted ? '🔇' : '🔊';
  muteBtn.classList.toggle('muted', deepstateMuted);

  // Auto-close when video ends (if unmuted)
  video.onended = () => {
    closeDeepstatePopup();
  };

  popup.classList.add('show');
  flashScreen('red');
  shakeScreen();
  vibrate(VIBES.attack);

  video.play().catch(() => {
    // Fallback to muted if autoplay with sound blocked
    deepstateMuted = true;
    video.muted = true;
    muteBtn.textContent = '🔇';
    muteBtn.classList.add('muted');
    video.play().catch(() => {});
  });

  // If muted, show briefly then fade out
  if (deepstateMuted) {
    setTimeout(() => {
      popup.classList.add('fade-out');
      setTimeout(() => {
        closeDeepstatePopup();
        popup.classList.remove('fade-out');
      }, 500);
    }, 1500);
  }
}

function closeDeepstatePopup() {
  const popup = document.getElementById('ds-popup');
  const video = document.getElementById('ds-video');

  // Stop video
  if (video) {
    video.pause();
    video.src = '';
  }

  popup.classList.remove('show');
}

function toggleDeepstateMute() {
  const video = document.getElementById('ds-video');
  const btn = document.getElementById('ds-mute-btn');
  const popup = document.getElementById('ds-popup');

  if (video) {
    deepstateMuted = !deepstateMuted;
    video.muted = deepstateMuted;
    btn.textContent = deepstateMuted ? '🔇' : '🔊';
    btn.classList.toggle('muted', deepstateMuted);

    // If muted, play "shut up" sound and fade out quickly
    if (deepstateMuted) {
      const muteSound = document.getElementById('mute-sound');
      if (muteSound) {
        muteSound.currentTime = 0;
        muteSound.play().catch(() => {});
      }

      setTimeout(() => {
        popup.classList.add('fade-out');
        setTimeout(() => {
          closeDeepstatePopup();
          popup.classList.remove('fade-out');
        }, 500);
      }, 1000);
    }
  }
}

// ==================== DEEPSTATE ATTACK ====================

function triggerDeepStateAttack() {
  // Don't attack during other overlays
  if (tweetGameActive) return;

  // Don't trigger if slot machine is active
  const slotMachine = document.getElementById('slot-machine-icon');
  if (slotMachine && slotMachine.classList.contains('active')) {
    console.log('Deep state attack delayed - slot machine active');
    setTimeout(triggerDeepStateAttack, 3000);
    return;
  }

  if (document.getElementById('tally-overlay')?.classList.contains('show')) return;
  if (document.getElementById('ending-overlay')?.classList.contains('show')) return;
  if (document.getElementById('trump-card-overlay')?.classList.contains('show')) return;

  // Check if impeachment triggers instead of random attack
  let atk;
  const loopN = G.ngPlusLoop || 0;
  const dsExcess = Math.max(0, G.deepStateHP - 50);
  const impeachChance = (loopN * 5) + dsExcess + (G.purity < 20 ? 10 : 0);
  const impeachAtk = ATTACKS.find(a => a.impeachment);

  if (impeachAtk && Math.random() * 100 < impeachChance) {
    atk = impeachAtk;
  } else {
    // Pick random non-impeachment attack
    const normalAttacks = ATTACKS.filter(a => !a.impeachment);
    atk = normalAttacks[Math.floor(Math.random() * normalAttacks.length)];
  }

  // HP damage bypasses scaling - attacks hit HARD!
  // Deep State gains still scaled
  const scale = getDifficultyScale();
  const rawHP = atk.hp; // No scaling - full damage!
  const scaledDS = atk.ds / scale;
  G.trumpHP += rawHP;
  G.deepStateHP += scaledDS;

  // Impeachment has extra consequences
  if (atk.impeachment) {
    G.purity = Math.max(0, G.purity - 10);
    G.moves = Math.max(1, G.moves - 1);
    G.impeachmentCount = (G.impeachmentCount || 0) + 1;
    if (G.gameHistory) G.gameHistory.impeachments = (G.gameHistory.impeachments || 0) + 1;
  }

  // Track attack survived in history
  if (G.gameHistory) G.gameHistory.attacksSurvived++;

  // Show notification using new system
  showNotification({
    type: atk.type || NOTIFICATION_CONFIG.defaultStyle,
    title: atk.t,
    message: atk.impeachment ? atk.m + ' (' + G.impeachmentCount + '/3)' : atk.m,
    video: atk.img,
    sender: 'Deep State Intelligence',
    handle: '@deepstate_ops',
    avatar: '🏛️',
    hpChange: rawHP,
    dsChange: Math.round(scaledDS)
  });

  // Update display
  setTimeout(() => {
    updateTrumpVideo();
    updateDisplay();
  }, 100);
}

// ==================== PRELOAD TEMPLATES ====================

function preloadNotificationTemplates() {
  ['tweet', 'email', 'text', 'postit', 'bulletin'].forEach(loadTemplate);
}

// Auto-preload on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', preloadNotificationTemplates);
} else {
  preloadNotificationTemplates();
}

// ==================== GLOBAL NOTIFICATION MUTE ====================

function toggleNotificationMute(btn) {
  notificationsMuted = !notificationsMuted;
  btn.textContent = notificationsMuted ? '🔇' : '🔊';
  btn.classList.toggle('muted', notificationsMuted);

  // Play shut up sound when muting
  if (notificationsMuted) {
    const muteSound = document.getElementById('mute-sound');
    if (muteSound) {
      muteSound.currentTime = 0;
      muteSound.play().catch(() => {});
    }

    // Find and mute any playing videos in notifications
    const overlay = btn.closest('.notification-overlay');
    if (overlay) {
      const video = overlay.querySelector('video');
      if (video) video.muted = true;

      // Shorten message if postit
      const msg = overlay.querySelector('.postit-message, .tweet-text, .email-message');
      if (msg) msg.classList.add('muted-short');

      // Auto close after short delay
      setTimeout(() => {
        const postit = overlay.querySelector('.postit-notification');
        if (postit) {
          tearPostit(postit);
        } else {
          closeNotification(btn);
        }
      }, 1000);
    }
  }
}

// ==================== POSTIT TEAR ANIMATION ====================

function tearPostit(element) {
  const postit = element.closest ? element.closest('.postit-notification') || element : element;
  const overlay = postit.closest('.notification-overlay');

  // Stop any videos
  const video = overlay?.querySelector('video');
  if (video) video.pause();

  // Add tear animation
  postit.classList.add('tearing');

  // Remove after animation
  setTimeout(() => {
    if (overlay && overlay.parentNode) {
      overlay.parentNode.removeChild(overlay);
    }
  }, 600);
}
