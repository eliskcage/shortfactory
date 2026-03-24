/**
 * ShortFactory Arcade System
 * 1980s Arcade Leaderboard + Music for ALL pages
 * HOLLYWOOD 2.0 - CHRIST IS KING
 */

// Arcade Leaderboard - TOP SCORES
const LEADERBOARD_DATA = [
    { rank: 1, name: 'DAN', score: 999999, color: '#ff0' },
    { rank: 2, name: 'GOD', score: 888888, color: '#f0f' },
    { rank: 3, name: 'USA', score: 777777, color: '#f00' },
    { rank: 4, name: 'KEK', score: 666666, color: '#0f0' },
    { rank: 5, name: 'ACE', score: 555555, color: '#0ff' },
    { rank: 6, name: 'MAX', score: 444444, color: '#ff0' },
    { rank: 7, name: 'ZEN', score: 333333, color: '#f0f' },
    { rank: 8, name: 'RON', score: 222222, color: '#0ff' }
];

// Create leaderboard HTML
function createLeaderboard() {
    if (document.getElementById('arcadeLeaderboard')) return; // Already exists

    const leaderboard = document.createElement('div');
    leaderboard.id = 'arcadeLeaderboard';
    leaderboard.className = 'arcade-leaderboard';

    let html = `
        <div class="leaderboard-header">
            <div class="header-title">HIGH SCORES</div>
            <div class="header-blink">★ TOP PLAYERS ★</div>
        </div>
        <div class="leaderboard-content">
    `;

    LEADERBOARD_DATA.forEach(entry => {
        html += `
            <div class="leaderboard-entry">
                <span class="rank">${entry.rank}.</span>
                <span class="player-name" style="color: ${entry.color}">${entry.name}</span>
                <span class="player-score">${entry.score.toLocaleString()}</span>
            </div>
        `;
    });

    html += `
        </div>
        <div class="leaderboard-footer">PRESS START</div>
    `;

    leaderboard.innerHTML = html;
    document.body.appendChild(leaderboard);

    console.log('🏆 Arcade leaderboard loaded');
}

// Create music player
function createMusicPlayer() {
    if (document.getElementById('arcadeMusic')) return; // Already exists

    const musicContainer = document.createElement('div');
    musicContainer.id = 'arcadeMusicContainer';
    musicContainer.className = 'arcade-music-player';

    // Check if user explicitly turned OFF music (default to ON)
    const musicOff = localStorage.getItem('arcadeMusicPlaying') === 'false';
    const shouldPlay = !musicOff; // Play by default unless user turned it off

    musicContainer.innerHTML = `
        <audio id="arcadeMusic" loop preload="auto">
            <source src="/arcade_music.mp3" type="audio/mpeg">
        </audio>
        <button class="music-toggle" id="musicToggle" title="Music controls">
            ${shouldPlay ? '🔊' : '🔇'}
        </button>
    `;

    document.body.appendChild(musicContainer);

    const audio = document.getElementById('arcadeMusic');
    const toggle = document.getElementById('musicToggle');

    // Set volume
    audio.volume = 0.3;

    // Try to auto-play (will be blocked until user interacts)
    let hasAttemptedPlay = false;

    const tryAutoPlay = () => {
        if (hasAttemptedPlay || musicOff) return;
        hasAttemptedPlay = true;

        audio.play().then(() => {
            console.log('🎵 Music auto-playing!');
            toggle.textContent = '🔊';
            localStorage.setItem('arcadeMusicPlaying', 'true');
        }).catch(err => {
            console.log('🎵 Autoplay blocked - will start on first click');
        });
    };

    // Try immediately
    tryAutoPlay();

    // Try again on first user interaction
    const unlockAndPlay = () => {
        tryAutoPlay();
        document.removeEventListener('click', unlockAndPlay);
        document.removeEventListener('touchstart', unlockAndPlay);
        document.removeEventListener('keydown', unlockAndPlay);
    };

    document.addEventListener('click', unlockAndPlay, { once: true });
    document.addEventListener('touchstart', unlockAndPlay, { once: true });
    document.addEventListener('keydown', unlockAndPlay, { once: true });

    // Toggle button - manual control
    toggle.addEventListener('click', (e) => {
        e.stopPropagation(); // Don't trigger other click handlers

        if (audio.paused) {
            audio.play().then(() => {
                toggle.textContent = '🔊';
                toggle.title = 'Mute Music';
                localStorage.setItem('arcadeMusicPlaying', 'true');
                console.log('🎵 Music playing');
            }).catch(err => {
                console.error('Failed to play:', err);
            });
        } else {
            audio.pause();
            toggle.textContent = '🔇';
            toggle.title = 'Play Music';
            localStorage.setItem('arcadeMusicPlaying', 'false');
            console.log('🎵 Music paused');
        }
    });

    console.log('🎵 Arcade music player loaded - Auto-playing on first interaction!');
}

// Add CSS styles
function injectArcadeStyles() {
    if (document.getElementById('arcadeSystemStyles')) return; // Already injected

    const style = document.createElement('style');
    style.id = 'arcadeSystemStyles';
    style.textContent = `
        /* Arcade Leaderboard */
        .arcade-leaderboard {
            position: fixed;
            top: 50%;
            left: 20px;
            transform: translateY(-50%);
            z-index: 999;
            background: rgba(0,0,0,0.9);
            border: 4px solid #ff0;
            border-radius: 10px;
            padding: 15px;
            box-shadow:
                0 0 30px rgba(255,255,0,0.6),
                inset 0 0 20px rgba(255,255,0,0.2);
            font-family: 'Press Start 2P', monospace;
            min-width: 280px;
            animation: leaderboardGlow 3s ease-in-out infinite;
        }

        @keyframes leaderboardGlow {
            0%, 100% {
                box-shadow: 0 0 30px rgba(255,255,0,0.6), inset 0 0 20px rgba(255,255,0,0.2);
            }
            50% {
                box-shadow: 0 0 50px rgba(255,255,0,0.9), inset 0 0 30px rgba(255,255,0,0.3);
            }
        }

        .leaderboard-header {
            text-align: center;
            margin-bottom: 15px;
            border-bottom: 2px solid #ff0;
            padding-bottom: 10px;
        }

        .header-title {
            font-size: 0.9rem;
            color: #ff0;
            text-shadow: 0 0 10px #ff0, 2px 2px 0px #000;
            margin-bottom: 5px;
        }

        .header-blink {
            font-size: 0.5rem;
            color: #f0f;
            text-shadow: 0 0 10px #f0f;
            animation: blinkText 1.5s ease-in-out infinite;
        }

        @keyframes blinkText {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .leaderboard-content {
            margin: 10px 0;
        }

        .leaderboard-entry {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
            font-size: 0.6rem;
            border-bottom: 1px solid rgba(255,255,0,0.2);
        }

        .leaderboard-entry:last-child {
            border-bottom: none;
        }

        .rank {
            color: #fff;
            width: 25px;
            text-shadow: 1px 1px 0px #000;
        }

        .player-name {
            flex: 1;
            font-weight: bold;
            text-shadow: 0 0 10px currentColor, 2px 2px 0px #000;
            letter-spacing: 0.1em;
        }

        .player-score {
            color: #0ff;
            text-shadow: 0 0 10px #0ff, 2px 2px 0px #000;
        }

        .leaderboard-footer {
            text-align: center;
            font-size: 0.5rem;
            color: #0f0;
            text-shadow: 0 0 10px #0f0;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 2px solid #0f0;
            animation: blinkText 1s ease-in-out infinite;
        }

        /* Music Player */
        .arcade-music-player {
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 999;
        }

        .music-toggle {
            background: rgba(0,0,0,0.9);
            border: 3px solid #0f0;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(0,255,0,0.6);
            transition: all 0.3s;
            color: #fff;
        }

        .music-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 0 30px rgba(0,255,0,0.9);
            background: rgba(0,255,0,0.2);
        }

        .music-toggle:active {
            transform: scale(0.95);
        }

        /* Mobile adjustments */
        /* Minecraft Showcase Button */
        .minecraft-showcase-btn {
            position: fixed;
            bottom: 90px;
            left: 20px;
            z-index: 999;
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #8b4513 0%, #654321 50%, #3d2817 100%);
            border: 4px solid #000;
            border-radius: 5px;
            box-shadow:
                0 0 20px rgba(139, 69, 19, 0.6),
                inset 0 0 10px rgba(255, 255, 255, 0.1),
                inset 0 -5px 10px rgba(0, 0, 0, 0.5);
            font-family: 'Press Start 2P', monospace;
            font-size: 0.5rem;
            color: #fff;
            text-align: center;
            text-decoration: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            line-height: 1.4;
            text-shadow: 2px 2px 0px #000;
        }

        .minecraft-showcase-btn:hover {
            transform: scale(1.1) translateY(-3px);
            box-shadow:
                0 5px 30px rgba(139, 69, 19, 0.9),
                inset 0 0 15px rgba(255, 255, 255, 0.2);
            background: linear-gradient(135deg, #a0522d 0%, #8b4513 50%, #654321 100%);
        }

        .minecraft-showcase-btn:active {
            transform: scale(0.95);
        }

        @media (max-width: 768px) {
            .arcade-leaderboard {
                left: 10px;
                min-width: 200px;
                padding: 10px;
                font-size: 0.5rem;
            }

            .header-title {
                font-size: 0.7rem;
            }

            .leaderboard-entry {
                font-size: 0.5rem;
            }

            .music-toggle {
                width: 50px;
                height: 50px;
                font-size: 1.2rem;
            }

            .minecraft-showcase-btn {
                width: 60px;
                height: 60px;
                font-size: 0.45rem;
                bottom: 80px;
            }
        }
    `;

    document.head.appendChild(style);
}

// Create Minecraft showcase button
function createMinecraftButton() {
    if (document.getElementById('minecraftBtn')) return; // Already exists

    const button = document.createElement('a');
    button.id = 'minecraftBtn';
    button.className = 'minecraft-showcase-btn';
    button.href = '/showcase_matrix.html';
    button.innerHTML = '📺<br>SHOWCASES';
    button.title = 'View ShortFactory Showcases';

    document.body.appendChild(button);

    console.log('📺 Minecraft showcase button loaded');
}

// Initialize arcade system
function initArcadeSystem() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        injectArcadeStyles();
        createLeaderboard();
        createMusicPlayer();
        createMinecraftButton();
        console.log('🎮 ARCADE SYSTEM LOADED - HOLLYWOOD 2.0');
    }
}

// Auto-initialize
initArcadeSystem();

// Export for manual use
if (typeof window !== 'undefined') {
    window.ArcadeSystem = {
        createLeaderboard,
        createMusicPlayer,
        createMinecraftButton,
        init: initArcadeSystem
    };
}
