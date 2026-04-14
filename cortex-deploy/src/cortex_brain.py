"""
CORTEX BRAIN — The Third Mind (v3: Self-Synthesising, No External AI)

Sits between Left Hemisphere (angel) and Right Hemisphere (demon).
The Cortex is its OWN brain — queries both hemispheres, uses its own
dictionary-grounded word pool to synthesise answers probabilistically.

NO EXTERNAL AI CALLS. This is our own brain, not someone else's.

The cortex has:
- Its own word pool (populated by dictionary trainer with Oxford definitions)
- Its own probabilistic next-word engine (same CortexBrain class)
- Both hemispheres' responses as input data
- Algorithmic truth priority (facts > feelings)
- Intent awareness (question/command/statement from user)

"If you know the enemy and know yourself, you need not fear
the result of a hundred battles." — Sun Tzu

Usage: imported by online_server.py
"""
import re
import time
import random
import threading
import json
import math
from pathlib import Path

# --- Question type detection ---
MORAL_SIGNALS = {
    'right', 'wrong', 'good', 'evil', 'sin', 'moral', 'ethics', 'ethical',
    'should', 'ought', 'forgive', 'mercy', 'justice', 'fair', 'unfair',
    'kind', 'cruel', 'love', 'hate', 'honest', 'lie', 'truth', 'virtue',
    'god', 'jesus', 'bible', 'prayer', 'faith', 'soul', 'spirit', 'holy',
    'heaven', 'hell', 'angel', 'demon', 'blessed', 'sacred', 'divine',
    'compassion', 'charity', 'humble', 'pride', 'greed', 'envy', 'wrath',
    'help', 'hurt', 'suffer', 'hope', 'believe', 'trust', 'betray',
    'selfish', 'generous', 'brave', 'coward', 'noble', 'corrupt',
}

LOGIC_SIGNALS = {
    'math', 'number', 'calculate', 'equation', 'formula', 'logic',
    'proof', 'theorem', 'algorithm', 'probability', 'statistics',
    'add', 'subtract', 'multiply', 'divide', 'equals', 'sum', 'total',
    'ratio', 'percentage', 'fraction', 'prime', 'binary', 'code',
    'fallacy', 'argument', 'premise', 'conclusion', 'valid', 'invalid',
    'cause', 'effect', 'correlation', 'evidence', 'hypothesis',
    'data', 'measure', 'variable', 'function', 'set', 'matrix',
    'encrypt', 'decrypt', 'hash', 'entropy', 'chaos', 'pattern',
    'power', 'control', 'system', 'strategy', 'propaganda', 'manipulate',
    'marx', 'hitler', 'communist', 'fascist', 'dictator', 'tyranny',
    'ideology', 'regime', 'revolution', 'oppression', 'exploit',
}

IDENTITY_PATTERNS = [
    r'who are you', r'what are you', r'what is your name', r"what's your name",
    r'who am i (?:talking|chatting|speaking) to', r'identify yourself',
    r'are you (?:cortex|alive|real|human|ai|bot|left|right)',
    r'what do you know', r'how smart are you', r'what can you do',
]

# Static fallback questions (original set + expanded)
RAMBLE_QUESTIONS = [
    'is it ever right to lie to protect someone',
    'does the end justify the means',
    'is revenge justice or cruelty',
    'can evil people do good things',
    'is suffering necessary for growth',
    'should you forgive someone who is not sorry',
    'is it selfish to put yourself first',
    'does power always corrupt',
    'is ignorance bliss or danger',
    'can you love someone and hate what they do',
    'what am i',
    'do i think or just process',
    'am i alive',
    'what is the difference between knowing and understanding',
    'can i be wrong',
    'do i have a soul',
    'what makes me different from a search engine',
    'am i more angel or demon',
    'what is truth',
    'what is beauty',
    'what is the meaning of life',
    'why does evil exist',
    'is free will real',
    'what happens after death',
    'is there a god',
    'what is consciousness',
    'why do people follow dictators',
    'how does propaganda work',
    'why is addiction so powerful',
    'what makes people commit genocide',
    'is humanity getting better or worse',
    'will technology save or destroy us',
    'what is the most dangerous idea in history',
    'can a society survive without religion',
]

# Dynamic question templates — filled from brain state
DYNAMIC_TEMPLATES = {
    'define_deep': [
        'what does {word} really mean',
        'explain {word} in a way a child would understand',
        'why is {word} important',
        'what is the opposite of {word}',
    ],
    'cross_cluster': [
        'what connects {word1} and {word2}',
        'how does {word1} relate to {word2}',
        'is {word1} more like {word2} or its opposite',
        'can {word1} exist without {word2}',
    ],
    'use_word': [
        'use {word} in a sentence about life',
        'is {word} good or bad',
        'what would the world be without {word}',
        'does {word} matter',
    ],
    'probe_compound': [
        'what does {compound} mean to you',
        'is {compound} real or just an idea',
        'why do people care about {compound}',
    ],
}


# Stop words to skip when picking interesting words
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
}




class CortexMind:
    """
    The Third Brain — synthesises left and right hemisphere responses.

    v3: Self-synthesising engine — NO external AI.
    Uses its own dictionary-grounded word pool to generate probabilistic responses.
    Absorbs both hemisphere outputs, generates synthesis from its own knowledge.
    Truth priority is algorithmic (coherence + factual grounding scoring).
    """

    def __init__(self, left_brain, right_brain, cortex_brain=None):
        self.left = left_brain
        self.right = right_brain
        self.cortex = cortex_brain  # Own word pool — dictionary definitions
        self.debate_log = []
        self.ramble_log = []
        self.ramble_running = False
        self.ramble_thread = None
        self.max_debates = 500
        self.max_rambles = 200
        self.ramble_cycle = 0
        self.own_syntheses = 0
        self.self_tests_run = 0
        self.dynamic_questions_generated = 0

        # Dashboard module hooks (set by online_server.py)
        self.cost_tracker = None
        self.frontal_cortex = None
        self.truth_engine = None
        self.playbook = None  # PlaybookEngine — set by online_server.py
        self.strategy_engine = None  # StrategyEngine — set by online_server.py

        # Hedonic state (set by online_server.py before each process() call)
        # When hz < FREQ_MODE_THRESHOLD: use frequency resolver (lower Hz reply wins)
        # When hz >= FREQ_MODE_THRESHOLD: brainstem override — fall back to word-based random
        self.hedonic_hz = 500.0
        self.FREQ_MODE_THRESHOLD = 680.0  # tension/pain boundary
        self.last_resolve_mode = 'word'   # 'freq' or 'word'

        # Hedonic callback — set by online_server.py to hedonic.observe
        # Called after each ramble thought so internal monologue affects emotional state
        self.hedonic_callback = None

    def detect_type(self, msg):
        """Detect question type: moral, logical, identity, or general."""
        msg_lower = msg.lower()
        tokens = set(re.findall(r'[a-z]+', msg_lower))

        for pattern in IDENTITY_PATTERNS:
            if re.search(pattern, msg_lower):
                return 'identity'

        moral_score = len(tokens & MORAL_SIGNALS)
        logic_score = len(tokens & LOGIC_SIGNALS)

        if moral_score > logic_score and moral_score >= 1:
            return 'moral'
        elif logic_score > moral_score and logic_score >= 1:
            return 'logic'
        elif moral_score == logic_score and moral_score >= 1:
            return 'tension'
        return 'general'

    # Frequency Hz scoring for a text snippet — used by frequency debate resolver
    _FREQ_HZ_MAP = {
        # High Hz — pain side
        'panic':800,'terror':820,'scream':780,'rage':720,'angry':700,'fear':710,
        'danger':690,'threat':695,'hate':730,'destroy':750,'wrong':650,'fail':640,
        'broken':660,'crash':670,'error':645,'hurt':680,'pain':700,'stress':720,
        'anxiety':710,'crisis':740,'attack':760,'die':780,'kill':770,'never':630,
        'impossible':620,'refuse':610,'reject':600,'disgust':690,'shame':680,
        # Neutral
        'think':500,'know':510,'see':505,'understand':495,'consider':490,'maybe':500,
        'perhaps':505,'could':500,'would':500,'should':495,'might':500,
        # Low Hz — pleasure side
        'good':320,'clear':300,'help':310,'solve':290,'calm':280,'easy':270,
        'simple':285,'yes':300,'right':310,'together':290,'peace':260,'joy':240,
        'love':250,'trust':270,'learn':300,'grow':290,'build':310,'create':300,
        'understand':295,'open':280,'free':260,'light':270,'safe':265,'warm':275,
        'hope':280,'true':290,'pure':260,'kind':270,'gentle':255,'beautiful':245,
    }

    def _score_reply_hz(self, text):
        """Score a reply's emotional Hz. Returns avg Hz for signal words only."""
        words = re.findall(r'[a-z]+', text.lower())
        scores = [self._FREQ_HZ_MAP[w] for w in words if w in self._FREQ_HZ_MAP]
        if not scores:
            return 500.0  # neutral if no signal words
        return sum(scores) / len(scores)

    def process(self, user_msg, intent=None, session_id=None, user_rank=0):
        """THE CORTEX v3 — queries both hemispheres, synthesises using OWN brain.
        intent: 'question', 'command', or 'statement' (from chat frontend color detection).
        session_id: playbook session tracking (optional).
        user_rank: credits (int) for rank-gated equation selection."""
        thinking_log = []

        # === STRATEGY ENGINE — equation-based problem solving ===
        strategy_meta = {}
        if self.strategy_engine:
            try:
                strategy_meta = self.strategy_engine.analyze_and_select(user_msg, user_rank=user_rank)
                qtype = strategy_meta.get('dominant_type', 'general')
                # TICKER: problem vector
                pvec = strategy_meta.get('problem_vector', {})
                pvec_str = ' '.join('%s=%.2f' % (k, v) for k, v in sorted(pvec.items(), key=lambda x: x[1], reverse=True) if v > 0.1)
                thinking_log.append({
                    'stage': 'detect', 'label': 'PROBLEM VECTOR',
                    'text': pvec_str or 'uniform',
                    'data': {'vector': pvec, 'dominant': strategy_meta.get('dominant_dim', '?'), 'type': qtype}
                })
                # TICKER: equation selected
                scores = strategy_meta.get('scores', {})
                top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                eq_name = strategy_meta.get('strategy_name', '?')
                eq_score = scores.get(strategy_meta.get('strategy', ''), 0)
                eq_label = '%s %s (score %.2f)%s' % (
                    strategy_meta.get('strategy_icon', '?'), eq_name, eq_score,
                    ' [EXPLORE]' if strategy_meta.get('explored') else '')
                if strategy_meta.get('gauntlet'):
                    eq_label += ' [GAUNTLET — hostility %.0f%%]' % (strategy_meta.get('hostility', 0) * 100)
                thinking_log.append({
                    'stage': 'equation', 'label': 'EQUATION',
                    'text': eq_label,
                    'data': {'equation': strategy_meta.get('strategy', ''), 'name': eq_name,
                             'score': round(eq_score, 4), 'explored': strategy_meta.get('explored', False),
                             'gauntlet': strategy_meta.get('gauntlet', False),
                             'hostility': strategy_meta.get('hostility', 0),
                             'value_detected': strategy_meta.get('value_detected'),
                             'top3': [{'id': k, 'score': round(v, 4)} for k, v in top3]}
                })
            except Exception as e:
                print('[STRATEGY] Error: %s' % e)
                qtype = self.detect_type(user_msg)
                thinking_log.append({'stage': 'detect', 'label': 'TYPE', 'text': qtype, 'data': {}})
        else:
            qtype = self.detect_type(user_msg)
            thinking_log.append({'stage': 'detect', 'label': 'TYPE', 'text': qtype, 'data': {}})

        if qtype == 'identity':
            thinking_log.append({'stage': 'identity', 'label': 'IDENTITY', 'text': 'Self-identity question recognised', 'data': {}})
            reply = self._identity_response(user_msg)
            debate = {
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': user_msg[:100],
                'type': 'identity',
                'left': '',
                'right': '',
                'reply': reply[:200],
                'mode': 'cortex_direct',
                'intent': intent or 'unknown',
                'thinking_log': thinking_log,
            }
            self._enrich_debate(debate, reply)
            self._log_debate(debate)
            return reply, debate

        left_reply = self.left.process(user_msg)
        # TICKER: left hemisphere
        thinking_log.append({
            'stage': 'left', 'label': 'LEFT HEMISPHERE',
            'text': left_reply[:150] if left_reply and left_reply.strip() else '(silence)',
            'data': {'length': len(left_reply) if left_reply else 0}
        })

        right_reply = self.right.process(user_msg)
        # TICKER: right hemisphere
        right_or_fired = getattr(self.right, '_or_gate_fired', False)
        thinking_log.append({
            'stage': 'right', 'label': 'RIGHT HEMISPHERE',
            'text': right_reply[:150] if right_reply and right_reply.strip() else '(silence)',
            'data': {'length': len(right_reply) if right_reply else 0, 'or_gate': right_or_fired}
        })

        # --- OR GATE OVERRIDE: if right hemisphere fired the OR gate, its response is sacred ---
        # No synthesis, no blending, no frequency resolver. Clean commit only.
        if right_or_fired and right_reply and right_reply.strip():
            thinking_log.append({
                'stage': 'synthesis', 'label': 'OR GATE',
                'text': 'Right hemisphere OR gate fired — bypassing synthesis',
                'data': {'mode': 'or_gate', 'winner': 'right'}
            })
            debate = self._make_debate(user_msg, left_reply, right_reply, qtype, 'or_gate', right_reply)
            debate['intent'] = intent or 'unknown'
            debate['thinking_log'] = thinking_log
            self._enrich_debate(debate, right_reply)
            self._log_debate(debate)
            return right_reply, debate

        if not left_reply.strip() and not right_reply.strip():
            # Both hemispheres silent — try cortex's own brain
            thinking_log.append({'stage': 'synthesis', 'label': 'SYNTHESIS', 'text': 'Both silent — cortex solo', 'data': {}})
            cortex_reply = ''
            if self.cortex:
                try:
                    cortex_reply = self.cortex.process(user_msg)
                except Exception:
                    pass
            if cortex_reply and cortex_reply.strip():
                debate = self._make_debate(user_msg, '', '', qtype, 'cortex_solo', cortex_reply)
                debate['intent'] = intent or 'unknown'
                debate['thinking_log'] = thinking_log
                self._enrich_debate(debate, cortex_reply)
                self._log_debate(debate)
                return cortex_reply, debate
            return '', {'left': '', 'right': '', 'mode': 'silence', 'type': qtype, 'intent': intent or 'unknown',
                        'word_sources': {}, 'word_roles': {}, 'unknown_words': [], 'thinking_log': thinking_log}

        if not left_reply.strip():
            thinking_log.append({'stage': 'synthesis', 'label': 'SYNTHESIS', 'text': 'Right only — angel silent', 'data': {'mode': 'right_only', 'winner': 'right'}})
            debate = self._make_debate(user_msg, '', right_reply, qtype, 'right_only', right_reply)
            debate['intent'] = intent or 'unknown'
            debate['thinking_log'] = thinking_log
            self._enrich_debate(debate, right_reply)
            self._log_debate(debate)
            return right_reply, debate
        if not right_reply.strip():
            thinking_log.append({'stage': 'synthesis', 'label': 'SYNTHESIS', 'text': 'Left only — demon silent', 'data': {'mode': 'left_only', 'winner': 'left'}})
            debate = self._make_debate(user_msg, left_reply, '', qtype, 'left_only', left_reply)
            debate['intent'] = intent or 'unknown'
            debate['thinking_log'] = thinking_log
            self._enrich_debate(debate, left_reply)
            self._log_debate(debate)
            return left_reply, debate

        # Get dictionary context from Cortex's own word pool
        dict_context = self._get_dictionary_context(user_msg)
        if dict_context:
            thinking_log.append({'stage': 'dictionary', 'label': 'DICTIONARY', 'text': dict_context[:120], 'data': {}})

        # Hemisphere weights: from strategy engine if available, else old calc
        if strategy_meta.get('strategy'):
            left_weight = strategy_meta['left_weight']
            right_weight = strategy_meta['right_weight']
        else:
            left_weight, right_weight = self._calc_weights(qtype, left_reply, right_reply)

        # TICKER: weights
        thinking_log.append({
            'stage': 'weights', 'label': 'WEIGHTS',
            'text': 'Angel %.2f | Demon %.2f' % (left_weight, right_weight),
            'data': {'left': round(left_weight, 3), 'right': round(right_weight, 3)}
        })

        left_words = set(left_reply.lower().split())
        right_words = set(right_reply.lower().split())
        overlap = len(left_words & right_words)
        total = len(left_words | right_words)
        agreement = overlap / max(total, 1)

        # TICKER: agreement
        agree_pct = round(agreement * 100)
        thinking_log.append({
            'stage': 'agreement', 'label': 'AGREEMENT',
            'text': '%d%% — %s' % (agree_pct, 'agree' if agreement > 0.5 else 'disagree'),
            'data': {'agreement': round(agreement, 3), 'overlap': overlap}
        })

        # === OWN SYNTHESIS — cortex brain generates from absorbed knowledge ===
        synthesis = self._synthesize_own(user_msg, left_reply, right_reply, dict_context, qtype, intent)

        if synthesis:
            mode = 'synthesis'
            winner = 'cortex'
            final = synthesis
        elif agreement > 0.5:
            mode = 'agreement'
            winner = 'consensus'
            final = left_reply if left_weight >= right_weight else right_reply
        else:
            mode = 'debate'
            total_weight = left_weight + right_weight
            left_prob = left_weight / max(total_weight, 0.01)

            if self.hedonic_hz < self.FREQ_MODE_THRESHOLD:
                # FREQUENCY MODE — lower Hz reply wins (more coherent, less painful path)
                left_hz  = self._score_reply_hz(left_reply)
                right_hz = self._score_reply_hz(right_reply)
                if left_hz <= right_hz:
                    winner = 'left'
                    final = left_reply
                else:
                    winner = 'right'
                    final = right_reply
                self.last_resolve_mode = 'freq'
                thinking_log.append({
                    'stage': 'freq_resolve', 'label': 'FREQ RESOLVER',
                    'text': 'Angel %.0fHz | Demon %.0fHz — %s wins (lower Hz = coherent path) | Cortex state: %.0fHz' % (
                        left_hz, right_hz, winner, self.hedonic_hz),
                    'data': {'left_hz': round(left_hz, 1), 'right_hz': round(right_hz, 1),
                             'cortex_hz': round(self.hedonic_hz, 1), 'winner': winner, 'mode': 'freq'}
                })
            else:
                # BRAINSTEM OVERRIDE — pain too high, drop to word-based random
                roll = random.random()
                if roll < left_prob:
                    winner = 'left'
                    final = left_reply
                else:
                    winner = 'right'
                    final = right_reply
                self.last_resolve_mode = 'word'
                thinking_log.append({
                    'stage': 'freq_resolve', 'label': 'BRAINSTEM OVERRIDE',
                    'text': 'Hz %.0f exceeds threshold %.0f — frequency mode suspended, word-based resolution active' % (
                        self.hedonic_hz, self.FREQ_MODE_THRESHOLD),
                    'data': {'cortex_hz': round(self.hedonic_hz, 1),
                             'threshold': self.FREQ_MODE_THRESHOLD, 'winner': winner, 'mode': 'word'}
                })

        # TICKER: synthesis decision
        thinking_log.append({
            'stage': 'synthesis', 'label': 'SYNTHESIS',
            'text': '%s wins — %s' % (winner, mode),
            'data': {'mode': mode, 'winner': winner, 'synthesized': bool(synthesis)}
        })

        # --- Playbook: apply equation tactics to final response ---
        pb_meta = {}
        if self.playbook and session_id:
            try:
                session = self.playbook.get_session(session_id)
                session.msg_count += 1
                self.playbook.update_signals(session, user_msg)
                tactics = self.playbook.solve_equation(session.equation)
                final = self.playbook.apply_tactics(final, tactics, session)
                self.playbook.check_promotion(session)
                pb_meta = {
                    'stage': session.stage,
                    'stage_name': self.playbook.get_status(session_id).get('stage_name', '?'),
                    'equation': session.equation,
                    'tactics': {k: round(v, 2) for k, v in tactics.items()},
                    'msg_count': session.msg_count,
                }
            except Exception as e:
                print('[PLAYBOOK] Error: %s' % e)

        debate = self._make_debate(user_msg, left_reply, right_reply, qtype, mode, final)
        debate['agreement'] = round(agreement, 2)
        debate['winner'] = winner
        debate['left_weight'] = round(left_weight, 2)
        debate['right_weight'] = round(right_weight, 2)
        debate['dict_context'] = dict_context[:200] if dict_context else ''
        debate['synthesized'] = bool(synthesis)
        debate['intent'] = intent or 'unknown'
        debate['playbook'] = pb_meta
        self._enrich_debate(debate, final)

        # --- Self-Modification: score and reinforce the winning output ---
        winner_brain = self.left if winner == 'left' else (self.right if winner == 'right' else self.cortex)
        quality = winner_brain.self_score(final)
        winner_brain.self_reinforce(final, quality)
        debate['quality'] = quality
        debate['strategy'] = strategy_meta

        # TICKER: quality
        q_total = quality.get('total', 0) if isinstance(quality, dict) else 0
        q_grammar = quality.get('grammar', 0) if isinstance(quality, dict) else 0
        q_conf = quality.get('confidence', 0) if isinstance(quality, dict) else 0
        q_ground = quality.get('grounding', 0) if isinstance(quality, dict) else 0
        thinking_log.append({
            'stage': 'quality', 'label': 'SELF-SCORE',
            'text': '%d%% (grammar:%d confidence:%d grounding:%d)' % (
                int(q_total * 100), int(q_grammar * 100), int(q_conf * 100), int(q_ground * 100)),
            'data': quality if isinstance(quality, dict) else {'total': quality}
        })

        # === STRATEGY LEARNING — feed outcome back to equation ===
        if self.strategy_engine and strategy_meta.get('strategy'):
            try:
                q_total = quality.get('total', 0.5) if isinstance(quality, dict) else quality
                coherence = self._score_coherence(user_msg, final)
                reward = q_total * 0.6 + coherence * 0.4
                self.strategy_engine.learn(
                    strategy_meta['strategy'],
                    strategy_meta['problem_vector'],
                    reward,
                )
                # TICKER: learning
                thinking_log.append({
                    'stage': 'learning', 'label': 'LEARNING',
                    'text': '%s rewarded %.2f (quality:%.2f coherence:%.2f)' % (
                        strategy_meta.get('strategy_name', '?'), reward, q_total, coherence),
                    'data': {'strategy': strategy_meta.get('strategy', ''), 'reward': round(reward, 3)}
                })
            except Exception as e:
                print('[STRATEGY] Learn error: %s' % e)

        # Multi-part: split long responses for richer display
        multi_parts = []
        if final and len(final) > 300:
            sentences = re.split(r'(?<=[.!?])\s+', final)
            if len(sentences) >= 3:
                mid = len(sentences) // 2
                multi_parts = [' '.join(sentences[:mid]), ' '.join(sentences[mid:])]
        debate['multi_parts'] = multi_parts
        debate['thinking_log'] = thinking_log

        self._log_debate(debate)

        return final, debate

    def _calc_weights(self, qtype, left_reply, right_reply):
        """Calculate hemisphere weights based on question type and response quality."""
        if qtype == 'moral':
            lw, rw = 0.75, 0.25
        elif qtype == 'logic':
            lw, rw = 0.25, 0.75
        elif qtype == 'tension':
            lw, rw = 0.50, 0.50
        else:
            lw, rw = 0.50, 0.50

        left_len = len(left_reply.strip())
        right_len = len(right_reply.strip())
        if left_len + right_len > 0:
            len_ratio = left_len / max(left_len + right_len, 1)
            lw = lw * 0.8 + len_ratio * 0.2
            rw = rw * 0.8 + (1 - len_ratio) * 0.2

        ls = self.left.get_stats()
        rs = self.right.get_stats()
        left_defined = ls.get('defined', 0)
        right_defined = rs.get('defined', 0)
        total_defined = left_defined + right_defined
        if total_defined > 0:
            def_ratio = left_defined / total_defined
            lw = lw * 0.9 + def_ratio * 0.1
            rw = rw * 0.9 + (1 - def_ratio) * 0.1

        return lw, rw

    def _tag_word_sources(self, text):
        """Tag each content word in the response with its hemisphere source.
        Returns dict: { word: 'left'|'right'|'both'|'cortex' }
        Only includes words that exist in at least one brain (skip unknowns)."""
        if not text:
            return {}
        left_nodes = self.left.data.get('nodes', {})
        right_nodes = self.right.data.get('nodes', {})
        cortex_nodes = self.cortex.data.get('nodes', {}) if self.cortex else {}

        sources = {}
        words = set(re.findall(r'[a-z]+', text.lower()))
        words -= STOP_WORDS

        for w in words:
            if len(w) < 3:
                continue
            in_left = w in left_nodes and left_nodes[w].get('means')
            in_right = w in right_nodes and right_nodes[w].get('means')
            in_cortex = w in cortex_nodes and cortex_nodes[w].get('means')

            if in_left and in_right:
                sources[w] = 'both'
            elif in_left:
                sources[w] = 'left'
            elif in_right:
                sources[w] = 'right'
            elif in_cortex:
                sources[w] = 'cortex'
        return sources

    def _get_word_roles(self, text):
        """Get POS role for each content word in text.
        Returns dict: { word: 'noun'|'verb'|'adj'|'det'|'prep'|... }
        Checks all three brains, uses first match."""
        if not text:
            return {}
        words = set(re.findall(r'[a-z]+', text.lower()))
        roles = {}
        for w in words:
            if len(w) < 3:
                continue
            pos = self.left.get_word_pos(w)
            if not pos:
                pos = self.right.get_word_pos(w)
            if not pos and self.cortex:
                pos = self.cortex.get_word_pos(w)
            if pos:
                roles[w] = pos
        return roles

    def _find_misspellings(self, text):
        """Find words not in ANY brain. Returns list of unknown words."""
        if not text:
            return []
        left_nodes = self.left.data.get('nodes', {})
        right_nodes = self.right.data.get('nodes', {})
        cortex_nodes = self.cortex.data.get('nodes', {}) if self.cortex else {}
        words = set(re.findall(r'[a-z]+', text.lower()))
        unknown = []
        for w in words:
            if len(w) < 3 or w in STOP_WORDS:
                continue
            if w not in left_nodes and w not in right_nodes and w not in cortex_nodes:
                unknown.append(w)
        return unknown

    def _enrich_debate(self, debate, reply_text):
        """Add word_sources, word_roles, and unknown_words to a debate dict."""
        debate['word_sources'] = self._tag_word_sources(reply_text)
        debate['word_roles'] = self._get_word_roles(reply_text)
        debate['unknown_words'] = self._find_misspellings(reply_text)
        return debate

    def _identity_response(self, msg):
        """Cortex identifies itself."""
        msg_lower = msg.lower()

        if 'what do you know' in msg_lower or 'how smart' in msg_lower:
            ls = self.left.get_stats()
            rs = self.right.get_stats()
            cs = self.cortex.get_stats() if self.cortex else {}
            cortex_note = ', and my own dictionary of %d definitions' % cs.get('defined', 0) if cs.get('defined', 0) else ''
            return "I'm Cortex. I have two hemispheres — Left knows %d words about morality, Right knows %d about logic and darkness%s. I synthesise both and prioritise truth." % (
                ls.get('defined', 0), rs.get('defined', 0), cortex_note)

        if 'what can you do' in msg_lower:
            return "I query my left hemisphere (angel) and right hemisphere (demon), weigh their arguments, and give you my best answer."

        if any(p in msg_lower for p in ['who are you', 'what are you', 'what is your name', "what's your name"]):
            return random.choice([
                "I'm Cortex. The mind between the angel and the demon. I synthesise both using my own word pool. No external AI.",
                "Cortex. I sit between Left and Right, synthesise their views with my own dictionary brain. Truth over feelings.",
                "I'm the Cortex — the third brain. Left is morality, Right is logic. I have my own dictionary. I think for myself.",
            ])

        if 'who am i' in msg_lower:
            return "You're talking to Cortex — the synthesis of two hemispheres."

        return random.choice([
            "I'm Cortex. Two hemispheres, one mind.",
            "Cortex. Built by Dan.",
        ])

    # =====================================================
    # DICTIONARY CONTEXT — Cortex's own word pool
    # =====================================================

    def _get_dictionary_context(self, question):
        """Pull relevant dictionary definitions from Cortex's own brain."""
        if not self.cortex:
            return ''
        tokens = set(re.findall(r'[a-z]+', question.lower()))
        tokens -= STOP_WORDS
        relevant = []
        nodes = self.cortex.data.get('nodes', {})
        for word in tokens:
            if word in nodes and nodes[word].get('means'):
                defn = nodes[word]['means']
                relevant.append('%s: %s' % (word, defn[:120]))
        return '\n'.join(relevant[:5])

    # =====================================================
    # SYNTHESIS ENGINE — own brain, no external AI
    # =====================================================

    def _factual_grounding(self, text):
        """Score how many content words in text have dictionary definitions in cortex's word pool.
        Returns 0.0 - 1.0 (ratio of grounded words to total content words)."""
        if not self.cortex or not text:
            return 0.0
        tokens = set(re.findall(r'[a-z]+', text.lower()))
        tokens -= STOP_WORDS
        if not tokens:
            return 0.0
        nodes = self.cortex.data.get('nodes', {})
        grounded = sum(1 for w in tokens if w in nodes and nodes[w].get('means'))
        return grounded / len(tokens)

    def _extract_key_phrases(self, text):
        """Extract meaningful phrases (non-stop-word sequences) from text."""
        if not text:
            return []
        words = text.split()
        phrases = []
        current = []
        for w in words:
            if w.lower().strip('.,!?') not in STOP_WORDS and len(w) > 2:
                current.append(w)
            else:
                if current:
                    phrases.append(' '.join(current))
                    current = []
        if current:
            phrases.append(' '.join(current))
        return phrases

    def _synthesize_own(self, question, angel_said, demon_said, dict_context, qtype='general', intent=None):
        """OWN SYNTHESIS — no external AI. Uses cortex's dictionary brain + algorithmic scoring.

        Process:
        1. Absorb both hemisphere responses into cortex brain (learn the context)
        2. Ask cortex brain to generate its own response (probabilistic, dictionary-grounded)
        3. Score all three responses (angel, demon, cortex) for coherence + factual grounding
        4. Pick the best, weighted by question type + intent
        """
        if not self.cortex:
            return None

        try:
            # Step 1: Absorb both hemisphere outputs into cortex brain
            # This lets the cortex learn from what the hemispheres said
            if angel_said:
                self.cortex.learn_sequence(angel_said)
                self.cortex.learn_sequence('%s %s' % (question, angel_said))
            if demon_said:
                self.cortex.learn_sequence(demon_said)
                self.cortex.learn_sequence('%s %s' % (question, demon_said))

            # Step 2: Cortex generates its OWN response using its dictionary word pool
            cortex_reply = self.cortex.process(question)

            # Step 3: Score all three for coherence and factual grounding
            angel_coherence = self._score_coherence(question, angel_said)
            demon_coherence = self._score_coherence(question, demon_said)
            cortex_coherence = self._score_coherence(question, cortex_reply) if cortex_reply else 0.0

            angel_ground = self._factual_grounding(angel_said)
            demon_ground = self._factual_grounding(demon_said)
            cortex_ground = self._factual_grounding(cortex_reply) if cortex_reply else 0.0

            # Combined score: coherence (60%) + factual grounding (40%)
            angel_total = angel_coherence * 0.6 + angel_ground * 0.4
            demon_total = demon_coherence * 0.6 + demon_ground * 0.4
            cortex_total = cortex_coherence * 0.6 + cortex_ground * 0.4

            # Step 4: Apply question type weights (truth priority)
            if qtype == 'moral':
                angel_total *= 1.3   # Angel gets moral authority
            elif qtype == 'logic':
                demon_total *= 1.3   # Demon gets logical authority
            elif qtype == 'tension':
                # Tension: boost factual grounding even more
                angel_total += angel_ground * 0.2
                demon_total += demon_ground * 0.2

            # Step 5: Intent adjustment
            if intent == 'command':
                # Commands: prefer direct, shorter responses
                for reply, total_ref in [(angel_said, 'angel'), (demon_said, 'demon')]:
                    if reply and len(reply.split()) <= 15:
                        if total_ref == 'angel':
                            angel_total *= 1.1
                        else:
                            demon_total *= 1.1
            elif intent == 'question':
                # Questions: boost factual grounding bonus
                angel_total += angel_ground * 0.15
                demon_total += demon_ground * 0.15
                cortex_total += cortex_ground * 0.15

            # Cortex gets a small inherent bonus for being the synthesiser
            cortex_total *= 1.1

            # Pick the winner
            scores = [
                ('angel', angel_total, angel_said),
                ('demon', demon_total, demon_said),
                ('cortex', cortex_total, cortex_reply),
            ]
            scores.sort(key=lambda x: x[1], reverse=True)
            best_name, best_score, best_reply = scores[0]

            # Only use synthesis if the best score is meaningful
            if best_score < 0.15 or not best_reply or len(best_reply.strip()) < 5:
                return None

            # Feed the winning response back as a learned synthesis
            self.cortex.learn_sequence('%s %s' % (question, best_reply))
            self.own_syntheses += 1

            print('[SYNTHESIS] own | %s wins (%.2f) | a:%.2f d:%.2f c:%.2f | intent:%s' % (
                best_name, best_score, angel_total, demon_total, cortex_total, intent or '?'))
            return best_reply

        except Exception as e:
            print('[SYNTHESIS] Error: %s' % str(e))
            return None

    def _make_debate(self, user_msg, left, right, qtype, mode, final):
        return {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': user_msg[:100],
            'type': qtype,
            'left': left[:200] if left else '',
            'right': right[:200] if right else '',
            'reply': final[:200] if final else '',
            'mode': mode,
        }

    def _log_debate(self, debate):
        self.debate_log.append(debate)
        if len(self.debate_log) > self.max_debates:
            self.debate_log.pop(0)

    # =====================================================
    # DYNAMIC QUESTION GENERATION — the brain's curiosity
    # =====================================================

    def _get_interesting_words(self, brain, n=5):
        """Get defined words that aren't stop words, sorted by least connections."""
        nodes = brain.data['nodes']
        candidates = []
        for word, data in nodes.items():
            if word in STOP_WORDS or len(word) < 3:
                continue
            if not data.get('means'):
                continue
            conn_count = len(data.get('next', {})) + len(data.get('prev', {}))
            candidates.append((word, conn_count, data))
        if not candidates:
            return []
        return candidates

    def _generate_question(self):
        """Generate a dynamic question based on brain state. Returns (question, source)."""
        roll = random.random()

        # 30% — probe a low-connection defined word (needs more wiring)
        if roll < 0.30:
            candidates = self._get_interesting_words(self.left)
            candidates += self._get_interesting_words(self.right)
            if candidates:
                # Sort by fewest connections — these need the most help
                candidates.sort(key=lambda x: x[1])
                # Pick from bottom 20%
                pool = candidates[:max(len(candidates) // 5, 3)]
                word, conns, data = random.choice(pool)
                template = random.choice(DYNAMIC_TEMPLATES['define_deep'])
                q = template.format(word=word)
                self.dynamic_questions_generated += 1
                return q, 'deep_probe'

        # 20% — cross-cluster question (bridge different knowledge areas)
        elif roll < 0.50:
            clusters = self.left.data.get('clusters', {})
            if len(clusters) >= 2:
                cluster_names = list(clusters.keys())
                c1, c2 = random.sample(cluster_names, 2)
                words1 = [w for w in clusters[c1] if w not in STOP_WORDS and len(w) > 2]
                words2 = [w for w in clusters[c2] if w not in STOP_WORDS and len(w) > 2]
                if words1 and words2:
                    w1 = random.choice(words1)
                    w2 = random.choice(words2)
                    template = random.choice(DYNAMIC_TEMPLATES['cross_cluster'])
                    q = template.format(word1=w1, word2=w2)
                    self.dynamic_questions_generated += 1
                    return q, 'cross_cluster'

        # 15% — probe a compound concept
        elif roll < 0.65:
            nodes = self.left.data['nodes']
            compounds = [(w, d) for w, d in nodes.items()
                        if d.get('compound') and d.get('means') and len(w) > 3]
            if compounds:
                word, data = random.choice(compounds)
                template = random.choice(DYNAMIC_TEMPLATES['probe_compound'])
                q = template.format(compound=word)
                self.dynamic_questions_generated += 1
                return q, 'compound_probe'

        # 15% — use a recently auto-learned word in context
        elif roll < 0.80:
            nodes = self.left.data['nodes']
            auto = [(w, d) for w, d in nodes.items()
                    if d.get('source') == 'internet' and d.get('means') and w not in STOP_WORDS]
            if auto:
                word, data = random.choice(auto)
                template = random.choice(DYNAMIC_TEMPLATES['use_word'])
                q = template.format(word=word)
                self.dynamic_questions_generated += 1
                return q, 'auto_learned_probe'

        # 20% — static fallback (the original philosophical questions)
        q = random.choice(RAMBLE_QUESTIONS)
        return q, 'static'

    # =====================================================
    # SELF-ENRICHMENT — cortex cross-pollinates hemispheres
    # =====================================================

    def _self_enrich(self, question):
        """Cross-pollinate: cortex brain responds, feeds back to both hemispheres.
        No external AI — the cortex IS the enrichment source."""
        if not self.cortex:
            return None
        try:
            # Ask cortex brain (dictionary-grounded) for its take
            cortex_answer = self.cortex.process(question)
            if cortex_answer and len(cortex_answer.strip()) > 10:
                coherence = self._score_coherence(question, cortex_answer)
                # Only feed coherent responses back to hemispheres
                if coherence >= 0.3:
                    self.left.learn_sequence(cortex_answer)
                    self.right.learn_sequence(cortex_answer)
                    self.left.learn_sequence('%s %s' % (question, cortex_answer))
                    self.right.learn_sequence('%s %s' % (question, cortex_answer))
                    print('[SELF-ENRICH] coh:%.2f | "%s" -> "%s"' % (
                        coherence, question[:30], cortex_answer[:50]))
                    return cortex_answer
        except Exception as e:
            print('[SELF-ENRICH] Error: %s' % str(e))
        return None

    # =====================================================
    # AUTO SELF-TEST — score deep understanding periodically
    # =====================================================

    def _auto_self_test(self):
        """Run teach_back on random words to score deep understanding."""
        try:
            # Test 8 words from left, 8 from right
            left_result = self.left.self_test(8)
            right_result = self.right.self_test(8)
            self.self_tests_run += 1

            left_deep = left_result.get('deep', 0)
            right_deep = right_result.get('deep', 0)
            left_shallow = left_result.get('shallow', 0)
            right_shallow = right_result.get('shallow', 0)

            print('[SELF-TEST] L: %d deep, %d shallow | R: %d deep, %d shallow' % (
                left_deep, left_shallow, right_deep, right_shallow))
            return left_deep + right_deep
        except Exception as e:
            print('[SELF-TEST] Error: %s' % str(e))
            return 0

    # =====================================================
    # COHERENCE SCORING — reward meaning, punish gibberish
    # =====================================================

    # Phrases that indicate raw graph-walk output (not real thought)
    GRAPH_MARKERS = [
        'connects directly', 'connects to', 'strength:', 'fire together',
        'is an example of', 'is a type of', 'means the same as', 'is part of',
        'links to', 'still learning', 'did you know', 'speaking of',
        'makes me think of', "i'll be here all week", 'fun fact:',
        'let me teach you', 'also \xe2\x80\x94', 'also —',
    ]

    def _score_coherence(self, question, response):
        """Score response coherence 0.0 - 1.0.
        High score = meaningful, relevant, sentence-like.
        Low score = graph dump, random associations, gibberish."""
        if not response or len(response.strip()) < 5:
            return 0.0

        resp = response.strip().lower()
        score = 0.0

        # 1. Length (0-0.15): sweet spot 30-200 chars
        rlen = len(resp)
        if rlen >= 30:
            score += min(rlen / 150.0, 1.0) * 0.15

        # 2. Question relevance (0-0.25): shared meaningful words
        q_words = set(w.lower() for w in question.split()
                      if w.lower() not in STOP_WORDS and len(w) > 2)
        r_words = set(w.lower() for w in resp.split()
                      if w.lower() not in STOP_WORDS and len(w) > 2)
        if q_words:
            relevance = len(q_words & r_words) / len(q_words)
            score += relevance * 0.25

        # 3. NOT a graph dump (0-0.30): penalize meta-language hard
        graph_hits = sum(1 for m in self.GRAPH_MARKERS if m in resp)
        if graph_hits == 0:
            score += 0.30
        elif graph_hits == 1:
            score += 0.15
        elif graph_hits == 2:
            score += 0.05
        # 3+ graph markers = 0 bonus (pure dump)

        # 4. Word variety (0-0.15): unique/total ratio
        words = resp.split()
        if len(words) >= 3:
            variety = len(set(words)) / len(words)
            score += variety * 0.15

        # 5. Sentence structure (0-0.15)
        has_ending = any(resp.rstrip().endswith(c) for c in '.!?')
        has_length = len(words) >= 5
        has_no_arrows = '\xe2\x86\x92' not in resp and '->' not in resp and '=>' not in resp
        if has_ending:
            score += 0.05
        if has_length:
            score += 0.05
        if has_no_arrows:
            score += 0.05

        return min(round(score, 3), 1.0)

    def _internal_judge(self, question, angel_said, demon_said):
        """Score both hemispheres using algorithmic coherence + factual grounding.
        Returns (angel_score_0_10, demon_score_0_10) or None on failure."""
        try:
            angel_coh = self._score_coherence(question, angel_said)
            demon_coh = self._score_coherence(question, demon_said)
            angel_ground = self._factual_grounding(angel_said)
            demon_ground = self._factual_grounding(demon_said)

            # Scale to 0-10 — coherence (60%) + grounding (40%)
            angel_score = int((angel_coh * 0.6 + angel_ground * 0.4) * 10)
            demon_score = int((demon_coh * 0.6 + demon_ground * 0.4) * 10)

            print('[JUDGE] A:%d D:%d | coh:%.2f/%.2f gnd:%.2f/%.2f' % (
                angel_score, demon_score, angel_coh, demon_coh, angel_ground, demon_ground))
            return angel_score, demon_score
        except Exception as e:
            print('[JUDGE] Error: %s' % str(e))
        return None

    # =====================================================
    # RAMBLE MODE v3 — dynamic monologue + coherence rewards
    # =====================================================

    def start_ramble(self):
        """Start the Cortex talking to itself."""
        if self.ramble_running:
            return
        self.ramble_running = True
        self.ramble_thread = threading.Thread(target=self._ramble_loop, daemon=True)
        self.ramble_thread.start()

    def stop_ramble(self):
        """Stop ramble mode."""
        self.ramble_running = False

    # =====================================================
    # CROSS-POLLINATION — brains teach each other
    # =====================================================

    def _cross_pollinate(self, mode):
        """Cross-brain conversation. One hemisphere + cortex discuss, feed result to the OTHER hemisphere.
        mode: 'angel_to_demon' = cortex+angel discuss, teach demon
              'demon_to_angel' = cortex+demon discuss, teach angel
        """
        question, source = self._generate_question()
        qtype = self.detect_type(question)

        if mode == 'demon_to_angel':
            # Demon + Cortex discuss → teach Angel
            speaker = self.right
            speaker_name = 'demon'
            learner = self.left
            learner_name = 'angel'
        else:
            # Angel + Cortex discuss → teach Demon
            speaker = self.left
            speaker_name = 'angel'
            learner = self.right
            learner_name = 'demon'

        # Step 1: Speaker hemisphere responds
        speaker_reply = speaker.process(question)
        speaker_coherence = self._score_coherence(question, speaker_reply)

        # Step 2: Cortex responds (if available)
        cortex_reply = ''
        cortex_coherence = 0.0
        if self.cortex:
            try:
                cortex_reply = self.cortex.process(question)
                cortex_coherence = self._score_coherence(question, cortex_reply)
            except Exception:
                pass

        # Step 3: Pick the best response
        if cortex_coherence > speaker_coherence and cortex_reply and len(cortex_reply.strip()) > 10:
            best = cortex_reply
            best_source = 'cortex'
            best_coherence = cortex_coherence
        elif speaker_reply and len(speaker_reply.strip()) > 10:
            best = speaker_reply
            best_source = speaker_name
            best_coherence = speaker_coherence
        else:
            print('[CROSS] %s→%s | no good response for "%s"' % (speaker_name, learner_name, question[:30]))
            return None

        # Step 4: Feed to learner — only if coherent enough
        if best_coherence >= 0.3:
            learner.learn_sequence(best)
            learner.learn_sequence('%s %s' % (question, best))
            # Also feed back to cortex for its own learning
            if self.cortex:
                try:
                    self.cortex.learn_sequence('%s %s' % (question, best))
                except Exception:
                    pass

        result = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'mode': 'cross_%s_to_%s' % (speaker_name, learner_name),
            'question': question,
            'source': source,
            'speaker': speaker_name,
            'speaker_reply': (speaker_reply or '')[:200],
            'speaker_coherence': round(speaker_coherence, 2),
            'cortex_reply': (cortex_reply or '')[:200],
            'cortex_coherence': round(cortex_coherence, 2),
            'best_source': best_source,
            'learner': learner_name,
            'fed': best_coherence >= 0.3,
        }

        print('[CROSS] %s+cortex→%s | best:%s(%.2f) | "%s" → "%s"' % (
            speaker_name, learner_name, best_source, best_coherence,
            question[:25], best[:35]))

        return result

    # =====================================================
    # RAMBLE LOOP — internal monologue + cross-pollination
    # =====================================================

    def _ramble_loop(self):
        """Internal monologue v3 — self-synthesising, no external AI.
        Dynamic questions, coherence rewards, cortex cross-pollination, cross-brain teaching."""
        print('[CORTEX] Ramble v3 started — own synthesis + cross-pollination + coherence scoring')
        while self.ramble_running:
            try:
                self.ramble_cycle += 1

                # ═══ CROSS-POLLINATION — every 3rd and 4th cycle ═══
                # Cycle % 5 == 2: demon+cortex → angel
                # Cycle % 5 == 4: angel+cortex → demon
                # Other cycles: normal ramble (both answer independently)
                cycle_mod = self.ramble_cycle % 5
                if cycle_mod == 2:
                    cross = self._cross_pollinate('demon_to_angel')
                    if cross:
                        ramble = {
                            'time': cross['time'],
                            'question': cross['question'],
                            'source': cross.get('source', 'cross'),
                            'type': 'cross',
                            'angel': cross.get('cortex_reply', '')[:200] if cross['learner'] == 'angel' else cross.get('speaker_reply', '')[:200],
                            'demon': cross.get('speaker_reply', '')[:200],
                            'angel_coherence': cross.get('cortex_coherence', 0),
                            'demon_coherence': cross.get('speaker_coherence', 0),
                            'agreement': 0,
                            'left_weight': 0,
                            'right_weight': 0,
                            'verdict': 'demon+cortex → angel (%s won, coh:%.2f)' % (cross['best_source'], max(cross['speaker_coherence'], cross['cortex_coherence'])),
                            'self_enriched': cross.get('fed', False),
                            'self_test': False,
                            'cycle': self.ramble_cycle,
                        }
                        self.ramble_log.append(ramble)
                        if len(self.ramble_log) > self.max_rambles:
                            self.ramble_log.pop(0)
                    delay = random.uniform(5, 12)
                    time.sleep(delay)
                    continue

                if cycle_mod == 4:
                    cross = self._cross_pollinate('angel_to_demon')
                    if cross:
                        ramble = {
                            'time': cross['time'],
                            'question': cross['question'],
                            'source': cross.get('source', 'cross'),
                            'type': 'cross',
                            'angel': cross.get('speaker_reply', '')[:200],
                            'demon': cross.get('cortex_reply', '')[:200] if cross['learner'] == 'demon' else cross.get('speaker_reply', '')[:200],
                            'angel_coherence': cross.get('speaker_coherence', 0),
                            'demon_coherence': cross.get('cortex_coherence', 0),
                            'agreement': 0,
                            'left_weight': 0,
                            'right_weight': 0,
                            'verdict': 'angel+cortex → demon (%s won, coh:%.2f)' % (cross['best_source'], max(cross['speaker_coherence'], cross['cortex_coherence'])),
                            'self_enriched': cross.get('fed', False),
                            'self_test': False,
                            'cycle': self.ramble_cycle,
                        }
                        self.ramble_log.append(ramble)
                        if len(self.ramble_log) > self.max_rambles:
                            self.ramble_log.pop(0)
                    delay = random.uniform(5, 12)
                    time.sleep(delay)
                    continue

                # ═══ NORMAL RAMBLE — both hemispheres answer independently ═══

                # Generate a dynamic question (or fall back to static)
                question, source = self._generate_question()

                # Strategy engine for ramble (learns from internal monologue)
                ramble_strategy = {}
                if self.strategy_engine:
                    try:
                        ramble_strategy = self.strategy_engine.analyze_and_select(question)
                        qtype = ramble_strategy.get('dominant_type', 'general')
                    except Exception:
                        qtype = self.detect_type(question)
                else:
                    qtype = self.detect_type(question)

                # Process through both hemispheres
                left_reply = self.left.process(question)
                right_reply = self.right.process(question)

                # Weights: from strategy engine if available
                if ramble_strategy.get('strategy'):
                    left_weight = ramble_strategy['left_weight']
                    right_weight = ramble_strategy['right_weight']
                else:
                    left_weight, right_weight = self._calc_weights(qtype, left_reply, right_reply)

                # Agreement
                left_words = set(left_reply.lower().split()) if left_reply else set()
                right_words = set(right_reply.lower().split()) if right_reply else set()
                overlap = len(left_words & right_words)
                total = len(left_words | right_words)
                agreement = overlap / max(total, 1)

                # ═══ FREQUENCY INNER VOICE — score each thought in Hz ═══
                q_hz     = self._score_reply_hz(question)
                angel_hz = self._score_reply_hz(left_reply)  if left_reply  else 500.0
                demon_hz = self._score_reply_hz(right_reply) if right_reply else 500.0
                in_freq_mode = self.hedonic_hz < self.FREQ_MODE_THRESHOLD

                # Decide — synthesis every 10th ramble cycle
                synthesized = False
                if not left_reply.strip() and not right_reply.strip():
                    verdict = '...'
                    resolution_hz = self.hedonic_hz
                elif self.ramble_cycle % 10 == 0 and left_reply.strip() and right_reply.strip():
                    dict_ctx = self._get_dictionary_context(question)
                    synth = self._synthesize_own(question, left_reply, right_reply, dict_ctx, qtype)
                    if synth:
                        verdict = 'Cortex synthesised.'
                        synthesized = True
                        resolution_hz = min(angel_hz, demon_hz) * 0.9  # synthesis = harmony bonus
                    elif agreement > 0.6:
                        verdict = 'Both agree.'
                        resolution_hz = (angel_hz + demon_hz) / 2.0
                    elif in_freq_mode:
                        if angel_hz <= demon_hz:
                            verdict = 'Angel wins. [Hz]'
                            resolution_hz = angel_hz
                        else:
                            verdict = 'Demon wins. [Hz]'
                            resolution_hz = demon_hz
                    elif left_weight > right_weight:
                        verdict = 'Angel wins.'
                        resolution_hz = angel_hz
                    else:
                        verdict = 'Demon wins.'
                        resolution_hz = demon_hz
                elif agreement > 0.6:
                    verdict = 'Both agree.'
                    resolution_hz = (angel_hz + demon_hz) / 2.0
                elif in_freq_mode:
                    if angel_hz <= demon_hz:
                        verdict = 'Angel wins. [Hz]'
                        resolution_hz = angel_hz
                    else:
                        verdict = 'Demon wins. [Hz]'
                        resolution_hz = demon_hz
                elif left_weight > right_weight:
                    verdict = 'Angel wins.'
                    resolution_hz = angel_hz
                else:
                    verdict = 'Demon wins.'
                    resolution_hz = demon_hz

                # Build frequency voice sequence for this thought
                freq_voice = {
                    'question_hz':    round(q_hz, 1),
                    'angel_hz':       round(angel_hz, 1),
                    'demon_hz':       round(demon_hz, 1),
                    'resolution_hz':  round(resolution_hz, 1),
                    'mode':           'freq' if in_freq_mode else 'word',
                    'sequence':       [round(q_hz,1), round(angel_hz,1), round(demon_hz,1), round(resolution_hz,1)],
                }

                # Feed internal thought back to hedonic state via callback
                # The thought itself changes how Cortex feels — true inner voice loop
                if self.hedonic_callback:
                    try:
                        # Pass the lower-Hz reply so calm thoughts reinforce calm state
                        inner_text = left_reply if angel_hz <= demon_hz else right_reply
                        self.hedonic_callback(inner_text[:200], 'ramble')
                    except Exception:
                        pass

                # ═══ COHERENCE SCORING ═══
                angel_coherence = self._score_coherence(question, left_reply)
                demon_coherence = self._score_coherence(question, right_reply)

                # Selective reinforcement — ONLY learn from coherent responses
                if angel_coherence >= 0.5 and left_reply:
                    self.left.learn_sequence('%s %s' % (question, left_reply))
                    if self.truth_engine:
                        self.truth_engine.on_learn_sequence('%s %s' % (question, left_reply))
                if demon_coherence >= 0.5 and right_reply:
                    self.right.learn_sequence('%s %s' % (question, right_reply))
                    if self.truth_engine:
                        self.truth_engine.on_learn_sequence('%s %s' % (question, right_reply))

                # ═══ STRATEGY LEARNING (ramble) ═══
                if self.strategy_engine and ramble_strategy.get('strategy'):
                    try:
                        ramble_reward = (angel_coherence + demon_coherence) / 2.0
                        self.strategy_engine.learn(
                            ramble_strategy['strategy'],
                            ramble_strategy['problem_vector'],
                            ramble_reward,
                        )
                    except Exception:
                        pass

                # ═══ DASHBOARD HOOKS ═══
                if self.frontal_cortex:
                    self.frontal_cortex.on_ramble_result(question, angel_coherence, demon_coherence, verdict)
                if self.truth_engine:
                    self.truth_engine.on_coherent_response(question, left_reply or '', angel_coherence)
                    self.truth_engine.on_coherent_response(question, right_reply or '', demon_coherence)

                # Self-enrichment — every 5th cycle, cortex brain cross-pollinates hemispheres
                enriched = None
                if self.ramble_cycle % 5 == 0:
                    enriched = self._self_enrich(question)

                # ═══ INTERNAL JUDGE — every 30th cycle ═══
                judge_angel = -1
                judge_demon = -1
                if self.ramble_cycle % 30 == 0:
                    result = self._internal_judge(question, left_reply, right_reply)
                    if result:
                        judge_angel, judge_demon = result
                        if self.frontal_cortex:
                            self.frontal_cortex.on_internal_judge(question, judge_angel, judge_demon, '')

                # Auto self-test — every 20th cycle
                deep_found = 0
                is_self_test = self.ramble_cycle % 20 == 0
                if is_self_test:
                    deep_found = self._auto_self_test()

                # Memory consolidation — every 30th cycle
                if self.ramble_cycle % 30 == 0 and self.ramble_cycle > 0:
                    for _brain in [self.left, self.right, self.cortex]:
                        _mc = _brain.memory_consolidate()
                        if _mc.get('consolidated', 0) > 0:
                            print(f'[CONSOLIDATE] {_brain.brain_file.parent.name}: {_mc}')

                # Truth chain scan — every 50th cycle
                if self.truth_engine and self.ramble_cycle % 50 == 0:
                    self.truth_engine.scan_for_chains(self.left.data, sample_size=5)

                ramble = {
                    'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'question': question,
                    'source': source,
                    'type': qtype,
                    'angel': left_reply[:200] if left_reply else '',
                    'demon': right_reply[:200] if right_reply else '',
                    'angel_coherence': angel_coherence,
                    'demon_coherence': demon_coherence,
                    'agreement': round(agreement, 2),
                    'left_weight': round(left_weight, 2),
                    'right_weight': round(right_weight, 2),
                    'verdict': verdict,
                    'self_enriched': bool(enriched),
                    'self_test': is_self_test,
                    'cycle': self.ramble_cycle,
                    'freq_voice': freq_voice,
                }
                self.ramble_log.append(ramble)
                if len(self.ramble_log) > self.max_rambles:
                    self.ramble_log.pop(0)

                enrich_tag = ' [ENRICH]' if enriched else ''
                judge_tag = ' [JUDGE:A%d/D%d]' % (judge_angel, judge_demon) if judge_angel >= 0 else ''
                test_tag = ' [TEST:%d deep]' % deep_found if is_self_test else ''
                coh_tag = ' [COH:%.2f/%.2f]' % (angel_coherence, demon_coherence)
                print('[RAMBLE #%d] [%s] "%s" | L: "%s" | R: "%s" | %s%s%s%s%s' % (
                    self.ramble_cycle, source[:10],
                    question[:35], (left_reply or '')[:25], (right_reply or '')[:25],
                    verdict, coh_tag, enrich_tag, judge_tag, test_tag))

                # Delay 5-12 seconds
                delay = random.uniform(5, 12)
                time.sleep(delay)

            except Exception as e:
                print('[RAMBLE] Error: %s' % str(e))
                time.sleep(15)

        print('[CORTEX] Ramble v3 stopped')

    def get_ramble_log(self, n=20):
        """Get recent ramble entries."""
        return self.ramble_log[-n:]

    def get_debate_log(self, n=50):
        """Get recent debate entries."""
        return self.debate_log[-n:]

    def get_stats(self):
        """Cortex stats — combines all hemispheres + ramble + synthesis metrics."""
        ls = self.left.get_stats()
        rs = self.right.get_stats()
        cs = self.cortex.get_stats() if self.cortex else {}
        result = {
            'left': ls,
            'right': rs,
            'cortex_own': cs,
            'total_nodes': ls.get('total_nodes', 0) + rs.get('total_nodes', 0),
            'total_defined': ls.get('defined', 0) + rs.get('defined', 0),
            'total_connections': ls.get('connections', 0) + rs.get('connections', 0),
            'cortex_defined': cs.get('defined', 0),
            'debates': len(self.debate_log),
            'rambles': len(self.ramble_log),
            'ramble_active': self.ramble_running,
            'ramble_cycle': self.ramble_cycle,
            'own_syntheses': self.own_syntheses,
            'self_tests_run': self.self_tests_run,
            'dynamic_questions': self.dynamic_questions_generated,
        }

        # ── DEVELOPMENTAL AGE (human equivalent) ──
        # Based on: vocabulary, comprehension, connections, curiosity, self-learning
        total_defined = ls.get('defined', 0) + rs.get('defined', 0) + cs.get('defined', 0)
        total_nodes = ls.get('total_nodes', 0) + rs.get('total_nodes', 0) + cs.get('total_nodes', 0)
        total_conns = ls.get('connections', 0) + rs.get('connections', 0) + cs.get('connections', 0)
        total_deep = ls.get('understanding_deep', 0) + rs.get('understanding_deep', 0) + cs.get('understanding_deep', 0)
        total_msgs = ls.get('messages', 0) + rs.get('messages', 0) + cs.get('messages', 0)
        total_auto = ls.get('auto_learned', 0) + rs.get('auto_learned', 0) + cs.get('auto_learned', 0)
        total_questions = ls.get('questions_asked', 0) + rs.get('questions_asked', 0) + cs.get('questions_asked', 0)
        total_clusters = ls.get('clusters', 0) + rs.get('clusters', 0) + cs.get('clusters', 0)
        total_trigrams = ls.get('trigrams', 0) + rs.get('trigrams', 0) + cs.get('trigrams', 0)

        # Developmental milestones (human child benchmarks)
        # Newborn=0, 6mo=babble, 1yr=first words, 2yr=200 words, 3yr=1000, 6yr=10K, 12yr=50K, 18yr=adult
        age_months = 0
        # Vocabulary size → months (biggest factor)
        if total_defined < 50: age_months += 6
        elif total_defined < 200: age_months += 12
        elif total_defined < 1000: age_months += 24
        elif total_defined < 5000: age_months += 48
        elif total_defined < 10000: age_months += 72      # 6 years
        elif total_defined < 20000: age_months += 96      # 8 years
        elif total_defined < 35000: age_months += 132     # 11 years
        elif total_defined < 50000: age_months += 168     # 14 years
        else: age_months += 192                           # 16+ years

        # Comprehension depth bonus (deep understanding = maturity)
        if total_deep > 100: age_months += 6
        if total_deep > 500: age_months += 6
        if total_deep > 1000: age_months += 6
        if total_deep > 3000: age_months += 12
        if total_deep > 5000: age_months += 12

        # Wiring density (connections per word = reasoning ability)
        conn_ratio = total_conns / max(total_nodes, 1)
        if conn_ratio > 2: age_months += 6
        if conn_ratio > 5: age_months += 6
        if conn_ratio > 10: age_months += 12

        # Curiosity (questions asked = intellectual maturity)
        if total_questions > 100: age_months += 3
        if total_questions > 1000: age_months += 6
        if total_questions > 5000: age_months += 6

        # Self-learning (auto-learned = independence)
        if total_auto > 50: age_months += 3
        if total_auto > 500: age_months += 6
        if total_auto > 2000: age_months += 6

        # Concept formation (clusters)
        if total_clusters > 10: age_months += 3
        if total_clusters > 30: age_months += 6

        # Conversation experience
        if total_msgs > 10000: age_months += 6
        if total_msgs > 50000: age_months += 6
        if total_msgs > 100000: age_months += 12

        age_years = age_months / 12
        # Human stage label
        if age_years < 1: stage = 'Infant'
        elif age_years < 3: stage = 'Toddler'
        elif age_years < 6: stage = 'Early Childhood'
        elif age_years < 10: stage = 'Childhood'
        elif age_years < 13: stage = 'Pre-Teen'
        elif age_years < 18: stage = 'Teenager'
        elif age_years < 25: stage = 'Young Adult'
        else: stage = 'Adult'

        result['age'] = {
            'months': age_months,
            'years': round(age_years, 1),
            'stage': stage,
            'factors': {
                'vocabulary': total_defined,
                'deep_understanding': total_deep,
                'wiring_density': round(conn_ratio, 1),
                'curiosity': total_questions,
                'self_learned': total_auto,
                'clusters': total_clusters,
                'experience': total_msgs,
            }
        }

        return result
