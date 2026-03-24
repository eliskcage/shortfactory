/**
 * High Score System - Trump Game
 * Triggers at 100%, 99%, 98%, 97% purity
 */

// Track which purity milestones have been recorded
const recordedMilestones = new Set();

// Minimum wealth required to qualify for high score (in thousands)
const MIN_WEALTH_THRESHOLD = 50000; // $50,000

// Check purity and trigger name entry
function checkPurityMilestone() {
    // Check if player asked Cortex to disable leaderboard
    const disableHighScores = localStorage.getItem('disable_highscores');
    if (disableHighScores === 'true') {
        return; // Leaderboard disabled by Cortex
    }

    const purityElement = document.getElementById('disp-purity');
    if (!purityElement) return;

    const purityText = purityElement.textContent.trim();
    const purity = parseInt(purityText);

    // ONLY SHOW LEADERBOARD AT 97% PURITY OR HIGHER
    if (purity < 97) {
        return; // Not pure enough for leaderboard
    }

    // Don't show if finale system is handling it
    if (typeof finaleActive !== 'undefined' && finaleActive) {
        return;
    }

    // Check if player has enough wealth to qualify
    const currentWealth = getPlayerWealth();
    if (currentWealth < MIN_WEALTH_THRESHOLD) {
        return; // Not impressive enough
    }

    // Check if we hit a milestone (97% or higher only)
    const milestones = [100, 99, 98, 97];
    if (milestones.includes(purity) && !recordedMilestones.has(purity)) {
        recordedMilestones.add(purity);
        showNameEntry(purity);
    }
}

// Get player's current wealth from game state
function getPlayerWealth() {
    // Try to get from global game state
    if (typeof G !== 'undefined' && G.oilCash !== undefined) {
        return G.oilCash;
    }

    // Try to parse from debt display (negative means we have money)
    const debtElement = document.getElementById('disp-debt');
    if (debtElement) {
        const debtText = debtElement.textContent.replace(/[^0-9.-]/g, '');
        const debt = parseFloat(debtText);

        // If debt is going down from 38T, wealth is increasing
        const startingDebt = 38000; // 38 trillion in billions
        return Math.max(0, startingDebt - debt);
    }

    // Try wealth stack count (number of money icons)
    const wealthStack = document.getElementById('wealth-stack');
    if (wealthStack && wealthStack.children) {
        return wealthStack.children.length * 10000; // Each icon = $10k
    }

    return 0;
}

// Show name entry modal
function showNameEntry(purity) {
    const modal = document.getElementById('highscore-entry-modal');
    if (!modal) return;

    document.getElementById('hs-purity-display').textContent = purity + '%';
    modal.classList.add('active');

    // Grey out game, turn off neon glow
    const phone = document.getElementById('phone');
    phone.classList.add('highscore-active');

    // Focus on input
    setTimeout(() => {
        const input = document.getElementById('hs-name-input');
        if (input) input.focus();
    }, 300);
}

// Submit high score
async function submitHighScore() {
    const input = document.getElementById('hs-name-input');
    const purityDisplay = document.getElementById('hs-purity-display');

    const name = (input.value || 'ANON').trim().toUpperCase();
    const purity = parseInt(purityDisplay.textContent);

    try {
        const response = await fetch('/trump/highscores.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, purity })
        });

        const data = await response.json();

        if (data.success) {
            console.log('✅ Score saved! Rank:', data.rank);
            closeNameEntry();

            // Show leaderboard after 500ms
            setTimeout(() => showLeaderboard(), 500);
        } else {
            console.error('Failed to save score:', data.error);
            closeNameEntry();
            triggerFinaleCallback();
        }
    } catch (error) {
        console.error('Error submitting score:', error);
        closeNameEntry();
        triggerFinaleCallback();
    }
}

// Skip high score entry - goes straight to finale narration
function skipHighScore() {
    closeNameEntry();
    triggerFinaleCallback();
}

// Fire the finale callback if set (from startFinale in main.js)
function triggerFinaleCallback() {
    if (typeof window.onFinaleHighScoreDone === 'function') {
        window.onFinaleHighScoreDone();
    }
}

// Close name entry modal
function closeNameEntry() {
    const modal = document.getElementById('highscore-entry-modal');
    if (modal) {
        modal.classList.remove('active');
    }

    const phone = document.getElementById('phone');
    phone.classList.remove('highscore-active');
}

// Show leaderboard
async function showLeaderboard() {
    try {
        const response = await fetch('/trump/highscores.php');
        const data = await response.json();

        if (data.success && data.scores) {
            populateLeaderboard(data.scores);

            const leaderboard = document.getElementById('highscore-leaderboard');
            if (leaderboard) {
                leaderboard.classList.add('active');

                // Grey out game
                const phone = document.getElementById('phone');
                phone.classList.add('highscore-active');
            }
        }
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
    }
}

// Populate leaderboard with scores
function populateLeaderboard(scores) {
    const tbody = document.getElementById('hs-scores-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    scores.forEach((score, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${score.player_name}</td>
            <td>${score.purity}%</td>
        `;
        tbody.appendChild(row);
    });

    // Fill empty rows if less than 10
    for (let i = scores.length; i < 10; i++) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${i + 1}</td><td>---</td><td>--</td>`;
        tbody.appendChild(row);
    }
}

// Close leaderboard
function closeLeaderboard() {
    const leaderboard = document.getElementById('highscore-leaderboard');
    if (leaderboard) {
        leaderboard.classList.remove('active');
    }

    const phone = document.getElementById('phone');
    phone.classList.remove('highscore-active');

    // Trigger finale narration if game is ending
    triggerFinaleCallback();
}

// Initialize system
function initHighScoreSystem() {
    // Add HTML structure
    injectHighScoreHTML();

    // Monitor purity changes every 500ms
    setInterval(checkPurityMilestone, 500);

    console.log('🏆 High Score System initialized');
}

// Inject HTML for modals
function injectHighScoreHTML() {
    const html = `
        <!-- High Score Name Entry -->
        <div class="highscore-entry-modal" id="highscore-entry-modal">
            <div class="hs-entry-box">
                <div class="hs-entry-title">PURITY MILESTONE!</div>
                <div class="hs-purity-big" id="hs-purity-display">100%</div>
                <div class="hs-entry-label">ENTER YOUR NAME</div>
                <input type="text" id="hs-name-input" class="hs-name-input" maxlength="3" placeholder="AAA">
                <button class="hs-submit-btn" onclick="submitHighScore()">SUBMIT</button>
                <button class="hs-skip-btn" onclick="skipHighScore()">SKIP</button>
            </div>
        </div>

        <!-- High Score Leaderboard -->
        <div class="highscore-leaderboard" id="highscore-leaderboard">
            <div class="hs-board-container">
                <img src="https://www.shortfactory.shop/trump/icons/trump-head.png" class="hs-trump-head" alt="Trump">
                <div class="hs-board-title">TOP SCORES</div>
                <table class="hs-board-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>NAME</th>
                            <th>PURITY</th>
                        </tr>
                    </thead>
                    <tbody id="hs-scores-body">
                        <!-- Filled by JS -->
                    </tbody>
                </table>
                <button class="hs-close-btn" onclick="closeLeaderboard()">CLOSE</button>
            </div>
        </div>

        <!-- High Score Styles -->
        <style>
        /* Grey overlay when highscore active */
        .phone-frame.highscore-active::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 9998;
            pointer-events: none;
        }

        /* Turn off neon glow */
        .phone-frame.highscore-active .map-section video,
        .phone-frame.highscore-active .trump-box video {
            filter: grayscale(100%) brightness(0.3) !important;
        }

        /* Name Entry Modal */
        .highscore-entry-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }

        .highscore-entry-modal.active {
            opacity: 1;
            pointer-events: all;
        }

        .hs-entry-box {
            background: #d00;
            border: 6px solid #000;
            padding: 30px;
            text-align: center;
            box-shadow: 0 0 50px rgba(255, 0, 0, 0.8);
            font-family: 'Press Start 2P', monospace;
        }

        .hs-entry-title {
            font-size: 16px;
            color: #000;
            margin-bottom: 20px;
            text-shadow: 2px 2px 0 #fff;
        }

        .hs-purity-big {
            font-size: 48px;
            color: #ff0;
            margin: 20px 0;
            text-shadow: 4px 4px 0 #000;
        }

        .hs-entry-label {
            font-size: 12px;
            color: #000;
            margin-bottom: 15px;
        }

        .hs-name-input {
            font-family: 'Press Start 2P', monospace;
            font-size: 16px;
            padding: 10px;
            border: 4px solid #000;
            background: #fff;
            color: #000;
            text-align: center;
            text-transform: uppercase;
            width: 100%;
            max-width: 300px;
            margin-bottom: 20px;
        }

        .hs-name-input:focus {
            outline: none;
            border-color: #ff0;
        }

        .hs-submit-btn, .hs-skip-btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 14px;
            padding: 12px 30px;
            border: 4px solid #000;
            background: #ff0;
            color: #000;
            cursor: pointer;
            margin: 5px;
            text-shadow: 1px 1px 0 #fff;
            transition: all 0.2s;
        }

        .hs-skip-btn {
            background: #666;
            color: #fff;
        }

        .hs-submit-btn:hover {
            background: #ffff00;
            transform: scale(1.05);
        }

        .hs-skip-btn:hover {
            background: #888;
            transform: scale(1.05);
        }

        /* Leaderboard */
        .highscore-leaderboard {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }

        .highscore-leaderboard.active {
            opacity: 1;
            pointer-events: all;
        }

        .hs-board-container {
            background: #d00;
            border: 8px solid #000;
            padding: 30px;
            text-align: center;
            box-shadow: 0 0 60px rgba(255, 0, 0, 0.9);
            font-family: 'Press Start 2P', monospace;
            max-width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .hs-trump-head {
            width: 80px;
            height: 80px;
            margin-bottom: 15px;
            border: 4px solid #ff0;
            border-radius: 50%;
        }

        .hs-board-title {
            font-size: 24px;
            color: #ff0;
            margin-bottom: 25px;
            text-shadow: 4px 4px 0 #000;
        }

        .hs-board-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
        }

        .hs-board-table th,
        .hs-board-table td {
            padding: 12px;
            border: 3px solid #000;
            background: #d00;
            color: #000;
            font-size: 12px;
            text-align: center;
        }

        .hs-board-table th {
            background: #800;
            color: #ff0;
            font-size: 14px;
        }

        .hs-board-table tr:nth-child(1) td {
            background: #ff0;
            color: #000;
            font-weight: bold;
        }

        .hs-board-table tr:nth-child(2) td {
            background: #ccc;
            color: #000;
        }

        .hs-board-table tr:nth-child(3) td {
            background: #cd7f32;
            color: #000;
        }

        .hs-close-btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 16px;
            padding: 15px 40px;
            border: 4px solid #000;
            background: #ff0;
            color: #000;
            cursor: pointer;
            text-shadow: 2px 2px 0 #fff;
            transition: all 0.2s;
        }

        .hs-close-btn:hover {
            background: #ffff00;
            transform: scale(1.05);
        }

        @media (max-width: 768px) {
            .hs-entry-box, .hs-board-container {
                padding: 20px;
            }

            .hs-board-title {
                font-size: 18px;
            }

            .hs-board-table th,
            .hs-board-table td {
                padding: 8px;
                font-size: 10px;
            }
        }
        </style>
    `;

    document.body.insertAdjacentHTML('beforeend', html);
}

// Auto-initialize when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHighScoreSystem);
} else {
    initHighScoreSystem();
}

// Export functions for manual use
if (typeof window !== 'undefined') {
    window.HighScoreSystem = {
        showLeaderboard,
        checkPurityMilestone,
        disableLeaderboard: () => {
            localStorage.setItem('disable_highscores', 'true');
            console.log('🚫 Leaderboard disabled by Cortex');
        },
        enableLeaderboard: () => {
            localStorage.removeItem('disable_highscores');
            console.log('✅ Leaderboard enabled');
        }
    };
}
