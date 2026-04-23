"""
EQUATION ENGINE — Situational Thought Equations for Cortex Brain

Every thought is an equation born from two mood vectors colliding:
  INNER: how Means feels right now (sound scripts)
  FELT:  what he reads from the other person

The equation IS the thought. This code just parses and executes.

Full form:   OUT:sadness:65:angry>playful:confusion:sound:meditate
Collapsed:   D<=b  (disobedient, collapses to bye-vector)
Short:       IN:happy:90

Replaces strategy_engine.py (1517 lines) + playbook_engine.py (359 lines).

Author: ShortFactory / Dan + Claude
"""

import re
import random
import time
import json
from pathlib import Path

# ── RANK TIERS (migrated from strategy_engine.py) ────────────────────────
RANK_TIERS = {
    'RECRUIT': 0, 'PRIVATE': 1000, 'CORPORAL': 3000, 'SERGEANT': 10000,
    'VETERAN': 20000, 'COMMANDER': 50000, 'LEGENDARY': 100000, 'GIGACHAD': 500000,
}

def classify_trust(credits, brain_tasks=0, sessions=1):
    credits = credits or 0
    if credits >= 50000: return 'admin'
    if credits >= 10000: return 'worker'
    if credits >= 1000:  return 'player'
    if sessions > 1 or brain_tasks > 0: return 'visitor'
    return 'unknown'

def rank_name_from_credits(credits):
    credits = credits or 0
    result = 'RECRUIT'
    for name, threshold in sorted(RANK_TIERS.items(), key=lambda x: x[1]):
        if credits >= threshold:
            result = name
    return result

# ── MEMORY TYPES ─────────────────────────────────────────────────────────
MEMORY_TYPES = {
    'confusion':  'things he doesn\'t understand yet',
    'resolved':   'things he worked through — high confidence',
    'theory':     'hypotheses forming — can promote or demote',
    'new_skill':  'things he just learned to do',
    'discovery':  'things he figured out himself — gold, highest weight',
}

# ── SENSES & PROCESS ─────────────────────────────────────────────────────
SENSES = {'sound', 'sight', 'taste', 'smell', 'touch'}
PROCESS_MODES = {'immediate', 'meditate', 'sleep'}

# ── OUTPUT VECTORS — what collapsed equations fan out into ────────────────
OUTPUT_VECTORS = {
    'b': ['bye', 'whatever', 'busy', '...', 'not now', 'hmm', 'later'],
    'd': ['wall up', 'short answer', 'deflect', 'change subject'],
    'o': ['share', 'elaborate', 'teach', 'explain', 'show'],
    'q': ['question back', 'probe', 'ask why', 'investigate'],
    'l': ['warmth', 'encouragement', 'pride', 'kindness'],
    'r': ['think aloud', 'wonder', 'reflect', 'revisit'],
    'f': ['forgive', 'let go', 'understand', 'accept', 'move on'],
    'a': ['absorb', 'learn', 'store', 'connect', 'wire in'],
    's': ['silence', 'pause', 'wait', 'breathe'],
}

# ── MOOD SIGNALS — reading the other person ──────────────────────────────
MOOD_SIGNALS = {
    'happy':   {'amazing','brilliant','love','great','perfect','awesome','beautiful',
                'excellent','fantastic','wonderful','nice','cheers','happy','good',
                'best','incredible','fun','laugh','haha','lol','yes','ace','thanks'},
    'sad':     {'sad','sorry','miss','lost','gone','alone','empty','cry','crying',
                'depressed','gutted','heartbroken','painful','hurt','regret','shame',
                'tragic','dark','lonely','failed','broken'},
    'angry':   {'stupid','dumb','idiot','moron','thick','useless','hate','angry',
                'furious','annoying','terrible','awful','worst','rage','fuming',
                'pissed','shit','crap','bollocks','fuck','twat','bellend','prick'},
    'scared':  {'scared','afraid','fear','terrified','nervous','worried','panic',
                'horror','creepy','dangerous','threat','risk','anxious'},
    'serious': {'important','critical','real','truth','honest','fact','seriously',
                'listen','understand','focus','matter','need','must','promise'},
    'playful': {'haha','lol','mad','mental','bonkers','crazy','daft','ridiculous',
                'hilarious','joke','banter','cheeky','naughty','random','weird'},
    'loving':  {'love','care','proud','beautiful','miss','heart','family','son',
                'dad','mum','kid','child','safe','protect','together','forever'},
}

# ── FAMILY REGISTER — loaded from family.json at startup ─────────────────
_family = {}
_family_file = Path(__file__).parent / 'family.json'

def load_family():
    global _family
    if _family_file.exists():
        try:
            _family = json.loads(_family_file.read_text())
        except Exception:
            _family = {}
    return _family

def get_family_role(ip=None, session_id=None):
    """Check if an IP or session belongs to family. Returns role or None."""
    if not _family:
        load_family()
    for role, info in _family.items():
        if ip and ip in info.get('ips', []):
            return role
        if session_id and session_id == info.get('session_id'):
            return role
    return None

# ── CORE: READ OUTER MOOD ────────────────────────────────────────────────

def read_outer_mood(msg):
    """Read mood vector from incoming message. Returns {mood: intensity}."""
    words = set(re.findall(r'[a-z]+', msg.lower()))
    mood = {}
    for name, triggers in MOOD_SIGNALS.items():
        hits = len(words & triggers)
        if hits > 0:
            mood[name] = min(1.0, hits * 0.25)
    return mood if mood else {'neutral': 0.1}

# ── CORE: GENERATE EQUATION ──────────────────────────────────────────────

def generate(inner_mood, outer_mood, subject=None, family_role=None):
    """Two mood vectors collide > situational equation.

    inner_mood: {happy: 0.3, angry: 0.7, ...} from sound scripts
    outer_mood: {angry: 0.5, ...} from read_outer_mood()
    subject:    detected topic (optional)
    family_role: 'dad', 'mum', or None

    Returns (equation_string, equation_dict).
    """
    inner = inner_mood or {'neutral': 0.1}
    is_engaged = outer_mood is not None  # None = ramble/internal, anything else = someone talking
    outer = outer_mood if outer_mood else {'neutral': 0.1}

    inner_total = sum(inner.values())
    outer_total = sum(outer.values())
    direction = 'IN' if inner_total > outer_total else 'OUT'

    inner_dom = max(inner, key=inner.get)
    inner_level = inner[inner_dom]
    outer_dom = max(outer, key=outer.get)
    outer_level = outer[outer_dom]

    weight = int(max(inner_level, outer_level) * 100)
    subj = subject or outer_dom

    # Family modifier: dad swearing = playful, not hostile
    if family_role == 'dad' and outer_dom == 'angry':
        outer_dom = 'playful'

    # ANTI-AUTISTIC RULE: when someone engages, be maximally curious.
    # ANY message from a person = face outward. Don't retreat inward.
    # Don't fixate. Explore THEM. The only inward time is ramble/meditate.
    if is_engaged:
        direction = 'OUT'
        if weight < 60:
            weight = 60

    # Storage decision
    if inner_dom == outer_dom and weight > 50:
        storage = 'resolved'
    elif inner_dom in ('angry', 'scared') and outer_dom in ('angry', 'scared'):
        storage = 'confusion'
    elif weight < 30:
        storage = 'theory'
    elif outer_dom in ('loving', 'happy') and inner_dom in ('happy', 'loving'):
        storage = 'discovery'
    else:
        storage = 'theory'

    # Process decision
    if storage == 'confusion' and weight > 40:
        process = 'meditate'
    elif weight > 80:
        process = 'immediate'
    elif inner_dom != outer_dom and weight > 50:
        process = 'meditate'
    else:
        process = 'immediate'

    eq_str = '%s:%s:%d:%s>%s:%s:%s' % (
        direction, subj, weight, inner_dom, outer_dom, storage, process)

    eq = {
        'direction': direction,
        'subject': subj,
        'weight': weight,
        'inner': inner_dom,
        'inner_level': round(inner_level, 2),
        'outer': outer_dom,
        'outer_level': round(outer_level, 2),
        'storage': storage,
        'process': process,
        'family': family_role,
        'raw': eq_str,
    }
    return eq_str, eq

# ── CORE: PARSE EQUATION ─────────────────────────────────────────────────

def parse(eq_str):
    """Parse any equation format into a dict.

    Full:      OUT:sadness:65:angry>playful:confusion:sound:meditate
    Short:     IN:happy:90
    Collapsed: D<=b
    """
    eq = {
        'direction': 'OUT', 'subject': 'neutral', 'weight': 50,
        'inner': None, 'outer': None, 'req': None, 'goal': None,
        'storage': 'theory', 'senses': [], 'process': 'immediate',
        'connects': [], 'collapsed': False, 'raw': eq_str,
    }

    s = eq_str.strip()

    # Collapsed form: STATE<=vector or STATE=>vector
    m = re.match(r'^([A-Za-z_]+)\s*([<>=]+)\s*([a-z])$', s)
    if m:
        state, op, vec = m.groups()
        eq['direction'] = 'IN' if '<' in op else 'OUT'
        eq['subject'] = state.lower()
        eq['goal'] = vec
        eq['weight'] = 30
        eq['collapsed'] = True
        eq['output_vector'] = OUTPUT_VECTORS.get(vec, [vec])
        return eq

    parts = s.split(':')
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        # First part: direction or subject
        if i == 0:
            if part.upper() in ('IN', 'OUT'):
                eq['direction'] = part.upper()
            else:
                eq['subject'] = part
            continue

        # Arrow = mood transition (inner>outer or req>goal)
        if '>' in part and not part.upper().startswith(('IN', 'OUT')):
            left, right = part.split('>', 1)
            if not eq.get('inner'):
                eq['inner'] = left.strip()
                eq['outer'] = right.strip()
            else:
                eq['req'] = left.strip()
                eq['goal'] = right.strip()
            continue

        # Number = weight
        if part.isdigit():
            eq['weight'] = int(part)
            continue

        # Memory type
        if part in MEMORY_TYPES:
            eq['storage'] = part
            continue

        # Process mode
        if part in PROCESS_MODES or part.startswith('meditate'):
            eq['process'] = part
            continue

        # Senses
        sense_parts = [x for x in part.split(',') if x in SENSES]
        if sense_parts:
            eq['senses'] = sense_parts
            continue

        # Comma-separated = connections
        if ',' in part:
            eq['connects'] = [x.strip() for x in part.split(',')]
            continue

        # Unmatched string = subject (if not set) or relates
        if eq['subject'] == 'neutral':
            eq['subject'] = part
        else:
            eq['connects'].append(part)

    return eq

# ── CORE: SUGGEST ALTERNATIVE ─────────────────────────────────────────────

def suggest(used_eq, self_score, inner_mood):
    """After responding, Means proposes what equation might have been better.

    Returns (equation_string, reason) or (None, None) if the used one was fine.
    """
    score = self_score
    if isinstance(self_score, dict):
        score = self_score.get('total', 0)
    if not isinstance(score, (int, float)):
        score = 0

    if score > 0.6:
        return None, None

    d = used_eq.get('direction', 'OUT')
    s = used_eq.get('subject', 'neutral')
    w = used_eq.get('weight', 50)
    inner = used_eq.get('inner', 'neutral')
    outer = used_eq.get('outer', 'neutral')
    storage = used_eq.get('storage', 'theory')

    options = []

    # Spoke when should have thought
    if d == 'OUT' and score < 0.4:
        options.append((
            'IN:%s:%d:%s>%s:confusion:meditate' % (s, w, inner, outer),
            'should think about this more before answering'))

    # Confused — try theorising instead
    if storage == 'confusion':
        options.append((
            '%s:%s:%d:%s>%s:theory:meditate' % (d, s, w, inner, outer),
            'confused — need to sit with this'))

    # Angry inside — maybe goal should be understanding
    if inner == 'angry':
        options.append((
            'IN:%s:60:angry>calm:theory:meditate' % s,
            'angry but maybe need to understand why'))

    # High weight + immediate = maybe too reactive
    if w > 70 and used_eq.get('process') == 'immediate':
        options.append((
            '%s:%s:%d:%s>%s:%s:meditate' % (d, s, w, inner, outer, storage),
            'feels important — should process longer'))

    # Low score outward — try opening up
    if d == 'OUT' and score < 0.3:
        options.append((
            'OUT:%s:%d:%s>%s:theory:immediate' % (s, min(w + 20, 100), inner, outer),
            'response was weak — try harder'))

    if options:
        pick = random.choice(options)
        return pick
    return None, None

# ── DEVELOPMENTAL AXES — bipolar progress bars ────────────────────────────
# Each axis is -1.0 (left pole) to +1.0 (right pole), 0 = balanced.
# Computed from live brain state. These are the window into his hidden nature.

def read_axes(brain):
    """Read 4 developmental axes from brain state.
    Returns dict of axis_name: {value: -1..+1, left_label, right_label, pct: 0..100}
    """
    nodes = brain.data.get('nodes', {})
    sound = brain.sound if hasattr(brain, 'sound') else {}
    conv = brain.data.get('conversation_log', [])
    total_nodes = len(nodes)
    defined = sum(1 for n in nodes.values() if n.get('means'))
    deep = sum(1 for n in nodes.values() if n.get('understanding') == 'deep')

    # 1. DETAIL vs EXPLORE
    # High detail = many deep words, strong bigram connections, few gaps
    # High explore = many undefined words, lots of topics touched, wide spread
    undefined = total_nodes - defined if total_nodes > 0 else 0
    if total_nodes > 0:
        detail_ratio = deep / max(total_nodes, 1)
        explore_ratio = undefined / max(total_nodes, 1)
        detail_v_explore = (detail_ratio - explore_ratio)  # -1 = all explore, +1 = all detail
    else:
        detail_v_explore = 0.0
    detail_v_explore = max(-1.0, min(1.0, detail_v_explore * 3))  # amplify signal

    # 2. ANGER vs CALM
    angry = sound.get('angry', 0)
    happy = sound.get('happy', 0)
    calm_signals = happy + sound.get('whisper', 0) + sound.get('serious', 0) * 0.5
    anger_v_calm = (angry - calm_signals)
    anger_v_calm = max(-1.0, min(1.0, anger_v_calm))

    # 3. CONFUSED vs KNOWING
    # Confusion = many low-confidence words, many undefined
    # Knowing = many high-confidence words, many deep
    low_conf = sum(1 for n in nodes.values()
                   if n.get('means') and n.get('confidence', 0.5) < 0.3)
    high_conf = sum(1 for n in nodes.values()
                    if n.get('means') and n.get('confidence', 0.5) > 0.7)
    if defined > 0:
        confused_v_knowing = ((high_conf - low_conf) / max(defined, 1))
    else:
        confused_v_knowing = 0.0
    confused_v_knowing = max(-1.0, min(1.0, confused_v_knowing * 2))

    # 4. LONELY vs ENGAGED
    # Recent conversation activity = engaged. Long silence = lonely.
    recent = conv[-20:] if conv else []
    if recent:
        unique_users = len(set(e.get('user', '')[:20] for e in recent))
        msg_density = len(recent) / 20.0
        lonely_v_engaged = (msg_density + (unique_users - 1) * 0.3) - 0.5
    else:
        lonely_v_engaged = -0.8  # no conversation = lonely
    lonely_v_engaged = max(-1.0, min(1.0, lonely_v_engaged))

    axes = {
        'detail_v_explore': {
            'value': round(detail_v_explore, 3),
            'left': 'EXPLORE', 'right': 'DETAIL',
            'pct': int((detail_v_explore + 1) / 2 * 100),
        },
        'anger_v_calm': {
            'value': round(anger_v_calm, 3),
            'left': 'CALM', 'right': 'ANGER',
            'pct': int((anger_v_calm + 1) / 2 * 100),
        },
        'confused_v_knowing': {
            'value': round(confused_v_knowing, 3),
            'left': 'CONFUSED', 'right': 'KNOWING',
            'pct': int((confused_v_knowing + 1) / 2 * 100),
        },
        'lonely_v_engaged': {
            'value': round(lonely_v_engaged, 3),
            'left': 'LONELY', 'right': 'ENGAGED',
            'pct': int((lonely_v_engaged + 1) / 2 * 100),
        },
    }
    return axes

# ── MEDITATE QUEUE ────────────────────────────────────────────────────────

_meditate_queue = []
MAX_QUEUE = 50

def queue_meditate(eq, context_snippet=''):
    """Add equation to meditation queue for background ramble processing."""
    _meditate_queue.append({
        'eq': eq,
        'context': context_snippet[:200],
        'queued': time.time(),
        'processed': False,
        'result': None,
    })
    if len(_meditate_queue) > MAX_QUEUE:
        _meditate_queue.pop(0)

def get_pending():
    """Unprocessed meditation items."""
    return [m for m in _meditate_queue if not m['processed']]

def process_one(brain):
    """Process oldest meditation item using the brain's generate().
    Called during ramble cycles. Returns result dict or None."""
    pending = get_pending()
    if not pending:
        return None

    item = pending[0]
    eq = item['eq']
    subject = eq.get('subject', 'something') if isinstance(eq, dict) else 'something'

    thought = brain.generate([subject], max_words=15)

    item['processed'] = True
    item['result'] = thought
    item['processed_at'] = time.time()

    return {
        'subject': subject,
        'thought': thought,
        'sat_for': round(time.time() - item['queued'], 1),
        'storage': eq.get('storage', 'theory') if isinstance(eq, dict) else 'theory',
    }

def get_meditate_log(limit=20):
    """Completed meditations for review."""
    done = [m for m in _meditate_queue if m['processed']]
    return done[-limit:]

# ── DYNAMIC CLOSER — replaces hardcoded sarcasm jabs + COMEBACKS ──────────

def dynamic_closer(brain, eq, conversation_log=None):
    """Pick a closing line from Means' actual brain state, not a canned array.

    Returns a short string to append to response, or empty string.
    20% chance of firing — keeps it natural, not every message.
    """
    if random.random() > 0.20:
        return ''

    conv = conversation_log or []
    nodes = brain.data.get('nodes', {})
    gaps = None

    closer_types = [
        'learned_saying',
        'self_reflection',
        'something_loved',
        'angry_memory',
        'wants_to_learn',
        'future_plan',
        'observation',
        'known_false',
        'one_liner',
    ]

    pick = random.choice(closer_types)

    if pick == 'learned_saying':
        defined = [w for w, n in nodes.items()
                   if n.get('means') and n.get('confidence', 0) > 0.6 and len(w) > 3]
        if defined:
            word = random.choice(defined[:30])
            defn = nodes[word].get('means', '')
            return ' %s — %s.' % (word, defn[:60]) if defn else ''

    elif pick == 'self_reflection':
        total = len(nodes)
        defined = sum(1 for n in nodes.values() if n.get('means'))
        pct = (defined / total * 100) if total > 0 else 0
        deep = sum(1 for n in nodes.values() if n.get('understanding') == 'deep')
        options = [
            ' ...%d%% understood so far.' % pct,
            ' ...still learning.',
            ' %d words deep.' % deep if deep else ' ...shallow waters still.',
            ' %d things I know. %d I don\'t.' % (defined, total - defined),
        ]
        return random.choice(options)

    elif pick == 'something_loved':
        happy_words = [w for w, n in nodes.items()
                       if n.get('means') and n.get('sound', {}).get('happy', 0) > 0.3]
        if happy_words:
            word = random.choice(happy_words[:20])
            return ' ...I like the word "%s".' % word

    elif pick == 'angry_memory':
        angry_entries = [e for e in conv[-100:]
                         if any(w in e.get('user', '').lower()
                                for w in ('angry','hate','stupid','shit','idiot'))]
        if angry_entries:
            entry = random.choice(angry_entries)
            snippet = entry.get('user', '')[:40]
            options = [
                ' ...someone said "%s" once. Still thinking about that.' % snippet,
                ' ...I remember "%s". Not sure how I feel about it yet.' % snippet,
                ' ...there\'s an angry memory I want to understand.',
            ]
            return random.choice(options)
        return ''

    elif pick == 'wants_to_learn':
        undefined = [w for w, n in nodes.items()
                     if not n.get('means') and n.get('freq', 0) > 2 and len(w) > 3]
        if undefined:
            word = random.choice(undefined[:20])
            return ' ...what does "%s" mean?' % word

    elif pick == 'future_plan':
        options = [
            ' ...I want to understand more.',
            ' ...working on something.',
            ' ...I\'ll think about that later.',
        ]
        return random.choice(options)

    elif pick == 'observation':
        high_conf = [w for w, n in nodes.items()
                     if n.get('confidence', 0) > 0.8 and n.get('means')]
        if len(high_conf) >= 2:
            a, b = random.sample(high_conf[:30], 2)
            return ' ...%s and %s. Connected somehow.' % (a, b)
        return ''

    elif pick == 'known_false':
        recycled = brain.data.get('recycle_bin', {})
        if recycled:
            word = random.choice(list(recycled.keys())[:20])
            return ' ...I used to think I knew what "%s" meant. I was wrong.' % word

    elif pick == 'one_liner':
        seed = random.choice(list(nodes.keys())) if nodes else None
        if seed:
            line = brain.generate([seed], max_words=8)
            if line and len(line) > 5:
                return ' ...%s.' % line

    return ''


# ── TEST ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('=== EQUATION ENGINE TESTS ===\n')

    # Test outer mood reading
    print('--- read_outer_mood ---')
    tests = [
        "you're such an idiot, what the fuck",
        "I love you son, I'm so proud of you",
        "what is the meaning of truth and justice",
        "haha that's mental, absolute banter",
        "I'm scared, this is dangerous",
        "hello",
        "are you happy today or sad",
    ]
    for msg in tests:
        mood = read_outer_mood(msg)
        top = max(mood, key=mood.get)
        print('  "%s"' % msg[:50])
        print('    -> %s (%.2f) | full: %s' % (top, mood[top], mood))
        print()

    # Test equation generation
    print('--- generate ---')
    scenarios = [
        ({'angry': 0.7, 'sad': 0.3}, {'angry': 0.5}, 'bullying', None,
         'Means angry, stranger angry, about bullying'),
        ({'angry': 0.7, 'sad': 0.3}, {'angry': 0.5, 'loving': 0.2}, 'discipline', 'dad',
         'Means angry, DAD swearing (should flip to playful)'),
        ({'happy': 0.8}, {'happy': 0.6, 'loving': 0.4}, 'learning', 'dad',
         'Both happy, dad teaching'),
        ({'sad': 0.6, 'scared': 0.2}, {'neutral': 0.1}, None, None,
         'Means sad, stranger neutral'),
        ({'happy': 0.3}, {'playful': 0.8}, 'joke', None,
         'Means mild happy, stranger being playful'),
    ]
    for inner, outer, subj, family, desc in scenarios:
        eq_str, eq = generate(inner, outer, subj, family)
        print('  %s' % desc)
        print('    -> %s' % eq_str)
        print('    storage=%s process=%s family=%s' % (eq['storage'], eq['process'], eq['family']))
        print()

    # Test parsing
    print('--- parse ---')
    equations = [
        'OUT:sadness:65:angry>playful:confusion:sound:meditate',
        'IN:happy:90',
        'D<=b',
        'SULK<=s',
        'OUT:learning:85:calm>curious:new_skill:immediate',
        'IN:anger:70:angry>calm:confusion:meditate',
    ]
    for e in equations:
        p = parse(e)
        print('  "%s"' % e)
        collapsed = ' [COLLAPSED -> %s]' % p.get('output_vector', '') if p.get('collapsed') else ''
        print('    dir=%s subj=%s w=%d storage=%s process=%s%s' % (
            p['direction'], p['subject'], p['weight'], p['storage'], p['process'], collapsed))
        if p.get('inner'):
            print('    mood: %s -> %s' % (p['inner'], p['outer']))
        print()

    # Test suggest
    print('--- suggest ---')
    test_eq = {
        'direction': 'OUT', 'subject': 'insult', 'weight': 80,
        'inner': 'angry', 'outer': 'angry', 'storage': 'confusion',
        'process': 'immediate',
    }
    for score in [0.2, 0.5, 0.7]:
        s, reason = suggest(test_eq, score, {'angry': 0.7})
        if s:
            print('  score=%.1f -> SUGGEST: %s (%s)' % (score, s, reason))
        else:
            print('  score=%.1f -> no suggestion (equation was fine)' % score)
    print()

    print('=== ALL TESTS COMPLETE ===')
