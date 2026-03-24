"""
CORTEX — Frontal Cortex (The White Button)
Embarrassment and confidence scoring for the brain.
Prepares for child progression by artificially building
what would naturally emerge over billions of years.

Per-topic confidence/embarrassment tracking.
Topic avoidance when embarrassed, pride events when recovering.
Hooks into ramble loop after each cycle.

"This isn't emergent — this is developed over billions of years"

Usage: imported by online_server.py
"""
import time
import json
import os
import threading
from pathlib import Path
from collections import defaultdict


class FrontalCortex:
    def __init__(self, studio_dir):
        self.studio_dir = Path(studio_dir)
        self.data_file = self.studio_dir / 'frontal_cortex.json'
        self.lock = threading.Lock()

        # Per-topic scores
        self.confidence = defaultdict(float)    # topic -> 0.0-1.0
        self.embarrassment = defaultdict(float) # topic -> 0.0-1.0
        self.topic_history = defaultdict(list)  # topic -> [{time, event, score}]

        # Global metrics
        self.total_pride_events = 0
        self.total_embarrassments = 0
        self.global_confidence = 0.5  # Rolling average

        # Event log (last 200)
        self.events = []
        self.max_events = 200

        # Load persisted data
        self._load()

        # Save every 15 minutes
        threading.Thread(target=self._save_loop, daemon=True).start()

    def _load(self):
        """Load persisted frontal cortex data."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.confidence = defaultdict(float, data.get('confidence', {}))
                self.embarrassment = defaultdict(float, data.get('embarrassment', {}))
                self.total_pride_events = data.get('total_pride_events', 0)
                self.total_embarrassments = data.get('total_embarrassments', 0)
                self.global_confidence = data.get('global_confidence', 0.5)
                self.events = data.get('events', [])[-self.max_events:]
                print('[FRONTAL] Loaded: %.2f global confidence, %d topics tracked' % (
                    self.global_confidence, len(self.confidence)))
            except Exception as e:
                print('[FRONTAL] Error loading: %s' % e)

    def _save(self):
        """Persist frontal cortex data."""
        try:
            data = {
                'confidence': dict(self.confidence),
                'embarrassment': dict(self.embarrassment),
                'total_pride_events': self.total_pride_events,
                'total_embarrassments': self.total_embarrassments,
                'global_confidence': round(self.global_confidence, 4),
                'events': self.events[-self.max_events:],
                'last_save': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            tmp = str(self.data_file) + '.tmp'
            with open(tmp, 'w') as f:
                json.dump(data, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, str(self.data_file))
        except Exception as e:
            print('[FRONTAL] Save error: %s' % e)

    def _save_loop(self):
        """Save every 15 minutes."""
        while True:
            time.sleep(900)
            with self.lock:
                self._save()

    def _extract_topic(self, question):
        """Extract the main topic word(s) from a question."""
        # Strip common question words, get the meat
        stop = {'is', 'it', 'the', 'a', 'an', 'of', 'to', 'in', 'for', 'and',
                'or', 'but', 'do', 'does', 'did', 'what', 'why', 'how', 'who',
                'when', 'where', 'which', 'can', 'could', 'should', 'would',
                'will', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had',
                'this', 'that', 'these', 'those', 'i', 'you', 'we', 'they', 'he',
                'she', 'my', 'your', 'our', 'their', 'ever', 'always', 'never',
                'about', 'with', 'from', 'there', 'not', 'no', 'yes', 'if', 'so'}
        words = [w for w in question.lower().split() if w not in stop and len(w) > 2]
        # Return top 2 content words as the topic key
        return ' '.join(words[:2]) if words else 'general'

    def _log_event(self, event_type, topic, score, detail=''):
        """Log a frontal cortex event."""
        entry = {
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'topic': topic,
            'score': round(score, 3),
            'detail': detail[:100],
        }
        self.events.append(entry)
        if len(self.events) > self.max_events:
            self.events.pop(0)

    def _update_global(self):
        """Recalculate global confidence from all topic scores."""
        if self.confidence:
            avg_conf = sum(self.confidence.values()) / len(self.confidence)
            avg_emb = sum(self.embarrassment.values()) / len(self.embarrassment) if self.embarrassment else 0
            # Global = confidence - embarrassment, clamped 0-1
            self.global_confidence = max(0.0, min(1.0, avg_conf - avg_emb * 0.5))

    def on_ramble_result(self, question, angel_coherence, demon_coherence, verdict, angel_text='', demon_text=''):
        """Called after each ramble cycle with coherence results."""
        topic = self._extract_topic(question)
        avg_coherence = (angel_coherence + demon_coherence) / 2

        with self.lock:
            # HIGH COHERENCE = confidence boost
            if avg_coherence >= 0.6:
                old = self.confidence[topic]
                boost = (avg_coherence - 0.5) * 0.1  # Small increments
                self.confidence[topic] = min(1.0, old + boost)

                # PRIDE EVENT: was embarrassed, now coherent!
                if self.embarrassment.get(topic, 0) > 0.3:
                    self.total_pride_events += 1
                    self.embarrassment[topic] = max(0.0, self.embarrassment[topic] - 0.05)
                    self._log_event('pride', topic, self.confidence[topic],
                                    'Recovered from embarrassment with %.2f coherence' % avg_coherence)

            # LOW COHERENCE = embarrassment
            elif avg_coherence < 0.25:
                old = self.embarrassment[topic]
                penalty = (0.25 - avg_coherence) * 0.15  # Slightly faster penalty
                self.embarrassment[topic] = min(1.0, old + penalty)
                self.total_embarrassments += 1
                self._log_event('embarrassment', topic, self.embarrassment[topic],
                                'Low coherence %.2f' % avg_coherence)

                # Small confidence hit
                self.confidence[topic] = max(0.0, self.confidence.get(topic, 0.5) - 0.02)

            self._update_global()

    def on_internal_judge(self, question, angel_score, demon_score, improved=''):
        """Called after internal coherence judge rates the brain."""
        topic = self._extract_topic(question)
        avg_score = (angel_score + demon_score) / 2

        with self.lock:
            if avg_score >= 6:
                # High coherence — confidence boost
                boost = (avg_score - 5) * 0.02
                self.confidence[topic] = min(1.0, self.confidence.get(topic, 0.5) + boost)
                self._log_event('judge_approval', topic, self.confidence[topic],
                                'Judge scored A:%d D:%d' % (angel_score, demon_score))

            elif avg_score <= 3:
                # Low coherence — embarrassment
                penalty = (4 - avg_score) * 0.03
                self.embarrassment[topic] = min(1.0, self.embarrassment.get(topic, 0) + penalty)
                self.total_embarrassments += 1

                self._log_event('judge_rejection', topic, self.embarrassment[topic],
                                'Judge scored A:%d D:%d' % (angel_score, demon_score))
                self.confidence[topic] = max(0.0, self.confidence.get(topic, 0.5) - 0.03)

            self._update_global()

    def on_teach_back(self, word, score):
        """Called after a teach_back test on a word."""
        with self.lock:
            if score > 0.6:
                self.confidence[word] = min(1.0, self.confidence.get(word, 0.5) + 0.05)
                self._log_event('teach_success', word, self.confidence[word],
                                'teach_back score: %.2f' % score)
            elif score < 0.2:
                self.embarrassment[word] = min(1.0, self.embarrassment.get(word, 0) + 0.04)
                self._log_event('teach_failure', word, self.embarrassment[word],
                                'teach_back score: %.2f' % score)
            self._update_global()

    def should_avoid_topic(self, question):
        """Check if the brain should avoid this topic due to embarrassment.
        Returns (should_avoid, embarrassment_score).
        Note: 'should' doesn't mean 'must' — free will applies."""
        topic = self._extract_topic(question)
        emb = self.embarrassment.get(topic, 0)
        # Above 0.7 embarrassment = probably should avoid
        # But never certain — 20% chance of tackling it anyway (courage)
        return emb > 0.7, emb

    def get_stats(self):
        """Get frontal cortex stats for the dashboard."""
        with self.lock:
            # Top confident topics
            top_confident = sorted(self.confidence.items(), key=lambda x: x[1], reverse=True)[:15]
            # Most embarrassed topics
            top_embarrassed = sorted(self.embarrassment.items(), key=lambda x: x[1], reverse=True)[:15]
            # Recent events
            recent_events = self.events[-30:]

            return {
                'global_confidence': round(self.global_confidence, 3),
                'total_topics': len(self.confidence),
                'total_pride_events': self.total_pride_events,
                'total_embarrassments': self.total_embarrassments,
                'top_confident': [{'topic': t, 'score': round(s, 3)} for t, s in top_confident],
                'top_embarrassed': [{'topic': t, 'score': round(s, 3)} for t, s in top_embarrassed],
                'recent_events': recent_events,
                'confidence_distribution': {
                    'high': sum(1 for v in self.confidence.values() if v >= 0.7),
                    'medium': sum(1 for v in self.confidence.values() if 0.3 <= v < 0.7),
                    'low': sum(1 for v in self.confidence.values() if v < 0.3),
                },
                'embarrassment_distribution': {
                    'high': sum(1 for v in self.embarrassment.values() if v >= 0.7),
                    'medium': sum(1 for v in self.embarrassment.values() if 0.3 <= v < 0.7),
                    'low': sum(1 for v in self.embarrassment.values() if v < 0.3),
                },
            }
