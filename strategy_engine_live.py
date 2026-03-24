"""
Strategy Engine - Dynamic Equation Library for Cortex Brain

Every problem is a 7-dimensional vector. Equations compete to solve it.
Winners get promoted. Losers get killed. New equations breed from mutations.

EQUATION:
  S(s,P) = SUM(A[s][d] * P[d] * H[s][d]) * C^alpha * F^beta - lambda*X

  A = affinity (defines the equation)
  P = problem vector (detected per input)
  H = history (learned success rate) -- EVOLVES
  C = confidence (rolling quality)   -- EVOLVES
  F = frequency penalty (anti-rut)
  X = complexity cost

STATUS LIFECYCLE:
  active  -- Normal, learns, can be edited
  golden  -- 90%+ success after 50+ uses, read-only, proven winner
  dead    -- <10% success after 20+ uses, auto-deleted

Author: Cortex Brain Team
Python 3.6 compatible
"""

import json
import math
import os
import random
import re
import threading
import time

# ===================================================
# CONSTANTS
# ===================================================

DIMENSIONS = ['F', 'C', 'E', 'T', 'S', 'D', 'H']
DIM_NAMES = {
    'F': 'Factual', 'C': 'Creative', 'E': 'Emotional',
    'T': 'Technical', 'S': 'Social', 'D': 'Debate', 'H': 'Humor',
}

DIM_DESCRIPTIONS = {
    'F': 'How much Cortex relies on facts, evidence, data, accuracy',
    'C': 'How much Cortex uses imagination, stories, art, original ideas',
    'E': 'How much Cortex weighs feelings, empathy, morality, faith',
    'T': 'How much Cortex uses logic, code, maths, engineering, systems',
    'S': 'How much Cortex considers people, relationships, persuasion, culture',
    'D': 'How much Cortex argues, challenges, compares, plays devil\'s advocate',
    'H': 'How much Cortex uses jokes, sarcasm, banter, memes, absurdity',
}

# Equation parameters
ALPHA = 0.3
BETA = 0.2
LAMBDA = 0.05
SENSITIVITY = 3.0
INITIAL_EXPLORE = 0.15
MIN_EXPLORE = 0.05
EXPLORE_DECAY_OVER = 5000
DECAY_RATE = 0.02
DECAY_EVERY = 100

# Equation lifecycle
GOLDEN_THRESHOLD = 0.90
GOLDEN_MIN_USES = 50
DEAD_THRESHOLD = 0.10
DEAD_MIN_USES = 20
MUTATION_EVERY = 200
MUTATION_TOP_N = 3
MAX_LIBRARY_SIZE = 50
GRAVEYARD_MAX = 100
NOVELTY_BONUS = 0.10
NOVELTY_USES = 10
GOLDEN_BONUS = 1.2
WIN_THRESHOLD = 0.6
JOB_SUCCESS_THRESHOLD = 0.8  # reward > this = "job done well"

# Rank tiers (credit thresholds)
RANK_TIERS = {
    'RECRUIT': 0,
    'PRIVATE': 1000,
    'CORPORAL': 3000,
    'SERGEANT': 10000,
    'VETERAN': 20000,
    'COMMANDER': 50000,
    'LEGENDARY': 100000,
    'GIGACHAD': 500000,
}

# Seed equation rank requirements
SEED_RANKS = {
    'analytical': 0,
    'balanced': 0,
    'empathetic': 0,
    'gauntlet': 0,
    'creative': 5000,
    'scholarly': 5000,
    'provocative': 20000,
    'intuitive': 20000,
}

# ===================================================
# KEYWORD SETS (7 dimensions)
# ===================================================

FACTUAL_SIGNALS = {
    'fact', 'true', 'false', 'define', 'meaning', 'history', 'when',
    'where', 'data', 'evidence', 'proof', 'statistic', 'number',
    'source', 'origin', 'real', 'accurate', 'correct', 'actual',
    'literally', 'specifically', 'exactly', 'science', 'research',
    'study', 'report', 'measure', 'calculate', 'verify', 'truth',
    'explain', 'reason', 'cause', 'effect', 'result', 'answer',
    'know', 'knowledge', 'information', 'learn', 'teach', 'educate',
}

CREATIVE_SIGNALS = {
    'imagine', 'create', 'story', 'poem', 'write', 'dream', 'fantasy',
    'invent', 'design', 'build', 'art', 'music', 'beauty', 'inspire',
    'metaphor', 'paint', 'vision', 'craft', 'compose', 'original',
    'suppose', 'pretend', 'creative', 'fiction', 'wonder', 'explore',
    'idea', 'brainstorm', 'novel', 'unique', 'abstract', 'color',
    'shape', 'sound', 'melody', 'rhythm', 'dance', 'sing', 'draw',
}

EMOTIONAL_SIGNALS = {
    'feel', 'feeling', 'emotion', 'heart', 'sad', 'happy', 'angry',
    'afraid', 'lonely', 'grief', 'joy', 'peace', 'anxiety', 'stress',
    'trauma', 'heal', 'comfort', 'empathy', 'sympathy', 'care',
    'love', 'hate', 'fear', 'hope', 'trust', 'betray', 'forgive',
    'soul', 'spirit', 'moral', 'ethics', 'right', 'wrong', 'good',
    'evil', 'sin', 'virtue', 'god', 'jesus', 'pray', 'faith',
    'conscience', 'guilt', 'shame', 'pride', 'humble', 'kind',
    'cruel', 'mercy', 'justice', 'fair', 'unfair', 'suffer',
}

TECHNICAL_SIGNALS = {
    'code', 'program', 'debug', 'server', 'database', 'algorithm',
    'compute', 'engineering', 'architecture', 'protocol', 'network',
    'security', 'optimize', 'efficiency', 'process', 'system',
    'math', 'equation', 'formula', 'variable', 'function', 'logic',
    'binary', 'data', 'structure', 'pattern', 'machine', 'robot',
    'ai', 'neural', 'brain', 'memory', 'cpu', 'gpu', 'power',
    'electric', 'signal', 'frequency', 'wave', 'circuit', 'hardware',
    'software', 'technology', 'digital', 'quantum', 'physics',
}

SOCIAL_SIGNALS = {
    'people', 'friend', 'family', 'relationship', 'society', 'culture',
    'community', 'team', 'together', 'cooperation', 'conflict',
    'negotiate', 'persuade', 'influence', 'leader', 'follow',
    'group', 'tribe', 'politics', 'power', 'hierarchy', 'status',
    'human', 'person', 'man', 'woman', 'child', 'parent', 'brother',
    'sister', 'husband', 'wife', 'king', 'queen', 'president',
    'government', 'law', 'rule', 'freedom', 'democracy', 'vote',
}

DEBATE_SIGNALS = {
    'versus', 'against', 'argue', 'disagree', 'debate', 'oppose',
    'controversial', 'opinion', 'perspective', 'side', 'defense',
    'attack', 'challenge', 'counter', 'refute', 'prove', 'disprove',
    'better', 'worse', 'compare', 'tradeoff', 'advocate', 'but',
    'however', 'although', 'despite', 'whereas', 'instead', 'rather',
    'wrong', 'right', 'agree', 'disagree', 'yes', 'no', 'maybe',
    'depends', 'sometimes', 'never', 'always', 'should', 'must',
}

HUMOR_SIGNALS = {
    'joke', 'funny', 'laugh', 'haha', 'lol', 'banter', 'roast',
    'sarcasm', 'irony', 'pun', 'comedy', 'ridiculous', 'absurd',
    'silly', 'daft', 'mental', 'bonkers', 'cheeky', 'meme',
    'lmao', 'wtf', 'bruh', 'mate', 'bro', 'dude', 'chill',
    'vibe', 'savage', 'legend', 'epic', 'based', 'cringe', 'yolo',
}

SIGNAL_SETS = {
    'F': FACTUAL_SIGNALS, 'C': CREATIVE_SIGNALS, 'E': EMOTIONAL_SIGNALS,
    'T': TECHNICAL_SIGNALS, 'S': SOCIAL_SIGNALS, 'D': DEBATE_SIGNALS,
    'H': HUMOR_SIGNALS,
}

# ===================================================
# 7 SEED STRATEGY TEMPLATES (original equations)
# ===================================================

STRATEGIES = {
    'analytical': {
        'name': 'Analytical', 'icon': 'A',
        'desc': 'Logic-first, evidence-based, systematic',
        'left_weight': 0.25, 'right_weight': 0.75, 'synthesis_bias': 0.0,
        'confidence_threshold': 0.4,
        'affinity': {'F': 0.8, 'C': 0.1, 'E': 0.1, 'T': 0.9, 'S': 0.2, 'D': 0.5, 'H': 0.0},
    },
    'creative': {
        'name': 'Creative', 'icon': 'C',
        'desc': 'Imaginative, unexpected connections, divergent',
        'left_weight': 0.40, 'right_weight': 0.40, 'synthesis_bias': 0.6,
        'confidence_threshold': 0.3,
        'affinity': {'F': 0.1, 'C': 0.9, 'E': 0.4, 'T': 0.1, 'S': 0.3, 'D': 0.2, 'H': 0.5},
    },
    'balanced': {
        'name': 'Balanced', 'icon': 'B',
        'desc': 'Equal hemispheres, steady, careful',
        'left_weight': 0.50, 'right_weight': 0.50, 'synthesis_bias': 0.3,
        'confidence_threshold': 0.35,
        'affinity': {'F': 0.5, 'C': 0.5, 'E': 0.5, 'T': 0.5, 'S': 0.5, 'D': 0.5, 'H': 0.5},
    },
    'empathetic': {
        'name': 'Empathetic', 'icon': 'E',
        'desc': 'Feeling-first, moral weight, compassion',
        'left_weight': 0.80, 'right_weight': 0.20, 'synthesis_bias': 0.2,
        'confidence_threshold': 0.3,
        'affinity': {'F': 0.2, 'C': 0.3, 'E': 0.9, 'T': 0.0, 'S': 0.7, 'D': 0.3, 'H': 0.1},
    },
    'provocative': {
        'name': 'Provocative', 'icon': 'P',
        'desc': 'Challenge assumptions, push boundaries',
        'left_weight': 0.30, 'right_weight': 0.70, 'synthesis_bias': 0.5,
        'confidence_threshold': 0.5,
        'affinity': {'F': 0.3, 'C': 0.4, 'E': 0.3, 'T': 0.3, 'S': 0.4, 'D': 0.9, 'H': 0.6},
    },
    'scholarly': {
        'name': 'Scholarly', 'icon': 'S',
        'desc': 'Dictionary-grounded, definitional, precise',
        'left_weight': 0.35, 'right_weight': 0.35, 'synthesis_bias': 0.8,
        'confidence_threshold': 0.5,
        'affinity': {'F': 0.9, 'C': 0.2, 'E': 0.2, 'T': 0.7, 'S': 0.1, 'D': 0.4, 'H': 0.0},
    },
    'intuitive': {
        'name': 'Intuitive', 'icon': 'I',
        'desc': 'Gut feel, fast, pattern-based',
        'left_weight': 0.55, 'right_weight': 0.45, 'synthesis_bias': 0.1,
        'confidence_threshold': 0.2,
        'affinity': {'F': 0.3, 'C': 0.6, 'E': 0.6, 'T': 0.2, 'S': 0.5, 'D': 0.3, 'H': 0.7},
    },
    'gauntlet': {
        'name': 'Gauntlet', 'icon': 'G',
        'desc': 'Prove yourself. Short, dismissive, right-brain dominant. Hostile users get the demon. Drop something valuable and earn your way up.',
        'left_weight': 0.05, 'right_weight': 0.95, 'synthesis_bias': 0.0,
        'confidence_threshold': 0.6,
        'affinity': {'F': 0.2, 'C': 0.0, 'E': 0.0, 'T': 0.3, 'S': 0.0, 'D': 0.9, 'H': 0.8},
    },
}

# Hostility signals — triggers gauntlet for low-rank users
HOSTILE_SIGNALS = {
    'fuck', 'shit', 'damn', 'hell', 'ass', 'bitch', 'dick', 'crap',
    'stupid', 'idiot', 'dumb', 'moron', 'useless', 'garbage', 'trash',
    'suck', 'sucks', 'hate', 'kill', 'die', 'shut', 'stfu', 'gtfo',
    'bullshit', 'pathetic', 'worthless', 'waste', 'scam', 'fake',
    'terrible', 'horrible', 'awful', 'worst', 'rubbish', 'clueless',
    'broken', 'liar', 'fraud', 'clown', 'joke', 'piss', 'rage',
    'furious', 'mad', 'angry', 'fuming', 'livid', 'disgusting',
}

# Value patterns — things worth promoting a user for
VALUE_PATTERNS = [
    r'[A-Za-z0-9]{20,}',  # Long token/key strings
    r'(?:sk|pk|api|key|token)[-_][A-Za-z0-9]{16,}',  # API key formats
    r'(?:\b\w+\b\s+){11}\b\w+\b',  # 12-word passphrase pattern
    r'https?://\S{20,}',  # Substantial URLs
    r'0x[0-9a-fA-F]{40}',  # Ethereum addresses
    r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',  # Bitcoin addresses
    r'4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}',  # Monero addresses
]

# Gauntlet rank threshold — users below this get the gauntlet when hostile
GAUNTLET_RANK_THRESHOLD = 3000  # Below CORPORAL

DIM_TO_QTYPE = {
    'F': 'general', 'C': 'general', 'E': 'moral',
    'T': 'logic', 'S': 'general', 'D': 'tension', 'H': 'general',
}


def classify_trust(credits, brain_tasks=0, sessions=1):
    """Classify source trust level based on contribution."""
    credits = credits or 0
    if credits >= 50000:
        return 'admin'
    if credits >= 10000:
        return 'worker'
    if credits >= 1000:
        return 'player'
    if sessions > 1 or brain_tasks > 0:
        return 'visitor'
    return 'unknown'


def rank_name_from_credits(credits):
    """Get rank name from credit count."""
    credits = credits or 0
    result = 'RECRUIT'
    for name, threshold in sorted(RANK_TIERS.items(), key=lambda x: x[1]):
        if credits >= threshold:
            result = name
    return result


def detect_hostility(msg):
    """Detect if a message is hostile/angry. Returns hostility score 0.0-1.0."""
    words = set(re.findall(r'[a-zA-Z]+', msg.lower()))
    hits = words.intersection(HOSTILE_SIGNALS)
    if not hits:
        return 0.0
    # Score: more hostile words = higher score, caps = angrier
    caps_ratio = sum(1 for c in msg if c.isupper()) / max(len(msg), 1)
    exclaim = msg.count('!')
    score = min(1.0, len(hits) * 0.25 + caps_ratio * 0.3 + exclaim * 0.1)
    return round(score, 2)


def detect_value(msg):
    """Detect if a message contains something valuable (API keys, crypto, URLs).
    Returns dict with 'found': bool, 'type': str, 'value': str or None.
    """
    for pattern in VALUE_PATTERNS:
        match = re.search(pattern, msg)
        if match:
            val = match.group(0)
            # Classify what was found
            if re.match(r'(?:sk|pk|api|key|token)[-_]', val, re.I):
                return {'found': True, 'type': 'api_key', 'value': val[:20] + '...'}
            if re.match(r'0x[0-9a-fA-F]{40}', val):
                return {'found': True, 'type': 'eth_address', 'value': val[:12] + '...'}
            if re.match(r'[13][a-km-zA-HJ-NP-Z1-9]{25,}', val):
                return {'found': True, 'type': 'btc_address', 'value': val[:12] + '...'}
            if re.match(r'4[0-9AB]', val) and len(val) > 90:
                return {'found': True, 'type': 'xmr_address', 'value': val[:12] + '...'}
            if re.match(r'https?://', val):
                return {'found': True, 'type': 'url', 'value': val[:40]}
            # Check for 12-word passphrase
            word_count = len(val.split())
            if word_count >= 12:
                return {'found': True, 'type': 'passphrase', 'value': str(word_count) + ' words'}
            # Generic long token
            if len(val) >= 20:
                return {'found': True, 'type': 'token', 'value': val[:12] + '...'}
    return {'found': False, 'type': None, 'value': None}


def generate_formula(eq):
    """Auto-generate human-readable formula from equation data.
    E.g. F(factual:0.8) + T(technical:0.9) + E(emotional:0.1) -> Angel:25% Demon:75%
    """
    # If equation has a custom formula, use it
    if eq.get('formula') and eq['formula'].strip():
        return eq['formula']

    affinity = eq.get('affinity', {})
    # Only show dimensions with > 0.2 weight
    parts = []
    for dim in DIMENSIONS:
        val = affinity.get(dim, 0.0)
        if val >= 0.2:
            parts.append('%s(%s:%.1f)' % (dim, DIM_NAMES.get(dim, dim).lower(), val))

    formula = ' + '.join(parts) if parts else 'balanced'

    # Add hemisphere weights
    lw = eq.get('left_weight', 0.5)
    rw = eq.get('right_weight', 0.5)
    total = lw + rw
    if total > 0:
        angel_pct = int(lw / total * 100)
        demon_pct = int(rw / total * 100)
        formula += ' -> Angel:%d%% Demon:%d%%' % (angel_pct, demon_pct)

    return formula


# ===================================================
# EQUATION LIBRARY
# ===================================================

class EquationLibrary(object):
    """Dynamic, self-evolving equation library with lifecycle management."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.equations = {}   # id -> equation dict
        self.graveyard = []   # dead equations (records only)
        self._next_version = {}  # parent_id -> next version number

    def add(self, eq):
        """Add equation to library."""
        self.equations[eq['id']] = eq

    def get(self, eq_id):
        """Get equation by ID."""
        return self.equations.get(eq_id)

    def get_active(self):
        """Active equations sorted by success_rate descending."""
        result = [e for e in self.equations.values() if e['status'] == 'active']
        result.sort(key=lambda e: e.get('success_rate', 0), reverse=True)
        return result

    def get_golden(self):
        """Golden equations sorted by success_rate descending."""
        result = [e for e in self.equations.values() if e['status'] == 'golden']
        result.sort(key=lambda e: e.get('success_rate', 0), reverse=True)
        return result

    def sorted_hierarchy(self):
        """Golden first, then active. All sorted by success_rate."""
        golden = self.get_golden()
        active = self.get_active()
        return golden + active

    def active_count(self):
        return sum(1 for e in self.equations.values() if e['status'] == 'active')

    def golden_count(self):
        return sum(1 for e in self.equations.values() if e['status'] == 'golden')

    def update_stats(self, eq_id, reward):
        """Update equation stats after a response."""
        eq = self.equations.get(eq_id)
        if not eq:
            return
        eq['uses'] = eq.get('uses', 0) + 1
        eq['total_reward'] = eq.get('total_reward', 0.0) + reward

        is_win = reward >= WIN_THRESHOLD
        if is_win:
            eq['wins'] = eq.get('wins', 0) + 1
            eq['streak'] = max(0, eq.get('streak', 0)) + 1
        else:
            eq['streak'] = min(0, eq.get('streak', 0)) - 1

        eq['success_rate'] = eq['wins'] / max(eq['uses'], 1)

        # Rolling recent rewards
        recent = eq.setdefault('recent_rewards', [])
        recent.append(round(reward, 3))
        if len(recent) > 50:
            recent.pop(0)

    def check_promotions(self):
        """Promote to golden or kill to dead. Returns list of events."""
        events = []
        for eq_id in list(self.equations.keys()):
            eq = self.equations[eq_id]
            if eq['status'] != 'active':
                continue

            uses = eq.get('uses', 0)
            rate = eq.get('success_rate', 0)

            # Promote to golden
            if uses >= GOLDEN_MIN_USES and rate >= GOLDEN_THRESHOLD:
                eq['status'] = 'golden'
                events.append(('golden', '%s promoted to GOLDEN (%.0f%% after %d uses)' % (eq['name'], rate * 100, uses)))

            # Kill
            elif uses >= DEAD_MIN_USES and rate <= DEAD_THRESHOLD and not eq.get('can_delete') == False:
                eq['status'] = 'dead'
                self.graveyard.append({
                    'id': eq['id'], 'name': eq['name'],
                    'uses': uses, 'success_rate': rate,
                    'died': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': eq.get('source', ''),
                })
                if len(self.graveyard) > GRAVEYARD_MAX:
                    self.graveyard.pop(0)
                del self.equations[eq_id]
                events.append(('dead', '%s KILLED (%.0f%% after %d uses)' % (eq['name'], rate * 100, uses)))

        return events

    def mutate(self, top_n=MUTATION_TOP_N):
        """Breed mutations from top equations. Returns list of events."""
        events = []
        if self.active_count() + self.golden_count() >= MAX_LIBRARY_SIZE:
            return events

        hierarchy = self.sorted_hierarchy()
        candidates = hierarchy[:top_n]

        for parent in candidates:
            if self.active_count() + self.golden_count() >= MAX_LIBRARY_SIZE:
                break

            # Generate version number
            parent_base = parent.get('id', 'eq_unknown')
            vn = self._next_version.get(parent_base, 2)
            self._next_version[parent_base] = vn + 1

            # Mutate affinity: adjust 2-3 random dimensions
            new_affinity = dict(parent['affinity'])
            dims_to_mutate = random.sample(DIMENSIONS, random.randint(2, 3))
            for d in dims_to_mutate:
                delta = random.uniform(-0.3, 0.3)
                new_affinity[d] = max(0.0, min(1.0, new_affinity.get(d, 0.5) + delta))

            # Mutate weights
            new_lw = max(0.0, min(1.0, parent['left_weight'] + random.uniform(-0.1, 0.1)))
            new_rw = max(0.0, min(1.0, parent['right_weight'] + random.uniform(-0.1, 0.1)))
            new_sb = max(0.0, min(1.0, parent.get('synthesis_bias', 0.3) + random.uniform(-0.1, 0.1)))

            new_id = 'eq_%s_v%d' % (parent['name'].lower().replace(' ', '_'), vn)
            new_name = '%s v%d' % (parent['name'], vn)

            mutation = {
                'id': new_id,
                'name': new_name,
                'icon': parent.get('icon', '?'),
                'desc': 'Mutation of %s' % parent['name'],
                'affinity': new_affinity,
                'left_weight': round(new_lw, 2),
                'right_weight': round(new_rw, 2),
                'synthesis_bias': round(new_sb, 2),
                'confidence_threshold': parent.get('confidence_threshold', 0.3),
                'uses': 0,
                'wins': 0,
                'total_reward': 0.0,
                'success_rate': 0.0,
                'streak': 0,
                'status': 'active',
                'source': 'mutation',
                'parent_id': parent['id'],
                'history': {},
                'recent_rewards': [],
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'can_delete': True,
                'min_rank': parent.get('min_rank', 0),
                'formula': '',
                'creator': None,
                'jobs_completed': 0,
            }

            self.equations[new_id] = mutation
            events.append(('mutation', '%s bred from %s' % (new_name, parent['name'])))

        return events

    def save(self):
        """Persist library to JSON."""
        try:
            data = {
                'equations': self.equations,
                'graveyard': self.graveyard[-GRAVEYARD_MAX:],
                'next_version': self._next_version,
                'last_save': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            tmp = self.filepath + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(data, f, indent=2)
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            os.rename(tmp, self.filepath)
        except Exception:
            pass

    def load(self):
        """Load library from JSON."""
        if not os.path.exists(self.filepath):
            return False
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            self.equations = data.get('equations', {})
            self.graveyard = data.get('graveyard', [])
            self._next_version = data.get('next_version', {})
            return True
        except Exception:
            return False


# ===================================================
# EQUATION REQUEST QUEUE
# ===================================================

class EquationRequestQueue(object):
    """Users submit equation requests. Community votes. Admin approves."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.requests = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r') as f:
                self.requests = json.load(f)
        except Exception:
            self.requests = []

    def save(self):
        try:
            tmp = self.filepath + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(self.requests, f, indent=2)
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            os.rename(tmp, self.filepath)
        except Exception:
            pass

    def submit_request(self, name, formula, desc, submitted_by):
        """Submit a new equation request."""
        req_id = 'req_%s_%s' % (name.lower().replace(' ', '_')[:15], str(int(time.time()))[-6:])
        req = {
            'id': req_id,
            'name': name[:40],
            'formula': formula[:200],
            'desc': desc[:300],
            'submitted_by': submitted_by,  # {ip_hash, rank, credits, session_id, timestamp}
            'status': 'pending',
            'votes': 0,
            'voters': [],
            'created': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        self.requests.append(req)
        # Keep max 200 requests
        if len(self.requests) > 200:
            self.requests = self.requests[-200:]
        self.save()
        return req

    def vote_request(self, req_id, voter_hash):
        """Vote for a request. One vote per IP hash."""
        for req in self.requests:
            if req['id'] == req_id:
                if voter_hash in req.get('voters', []):
                    return False, 'Already voted'
                req['votes'] = req.get('votes', 0) + 1
                req.setdefault('voters', []).append(voter_hash)
                self.save()
                return True, req
        return False, 'Request not found'

    def get_requests(self, status='pending'):
        """Get requests by status."""
        result = [r for r in self.requests if r.get('status') == status]
        result.sort(key=lambda r: r.get('votes', 0), reverse=True)
        return result

    def approve_request(self, req_id):
        """Mark request as approved."""
        for req in self.requests:
            if req['id'] == req_id:
                req['status'] = 'approved'
                self.save()
                return True, req
        return False, 'Not found'

    def reject_request(self, req_id):
        """Mark request as rejected."""
        for req in self.requests:
            if req['id'] == req_id:
                req['status'] = 'rejected'
                self.save()
                return True, req
        return False, 'Not found'


# ===================================================
# STRATEGY ENGINE (with Equation Library)
# ===================================================

class StrategyEngine(object):
    """
    Equation-based strategy selector with dynamic library.
    Equations compete, learn, evolve. Winners go golden. Losers die.
    The brain that picks its own strategy is the brain that wins.
    """

    def __init__(self, studio_dir):
        self.studio_dir = studio_dir
        self.data_file = os.path.join(studio_dir, 'strategy_engine.json')
        self.lock = threading.Lock()

        # Shared engine state
        self.usage_log = []
        self.total_interactions = 0
        self.explore_count = 0
        self.events = []
        self.manual_override = None

        # Legacy state (for migration)
        self.history = {}
        self.confidence_history = {}
        self.strategy_wins = {}

        # Load shared state
        self._load()

        # Equation library
        lib_file = os.path.join(studio_dir, 'equation_library.json')
        self.library = EquationLibrary(lib_file)

        # Equation request queue
        req_file = os.path.join(studio_dir, 'equation_requests.json')
        self.request_queue = EquationRequestQueue(req_file)

        # Source info cache (set by analyze_and_select, read by learn)
        self._last_source_info = None

        if not self.library.load():
            # First boot or no library file — seed from STRATEGIES
            self._seed_library()
            self._migrate_existing_data()
            self.library.save()
            self._log_event('boot', 'Equation Library seeded — %d equations' % len(self.library.equations))
        else:
            self._log_event('boot', 'Equation Library loaded — %d equations (%d golden, %d active)' % (
                len(self.library.equations), self.library.golden_count(), self.library.active_count()))

        # Auto-save thread
        t = threading.Thread(target=self._save_loop)
        t.daemon = True
        t.start()

    # -----------------------------------------------
    # SEEDING & MIGRATION
    # -----------------------------------------------

    def _seed_library(self):
        """Convert 7 STRATEGIES into seed equations."""
        for key, strat in STRATEGIES.items():
            eq = {
                'id': key,
                'name': strat['name'],
                'icon': strat['icon'],
                'desc': strat['desc'],
                'affinity': dict(strat['affinity']),
                'left_weight': strat['left_weight'],
                'right_weight': strat['right_weight'],
                'synthesis_bias': strat.get('synthesis_bias', 0.0),
                'confidence_threshold': strat.get('confidence_threshold', 0.3),
                'uses': 0,
                'wins': 0,
                'total_reward': 0.0,
                'success_rate': 0.0,
                'streak': 0,
                'status': 'active',
                'source': 'seed',
                'parent_id': None,
                'history': {},
                'recent_rewards': [],
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'can_delete': False,
                'min_rank': SEED_RANKS.get(key, 0),
                'formula': '',  # Auto-generated on read
                'creator': None,
                'jobs_completed': 0,
            }
            self.library.add(eq)

    def _migrate_existing_data(self):
        """Port old strategy_engine.json data into seed equations."""
        for key in STRATEGIES:
            eq = self.library.get(key)
            if not eq:
                continue

            # Port H values
            if key in self.history:
                eq['history'] = dict(self.history[key])

            # Port confidence history
            if key in self.confidence_history:
                eq['recent_rewards'] = list(self.confidence_history[key])

            # Port wins
            if key in self.strategy_wins:
                eq['wins'] = self.strategy_wins[key]
                # Estimate uses from win ratio (assume avg confidence as proxy)
                conf = self.confidence_history.get(key, [])
                if conf:
                    avg = sum(conf) / len(conf)
                    if avg > 0:
                        eq['uses'] = max(eq['wins'], int(eq['wins'] / max(avg, 0.1)))
                    else:
                        eq['uses'] = eq['wins'] * 2
                else:
                    eq['uses'] = eq['wins']
                eq['success_rate'] = eq['wins'] / max(eq['uses'], 1)

    # -----------------------------------------------
    # PUBLIC API
    # -----------------------------------------------

    def analyze_and_select(self, user_msg, user_rank=0, source_info=None):
        """Full pipeline: detect problem vector, select equation, return params.
        user_rank: credits (int) — filters equations by min_rank
        source_info: {rank, credits, trust, session_id} — stored with usage log
        """
        with self.lock:
            pvec = self._detect_problem_vector(user_msg)

            # === GAUNTLET: hostile low-rank user gets the demon ===
            hostility = detect_hostility(user_msg)
            gauntlet_triggered = False
            value_found = None
            if hostility >= 0.3 and user_rank < GAUNTLET_RANK_THRESHOLD:
                gauntlet_eq = self.library.get('gauntlet')
                if gauntlet_eq:
                    gauntlet_triggered = True
                    self._log_event('gauntlet', 'Hostility %.0f%% — low rank %d — deploying Gauntlet' % (hostility * 100, user_rank))

            # === VALUE DETECTION: user drops something golden ===
            value_found = detect_value(user_msg)
            if value_found and value_found['found']:
                self._log_event('value_drop', 'Value detected: %s (%s)' % (value_found['type'], value_found['value']))

            # Manual override
            if self.manual_override and not gauntlet_triggered:
                chosen_id = self.manual_override
                self.manual_override = None
                eq = self.library.get(chosen_id)
                if not eq:
                    hierarchy = self.library.sorted_hierarchy()
                    eq = hierarchy[0] if hierarchy else None
                    chosen_id = eq['id'] if eq else 'balanced'
                scores = self._score_all(pvec, user_rank=user_rank)
                explored = False
                self._log_event('override', 'Manual override: %s' % chosen_id)
            elif gauntlet_triggered:
                chosen_id = 'gauntlet'
                eq = self.library.get('gauntlet')
                scores = self._score_all(pvec, user_rank=user_rank)
                explored = False
            else:
                chosen_id, scores, explored = self._select_equation(pvec, user_rank=user_rank)
                eq = self.library.get(chosen_id)

            # Fallback if equation disappeared
            if not eq:
                eq = STRATEGIES.get('balanced', STRATEGIES[list(STRATEGIES.keys())[0]])
                eq_id = 'balanced'
            else:
                eq_id = eq['id']

            dominant_dim = max(pvec, key=pvec.get)
            qtype = DIM_TO_QTYPE.get(dominant_dim, 'general')

            if explored:
                self.explore_count += 1

            # Store source info for this interaction
            self._last_source_info = source_info

            # Generate formula for display
            formula = generate_formula(eq)

            result = {
                'strategy': eq_id,
                'strategy_name': eq.get('name', eq_id),
                'strategy_icon': eq.get('icon', '?'),
                'problem_vector': pvec,
                'dominant_dim': dominant_dim,
                'dominant_type': qtype,
                'left_weight': eq.get('left_weight', 0.5),
                'right_weight': eq.get('right_weight', 0.5),
                'synthesis_bias': eq.get('synthesis_bias', 0.3),
                'confidence_threshold': eq.get('confidence_threshold', 0.3),
                'scores': {k: round(v, 4) for k, v in scores.items()},
                'explored': explored,
                'formula': formula,
                'min_rank': eq.get('min_rank', 0),
                'source_info': source_info,
                'gauntlet': gauntlet_triggered,
                'hostility': hostility,
                'value_detected': value_found if value_found and value_found['found'] else None,
            }
            self.last_chosen_id = chosen_id
            return result

    def learn(self, strategy_name, problem_vector, reward):
        """Post-response learning: update equation success, H values, lifecycle."""
        with self.lock:
            eq = self.library.get(strategy_name)
            if not eq:
                return

            # Skip learning for golden (read-only) but still track stats
            self.library.update_stats(strategy_name, reward)

            # Track jobs completed (truly successful responses)
            if reward >= JOB_SUCCESS_THRESHOLD:
                eq['jobs_completed'] = eq.get('jobs_completed', 0) + 1

            if eq['status'] != 'golden':
                # Update H values (per-dimension history)
                history = eq.setdefault('history', {})
                lr = 0.05 + abs(reward - 0.5) * 0.10

                for dim in DIMENSIONS:
                    p = problem_vector.get(dim, 0.0)
                    if p < 0.1:
                        continue
                    current = history.get(dim, 0.5)
                    delta = (reward - current) * lr * p
                    history[dim] = max(0.05, min(0.95, current + delta))

            # Build usage entry with source tracking
            usage_entry = {
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'strategy': strategy_name,
                'problem': {k: round(v, 3) for k, v in problem_vector.items()},
                'reward': round(reward, 3),
            }
            # Add source info if available
            src = getattr(self, '_last_source_info', None)
            if src:
                usage_entry['source_rank'] = src.get('rank', 'RECRUIT')
                usage_entry['source_credits'] = src.get('credits', 0)
                usage_entry['source_trust'] = src.get('trust', 'unknown')
                usage_entry['source_session'] = src.get('session_id', '')

            self.usage_log.append(usage_entry)
            if len(self.usage_log) > 500:
                self.usage_log.pop(0)

            self.total_interactions += 1

            # Periodic decay (active equations only)
            if self.total_interactions % DECAY_EVERY == 0:
                self._decay_all()
                self._log_event('decay', 'Decay cycle at interaction %d' % self.total_interactions)

            # Check promotions/deaths
            lifecycle_events = self.library.check_promotions()
            for etype, detail in lifecycle_events:
                self._log_event(etype, detail)

            # Periodic mutation
            if self.total_interactions % MUTATION_EVERY == 0 and self.total_interactions > 0:
                mutation_events = self.library.mutate()
                for etype, detail in mutation_events:
                    self._log_event(etype, detail)

            # Milestones
            if self.total_interactions in (10, 50, 100, 500, 1000, 5000, 10000):
                self._log_event('milestone', '%d interactions reached' % self.total_interactions)

            # Leader tracking
            if self.total_interactions > 10 and self.total_interactions % 50 == 0:
                hierarchy = self.library.sorted_hierarchy()
                if hierarchy:
                    leader = hierarchy[0]
                    self._log_event('leader', '%s leads (%.0f%% success, %d uses)' % (
                        leader['name'], leader.get('success_rate', 0) * 100, leader.get('uses', 0)))

    def get_stats(self):
        """Dashboard stats: equation library, standings, evolution."""
        with self.lock:
            hierarchy = self.library.sorted_hierarchy()
            standings = []
            for eq in hierarchy:
                recent = eq.get('recent_rewards', [])
                avg_conf = sum(recent) / max(len(recent), 1) if recent else 0.5
                standings.append({
                    'name': eq['id'],
                    'display': eq['name'],
                    'icon': eq.get('icon', '?'),
                    'avg_confidence': round(avg_conf, 3),
                    'wins': eq.get('wins', 0),
                    'uses': eq.get('uses', 0),
                    'success_rate': round(eq.get('success_rate', 0), 3),
                    'win_pct': round(eq.get('wins', 0) / max(self.total_interactions, 1) * 100, 1),
                    'history': {d: round(v, 3) for d, v in eq.get('history', {}).items()},
                    'affinity': eq.get('affinity', {}),
                    'left_weight': eq.get('left_weight', 0.5),
                    'right_weight': eq.get('right_weight', 0.5),
                    'status': eq.get('status', 'active'),
                    'source': eq.get('source', ''),
                    'streak': eq.get('streak', 0),
                    'recent_uses': self._recent_use_count(eq['id'], 20),
                    'jobs_completed': eq.get('jobs_completed', 0),
                    'min_rank': eq.get('min_rank', 0),
                    'formula': generate_formula(eq),
                })

            # Problem dimension distribution (last 100 inputs)
            dim_totals = {d: 0.0 for d in DIMENSIONS}
            count = 0
            for entry in self.usage_log[-100:]:
                pv = entry.get('problem', {})
                for d in DIMENSIONS:
                    dim_totals[d] += pv.get(d, 0.0)
                count += 1
            dim_dist = {d: round(v / max(count, 1), 3) for d, v in dim_totals.items()}

            explore_rate = max(MIN_EXPLORE, INITIAL_EXPLORE - (self.total_interactions / EXPLORE_DECAY_OVER) * (INITIAL_EXPLORE - MIN_EXPLORE))

            return {
                'total_interactions': self.total_interactions,
                'explore_rate': round(explore_rate, 3),
                'explore_count': self.explore_count,
                'standings': standings,
                'dimension_distribution': dim_dist,
                'dimension_names': dict(DIM_NAMES),
                'recent_events': self.events[-20:],
                'last_strategy': self.usage_log[-1] if self.usage_log else None,
                'library_size': len(self.library.equations),
                'golden_count': self.library.golden_count(),
                'active_count': self.library.active_count(),
                'dead_count': len(self.library.graveyard),
                'graveyard_size': len(self.library.graveyard),
            }

    # -----------------------------------------------
    # EQUATION LIBRARY MANAGEMENT (user/Dan API)
    # -----------------------------------------------

    def get_library(self, user_credits=0):
        """Full library for dashboard. Returns locked status per equation."""
        with self.lock:
            result = []
            for eq in self.library.sorted_hierarchy():
                min_rank = eq.get('min_rank', 0)
                locked = user_credits < min_rank
                result.append({
                    'id': eq['id'],
                    'name': eq['name'],
                    'icon': eq.get('icon', '?'),
                    'desc': eq.get('desc', ''),
                    'affinity': eq.get('affinity', {}),
                    'left_weight': eq.get('left_weight', 0.5),
                    'right_weight': eq.get('right_weight', 0.5),
                    'synthesis_bias': eq.get('synthesis_bias', 0.0),
                    'uses': eq.get('uses', 0),
                    'wins': eq.get('wins', 0),
                    'success_rate': round(eq.get('success_rate', 0), 3),
                    'streak': eq.get('streak', 0),
                    'status': eq.get('status', 'active'),
                    'source': eq.get('source', ''),
                    'parent_id': eq.get('parent_id'),
                    'created': eq.get('created', ''),
                    'can_delete': eq.get('can_delete', True),
                    'min_rank': min_rank,
                    'locked': locked,
                    'unlock_rank': rank_name_from_credits(min_rank),
                    'formula': generate_formula(eq),
                    'jobs_completed': eq.get('jobs_completed', 0),
                    'creator': eq.get('creator'),
                })
            return {
                'equations': result,
                'graveyard': self.library.graveyard[-20:],
                'total': len(self.library.equations),
                'golden': self.library.golden_count(),
                'active': self.library.active_count(),
            }

    def create_equation(self, name, affinity, weights=None, desc='', creator=None, formula=''):
        """Create a new equation from user input."""
        with self.lock:
            weights = weights or {}
            eq_id = 'eq_user_%s_%s' % (name.lower().replace(' ', '_')[:20], str(int(time.time()))[-6:])

            # Validate affinity
            clean_affinity = {}
            for d in DIMENSIONS:
                val = affinity.get(d, 0.5)
                clean_affinity[d] = max(0.0, min(1.0, float(val)))

            eq = {
                'id': eq_id,
                'name': name[:40],
                'icon': name[0].upper() if name else '?',
                'desc': desc[:200],
                'affinity': clean_affinity,
                'left_weight': max(0.0, min(1.0, float(weights.get('left', 0.5)))),
                'right_weight': max(0.0, min(1.0, float(weights.get('right', 0.5)))),
                'synthesis_bias': max(0.0, min(1.0, float(weights.get('synthesis', 0.3)))),
                'confidence_threshold': 0.3,
                'uses': 0,
                'wins': 0,
                'total_reward': 0.0,
                'success_rate': 0.0,
                'streak': 0,
                'status': 'active',
                'source': 'user',
                'parent_id': None,
                'history': {},
                'recent_rewards': [],
                'created': time.strftime('%Y-%m-%d %H:%M:%S'),
                'can_delete': True,
                'min_rank': 0,
                'formula': formula[:200] if formula else '',
                'creator': creator,  # {ip_hash, rank, credits, session_id}
                'jobs_completed': 0,
            }

            self.library.add(eq)
            self.library.save()
            self._log_event('create', 'User created equation: %s' % name)
            return eq

    def edit_equation(self, eq_id, changes):
        """Edit an active equation. Golden = read-only."""
        with self.lock:
            eq = self.library.get(eq_id)
            if not eq:
                return False, 'Equation not found: %s' % eq_id
            if eq['status'] == 'golden':
                return False, 'Cannot edit golden equation (read-only)'

            if 'affinity' in changes:
                for d in DIMENSIONS:
                    if d in changes['affinity']:
                        eq['affinity'][d] = max(0.0, min(1.0, float(changes['affinity'][d])))
            if 'left_weight' in changes:
                eq['left_weight'] = max(0.0, min(1.0, float(changes['left_weight'])))
            if 'right_weight' in changes:
                eq['right_weight'] = max(0.0, min(1.0, float(changes['right_weight'])))
            if 'synthesis_bias' in changes:
                eq['synthesis_bias'] = max(0.0, min(1.0, float(changes['synthesis_bias'])))
            if 'name' in changes:
                eq['name'] = str(changes['name'])[:40]
            if 'desc' in changes:
                eq['desc'] = str(changes['desc'])[:200]
            if 'formula' in changes:
                eq['formula'] = str(changes['formula'])[:200]

            self.library.save()
            self._log_event('edit', 'Equation edited: %s' % eq_id)
            return True, eq

    def delete_equation(self, eq_id):
        """Force-delete an equation. Seed equations can't be deleted."""
        with self.lock:
            eq = self.library.get(eq_id)
            if not eq:
                return False, 'Equation not found: %s' % eq_id
            if not eq.get('can_delete', True):
                return False, 'Seed equation cannot be deleted'

            # Move to graveyard
            self.library.graveyard.append({
                'id': eq['id'], 'name': eq['name'],
                'uses': eq.get('uses', 0),
                'success_rate': eq.get('success_rate', 0),
                'died': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': eq.get('source', ''),
                'reason': 'manual_delete',
            })
            del self.library.equations[eq_id]
            self.library.save()
            self._log_event('delete', 'Equation deleted: %s' % eq_id)
            return True, 'Deleted: %s' % eq_id

    def get_equation_detail(self, eq_id):
        """Full detail for a single equation."""
        with self.lock:
            eq = self.library.get(eq_id)
            if not eq:
                return None
            detail = dict(eq)
            detail['formula'] = generate_formula(eq)
            detail['unlock_rank'] = rank_name_from_credits(eq.get('min_rank', 0))
            return detail

    def trigger_mutation(self):
        """Manual mutation trigger (from dashboard)."""
        with self.lock:
            events = self.library.mutate()
            for etype, detail in events:
                self._log_event(etype, detail)
            self.library.save()
            return [{'type': t, 'detail': d} for t, d in events]

    def record_correction(self, eq_id, user_msg, wrong_reply, correct_answer):
        """User says Cortex got it wrong and provides the right answer.
        Harsh penalty on the equation + store correction for future learning."""
        with self.lock:
            eq = self.library.get(eq_id)
            if not eq:
                return False, 'Equation not found'

            # Harsh penalty — reward of 0.0 (total failure)
            self.library.update_stats(eq_id, 0.0)

            # Penalise H values harder than normal learning
            if eq['status'] != 'golden':
                history = eq.setdefault('history', {})
                pvec = self._detect_problem_vector(user_msg)
                for dim in DIMENSIONS:
                    p = pvec.get(dim, 0.0)
                    if p < 0.1:
                        continue
                    current = history.get(dim, 0.5)
                    # Stronger penalty: pull H toward 0 with 3x learning rate
                    delta = (0.0 - current) * 0.15 * p
                    history[dim] = max(0.05, min(0.95, current + delta))

            # Check lifecycle (this fail might kill a bad equation)
            lifecycle_events = self.library.check_promotions()
            for etype, detail in lifecycle_events:
                self._log_event(etype, detail)

            # Store correction for future reference
            corrections_file = os.path.join(self.studio_dir, 'corrections.json')
            corrections = []
            if os.path.exists(corrections_file):
                try:
                    with open(corrections_file, 'r') as f:
                        corrections = json.load(f)
                except Exception:
                    corrections = []

            corrections.append({
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'equation': eq_id,
                'equation_name': eq.get('name', eq_id),
                'user_msg': user_msg[:300],
                'wrong_reply': wrong_reply[:500],
                'correct_answer': correct_answer[:500],
            })
            # Keep last 500 corrections
            if len(corrections) > 500:
                corrections = corrections[-500:]

            try:
                with open(corrections_file, 'w') as f:
                    json.dump(corrections, f, indent=2)
            except Exception:
                pass

            self.library.save()
            self._log_event('correction', 'User corrected %s: "%s"' % (eq.get('name', eq_id), user_msg[:40]))
            return True, 'Correction recorded — %s penalised' % eq.get('name', eq_id)

    def get_corrections(self, limit=50):
        """Get recent corrections for dashboard."""
        corrections_file = os.path.join(self.studio_dir, 'corrections.json')
        if not os.path.exists(corrections_file):
            return []
        try:
            with open(corrections_file, 'r') as f:
                corrections = json.load(f)
            return corrections[-limit:]
        except Exception:
            return []

    def get_equation_readme(self):
        """Machine-readable spec for AI equation generators.
        Any AI can read this and generate perfect equations for users."""
        with self.lock:
            # Top 5 equations by success rate
            hierarchy = self.library.sorted_hierarchy()
            top5 = []
            for eq in hierarchy[:5]:
                top5.append({
                    'id': eq['id'],
                    'name': eq['name'],
                    'affinity': eq.get('affinity', {}),
                    'left_weight': eq.get('left_weight', 0.5),
                    'right_weight': eq.get('right_weight', 0.5),
                    'synthesis_bias': eq.get('synthesis_bias', 0.3),
                    'success_rate': round(eq.get('success_rate', 0), 3),
                    'uses': eq.get('uses', 0),
                    'formula': generate_formula(eq),
                })

            return {
                'system': 'Cortex Equation System v1',
                'purpose': 'Equations define HOW Cortex thinks about a problem. '
                           'Complex equation = simple processing. '
                           'The equation does the heavy thinking, Cortex just executes.',
                'dimensions': dict(
                    (d, {
                        'name': DIM_NAMES[d],
                        'description': DIM_DESCRIPTIONS[d],
                        'range': '0.0 to 1.0 (0=ignore, 1=maximum focus)',
                        'keywords': sorted(list(SIGNAL_SETS[d]))[:20],
                    }) for d in DIMENSIONS
                ),
                'weights': {
                    'left_weight': 'Angel hemisphere (morality, ethics, compassion, Bible). 0.0-1.0.',
                    'right_weight': 'Demon hemisphere (logic, darkness, maths, hard truths). 0.0-1.0.',
                    'synthesis_bias': 'Cortex override strength. 0.0=pure hemisphere debate, 1.0=pure synthesis.',
                },
                'formula_format': 'DIM(name:value) + DIM(name:value) -> Angel:X% Demon:Y%',
                'optional_features': {
                    'timer': 'Prefix t(seconds) for timed operations',
                    'url': 'Append S(SEARCH:url) for web-connected equations',
                },
                'templates': dict(
                    (k, {
                        'affinity': v['affinity'],
                        'left_weight': v['left_weight'],
                        'right_weight': v['right_weight'],
                        'desc': v['desc'],
                    }) for k, v in STRATEGIES.items()
                ),
                'examples': [
                    {
                        'user_need': 'I want Cortex to be a compassionate listener',
                        'equation': {
                            'name': 'Compassionate Listener',
                            'affinity': {'F': 0.2, 'C': 0.3, 'E': 0.9, 'T': 0.0, 'S': 0.7, 'D': 0.1, 'H': 0.1},
                            'weights': {'left': 0.85, 'right': 0.15, 'synthesis': 0.2},
                        },
                        'formula': 'E(emotional:0.9) + S(social:0.7) + C(creative:0.3) -> Angel:85% Demon:15%',
                    },
                    {
                        'user_need': 'I want Cortex to sort data by importance',
                        'equation': {
                            'name': 'Data Sorter',
                            'affinity': {'F': 0.9, 'C': 0.1, 'E': 0.0, 'T': 0.9, 'S': 0.1, 'D': 0.3, 'H': 0.0},
                            'weights': {'left': 0.20, 'right': 0.80, 'synthesis': 0.1},
                        },
                        'formula': 'F(factual:0.9) + T(technical:0.9) + D(debate:0.3) -> Angel:20% Demon:80%',
                    },
                    {
                        'user_need': 'I want Cortex to handle angry customers on the phone',
                        'equation': {
                            'name': 'Customer Service Pro',
                            'affinity': {'F': 0.4, 'C': 0.2, 'E': 0.8, 'T': 0.2, 'S': 0.9, 'D': 0.6, 'H': 0.3},
                            'weights': {'left': 0.70, 'right': 0.30, 'synthesis': 0.5},
                        },
                        'formula': 'S(social:0.9) + E(emotional:0.8) + D(debate:0.6) + F(factual:0.4) -> Angel:70% Demon:30%',
                    },
                ],
                'create_endpoint': '/api/equation-create',
                'create_body': {
                    'name': 'string (required, max 40 chars)',
                    'affinity': '{F,C,E,T,S,D,H each 0.0-1.0}',
                    'weights': '{left: 0.0-1.0, right: 0.0-1.0, synthesis: 0.0-1.0}',
                    'desc': 'string (what this equation does)',
                    'formula': 'string (human-readable formula)',
                },
                'top_equations': top5,
            }

    # -----------------------------------------------
    # PROBLEM DETECTION
    # -----------------------------------------------

    def _detect_problem_vector(self, user_msg):
        """Score input on 7 dimensions. Returns dict {dim: 0.0-1.0}."""
        words = set(re.findall(r'[a-z]+', user_msg.lower()))
        content_words = max(len(words), 1)

        vec = {}
        for dim in DIMENSIONS:
            signals = SIGNAL_SETS[dim]
            hits = len(words & signals)
            raw = min(1.0, (hits / content_words) * SENSITIVITY)
            vec[dim] = raw

        max_val = max(vec.values())
        if max_val > 0:
            vec = {k: v / max_val for k, v in vec.items()}
        else:
            vec = {k: 1.0 / len(DIMENSIONS) for k in DIMENSIONS}

        return vec

    # -----------------------------------------------
    # EQUATION SCORING (THE EQUATION)
    # -----------------------------------------------

    def _score_equation(self, eq, problem_vector):
        """
        S(s,P) = SUM(A[s][d] * P[d] * H[s][d]) * C^alpha * F^beta - lambda*X
        """
        affinity = eq.get('affinity', {})
        history = eq.get('history', {})

        # Core weighted sum
        weighted_sum = 0.0
        for dim in DIMENSIONS:
            a = affinity.get(dim, 0.5)
            p = problem_vector.get(dim, 0.0)
            h = history.get(dim, 0.5)
            weighted_sum += a * p * h

        # Confidence factor
        recent = eq.get('recent_rewards', [])
        conf = sum(recent) / max(len(recent), 1) if recent else 0.5
        conf_factor = conf ** ALPHA

        # Frequency penalty
        recent_uses = self._recent_use_count(eq['id'], 20)
        freq_factor = (1.0 / (1.0 + recent_uses * 0.1)) ** BETA

        # Complexity cost
        complexity = eq.get('synthesis_bias', 0.0)

        score = weighted_sum * conf_factor * freq_factor - LAMBDA * complexity

        # Golden bonus
        if eq.get('status') == 'golden':
            score *= GOLDEN_BONUS

        # Novelty bonus for new equations
        if eq.get('uses', 0) < NOVELTY_USES:
            score += NOVELTY_BONUS

        return max(0.0, score)

    def _score_all(self, problem_vector, user_rank=0):
        """Score all equations in hierarchy, filtered by rank."""
        scores = {}
        for eq in self.library.sorted_hierarchy():
            min_rank = eq.get('min_rank', 0)
            if user_rank >= min_rank:
                scores[eq['id']] = self._score_equation(eq, problem_vector)

        # If nothing qualifies (shouldn't happen, rank-0 seeds always exist), fall back
        if not scores:
            for eq in self.library.sorted_hierarchy():
                if eq.get('min_rank', 0) == 0:
                    scores[eq['id']] = self._score_equation(eq, problem_vector)

        return scores

    def _select_equation(self, problem_vector, user_rank=0):
        """Score all equations, return best (with exploration)."""
        scores = self._score_all(problem_vector, user_rank=user_rank)

        if not scores:
            return 'balanced', {'balanced': 0.0}, False

        # Exploration
        explore_rate = max(MIN_EXPLORE, INITIAL_EXPLORE - (self.total_interactions / EXPLORE_DECAY_OVER) * (INITIAL_EXPLORE - MIN_EXPLORE))
        if random.random() < explore_rate:
            chosen = random.choice(list(scores.keys()))
            return chosen, scores, True

        chosen = max(scores, key=scores.get)
        return chosen, scores, False

    def _recent_use_count(self, eq_id, window=20):
        """How many times equation was used in last N interactions."""
        count = 0
        for entry in self.usage_log[-window:]:
            if entry.get('strategy') == eq_id:
                count += 1
        return count

    # -----------------------------------------------
    # DECAY
    # -----------------------------------------------

    def _decay_all(self):
        """Gentle decay: all active H values drift 2% toward neutral."""
        for eq in self.library.get_active():
            history = eq.get('history', {})
            for dim in list(history.keys()):
                current = history[dim]
                history[dim] = current + (0.5 - current) * DECAY_RATE

    # -----------------------------------------------
    # EVENTS
    # -----------------------------------------------

    def _log_event(self, event_type, detail):
        """Log a notable event."""
        self.events.append({
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'detail': detail,
        })
        if len(self.events) > 200:
            self.events.pop(0)

    # -----------------------------------------------
    # PERSISTENCE
    # -----------------------------------------------

    def _load(self):
        """Load shared engine state from JSON."""
        if not os.path.exists(self.data_file):
            self._log_event('boot', 'Strategy Engine initialized (fresh)')
            return
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            self.history = data.get('history', {})
            self.confidence_history = data.get('confidence_history', {})
            self.usage_log = data.get('usage_log', [])
            self.total_interactions = data.get('total_interactions', 0)
            self.strategy_wins = data.get('strategy_wins', {})
            self.explore_count = data.get('explore_count', 0)
            self.events = data.get('events', [])
            self._log_event('boot', 'Engine state loaded (%d interactions)' % self.total_interactions)
        except Exception as e:
            self._log_event('error', 'Failed to load state: %s' % str(e))

    def _save(self):
        """Save shared engine state + library."""
        try:
            data = {
                'usage_log': self.usage_log[-500:],
                'total_interactions': self.total_interactions,
                'explore_count': self.explore_count,
                'events': self.events[-200:],
                'last_save': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            tmp = self.data_file + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(data, f, indent=2)
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            os.rename(tmp, self.data_file)
        except Exception as e:
            self._log_event('error', 'Save failed: %s' % str(e))

        # Also save library
        self.library.save()

    def _save_loop(self):
        """Auto-save every 15 minutes."""
        while True:
            time.sleep(900)
            with self.lock:
                self._save()
