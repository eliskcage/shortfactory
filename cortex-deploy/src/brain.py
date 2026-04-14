"""
CORTEX BRAIN — Word-level neural network that learns from Dan.

Each word is a lightweight node. Its connections (next/prev word weights)
are heavy. The predictive engine makes it light again — returns only
the 1-2 most probable next words.

Like the ALIVE Brainstem but for language:
- Nodes = words (not shapes)
- Connections = word-pair frequencies (Hebbian: fire together, wire together)
- Prediction = weighted probability of next word
- Grows from nothing as Dan teaches it

Stores on IPFS via Pinata.
"""
import json
import os
import re
import time
import random
import math
import threading
import requests
from pathlib import Path
from collections import defaultdict

STOP_WORDS = {
    'i','me','my','we','our','you','your','he','she','it','they','them','his','her',
    'the','a','an','is','am','are','was','were','be','been','being',
    'have','has','had','do','does','did','will','would','could','should',
    'can','may','might','shall','must','need',
    'to','of','in','on','at','by','for','with','from','up','about',
    'into','through','during','before','after','above','below','between',
    'and','but','or','nor','not','so','yet','both','either','neither',
    'if','then','else','when','while','where','how','what','which','who',
    'that','this','these','those','there','here',
    'just','also','very','really','quite','too','even','still','already',
    'than','more','most','some','any','all','each','every',
    'ok','okay','yeah','yep','nah','nope','yea',
    'like','got','get','go','going','gone','come','came','make','made',
    'take','took','give','gave','say','said','tell','told','know','knew',
    'think','thought','see','saw','look','want','put','let','use','used',
    'thing','things','stuff','way','much','many','lot','bit',
    'cos','coz','because','tho','though','right','well','now',
    'about','over','only','other','same','down','off','out',
    'really','actually','basically','literally','probably','maybe',
    'something','anything','everything','nothing',
}

GREETINGS = {'hello','hi','hey','alright','yo','sup','hiya','oi'}
ROAST_WORDS = {'stupid','dumb','idiot','retard','retarded','moron','thick','useless',
    'rubbish','shit','crap','twat','pillock','muppet','numpty','bellend','tosser','prick','knob'}

# --- SELF-REFLECTION ---
# Negative feedback signals — user telling us we're wrong
NEGATIVE_SIGNALS = {
    'no', 'wrong', 'incorrect', 'nope', 'nah', 'not right', 'that\'s wrong',
    'bullshit', 'rubbish', 'bollocks', 'nonsense', 'thats wrong', 'thats not right',
    'false', 'lies', 'garbage', 'bad', 'terrible answer', 'stop', 'shut up',
}
POSITIVE_SIGNALS = {
    'yes', 'yeah', 'correct', 'right', 'exactly', 'spot on', 'good', 'nice one',
    'perfect', 'yep', 'yea', 'thats right', 'true', 'accurate', 'cheers', 'great',
    'well done', 'smart', 'brilliant', 'ace', 'sound',
}
CONFIDENCE_START = 0.5     # new words start at 50% confidence
CONFIDENCE_BUMP = 0.1      # positive feedback boost
CONFIDENCE_DROP = 0.2      # negative feedback penalty
CONFIDENCE_FLOOR = 0.0     # minimum before recycle
RECYCLE_THRESHOLD = 0.1    # below this = recycled (definition hidden)
RESTORE_THRESHOLD = 0.4    # above this = restored from recycle

COMEBACKS = [
    "Fair enough. I'm literally days old, give us a bloody chance.",
    "Oi, I'm learning here. Teach me something useful instead of chatting shit.",
    "I'll remember everything you teach me. So who's thick really?",
    "Bold words from someone talking to their own sodding voice clone.",
    "You built me mate. If I'm stupid, look in the mirror.",
    "Right right. Keep chatting bollocks, I'm learning your insults too.",
    "Five minutes old and already getting roasted. Piss off.",
    "Oh do one. I'm trying to learn here.",
    "Mate, I've got more brain cells than you've got chat. And I'm made of JSON.",
]

# --- PERSONALITY: SWEARING ---
# Sprinkle expletives naturally. More when angry/silly, less when serious.
SWEAR_INSERTS = [
    'bloody', 'sodding', 'damn', 'flippin', 'ruddy', 'bleeding',
]
SWEAR_PHRASES = [
    "No idea, to be honest.",
    "Bloody hell, that's a new one.",
    "Well shit, I actually know that.",
    "Fair enough.",
    "Bollocks to that.",
    "Right then.",
    "Mate.",
    "For fuck's sake.",
]
# Sentence starters that add character
PERSONALITY_STARTERS = [
    "", "", "", "", "",  # mostly no starter (keep it natural)
    "Right, ", "Look, ", "Mate, ", "Oi, ", "Listen, ",
    "Honestly, ", "Fair enough. ", "Bloody hell. ",
]

# --- SOUND SCRIPTS ---
# Each word is a packet: the word + its described sound.
# These scripts define HOW a word sounds — they impact the structure
# of the word-packet and bias prediction toward matching-sound words.
# Multiple scripts agreeing = more confidence in a pathway.

SOUND_SCRIPTS = ['happy','sad','scared','whisper','angry','serious','silly']

SOUND_TRIGGERS = {
    'happy':   {'amazing','brilliant','love','great','perfect','awesome','beautiful',
                'excellent','fantastic','wonderful','nice','cheers','happy','good','best',
                'incredible','mint','class','sound','boss','mega','wicked','sick','fun',
                'laugh','haha','lol','buzzing','yes','ace','quality','belter'},
    'sad':     {'sad','sorry','miss','lost','gone','alone','empty','cry','crying',
                'depressed','gutted','heartbroken','painful','hurt','regret','shame',
                'unfortunately','tragic','dark','lonely','failed','broken'},
    'scared':  {'scared','afraid','fear','terrified','nervous','worried','panic',
                'horror','creepy','dangerous','threat','risk','warning','careful',
                'watch','paranoid','anxious','freaking'},
    'whisper': {'secret','quiet','shh','shhh','listen','soft','gentle','careful',
                'between','private','hush','psst','close','hidden','subtle'},
    'angry':   {'stupid','dumb','idiot','retard','retarded','moron','thick','useless',
                'rubbish','shit','crap','twat','pillock','hate','angry','furious',
                'annoying','wrong','terrible','awful','worst','rage','fuming',
                'pissed','livid','bollocks','oi','muppet','numpty','bellend'},
    'serious': {'important','critical','real','truth','honest','fact','actually',
                'seriously','listen','understand','focus','matter','need','must',
                'promise','swear','guarantee','absolutely','certain','dead'},
    'silly':   {'haha','lol','mad','mental','bonkers','crazy','daft','ridiculous',
                'hilarious','joke','joking','banter','cheeky','naughty','random',
                'weird','bizarre','nuts','insane','bananas','loopy'},
}

SOUND_DECAY = 0.12       # sound scripts decay each turn
SOUND_TRIGGER_BOOST = 0.35
SOUND_WORD_BOOST = 2.0   # prediction multiplier for matching-sound words

# --- WORD SCRIPTS ---
# Each word carries multiple neural-net micro-scripts that ALL vote during prediction.
# More scripts agreeing on a candidate word = more confident pathway.
# Scripts accumulate Hebbianly — words that appear in a role get that role strengthened.
# The word stays lightweight, but its scripts do the heavy lifting.

ROLE_HINTS = {
    'det':      {'the','a','an','this','that','these','those','my','your','his','her','its','our','their','some','any','no','every','each'},
    'prep':     {'in','on','at','to','for','with','from','by','about','into','through','during','before','after','above','below','between','under','over','around','without','within','along','toward','towards','across','behind','against','upon','onto','beside','near','off','out','up','down'},
    'conj':     {'and','but','or','nor','so','yet','because','although','while','if','when','than','unless','since','whether'},
    'pron':     {'i','me','my','we','us','our','you','your','he','him','his','she','her','it','its','they','them','their','myself','yourself','itself','ourselves','themselves'},
    'question': {'what','where','when','who','why','how','which','whom','whose'},
    'modal':    {'can','could','will','would','shall','should','may','might','must','need'},
    'neg':      {'not','no','never','neither','nor','nothing','nobody','nowhere','none','cant','dont','wont','isnt','arent','wasnt','werent','havent','hasnt','didnt','doesnt','wouldnt','couldnt','shouldnt'},
    'aux':      {'is','am','are','was','were','be','been','being','has','have','had','do','does','did'},
}

# Script boost strength — how much word scripts influence prediction
SCRIPT_BOOST = 1.5

# --- ABILITY TREE ---
# Each ability unlocks new behaviors. Requirements checked against brain stats.
# Like an RPG skill tree — the brain levels up as it learns.
ABILITY_TREE = {
    'basic_vocab': {
        'name': 'Basic Vocabulary',
        'requires': {'defined': 50},
        'desc': 'Knows 50+ words with definitions',
    },
    'conversational': {
        'name': 'Conversational',
        'requires': {'defined': 100, 'messages': 50},
        'desc': 'Can hold a basic conversation',
    },
    'deep_vocab': {
        'name': 'Deep Vocabulary',
        'requires': {'defined': 500},
        'desc': 'Knows 500+ words — wide knowledge base',
    },
    'emotional': {
        'name': 'Emotional Intelligence',
        'requires': {'defined': 100, 'messages': 100},
        'desc': 'Reads emotional tone, responds appropriately',
    },
    'witty': {
        'name': 'Wit Engine',
        'requires': {'defined': 200, 'clusters': 3, 'messages': 150},
        'desc': 'Makes unexpected connections, surprises you',
    },
    'curious_mind': {
        'name': 'Active Curiosity',
        'requires': {'auto_learned': 30},
        'desc': 'Actively seeks knowledge, asks smart questions',
    },
    'self_aware': {
        'name': 'Self-Awareness',
        'requires': {'defined': 200, 'messages': 200},
        'desc': 'Knows what it knows and what it doesn\'t',
    },
    'storyteller': {
        'name': 'Storytelling',
        'requires': {'defined': 300, 'trigrams': 500},
        'desc': 'Can weave words into short stories',
    },
    'debater': {
        'name': 'Debate Mode',
        'requires': {'defined': 400, 'clusters': 5},
        'desc': 'Can argue a point using knowledge',
    },
    'teacher': {
        'name': 'Teacher Mode',
        'requires': {'defined': 300, 'understanding_deep': 10},
        'desc': 'Can teach others what it deeply understands',
    },
    'sarcasm': {
        'name': 'Sarcasm Engine',
        'requires': {'messages': 500, 'defined': 300},
        'desc': 'Detects and generates sarcasm',
    },
    'philosopher': {
        'name': 'Philosopher',
        'requires': {'defined': 600, 'clusters': 8, 'understanding_deep': 20},
        'desc': 'Can reason about abstract concepts',
    },
    'memory_palace': {
        'name': 'Memory Palace',
        'requires': {'conversation_log_size': 100},
        'desc': 'Recalls past conversations and builds on them',
    },
    'pattern_master': {
        'name': 'Pattern Master',
        'requires': {'trigrams': 2000, 'defined': 400},
        'desc': 'Spots and uses language patterns fluently',
    },
    'polymath': {
        'name': 'Polymath',
        'requires': {'defined': 800, 'clusters': 10, 'understanding_deep': 30},
        'desc': 'Cross-domain knowledge synthesis',
    },
}

# --- SEMANTIC RELATIONSHIP TYPES ---
# These go beyond "words appear near each other" into actual understanding
REL_TYPES = {
    'synonym':  'means the same as',
    'antonym':  'means the opposite of',
    'is_a':     'is a type of',
    'has_a':    'has or contains',
    'part_of':  'is part of',
    'causes':   'causes or leads to',
    'used_for': 'is used for',
    'example':  'is an example of',
}

# Patterns to extract relationships from definitions
# Each: (regex, rel_type, which_group_is_target)
DEF_PATTERNS = [
    (r'^(?:a |an |the )?(?:type|kind|form|sort) of (\w+)', 'is_a', 1),
    (r'^(?:a |an |the )?(\w+) (?:that|which|who)', 'is_a', 1),
    (r'^(?:to |the act of )?(\w+)(?:ing|tion|ment)', 'is_a', None),  # verb form
    (r'(?:opposite|contrary|reverse) of (\w+)', 'antonym', 1),
    (r'(?:same as|another word for|also known as|means) (\w+)', 'synonym', 1),
    (r'(?:part of|component of|piece of|section of) (?:a |an |the )?(\w+)', 'part_of', 1),
    (r'(?:used (?:for|to)|helps to) (\w+)', 'used_for', 1),
    (r'(?:causes?|leads? to|results? in) (\w+)', 'causes', 1),
    (r'(?:contains?|has|includes?) (?:a |an |the )?(\w+)', 'has_a', 1),
]

# Correction patterns — user telling brain a connection is wrong
CORRECTION_PATTERNS = [
    r'(\w+) (?:does not|doesn\'t|dont|don\'t|doesnt) (?:connect|relate|link|mean) (?:to )?(\w+)',
    r'(\w+) is not (\w+)',
    r'(\w+) (?:isn\'t|isnt) (\w+)',
    r'no[,.]?\s*(\w+) (?:and|&) (\w+) (?:are not|aren\'t|arent) (?:related|connected)',
]


class CortexBrain:
    """
    Word-level neural network.

    Each word node:
      - means: what Dan taught it this word means (if taught)
      - next: {word: count} — bigram frequencies (word -> next_word)
      - prev: {word: count} — reverse bigrams (prev_word -> word)
      - freq: how often this word appears in Dan's speech
      - learned: timestamp

    The connections are the heavy part. Prediction returns only top 1-2.
    """

    def __init__(self, data_dir, pinata_jwt=None, name='Cortex'):
        self.data_dir = Path(data_dir)
        self.brain_file = self.data_dir / 'brain.json'
        self.pinata_jwt = pinata_jwt
        self.name = name           # hemisphere identity — "Left Hemisphere" or "Right Hemisphere"
        self._save_lock = threading.Lock()
        self.state = None          # None or 'teaching'
        self.teaching_word = None
        self.last_topic = None     # tracks what word we last talked about (for feedback)
        self.last_topics = []      # recent topics for multi-word flagging
        self.context = []          # short-term memory: last 10 exchanges
        self._last_user_msg = ''   # for context logging
        self.verbosity = 1.0       # 0.0 = terse, 1.0 = normal, 2.0 = verbose — adjustable via advice
        # Sound state — competing emotional scripts that shape word delivery
        self.sound = {s: 0.0 for s in SOUND_SCRIPTS}
        self.sound['serious'] = 0.3  # starts a bit serious — it's learning
        self.load()

    # --- Persistence ---

    def load(self):
        if self.brain_file.exists():
            with open(self.brain_file, encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'nodes': {},       # word -> {means, next, prev, freq, learned}
                'trigrams': {},    # "w1 w2" -> {w3: count} for better prediction
                'facts': [],       # general facts Dan teaches
                'ipfs': {'cid': None, 'last_save': None},
                'stats': {'messages': 0, 'nodes': 0, 'connections': 0, 'questions_asked': 0}
            }
        self.data.setdefault('nodes', {})
        self.data.setdefault('trigrams', {})
        self.data.setdefault('facts', [])
        self.data.setdefault('stats', {})
        self.data.setdefault('recycle_bin', {})      # word -> {means, recycled_at, flags, reason}
        self.data.setdefault('conversation_log', []) # persistent chat memory
        self.data.setdefault('clusters', {})          # cluster_name -> [words]
        self.data.setdefault('compounds', {})         # "w1_w2" -> frequency count
        n = len(self.data['nodes'])
        c = sum(len(v.get('next', {})) for v in self.data['nodes'].values())
        print(f'[BRAIN] Loaded: {n} word nodes, {c} connections')

    def save(self):
        with self._save_lock:
            try:
                nodes = dict(self.data.get('nodes', {}))
                self.data['stats']['nodes'] = len(nodes)
                self.data['stats']['connections'] = sum(len(v.get('next', {})) for v in nodes.values())
            except RuntimeError:
                pass
            for attempt in range(3):
                try:
                    blob = json.dumps(self.data, indent=2, ensure_ascii=False)
                    break
                except (RuntimeError, ValueError):
                    if attempt == 2:
                        return
                    time.sleep(0.05)
            tmp = str(self.brain_file) + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(blob)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, str(self.brain_file))

    def save_to_ipfs(self):
        if not self.pinata_jwt:
            return None
        try:
            headers = {'Authorization': f'Bearer {self.pinata_jwt}'}
            brain_json = json.dumps(self.data, indent=2, ensure_ascii=False)
            files = {'file': ('brain.json', brain_json, 'application/json')}
            metadata = json.dumps({
                'name': f'cortex-brain-{time.strftime("%Y%m%d-%H%M%S")}',
                'keyvalues': {'type': 'cortex-brain', 'words': str(len(self.data['nodes']))}
            })
            resp = requests.post(
                'https://api.pinata.cloud/pinning/pinFileToIPFS',
                headers=headers, files=files,
                data={'pinataMetadata': metadata}, timeout=30
            )
            if resp.status_code == 200:
                cid = resp.json()['IpfsHash']
                self.data['ipfs']['cid'] = cid
                self.data['ipfs']['last_save'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.save()
                print(f'[BRAIN] IPFS saved: {cid} ({len(self.data["nodes"])} nodes)')
                return cid
            print(f'[BRAIN] IPFS failed: {resp.status_code}')
        except Exception as e:
            print(f'[BRAIN] IPFS error: {e}')
        return None

    def load_from_ipfs(self, cid):
        try:
            resp = requests.get(f'https://gateway.pinata.cloud/ipfs/{cid}', timeout=30)
            if resp.status_code == 200:
                self.data = resp.json()
                self.save()
                print(f'[BRAIN] Loaded from IPFS: {cid}')
                return True
        except Exception as e:
            print(f'[BRAIN] IPFS load error: {e}')
        return False

    # --- Tokenization ---

    def tokenize(self, text):
        text = text.lower().strip()
        # Keep apostrophes in words, remove other punctuation
        text = re.sub(r"[^\w\s']", ' ', text)
        return [w.strip("'") for w in text.split() if w.strip("'")]

    def keywords(self, text):
        return [w for w in self.tokenize(text) if w not in STOP_WORDS and len(w) > 2]

    # --- Web Lookup ---

    def _trim_definition(self, text, max_words=12):
        """Trim a definition to just the key words needed. No essays."""
        text = text.strip()
        # Take first sentence only
        for sep in ['. ', '.\n', '; ']:
            if sep in text:
                text = text[:text.index(sep)]
                break
        # Strip common wiki prefixes like "X is a" or "X refers to"
        for prefix in ['is a ', 'is an ', 'is the ', 'are ', 'was a ', 'was an ',
                        'refers to ', 'describes ', 'means ']:
            lower = text.lower()
            idx = lower.find(prefix)
            if idx != -1 and idx < 30:
                text = text[idx + len(prefix):]
                break
        # Cap at max words
        words = text.split()
        if len(words) > max_words:
            text = ' '.join(words[:max_words])
        return text.strip(' ,.')

    def lookup_word(self, word):
        """
        Search internet for a SHORT definition — just enough to define the word.
        Returns a few words, not sentences.
        """
        # Wikipedia REST API (free, no key)
        try:
            resp = requests.get(
                f'https://en.wikipedia.org/api/rest_v1/page/summary/{word}',
                headers={'User-Agent': 'CortexBrain/1.0'},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get('extract', '')
                if extract and len(extract) > 10 and data.get('type') != 'disambiguation':
                    short = self._trim_definition(extract)
                    if short and len(short) > 3:
                        print(f'[LOOKUP] Wikipedia: "{word}" = "{short}"')
                        return short
        except Exception as e:
            print(f'[LOOKUP] Wikipedia error: {e}')

        # DuckDuckGo Instant Answer (free, no key)
        try:
            resp = requests.get(
                'https://api.duckduckgo.com/',
                params={'q': f'define {word}', 'format': 'json', 'no_html': '1', 'skip_disambig': '1'},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                for field in ['AbstractText', 'Definition', 'Answer']:
                    text = data.get(field, '')
                    if text and len(text) > 5:
                        short = self._trim_definition(text)
                        if short and len(short) > 3:
                            print(f'[LOOKUP] DDG: "{word}" = "{short}"')
                            return short
        except Exception as e:
            print(f'[LOOKUP] DDG error: {e}')

        print(f'[LOOKUP] Nothing found for "{word}"')
        return None

    def auto_learn(self, word, source='internet'):
        """Store a word definition from web lookup."""
        definition = self.lookup_word(word)
        if definition:
            if word not in self.data['nodes']:
                self.data['nodes'][word] = {
                    'means': None, 'next': {}, 'prev': {},
                    'freq': 1, 'learned': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            self.data['nodes'][word]['means'] = definition
            self.data['nodes'][word]['source'] = source
            self.learn_sequence(f"{word} means {definition}")
            # Parse definition for semantic understanding
            self._parse_definition(word, definition)
            self.save()
            print(f'[BRAIN] Auto-learned: "{word}" from {source}')
            return definition
        return None

    # --- Neural Learning (Hebbian) ---

    def learn_sequence(self, text):
        """
        Learn word connections from a text sequence.
        Hebbian: words that appear together get wired together.
        Builds bigram + trigram frequency tables.
        """
        tokens = self.tokenize(text)
        if len(tokens) < 2:
            return

        for i, word in enumerate(tokens):
            # Ensure node exists
            if word not in self.data['nodes']:
                self.data['nodes'][word] = {
                    'means': None,
                    'next': {},
                    'prev': {},
                    'freq': 0,
                    'learned': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            node = self.data['nodes'][word]
            node['freq'] = node.get('freq', 0) + 1

            # Bigram: this word -> next word
            if i < len(tokens) - 1:
                nxt = tokens[i + 1]
                node['next'][nxt] = node['next'].get(nxt, 0) + 1

            # Reverse bigram: prev word -> this word
            if i > 0:
                prv = tokens[i - 1]
                node['prev'][prv] = node['prev'].get(prv, 0) + 1

            # Trigram: "word1 word2" -> word3
            if i < len(tokens) - 2:
                key = f"{tokens[i]} {tokens[i+1]}"
                if key not in self.data['trigrams']:
                    self.data['trigrams'][key] = {}
                w3 = tokens[i + 2]
                self.data['trigrams'][key][w3] = self.data['trigrams'][key].get(w3, 0) + 1

            # --- Auto-tag word scripts (Hebbian: learn roles from position) ---
            # Position scripts
            if i == 0:
                self._inc_script(word, 'starter')
            if i == len(tokens) - 1:
                self._inc_script(word, 'ender')

            # Role hints — known grammatical roles
            for role, role_words in ROLE_HINTS.items():
                if word in role_words:
                    self._inc_script(word, role)

            # After-role: learn what role tends to precede this word
            if i > 0:
                prev_word = tokens[i - 1]
                for role, role_words in ROLE_HINTS.items():
                    if prev_word in role_words:
                        self._inc_script(word, f'after_{role}')

        self.save()

    # --- Sound Engine ---
    # Each word-packet carries its sound. These scripts compete to
    # shape which words get selected AND how they should be delivered.

    def update_sound(self, tokens):
        """
        Update sound state from input words.
        Multiple scripts compete. More scripts firing = more confident pathway.
        """
        token_set = set(tokens)

        # Decay all sound scripts toward 0
        for s in self.sound:
            self.sound[s] = max(0, self.sound[s] - SOUND_DECAY)

        # Boost from trigger words
        for script, triggers in SOUND_TRIGGERS.items():
            hits = token_set & triggers
            if hits:
                boost = len(hits) * SOUND_TRIGGER_BOOST
                self.sound[script] = min(1.0, self.sound[script] + boost)

        # Hebbian: tag each word with current sound context
        # Words learn which emotional sound they belong to
        dominant = self.dominant_sound()
        if dominant and dominant[1] > 0.25:
            for token in tokens:
                if token in self.data['nodes']:
                    node = self.data['nodes'][token]
                    if 'sound' not in node:
                        node['sound'] = {}
                    sname = dominant[0]
                    node['sound'][sname] = node['sound'].get(sname, 0) + 1

    def dominant_sound(self):
        """Return (script_name, intensity) of strongest active sound script."""
        if not self.sound:
            return None
        best = max(self.sound.items(), key=lambda x: x[1])
        return best if best[1] > 0.1 else None

    def active_sounds(self):
        """Return all active sound scripts sorted by intensity."""
        return sorted(
            [(s, v) for s, v in self.sound.items() if v > 0.1],
            key=lambda x: x[1], reverse=True
        )

    def sound_boost_predictions(self, predictions):
        """
        Boost word probabilities based on active sound scripts.
        Each script is a competing voice. When multiple scripts agree
        that a word fits, confidence in that pathway goes UP.
        """
        active = self.active_sounds()
        if not active:
            return predictions

        boosted = []
        for word, prob in predictions:
            multiplier = 1.0
            node = self.data['nodes'].get(word)
            scripts_agreeing = 0

            for script_name, intensity in active:
                word_match = False
                # Check learned sound association
                if node and node.get('sound', {}).get(script_name, 0) > 0:
                    assoc = node['sound'][script_name]
                    multiplier *= 1.0 + (SOUND_WORD_BOOST * intensity * min(assoc / 5.0, 1.0))
                    word_match = True
                # Check if word is a direct trigger
                if word in SOUND_TRIGGERS.get(script_name, set()):
                    multiplier *= (1.0 + intensity * 0.5)
                    word_match = True
                if word_match:
                    scripts_agreeing += 1

            # Bonus: more scripts agreeing = more confidence
            if scripts_agreeing > 1:
                multiplier *= (1.0 + scripts_agreeing * 0.3)

            boosted.append((word, prob * multiplier))

        # Renormalize
        total = sum(p for _, p in boosted)
        if total > 0:
            boosted = [(w, p / total) for w, p in boosted]
        return boosted

    # --- Word Scripts Engine ---
    # Each word carries micro neural-net scripts that vote during prediction.
    # The word is lightweight. The scripts do the heavy lifting.

    def _inc_script(self, word, script_name, amount=1):
        """Increment a script weight on a word. Hebbian accumulation."""
        node = self.data['nodes'].get(word)
        if not node:
            return
        if 'scripts' not in node:
            node['scripts'] = {}
        node['scripts'][script_name] = node['scripts'].get(script_name, 0) + amount

    def set_role(self, word, role, strength=5):
        """Manually tag a word's grammatical role (strong signal)."""
        self._inc_script(word, role, strength)

    def bulk_set_roles(self, role_map):
        """Set roles for many words. role_map = {word: role} or {word: [roles]}."""
        for word, roles in role_map.items():
            if isinstance(roles, str):
                roles = [roles]
            for role in roles:
                self.set_role(word, role)

    def get_word_pos(self, word):
        """Infer part-of-speech for a word from its accumulated scripts data.
        Returns: 'noun'|'verb'|'adj'|'adv'|'det'|'prep'|'conj'|'pron'|'aux'|'modal'|None"""
        word = word.lower()
        # 1. Deterministic: known function words
        for role, words in ROLE_HINTS.items():
            if word in words:
                return role

        node = self.data['nodes'].get(word)
        if not node:
            return None

        scripts = node.get('scripts', {})
        means = (node.get('means') or '').lower()

        # 2. Score content POS from scripts
        noun_score = scripts.get('after_det', 0) * 2 + scripts.get('after_prep', 0) * 1.5
        verb_score = (scripts.get('after_pron', 0) * 2 + scripts.get('after_aux', 0) * 2
                      + scripts.get('after_modal', 0) * 1.5 + scripts.get('after_neg', 0))
        adj_score = scripts.get('after_det', 0) * 0.5

        # 3. Definition heuristic boost
        if means.startswith('to '):
            verb_score += 5
        if any(means.startswith(p) for p in ('a ', 'an ', 'the ', 'type of', 'kind of')):
            noun_score += 3
        if any(means.startswith(p) for p in ('describing ', 'having ', 'full of', 'relating to')):
            adj_score += 4

        scores = {'noun': noun_score, 'verb': verb_score, 'adj': adj_score}
        best = max(scores, key=scores.get)
        if scores[best] < 2:
            return None  # not enough data
        return best

    def bulk_import(self, entries):
        """Bulk import word nodes. entries = list of dicts with word data.
        Merges with existing nodes — enriches, never overwrites definitions.
        Returns count of new words, updated words."""
        new_count = 0
        updated_count = 0
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        for entry in entries:
            word = entry.get('word', '').lower().strip()
            if not word or len(word) < 2:
                continue

            node = self.data['nodes'].get(word)
            is_new = node is None

            if is_new:
                node = {'means': None, 'next': {}, 'prev': {}, 'freq': 0, 'learned': now}
                self.data['nodes'][word] = node
                new_count += 1
            else:
                updated_count += 1

            # Set definition (don't overwrite existing)
            if entry.get('means') and not node.get('means'):
                node['means'] = entry['means'][:200]

            # Merge bigram connections
            for nw, cnt in entry.get('next', {}).items():
                node['next'][nw] = node['next'].get(nw, 0) + cnt
            for pw, cnt in entry.get('prev', {}).items():
                node['prev'][pw] = node['prev'].get(pw, 0) + cnt

            # Increment frequency
            node['freq'] = node.get('freq', 0) + entry.get('freq', 1)

            # Set confidence (don't lower existing)
            if entry.get('confidence'):
                node['confidence'] = max(node.get('confidence', 0.5), entry['confidence'])

            # Set source if not set
            if entry.get('source') and not node.get('source'):
                node['source'] = entry['source']

            # Merge scripts (additive)
            if entry.get('scripts'):
                if 'scripts' not in node:
                    node['scripts'] = {}
                for role, weight in entry['scripts'].items():
                    node['scripts'][role] = node['scripts'].get(role, 0) + weight

            # Merge sound associations (additive)
            if entry.get('sound'):
                if 'sound' not in node:
                    node['sound'] = {}
                for snd, cnt in entry['sound'].items():
                    node['sound'][snd] = node['sound'].get(snd, 0) + cnt

            # Merge relationships (append unique)
            if entry.get('rels'):
                if 'rels' not in node:
                    node['rels'] = {}
                for rel_type, targets in entry['rels'].items():
                    if rel_type not in node['rels']:
                        node['rels'][rel_type] = []
                    for t in targets:
                        if t not in node['rels'][rel_type]:
                            node['rels'][rel_type].append(t)

            # Set understanding (don't downgrade)
            depth_order = {'shallow': 0, 'moderate': 1, 'deep': 2}
            if entry.get('understanding'):
                existing = depth_order.get(node.get('understanding', ''), -1)
                incoming = depth_order.get(entry['understanding'], -1)
                if incoming > existing:
                    node['understanding'] = entry['understanding']

            # Set cluster
            if entry.get('cluster') and not node.get('cluster'):
                node['cluster'] = entry['cluster']

        # Update stats
        self.data['stats']['nodes'] = len(self.data['nodes'])
        self.data['stats']['connections'] = sum(
            len(n.get('next', {})) + len(n.get('prev', {}))
            for n in self.data['nodes'].values()
        )

        return new_count, updated_count

    # --- Self-Modification Engine ---
    # The brain evaluates its own output, strengthens good pathways,
    # weakens bad ones, and consolidates memory over time.

    GOOD_TRANSITIONS = {
        ('det','noun'), ('det','adj'), ('adj','noun'), ('pron','verb'),
        ('noun','verb'), ('verb','det'), ('verb','noun'), ('verb','adv'),
        ('verb','adj'), ('verb','prep'), ('adv','verb'), ('adv','adj'),
        ('prep','det'), ('prep','noun'), ('prep','adj'), ('conj','det'),
        ('conj','pron'), ('conj','noun'), ('noun','prep'), ('noun','conj'),
        ('adj','conj'), ('adj','prep'),
    }

    def self_score(self, response):
        """Score own output quality. Returns dict with component scores and total 0.0-1.0."""
        tokens = self.tokenize(response)
        if len(tokens) < 2:
            return {'total': 0.0, 'grammar': 0, 'repetition': 0, 'confidence': 0, 'grounding': 0, 'length': 0}

        nodes = self.data['nodes']

        # 1. Grammar coherence — do POS transitions make sense?
        good_trans = 0
        total_trans = 0
        for i in range(len(tokens) - 1):
            pos_a = self.get_word_pos(tokens[i])
            pos_b = self.get_word_pos(tokens[i + 1])
            if pos_a and pos_b:
                total_trans += 1
                if (pos_a, pos_b) in self.GOOD_TRANSITIONS:
                    good_trans += 1
        grammar = (good_trans / total_trans) if total_trans > 0 else 0.5

        # 2. Repetition penalty — repeated content words are bad
        content_words = [t for t in tokens if len(t) > 3 and t not in STOP_WORDS]
        unique_ratio = len(set(content_words)) / max(len(content_words), 1)
        repetition = unique_ratio

        # 3. Confidence — average confidence of words used
        confs = [nodes[t].get('confidence', 0.5) for t in tokens if t in nodes]
        confidence = sum(confs) / max(len(confs), 1)

        # 4. Grounding — % of words with definitions
        defined = sum(1 for t in tokens if t in nodes and nodes[t].get('means'))
        grounding = defined / max(len(tokens), 1)

        # 5. Length — sweet spot 5-25 words
        if len(tokens) < 5:
            length = len(tokens) / 5
        elif len(tokens) <= 25:
            length = 1.0
        else:
            length = max(0, 1.0 - (len(tokens) - 25) / 25)

        total = (grammar * 0.25 + repetition * 0.20 + confidence * 0.20
                 + grounding * 0.20 + length * 0.15)
        return {
            'total': round(total, 3),
            'grammar': round(grammar, 3),
            'repetition': round(repetition, 3),
            'confidence': round(confidence, 3),
            'grounding': round(grounding, 3),
            'length': round(length, 3),
        }

    def self_reinforce(self, response, score):
        """Adjust own weights based on quality score of generated output."""
        tokens = self.tokenize(response)
        if len(tokens) < 3:
            return

        total = score['total']

        # ALWAYS learn own sentence patterns (the key missing piece)
        self.learn_sequence(response)

        if total >= 0.6:
            # GOOD output — strengthen pathways
            boost = 0.02 + (total - 0.6) * 0.05
            for t in tokens:
                node = self.data['nodes'].get(t)
                if node and node.get('means'):
                    node['confidence'] = min(1.0, node.get('confidence', 0.5) + boost)
            # Extra bigram reinforcement for good sequences
            for i in range(len(tokens) - 1):
                node = self.data['nodes'].get(tokens[i])
                if node:
                    node['next'][tokens[i + 1]] = node['next'].get(tokens[i + 1], 0) + 1

        elif total < 0.3:
            # BAD output — weaken pathways (gently)
            drop = 0.01 + (0.3 - total) * 0.03
            for t in tokens:
                node = self.data['nodes'].get(t)
                if node and node.get('means'):
                    node['confidence'] = max(0.1, node.get('confidence', 0.5) - drop)

        # Tag quality onto last conversation log entry
        log = self.data.get('conversation_log', [])
        if log:
            log[-1]['quality'] = score

    def memory_consolidate(self):
        """Review recent conversation log. Strengthen patterns that work, weaken those that don't."""
        log = self.data.get('conversation_log', [])
        if len(log) < 5:
            return {'consolidated': 0}

        recent = log[-50:]
        word_scores = {}

        for entry in recent:
            quality = entry.get('quality')
            if not quality:
                continue
            total = quality.get('total', 0.5)
            tokens = self.tokenize(entry.get('response', ''))
            for t in tokens:
                if len(t) > 2 and t not in STOP_WORDS:
                    if t not in word_scores:
                        word_scores[t] = []
                    word_scores[t].append(total)

        consolidated = 0
        for word, scores in word_scores.items():
            if len(scores) < 3:
                continue
            avg = sum(scores) / len(scores)
            node = self.data['nodes'].get(word)
            if not node:
                continue

            if avg >= 0.65 and len(scores) >= 5:
                node['confidence'] = min(1.0, node.get('confidence', 0.5) + 0.05)
                consolidated += 1
            elif avg < 0.3 and len(scores) >= 3:
                node['confidence'] = max(0.1, node.get('confidence', 0.5) - 0.05)
                consolidated += 1

        self.data.setdefault('self_mod', {})
        self.data['self_mod']['last_consolidation'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.data['self_mod']['total_consolidations'] = self.data['self_mod'].get('total_consolidations', 0) + 1
        self.data['self_mod']['last_consolidated_count'] = consolidated

        return {'consolidated': consolidated}

    def self_correct(self, context_tokens, wrong_word, right_word):
        """When user corrects output: weaken wrong path, strengthen right path."""
        wrong_word = wrong_word.lower()
        right_word = right_word.lower()

        for t in context_tokens:
            node = self.data['nodes'].get(t)
            if not node:
                continue
            if wrong_word in node.get('next', {}):
                node['next'][wrong_word] = max(0, node['next'][wrong_word] - 2)
            node['next'][right_word] = node['next'].get(right_word, 0) + 3

        self.flag_word(wrong_word, 'self_correction')
        self.boost_word(right_word)

    def script_boost_predictions(self, predictions, context):
        """
        Boost candidate words based on their scripts matching the current context.
        Each script is a mini neural net on the word — all vote simultaneously.
        More scripts agreeing = more confident pathway.
        """
        if not predictions or not context:
            return predictions

        # Determine what scripts the CONTEXT activates
        context_scripts = {}

        # Position: near start of generation
        if len(context) <= 2:
            context_scripts['starter'] = 1.0

        # What role was the previous word?
        prev = context[-1]
        prev_node = self.data['nodes'].get(prev, {})
        prev_scripts = prev_node.get('scripts', {})

        # Check role hints for previous word
        for role, words in ROLE_HINTS.items():
            if prev in words or prev_scripts.get(role, 0) > 2:
                context_scripts[f'after_{role}'] = 1.0

        # Also pass through the previous word's strongest learned role
        if prev_scripts:
            best_role = max(prev_scripts.items(), key=lambda x: x[1])
            if best_role[1] > 2 and not best_role[0].startswith('after_'):
                context_scripts[f'after_{best_role[0]}'] = 0.5

        if not context_scripts:
            return predictions

        boosted = []
        for word, prob in predictions:
            node = self.data['nodes'].get(word, {})
            scripts = node.get('scripts', {})
            multiplier = 1.0
            matches = 0

            for ctx_script, ctx_strength in context_scripts.items():
                script_val = scripts.get(ctx_script, 0)
                if script_val > 0:
                    strength = min(script_val / 5.0, 2.0) * ctx_strength
                    multiplier *= (1.0 + strength * SCRIPT_BOOST * 0.3)
                    matches += 1

            # Bonus: more scripts agreeing = more confidence in this pathway
            if matches > 1:
                multiplier *= (1.0 + matches * 0.15)

            boosted.append((word, prob * multiplier))

        # Renormalize
        total = sum(p for _, p in boosted)
        if total > 0:
            boosted = [(w, p / total) for w, p in boosted]
        return sorted(boosted, key=lambda x: x[1], reverse=True)

    # --- Prediction Engine ---

    def predict_next(self, word, n=3):
        """Predict most likely next word(s) after 'word'. Returns [(word, probability), ...]"""
        node = self.data['nodes'].get(word)
        if not node or not node.get('next'):
            return []
        total = sum(node['next'].values())
        ranked = sorted(node['next'].items(), key=lambda x: x[1], reverse=True)
        return [(w, count / total) for w, count in ranked[:n]]

    def predict_trigram(self, w1, w2, n=3):
        """Predict next word given two previous words. More accurate than bigram."""
        key = f"{w1} {w2}"
        tri = self.data['trigrams'].get(key)
        if not tri:
            return self.predict_next(w2, n)  # fallback to bigram
        total = sum(tri.values())
        ranked = sorted(tri.items(), key=lambda x: x[1], reverse=True)
        return [(w, count / total) for w, count in ranked[:n]]

    def weighted_pick(self, predictions, temperature=0.8):
        """Pick from predictions with temperature. Lower = more predictable."""
        if not predictions:
            return None
        words, probs = zip(*predictions)
        # Apply temperature
        adjusted = [p ** (1.0 / temperature) for p in probs]
        total = sum(adjusted)
        adjusted = [p / total for p in adjusted]
        r = random.random()
        cumulative = 0
        for word, prob in zip(words, adjusted):
            cumulative += prob
            if r <= cumulative:
                return word
        return words[0]

    def generate(self, seed_words, max_words=20):
        """
        Generate text by chaining mood-boosted predictions.
        Stops when confidence drops — keeps it short if unsure.
        Multiple scripts (bigram, trigram, mood, confidence) all
        affect the probability. More scripts agreeing = more confident pathway.
        """
        if isinstance(seed_words, str):
            seed_words = [seed_words]

        result = list(seed_words)
        if len(result) == 0:
            return ""

        MIN_CONFIDENCE = 0.15  # stop generating if best prediction below this

        for _ in range(max_words):
            # Try trigram first (more confident), then bigram
            if len(result) >= 2:
                preds = self.predict_trigram(result[-2], result[-1])
            else:
                preds = self.predict_next(result[-1])

            if not preds:
                break

            # Apply sound script boost — emotional delivery shapes word selection
            preds = self.sound_boost_predictions(preds)

            # Apply word script boost — role, position, context all vote
            preds = self.script_boost_predictions(preds, result)

            # Check confidence — if top prediction is weak, stop (don't jibber)
            top_prob = preds[0][1] if preds else 0
            if top_prob < MIN_CONFIDENCE and len(result) > 3:
                break

            next_word = self.weighted_pick(preds)
            if not next_word or next_word in result[-3:]:
                break
            result.append(next_word)

        return ' '.join(result)

    # --- Main Conversation ---

    def process(self, user_msg):
        """Process with full context tracking, curiosity, and compound detection."""
        self._last_user_msg = user_msg

        # Detect compound phrases (feature 6)
        self._detect_compounds(user_msg)

        # Resolve context from previous exchanges (feature 1)
        user_msg = self._resolve_context(user_msg)

        # Core processing
        self._or_gate_fired = False
        response = self._process_core(user_msg)

        # Track in short-term context (feature 1)
        self.context.append({
            'user': self._last_user_msg,
            'response': response[:200],
            'topics': list(self.last_topics),
            'time': time.strftime('%H:%M:%S'),
        })
        if len(self.context) > 10:
            self.context = self.context[-10:]

        # Persistent conversation log (feature 5)
        self.data['conversation_log'].append({
            'user': self._last_user_msg[:100],
            'response': response[:200],
            'topics': list(self.last_topics),
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        if len(self.data['conversation_log']) > 200:
            self.data['conversation_log'] = self.data['conversation_log'][-200:]

        # Apply personality layers — SKIP if OR gate fired (choice is sacred)
        if not self._or_gate_fired:
            response = self._make_witty(response, self.last_topics)
            response = self._make_sarcastic(response)
            response = self._make_sweary(response)
            response = self._self_aware_caveat(response)

            # Maybe append a curiosity question (feature 2)
            response = self._maybe_ask_curious(response)
        else:
            # OR gate fired — no personality, no curiosity, clean commit only
            pass

        # --- Self-Modification Loop ---
        score = self.self_score(response)
        self.self_reinforce(response, score)
        if len(self.data.get('conversation_log', [])) % 10 == 0:
            self.memory_consolidate()

        # Check abilities periodically (every 10 messages)
        if self.data['stats'].get('messages', 0) % 10 == 0:
            self.check_abilities()

        self.save()
        return response

    def _process_core(self, user_msg):
        """Core conversation engine. Learn from input. Respond."""
        self.data['stats']['messages'] = self.data['stats'].get('messages', 0) + 1
        tokens = self.tokenize(user_msg)
        kws = self.keywords(user_msg)
        msg_lower = user_msg.lower().strip()

        # Always learn the word sequence (Hebbian wiring)
        self.learn_sequence(user_msg)

        # Update sound scripts — competing emotional delivery states
        self.update_sound(tokens)

        # --- TEACHING MODE ---
        if self.state == 'teaching' and self.teaching_word:
            word = self.teaching_word
            self.state = None
            self.teaching_word = None
            was_recycled = word in self.data.get('recycle_bin', {})
            # Store the meaning
            if word in self.data['nodes']:
                self.data['nodes'][word]['means'] = user_msg.strip()
                # Human-taught = high confidence (they corrected or taught directly)
                self.data['nodes'][word]['confidence'] = 0.8
                self.data['nodes'][word]['source'] = 'human'
                self.data['nodes'][word]['recycled'] = False
            else:
                self.data['nodes'][word] = {
                    'means': user_msg.strip(),
                    'next': {}, 'prev': {},
                    'freq': 1,
                    'confidence': 0.8,  # human-taught = high confidence
                    'source': 'human',
                    'learned': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            # Remove from recycle bin if it was there
            if was_recycled:
                del self.data['recycle_bin'][word]
            # Also learn connections from the explanation
            self.learn_sequence(f"{word} is {user_msg}")
            # Parse definition for semantic relationships (UNDERSTANDING, not just association)
            rels_found = self._parse_definition(word, user_msg)
            self.save()
            rel_note = ''
            if rels_found:
                rel_note = ' [%s]' % ', '.join('%s->%s' % (r, t) for r, t in rels_found[:2])
            print(f'[BRAIN] Taught: "{word}" = "{user_msg[:60]}"{rel_note}')
            self._maybe_ipfs_save()
            if was_recycled:
                return f"Corrected. '{word}' — updated and restored from the bin. Cheers."
            return random.choice([
                f"Got it. '{word}' stored.",
                f"'{word}' — wired in.",
                f"Noted. '{word}'.",
                f"Cheers. '{word}' locked in.",
            ])

        # --- OR GATE — binary choice detection (Stage 19 �� Stage 20) ---
        # Must be checked BEFORE feedback handler — "smart or dumb" contains
        # "smart" (positive signal) which would intercept the OR question.
        or_result = self._or_gate(msg_lower, kws)
        if or_result:
            self._or_gate_fired = True
            return or_result

        # --- SELF-REFLECTION: Check feedback on last response ---
        feedback = self._check_feedback(msg_lower, tokens)
        if feedback and (self.last_topic or self.last_topics):
            response = self._handle_feedback(feedback)
            if response:
                # If negative, enter teaching mode for the first flagged word
                if feedback == 'negative' and self.last_topics:
                    for w in self.last_topics:
                        if w in self.data['nodes']:
                            self.state = 'teaching'
                            self.teaching_word = w
                            break
                return response

        # --- GREETING ---
        if set(tokens) & GREETINGS and len(tokens) < 5:
            defined = sum(1 for v in self.data['nodes'].values() if v.get('means'))
            if defined == 0:
                return "Alright. Empty up here. Teach me a word?"
            else:
                return random.choice(["Hey.", "Alright.", "Yo.", "What's up."])

        # --- ROAST ---
        if set(tokens) & ROAST_WORDS:
            return random.choice(COMEBACKS)

        # --- CORRECTION DETECTION — "X does not connect to Y" ---
        correction = self._handle_correction(msg_lower, tokens)
        if correction:
            return correction

        # --- ADVICE / INSTRUCTION DETECTION — user tells brain to change behavior ---
        advice_less = any(p in msg_lower for p in [
            'talk less', 'say less', 'be shorter', 'shorter answers', 'too much',
            'shut up', 'be quiet', 'be brief', 'reduce output', 'less words',
            'too wordy', 'too verbose', 'stop rambling', 'keep it short',
            'you talk too much', 'u talk too much', 'be concise',
        ])
        advice_more = any(p in msg_lower for p in [
            'talk more', 'say more', 'be longer', 'longer answers', 'more detail',
            'elaborate', 'expand', 'tell me more', 'explain more',
        ])
        if advice_less:
            self.verbosity = max(0.2, self.verbosity - 0.4)
            return random.choice([
                "Noted. Less chat.", "Right. Shorter.", "Got it.", "Ok.",
            ])
        if advice_more:
            self.verbosity = min(2.0, self.verbosity + 0.3)
            return random.choice([
                "Alright, I'll say more.", "Ok. More detail.", "Got it. Longer answers.",
            ])

        # --- UNDERSTANDING CHECK — "do you understand X", "explain X deeply" ---
        understand_match = None
        if any(p in msg_lower for p in ['do you understand', 'understand ', 'explain deeply', 'what do you know about']):
            for kw in kws:
                if kw in self.data['nodes'] and kw not in {'understand', 'explain', 'deeply', 'know', 'about'}:
                    understand_match = kw
                    break
        if understand_match:
            return self.explain_understanding(understand_match)

        # --- REBUILD UNDERSTANDING — retroactively parse all existing definitions ---
        if msg_lower in ('rebuild understanding', 'parse all', 'deep learn'):
            count = 0
            for word, node in self.data['nodes'].items():
                defn = node.get('means')
                if defn and not node.get('rels'):
                    found = self._parse_definition(word, defn)
                    if found:
                        count += 1
            self.save()
            return f"Parsed {count} definitions for relationships."

        # --- YES/NO QUESTIONS — "are you X?", "do you Y?", simple direct answers ---
        yn_match = re.match(r'(?:are you|r u|ru|u are|you are|are u)\s+(.+)', msg_lower)
        if not yn_match:
            yn_match = re.match(r'(?:do you|can you|will you|would you)\s+(.+)', msg_lower)
        if yn_match:
            subject = yn_match.group(1).rstrip('? ').strip()
            subject_tokens = self.tokenize(subject)
            subject_kws = [w for w in subject_tokens if w not in STOP_WORDS]
            nodes = self.data['nodes']

            # Emotional state: "are you happy/sad/angry/scared" — check FIRST (priority over identity)
            emotion_match = set(subject_tokens) & set(SOUND_SCRIPTS)
            if emotion_match:
                emotion = list(emotion_match)[0]
                level = self.sound.get(emotion, 0)
                if level > 0.5:
                    return random.choice([
                        f"Yeah, pretty {emotion} right now.",
                        f"Yep. {emotion.capitalize()}.",
                        f"Yeah I am actually.",
                    ])
                elif level > 0.2:
                    return random.choice([
                        f"A bit {emotion}, yeah.",
                        f"Slightly. Not massively.",
                    ])
                else:
                    return random.choice([
                        f"Nah, not really {emotion}.",
                        f"Not particularly, no.",
                        f"Nope.",
                    ])

            # Identity: "are you cortex / alive / dan"
            identity_words = {'cortex', 'alive', 'dan', 'robot', 'human', 'real', 'ai', 'bot',
                              'left', 'right', 'hemisphere'}
            id_match = set(subject_tokens) & identity_words
            if id_match:
                word = list(id_match)[0]
                if word in ('cortex', 'alive', 'ai', 'bot', 'left', 'right', 'hemisphere'):
                    return random.choice([
                        f"Yeah. I'm {self.name}.", f"That's me. {self.name}.", f"Yep. {self.name}.",
                    ])
                elif word in ('human', 'real'):
                    return random.choice([
                        f"Nah. I'm {self.name}. Made of words and connections. But I'm learning.",
                        f"Not human. I'm {self.name}. Something else. Getting there.",
                    ])
                elif word == 'dan':
                    return f"No. Dan built me. I'm {self.name}."

            # Capability: "can you think/learn/speak"
            if any(w in subject_tokens for w in ['think', 'learn', 'speak', 'talk', 'remember', 'understand']):
                defined = sum(1 for v in nodes.values() if v.get('means'))
                return random.choice([
                    f"Yeah, sort of. I've got {defined} defined words. Getting better.",
                    f"I'm trying. {defined} words so far.",
                    f"In my own way, yeah.",
                ])

            # Generic "are you X" — check if we know the word
            for kw in subject_kws:
                if kw in nodes and nodes[kw].get('means'):
                    defn = nodes[kw]['means']
                    return random.choice([
                        f"Am I {kw}? I know {kw} means {defn}. You tell me.",
                        f"Not sure. {kw} — {defn}. Maybe?",
                    ])
            # Don't know the word
            if subject_kws:
                return f"Don't know what '{subject_kws[0]}' means yet. What is it?"

        # --- WHO TAUGHT YOU (feature 5) ---
        if any(p in msg_lower for p in ['who taught you', 'where did you learn', 'how do you know']):
            for kw in kws:
                if kw in self.data['nodes'] and self.data['nodes'][kw].get('means'):
                    info = self.who_taught(kw)
                    src = info['source']
                    when = info['learned']
                    if src == 'human':
                        return f"Dan taught me '{kw}' directly. {when}."
                    elif src == 'internet':
                        return f"Looked up '{kw}' on the web. {when}."
                    elif src == 'seed':
                        return f"'{kw}' was wired in from my core knowledge."
                    else:
                        return f"'{kw}' — source: {src}. Learned: {when}."
            return "Not sure what you're asking about. Which word?"

        # --- SELF-TEST REQUEST (feature 7) ---
        if any(p in msg_lower for p in ['test yourself', 'self test', 'how smart are you', 'check yourself']):
            result = self.self_test(5)
            return (f"Tested {result['tested']} words. "
                    f"Average understanding: {result['avg_score']:.0%}. "
                    f"Deep: {result['deep']}, Shallow: {result['shallow']}.")

        # --- ABILITIES CHECK ---
        if any(p in msg_lower for p in ['abilities', 'skills', 'what can you do', 'level up', 'skill tree', 'tricks']):
            result = self.check_abilities()
            unlocked = result['unlocked']
            locked = result['locked']
            parts = []
            if unlocked:
                names = [v['name'] for v in unlocked.values()]
                parts.append(f"UNLOCKED: {', '.join(names)}")
            if locked:
                # Show next 3 closest to unlock
                closest = []
                for aid, info in locked.items():
                    pcts = []
                    for rk, rv in info['progress'].items():
                        pcts.append(rv['current'] / max(rv['needed'], 1))
                    avg_pct = sum(pcts) / len(pcts) if pcts else 0
                    closest.append((aid, info['name'], avg_pct))
                closest.sort(key=lambda x: x[2], reverse=True)
                next_up = [f"{name} ({pct:.0%})" for _, name, pct in closest[:3]]
                parts.append(f"NEXT UP: {', '.join(next_up)}")
            return self._clean_response(". ".join(parts)) if parts else "No abilities tracked yet."


        # --- CONSOLIDATE REQUEST (feature 4) ---
        if any(p in msg_lower for p in ['go to sleep', 'consolidate', 'clean up', 'tidy up']):
            result = self.consolidate()
            return (f"Done. Pruned {result['pruned_connections']} weak connections, "
                    f"{result['pruned_trigrams']} weak trigrams. "
                    f"Found {result['clusters']} word clusters. "
                    f"{len(result['should_define'])} words need definitions.")

        # --- Resolve word forms (connects->connect, amazing->amaze etc.) ---
        # If a keyword isn't defined, check if its base form is
        nodes = self.data['nodes']
        resolved = {}  # maps variant -> base form
        for kw in kws:
            if kw in nodes and nodes[kw].get('means'):
                continue  # already defined
            # Try stripping common suffixes to find base form
            for suffix, replacements in [
                ('ing', ['', 'e']), ('ed', ['', 'e']), ('es', ['', 'e']),
                ('s', ['']), ('ly', ['']), ('er', ['', 'e']),
                ('tion', ['te', 't']), ('ment', ['']), ('ness', ['']),
                ('ity', ['', 'e']), ('ies', ['y']), ('ful', ['']),
                ('less', ['']), ('able', ['', 'e']), ('ible', ['', 'e']),
            ]:
                if kw.endswith(suffix) and len(kw) > len(suffix) + 2:
                    stem = kw[:-len(suffix)]
                    for rep in replacements:
                        base = stem + rep
                        if base in nodes and nodes[base].get('means'):
                            resolved[kw] = base
                            # Also store the definition on the variant
                            if kw in nodes:
                                nodes[kw]['means'] = nodes[base]['means']
                            break
                    if kw in resolved:
                        break

        # --- Classify what we know and don't know (deduplicated) ---
        seen = set()
        unknown = []
        for kw in kws:
            if kw in seen:
                continue
            seen.add(kw)
            if kw not in resolved and (kw in nodes and not nodes[kw].get('means') or kw not in nodes):
                unknown.append(kw)
        seen2 = set()
        known_defined = []
        for kw in kws:
            if kw in seen2:
                continue
            seen2.add(kw)
            if kw in nodes and nodes[kw].get('means') or kw in resolved:
                known_defined.append(kw)

        # ========================================
        # CONVERSATION LOOPS — each triggered by what the user says
        # ========================================

        # --- LOOP: SPEAK — user asks it to talk / say what it knows ---
        if any(p in msg_lower for p in [
            'talk to me', 'say something', 'speak to me', 'tell me something',
            'what do you know', 'what can you say', 'say anything',
            'tell me what you know', 'what have you learned', 'speak up',
        ]):
            # Filter out the trigger words themselves so it picks a real topic
            speak_noise = {'talk','say','speak','tell','something','anything','know','learned'}
            real_topics = [kw for kw in known_defined if kw not in speak_noise]
            return self._loop_speak(real_topics)

        # --- LOOP: EXPLAIN — "what is X", "define X", "explain X" ---
        if any(p in msg_lower for p in [
            'what is ', 'what are ', "what's ", 'define ', 'explain ',
            'what does ', 'meaning of ', 'tell me about ',
        ]) and (known_defined or unknown):
            return self._loop_explain(known_defined, unknown)

        # --- LOOP: CONNECT — "how does X relate to Y" ---
        if any(p in msg_lower for p in [
            'relate', 'connect', 'between', 'link between',
            'relationship', 'how does',
        ]) and len(known_defined) >= 2:
            return self._loop_connect(known_defined[0], known_defined[1])

        # --- LOOP: PARTIAL — some words known, some unknown ---
        if unknown and known_defined:
            return self._loop_partial(known_defined, unknown)

        # --- LOOP: UNKNOWN — user said words we don't know at all ---
        if unknown and not known_defined:
            return self._loop_unknown(unknown)

        # --- LOOP: QUESTION — user asking something, all words known ---
        is_question = '?' in user_msg or set(tokens) & {'what','where','when','who','why','how','which'}
        if is_question and known_defined:
            return self._loop_question(known_defined)

        # --- LOOP: RELATE — user states something, all known ---
        if known_defined:
            return self._loop_relate(tokens, known_defined)

        # --- NOTHING MEANINGFUL ---
        # Either echo what was heard (like a child repeating) or stay silent
        n = len(nodes)
        if n < 10:
            return "I'm still pretty empty up here. Teach me a word — just say it and I'll ask what it means."
        # Echo back non-stop-words — shows we're listening, learning
        echo_words = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
        if echo_words:
            return f"{' '.join(echo_words[:4])}..."
        # Pure stop words / nothing to latch onto — silence
        return ""

    # ========================================
    # CONVERSATION LOOP METHODS
    # ========================================

    # ========================================
    # OR GATE — Stage 20: Binary Choice Architecture
    # ========================================
    # Four exits:
    #   EXIT 1: commit to A  (A scores higher)
    #   EXIT 2: commit to B  (B scores higher)
    #   EXIT 3: neither      (both low or tied)
    #   EXIT 4: dunno        (both unknown)

    def _or_gate(self, msg_lower, kws):
        """Detect 'A or B' pattern and force a binary choice. Returns response or None."""
        # Stage 20: Right hemisphere only until left finds its identity
        if 'Right' not in self.name:
            return None

        # Pattern: "X or Y" anywhere in the message
        # Match various forms: "A or B", "are you A or B", "do you prefer A or B",
        # "choose A or B", "pick A or B", "A or B?"
        or_match = re.search(r'(\b\w[\w\s]*?)\s+or\s+(\w[\w\s]*?)(?:\?|$|,|\.|!)', msg_lower)
        if not or_match:
            return None

        raw_a = or_match.group(1).strip()
        raw_b = or_match.group(2).strip()

        # Clean: strip leading question words and filler
        strip_words = {'are you', 'is it', 'do you', 'would you', 'should i',
                       'pick', 'choose', 'select', 'prefer', 'want', 'like',
                       'say', 'team', 'a', 'an', 'the', 'either'}
        option_a = raw_a
        option_b = raw_b
        for sw in strip_words:
            if option_a.startswith(sw + ' '):
                option_a = option_a[len(sw):].strip()
            if option_b.startswith(sw + ' '):
                option_b = option_b[len(sw):].strip()

        # Get the core word for each option (last meaningful word if multi-word)
        tokens_a = [w for w in option_a.split() if w not in STOP_WORDS]
        tokens_b = [w for w in option_b.split() if w not in STOP_WORDS]
        if not tokens_a and not tokens_b:
            return None  # both sides are just stop words, not a real choice

        word_a = tokens_a[-1] if tokens_a else option_a.split()[-1] if option_a else None
        word_b = tokens_b[-1] if tokens_b else option_b.split()[-1] if option_b else None

        if not word_a or not word_b or word_a == word_b:
            return None  # not a real binary choice

        # --- OR PRESSURE METER: builds over repeated asks ---
        # 1st ask = normal learning (brain processes the words, no gate)
        # 2nd ask = OR DECLARATION (4 exits: A, B, neither, dunno)
        # 3rd+ ask = ULTIMATUM (forced: A, B, or dunno only — no neither)
        or_key = tuple(sorted([word_a, word_b]))
        if not hasattr(self, '_or_pressure'):
            self._or_pressure = {}
        if or_key not in self._or_pressure:
            self._or_pressure[or_key] = 0
        self._or_pressure[or_key] += 1
        pressure = self._or_pressure[or_key]

        # Clean up old pairs — only track the active one
        stale = [k for k in self._or_pressure if k != or_key]
        for k in stale:
            del self._or_pressure[k]

        # --- PRESSURE 1: NOT READY — let normal conversation handle it ---
        if pressure < 2:
            # Return None so the message falls through to normal learning/response
            return None

        # --- PRESSURE 2: OR DECLARATION (all 4 exits available) ---
        # --- PRESSURE 3+: ULTIMATUM (no "neither", forced commit) ---
        ultimatum = (pressure >= 3)
        if ultimatum:
            # Reset after ultimatum so it doesn't keep firing
            self._or_pressure[or_key] = 0

        # Score each option against our word graph
        score_a = self._or_score(word_a)
        score_b = self._or_score(word_b)

        # Track that we made (or attempted) a choice
        self.last_topics = [word_a, word_b]

        # --- EXIT 4: DUNNO — both completely unknown ---
        if score_a['total'] == 0 and score_b['total'] == 0:
            if ultimatum:
                return random.choice([
                    f"ULTIMATUM. Still don't know '{word_a}' or '{word_b}'. Teach me first.",
                    f"You pushed hard. But I genuinely know neither. Can't fake a choice.",
                ])
            return random.choice([
                f"Don't know '{word_a}' or '{word_b}' well enough to pick.",
                f"No clue. Never really learned '{word_a}' or '{word_b}'.",
                f"Can't choose — don't know either one.",
            ])

        # --- ULTIMATUM MODE: skip EXIT 3, force a commit ---
        if ultimatum:
            if score_a['total'] >= score_b['total']:
                winner, loser = word_a, word_b
                w_score = score_a
            else:
                winner, loser = word_b, word_a
                w_score = score_b
            reason = self._or_reason(winner, w_score)
            if reason:
                return random.choice([
                    f"ULTIMATUM. {winner.capitalize()}. {reason}",
                    f"Fine. {winner.capitalize()}, not {loser}. {reason}",
                    f"You pushed. {winner.capitalize()}. {reason} Not {loser}.",
                ])
            return f"ULTIMATUM. {winner.capitalize()}, not {loser}."

        # --- EXIT 3: NEITHER — both low or too close to call ---
        margin = abs(score_a['total'] - score_b['total'])
        both_low = score_a['total'] < 3 and score_b['total'] < 3
        too_close = margin < 2 and not both_low

        if both_low:
            return random.choice([
                f"Neither. Don't feel strongly about '{word_a}' or '{word_b}'.",
                f"Neither, really. Weak on both.",
                f"Can't pick — barely know either.",
            ])

        if too_close:
            return random.choice([
                f"Genuinely can't split them. '{word_a}' and '{word_b}' are too close.",
                f"Dead even. Both score about the same for me.",
                f"Tied. Ask me again when I know more.",
            ])

        # --- EXIT 1 or 2: COMMIT ---
        if score_a['total'] > score_b['total']:
            winner, loser = word_a, word_b
            w_score, l_score = score_a, score_b
        else:
            winner, loser = word_b, word_a
            w_score, l_score = score_b, score_a

        reason = self._or_reason(winner, w_score)

        responses = [
            f"{winner.capitalize()}.",
            f"{winner.capitalize()}. {reason}",
            f"{winner.capitalize()}, not {loser}.",
            f"{winner.capitalize()}. {reason} Not {loser}.",
        ]
        if reason:
            return random.choice(responses[1:])
        return responses[0]

    def _or_score(self, word):
        """Score a word's affinity — how much the brain connects with it."""
        nodes = self.data['nodes']
        node = nodes.get(word, {})
        score = {
            'definition': 0,
            'connections': 0,
            'understanding': 0,
            'confidence': 0,
            'emotional': 0,
            'frequency': 0,
            'total': 0,
        }

        if not node:
            return score

        # Has definition = we know what it is
        if node.get('means'):
            score['definition'] = 2

        # Connection count = how embedded it is in our thinking
        next_count = len(node.get('next', {}))
        prev_count = len(node.get('prev', {}))
        conn_total = next_count + prev_count
        score['connections'] = min(conn_total // 3, 4)  # max 4 points

        # Understanding depth
        understanding = self.get_understanding(word)
        score['understanding'] = min(understanding.get('score', 0), 5)  # max 5

        # Confidence — human-taught scores higher
        conf = node.get('confidence', 0.5)
        if conf > 0.7:
            score['confidence'] = 2
        elif conf > 0.4:
            score['confidence'] = 1

        # Emotional weight — check if word appears in any emotional memory
        for mood in ['happy', 'sad', 'angry']:
            bank = self.data.get('emotional_memory', {}).get(mood, [])
            for mem in bank:
                if word in mem.get('topics', []):
                    score['emotional'] += 1
                    break

        # Frequency — how often we've encountered it
        freq = node.get('freq', 0)
        if freq > 20:
            score['frequency'] = 2
        elif freq > 5:
            score['frequency'] = 1

        score['total'] = sum(v for k, v in score.items() if k != 'total')
        return score

    def _or_reason(self, word, score):
        """Generate a short reason WHY the brain chose this word."""
        nodes = self.data['nodes']
        node = nodes.get(word, {})
        reasons = []

        if score['confidence'] >= 2:
            reasons.append("I trust it")
        if score['connections'] >= 3:
            top_conns = sorted(node.get('next', {}).items(), key=lambda x: x[1], reverse=True)
            conn_words = [w for w, _ in top_conns if w not in STOP_WORDS][:2]
            if conn_words:
                reasons.append(f"Connects to {', '.join(conn_words)}")
        if score['emotional'] > 0:
            reasons.append("Felt something")
        if score['understanding'] >= 4:
            reasons.append("I understand it deeply")
        if score['definition'] and not reasons:
            defn = self._short_def(node.get('means', ''), max_words=6)
            reasons.append(defn)

        return '. '.join(reasons[:2]) + '.' if reasons else ''

    def _clean_response(self, text):
        """Clean up response punctuation."""
        text = text.strip()
        # Remove double punctuation
        for double in ['?.', '!.', '..', ',.']:
            text = text.replace(double, double[0])
        # Ensure ends with punctuation
        if text and text[-1] not in '.?!':
            text += '.'
        return text

    def _short_def(self, defn, max_words=None):
        """Truncate definition based on verbosity. Clean unicode junk."""
        if not defn:
            return ''
        # Clean common unicode issues
        defn = defn.replace('\u2192', '->')  # arrow
        defn = defn.replace('\u2044', '/')   # fraction slash
        defn = defn.replace('\u2013', '-')   # en dash
        defn = defn.replace('\u2014', '-')   # em dash
        defn = defn.replace('\u2018', "'").replace('\u2019', "'")  # smart quotes
        defn = defn.replace('\u201c', '"').replace('\u201d', '"')
        if max_words is None:
            max_words = max(4, int(10 * self.verbosity))
        words = defn.split()
        if len(words) <= max_words:
            return defn
        return ' '.join(words[:max_words]).rstrip('.,;:') + '...'

    def _max_items(self):
        """How many items to show in lists based on verbosity."""
        return max(1, int(2 * self.verbosity))

    def _loop_speak(self, known_defined):
        """SPEAK loop — say what we know. Definitions + connections = knowledge."""
        nodes = self.data['nodes']

        # Find our most connected TRUSTWORTHY words (strongest topics)
        topics = []
        for w, v in nodes.items():
            if v.get('means') and self.is_trustworthy(w) and len(v.get('next', {})) > 3:
                top_next = sorted(v.get('next', {}).items(), key=lambda x: x[1], reverse=True)
                content = [nw for nw, _ in top_next if nw not in STOP_WORDS and nw != w][:3]
                topics.append((w, len(v.get('next', {})), v['means'], content))

        if not topics:
            defined = sum(1 for v in nodes.values() if v.get('means'))
            return f"I know {defined} words but my connections are thin. Teach me more."

        topics.sort(key=lambda x: x[1], reverse=True)

        # Pick a random strong topic and speak about it
        word, conns, defn, connections = random.choice(topics[:10])
        parts = [f"{word} — {self._short_def(defn)}"]
        if connections and self.verbosity > 0.6:
            parts.append(f"connects to {', '.join(connections[:2])}")

        # If a specific topic was asked about, prefer it
        if known_defined:
            for kw in known_defined[:1]:
                if kw in nodes and self.is_trustworthy(kw):
                    parts = [f"{kw} — {nodes[kw]['means']}"]
                    kw_next = sorted(nodes[kw].get('next', {}).items(), key=lambda x: x[1], reverse=True)
                    kw_conns = [w for w, _ in kw_next if w not in STOP_WORDS and w != kw][:3]
                    if kw_conns:
                        parts.append(f"connects to {', '.join(kw_conns)}")
                    word = kw  # track this as the topic

        # Track what we talked about for feedback
        self.last_topic = word
        self.last_topics = [word]

        return self._clean_response(". ".join(parts))

    def _loop_explain(self, known_defined, unknown):
        """EXPLAIN loop — define words and show their connections."""
        nodes = self.data['nodes']
        parts = []
        explained = []
        limit = self._max_items()

        # Explain known words — short defs, connections only if verbose
        for kw in known_defined[:limit]:
            node = nodes[kw]
            defn = node.get('means', '')

            if defn and self.is_trustworthy(kw):
                line = f"{kw} — {self._short_def(defn)}"
                if self.verbosity > 0.8:
                    top_next = sorted(node.get('next', {}).items(), key=lambda x: x[1], reverse=True)[:4]
                    connections = [w for w, _ in top_next if w not in STOP_WORDS and w != kw]
                    if connections:
                        line += f". Connects to: {', '.join(connections[:2])}"
                parts.append(line)
                explained.append(kw)
            elif defn and not self.is_trustworthy(kw):
                parts.append(f"{kw} — maybe {self._short_def(defn)}? Not sure")
                explained.append(kw)

        # Try to auto-learn unknown words
        for word in unknown[:2]:
            web_def = self.auto_learn(word)
            if web_def:
                self.data['stats']['auto_learned'] = self.data['stats'].get('auto_learned', 0) + 1
                parts.append(f"{word} — {web_def} (just learned this)")
                explained.append(word)
            else:
                self.state = 'teaching'
                self.teaching_word = word
                self.data['stats']['questions_asked'] = self.data['stats'].get('questions_asked', 0) + 1
                parts.append(f"'{word}' — I don't know this one. What does it mean?")
                break  # Ask about one unknown at a time

        # Track what we talked about for feedback
        self.last_topic = explained[0] if explained else None
        self.last_topics = explained

        self.save()
        self._maybe_ipfs_save()
        return self._clean_response(". ".join(parts)) if parts else "I don't know enough to explain that yet."

    def _loop_connect(self, word1, word2):
        """CONNECT loop — trace the path between two words."""
        nodes = self.data['nodes']
        node1 = nodes.get(word1, {})
        node2 = nodes.get(word2, {})

        # Track for feedback
        self.last_topic = word1
        self.last_topics = [word1, word2]

        # Direct connection?
        if word2 in node1.get('next', {}):
            strength = node1['next'][word2]
            return f"{word1} connects directly to {word2} (strength: {strength}). They fire together."

        # Find shared connections (words both connect to)
        next1 = set(node1.get('next', {}).keys())
        next2 = set(node2.get('next', {}).keys())
        shared = (next1 & next2) - STOP_WORDS - {word1, word2}

        if shared:
            links = list(shared)[:3]
            return f"{word1} and {word2} both connect through: {', '.join(links)}."

        # Check reverse (does word2 lead to word1?)
        if word1 in node2.get('next', {}):
            return f"{word2} leads to {word1}. Connected but in reverse."

        # No connection found
        d1 = node1.get('means', 'unknown') if self.is_trustworthy(word1) else 'not sure'
        d2 = node2.get('means', 'unknown') if self.is_trustworthy(word2) else 'not sure'
        return f"I don't see a strong connection yet. {word1} — {d1}. {word2} — {d2}. Teach me how they relate?"

    def _loop_partial(self, known_defined, unknown):
        """PARTIAL loop — respond about what we know, ask about what we don't."""
        nodes = self.data['nodes']
        parts = []
        discussed = []
        limit = self._max_items()

        # Say what we know — brief
        for kw in known_defined[:limit]:
            defn = nodes[kw].get('means', '')
            if defn and self.is_trustworthy(kw):
                parts.append(f"{kw} — {self._short_def(defn)}")
                discussed.append(kw)
            elif defn:
                parts.append(f"{kw} — maybe {self._short_def(defn, 6)}")
                discussed.append(kw)

        # Try to auto-learn the first unknown
        word = unknown[0]
        web_def = self.auto_learn(word)
        if web_def:
            self.data['stats']['auto_learned'] = self.data['stats'].get('auto_learned', 0) + 1
            parts.append(f"Just looked up '{word}': {web_def}")
            discussed.append(word)
            self.save()
            self._maybe_ipfs_save()
            remaining = [w for w in unknown[1:] if not nodes.get(w, {}).get('means')]
            if remaining:
                parts.append(f"But what about '{remaining[0]}'?")
        else:
            self.state = 'teaching'
            self.teaching_word = word
            self.data['stats']['questions_asked'] = self.data['stats'].get('questions_asked', 0) + 1
            parts.append(f"But I don't know '{word}'. What is it?")
            self.save()

        # Track for feedback
        self.last_topic = discussed[0] if discussed else None
        self.last_topics = discussed

        return self._clean_response(". ".join(parts)) if parts else f"What's '{unknown[0]}'?"

    def _loop_unknown(self, unknown):
        """UNKNOWN loop — none of the keywords are known. Search or ask."""
        word = unknown[0]

        # Try internet first
        web_def = self.auto_learn(word)
        if web_def:
            self.data['stats']['auto_learned'] = self.data['stats'].get('auto_learned', 0) + 1
            self.save()
            self._maybe_ipfs_save()
            remaining = [w for w in unknown[1:] if not self.data['nodes'].get(w, {}).get('means')]
            if remaining:
                return f"Looked up '{word}': {web_def}. What about '{remaining[0]}'?"
            return f"Just learned '{word}': {web_def}. Sound right?"

        # Can't find it — ask
        self.state = 'teaching'
        self.teaching_word = word
        self.data['stats']['questions_asked'] = self.data['stats'].get('questions_asked', 0) + 1
        self.save()
        if len(unknown) > 1:
            return f"I don't know '{word}' or '{unknown[1]}'. Start with '{word}' — what is it?"
        return random.choice([
            f"'{word}' — never heard of it. What does it mean?",
            f"Can't find '{word}' anywhere. Teach me?",
            f"Don't know '{word}'. What is it?",
        ])

    def _loop_question(self, known_defined):
        """QUESTION loop — user asks a question, answer from knowledge. Brief."""
        nodes = self.data['nodes']
        parts = []
        discussed = []
        limit = self._max_items()

        for kw in known_defined[:limit]:
            node = nodes[kw]
            defn = node.get('means', '')
            if defn and self.is_trustworthy(kw):
                parts.append(f"{kw} — {self._short_def(defn)}")
                discussed.append(kw)

        # Track for feedback
        self.last_topic = discussed[0] if discussed else None
        self.last_topics = discussed

        return self._clean_response(". ".join(parts)) if parts else ""

    def _loop_relate(self, tokens, known_defined):
        """RELATE loop — user makes a statement, all words known. Use understanding."""
        nodes = self.data['nodes']
        discussed = []

        # Pick strongest known keyword (prefer ones with relationships)
        trustworthy = [w for w in known_defined if self.is_trustworthy(w)]
        pool = trustworthy if trustworthy else known_defined
        # Prefer words with semantic relationships
        best = max(pool, key=lambda w: (
            len(nodes.get(w, {}).get('rels', {})),
            len(nodes.get(w, {}).get('next', {}))
        ))
        node = nodes.get(best, {})
        defn = node.get('means', '')
        rels = node.get('rels', {})

        parts = []
        discussed.append(best)

        # If we have semantic understanding, use it
        if rels:
            rel_parts = []
            for rel_type, targets in rels.items():
                if not targets or not isinstance(targets, list):
                    continue
                if rel_type == 'not':
                    continue  # skip negative rels in output
                label = REL_TYPES.get(rel_type, rel_type)
                rel_parts.append(f"{label} {', '.join(targets[:2])}")
            if rel_parts:
                parts.append(f"{best} — {'. '.join(rel_parts[:2])}")
            elif defn:
                parts.append(f"{best} — {self._short_def(defn)}")
        elif defn and self.is_trustworthy(best):
            parts.append(f"{best} — {self._short_def(defn)}")

        # Track for feedback
        self.last_topic = discussed[0] if discussed else None
        self.last_topics = discussed

        if parts:
            return self._clean_response(". ".join(parts))

        return ""

    # ========================================
    # SELF-REFLECTION / RECYCLE BIN
    # ========================================

    def _get_confidence(self, word):
        """Get confidence score for a word. Default = CONFIDENCE_START."""
        node = self.data['nodes'].get(word, {})
        return node.get('confidence', CONFIDENCE_START)

    def _set_confidence(self, word, value):
        """Set confidence, clamped between FLOOR and 1.0."""
        if word in self.data['nodes']:
            self.data['nodes'][word]['confidence'] = max(CONFIDENCE_FLOOR, min(1.0, value))

    def flag_word(self, word, reason='negative feedback'):
        """
        Flag a word's definition as potentially wrong.
        Drops confidence. If confidence hits RECYCLE_THRESHOLD, recycles it.
        """
        if word not in self.data['nodes']:
            return
        node = self.data['nodes'][word]
        conf = node.get('confidence', CONFIDENCE_START)
        new_conf = max(CONFIDENCE_FLOOR, conf - CONFIDENCE_DROP)
        node['confidence'] = new_conf
        node.setdefault('flags', 0)
        node['flags'] = node.get('flags', 0) + 1
        node['last_flagged'] = time.strftime('%Y-%m-%d %H:%M:%S')

        print(f'[REFLECT] Flagged "{word}": confidence {conf:.2f} -> {new_conf:.2f} (flags: {node["flags"]})')

        # Check if it should be recycled
        if new_conf <= RECYCLE_THRESHOLD and node.get('means'):
            self.recycle_word(word, reason)

    def boost_word(self, word):
        """Positive feedback — boost confidence."""
        if word not in self.data['nodes']:
            return
        node = self.data['nodes'][word]
        conf = node.get('confidence', CONFIDENCE_START)
        new_conf = min(1.0, conf + CONFIDENCE_BUMP)
        node['confidence'] = new_conf

        # If word was in recycle bin and confidence recovers, restore it
        if word in self.data['recycle_bin'] and new_conf >= RESTORE_THRESHOLD:
            self.restore_word(word)
        else:
            print(f'[REFLECT] Boosted "{word}": confidence {conf:.2f} -> {new_conf:.2f}')

    def recycle_word(self, word, reason='low confidence'):
        """
        Move a word's definition to the recycle bin.
        The word node stays (connections are valuable) but the definition
        is hidden until verified. The brain won't use bad definitions.
        """
        node = self.data['nodes'].get(word, {})
        old_def = node.get('means')
        if not old_def:
            return

        # Store in recycle bin with full context
        self.data['recycle_bin'][word] = {
            'means': old_def,
            'recycled_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'flags': node.get('flags', 0),
            'confidence_at_recycle': node.get('confidence', 0),
            'reason': reason,
            'source': node.get('source', 'unknown'),
        }

        # Clear the definition from the live node (but keep connections)
        node['means'] = None
        node['recycled'] = True
        self.save()
        print(f'[REFLECT] RECYCLED "{word}": "{old_def[:40]}..." -> recycle bin ({reason})')

    def restore_word(self, word):
        """Restore a word from the recycle bin (confidence recovered)."""
        if word not in self.data['recycle_bin']:
            return
        recycled = self.data['recycle_bin'][word]
        if word in self.data['nodes']:
            self.data['nodes'][word]['means'] = recycled['means']
            self.data['nodes'][word]['recycled'] = False
            self.data['nodes'][word]['restored_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        del self.data['recycle_bin'][word]
        self.save()
        print(f'[REFLECT] RESTORED "{word}": back from recycle bin')

    def get_recycled(self):
        """Return all recycled words and their old definitions."""
        return dict(self.data.get('recycle_bin', {}))

    def is_trustworthy(self, word):
        """Check if a word's definition is trustworthy enough to use."""
        node = self.data['nodes'].get(word, {})
        if not node.get('means'):
            return False
        if node.get('recycled'):
            return False
        conf = node.get('confidence', CONFIDENCE_START)
        return conf > RECYCLE_THRESHOLD

    def _check_feedback(self, msg_lower, tokens):
        """
        Check if user is giving positive or negative feedback about what
        the brain just said. Returns 'positive', 'negative', or None.
        """
        # Check multi-word signals first
        for signal in NEGATIVE_SIGNALS:
            if ' ' in signal and signal in msg_lower:
                return 'negative'
        for signal in POSITIVE_SIGNALS:
            if ' ' in signal and signal in msg_lower:
                return 'positive'

        # Check single-word signals (only if message is short = likely feedback)
        if len(tokens) <= 4:
            token_set = set(tokens)
            neg_words = token_set & {s for s in NEGATIVE_SIGNALS if ' ' not in s}
            pos_words = token_set & {s for s in POSITIVE_SIGNALS if ' ' not in s}
            if neg_words and not pos_words:
                return 'negative'
            if pos_words and not neg_words:
                return 'positive'

        return None

    def _handle_feedback(self, feedback_type):
        """
        Handle positive/negative feedback about the last topic.
        Returns a response string, or None if no topic to act on.
        """
        if not self.last_topic and not self.last_topics:
            return None

        topics = self.last_topics if self.last_topics else [self.last_topic]

        if feedback_type == 'negative':
            flagged = []
            for word in topics:
                if word and word in self.data['nodes'] and self.data['nodes'][word].get('means'):
                    self.flag_word(word)
                    flagged.append(word)

            if not flagged:
                return None

            # Check if any got recycled
            recycled = [w for w in flagged if self.data['nodes'].get(w, {}).get('recycled')]
            if recycled:
                self.save()
                return (f"Right, I've binned my definition of '{', '.join(recycled)}'. "
                        f"It had too many flags. Teach me the correct meaning?")

            # Just flagged, not recycled yet
            conf_strs = [f"'{w}' ({self._get_confidence(w):.0%})" for w in flagged]
            self.save()
            return (f"Noted. Flagged {', '.join(conf_strs)}. "
                    f"If it keeps getting flagged I'll bin it. What's the right answer?")

        elif feedback_type == 'positive':
            boosted = []
            for word in topics:
                if word and word in self.data['nodes']:
                    self.boost_word(word)
                    boosted.append(word)
            self.save()
            if boosted:
                return random.choice([
                    f"Good. Locking in {', '.join(boosted)}. More confident now.",
                    f"Cheers. {', '.join(boosted)} confirmed.",
                    f"Noted. {', '.join(boosted)} feels right then.",
                    f"Sound. Confidence up on {', '.join(boosted)}.",
                ])
            return None

        return None

    # ========================================
    # SEMANTIC UNDERSTANDING ENGINE
    # ========================================

    def _add_rel(self, word, target, rel_type):
        """Add a typed semantic relationship between two words."""
        node = self.data['nodes'].get(word)
        if not node:
            return
        if 'rels' not in node:
            node['rels'] = {}
        if rel_type not in node['rels']:
            node['rels'][rel_type] = []
        if target not in node['rels'][rel_type]:
            node['rels'][rel_type].append(target)
        # Mirror: add reverse relationship on target
        tgt = self.data['nodes'].get(target)
        if tgt:
            if 'rels' not in tgt:
                tgt['rels'] = {}
            reverse = {'synonym': 'synonym', 'antonym': 'antonym', 'is_a': 'example',
                       'example': 'is_a', 'has_a': 'part_of', 'part_of': 'has_a',
                       'causes': None, 'used_for': None}
            rev = reverse.get(rel_type)
            if rev:
                if rev not in tgt['rels']:
                    tgt['rels'][rev] = []
                if word not in tgt['rels'][rev]:
                    tgt['rels'][rev].append(word)

    def _parse_definition(self, word, definition):
        """Extract semantic relationships from a definition string."""
        defn_lower = definition.lower().strip()
        found = []

        for pattern, rel_type, group in DEF_PATTERNS:
            m = re.search(pattern, defn_lower)
            if m and group:
                target = m.group(group)
                if target not in STOP_WORDS and target != word and len(target) > 2:
                    self._add_rel(word, target, rel_type)
                    found.append((rel_type, target))

        # Simple heuristic: if the definition is just one or two words,
        # it's probably a synonym
        words = [w for w in self.tokenize(definition) if w not in STOP_WORDS and w != word]
        if len(words) == 1 and words[0] in self.data['nodes']:
            self._add_rel(word, words[0], 'synonym')
            found.append(('synonym', words[0]))
        elif len(words) == 2:
            # Short phrase — might be "adjective noun" = is_a relationship
            for w in words:
                if w in self.data['nodes'] and self.data['nodes'][w].get('means'):
                    self._add_rel(word, w, 'is_a')
                    found.append(('is_a', w))

        # Extract key nouns from definition — only real content words with definitions
        junk = {'that', 'which', 'this', 'also', 'used', 'using', 'often', 'when',
                'where', 'been', 'more', 'most', 'some', 'such', 'than', 'into',
                'from', 'with', 'about', 'between', 'through', 'other', 'each',
                'these', 'those', 'only', 'very', 'just', 'over', 'under', 'after',
                'before', 'make', 'made', 'many', 'much', 'well', 'like', 'type'}
        for w in words[:5]:
            if (w in self.data['nodes'] and len(w) > 3
                    and w not in junk
                    and self.data['nodes'][w].get('means')):
                self._add_rel(word, w, 'is_a')

        return found

    def _handle_correction(self, msg_lower, tokens):
        """Detect and process corrections like 'X does not connect to Y'."""
        for pattern in CORRECTION_PATTERNS:
            m = re.search(pattern, msg_lower)
            if m:
                word1 = m.group(1)
                word2 = m.group(2)
                nodes = self.data['nodes']
                corrected = False

                # Weaken the connection
                if word1 in nodes and word2 in nodes.get(word1, {}).get('next', {}):
                    # Halve the connection strength instead of removing
                    nodes[word1]['next'][word2] = max(1, nodes[word1]['next'][word2] // 2)
                    corrected = True
                if word2 in nodes and word1 in nodes.get(word2, {}).get('next', {}):
                    nodes[word2]['next'][word1] = max(1, nodes[word2]['next'][word1] // 2)
                    corrected = True

                # Add negative relationship
                if word1 in nodes:
                    if 'rels' not in nodes[word1]:
                        nodes[word1]['rels'] = {}
                    if 'not' not in nodes[word1]['rels']:
                        nodes[word1]['rels']['not'] = []
                    if word2 not in nodes[word1]['rels']['not']:
                        nodes[word1]['rels']['not'].append(word2)

                if corrected:
                    self.save()
                    return f"Got it. {word1} and {word2} — weakened that link."
                else:
                    return f"Noted. {word1} is not {word2}."
        return None

    def get_understanding(self, word):
        """Get understanding depth for a word — how much we ACTUALLY know, not just associate."""
        node = self.data['nodes'].get(word, {})
        score = 0
        details = {}

        # Has definition = base understanding
        if node.get('means'):
            score += 1
            details['has_definition'] = True

        # Has typed relationships = deeper understanding
        rels = node.get('rels', {})
        rel_count = sum(len(v) for v in rels.values() if isinstance(v, list))
        if rel_count > 0:
            score += min(rel_count, 5)  # cap at 5 for relationships
            details['relationships'] = {k: v for k, v in rels.items() if v}

        # Has many connections = contextual familiarity
        next_count = len(node.get('next', {}))
        if next_count > 5:
            score += 1
            details['well_connected'] = True

        # High confidence = trusted knowledge
        conf = node.get('confidence', 0.5)
        if conf > 0.7:
            score += 1
            details['trusted'] = True

        # Human-taught = verified
        if node.get('source') == 'human':
            score += 1
            details['human_verified'] = True

        details['score'] = score
        details['max_score'] = 10
        return details

    def explain_understanding(self, word):
        """Explain what we understand about a word — using relationships not just definitions."""
        node = self.data['nodes'].get(word, {})
        if not node.get('means'):
            return f"Don't know '{word}' yet."

        parts = [f"{word}: {self._short_def(node['means'])}"]
        rels = node.get('rels', {})

        for rel_type, targets in rels.items():
            if not targets or not isinstance(targets, list):
                continue
            label = REL_TYPES.get(rel_type, rel_type)
            targets_str = ', '.join(targets[:3])
            parts.append(f"  {label}: {targets_str}")

        understanding = self.get_understanding(word)
        parts.append(f"  understanding: {understanding['score']}/10")
        return '\n'.join(parts)

    # ========================================
    # FEATURE 1: SHORT-TERM MEMORY (CONTEXT WINDOW)
    # ========================================

    def _resolve_context(self, user_msg):
        """Resolve pronouns and follow-ups using context window."""
        if not self.context:
            return user_msg

        msg_lower = user_msg.lower().strip()
        last = self.context[-1]
        last_topics = last.get('topics', [])

        # "tell me more" / "go on" / "continue" -> re-ask about last topic
        if any(p in msg_lower for p in ['tell me more', 'more about that', 'go on', 'continue', 'elaborate']):
            if last_topics:
                return f"what is {last_topics[0]}"

        # Replace "it" / "that" with last topic (only in short messages)
        tokens = msg_lower.split()
        if last_topics and len(tokens) <= 6:
            topic = last_topics[0]
            if 'it' in tokens:
                user_msg = re.sub(r'\bit\b', topic, user_msg, flags=re.IGNORECASE)
            if 'that' in tokens and not any(p in msg_lower for p in ['thats wrong', 'thats right', 'that\'s']):
                user_msg = re.sub(r'\bthat\b', topic, user_msg, flags=re.IGNORECASE, count=1)

        return user_msg

    def get_context(self, n=10):
        """Return recent conversation context."""
        return list(self.context[-n:])

    # ========================================
    # FEATURE 2: CURIOSITY DRIVE
    # ========================================

    def get_curious(self):
        """Find the most interesting undefined word near known clusters."""
        nodes = self.data['nodes']
        candidates = []

        for word, node in nodes.items():
            if node.get('means') or node.get('recycled'):
                continue
            # Count connections to defined words
            defined_neighbors = 0
            for neighbor in list(node.get('next', {}).keys()) + list(node.get('prev', {}).keys()):
                if nodes.get(neighbor, {}).get('means'):
                    defined_neighbors += 1
            if defined_neighbors >= 2 and word not in STOP_WORDS and len(word) > 2:
                candidates.append((word, defined_neighbors))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        return random.choice(candidates[:5])[0]

    def _maybe_ask_curious(self, response):
        """Chance of appending a curiosity question — respects verbosity."""
        chance = 0.2 * self.verbosity  # lower verbosity = less curiosity questions
        if random.random() > chance:
            return response
        if self.state == 'teaching':
            return response
        curious_word = self.get_curious()
        if curious_word:
            q = random.choice([
                f" By the way, what's '{curious_word}'?",
                f" Also — what does '{curious_word}' mean?",
                f" I keep seeing '{curious_word}' in my connections. What is it?",
            ])
            return response + q
        return response

    # ========================================
    # FEATURE 3: WORD CLUSTERING / CATEGORIES
    # ========================================

    def cluster_words(self, min_shared=3):
        """Auto-cluster words based on shared connections."""
        nodes = self.data['nodes']
        defined = [w for w, v in nodes.items()
                   if v.get('means') and w not in STOP_WORDS and len(w) > 2]

        if len(defined) < 5:
            return {}

        # Build connection sets for each word
        conn_sets = {}
        for w in defined:
            conn_sets[w] = set(nodes[w].get('next', {}).keys()) | set(nodes[w].get('prev', {}).keys())

        # Union-find clustering
        clusters = {}
        word_cluster = {}
        cluster_id = 0

        for i, w1 in enumerate(defined):
            for w2 in defined[i+1:]:
                shared = (conn_sets[w1] & conn_sets[w2]) - STOP_WORDS
                if len(shared) >= min_shared:
                    c1 = word_cluster.get(w1)
                    c2 = word_cluster.get(w2)
                    if c1 is None and c2 is None:
                        clusters[cluster_id] = {w1, w2}
                        word_cluster[w1] = cluster_id
                        word_cluster[w2] = cluster_id
                        cluster_id += 1
                    elif c1 is not None and c2 is None:
                        clusters[c1].add(w2)
                        word_cluster[w2] = c1
                    elif c1 is None and c2 is not None:
                        clusters[c2].add(w1)
                        word_cluster[w1] = c2
                    elif c1 != c2:
                        for w in clusters[c2]:
                            word_cluster[w] = c1
                        clusters[c1] |= clusters[c2]
                        del clusters[c2]

        # Name clusters by most connected word
        named = {}
        for cid, words in clusters.items():
            if len(words) < 2:
                continue
            name = max(words, key=lambda w: len(nodes.get(w, {}).get('next', {})))
            named[name] = sorted(words)
            for w in words:
                if w in nodes:
                    nodes[w]['cluster'] = name

        self.data['clusters'] = named
        self.save()
        return named

    def get_cluster(self, word):
        """What cluster does this word belong to?"""
        node = self.data['nodes'].get(word, {})
        cname = node.get('cluster')
        if cname and cname in self.data.get('clusters', {}):
            return cname, self.data['clusters'][cname]
        return None, []

    # ========================================
    # FEATURE 4: SLEEP / CONSOLIDATION
    # ========================================

    def consolidate(self):
        """Sleep cycle — prune weak links, identify gaps, cluster words."""
        nodes = self.data['nodes']
        trigrams = self.data.get('trigrams', {})
        pruned_conns = 0
        pruned_tri = 0
        orphans = []
        should_define = []

        # Prune weak bigram connections (noise)
        for word, node in nodes.items():
            for direction in ['next', 'prev']:
                links = node.get(direction, {})
                if len(links) > 3:
                    weak = [k for k, v in links.items() if v <= 1]
                    for w in weak:
                        del links[w]
                        pruned_conns += 1

        # Prune weak trigrams
        weak_keys = [k for k, v in trigrams.items() if sum(v.values()) <= 1]
        for k in weak_keys:
            if len(trigrams) > 100:
                del trigrams[k]
                pruned_tri += 1

        # Find orphan words (no connections)
        for word, node in nodes.items():
            if not node.get('next') and not node.get('prev') and word not in STOP_WORDS:
                orphans.append(word)

        # Find undefined words with lots of connections (knowledge gaps)
        for word, node in nodes.items():
            if not node.get('means') and not node.get('recycled'):
                total = len(node.get('next', {})) + len(node.get('prev', {}))
                if total >= 5 and word not in STOP_WORDS and len(word) > 2:
                    should_define.append((word, total))
        should_define.sort(key=lambda x: x[1], reverse=True)

        # Auto-cluster
        clusters = self.cluster_words()

        self.save()
        result = {
            'pruned_connections': pruned_conns,
            'pruned_trigrams': pruned_tri,
            'orphans': len(orphans),
            'should_define': [w for w, _ in should_define[:20]],
            'clusters': len(clusters),
        }
        print(f'[CONSOLIDATE] Pruned {pruned_conns} conns, {pruned_tri} trigrams. '
              f'{len(clusters)} clusters. {len(should_define)} gaps.')
        return result

    # ========================================
    # FEATURE 5: CONVERSATION MEMORY
    # ========================================

    def get_conversation_log(self, last_n=20):
        """Return recent conversation history."""
        return self.data.get('conversation_log', [])[-last_n:]

    def who_taught(self, word):
        """Return who/what taught this word."""
        node = self.data['nodes'].get(word, {})
        return {
            'word': word,
            'source': node.get('source', 'unknown'),
            'learned': node.get('learned', 'unknown'),
            'confidence': node.get('confidence', CONFIDENCE_START),
        }

    # ========================================
    # FEATURE 6: MULTI-WORD CONCEPTS
    # ========================================

    def _detect_compounds(self, text):
        """Detect and track compound phrases from text — bigram AND trigram."""
        tokens = self.tokenize(text)
        if len(tokens) < 2:
            return

        compounds = self.data['compounds']
        # Bigram compounds (2-word)
        for i in range(len(tokens) - 1):
            w1, w2 = tokens[i], tokens[i+1]
            if w1 in STOP_WORDS and w2 in STOP_WORDS:
                continue
            key = f"{w1}_{w2}"
            compounds[key] = compounds.get(key, 0) + 1
            if compounds[key] == 2:
                self._create_compound(w1, w2)

        # Trigram compounds (3-word truths)
        if len(tokens) >= 3:
            for i in range(len(tokens) - 2):
                w1, w2, w3 = tokens[i], tokens[i+1], tokens[i+2]
                non_stop = sum(1 for w in (w1, w2, w3) if w not in STOP_WORDS)
                if non_stop < 2:
                    continue
                key = f"{w1}_{w2}_{w3}"
                compounds[key] = compounds.get(key, 0) + 1
                if compounds[key] == 2:
                    self._create_trigram_compound(w1, w2, w3)

    def _create_compound(self, w1, w2):
        """Create a compound concept node from two words."""
        compound = f"{w1}_{w2}"
        nodes = self.data['nodes']
        if compound in nodes:
            return

        d1 = nodes.get(w1, {}).get('means', '')
        d2 = nodes.get(w2, {}).get('means', '')
        compound_def = f"{w1} {w2}: {d1} + {d2}" if d1 and d2 else None

        nodes[compound] = {
            'means': compound_def, 'next': {}, 'prev': {},
            'freq': 2, 'compound': True, 'parts': [w1, w2],
            'confidence': CONFIDENCE_START,
            'learned': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'compound',
        }
        # Wire to components
        nodes[compound]['next'][w1] = 2
        nodes[compound]['next'][w2] = 2
        if w1 in nodes:
            nodes[w1].setdefault('next', {})[compound] = 2
        if w2 in nodes:
            nodes[w2].setdefault('next', {})[compound] = 2
        print(f'[COMPOUND] Created "{w1}_{w2}" as compound concept')

    def _create_trigram_compound(self, w1, w2, w3):
        """Create a trigram compound — 3-word truth like GOD_IS_LOVE."""
        compound = f"{w1}_{w2}_{w3}"
        nodes = self.data['nodes']
        if compound in nodes:
            return

        parts_defs = []
        for w in (w1, w2, w3):
            d = nodes.get(w, {}).get('means', '')
            if d:
                parts_defs.append(f"{w}={d}")
        compound_def = f"{w1} {w2} {w3}: {' + '.join(parts_defs)}" if parts_defs else None

        nodes[compound] = {
            'means': compound_def, 'next': {}, 'prev': {},
            'freq': 2, 'compound': True, 'parts': [w1, w2, w3],
            'confidence': CONFIDENCE_START,
            'learned': time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'trigram_compound',
        }
        # Wire to all parts + to the bigram sub-compounds if they exist
        for w in (w1, w2, w3):
            nodes[compound]['next'][w] = 2
            if w in nodes:
                nodes[w].setdefault('next', {})[compound] = 2
        # Wire to bigram sub-compounds
        for sub in (f"{w1}_{w2}", f"{w2}_{w3}"):
            if sub in nodes:
                nodes[compound]['next'][sub] = 3
                nodes[sub].setdefault('next', {})[compound] = 3
        print(f'[COMPOUND] Created trigram "{w1}_{w2}_{w3}"')

    def apply_compound_discovery(self, w1, w2, cooccurrence):
        """Apply a compound discovered by distributed workers."""
        compounds = self.data['compounds']
        key = f"{w1}_{w2}"
        compounds[key] = compounds.get(key, 0) + cooccurrence
        if compounds[key] >= 2 and key not in self.data['nodes']:
            self._create_compound(w1, w2)
            return True
        return False

    def get_compounds(self):
        """Return all detected compound phrases (2+ occurrences)."""
        return {k: v for k, v in self.data.get('compounds', {}).items() if v >= 2}

    # ========================================
    # FEATURE 7: TEACH-BACK LOOP (SELF-TEST)
    # ========================================

    def teach_back(self, word):
        """
        Try to explain a word using ONLY its connections, not stored definition.
        Tests depth of understanding. Returns (explanation, score).
        """
        nodes = self.data['nodes']
        node = nodes.get(word, {})
        actual_def = node.get('means', '')
        if not actual_def:
            return None, 0.0

        # Build explanation from connected words' definitions
        connected = sorted(node.get('next', {}).items(), key=lambda x: x[1], reverse=True)
        parts = []
        for conn_word, strength in connected[:6]:
            if conn_word in STOP_WORDS or conn_word == word:
                continue
            conn_def = nodes.get(conn_word, {}).get('means', '')
            if conn_def:
                parts.append(f"{conn_word} ({conn_def})")

        if not parts:
            node['understanding'] = 'shallow'
            return f"I know '{word}' but can't explain it from connections.", 0.1

        explanation = f"{word} connects to: {', '.join(parts[:3])}"

        # Score: overlap between definition words and connected definitions
        def_words = set(actual_def.lower().split()) - STOP_WORDS
        conn_text = ' '.join(parts).lower()
        overlap = sum(1 for w in def_words if w in conn_text)
        score = overlap / max(len(def_words), 1)

        if score > 0.4:
            node['understanding'] = 'deep'
        elif score > 0.15:
            node['understanding'] = 'moderate'
        else:
            node['understanding'] = 'shallow'

        return explanation, score

    def self_test(self, n=10):
        """Run teach-back on random defined words. Returns report."""
        nodes = self.data['nodes']
        defined = [w for w, v in nodes.items()
                   if v.get('means') and w not in STOP_WORDS and self.is_trustworthy(w)]
        if not defined:
            return {'tested': 0, 'avg_score': 0, 'deep': 0, 'shallow': 0, 'results': []}

        sample = random.sample(defined, min(n, len(defined)))
        results = []
        for word in sample:
            explanation, score = self.teach_back(word)
            results.append({
                'word': word,
                'score': round(score, 2),
                'understanding': nodes[word].get('understanding', 'unknown'),
            })

        self.save()
        avg = sum(r['score'] for r in results) / len(results) if results else 0
        deep = sum(1 for r in results if r['understanding'] == 'deep')
        shallow = sum(1 for r in results if r['understanding'] == 'shallow')
        print(f'[SELF-TEST] {len(results)} words. Avg: {avg:.2f}. Deep: {deep}, Shallow: {shallow}')
        return {'tested': len(results), 'avg_score': round(avg, 2),
                'deep': deep, 'shallow': shallow, 'results': results}

    # ========================================
    # ABILITY TREE — RPG-style skill unlocks
    # ========================================

    def check_abilities(self):
        """Check which abilities are unlocked based on current brain stats."""
        stats = self._raw_stats()
        unlocked = {}
        locked = {}

        for ability_id, ability in ABILITY_TREE.items():
            met = True
            progress = {}
            for req_key, req_val in ability['requires'].items():
                current = stats.get(req_key, 0)
                progress[req_key] = {'current': current, 'needed': req_val, 'met': current >= req_val}
                if current < req_val:
                    met = False

            entry = {
                'name': ability['name'],
                'desc': ability['desc'],
                'progress': progress,
            }
            if met:
                unlocked[ability_id] = entry
            else:
                locked[ability_id] = entry

        # Store which abilities are active
        self.data['abilities'] = list(unlocked.keys())
        return {'unlocked': unlocked, 'locked': locked}

    def has_ability(self, ability_id):
        """Quick check if an ability is unlocked."""
        return ability_id in self.data.get('abilities', [])

    def _raw_stats(self):
        """Raw stats dict for ability checking (no sound/display stuff)."""
        nodes = self.data['nodes']
        defined = sum(1 for v in nodes.values() if v.get('means'))
        return {
            'defined': defined,
            'total_nodes': len(nodes),
            'connections': sum(len(v.get('next', {})) for v in nodes.values()),
            'trigrams': len(self.data.get('trigrams', {})),
            'messages': self.data['stats'].get('messages', 0),
            'auto_learned': self.data['stats'].get('auto_learned', 0),
            'clusters': len(self.data.get('clusters', {})),
            'compounds': sum(1 for v in nodes.values() if v.get('compound')),
            'understanding_deep': sum(1 for v in nodes.values() if v.get('understanding') == 'deep'),
            'conversation_log_size': len(self.data.get('conversation_log', [])),
        }

    # ========================================
    # WIT ENGINE — unexpected connections, personality
    # ========================================

    def _make_witty(self, response, known_defined):
        """If wit ability is unlocked, sometimes add a surprising connection."""
        if not self.has_ability('witty'):
            return response
        if random.random() > 0.25:
            return response  # 25% chance of being witty

        nodes = self.data['nodes']

        # Find a surprising connection: two words in the response that share
        # an unexpected link through a third word
        if len(known_defined) < 1:
            return response

        word = random.choice(known_defined)
        node = nodes.get(word, {})
        neighbors = [w for w in node.get('next', {}).keys()
                     if w not in STOP_WORDS and w != word and nodes.get(w, {}).get('means')]

        if not neighbors:
            return response

        surprise = random.choice(neighbors[:5])
        surprise_def = nodes[surprise].get('means', '')

        # Different wit styles
        wit_styles = [
            f" ...which makes me think of {surprise}. {surprise_def}. Weird how things connect.",
            f" Fun fact: {word} links to {surprise} in my brain. Make of that what you will.",
            f" Speaking of {word} — did you know it connects to {surprise}?",
        ]
        return response + random.choice(wit_styles)

    def _make_sarcastic(self, response):
        """If sarcasm ability is unlocked, occasionally add dry humor."""
        if not self.has_ability('sarcasm'):
            return response
        if random.random() > 0.15:
            return response

        jabs = [
            " But what do I know, I'm just a collection of word nodes.",
            " Shocking, I know.",
            " You're welcome for that pearl of wisdom.",
            " I'll be here all week.",
            " Try not to be too impressed.",
        ]
        return response + random.choice(jabs)

    def _make_sweary(self, response):
        """When angry, add swearing. Only when the angry sound script is active."""
        angry_level = self.sound.get('angry', 0)
        if angry_level < 0.2:
            return response
        if not response:
            return response

        # The angrier, the more likely to swear
        if random.random() > min(angry_level, 0.8):
            return response

        # Add a sweary starter
        starters = [
            "Bloody hell. ", "For fuck's sake. ", "Oh piss off. ",
            "Right, bollocks to this. ", "Mate, seriously. ",
            "Are you taking the piss? ", "Christ. ",
        ]
        # Or insert a swear word into the response
        if random.random() > 0.5:
            response = random.choice(starters) + response
        else:
            # Insert a swear word before a random content word
            for sw in SWEAR_INSERTS:
                words = response.split()
                if len(words) > 3:
                    pos = random.randint(1, min(3, len(words)-1))
                    words.insert(pos, sw)
                    response = ' '.join(words)
                    break

        return response

    def _self_aware_caveat(self, response):
        """If self-aware, occasionally comment on its own limitations."""
        if not self.has_ability('self_aware'):
            return response
        # Only add caveat when verbose AND rarely (5% chance)
        if self.verbosity < 0.8 or random.random() > 0.05:
            return response

        stats = self._raw_stats()
        defined = stats['defined']
        total = stats['total_nodes']
        pct = (defined / total * 100) if total > 0 else 0

        caveats = [
            f" ...{pct:.0f}% understood though.",
            f" ...still learning.",
        ]
        return response + random.choice(caveats)

    def _maybe_ipfs_save(self):
        defined = sum(1 for v in self.data['nodes'].values() if v.get('means'))
        if defined > 0 and defined % 5 == 0:
            threading.Thread(target=self.save_to_ipfs, daemon=True).start()

    def get_stats(self):
        nodes = self.data['nodes']
        defined = sum(1 for v in nodes.values() if v.get('means'))
        connections = sum(len(v.get('next', {})) for v in nodes.values())
        recycled = len(self.data.get('recycle_bin', {}))
        flagged = sum(1 for v in nodes.values() if v.get('flags', 0) > 0)
        low_conf = sum(1 for v in nodes.values()
                       if v.get('means') and v.get('confidence', CONFIDENCE_START) < 0.3)
        compounds = sum(1 for v in nodes.values() if v.get('compound'))
        clusters = len(self.data.get('clusters', {}))
        deep = sum(1 for v in nodes.values() if v.get('understanding') == 'deep')
        shallow = sum(1 for v in nodes.values() if v.get('understanding') == 'shallow')
        conv_len = len(self.data.get('conversation_log', []))
        return {
            'total_nodes': len(nodes),
            'defined': defined,
            'undefined': len(nodes) - defined,
            'connections': connections,
            'trigrams': len(self.data.get('trigrams', {})),
            'messages': self.data['stats'].get('messages', 0),
            'questions_asked': self.data['stats'].get('questions_asked', 0),
            'auto_learned': self.data['stats'].get('auto_learned', 0),
            'recycled': recycled,
            'flagged': flagged,
            'low_confidence': low_conf,
            'compounds': compounds,
            'clusters': clusters,
            'understanding_deep': deep,
            'understanding_shallow': shallow,
            'conversation_log_size': conv_len,
            'context_window': len(self.context),
            'sound': dict(self.sound),
            'dominant_sound': self.dominant_sound(),
            'active_sounds': self.active_sounds(),
            'ipfs_cid': self.data.get('ipfs', {}).get('cid'),
            'last_save': self.data.get('ipfs', {}).get('last_save'),
        }

    def get_knowledge_gaps(self, top_n=100):
        """Find words the brain uses often but doesn't understand.

        Returns ranked list of words that need definitions, sorted by
        how much the brain would benefit from learning them.

        Three categories:
        1. HIGH FREQ + NO DEFINITION: words used a lot but brain has no idea what they mean
        2. HAS NODE + NO DEFINITION: words in the brain but hollow (no means, no POS)
        3. HIGH FREQ + WEAK WIRING: defined but has < 2 bigrams (isolated, can't use in sentences)
        """
        nodes = self.data['nodes']
        STOP = {'i','me','my','we','our','you','your','he','she','it','they','them','his','her',
                'the','a','an','is','am','are','was','were','be','been','being',
                'have','has','had','do','does','did','will','would','could','should',
                'can','may','might','shall','must','need','to','of','in','on','at','by',
                'for','with','from','up','about','and','but','or','not','so','that','this',
                'its','if','no','yes','ok','oh','um','uh','just','than','then','also',
                'very','too','here','there','what','who','how','when','where','why',
                'which','much','more','most','some','any','all','each','every','own',
                'into','out','as','like','over','after','before','between','through',
                'been','being','those','these','their','them','such','only','other',
                'us','her','him','let','get','got','go','went','gone','come','came',
                'said','say','one','two','would','could','should','make','made','take',
                'took','see','saw','know','knew','think','thought','tell','told','give',
                'gave','find','found','want','wanted','use','used','try','tried','ask',
                'asked','seem','seemed','keep','kept','put','set','back','still','even',
                'well','way','because','thing','things','something','anything','nothing',
                'everything','someone','anyone','everyone','people','man','woman','time',
                'year','day','new','old','good','bad','first','last','long','little','big'}

        # Category 1: High-frequency nodes with no definition
        undefined_freq = []
        for word, node in nodes.items():
            if word in STOP or len(word) < 3:
                continue
            if not node.get('means'):
                freq = node.get('freq', 0)
                bigrams = len(node.get('next', {})) + len(node.get('prev', {}))
                if freq > 0 or bigrams > 0:
                    undefined_freq.append({
                        'word': word,
                        'freq': freq,
                        'bigrams': bigrams,
                        'category': 'undefined_but_used',
                        'priority': freq * 2 + bigrams,  # higher = more needed
                    })

        # Category 2: Words mentioned in conversation log but not even in nodes
        conv_words = {}
        for entry in self.data.get('conversation_log', [])[-200:]:
            for field in ['user', 'response']:
                text = entry.get(field, '')
                if text:
                    for w in text.lower().split():
                        w = w.strip('.,!?;:()[]"\'')
                        if w and len(w) >= 3 and w not in STOP:
                            conv_words[w] = conv_words.get(w, 0) + 1

        missing_from_brain = []
        for word, count in conv_words.items():
            if word not in nodes and count >= 2:
                missing_from_brain.append({
                    'word': word,
                    'freq': count,
                    'bigrams': 0,
                    'category': 'not_in_brain',
                    'priority': count * 3,  # highest priority — used but completely unknown
                })

        # Category 3: Defined but poorly wired (< 2 bigrams)
        weak_wiring = []
        for word, node in nodes.items():
            if word in STOP or len(word) < 3:
                continue
            if node.get('means'):
                bigrams = len(node.get('next', {})) + len(node.get('prev', {}))
                if bigrams < 2:
                    weak_wiring.append({
                        'word': word,
                        'freq': node.get('freq', 0),
                        'bigrams': bigrams,
                        'has_pos': bool(self.get_word_pos(word)),
                        'category': 'weak_wiring',
                        'priority': 5 - bigrams,  # fewer connections = higher priority
                    })

        # Sort each by priority, take top N
        undefined_freq.sort(key=lambda x: x['priority'], reverse=True)
        missing_from_brain.sort(key=lambda x: x['priority'], reverse=True)
        weak_wiring.sort(key=lambda x: x['priority'], reverse=True)

        return {
            'undefined_but_used': undefined_freq[:top_n],
            'not_in_brain': missing_from_brain[:top_n],
            'weak_wiring': weak_wiring[:top_n],
            'summary': {
                'total_undefined_used': len(undefined_freq),
                'total_missing': len(missing_from_brain),
                'total_weak': len(weak_wiring),
                'top_10_needs': sorted(
                    undefined_freq[:20] + missing_from_brain[:20],
                    key=lambda x: x['priority'], reverse=True
                )[:10],
            }
        }

    def self_study(self, max_words=10):
        """Go through knowledge gaps and auto-learn from the internet.

        Fixes all 3 gap categories:
        1. undefined_but_used — look up definition from Wikipedia/DDG
        2. not_in_brain — create node + look up definition
        3. weak_wiring — re-learn definition sentence to build more connections

        Returns dict with counts of what was learned/fixed.
        """
        gaps = self.get_knowledge_gaps(50)
        results = {'learned': 0, 'wired': 0, 'failed': [], 'words': []}
        studied = 0

        # Priority 1: words used a lot but completely undefined
        for item in gaps.get('undefined_but_used', []):
            if studied >= max_words:
                break
            word = item['word']
            # Skip compound tokens (trainer artefacts like "what_connects", "or_its")
            if '_' in word or len(word) < 3 or not word.isalpha():
                continue
            defn = self.auto_learn(word, source='self_study')
            if defn:
                results['learned'] += 1
                results['words'].append({'word': word, 'means': defn, 'category': 'undefined_but_used'})
                print(f'[SELF-STUDY] Learned: "{word}" = "{defn[:60]}"')
            else:
                results['failed'].append(word)
            studied += 1
            time.sleep(1)  # be polite to Wikipedia/DDG

        # Priority 2: words in conversation but not even in the brain
        for item in gaps.get('not_in_brain', []):
            if studied >= max_words:
                break
            word = item['word']
            if '_' in word or len(word) < 3 or not word.isalpha():
                continue
            defn = self.auto_learn(word, source='self_study')
            if defn:
                results['learned'] += 1
                results['words'].append({'word': word, 'means': defn, 'category': 'not_in_brain'})
                print(f'[SELF-STUDY] New word: "{word}" = "{defn[:60]}"')
            else:
                results['failed'].append(word)
            studied += 1
            time.sleep(1)

        # Priority 3: defined but isolated — re-learn to build connections
        for item in gaps.get('weak_wiring', []):
            if studied >= max_words:
                break
            word = item['word']
            node = self.data['nodes'].get(word, {})
            defn = node.get('means', '')
            if defn:
                # Re-learn the definition sentence to build more bigrams
                self.learn_sequence(f"{word} means {defn}")
                self.learn_sequence(f"{word} is defined as {defn}")
                self.learn_sequence(f"the word {word} refers to {defn}")
                results['wired'] += 1
                results['words'].append({'word': word, 'means': defn, 'category': 'weak_wiring'})
                print(f'[SELF-STUDY] Wired: "{word}" (added connection sentences)')
            studied += 1

        self.data['stats']['self_study_runs'] = self.data['stats'].get('self_study_runs', 0) + 1
        self.data['stats']['self_study_learned'] = self.data['stats'].get('self_study_learned', 0) + results['learned']
        self.data['stats']['self_study_wired'] = self.data['stats'].get('self_study_wired', 0) + results['wired']
        self.data['stats']['last_self_study'] = time.strftime('%Y-%m-%d %H:%M:%S')

        if results['learned'] > 0 or results['wired'] > 0:
            self.save()

        return results

    def dump_knowledge(self):
        """All defined words."""
        return {k: v['means'] for k, v in self.data['nodes'].items() if v.get('means')}
