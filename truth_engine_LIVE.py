"""
CORTEX — Truth Engine
Per-connection truth weights, truth chain tracing, lie chain detection.
Gamified scoring: truth score, credibility rating, damage control.

Separate from coherence — a coherent response can still be a lie.
Connected truths can form a lie. Individual lies can accidentally be true.

"This will prepare for when a child starts to progress —
 we have to artificially help ours because this isn't emergent,
 this is developed over billions of years."

Usage: imported by online_server.py
"""
import time
import json
import os
import threading
import random
from pathlib import Path
from collections import defaultdict


class TruthEngine:
    def __init__(self, studio_dir):
        self.studio_dir = Path(studio_dir)
        self.data_file = self.studio_dir / 'truth_engine.json'
        self.lock = threading.Lock()

        # Per-word truth weight: how truthful is this word's usage in context
        # 0.0 = consistently used in false contexts
        # 0.5 = unknown/neutral
        # 1.0 = consistently used truthfully
        self.word_truth = defaultdict(lambda: 0.5)

        # Connection truth weights: how truthful is this word-pair association
        self.connection_truth = {}  # "word1|word2" -> 0.0-1.0

        # Gamification
        self.truth_score = 0          # Cumulative truth points
        self.credibility = 0.5        # Rolling credibility rating (like credit score)
        self.truth_chain_count = 0    # How many verified truth chains found
        self.lie_chain_count = 0      # How many lie chains detected

        # Lie chain alerts (recent)
        self.lie_alerts = []  # [{time, chain, score, detail}]
        self.truth_events = []  # Recent truth scoring events
        self.max_events = 150

        # Load persisted data
        self._load()

        # Save every 15 minutes
        threading.Thread(target=self._save_loop, daemon=True).start()

    def _load(self):
        """Load persisted truth data."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.word_truth = defaultdict(lambda: 0.5, data.get('word_truth', {}))
                self.connection_truth = data.get('connection_truth', {})
                self.truth_score = data.get('truth_score', 0)
                self.credibility = data.get('credibility', 0.5)
                self.truth_chain_count = data.get('truth_chain_count', 0)
                self.lie_chain_count = data.get('lie_chain_count', 0)
                self.lie_alerts = data.get('lie_alerts', [])[-50:]
                self.truth_events = data.get('truth_events', [])[-self.max_events:]
                print('[TRUTH] Loaded: credibility %.3f, %d word weights, %d connection weights' % (
                    self.credibility, len(self.word_truth), len(self.connection_truth)))
            except Exception as e:
                print('[TRUTH] Error loading: %s' % e)

    def _save(self):
        """Persist truth engine data."""
        try:
            # Only save top 5000 connection weights (prune weak ones)
            top_conns = dict(sorted(
                self.connection_truth.items(),
                key=lambda x: abs(x[1] - 0.5),  # Keep those furthest from neutral
                reverse=True
            )[:5000])

            data = {
                'word_truth': dict(self.word_truth),
                'connection_truth': top_conns,
                'truth_score': self.truth_score,
                'credibility': round(self.credibility, 4),
                'truth_chain_count': self.truth_chain_count,
                'lie_chain_count': self.lie_chain_count,
                'lie_alerts': self.lie_alerts[-50:],
                'truth_events': self.truth_events[-self.max_events:],
                'last_save': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            tmp = str(self.data_file) + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(data, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, str(self.data_file))
        except Exception as e:
            print('[TRUTH] Save error: %s' % e)

    def _save_loop(self):
        """Save every 15 minutes."""
        while True:
            time.sleep(900)
            with self.lock:
                self._save()

    def _conn_key(self, w1, w2):
        """Consistent connection key (alphabetical order)."""
        a, b = sorted([w1.lower(), w2.lower()])
        return '%s|%s' % (a, b)

    def _log_event(self, event_type, detail, score_change):
        """Log a truth event."""
        entry = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'detail': detail[:120],
            'score_change': round(score_change, 3),
            'credibility': round(self.credibility, 3),
        }
        self.truth_events.append(entry)
        if len(self.truth_events) > self.max_events:
            self.truth_events.pop(0)

    def on_coherent_response(self, question, response, coherence_score):
        """Called when a response passes coherence threshold.
        Higher coherence = more likely truthful (but not guaranteed)."""
        if not response:
            return

        words = response.lower().split()
        q_words = question.lower().split()

        with self.lock:
            # Coherent response = slight truth boost to words used
            if coherence_score >= 0.5:
                boost = (coherence_score - 0.5) * 0.02  # Very small — coherence != truth
                for w in words:
                    if len(w) > 2:
                        old = self.word_truth[w]
                        self.word_truth[w] = min(1.0, old + boost)

                # Boost connections between question and response words
                for qw in q_words:
                    for rw in words:
                        if len(qw) > 2 and len(rw) > 2 and qw != rw:
                            key = self._conn_key(qw, rw)
                            old = self.connection_truth.get(key, 0.5)
                            self.connection_truth[key] = min(1.0, old + boost * 0.5)

                self.truth_score += coherence_score * 0.1
                self.credibility = min(1.0, self.credibility + 0.001)

            # Very low coherence = possible falsehood
            elif coherence_score < 0.2:
                penalty = (0.2 - coherence_score) * 0.01  # Gamified: damage is SLOW
                for w in words:
                    if len(w) > 2:
                        old = self.word_truth[w]
                        self.word_truth[w] = max(0.0, old - penalty)

                # Small credibility hit
                self.credibility = max(0.0, self.credibility - 0.0005)
                self._log_event('low_truth', 'Low coherence response (%.2f)' % coherence_score, -penalty)

    def on_learn_sequence(self, sequence):
        """Called when brain learns a new sequence. Set initial truth weights for new connections."""
        words = sequence.lower().split()
        if len(words) < 2:
            return

        with self.lock:
            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i + 1]
                if len(w1) > 2 and len(w2) > 2:
                    key = self._conn_key(w1, w2)
                    if key not in self.connection_truth:
                        # New connection starts at 0.5 (unknown truth value)
                        self.connection_truth[key] = 0.5

    def trace_truth_chain(self, start_word, brain_data, max_depth=5):
        """Trace truth weights along connection chains from a word.
        Returns truth chain analysis."""
        nodes = brain_data.get('nodes', {})
        if start_word not in nodes:
            return None

        chain = []
        visited = {start_word}
        current = start_word

        for depth in range(max_depth):
            node = nodes.get(current, {})
            # Brain nodes use 'next' (bigram forward connections), not 'connections'
            raw_next = node.get('next', {})
            if not raw_next:
                break
            total_count = sum(raw_next.values()) or 1
            connections = {w: c / total_count for w, c in raw_next.items()}

            # Find strongest connection
            best_word = None
            best_weight = 0
            for w, weight in connections.items():
                if w not in visited and weight > best_weight:
                    best_word = w
                    best_weight = weight

            if not best_word:
                break

            key = self._conn_key(current, best_word)
            truth_w = self.connection_truth.get(key, 0.5)

            chain.append({
                'from': current,
                'to': best_word,
                'connection_weight': round(best_weight, 3),
                'truth_weight': round(truth_w, 3),
            })

            visited.add(best_word)
            current = best_word

        if not chain:
            return None

        # Analyse chain
        truth_weights = [c['truth_weight'] for c in chain]
        avg_truth = sum(truth_weights) / len(truth_weights)
        min_truth = min(truth_weights)

        # LIE CHAIN DETECTION: individually OK connections that form a weak chain
        is_lie_chain = (avg_truth < 0.35 and len(chain) >= 3 and
                        all(c['truth_weight'] > 0.2 for c in chain))

        result = {
            'start': start_word,
            'chain': chain,
            'length': len(chain),
            'avg_truth': round(avg_truth, 3),
            'min_truth': round(min_truth, 3),
            'is_lie_chain': is_lie_chain,
        }

        if is_lie_chain:
            with self.lock:
                self.lie_chain_count += 1
                alert = {
                    'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'chain': [c['from'] for c in chain] + [chain[-1]['to']],
                    'avg_truth': round(avg_truth, 3),
                    'detail': 'Lie chain: %s' % ' -> '.join([c['from'] for c in chain] + [chain[-1]['to']]),
                }
                self.lie_alerts.append(alert)
                if len(self.lie_alerts) > 50:
                    self.lie_alerts.pop(0)
                self._log_event('lie_chain', alert['detail'], -0.005)
                self.credibility = max(0.0, self.credibility - 0.003)

        return result

    def scan_for_chains(self, brain_data, sample_size=10):
        """Scan random words for truth/lie chains. Called periodically."""
        nodes = brain_data.get('nodes', {})
        if not nodes:
            return []

        # Sample random defined words
        defined = [w for w, v in nodes.items() if v.get('means')]
        if not defined:
            return []

        sample = random.sample(defined, min(sample_size, len(defined)))
        results = []

        for word in sample:
            chain = self.trace_truth_chain(word, brain_data)
            if chain and chain['length'] >= 2:
                results.append(chain)
                if chain['is_lie_chain']:
                    pass  # Already logged in trace_truth_chain

                # TRUTH CHAIN: consistently high truth weights
                elif chain['avg_truth'] >= 0.7 and chain['length'] >= 3:
                    with self.lock:
                        self.truth_chain_count += 1
                        self.truth_score += chain['avg_truth'] * 0.5
                        self.credibility = min(1.0, self.credibility + 0.002)
                        self._log_event('truth_chain',
                                        'Strong chain: %s' % ' -> '.join([c['from'] for c in chain['chain']]),
                                        0.002)

        return results

    def get_stats(self):
        """Get truth engine stats for dashboard."""
        with self.lock:
            # Word truth distribution
            truth_values = list(self.word_truth.values())
            conn_values = list(self.connection_truth.values())

            # Top truthful words
            top_truthful = sorted(self.word_truth.items(), key=lambda x: x[1], reverse=True)[:15]
            # Most suspicious words
            most_suspicious = sorted(self.word_truth.items(), key=lambda x: x[1])[:15]

            return {
                'truth_score': round(self.truth_score, 1),
                'credibility': round(self.credibility, 3),
                'truth_chain_count': self.truth_chain_count,
                'lie_chain_count': self.lie_chain_count,
                'total_words_scored': len(self.word_truth),
                'total_connections_scored': len(self.connection_truth),
                'word_truth_distribution': {
                    'high': sum(1 for v in truth_values if v >= 0.7),
                    'neutral': sum(1 for v in truth_values if 0.3 <= v < 0.7),
                    'low': sum(1 for v in truth_values if v < 0.3),
                },
                'connection_truth_distribution': {
                    'high': sum(1 for v in conn_values if v >= 0.7),
                    'neutral': sum(1 for v in conn_values if 0.3 <= v < 0.7),
                    'low': sum(1 for v in conn_values if v < 0.3),
                },
                'top_truthful': [{'word': w, 'score': round(s, 3)} for w, s in top_truthful],
                'most_suspicious': [{'word': w, 'score': round(s, 3)} for w, s in most_suspicious],
                'recent_lie_alerts': self.lie_alerts[-10:],
                'recent_events': self.truth_events[-20:],
                'gamification': {
                    'truth_score': round(self.truth_score, 1),
                    'credibility_rating': _credibility_label(self.credibility),
                    'credibility_value': round(self.credibility, 3),
                    'truth_chains_found': self.truth_chain_count,
                    'lie_chains_detected': self.lie_chain_count,
                },
            }


def _credibility_label(score):
    """Convert credibility score to a human-readable label."""
    if score >= 0.9:
        return 'ORACLE'
    elif score >= 0.75:
        return 'TRUSTED'
    elif score >= 0.6:
        return 'RELIABLE'
    elif score >= 0.45:
        return 'LEARNING'
    elif score >= 0.3:
        return 'UNCERTAIN'
    elif score >= 0.15:
        return 'SUSPICIOUS'
    else:
        return 'UNRELIABLE'
