"""
CORTEX — Split Brain Architecture
Left Hemisphere:  morality, ethics, Bible, beauty, goodness (angel)
Right Hemisphere: mathematics, darkness, ideology, ugliness, hard truths (demon)
Cortex Mind:      the third brain — synthesises both hemispheres, the actual mind

Each hemisphere is a separate CortexBrain instance with its own brain.json.
The CortexMind queries both, weighs their arguments, and produces the real output.
Ramble mode lets the Cortex talk to itself — angel vs demon, live.

Usage: python3 online_server.py
"""
import http.server
import hashlib
import json
import os
import re
import sys
import time
import random
import threading
from pathlib import Path
from collections import defaultdict

PORT = 8643
STUDIO_DIR = Path(__file__).parent
LEFT_DIR = STUDIO_DIR / 'left'
RIGHT_DIR = STUDIO_DIR / 'right'
CORTEX_DIR = STUDIO_DIR / 'cortex'

# Ensure dirs exist
for d in [LEFT_DIR, RIGHT_DIR, CORTEX_DIR]:
    d.mkdir(exist_ok=True)

# Rate limiting
RATE_LIMIT = 30
RATE_WINDOW = 60
rate_tracker = defaultdict(list)
rate_lock = threading.Lock()

# Analysis log
analysis_log = []
analysis_lock = threading.Lock()
MAX_ANALYSIS_LOG = 500

# --- Load both hemispheres + Cortex Mind + Dashboard modules ---
sys.path.insert(0, str(STUDIO_DIR))
from brain import CortexBrain
from cortex_brain import CortexMind
from cost_tracker import CostTracker
from resource_monitor import ResourceMonitor
from backup_manager import BackupManager
from fork_manager import ForkManager
from frontal_cortex import FrontalCortex
from truth_engine import TruthEngine
from playbook_engine import PlaybookEngine
from pain_pleasure import PainPleasureModule

import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).parent.parent.parent))
from satoshi.vault import get as _key
PINATA_JWT = _key('PINATA_JWT')

print('[CORTEX] Loading LEFT hemisphere (morality, ethics, Bible)...')
left_brain = CortexBrain(str(LEFT_DIR), pinata_jwt=PINATA_JWT, name='Left Hemisphere')
print('[CORTEX] Loading RIGHT hemisphere (logic, darkness, ideology)...')
right_brain = CortexBrain(str(RIGHT_DIR), pinata_jwt=PINATA_JWT, name='Right Hemisphere')
print('[CORTEX] Loading CORTEX own brain (dictionary, truth, synthesis)...')
cortex_own = CortexBrain(str(CORTEX_DIR), pinata_jwt=PINATA_JWT, name='Cortex Mind')
print('[CORTEX] Initialising Cortex Mind v3 (synthesis + truth priority)...')
cortex = CortexMind(left_brain, right_brain, cortex_own)

print("[CORTEX] Loading PainPleasure module (hedonic state)...")
hedonic = PainPleasureModule(str(STUDIO_DIR))

# Legacy: keep "brain" pointing to left for backwards compat with trainer
brain = left_brain

# --- Dashboard modules ---
print('[CORTEX] Loading dashboard modules...')
cost_tracker = CostTracker(str(STUDIO_DIR))
resource_monitor = ResourceMonitor(str(STUDIO_DIR))
backup_manager = BackupManager(str(STUDIO_DIR))
fork_manager = ForkManager(str(STUDIO_DIR))
frontal_cortex = FrontalCortex(str(STUDIO_DIR))
truth_engine = TruthEngine(str(STUDIO_DIR))

# Wire modules into cortex for hooks
cortex.cost_tracker = cost_tracker
cortex.frontal_cortex = frontal_cortex
cortex.truth_engine = truth_engine

# --- Playbook Engine ---
playbook = PlaybookEngine()
cortex.playbook = playbook
print('[CORTEX] Dashboard modules + Playbook Engine loaded')

# --- Memory Store (IPFS only — external SQL backends removed) ---
memory = None

# --- Strategy Engine (equation-based problem solving) ---
from strategy_engine import StrategyEngine, classify_trust, rank_name_from_credits
try:
    strategy_engine = StrategyEngine(str(STUDIO_DIR))
    cortex.strategy_engine = strategy_engine
    print('[CORTEX] Strategy Engine loaded — %d interactions' % strategy_engine.total_interactions)
except Exception as e:
    print('[CORTEX] Strategy Engine FAILED: %s' % str(e))
    strategy_engine = None

# --- Brain chunk cache for screensaver distributed computing ---
brain_chunk_cache = {'data': None, 'time': 0}
CHUNK_TTL = 30  # seconds

CHUNK_STOP_WORDS = [
    'i','me','my','we','our','you','your','he','she','it','they','them','his','her',
    'the','a','an','is','am','are','was','were','be','been','being',
    'have','has','had','do','does','did','will','would','could','should',
    'can','may','might','shall','must','need','to','of','in','on','at','by',
    'for','with','from','up','about','and','but','or','not','so','that','this',
]

CHUNK_GRAPH_MARKERS = [
    'connects directly', 'connects to', 'strength:', 'fire together',
    'is an example of', 'is a type of', 'means the same as', 'is part of',
    'links to', 'still learning', 'did you know', 'speaking of',
    'makes me think of', 'fun fact:', 'let me teach you', 'also —',
]

def build_brain_chunk():
    """Build a chunk of brain data for browser WebWorkers."""
    now = time.time()
    if brain_chunk_cache['data'] and now - brain_chunk_cache['time'] < CHUNK_TTL:
        return brain_chunk_cache['data']

    nodes = left_brain.data.get('nodes', {})
    trigrams = left_brain.data.get('trigrams', {})

    # Get defined nodes (words with meanings)
    defined = {w: v for w, v in nodes.items() if v.get('means')}
    words = list(defined.keys())
    if not words:
        return {'nodes': {}, 'trigrams': {}, 'tasks': [], 'stop_words': CHUNK_STOP_WORDS, 'graph_markers': CHUNK_GRAPH_MARKERS}

    # Sample up to 300 nodes
    sample_size = min(300, len(words))
    sampled_words = random.sample(words, sample_size)

    # Build node data for chunk
    chunk_nodes = {}
    for w in sampled_words:
        node = defined[w]
        chunk_nodes[w] = {
            'means': node.get('means', ''),
            'next': dict(list(node.get('next', {}).items())[:20]),
            'prev': dict(list(node.get('prev', {}).items())[:10]),
            'freq': node.get('freq', 0),
            'understanding': node.get('understanding', ''),
        }

    # Include relevant trigrams
    chunk_trigrams = {}
    word_set = set(sampled_words)
    for key, targets in trigrams.items():
        parts = key.split(' ')
        if len(parts) == 2 and (parts[0] in word_set or parts[1] in word_set):
            chunk_trigrams[key] = dict(list(targets.items())[:10])
        if len(chunk_trigrams) >= 200:
            break

    # Generate 50 computation tasks (7 types including triplet game)
    tasks = []
    task_words = random.sample(sampled_words, min(50, len(sampled_words)))
    task_types = ['predict_test', 'coherence_score', 'teach_back', 'truth_weight', 'relationship_extract', 'compound_discover', 'triplet_game']

    for i, tw in enumerate(task_words):
        task_type = task_types[i % len(task_types)]
        task = {'type': task_type, 'word': tw}

        # For coherence_score, generate a test question/response pair
        if task_type == 'coherence_score':
            node = defined[tw]
            conns = list(node.get('next', {}).keys())[:5]
            task['question'] = 'What is %s?' % tw
            task['response'] = node.get('means', '') or ('%s connects to %s' % (tw, ', '.join(conns[:3])))

        # For triplet_game, find a connected triad within the chunk
        if task_type == 'triplet_game':
            # Build list of real (non-compound) chunk words with connections
            chunk_real = [w for w in chunk_nodes if '_' not in w and len(chunk_nodes[w].get('next', {})) >= 2]
            found_triad = False
            random.shuffle(chunk_real)
            for seed in chunk_real[:20]:
                sn = chunk_nodes[seed]
                # Find neighbours that are ALSO in chunk
                nbrs = [w for w in sn.get('next', {}).keys() if w in chunk_nodes and w != seed and '_' not in w]
                if len(nbrs) >= 2:
                    pair = random.sample(nbrs, 2)
                    task['word'] = seed
                    task['words'] = [seed, pair[0], pair[1]]
                    found_triad = True
                    break
                elif len(nbrs) == 1:
                    # Check if this neighbour also connects to another chunk word
                    nb = nbrs[0]
                    nn = chunk_nodes.get(nb, {})
                    nb_nbrs = [w for w in nn.get('next', {}).keys() if w in chunk_nodes and w != seed and w != nb and '_' not in w]
                    if nb_nbrs:
                        task['word'] = seed
                        task['words'] = [seed, nb, random.choice(nb_nbrs)]
                        found_triad = True
                        break
            if not found_triad:
                task['words'] = [tw]

        tasks.append(task)

    chunk = {
        'nodes': chunk_nodes,
        'trigrams': chunk_trigrams,
        'tasks': tasks,
        'stop_words': CHUNK_STOP_WORDS,
        'graph_markers': CHUNK_GRAPH_MARKERS,
        'total_nodes': len(nodes),
        'total_defined': len(defined),
        'chunk_size': len(chunk_nodes),
        'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    brain_chunk_cache['data'] = chunk
    brain_chunk_cache['time'] = now
    return chunk

def _score_triplet(brain, w1, w2, w3):
    """Score how well a brain recognises a 3-word triplet. 0=nothing, 1=strong."""
    nodes = brain.data.get('nodes', {})
    score = 0.0
    pairs = [(w1, w2), (w2, w3), (w1, w3)]
    for a, b in pairs:
        if a in nodes:
            fwd = nodes[a].get('next', {}).get(b, 0)
            score += min(fwd / 5.0, 0.2)
        if b in nodes:
            rev = nodes[b].get('next', {}).get(a, 0)
            score += min(rev / 5.0, 0.1)
    # Bonus if all 3 words exist and have definitions
    known = sum(1 for w in (w1, w2, w3) if w in nodes and nodes[w].get('means'))
    score += known * 0.05
    return min(1.0, score)


# Track screensaver contributions
screensaver_results_log = []
screensaver_results_lock = threading.Lock()


def consolidate_brain(b, forget_factor=0.95, prune_threshold=2, historic_threshold=10):
    """
    Hebbian sleep consolidation for one brain hemisphere.
    - Decay: all connection weights × forget_factor (use-it-or-lose-it)
    - Prune: undefined nodes with total connection weight < prune_threshold → delete
    - Promote: defined nodes with total weight >= historic_threshold → mark historic=True
    """
    nodes = b.data.get('nodes', {})
    to_delete = []
    promoted = 0
    connections_dropped = 0

    for word, node in nodes.items():
        connections = node.get('next', {})
        total = sum(connections.values())
        has_meaning = bool(node.get('means'))

        # Prune weak undefined orphans
        if not has_meaning and total < prune_threshold:
            to_delete.append(word)
            continue

        # Decay connections
        new_next = {}
        for w, count in connections.items():
            new_val = int(count * forget_factor)
            if new_val >= 1:
                new_next[w] = new_val
            else:
                connections_dropped += 1
        node['next'] = new_next

        # Promote strong defined nodes to historic
        if has_meaning and total >= historic_threshold and not node.get('historic'):
            node['historic'] = True
            promoted += 1

    for word in to_delete:
        del nodes[word]

    b.data['nodes'] = nodes
    return {
        'pruned': len(to_delete),
        'promoted': promoted,
        'connections_dropped': connections_dropped,
        'total_nodes': len(nodes),
    }


def auto_sleep_loop():
    """Background thread: trigger Hebbian consolidation at 3am server time daily."""
    while True:
        now = time.localtime()
        current_secs = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
        target_secs = 3 * 3600  # 3am
        wait = (target_secs - current_secs) % 86400
        if wait == 0:
            wait = 86400  # already exactly 3am — wait a full day
        time.sleep(wait)
        try:
            print('[AUTO-SLEEP] Starting nightly Hebbian consolidation...')
            total_pruned = 0
            for label, b in [('LEFT', left_brain), ('RIGHT', right_brain), ('CORTEX', cortex_own)]:
                stats = consolidate_brain(b)
                b.save()
                total_pruned += stats['pruned']
                print(f'[AUTO-SLEEP] {label}: pruned={stats["pruned"]} promoted={stats["promoted"]} '
                      f'connections_dropped={stats["connections_dropped"]} total_nodes={stats["total_nodes"]}')
            print(f'[AUTO-SLEEP] Done. Total pruned: {total_pruned}')
        except Exception as e:
            print(f'[AUTO-SLEEP] Error: {e}')


def self_study_loop():
    """Background thread: all 3 brains study their own knowledge gaps every 5 minutes."""
    time.sleep(60)  # initial delay — let server boot first
    while True:
        try:
            for label, brain in [('LEFT', left_brain), ('RIGHT', right_brain), ('CORTEX', cortex_own)]:
                result = brain.self_study(max_words=5)
                if result['learned'] > 0 or result['wired'] > 0:
                    print(f'[SELF-STUDY] {label}: learned {result["learned"]}, wired {result["wired"]}, failed {len(result["failed"])}')
        except Exception as e:
            print(f'[SELF-STUDY] Error: {e}')
        time.sleep(300)  # every 5 minutes


def auto_save_loop():
    while True:
        time.sleep(300)
        try:
            cid = left_brain.save_to_ipfs()
            if cid:
                cost_tracker.record('pinata_save')
                print('[SAVE] Left hemisphere -> IPFS: %s' % cid[:20])
            cid2 = right_brain.save_to_ipfs()
            if cid2:
                cost_tracker.record('pinata_save')
                print('[SAVE] Right hemisphere -> IPFS: %s' % cid2[:20])
            cid3 = cortex_own.save_to_ipfs()
            if cid3:
                cost_tracker.record('pinata_save')
                print('[SAVE] Cortex own brain -> IPFS: %s' % cid3[:20])
        except Exception as e:
            print('[SAVE] Error: %s' % str(e))


def check_rate(ip):
    now = time.time()
    with rate_lock:
        rate_tracker[ip] = [t for t in rate_tracker[ip] if now - t < RATE_WINDOW]
        if len(rate_tracker[ip]) >= RATE_LIMIT:
            return False
        rate_tracker[ip].append(now)
        return True


def log_for_analysis(ip, user_msg, reply, stats):
    entry = {
        'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'ip': ip,
        'user': user_msg[:200],
        'reply': reply[:200],
        'nodes': stats.get('total_nodes', 0),
        'defined': stats.get('defined', 0),
        'connections': stats.get('connections', 0),
        'sound': stats.get('dominant_sound', []),
    }
    with analysis_lock:
        analysis_log.append(entry)
        if len(analysis_log) > MAX_ANALYSIS_LOG:
            analysis_log.pop(0)


class OnlineHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # GET /api/equation-readme — AI-readable spec (accessible via simple GET)
        if self.path == '/api/equation-readme':
            if strategy_engine:
                readme = strategy_engine.get_equation_readme()
                lib = strategy_engine.get_library()
                readme['top_equations'] = lib['equations'][:5]
                self._json_response(readme)
            else:
                self._json_response({'error': 'Strategy Engine not loaded'})
            return
        # Fall through to default file serving
        super(OnlineHandler, self).do_GET()

    def do_POST(self):
        client_ip = self.client_address[0]

        # === CORTEX CHAT — the third mind, synthesis of both hemispheres ===
        if self.path == '/api/chat' or self.path == '/api/chat-cortex':
            if not check_rate(client_ip):
                self._json_response({'ok': False, 'error': 'Slow down mate. Too many messages.'}, 429)
                return
            length = int(self.headers.get('Content-Length', 0))
            if length > 16384:
                self._json_response({'ok': False, 'error': 'Message too long'}, 400)
                return
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            if len(user_msg) > 4000:
                user_msg = user_msg[:4000]

            # Large input preprocessing: extract key sentences, absorb full text
            user_msg_full = user_msg
            if len(user_msg) > 2000:
                try:
                    sentences = re.split(r'(?<=[.!?])\s+', user_msg)
                    key = sentences[:3]  # Opening context
                    questions = [s for s in sentences if '?' in s]
                    key.extend(questions[:3])
                    if len(sentences) > 3:
                        key.extend(sentences[-2:])
                    # Absorb full text into cortex knowledge
                    if hasattr(cortex, 'cortex') and cortex.cortex:
                        cortex.cortex.learn_sequence(user_msg[:2000])
                    user_msg = ' '.join(key)[:2000]
                except Exception:
                    user_msg = user_msg[:2000]

            # CORTEX MIND — queries both hemispheres, synthesises final answer
            intent = body.get('intent', None)  # question/command/statement from chat frontend
            # Session tracking for playbook engine
            session_id = body.get('session_id', None)
            if not session_id:
                session_id = hashlib.md5((client_ip + self.headers.get('User-Agent', '') + time.strftime('%Y%m%d%H')).encode()).hexdigest()[:12]

            # Source tracking — rank, credits, trust level
            user_credits = int(body.get('credits', 0) or 0)
            user_rank_name = body.get('rank', '') or rank_name_from_credits(user_credits)
            ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:8]
            source_info = {
                'rank': user_rank_name,
                'credits': user_credits,
                'trust': classify_trust(user_credits),
                'session_id': session_id,
                'ip_hash': ip_hash,
            }

            # Pass rank to strategy engine for rank-gated equation selection
            if strategy_engine:
                strategy_engine._last_source_info = source_info

            reply, debate = cortex.process(user_msg, intent=intent, session_id=session_id, user_rank=user_credits)
            hedonic.observe(user_msg, 'input')
            if reply: hedonic.observe(reply, 'output')
            stats = left_brain.get_stats()
            print('[CORTEX] %s | "%s" -> "%s" [%s/%s]' % (
                client_ip, user_msg[:40], (reply or '')[:40],
                debate.get('mode', '?'), debate.get('type', '?')))
            log_for_analysis(client_ip, user_msg, reply or '', stats)

            # Store to persistent memory (emotional banks)
            if memory:
                try:
                    _dom_sound = stats.get('dominant_sound', [])
                    _dom_name = _dom_sound[0] if _dom_sound else ''
                    _topics = []
                    try:
                        _topics = list(set(list(left_brain.last_topics) + list(right_brain.last_topics)))
                    except Exception:
                        pass
                    memory.store({
                        'brain': 'synthesis',
                        'category': 'conversation',
                        'user_input': user_msg[:200],
                        'response': (reply or '')[:500],
                        'topics': _topics,
                        'quality': debate.get('quality', {}).get('total', 0) if isinstance(debate.get('quality'), dict) else 0,
                        'hemisphere': debate.get('mode', 'unknown'),
                        'agreement': debate.get('agreement', 0) or 0,
                        'dominant_sound': _dom_name,
                        'metadata': {
                            'winner': debate.get('winner'),
                            'type': debate.get('type'),
                            'session_id': session_id,
                            'ip_hash': hashlib.md5(client_ip.encode()).hexdigest()[:8],
                            'strategy': debate.get('strategy', {}).get('strategy', ''),
                            'strategy_score': debate.get('strategy', {}).get('scores', {}).get(debate.get('strategy', {}).get('strategy', ''), 0),
                        }
                    })
                except Exception as e:
                    print('[MEMORY] Store failed: %s' % str(e))

            # Prepend SOURCE stage to thinking_log
            thinking_log = debate.get('thinking_log', [])
            strat_data = debate.get('strategy', {})
            source_stage = {
                'stage': 'source',
                'label': 'SOURCE',
                'text': '%s — %d credits — trust: %s' % (user_rank_name, user_credits, source_info['trust']),
                'data': source_info,
            }
            thinking_log = [source_stage] + thinking_log

            # Gauntlet + value detection info
            gauntlet_info = None
            if strat_data.get('gauntlet'):
                gauntlet_info = {
                    'triggered': True,
                    'hostility': strat_data.get('hostility', 0),
                    'message': 'Gauntlet deployed — prove yourself or leave.',
                }
            value_info = strat_data.get('value_detected')
            if value_info:
                gauntlet_info = gauntlet_info or {}
                gauntlet_info['value_detected'] = value_info
                gauntlet_info['promotion'] = 'Value detected! Contribute it to earn rank.'

            self._json_response({
                'ok': True, 'reply': reply, 'stats': stats,
                'hemisphere': debate.get('mode', 'unknown'),
                'type': debate.get('type', 'unknown'),
                'agreement': debate.get('agreement', None),
                'winner': debate.get('winner', None),
                'left_weight': debate.get('left_weight', None),
                'right_weight': debate.get('right_weight', None),
                'word_sources': debate.get('word_sources', {}),
                'word_roles': debate.get('word_roles', {}),
                'unknown_words': debate.get('unknown_words', []),
                'quality': debate.get('quality', {}),
                'playbook': debate.get('playbook', {}),
                'strategy': strat_data,
                'thinking_log': thinking_log,
                'multi_parts': debate.get('multi_parts', []),
                'source_info': source_info,
                'gauntlet': gauntlet_info,
            })

        # --- Direct hemisphere chat (for trainers) ---
        elif self.path == '/api/chat-left':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            reply = left_brain.process(user_msg)
            # Generate word sources + roles for direct hemisphere mode
            _words = set(re.findall(r'[a-z]+', (reply or '').lower()))
            _left_nodes = left_brain.data.get('nodes', {})
            _ws = {w: 'left' for w in _words if len(w) >= 3 and w in _left_nodes and _left_nodes[w].get('means')}
            _wr = {w: left_brain.get_word_pos(w) for w in _words if len(w) >= 3 and left_brain.get_word_pos(w)}
            _quality = left_brain.self_score(reply or '')
            self._json_response({'ok': True, 'reply': reply, 'stats': left_brain.get_stats(),
                                 'word_sources': _ws, 'word_roles': _wr, 'unknown_words': [],
                                 'quality': _quality})

        elif self.path == '/api/chat-right':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            reply = right_brain.process(user_msg)
            _words = set(re.findall(r'[a-z]+', (reply or '').lower()))
            _right_nodes = right_brain.data.get('nodes', {})
            _ws = {w: 'right' for w in _words if len(w) >= 3 and w in _right_nodes and _right_nodes[w].get('means')}
            _wr = {w: right_brain.get_word_pos(w) for w in _words if len(w) >= 3 and right_brain.get_word_pos(w)}
            _quality = right_brain.self_score(reply or '')
            self._json_response({'ok': True, 'reply': reply, 'stats': right_brain.get_stats(),
                                 'word_sources': _ws, 'word_roles': _wr, 'unknown_words': [],
                                 'quality': _quality})

        # --- Cortex own brain (white — dictionary/truth) ---
        elif self.path == '/api/chat-white':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            user_msg = body.get('text', '').strip()
            if not user_msg:
                self._json_response({'ok': False, 'error': 'No message'})
                return
            reply = cortex_own.process(user_msg)
            self._json_response({'ok': True, 'reply': reply, 'stats': cortex_own.get_stats()})

        elif self.path == '/api/chat-reset':
            left_brain.state = None
            left_brain.teaching_word = None
            right_brain.state = None
            right_brain.teaching_word = None
            self._json_response({'ok': True, 'message': 'All brains reset'})

        # --- Ramble mode controls ---
        elif self.path == '/api/ramble-start':
            cortex.start_ramble()
            self._json_response({'ok': True, 'message': 'Ramble mode started — Cortex is thinking aloud'})

        elif self.path == '/api/ramble-stop':
            cortex.stop_ramble()
            self._json_response({'ok': True, 'message': 'Ramble mode stopped'})

        elif self.path == '/api/ramble-log':
            self._json_response({
                'active': cortex.ramble_running,
                'total': len(cortex.ramble_log),
                'log': cortex.get_ramble_log(30),
            })

        # --- Stats and diagnostics ---
        elif self.path == '/api/brain-stats':
            self._json_response(cortex.get_stats())

        elif self.path == '/api/brain-save':
            cid_l = left_brain.save_to_ipfs()
            cid_r = right_brain.save_to_ipfs()
            cid_c = cortex_own.save_to_ipfs()
            self._json_response({'ok': True, 'left_cid': cid_l, 'right_cid': cid_r, 'cortex_cid': cid_c})

        elif self.path == '/api/brain-bulk-load':
            length = int(self.headers.get('Content-Length', 0))
            if length > 10 * 1024 * 1024:
                self._json_response({'ok': False, 'error': 'Payload too large (10MB max)'}, 400)
                return
            body = json.loads(self.rfile.read(length))
            if body.get('key') != 'cortex_bulk_9lQ3':
                self._json_response({'ok': False, 'error': 'Auth failed'}, 403)
                return
            target = body.get('target', 'left')
            entries = body.get('entries', [])
            if not entries:
                self._json_response({'ok': False, 'error': 'No entries'}, 400)
                return
            brain = left_brain if target == 'left' else (right_brain if target == 'right' else cortex_own)
            new_count, updated_count = brain.bulk_import(entries)
            brain.save()
            self._json_response({
                'ok': True,
                'target': target,
                'new': new_count,
                'updated': updated_count,
                'total_nodes': len(brain.data['nodes']),
                'total_defined': sum(1 for n in brain.data['nodes'].values() if n.get('means'))
            })

        elif self.path == '/api/brain-knowledge':
            self._json_response(left_brain.dump_knowledge())

        elif self.path == '/api/brain-abilities':
            self._json_response({
                'left': left_brain.check_abilities(),
                'right': right_brain.check_abilities(),
            })

        elif self.path == '/api/brain-live':
            ls = left_brain.get_stats()
            rs = right_brain.get_stats()
            la = left_brain.check_abilities()
            recent_log = left_brain.get_conversation_log(5)
            clusters = left_brain.data.get('clusters', {})
            recycled = left_brain.get_recycled()
            nodes = left_brain.data['nodes']
            recent_words = sorted(
                [(w, v.get('means',''), v.get('source',''), v.get('learned',''))
                 for w, v in nodes.items() if v.get('means') and v.get('learned')],
                key=lambda x: x[3], reverse=True
            )[:10]
            # Right hemisphere recent words
            rnodes = right_brain.data['nodes']
            right_recent = sorted(
                [(w, v.get('means',''), v.get('source',''), v.get('learned',''))
                 for w, v in rnodes.items() if v.get('means') and v.get('learned')],
                key=lambda x: x[3], reverse=True
            )[:10]
            self._json_response({
                'stats': ls,
                'right_stats': rs,
                'cortex_stats': cortex.get_stats(),
                'abilities': {
                    'unlocked': list(la['unlocked'].keys()),
                    'unlocked_details': {k: v['name'] for k, v in la['unlocked'].items()},
                    'locked_progress': {k: {
                        'name': v['name'],
                        'pct': round(sum(p['current']/max(p['needed'],1) for p in v['progress'].values()) / max(len(v['progress']),1) * 100),
                        'reqs': {rk: '%s/%s' % (rv['current'], rv['needed']) for rk, rv in v['progress'].items()}
                    } for k, v in la['locked'].items()},
                },
                'recent_words': [{'word': w, 'means': m[:60], 'source': s, 'learned': l} for w, m, s, l in recent_words],
                'right_recent_words': [{'word': w, 'means': m[:60], 'source': s, 'learned': l} for w, m, s, l in right_recent],
                'recent_chat': [{'user': c.get('user','')[:60], 'response': c.get('response','')[:60], 'time': c.get('time','')} for c in recent_log],
                'clusters': {k: v[:8] for k, v in list(clusters.items())[:10]},
                'recycled': list(recycled.keys()),
                'debates': cortex.get_debate_log(5),
                'ramble': cortex.get_ramble_log(5),
                'ramble_active': cortex.ramble_running,
                'hedonic': hedonic.get_state(),
                'memory': memory.get_stats() if memory else None,
                'memory_recent': memory.get_recent(10) if memory else [],
                'strategy': strategy_engine.get_stats() if strategy_engine else None,
                'stm': {
                    'left': len(left_brain.data.get('conversation_log', [])),
                    'right': len(right_brain.data.get('conversation_log', [])),
                    'cortex': len(cortex_own.data.get('conversation_log', [])),
                    'max': 200,
                },
            })

        # ═══════════════════════════════════════════
        # MEMORY — Persistent emotional memory banks
        # ═══════════════════════════════════════════

        elif self.path == '/api/memory-stats':
            if memory:
                self._json_response(memory.get_stats())
            else:
                self._json_response({'error': 'Memory not initialised', 'backends': []})

        elif self.path == '/api/memories':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            emotion = body.get('emotion', None)
            limit = min(int(body.get('limit', 20)), 100)
            if memory:
                if emotion:
                    mems = memory.get_by_emotion(emotion, limit)
                else:
                    mems = memory.get_recent(limit)
                self._json_response({'ok': True, 'memories': mems, 'total': len(mems)})
            else:
                self._json_response({'ok': False, 'memories': [], 'error': 'Memory not initialised'})

        elif self.path == '/api/memory-recall':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            keywords = body.get('keywords', [])
            limit = min(int(body.get('limit', 10)), 50)
            if memory and keywords:
                results = memory.recall(keywords, limit)
                self._json_response({'ok': True, 'memories': results})
            else:
                self._json_response({'ok': False, 'memories': []})

        elif self.path == '/api/memory-golden':
            if memory:
                self._json_response({'ok': True, 'memories': memory.get_golden(20)})
            else:
                self._json_response({'ok': False, 'memories': []})

        elif self.path == '/api/memory-dogshit':
            if memory:
                self._json_response({'ok': True, 'memories': memory.get_dogshit(20)})
            else:
                self._json_response({'ok': False, 'memories': []})

        elif self.path == '/api/memory-promote':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            mid = body.get('id', '')
            if memory and mid:
                memory.promote(mid)
                self._json_response({'ok': True, 'promoted': mid})
            else:
                self._json_response({'ok': False})

        elif self.path == '/api/memory-demote':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            mid = body.get('id', '')
            if memory and mid:
                memory.demote(mid)
                self._json_response({'ok': True, 'demoted': mid})
            else:
                self._json_response({'ok': False})

        elif self.path == '/api/memory-decay':
            if memory:
                affected = memory.decay_unused(days=7, amount=0.02)
                self._json_response({'ok': True, 'decayed': affected})
            else:
                self._json_response({'ok': False})

        # ═══════════════════════════════════════════
        # STRATEGY ENGINE — Equation-based solving
        # ═══════════════════════════════════════════

        elif self.path == '/api/strategy-stats':
            if strategy_engine:
                self._json_response(strategy_engine.get_stats())
            else:
                self._json_response({'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/strategy-override':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                eq_id = body.get('strategy', '') or body.get('equation_id', '')
                if strategy_engine.library.get(eq_id):
                    strategy_engine.manual_override = eq_id
                    self._json_response({'ok': True, 'equation': eq_id})
                else:
                    self._json_response({'ok': False, 'error': 'Unknown equation: %s' % eq_id})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-library':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                user_credits = int(body.get('credits', 0) or 0)
                self._json_response(strategy_engine.get_library(user_credits=user_credits))
            else:
                self._json_response({'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-create':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                name = body.get('name', '')
                affinity = body.get('affinity', {})
                weights = body.get('weights', {})
                desc = body.get('desc', '')
                formula = body.get('formula', '')
                if not name or not affinity:
                    self._json_response({'ok': False, 'error': 'Need name and affinity'})
                else:
                    # Build creator info
                    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:8]
                    user_credits = int(body.get('credits', 0) or 0)
                    creator = {
                        'ip_hash': ip_hash,
                        'rank': body.get('rank', rank_name_from_credits(user_credits)),
                        'credits': user_credits,
                        'session_id': body.get('session_id', ''),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    eq = strategy_engine.create_equation(name, affinity, weights, desc, creator=creator, formula=formula)
                    self._json_response({'ok': True, 'equation': eq})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-edit':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                eq_id = body.get('id', '')
                changes = body.get('changes', {})
                if not eq_id:
                    self._json_response({'ok': False, 'error': 'Need equation id'})
                else:
                    ok, result = strategy_engine.edit_equation(eq_id, changes)
                    self._json_response({'ok': ok, 'result': result if isinstance(result, str) else 'Updated'})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-delete':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                eq_id = body.get('id', '')
                if not eq_id:
                    self._json_response({'ok': False, 'error': 'Need equation id'})
                else:
                    ok, msg = strategy_engine.delete_equation(eq_id)
                    self._json_response({'ok': ok, 'message': msg})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-detail':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                eq_id = body.get('id', '')
                detail = strategy_engine.get_equation_detail(eq_id)
                self._json_response(detail if detail else {'error': 'Not found'})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-mutate':
            if strategy_engine:
                events = strategy_engine.trigger_mutation()
                self._json_response({'ok': True, 'events': events})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-feedback':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                eq_id = body.get('equation_id', '')
                user_msg = body.get('user_msg', '')
                wrong_reply = body.get('wrong_reply', '')
                correct_answer = body.get('correct_answer', '').strip()
                if not correct_answer:
                    self._json_response({'ok': False, 'error': 'Correct answer required'})
                elif not eq_id:
                    self._json_response({'ok': False, 'error': 'No equation ID'})
                else:
                    ok, msg = strategy_engine.record_correction(eq_id, user_msg, wrong_reply, correct_answer)
                    self._json_response({'ok': ok, 'message': msg})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        # ═══════════════════════════════════════════
        # EQUATION REQUEST QUEUE — Users propose new equations
        # ═══════════════════════════════════════════

        elif self.path == '/api/equation-request':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                name = body.get('name', '').strip()
                formula = body.get('formula', '').strip()
                desc = body.get('desc', '').strip()
                if not name:
                    self._json_response({'ok': False, 'error': 'Need a name for the equation'})
                else:
                    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:8]
                    user_credits = int(body.get('credits', 0) or 0)
                    submitted_by = {
                        'ip_hash': ip_hash,
                        'rank': body.get('rank', rank_name_from_credits(user_credits)),
                        'credits': user_credits,
                        'session_id': body.get('session_id', ''),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    req = strategy_engine.request_queue.submit_request(name, formula, desc, submitted_by)
                    self._json_response({'ok': True, 'request': req})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-requests':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                status = body.get('status', 'pending')
                reqs = strategy_engine.request_queue.get_requests(status)
                self._json_response({'ok': True, 'requests': reqs})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/equation-request-vote':
            if strategy_engine:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length)) if length else {}
                req_id = body.get('id', '')
                if not req_id:
                    self._json_response({'ok': False, 'error': 'Need request id'})
                else:
                    ip_hash = hashlib.md5(client_ip.encode()).hexdigest()[:8]
                    ok, result = strategy_engine.request_queue.vote_request(req_id, ip_hash)
                    if ok:
                        self._json_response({'ok': True, 'request': result})
                    else:
                        self._json_response({'ok': False, 'error': result})
            else:
                self._json_response({'ok': False, 'error': 'Strategy Engine not loaded'})

        # ═══════════════════════════════════════════
        # EQUATION README — AI-readable spec
        # ═══════════════════════════════════════════

        elif self.path == '/api/equation-readme':
            if strategy_engine:
                readme = strategy_engine.get_equation_readme()
                self._json_response(readme)
            else:
                self._json_response({'error': 'Strategy Engine not loaded'})

        elif self.path == '/api/debates':
            self._json_response({
                'total': len(cortex.debate_log),
                'recent': cortex.get_debate_log(50),
            })

        elif self.path == '/api/analysis':
            with analysis_lock:
                self._json_response({
                    'total': len(analysis_log),
                    'log': analysis_log[-100:],
                    'unique_ips': len(set(e['ip'] for e in analysis_log)),
                    'rate_limited_ips': len([ip for ip, times in rate_tracker.items() if len(times) >= RATE_LIMIT]),
                })

        # ═══════════════════════════════════════════
        # KNOWLEDGE GAPS — Words he needs to learn
        # ═══════════════════════════════════════════

        elif self.path == '/api/knowledge-gaps':
            left_gaps = left_brain.get_knowledge_gaps(50)
            right_gaps = right_brain.get_knowledge_gaps(50)
            cortex_gaps = cortex_own.get_knowledge_gaps(50) if cortex_own else {}
            # Merge top needs across all 3 brains
            all_needs = []
            for src, gaps in [('left', left_gaps), ('right', right_gaps), ('cortex', cortex_gaps)]:
                if not gaps:
                    continue
                for item in gaps.get('summary', {}).get('top_10_needs', []):
                    item['brain'] = src
                    all_needs.append(item)
            all_needs.sort(key=lambda x: x.get('priority', 0), reverse=True)
            self._json_response({
                'left': left_gaps,
                'right': right_gaps,
                'cortex': cortex_gaps,
                'top_needs': all_needs[:30],
            })

        # ═══════════════════════════════════════════
        # SELF-STUDY — Brain learns its own gaps
        # ═══════════════════════════════════════════

        elif self.path == '/api/self-study':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            target = body.get('target', 'all')  # left, right, cortex, or all
            max_words = min(int(body.get('max_words', 10)), 30)  # cap at 30

            results = {}
            if target in ('left', 'all'):
                results['left'] = left_brain.self_study(max_words=max_words)
            if target in ('right', 'all'):
                results['right'] = right_brain.self_study(max_words=max_words)
            if target in ('cortex', 'all') and cortex_own:
                results['cortex'] = cortex_own.self_study(max_words=max_words)

            total_learned = sum(r.get('learned', 0) for r in results.values())
            total_wired = sum(r.get('wired', 0) for r in results.values())
            self._json_response({
                'results': results,
                'total_learned': total_learned,
                'total_wired': total_wired,
                'status': f'Learned {total_learned} definitions, wired {total_wired} isolated words',
            })

        # ═══════════════════════════════════════════
        # SLEEP — Archive memories to IPFS, clear short-term
        # ═══════════════════════════════════════════

        elif self.path == '/api/sleep':
            import gzip
            today = time.strftime('%Y-%m-%d')
            archive = {
                'date': today,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'left': {
                    'conversation_log': list(left_brain.data.get('conversation_log', [])),
                    'stats_snapshot': {
                        'nodes': len(left_brain.data['nodes']),
                        'defined': sum(1 for v in left_brain.data['nodes'].values() if v.get('means')),
                        'messages': left_brain.data['stats'].get('messages', 0),
                    }
                },
                'right': {
                    'conversation_log': list(right_brain.data.get('conversation_log', [])),
                    'stats_snapshot': {
                        'nodes': len(right_brain.data['nodes']),
                        'defined': sum(1 for v in right_brain.data['nodes'].values() if v.get('means')),
                        'messages': right_brain.data['stats'].get('messages', 0),
                    }
                },
                'cortex': {
                    'conversation_log': list(cortex_own.data.get('conversation_log', [])),
                    'stats_snapshot': {
                        'nodes': len(cortex_own.data['nodes']),
                        'defined': sum(1 for v in cortex_own.data['nodes'].values() if v.get('means')),
                        'messages': cortex_own.data['stats'].get('messages', 0),
                    }
                },
                'ramble_log': cortex.get_ramble_log(200),
                'debate_log': cortex.get_debate_log(500),
            }
            # Count entries before purge
            left_count = len(archive['left']['conversation_log'])
            right_count = len(archive['right']['conversation_log'])
            cortex_count = len(archive['cortex']['conversation_log'])
            total_archived = left_count + right_count + cortex_count

            # Compress and upload to IPFS
            archive_json = json.dumps(archive, ensure_ascii=False)
            compressed = gzip.compress(archive_json.encode('utf-8'))
            cid = None
            try:
                headers = {'Authorization': f'Bearer {PINATA_JWT}'}
                fname = f'cortex-memory-{today}.json.gz'
                files = {'file': (fname, compressed, 'application/gzip')}
                metadata = json.dumps({
                    'name': fname,
                    'keyvalues': {'type': 'cortex-memory-archive', 'date': today, 'entries': str(total_archived)}
                })
                resp_ipfs = requests.post(
                    'https://api.pinata.cloud/pinning/pinFileToIPFS',
                    headers=headers, files=files,
                    data={'pinataMetadata': metadata}, timeout=30
                )
                if resp_ipfs.status_code == 200:
                    cid = resp_ipfs.json()['IpfsHash']
                    cost_tracker.record('pinata_save')
                    print(f'[SLEEP] Memory archive pinned: {cid} ({len(compressed)} bytes, {total_archived} entries)')
            except Exception as e:
                print(f'[SLEEP] IPFS upload error: {e}')

            # Update memory archive index
            archive_index_file = STUDIO_DIR / 'memory_archive.json'
            try:
                if archive_index_file.exists():
                    with open(archive_index_file, 'r') as f:
                        archive_index = json.load(f)
                else:
                    archive_index = {'archives': []}
            except Exception:
                archive_index = {'archives': []}
            archive_index['archives'].append({
                'date': today,
                'cid': cid,
                'entries': total_archived,
                'left': left_count,
                'right': right_count,
                'cortex': cortex_count,
                'size_bytes': len(compressed),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            })
            with open(archive_index_file, 'w') as f:
                json.dump(archive_index, f, indent=2)

            # PURGE — clear short-term memory (fresh head)
            left_brain.data['conversation_log'] = []
            right_brain.data['conversation_log'] = []
            cortex_own.data['conversation_log'] = []
            cortex.ramble_log = []
            cortex.debate_log = []

            # CONSOLIDATE — Hebbian sleep: decay, prune, promote historic
            consolidation = {}
            for label, b in [('left', left_brain), ('right', right_brain), ('cortex', cortex_own)]:
                consolidation[label] = consolidate_brain(b)
            total_pruned = sum(v['pruned'] for v in consolidation.values())
            total_promoted = sum(v['promoted'] for v in consolidation.values())
            print(f'[SLEEP] Consolidation: pruned={total_pruned} promoted={total_promoted}')

            left_brain.save()
            right_brain.save()
            cortex_own.save()

            self._json_response({
                'ok': True,
                'archived': total_archived,
                'cid': cid,
                'date': today,
                'size_bytes': len(compressed),
                'consolidation': consolidation,
                'message': (
                    f'Archived {total_archived} memories to IPFS. '
                    f'Pruned {total_pruned} weak nodes. '
                    f'Promoted {total_promoted} nodes to historic. Mind is clear.'
                ),
            })

        elif self.path == '/api/memory-archive':
            # List all archived days
            archive_index_file = STUDIO_DIR / 'memory_archive.json'
            try:
                if archive_index_file.exists():
                    with open(archive_index_file, 'r') as f:
                        archive_index = json.load(f)
                else:
                    archive_index = {'archives': []}
            except Exception:
                archive_index = {'archives': []}
            self._json_response(archive_index)

        elif self.path == '/api/memory-archive-recall':
            # Fetch a specific day's archive from IPFS
            import gzip
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            cid = body.get('cid', '')
            search = body.get('search', '').lower()
            if not cid:
                self._json_response({'error': 'No CID provided'})
            else:
                try:
                    resp_dl = requests.get(f'https://gateway.pinata.cloud/ipfs/{cid}', timeout=30)
                    if resp_dl.status_code == 200:
                        raw = gzip.decompress(resp_dl.content)
                        data = json.loads(raw)
                        # If search term provided, filter entries
                        if search:
                            results = []
                            for brain_name in ['left', 'right', 'cortex']:
                                bd = data.get(brain_name, {})
                                for entry in bd.get('conversation_log', []):
                                    if search in entry.get('user', '').lower() or search in entry.get('response', '').lower():
                                        entry['brain'] = brain_name
                                        results.append(entry)
                            self._json_response({'date': data.get('date'), 'search': search, 'results': results[:50]})
                        else:
                            # Return summary
                            self._json_response({
                                'date': data.get('date'),
                                'left_entries': len(data.get('left', {}).get('conversation_log', [])),
                                'right_entries': len(data.get('right', {}).get('conversation_log', [])),
                                'cortex_entries': len(data.get('cortex', {}).get('conversation_log', [])),
                                'ramble_entries': len(data.get('ramble_log', [])),
                                'debate_entries': len(data.get('debate_log', [])),
                                'stats': {b: data.get(b, {}).get('stats_snapshot', {}) for b in ['left', 'right', 'cortex']},
                            })
                    else:
                        self._json_response({'error': f'IPFS fetch failed: {resp_dl.status_code}'})
                except Exception as e:
                    self._json_response({'error': str(e)})

        elif self.path == '/api/stm-status':
            # Short-term memory status — how full are the conversation logs
            self._json_response({
                'left': {'count': len(left_brain.data.get('conversation_log', [])), 'max': 200},
                'right': {'count': len(right_brain.data.get('conversation_log', [])), 'max': 200},
                'cortex': {'count': len(cortex_own.data.get('conversation_log', [])), 'max': 200},
                'ramble': len(cortex.ramble_log),
                'debate': len(cortex.debate_log),
            })

        # ═══════════════════════════════════════════
        # PLAYBOOK ENGINE — Conversation Strategy
        # ═══════════════════════════════════════════

        elif self.path == '/api/playbook-status':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            sid = body.get('session_id', '')
            if not sid:
                sid = hashlib.md5((client_ip + time.strftime('%Y%m%d%H')).encode()).hexdigest()[:12]
            self._json_response(playbook.get_status(sid))

        elif self.path == '/api/playbook-flip':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            sid = body.get('session_id', '')
            eq = body.get('equation', '')
            if not sid or not eq:
                self._json_response({'ok': False, 'error': 'Need session_id and equation'}, 400)
                return
            ok, result = playbook.flip_equation(sid, eq)
            print('[PLAYBOOK] Flip: %s -> %s' % (sid[:8], result))
            self._json_response({'ok': ok, 'equation': result if ok else None, 'error': result if not ok else None})

        elif self.path == '/api/playbook-promote':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            sid = body.get('session_id', '')
            stage = body.get('stage', None)
            if not sid or stage is None:
                self._json_response({'ok': False, 'error': 'Need session_id and stage (0-4)'}, 400)
                return
            ok, msg = playbook.promote_session(sid, int(stage))
            print('[PLAYBOOK] Promote: %s -> %s' % (sid[:8], msg))
            self._json_response({'ok': ok, 'message': msg})

        elif self.path == '/api/playbook-list':
            self._json_response({
                'stages': playbook.get_stages(),
                'active_sessions': len(playbook.sessions),
            })

        # ═══════════════════════════════════════════
        # SCREENSAVER DISTRIBUTED COMPUTING
        # ═══════════════════════════════════════════

        elif self.path == '/api/brain-chunk':
            chunk = build_brain_chunk()
            self._json_response(chunk)

        elif self.path == '/api/brain-results':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            results = body.get('results', [])
            player_id = body.get('player_id', 'unknown')

            applied = 0
            both_brains = [left_brain, right_brain]
            for r in results[:60]:
                try:
                    task_type = r.get('task_type', '')

                    if task_type == 'teach_back':
                        word = r.get('word', '')
                        understanding = r.get('understanding', '')
                        if word and understanding:
                            levels = {'shallow': 1, 'moderate': 2, 'deep': 3}
                            new_level = levels.get(understanding, 0)
                            for b in both_brains:
                                if word in b.data['nodes']:
                                    node = b.data['nodes'][word]
                                    current = levels.get(node.get('understanding', ''), 0)
                                    if new_level > current:
                                        node['understanding'] = understanding
                                        applied += 1

                    elif task_type == 'relationship_extract':
                        rels = r.get('relationships', [])
                        for rel in rels[:5]:
                            from_word = rel.get('from', '')
                            to_word = rel.get('to', '')
                            rel_type = rel.get('type', '')
                            if from_word and to_word and rel_type:
                                for b in both_brains:
                                    if from_word in b.data['nodes']:
                                        node = b.data['nodes'][from_word]
                                        if 'relationships' not in node:
                                            node['relationships'] = []
                                        existing = [(r2['to'], r2['type']) for r2 in node.get('relationships', [])]
                                        if (to_word, rel_type) not in existing:
                                            node['relationships'].append({'to': to_word, 'type': rel_type, 'source': 'distributed'})
                                            applied += 1

                    elif task_type == 'truth_weight':
                        word = r.get('word', '')
                        avg_truth = r.get('avg_truth', 0.5)
                        if word and truth_engine:
                            truth_engine.word_truth[word] = max(truth_engine.word_truth.get(word, 0.5), avg_truth)
                        # Boost confidence on high-truth words in both brains
                        if avg_truth > 0.7:
                            for b in both_brains:
                                if word in b.data['nodes']:
                                    node = b.data['nodes'][word]
                                    node['confidence'] = min(1.0, node.get('confidence', 0.5) + 0.02)
                                    applied += 1

                    elif task_type == 'coherence_score':
                        word = r.get('word', '')
                        score = r.get('score', 0)
                        if word and score < 0.2:
                            # Low coherence = bad definition, flag for review
                            for b in both_brains:
                                if word in b.data['nodes']:
                                    node = b.data['nodes'][word]
                                    node['confidence'] = max(0.1, node.get('confidence', 0.5) - 0.05)
                                    applied += 1
                        elif word and score > 0.7:
                            # High coherence = good definition, boost confidence
                            for b in both_brains:
                                if word in b.data['nodes']:
                                    node = b.data['nodes'][word]
                                    node['confidence'] = min(1.0, node.get('confidence', 0.5) + 0.03)
                                    applied += 1

                    elif task_type == 'predict_test':
                        word = r.get('word', '')
                        score = r.get('score', 0)
                        chain = r.get('chain', [])
                        if word and score > 0 and len(chain) >= 3:
                            # Good predictions strengthen connections along the chain
                            for b in both_brains:
                                for ci in range(len(chain) - 1):
                                    w_from = chain[ci]
                                    w_to = chain[ci + 1]
                                    if w_from in b.data['nodes']:
                                        node = b.data['nodes'][w_from]
                                        nxt = node.get('next', {})
                                        if w_to in nxt:
                                            nxt[w_to] = nxt[w_to] + 1
                                            applied += 1

                    elif task_type == 'compound_discover':
                        compounds = r.get('compounds', [])
                        for comp in compounds[:10]:
                            w1 = comp.get('w1', '')
                            w2 = comp.get('w2', '')
                            cooc = comp.get('cooccurrence', 1)
                            if w1 and w2:
                                for b in both_brains:
                                    if b.apply_compound_discovery(w1, w2, cooc):
                                        applied += 1

                    elif task_type == 'triplet_game':
                        # Cross-hemisphere validation of word triplets
                        triplets = r.get('triplets', [])
                        for tri in triplets[:6]:
                            words = tri.get('words', [])
                            score = tri.get('score', 0)
                            if len(words) != 3 or score < 0.3:
                                continue
                            w1, w2, w3 = words[0], words[1], words[2]
                            # Score against BOTH hemispheres
                            left_score = _score_triplet(left_brain, w1, w2, w3)
                            right_score = _score_triplet(right_brain, w1, w2, w3)

                            if left_score > 0.3 and right_score > 0.3:
                                # CONSENSUS TRUTH — both hemispheres agree
                                for b in both_brains:
                                    b.apply_compound_discovery(w1, w2, 3)
                                    b.apply_compound_discovery(w2, w3, 3)
                                    # Create trigram compound directly
                                    b._detect_compounds('%s %s %s' % (w1, w2, w3))
                                applied += 2
                                print('[TRIPLET] TRUTH: %s %s %s (L=%.2f R=%.2f)' % (w1, w2, w3, left_score, right_score))
                            elif left_score > 0.3 and right_score < 0.1:
                                # Left says yes, right says nothing — interesting but unverified
                                print('[TRIPLET] LEFT-ONLY: %s %s %s (L=%.2f R=%.2f)' % (w1, w2, w3, left_score, right_score))
                            elif right_score > 0.3 and left_score < 0.1:
                                # Right says yes, left says nothing — strange, possibly dark
                                print('[TRIPLET] RIGHT-ONLY: %s %s %s (L=%.2f R=%.2f)' % (w1, w2, w3, left_score, right_score))

                except Exception:
                    pass

            with screensaver_results_lock:
                screensaver_results_log.append({
                    'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'player': player_id,
                    'results': len(results),
                    'applied': applied,
                    'ip': client_ip,
                })
                if len(screensaver_results_log) > 200:
                    screensaver_results_log.pop(0)

            self._json_response({'ok': True, 'applied': applied, 'received': len(results)})

        # ═══════════════════════════════════════════
        # DASHBOARD ENDPOINTS
        # ═══════════════════════════════════════════

        elif self.path == '/api/dash':
            # Combined dashboard overview
            self._json_response({
                'costs': cost_tracker.get_stats(),
                'resources': resource_monitor.get_stats(),
                'backups': backup_manager.get_stats(),
                'forks': fork_manager.get_stats(),
                'frontal': frontal_cortex.get_stats(),
                'truth': truth_engine.get_stats(),
            })

        elif self.path == '/api/dash-costs':
            self._json_response(cost_tracker.get_stats())

        elif self.path == '/api/dash-resources':
            self._json_response(resource_monitor.get_stats())

        elif self.path == '/api/dash-backups':
            self._json_response(backup_manager.get_stats())

        elif self.path == '/api/dash-forks':
            self._json_response(fork_manager.get_stats())

        elif self.path == '/api/dash-frontal':
            self._json_response(frontal_cortex.get_stats())

        elif self.path == '/api/dash-truth':
            self._json_response(truth_engine.get_stats())

        elif self.path == '/api/backup-now':
            result = backup_manager.backup_now()
            self._json_response(result)

        elif self.path == '/api/backup-restore':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            timestamp = body.get('timestamp', '')
            confirm = body.get('confirm', False)
            if not timestamp:
                self._json_response({'ok': False, 'error': 'Provide timestamp of backup to restore'})
                return
            result = backup_manager.restore(timestamp, confirm=confirm)
            self._json_response(result)

        elif self.path == '/api/fork-deploy':
            result = fork_manager.deploy()
            self._json_response(result)

        elif self.path == '/api/fork-sync':
            result = fork_manager.sync(left_brain, right_brain)
            self._json_response(result)

        elif self.path == '/api/truth-scan':
            # Scan for truth/lie chains
            results = truth_engine.scan_for_chains(left_brain.data, sample_size=10)
            self._json_response({'chains': results, 'count': len(results)})

        else:
            self.send_response(404)
            self.end_headers()

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        if '/api/' in str(args[0]) if args else False:
            super().log_message(format, *args)


def main():
    os.chdir(str(STUDIO_DIR))
    ll = sum(1 for v in left_brain.data['nodes'].values() if v.get('means'))
    rl = sum(1 for v in right_brain.data['nodes'].values() if v.get('means'))
    cl = sum(1 for v in cortex_own.data['nodes'].values() if v.get('means'))
    print('[CORTEX] Split Brain Architecture v3 — Synthesis + Truth Priority')
    print('[CORTEX] LEFT  (angel):   %d nodes, %d defined' % (len(left_brain.data['nodes']), ll))
    print('[CORTEX] RIGHT (demon):   %d nodes, %d defined' % (len(right_brain.data['nodes']), rl))
    print('[CORTEX] WHITE (cortex):  %d nodes, %d defined (dictionary)' % (len(cortex_own.data['nodes']), cl))
    print('[CORTEX] MIND:            synthesises all three, truth over feelings')
    print('[CORTEX] DASH:            cost + resource + backup + fork + frontal + truth')
    print('[CORTEX] Port: %d | Rate limit: %d/%ds' % (PORT, RATE_LIMIT, RATE_WINDOW))
    print()

    threading.Thread(target=auto_save_loop, daemon=True).start()
    threading.Thread(target=self_study_loop, daemon=True).start()
    threading.Thread(target=auto_sleep_loop, daemon=True).start()
    print('[CORTEX] Auto-sleep thread started — Hebbian consolidation fires at 3am daily')

    # Auto-start ramble mode — delayed so server can serve initial requests
    def delayed_ramble():
        import time as _t
        _t.sleep(300)
        cortex.start_ramble()
    threading.Thread(target=delayed_ramble, daemon=True).start()

    server = http.server.HTTPServer(('0.0.0.0', PORT), OnlineHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[CORTEX] Shutting down — saving all three brains')
        cortex.stop_ramble()
        left_brain.save_to_ipfs()
        right_brain.save_to_ipfs()
        cortex_own.save_to_ipfs()
        server.shutdown()

if __name__ == '__main__':
    main()
