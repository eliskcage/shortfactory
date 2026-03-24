/**
 * Cortex AI Command System
 * Allows Cortex (Grok chatbot) to control game features
 */

(function() {
    'use strict';

    // Cortex command handler
    window.CortexCommands = {
        // Disable high score leaderboard
        disableLeaderboard: function() {
            localStorage.setItem('disable_highscores', 'true');
            console.log('✅ Leaderboard disabled by Cortex');

            // Show confirmation to user
            showCortexNotification('🏆 Leaderboard Disabled', 'You can now play without high score interruptions!');

            return { success: true, message: 'Leaderboard disabled' };
        },

        // Re-enable high score leaderboard
        enableLeaderboard: function() {
            localStorage.removeItem('disable_highscores');
            console.log('✅ Leaderboard enabled by Cortex');

            showCortexNotification('🏆 Leaderboard Enabled', 'High scores are now active!');

            return { success: true, message: 'Leaderboard enabled' };
        },

        // Check leaderboard status
        checkLeaderboardStatus: function() {
            const disabled = localStorage.getItem('disable_highscores') === 'true';
            return {
                success: true,
                disabled: disabled,
                message: disabled ? 'Leaderboard is currently disabled' : 'Leaderboard is active'
            };
        },

        // View current leaderboard
        viewLeaderboard: function() {
            if (typeof window.HighScoreSystem !== 'undefined') {
                window.HighScoreSystem.showLeaderboard();
                return { success: true, message: 'Showing leaderboard' };
            }
            return { success: false, message: 'Leaderboard not available on this page' };
        },

        // Get help
        help: function() {
            const commands = [
                'CortexCommands.disableLeaderboard() - Disable high score popups',
                'CortexCommands.enableLeaderboard() - Re-enable high scores',
                'CortexCommands.checkLeaderboardStatus() - Check if leaderboard is on/off',
                'CortexCommands.viewLeaderboard() - View current top scores'
            ];
            console.log('🤖 Cortex Commands:', commands);
            return { success: true, commands: commands };
        }
    };

    // Notification system
    function showCortexNotification(title, message) {
        const notification = document.createElement('div');
        notification.className = 'cortex-notification';
        notification.innerHTML = `
            <div class="cortex-notif-title">${title}</div>
            <div class="cortex-notif-message">${message}</div>
        `;

        // Add styles if not already present
        if (!document.getElementById('cortex-notif-styles')) {
            const styles = document.createElement('style');
            styles.id = 'cortex-notif-styles';
            styles.textContent = `
                .cortex-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 999999;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #fff;
                    padding: 20px 25px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.5);
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    font-family: 'Press Start 2P', monospace;
                    max-width: 350px;
                    animation: cortexSlideIn 0.5s ease-out;
                }

                @keyframes cortexSlideIn {
                    from {
                        transform: translateX(400px);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                .cortex-notif-title {
                    font-size: 0.8rem;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 0 rgba(0,0,0,0.3);
                }

                .cortex-notif-message {
                    font-size: 0.6rem;
                    line-height: 1.6;
                    color: rgba(255, 255, 255, 0.9);
                }

                @media (max-width: 768px) {
                    .cortex-notification {
                        top: 10px;
                        right: 10px;
                        left: 10px;
                        max-width: none;
                    }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);

        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'cortexSlideIn 0.5s ease-out reverse';
            setTimeout(() => notification.remove(), 500);
        }, 4000);
    }

    // Listen for Cortex messages (for future integration)
    window.addEventListener('message', (event) => {
        if (event.origin !== window.location.origin) return;
        if (event.data && event.data.type === 'cortex-command') {
            const { command, args } = event.data;
            if (window.CortexCommands[command]) {
                const result = window.CortexCommands[command](...(args || []));
                console.log('🤖 Cortex executed:', command, result);
            }
        }
    });

    console.log('🤖 Cortex Command System loaded');
    console.log('💡 Type CortexCommands.help() for available commands');
})();
