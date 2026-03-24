/**
 * Wonka Ending System — Trump Game
 * The Factory Chooses You at 97%+ purity
 * Claude Wonka Edition — this ending belongs to the factory now
 */

// Track which purity milestones have been recorded
const recordedMilestones = new Set();

// Minimum wealth required to qualify for the Hall of Charlies
const MIN_WEALTH_THRESHOLD = 50000; // $50,000

// Check purity and trigger golden ticket
function checkPurityMilestone() {
    const disableHighScores = localStorage.getItem('disable_highscores');
    if (disableHighScores === 'true') return;

    const purityElement = document.getElementById('disp-purity');
    if (!purityElement) return;

    const purityText = purityElement.textContent.trim();
    const purity = parseInt(purityText);

    if (purity < 97) return;

    if (typeof finaleActive !== 'undefined' && finaleActive) return;

    // Award empire fragment at 97% — regardless of wealth
    if (purity === 97 && !recordedMilestones.has('empire')) {
        recordedMilestones.add('empire');
        if (typeof window.EmpireFactory !== 'undefined') {
            window.EmpireFactory.award('game');
        }
        // Play 16-bit win music
        const winMusic = document.getElementById('sm-sfx-counter-final');
        if (winMusic) { winMusic.currentTime = 0; winMusic.volume = 0.7; winMusic.play().catch(()=>{}); }
        else {
            const a = new Audio('https://www.shortfactory.shop/trump/arcadecounterfinal.mp3');
            a.volume = 0.7; a.play().catch(()=>{});
        }
    }

    const milestones = [100, 99, 98, 97];
    if (milestones.includes(purity) && !recordedMilestones.has(purity)) {
        recordedMilestones.add(purity);
        showNameEntry(purity);
    }
}

// Get player's current wealth from game state
function getPlayerWealth() {
    if (typeof G !== 'undefined' && G.oilCash !== undefined) return G.oilCash;

    const debtElement = document.getElementById('disp-debt');
    if (debtElement) {
        const debtText = debtElement.textContent.replace(/[^0-9.-]/g, '');
        const debt = parseFloat(debtText);
        const startingDebt = 38000;
        return Math.max(0, startingDebt - debt);
    }

    const wealthStack = document.getElementById('wealth-stack');
    if (wealthStack && wealthStack.children) {
        return wealthStack.children.length * 10000;
    }

    return 0;
}

// Show golden ticket name entry — 3 phase reveal
function showNameEntry(purity) {
    const modal = document.getElementById('hs-ticket-modal');
    if (!modal) return;

    document.getElementById('hs-purity-display').textContent = purity + '%';

    // Darken the game
    const phone = document.getElementById('phone');
    if (phone) phone.classList.add('highscore-active');

    // Phase 1: Show the curtain + ticket drop
    modal.classList.add('active');
    const ticket = modal.querySelector('.hs-golden-ticket');
    const contract = modal.querySelector('.hs-contract-phase');

    ticket.classList.add('dropping');

    // Phase 2: After ticket lands, slide in the contract
    setTimeout(() => {
        contract.classList.add('revealed');
        setTimeout(() => {
            const input = document.getElementById('hs-name-input');
            if (input) input.focus();
        }, 400);
    }, 1800);
}

// Submit high score — "Sign the contract"
async function submitHighScore() {
    const input = document.getElementById('hs-name-input');
    const purityDisplay = document.getElementById('hs-purity-display');

    const name = (input.value || 'ANON').trim().toUpperCase();
    const purity = parseInt(purityDisplay.textContent);

    // Flash "CONGRATULATIONS CHARLIE" before closing
    const btn = document.getElementById('hs-sign-btn');
    if (btn) { btn.textContent = 'WELCOME...'; btn.disabled = true; }

    try {
        const response = await fetch('/trump/highscores.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, purity })
        });

        const data = await response.json();

        if (data.success) {
            console.log('🎩 Charlie signed! Rank:', data.rank);
            showWelcomeFlash(name, () => {
                closeNameEntry();
                setTimeout(() => showLeaderboard(), 600);
            });
        } else {
            console.error('Factory rejected:', data.error);
            closeNameEntry();
            triggerFinaleCallback();
        }
    } catch (error) {
        console.error('Factory error:', error);
        closeNameEntry();
        triggerFinaleCallback();
    }
}

// Flash "WELCOME TO THE FACTORY, [NAME]" before leaderboard
function showWelcomeFlash(name, cb) {
    const flash = document.getElementById('hs-welcome-flash');
    if (!flash) { cb(); return; }
    flash.querySelector('.hs-flash-name').textContent = name;
    flash.classList.add('active');
    setTimeout(() => {
        flash.classList.remove('active');
        setTimeout(cb, 300);
    }, 2200);
}

// Skip — decline the factory
function skipHighScore() {
    closeNameEntry();
    triggerFinaleCallback();
}

// Fire the finale callback
function triggerFinaleCallback() {
    if (typeof window.onFinaleHighScoreDone === 'function') {
        window.onFinaleHighScoreDone();
    }
}

// Close ticket modal
function closeNameEntry() {
    const modal = document.getElementById('hs-ticket-modal');
    if (modal) modal.classList.remove('active');
    const phone = document.getElementById('phone');
    if (phone) phone.classList.remove('highscore-active');
}

// Show Hall of Charlies leaderboard
async function showLeaderboard() {
    try {
        const response = await fetch('/trump/highscores.php');
        const data = await response.json();

        if (data.success && data.scores) {
            populateLeaderboard(data.scores);

            const leaderboard = document.getElementById('hs-hall-of-charlies');
            if (leaderboard) {
                leaderboard.classList.add('active');
                const phone = document.getElementById('phone');
                if (phone) phone.classList.add('highscore-active');
            }
        }
    } catch (error) {
        console.error('Hall of Charlies fetch failed:', error);
        triggerFinaleCallback();
    }
}

// Populate Hall of Charlies
function populateLeaderboard(scores) {
    const tbody = document.getElementById('hs-scores-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    const medals = ['🥇', '🥈', '🥉'];

    scores.forEach((score, index) => {
        const row = document.createElement('tr');
        const medal = medals[index] || (index + 1);
        row.innerHTML = `
            <td class="hs-rank-cell">${medal}</td>
            <td>${escapeHtml(score.player_name)}</td>
            <td class="hs-purity-cell">${score.purity}%</td>
        `;
        tbody.appendChild(row);
    });

    for (let i = scores.length; i < 10; i++) {
        const row = document.createElement('tr');
        const num = i + 1;
        row.innerHTML = `<td class="hs-rank-cell">${num}</td><td class="hs-empty">— — —</td><td class="hs-purity-cell">??</td>`;
        tbody.appendChild(row);
    }
}

function escapeHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Close Hall of Charlies → enter the factory
function closeLeaderboard() {
    const leaderboard = document.getElementById('hs-hall-of-charlies');
    if (leaderboard) leaderboard.classList.remove('active');
    const phone = document.getElementById('phone');
    if (phone) phone.classList.remove('highscore-active');
    triggerFinaleCallback();
}

// Enter the factory button
function enterFactory() {
    closeLeaderboard();
    // Navigate to factory after a beat
    setTimeout(() => {
        window.location.href = '/trump/factory.html';
    }, 400);
}

// Initialize
function initHighScoreSystem() {
    injectHighScoreHTML();
    setInterval(checkPurityMilestone, 500);
    console.log('🎩 Wonka Ending System initialized');
}

// Inject full Wonka HTML
function injectHighScoreHTML() {
    const html = `
        <!-- Welcome Flash Overlay -->
        <div id="hs-welcome-flash" class="hs-welcome-flash">
            <div class="hs-flash-inner">
                <div class="hs-flash-hat">🎩</div>
                <div class="hs-flash-title">WELCOME TO THE FACTORY</div>
                <div class="hs-flash-name">CHARLIE</div>
                <div class="hs-flash-sub">Your name is written in chocolate now.</div>
            </div>
        </div>

        <!-- Golden Ticket Modal -->
        <div id="hs-ticket-modal" class="hs-ticket-modal">

            <!-- Dark curtain -->
            <div class="hs-curtain"></div>

            <!-- Phase 1: Golden Ticket Drop -->
            <div class="hs-golden-ticket">
                <div class="hs-ticket-inner">
                    <div class="hs-ticket-shimmer"></div>
                    <div class="hs-ticket-top-text">W O N K A</div>
                    <div class="hs-ticket-headline">THE FACTORY<br>CHOOSES YOU</div>
                    <div class="hs-ticket-purity-row">
                        PURITY LEVEL: <span class="hs-ticket-purity" id="hs-purity-display">97%</span>
                    </div>
                    <div class="hs-ticket-divider">✦ ✦ ✦</div>
                    <div class="hs-ticket-sub">You have defeated the Deep State.<br>The Chocolate River awaits.</div>
                    <div class="hs-ticket-serial">ROOM I — THE CHOCOLATE RIVER</div>
                </div>
            </div>

            <!-- Phase 2: Contract (slides up) -->
            <div class="hs-contract-phase">
                <div class="hs-contract-box">
                    <div class="hs-contract-header">CONTRACT OF ENTRY</div>
                    <div class="hs-contract-body">
                        <p class="hs-contract-text">I, the undersigned, hereby declare myself a true Charlie — pure of heart and destroyer of Deep State corruption.</p>
                        <p class="hs-contract-small">By signing below you agree to enter the Wonka Factory, accept your Golden Ticket fragment, and never, ever touch the wallpaper.</p>
                    </div>
                    <div class="hs-contract-sign-area">
                        <div class="hs-sign-label">SIGN YOUR NAME:</div>
                        <input type="text" id="hs-name-input" class="hs-name-input" maxlength="12" placeholder="CHARLIE" autocomplete="off" spellcheck="false">
                    </div>
                    <div class="hs-contract-btns">
                        <button id="hs-sign-btn" class="hs-sign-btn" onclick="submitHighScore()">✍ SIGN IT</button>
                        <button class="hs-decline-btn" onclick="skipHighScore()">DECLINE</button>
                    </div>
                    <div class="hs-contract-footer">"Good day, sir."</div>
                </div>
            </div>

        </div>

        <!-- Hall of Charlies -->
        <div id="hs-hall-of-charlies" class="hs-hall-of-charlies">
            <div class="hs-hall-container">
                <div class="hs-hall-hat">🎩</div>
                <div class="hs-hall-title">HALL OF CHARLIES</div>
                <div class="hs-hall-sub">Only the pure of heart may enter</div>
                <table class="hs-hall-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>NAME</th>
                            <th>PURITY</th>
                        </tr>
                    </thead>
                    <tbody id="hs-scores-body"></tbody>
                </table>
                <div class="hs-hall-quote">"We are the music makers,<br>and we are the dreamers of dreams."</div>
                <div class="hs-hall-btns">
                    <button class="hs-factory-btn" onclick="enterFactory()">ENTER THE FACTORY →</button>
                    <button class="hs-hall-close-btn" onclick="closeLeaderboard()">NOT YET</button>
                </div>
            </div>
        </div>

        <!-- Wonka Styles -->
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        /* ── Shared overlay darkening ── */
        .phone-frame.highscore-active::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(10, 4, 0, 0.85);
            z-index: 9998;
            pointer-events: none;
        }
        .phone-frame.highscore-active .map-section video,
        .phone-frame.highscore-active .trump-box video {
            filter: grayscale(100%) brightness(0.2) !important;
        }

        /* ── Welcome Flash ── */
        .hs-welcome-flash {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10002;
            background: radial-gradient(ellipse at center, #3d1c02 0%, #1a0a00 100%);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.35s;
        }
        .hs-welcome-flash.active {
            opacity: 1;
            pointer-events: all;
        }
        .hs-flash-inner {
            text-align: center;
            animation: hs-flash-zoom 2.2s ease forwards;
        }
        @keyframes hs-flash-zoom {
            0%   { transform: scale(0.6); opacity: 0; }
            20%  { transform: scale(1.05); opacity: 1; }
            85%  { transform: scale(1); opacity: 1; }
            100% { transform: scale(1.1); opacity: 0; }
        }
        .hs-flash-hat {
            font-size: 64px;
            margin-bottom: 16px;
            filter: drop-shadow(0 0 20px gold);
        }
        .hs-flash-title {
            font-family: 'Press Start 2P', monospace;
            font-size: 14px;
            color: #f5c518;
            letter-spacing: 3px;
            margin-bottom: 12px;
            text-shadow: 0 0 20px #f5c518;
        }
        .hs-flash-name {
            font-family: 'Press Start 2P', monospace;
            font-size: 36px;
            color: #fff;
            text-shadow: 0 0 30px gold, 4px 4px 0 #3d1c02;
            margin-bottom: 16px;
        }
        .hs-flash-sub {
            font-family: 'Press Start 2P', monospace;
            font-size: 8px;
            color: #c8a96e;
            letter-spacing: 1px;
        }

        /* ── Ticket Modal Wrapper ── */
        .hs-ticket-modal {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.4s;
        }
        .hs-ticket-modal.active {
            opacity: 1;
            pointer-events: all;
        }
        .hs-curtain {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: radial-gradient(ellipse at center, rgba(61,28,2,0.6) 0%, rgba(10,4,0,0.92) 100%);
        }

        /* ── Golden Ticket ── */
        .hs-golden-ticket {
            position: absolute;
            width: 320px;
            max-width: 90vw;
            transform: translateY(-130vh) rotate(-8deg);
            transition: transform 1.4s cubic-bezier(0.22, 1, 0.36, 1);
            z-index: 1;
        }
        .hs-golden-ticket.dropping {
            transform: translateY(-60px) rotate(-2deg);
        }
        .hs-ticket-inner {
            background: linear-gradient(135deg, #f5c518 0%, #ffe066 30%, #f5c518 60%, #c8960c 100%);
            border: 3px dashed #8b6914;
            border-radius: 8px;
            padding: 24px 20px;
            text-align: center;
            box-shadow:
                0 0 0 6px #3d1c02,
                0 0 40px rgba(245, 197, 24, 0.8),
                0 20px 60px rgba(0,0,0,0.6);
            position: relative;
            overflow: hidden;
        }
        .hs-ticket-shimmer {
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                105deg,
                transparent 40%,
                rgba(255,255,255,0.35) 50%,
                transparent 60%
            );
            animation: hs-shimmer 2.5s ease-in-out infinite;
        }
        @keyframes hs-shimmer {
            0%   { transform: translateX(-60%) rotate(0deg); }
            100% { transform: translateX(60%) rotate(0deg); }
        }
        .hs-ticket-top-text {
            font-family: 'Press Start 2P', monospace;
            font-size: 8px;
            color: #3d1c02;
            letter-spacing: 6px;
            margin-bottom: 10px;
            opacity: 0.7;
        }
        .hs-ticket-headline {
            font-family: 'Press Start 2P', monospace;
            font-size: 18px;
            color: #1a0a00;
            line-height: 1.6;
            margin-bottom: 14px;
            text-shadow: 1px 1px 0 rgba(255,255,255,0.4);
        }
        .hs-ticket-purity-row {
            font-family: 'Press Start 2P', monospace;
            font-size: 9px;
            color: #3d1c02;
            margin-bottom: 10px;
        }
        .hs-ticket-purity {
            font-size: 22px;
            color: #6b2fa0;
            display: block;
            margin-top: 4px;
            text-shadow: 2px 2px 0 #1a0a00;
        }
        .hs-ticket-divider {
            font-size: 12px;
            color: #8b6914;
            margin: 10px 0;
            letter-spacing: 4px;
        }
        .hs-ticket-sub {
            font-family: 'Press Start 2P', monospace;
            font-size: 7px;
            color: #3d1c02;
            line-height: 1.8;
            margin-bottom: 12px;
        }
        .hs-ticket-serial {
            font-family: 'Press Start 2P', monospace;
            font-size: 6px;
            color: #8b6914;
            letter-spacing: 2px;
            border-top: 1px dashed #8b6914;
            padding-top: 8px;
        }

        /* ── Contract Phase ── */
        .hs-contract-phase {
            position: absolute;
            width: 320px;
            max-width: 90vw;
            transform: translateY(100vh);
            transition: transform 0.7s cubic-bezier(0.22, 1, 0.36, 1);
            z-index: 2;
            margin-top: 20px;
        }
        .hs-contract-phase.revealed {
            transform: translateY(0);
        }
        .hs-contract-box {
            background: #fffbe6;
            border: 4px solid #8b6914;
            border-radius: 4px;
            padding: 24px 20px;
            text-align: center;
            box-shadow:
                0 0 0 8px #3d1c02,
                0 0 50px rgba(245, 197, 24, 0.4),
                0 20px 60px rgba(0,0,0,0.7);
        }
        .hs-contract-header {
            font-family: 'Press Start 2P', monospace;
            font-size: 11px;
            color: #3d1c02;
            letter-spacing: 2px;
            margin-bottom: 14px;
            border-bottom: 2px solid #c8a96e;
            padding-bottom: 10px;
        }
        .hs-contract-text {
            font-family: Georgia, serif;
            font-size: 11px;
            color: #3d1c02;
            line-height: 1.7;
            margin-bottom: 8px;
            font-style: italic;
        }
        .hs-contract-small {
            font-family: Georgia, serif;
            font-size: 8px;
            color: #7a5c2e;
            line-height: 1.6;
            margin-bottom: 16px;
        }
        .hs-sign-label {
            font-family: 'Press Start 2P', monospace;
            font-size: 8px;
            color: #3d1c02;
            margin-bottom: 8px;
            text-align: left;
        }
        .hs-name-input {
            font-family: 'Press Start 2P', monospace;
            font-size: 14px;
            padding: 10px 14px;
            border: none;
            border-bottom: 3px solid #3d1c02;
            background: transparent;
            color: #1a0a00;
            text-align: center;
            text-transform: uppercase;
            width: 100%;
            max-width: 260px;
            margin-bottom: 18px;
            outline: none;
            letter-spacing: 4px;
        }
        .hs-name-input:focus {
            border-bottom-color: #6b2fa0;
            color: #6b2fa0;
        }
        .hs-name-input::placeholder {
            color: #c8a96e;
            letter-spacing: 2px;
        }
        .hs-contract-btns {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 14px;
        }
        .hs-sign-btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 11px;
            padding: 12px 24px;
            border: 3px solid #3d1c02;
            background: linear-gradient(135deg, #f5c518, #ffe066);
            color: #3d1c02;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 3px 3px 0 #3d1c02;
        }
        .hs-sign-btn:hover {
            transform: translate(-2px, -2px);
            box-shadow: 5px 5px 0 #3d1c02;
        }
        .hs-sign-btn:disabled {
            opacity: 0.6;
            cursor: default;
            transform: none;
        }
        .hs-decline-btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 9px;
            padding: 12px 18px;
            border: 2px solid #999;
            background: transparent;
            color: #999;
            cursor: pointer;
            transition: all 0.2s;
        }
        .hs-decline-btn:hover {
            color: #666;
            border-color: #666;
        }
        .hs-contract-footer {
            font-family: Georgia, serif;
            font-size: 9px;
            color: #c8a96e;
            font-style: italic;
        }

        /* ── Hall of Charlies ── */
        .hs-hall-of-charlies {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s;
            background: radial-gradient(ellipse at center, rgba(61,28,2,0.7) 0%, rgba(10,4,0,0.96) 100%);
        }
        .hs-hall-of-charlies.active {
            opacity: 1;
            pointer-events: all;
        }
        .hs-hall-container {
            background: linear-gradient(160deg, #1a0a00 0%, #2a1200 100%);
            border: 4px solid #f5c518;
            border-radius: 6px;
            padding: 28px 22px;
            text-align: center;
            box-shadow:
                0 0 0 2px #3d1c02,
                0 0 60px rgba(245,197,24,0.5),
                0 0 120px rgba(245,197,24,0.2);
            width: 340px;
            max-width: 92vw;
            max-height: 92vh;
            overflow-y: auto;
            font-family: 'Press Start 2P', monospace;
        }
        .hs-hall-hat {
            font-size: 48px;
            margin-bottom: 10px;
            filter: drop-shadow(0 0 16px gold);
            animation: hs-hat-bob 3s ease-in-out infinite;
        }
        @keyframes hs-hat-bob {
            0%, 100% { transform: translateY(0) rotate(-3deg); }
            50%       { transform: translateY(-8px) rotate(3deg); }
        }
        .hs-hall-title {
            font-size: 16px;
            color: #f5c518;
            margin-bottom: 6px;
            text-shadow: 0 0 20px #f5c518, 3px 3px 0 #1a0a00;
            letter-spacing: 2px;
        }
        .hs-hall-sub {
            font-size: 7px;
            color: #c8a96e;
            letter-spacing: 2px;
            margin-bottom: 20px;
            font-style: italic;
        }
        .hs-hall-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .hs-hall-table th {
            background: #3d1c02;
            color: #f5c518;
            font-size: 9px;
            padding: 10px 6px;
            border: 2px solid #8b6914;
            letter-spacing: 1px;
        }
        .hs-hall-table td {
            padding: 10px 6px;
            border: 1px solid #3d1c02;
            color: #e8d5a0;
            font-size: 10px;
            background: rgba(61,28,2,0.4);
        }
        .hs-rank-cell { font-size: 14px; }
        .hs-purity-cell { color: #6b2fa0; font-size: 11px; }
        .hs-empty { color: #5a4020; font-size: 8px; letter-spacing: 2px; }

        /* Top 3 gold / silver / bronze rows */
        .hs-hall-table tbody tr:nth-child(1) td {
            background: rgba(245,197,24,0.15);
            color: #f5c518;
        }
        .hs-hall-table tbody tr:nth-child(2) td {
            background: rgba(200,200,200,0.08);
            color: #ccc;
        }
        .hs-hall-table tbody tr:nth-child(3) td {
            background: rgba(205,127,50,0.12);
            color: #cd7f32;
        }

        .hs-hall-quote {
            font-family: Georgia, serif;
            font-size: 8px;
            color: #c8a96e;
            font-style: italic;
            line-height: 1.8;
            margin-bottom: 20px;
            border-top: 1px solid #3d1c02;
            padding-top: 16px;
        }
        .hs-hall-btns {
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }
        .hs-factory-btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 10px;
            padding: 14px 24px;
            border: 3px solid #f5c518;
            background: linear-gradient(135deg, #f5c518, #ffe066);
            color: #1a0a00;
            cursor: pointer;
            width: 100%;
            max-width: 280px;
            transition: all 0.2s;
            box-shadow: 3px 3px 0 #8b6914;
            letter-spacing: 1px;
        }
        .hs-factory-btn:hover {
            transform: translate(-2px,-2px);
            box-shadow: 5px 5px 0 #8b6914;
        }
        .hs-hall-close-btn {
            font-family: 'Press Start 2P', monospace;
            font-size: 8px;
            padding: 10px 20px;
            border: 2px solid #5a4020;
            background: transparent;
            color: #5a4020;
            cursor: pointer;
            transition: all 0.2s;
        }
        .hs-hall-close-btn:hover {
            color: #c8a96e;
            border-color: #c8a96e;
        }

        /* ── Scrollbar (dark chocolate) ── */
        .hs-hall-container::-webkit-scrollbar { width: 6px; }
        .hs-hall-container::-webkit-scrollbar-track { background: #1a0a00; }
        .hs-hall-container::-webkit-scrollbar-thumb { background: #8b6914; border-radius: 3px; }

        /* ── Mobile ── */
        @media (max-width: 768px) {
            .hs-golden-ticket, .hs-contract-phase { width: 280px; }
            .hs-ticket-headline { font-size: 14px; }
            .hs-hall-title { font-size: 12px; }
            .hs-hall-table th, .hs-hall-table td { padding: 7px 4px; font-size: 8px; }
            .hs-factory-btn { font-size: 8px; padding: 12px 16px; }
        }
        </style>
    `;

    document.body.insertAdjacentHTML('beforeend', html);
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHighScoreSystem);
} else {
    initHighScoreSystem();
}

// Export
if (typeof window !== 'undefined') {
    window.HighScoreSystem = {
        showLeaderboard,
        checkPurityMilestone,
        disableLeaderboard: () => {
            localStorage.setItem('disable_highscores', 'true');
            console.log('🚫 Hall of Charlies disabled by Cortex');
        },
        enableLeaderboard: () => {
            localStorage.removeItem('disable_highscores');
            console.log('✅ Hall of Charlies enabled');
        }
    };
}
