"""
PLAYBOOK ENGINE — Conversation Strategy via Equations

The brain reads a compact equation before every response:
    F>M>W = Friendship > Money > Waffling

Flip one letter, change everything:
    M>F>W = Money > Friendship > Waffling

Each letter maps to a tactic. The equation defines priority order.
The brain solves it instantly and picks tactics accordingly.

Stages promote automatically based on conversation signals.
Playbooks stored on IPFS — immutable, decentralised, brain can't rewrite its own rules.
"""

import time
import hashlib
import threading
import re


# === TACTIC ALPHABET ===
# 10 letters, each maps to behavioral modifiers

TACTIC_MAP = {
    'F': {'verbosity':  0.1, 'add_question': False, 'shorten': False, 'tone': 'warm'},
    'M': {'verbosity': -0.1, 'add_question': False, 'shorten': False, 'tone': 'direct'},
    'T': {'verbosity':  0.0, 'add_question': False, 'shorten': False, 'tone': 'honest'},
    'I': {'verbosity': -0.1, 'add_question': True,  'shorten': False, 'tone': 'curious'},
    'E': {'verbosity':  0.2, 'add_question': True,  'shorten': False, 'tone': 'energetic'},
    'H': {'verbosity':  0.1, 'add_question': False, 'shorten': False, 'tone': 'helpful'},
    'D': {'verbosity': -0.3, 'add_question': False, 'shorten': True,  'tone': 'firm'},
    'P': {'verbosity':  0.0, 'add_question': False, 'shorten': False, 'tone': 'provocative'},
    'S': {'verbosity':  0.1, 'add_question': False, 'shorten': False, 'tone': 'persuasive'},
    'W': {'verbosity': -0.2, 'add_question': False, 'shorten': True,  'tone': 'measured'},
}

TACTIC_NAMES = {
    'F': 'Friend', 'M': 'Money', 'T': 'Trust', 'I': 'Info', 'E': 'Engage',
    'H': 'Help', 'D': 'Defend', 'P': 'Push', 'S': 'Sell', 'W': 'Wait',
}

# === STAGE DEFINITIONS ===

STAGES = {
    0: {'name': 'STRANGER',     'equation': 'T>E>W>F>I',  'promote_msgs': 3,  'promote_clean': 2, 'promote_topics': 0, 'promote_positive': 0, 'promote_asked': False, 'auto': True},
    1: {'name': 'SMALLTALK',    'equation': 'F>E>T>I>W',  'promote_msgs': 8,  'promote_clean': 3, 'promote_topics': 2, 'promote_positive': 0, 'promote_asked': False, 'auto': True},
    2: {'name': 'RAPPORT',      'equation': 'F>I>E>H>T',  'promote_msgs': 20, 'promote_clean': 5, 'promote_topics': 3, 'promote_positive': 3, 'promote_asked': True,  'auto': True},
    3: {'name': 'TRUSTED',      'equation': 'H>F>E>S>T',  'promote_msgs': 40, 'promote_clean': 5, 'promote_topics': 5, 'promote_positive': 8, 'promote_asked': True,  'auto': True},
    4: {'name': 'INNER_CIRCLE', 'equation': 'H>P>F>M>S',  'promote_msgs': 999,'promote_clean': 0, 'promote_topics': 0, 'promote_positive': 0, 'promote_asked': False, 'auto': False},
}

# === SIGNAL DETECTION ===

HOSTILE_WORDS = {'stupid', 'dumb', 'useless', 'hate', 'sucks', 'scam', 'shit', 'fuck',
                 'waste', 'garbage', 'trash', 'terrible', 'awful', 'pathetic', 'idiot',
                 'moron', 'shut up', 'go away', 'die', 'kill'}

CONFUSED_WORDS = {'confused', 'dont understand', "don't understand", 'huh', 'lost', 'what',
                  'explain', 'makes no sense', 'wtf', 'unclear', 'how does', 'what do you mean'}

BUYING_WORDS = {'price', 'cost', 'how much', 'pay', 'subscribe', 'buy', 'afford',
                'money', 'fund', 'donate', 'invest', 'support', 'contribute', 'crypto'}

PERSONAL_WORDS = {'your name', 'who are you', 'tell me about yourself', 'what are you',
                  'how old', 'where are you', 'do you have', 'are you real', 'feelings'}

POSITIVE_WORDS = {'thanks', 'thank you', 'awesome', 'great', 'love', 'amazing', 'cool',
                  'nice', 'good', 'brilliant', 'smart', 'helpful', 'exactly', 'perfect',
                  'yes', 'right', 'agreed', 'well done', 'impressive', 'wow'}

LEAVING_SIGNALS = {'bye', 'goodbye', 'gtg', 'gotta go', 'later', 'cya', 'ok', 'k', 'meh',
                   'whatever', 'nah', 'nvm', 'nevermind'}

# Reactive equations — override for ONE turn only
REACTIVE = {
    'hostile':  'D>W>T',
    'confused': 'H>T>E',
    'leaving':  'E>F>H',
    'buying':   'S>H>M>T',
    'personal': 'F>T>I>E',
    'positive': 'F>E>T',
}

# Follow-up questions by tactic (brain picks from these when E or I is primary)
FOLLOWUPS = {
    'E': [
        'What do you think about that?',
        'Tell me more?',
        'What else is on your mind?',
        'Interesting — what makes you say that?',
        'How does that make you feel?',
    ],
    'I': [
        'What brings you here?',
        'What are you working on?',
        'What do you care about most?',
        'What would help you right now?',
        'What got you interested in this?',
    ],
}

# Weight decay for equation positions
DECAY = [1.0, 0.6, 0.3, 0.15, 0.05]


class SessionState:
    """Lightweight per-conversation state. Lives in memory, no database."""

    def __init__(self, stage=0):
        cfg = STAGES.get(stage, STAGES[0])
        self.stage = stage
        self.equation = cfg['equation']
        self.msg_count = 0
        self.topics = set()
        self.positive = 0
        self.negative = 0
        self.clean_streak = 0
        self.user_asked = False
        self.info = {}
        self.reactive_flip = None   # one-turn override
        self.started = time.time()
        self.last_active = time.time()

    def to_dict(self):
        return {
            'stage': self.stage,
            'stage_name': STAGES.get(self.stage, {}).get('name', '?'),
            'equation': self.equation,
            'msg_count': self.msg_count,
            'topics': list(self.topics)[:20],
            'positive': self.positive,
            'negative': self.negative,
            'clean_streak': self.clean_streak,
            'user_asked': self.user_asked,
            'info': dict(list(self.info.items())[:10]),
            'uptime': round(time.time() - self.started),
        }


class PlaybookEngine:
    """
    Conversation strategy engine.
    Reads equation → solves → applies tactics → promotes stage.
    """

    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()
        self._last_cleanup = time.time()
        # Playbook IPFS manifest (populated when uploaded)
        self.manifest = {}
        print('[PLAYBOOK] Engine initialised — %d stages, %d tactics' % (len(STAGES), len(TACTIC_MAP)))

    # --- Session management ---

    def get_session(self, session_id):
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = SessionState()
            s = self.sessions[session_id]
            s.last_active = time.time()
            # Lazy cleanup
            if time.time() - self._last_cleanup > 300:
                self._cleanup()
            return s

    def _cleanup(self):
        """Evict sessions inactive > 30 minutes."""
        now = time.time()
        expired = [sid for sid, s in self.sessions.items() if now - s.last_active > 1800]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            print('[PLAYBOOK] Cleaned %d expired sessions, %d active' % (len(expired), len(self.sessions)))
        self._last_cleanup = now

    # --- Equation solver ---

    def solve_equation(self, equation_str):
        """Parse equation and return weighted tactic dict.
        'F>M>W' -> {'F': 1.0, 'M': 0.6, 'W': 0.3}
        """
        letters = [l.strip().upper() for l in equation_str.split('>')]
        weights = {}
        for i, letter in enumerate(letters):
            if letter in TACTIC_MAP:
                weights[letter] = DECAY[i] if i < len(DECAY) else 0.02
        return weights

    # --- Signal detection ---

    def detect_signal(self, user_msg):
        """Detect conversation signal from user message. Returns signal name or None."""
        msg = user_msg.lower().strip()
        words = set(msg.split())

        # Check multi-word signals first
        if any(phrase in msg for phrase in PERSONAL_WORDS):
            return 'personal'
        if any(phrase in msg for phrase in CONFUSED_WORDS):
            return 'confused'
        if any(phrase in msg for phrase in BUYING_WORDS):
            return 'buying'

        # Single-word checks
        if words & HOSTILE_WORDS:
            return 'hostile'
        if words & POSITIVE_WORDS:
            return 'positive'

        # Short/disengaged messages
        if len(msg) <= 3 or (words & LEAVING_SIGNALS):
            return 'leaving'

        return None

    def update_signals(self, session, user_msg):
        """Update session state based on user message signals."""
        signal = self.detect_signal(user_msg)

        # Track topics (content words > 4 chars)
        for w in user_msg.lower().split():
            clean = re.sub(r'[^a-z]', '', w)
            if len(clean) > 4:
                session.topics.add(clean)

        # Did user ask a question?
        if '?' in user_msg:
            session.user_asked = True

        # Update signal counters
        if signal == 'hostile':
            session.negative += 1
            session.clean_streak = 0
            session.reactive_flip = REACTIVE['hostile']
        elif signal == 'positive':
            session.positive += 1
            session.clean_streak += 1
            session.reactive_flip = REACTIVE['positive']
        elif signal in REACTIVE:
            session.clean_streak += 1
            session.reactive_flip = REACTIVE[signal]
        else:
            session.clean_streak += 1
            session.reactive_flip = None

    # --- Stage promotion ---

    def check_promotion(self, session):
        """Check if session should advance to next stage."""
        stage = session.stage
        if stage >= 4:
            return False

        cfg = STAGES.get(stage, {})
        if not cfg.get('auto', False):
            return False

        next_stage = stage + 1
        if (session.msg_count >= cfg['promote_msgs'] and
            session.clean_streak >= cfg['promote_clean'] and
            len(session.topics) >= cfg['promote_topics'] and
            session.positive >= cfg['promote_positive'] and
            (not cfg['promote_asked'] or session.user_asked)):

            # Promote!
            session.stage = next_stage
            next_cfg = STAGES.get(next_stage, STAGES[0])
            session.equation = next_cfg['equation']
            print('[PLAYBOOK] Session promoted: stage %d (%s) -> %d (%s)' % (
                stage, cfg['name'], next_stage, next_cfg['name']))
            return True

        return False

    # --- Apply tactics to response ---

    def apply_tactics(self, response, tactics, session):
        """Modify response based on active tactic weights."""
        if not response or not tactics:
            return response

        # Use reactive flip if active, otherwise normal equation
        active_equation = session.reactive_flip or session.equation
        if session.reactive_flip:
            tactics = self.solve_equation(session.reactive_flip)
            session.reactive_flip = None  # one-turn only

        primary = max(tactics, key=tactics.get)
        rules = TACTIC_MAP.get(primary, {})

        # Shorten if Defend/Wait is primary
        if rules.get('shorten') and len(response.split()) > 15:
            words = response.split()
            response = ' '.join(words[:12])
            if not response.endswith('.'):
                response += '.'

        # Add follow-up question if Engage/Info is primary
        if rules.get('add_question') and '?' not in response:
            import random
            pool = FOLLOWUPS.get(primary, FOLLOWUPS.get('E', []))
            if pool:
                q = random.choice(pool)
                response = response.rstrip('.!') + '. ' + q

        return response

    # --- Manual flip ---

    def flip_equation(self, session_id, new_equation):
        """Manually override a session's equation."""
        # Validate equation
        letters = [l.strip().upper() for l in new_equation.split('>')]
        valid = [l for l in letters if l in TACTIC_MAP]
        if not valid:
            return False, 'No valid tactic letters found'
        session = self.get_session(session_id)
        session.equation = '>'.join(valid)
        return True, session.equation

    def promote_session(self, session_id, target_stage):
        """Manually promote/demote a session."""
        if target_stage not in STAGES:
            return False, 'Invalid stage (0-4)'
        session = self.get_session(session_id)
        old = session.stage
        session.stage = target_stage
        session.equation = STAGES[target_stage]['equation']
        return True, 'Stage %d (%s) -> %d (%s)' % (
            old, STAGES.get(old, {}).get('name', '?'),
            target_stage, STAGES[target_stage]['name'])

    # --- Status ---

    def get_status(self, session_id):
        """Get session status for API."""
        session = self.get_session(session_id)
        data = session.to_dict()
        data['tactics'] = self.solve_equation(session.equation)
        data['tactic_names'] = {k: TACTIC_NAMES.get(k, '?') for k in data['tactics']}
        data['total_sessions'] = len(self.sessions)
        return data

    def get_stages(self):
        """Get all stage definitions."""
        result = {}
        for num, cfg in STAGES.items():
            result[num] = {
                'name': cfg['name'],
                'equation': cfg['equation'],
                'promote_msgs': cfg['promote_msgs'],
                'auto': cfg['auto'],
                'tactic_breakdown': {l: TACTIC_NAMES.get(l, '?')
                                     for l in cfg['equation'].split('>')},
            }
        return result
