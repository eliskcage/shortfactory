/**
 * CONTRIBUTION.JS — You are the battery
 * Site-wide: grayscale punishment for freeloaders, color unlocks for contributors.
 * Tool locking until contribution thresholds are met.
 * Load on EVERY page.
 */
(function() {
    'use strict';

    // ─── Contribution types ──────────────────────────────────────
    // Each type = 1 color unlock. 5 types = full color.
    function getContributions() {
        var player = null;
        try { player = JSON.parse(localStorage.getItem('sc_player')); } catch(e) {}

        var contributions = 0;
        var types = {};

        // 1. GPU contribution (screensaver ran)
        if (player && player.gpuSeconds > 0) {
            contributions++;
            types.gpu = true;
        }

        // 2. Brain tasks completed (>10)
        if (player && player.brainTasks > 10) {
            contributions++;
            types.brain = true;
        }

        // 3. Merch/checkout purchased
        if (localStorage.getItem('sf_purchased') === 'true') {
            contributions++;
            types.wallet = true;
        }

        // 4. Game played (>5 mins)
        if (localStorage.getItem('sf_game_played') === 'true') {
            contributions++;
            types.game = true;
        }

        // 5. Imaginator used
        if (localStorage.getItem('sf_imaginator_used') === 'true') {
            contributions++;
            types.imaginator = true;
        }

        // 6. ALIVE app interaction
        if (localStorage.getItem('sf_alive_used') === 'true') {
            contributions++;
            types.alive = true;
        }

        // 7. API vault donation
        var vault = [];
        try { vault = JSON.parse(localStorage.getItem('sf_api_vault')) || []; } catch(e) {}
        if (vault.length > 0) {
            contributions++;
            types.apiVault = true;
        }

        return {
            count: Math.min(contributions, 6),
            types: types,
            credits: player ? (player.credits || 0) : 0,
            gpuSeconds: player ? (player.gpuSeconds || 0) : 0,
            brainTasks: player ? (player.brainTasks || 0) : 0,
            sessions: player ? (player.sessions || 0) : 0
        };
    }

    // ─── Apply grayscale based on contribution count ─────────────
    function applyGrayscale() {
        // Unlocked bypass — no grayscale (must contribute to earn it)
        if (localStorage.getItem('sf_unlocked') === 'true') {
            return getContributions();
        }

        var c = getContributions();
        var grayscale;

        switch(c.count) {
            case 0: grayscale = 1.0; break;
            case 1: grayscale = 0.8; break;
            case 2: grayscale = 0.65; break;
            case 3: grayscale = 0.45; break;
            case 4: grayscale = 0.25; break;
            case 5: grayscale = 0.1; break;
            default: grayscale = 0; break;
        }

        if (grayscale > 0) {
            document.documentElement.style.filter = 'grayscale(' + grayscale + ')';
            document.documentElement.style.transition = 'filter 2s ease';
        }

        // Inject CSS for locked tools
        var style = document.createElement('style');
        style.textContent = [
            '.sf-locked { position: relative !important; pointer-events: none !important; opacity: 0.3 !important; filter: grayscale(1) !important; }',
            '.sf-locked::after { content: "CONTRIBUTE TO UNLOCK"; position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.7); color: #daa520; font-family: "Orbitron", monospace; font-size: 10px; letter-spacing: 2px; pointer-events: auto; cursor: pointer; border-radius: inherit; z-index: 10; }',
            '.sf-lock-notice { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.95); color: #888; font-family: "Courier New", monospace; font-size: 11px; text-align: center; padding: 8px 16px; z-index: 9998; border-top: 1px solid #222; display: ' + (grayscale > 0 ? 'block' : 'none') + '; }',
            '.sf-lock-notice strong { color: #daa520; }',
            '.sf-lock-notice a { color: #00ccff; text-decoration: none; }',
        ].join('\n');
        document.head.appendChild(style);

        // Add notice bar at bottom if not fully unlocked
        if (grayscale > 0) {
            var notice = document.createElement('div');
            notice.className = 'sf-lock-notice';
            notice.innerHTML = 'YOU ARE THE <strong>BATTERY</strong>. ' +
                c.count + '/6 contributions. ' +
                '<a href="/screensaver/">SUPERCHARGE</a> to unlock color.';
            document.body.appendChild(notice);
        }

        return c;
    }

    // ─── Lock specific tools based on thresholds ─────────────────
    function lockTools() {
        var c = getContributions();

        // Tool lock rules: [selector, unlock condition]
        var rules = [
            { href: '/imaginator/', unlock: c.types.wallet || c.credits >= 1000 },
            { href: '/comicvid/', unlock: c.types.wallet || c.credits >= 2000 },
            { href: '/ipfs/', unlock: c.types.wallet || c.credits >= 5000 },
            { href: '/dares4dosh/', unlock: c.types.game || c.types.gpu },
            { href: '/dares4dosh/app/', unlock: c.types.game || c.types.gpu },
        ];

        // Always available (contribution channels): screensaver, game, alive
        // Cortex chat unlocks via screensaver or game
        var cortexBubble = document.getElementById('cortexBubble');
        if (cortexBubble && !c.types.gpu && !c.types.game) {
            cortexBubble.classList.add('sf-locked');
            cortexBubble.addEventListener('click', function(e) {
                e.stopPropagation();
                window.location.href = '/screensaver/';
            }, true);
        }

        // Lock matching links
        var allLinks = document.querySelectorAll('a[href]');
        for (var i = 0; i < allLinks.length; i++) {
            var link = allLinks[i];
            var href = link.getAttribute('href');
            if (!href) continue;

            for (var j = 0; j < rules.length; j++) {
                if (href.indexOf(rules[j].href) === 0 && !rules[j].unlock) {
                    link.classList.add('sf-locked');
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        window.location.href = '/screensaver/';
                    }, true);
                    break;
                }
            }
        }
    }

    // ─── Contribution tracking helpers ───────────────────────────
    // Call these from other pages to register contributions
    window.SFContribution = {
        getContributions: getContributions,

        markGamePlayed: function() {
            localStorage.setItem('sf_game_played', 'true');
        },

        markImaginatorUsed: function() {
            localStorage.setItem('sf_imaginator_used', 'true');
        },

        markAliveUsed: function() {
            localStorage.setItem('sf_alive_used', 'true');
        },

        markPurchased: function() {
            localStorage.setItem('sf_purchased', 'true');
        },

        refresh: function() {
            document.documentElement.style.filter = '';
            applyGrayscale();
        }
    };

    // ─── Init on DOM ready ───────────────────────────────────────
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            applyGrayscale();
            lockTools();
        });
    } else {
        applyGrayscale();
        lockTools();
    }
})();
