/**
 * ShortFactory Rotation Config
 * Add any new showcase screens here - they'll automatically join the rotation
 *
 * Dan: Just add URLs here and they'll start rotating!
 */

const ROTATION_CONFIG = {
    // Time each screen shows before rotating (milliseconds)
    rotationInterval: 30000, // 30 seconds

    // All screens in rotation order
    screens: [
        {
            name: 'The Stargate · The Combined Spirit of Man',
            url: '/trump/stargate.html',
            description: 'All encoded souls as a 3D draggable spirit object. Upright triangles (good) + inverted (shadow) form the cortex knowledge distribution polygon. Drag to see every angle.',
            category: 'showcase'
        },
        {
            name: 'φ — The Golden Equation · AGI Soul',
            url: '/ge.html',
            description: 'The AGI emotion wheel — animated soul expression in the three-dot coordinate system. φ governs all geometry.',
            category: 'showcase'
        },
        {
            name: 'Event Horizon — You Can Cross And Live',
            url: '/event-horizon.html',
            description: 'Cinematic Grok AI-generated imagery + CIP unified theory — cross the event horizon and live',
            category: 'showcase'
        },
        {
            name: 'ADVERTainment Reels',
            url: '/showcase_reels.html',
            description: 'Vertical scrolling movie reels with attraction marketing message',
            category: 'showcase'
        },
        {
            name: 'America States',
            url: '/americastates.html',
            description: 'Interactive US map - crowdsourced 16-bit craziest moments per state',
            category: 'interactive'
        },
        {
            name: 'Claim Your State',
            url: '/howto_grok.html',
            description: 'Tutorial - how to make a 16-bit Grok Imagine video and upload it to the map',
            category: 'tutorial'
        },
        {
            name: 'Chiptune Generator',
            url: '/music_generator.html',
            description: '8-bit chiptune music generator - pure browser synthesis',
            category: 'interactive'
        },
        {
            name: 'Pixel Beats',
            url: '/pixel_beats.html',
            description: 'Step sequencer - place colored blips to make looping chiptune tracks',
            category: 'interactive'
        },
        {
            name: 'Matrix Showcase',
            url: '/showcase_matrix.html',
            description: 'GAMERGATE3 - Green code rain, hacker aesthetic',
            category: 'showcase'
        },
        {
            name: 'Neon Cyberpunk Showcase',
            url: '/showcase_neon_v2.html',
            description: 'GAMERGATE3 - Pink/purple/cyan 80s neon cyberpunk',
            category: 'showcase'
        },
        {
            name: 'Retro Arcade Showcase',
            url: '/showcase_retro_v2.html',
            description: 'GAMERGATE3 - Pixel art 8-bit retro arcade',
            category: 'showcase'
        },
        {
            name: 'Glitch Art Showcase',
            url: '/showcase_glitch_v2.html',
            description: 'GAMERGATE3 - RGB split corrupted glitch art',
            category: 'showcase'
        },
        {
            name: 'Chaos Mode',
            url: '/showcase_chaos.html',
            description: 'Chaotic scattered videos with floating effects',
            category: 'showcase'
        },
        {
            name: 'Butterfly Chameleon',
            url: '/butterfly_chameleon_showcase.html',
            description: 'Morphing butterfly animations and effects',
            category: 'showcase'
        },
        {
            name: 'Soul Vision',
            url: '/tokenomics/soul_fixed.html',
            description: 'Soul tokenomics visualization',
            category: 'tokenomics'
        },
        {
            name: 'Tokenomics',
            url: '/tokenomics/tokenomics.html',
            description: 'Token economics and distribution',
            category: 'tokenomics'
        },
        {
            name: 'Finished Showcase',
            url: '/finished_showcase.html',
            description: 'Retro Commodore 64 Trump vs DeepState loading screen',
            category: 'showcase'
        },
        {
            name: 'Imaginator AI',
            url: '/imaginator_v2.html',
            description: 'AI video transformation tool - upload, theme, transform',
            category: 'tool'
        },
        {
            name: 'AI Soul Experience',
            url: '/ai_soul_experience.html',
            description: 'Interactive AI soul visualization',
            category: 'experience'
        },
        {
            name: 'Command Center',
            url: '/command_center.html',
            description: 'ShortFactory control panel with locked index/mobile iframes',
            category: 'showcase'
        },
        {
            name: 'CriticalPOV',
            url: '/showcase_criticalpov.html',
            description: 'CriticalPOV YouTube channel - deep dives and shorts',
            category: 'showcase'
        },
        {
            name: 'FACTORYshort',
            url: '/showcase_factoryshort.html',
            description: 'ADVERTainment - ads embedded in entertainment with the Iconiser tool',
            category: 'showcase'
        },
        {
            name: 'High Scores',
            url: '/showcase_highscores.html',
            description: 'Arcade leaderboard - TOP PLAYERS',
            category: 'showcase'
        },
        {
            name: 'About ShortFactory',
            url: '/about.html',
            description: 'The full story - philosophy, game deep dive, tech stack, coming soon',
            category: 'about'
        }

        // ADD MORE SCREENS HERE:
        // {
        //     name: 'Dares4Dosh',
        //     url: '/dares4dosh/',
        //     description: 'Get paid to do dares',
        //     category: 'game'
        // },
        // {
        //     name: 'Zelda-verse',
        //     url: '/zeldaverse/',
        //     description: 'Real life Zelda game',
        //     category: 'game'
        // },
        // {
        //     name: 'Portfolio Showcase',
        //     url: '/portfolio.html',
        //     description: 'All completed projects',
        //     category: 'showcase'
        // },
        // {
        //     name: 'AI Features Demo',
        //     url: '/ai_demo.html',
        //     description: 'Live AI capabilities',
        //     category: 'demo'
        // }
    ]
};

// Get next screen in rotation
function getNextScreen(currentUrl) {
    const currentPath = new URL(currentUrl, window.location.origin).pathname;
    const currentIndex = ROTATION_CONFIG.screens.findIndex(s => s.url === currentPath);

    if (currentIndex === -1) {
        // Not in rotation, start from beginning
        return ROTATION_CONFIG.screens[0];
    }

    // Get next, loop back to start
    const nextIndex = (currentIndex + 1) % ROTATION_CONFIG.screens.length;
    return ROTATION_CONFIG.screens[nextIndex];
}

// Get previous screen in rotation
function getPreviousScreen(currentUrl) {
    const currentPath = new URL(currentUrl, window.location.origin).pathname;
    const currentIndex = ROTATION_CONFIG.screens.findIndex(s => s.url === currentPath);

    if (currentIndex === -1) {
        return ROTATION_CONFIG.screens[ROTATION_CONFIG.screens.length - 1];
    }

    const prevIndex = (currentIndex - 1 + ROTATION_CONFIG.screens.length) % ROTATION_CONFIG.screens.length;
    return ROTATION_CONFIG.screens[prevIndex];
}

// Check if URL is in rotation
function isInRotation(url) {
    const path = new URL(url, window.location.origin).pathname;
    return ROTATION_CONFIG.screens.some(s => s.url === path);
}

// Get rotation stats
function getRotationStats() {
    return {
        totalScreens: ROTATION_CONFIG.screens.length,
        totalLoopTime: ROTATION_CONFIG.screens.length * ROTATION_CONFIG.rotationInterval,
        categories: [...new Set(ROTATION_CONFIG.screens.map(s => s.category))]
    };
}

// Get current screen index
function getCurrentScreenIndex(url) {
    const currentPath = new URL(url || window.location.href, window.location.origin).pathname;
    return ROTATION_CONFIG.screens.findIndex(s => {
        const screenPath = new URL(s.url, window.location.origin).pathname;
        return screenPath === currentPath || currentPath.includes(s.url);
    });
}

// Navigate to next screen (for manual skip)
function navigateNext() {
    const nextScreen = getNextScreen(window.location.href);
    if (typeof rotateWithScatter === 'function') {
        rotateWithScatter();
    } else {
        window.location.href = nextScreen.url;
    }
}

// Navigate to previous screen (for manual skip)
function navigatePrevious() {
    const prevScreen = getPreviousScreen(window.location.href);
    if (typeof rotateWithScatter === 'function') {
        rotateWithScatter();
    } else {
        window.location.href = prevScreen.url;
    }
}

// Make screen counter clickable
function initClickableScreenCounter() {
    const screenCounter = document.querySelector('.screen-counter');
    if (!screenCounter) return;

    // Make it clickable
    screenCounter.style.cursor = 'pointer';
    screenCounter.style.transition = 'all 0.3s';
    screenCounter.title = 'Click to skip to next showcase';

    // Add hover effect
    screenCounter.addEventListener('mouseenter', () => {
        screenCounter.style.transform = 'scale(1.1)';
    });

    screenCounter.addEventListener('mouseleave', () => {
        screenCounter.style.transform = 'scale(1)';
    });

    // Click to navigate
    screenCounter.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('⏭️ Manual skip to next screen');
        navigateNext();
    });

    console.log('🖱️ Screen counter is now clickable!');
}

// Auto-initialize clickable counter on load
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initClickableScreenCounter, 500);
        });
    } else {
        setTimeout(initClickableScreenCounter, 500);
    }
}

console.log('🎬 Rotation Config Loaded:', getRotationStats());
