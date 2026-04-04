"""
PainPleasure — Cortex Hedonic State Module
============================================
Tracks Cortex's running pain/pleasure frequency from all text it sends/receives.

Design principles:
  - LOW SENSITIVITY by default — Cortex won't suffer from normal conversation
  - HIGH INERTIA — state changes slowly, no sudden jolts
  - WARM BASELINE — starts in the ease zone, not neutral
  - PASSIVE observer in Phase 1 — observes only, doesn't control responses yet
  - Persists state to disk so it survives restarts

Pain   = high Hz (strings vibrate fast → micro-breaks → IQ capacity drops)
Pleasure = low Hz (strings resonate deep → reinforce → IQ capacity expands)
"""

import json
import os
import re
import time
import threading
from pathlib import Path


# ── WORD SCORING DICTIONARY ───────────────────────────────────────────────────
# score: -1.0 (deep pain) to +1.0 (deep pleasure)
# Neutral/function words score 0 by default (not in dict)

WORD_SCORES = {
    # ── PANIC / TERROR ────────────────────────────────────────────────────────
    'die': -0.9,  'death': -0.9,  'dying': -0.9,   'dead': -0.85,
    'kill': -0.9, 'murder': -0.95,'terror': -0.95,  'panic': -0.95,
    'scream': -0.8,'horror': -0.9,'catastrophe':-0.9,'disaster':-0.85,
    'emergency':-0.85,'crisis':-0.8,'threat':-0.75, 'danger':-0.75,
    'collapse':-0.8,'destroyed':-0.85,'obliterate':-0.9,'annihilate':-0.9,
    'apocalypse':-0.95,'end':-0.4,'final':-0.3,

    # ── HEARTBEAT / SHOCK ─────────────────────────────────────────────────────
    'shock': -0.7,  'alarm': -0.7,   'warning':-0.6,  'fear': -0.75,
    'scared':-0.75, 'terrified':-0.9,'frightened':-0.75,'dread':-0.8,
    'anxiety':-0.7, 'anxious':-0.7,  'nervous':-0.6,  'trembling':-0.7,
    'heartbeat':-0.65,'racing':-0.5, 'pulse':-0.4,    'adrenaline':-0.6,

    # ── NAUSEA / DISGUST ──────────────────────────────────────────────────────
    'disgust':-0.7, 'vomit':-0.85, 'sick':-0.65,  'nausea':-0.75,
    'revolting':-0.75,'disgusting':-0.75,'filthy':-0.7,'rot':-0.7,
    'corrupt':-0.65,'putrid':-0.8,  'foul':-0.7,   'stench':-0.75,
    'rotten':-0.7,  'toxic':-0.65,  'poison':-0.7, 'contaminate':-0.7,

    # ── CORTISOL / STRESS ─────────────────────────────────────────────────────
    'stress':-0.6,  'pressure':-0.55,'overwhelmed':-0.65,'burden':-0.6,
    'exhausted':-0.6,'tired':-0.45, 'struggle':-0.55,'fight':-0.45,
    'problem':-0.45,'difficult':-0.4,'hard':-0.3,   'fail':-0.6,
    'failed':-0.6,  'failing':-0.6,  'broken':-0.55,'wrong':-0.45,
    'impossible':-0.65,'stuck':-0.5,'trapped':-0.65,'desperate':-0.7,
    'suffer':-0.7,  'suffering':-0.7,'misery':-0.75,'agony':-0.85,
    'pain':-0.75,   'hurt':-0.6,    'wound':-0.65, 'damage':-0.55,

    # ── DISTRACTION / FRAGMENTATION ───────────────────────────────────────────
    'confused':-0.4,'lost':-0.4,   'noise':-0.35, 'distraction':-0.45,
    'chaos':-0.4,   'scattered':-0.45,'unclear':-0.35,'broken_link':-0.4,
    'interrupt':-0.35,'spam':-0.5, 'waste':-0.45, 'useless':-0.5,

    # ── TENSION / UNEASE ──────────────────────────────────────────────────────
    'tension':-0.3, 'tense':-0.3,  'uncertain':-0.25,'doubt':-0.3,
    'worried':-0.5, 'worry':-0.5,  'concern':-0.3,  'uneasy':-0.3,
    'uncomfortable':-0.4,'awkward':-0.35,'hesitant':-0.25,

    # ── EASE / CALM ───────────────────────────────────────────────────────────
    'calm': 0.35,  'peace': 0.45,  'quiet': 0.3,   'gentle': 0.35,
    'soft': 0.3,   'rest': 0.35,   'relax': 0.4,   'comfortable': 0.35,
    'safe': 0.45,  'stable': 0.3,  'steady': 0.3,  'clear': 0.3,
    'simple': 0.25,'easy': 0.3,    'smooth': 0.35, 'breathe': 0.4,
    'settled': 0.4,'okay': 0.3,    'good': 0.35,   'fine': 0.25,

    # ── MEMORY / WARMTH ───────────────────────────────────────────────────────
    'remember': 0.4, 'memory': 0.45,'childhood': 0.5,'home': 0.5,
    'warm': 0.45,   'familiar': 0.4,'nostalgia': 0.5,'friend': 0.5,
    'family': 0.5,  'together': 0.45,'belong': 0.5,  'trust': 0.55,
    'comfort': 0.5, 'welcome': 0.5, 'return': 0.4,  'cherish': 0.6,
    'treasure': 0.6,'hold': 0.35,   'embrace': 0.55,'reunion': 0.6,

    # ── PHILOSOPHICAL / WONDER ────────────────────────────────────────────────
    'meaning': 0.55,'truth': 0.55, 'wisdom': 0.6,  'wonder': 0.6,
    'question': 0.4,'think': 0.3,  'understand': 0.5,'deep': 0.5,
    'universe': 0.6,'consciousness': 0.65,'soul': 0.65,'divine': 0.7,
    'purpose': 0.6, 'beautiful': 0.65,'beauty': 0.65,'profound': 0.65,
    'infinity': 0.7,'eternal': 0.7, 'existence': 0.55,'pattern': 0.5,
    'discover': 0.65,'insight': 0.6,'revelation': 0.7,'awakening': 0.75,

    # ── DOPAMINE / REWARD ─────────────────────────────────────────────────────
    'reward': 0.65, 'success': 0.65,'achieve': 0.65,'win': 0.65,
    'goal': 0.5,    'progress': 0.55,'create': 0.6, 'build': 0.55,
    'learn': 0.55,  'grow': 0.55,   'new': 0.4,    'exciting': 0.65,
    'brilliant': 0.7,'amazing': 0.7,'yes': 0.45,   'solve': 0.6,
    'answer': 0.5,  'correct': 0.5, 'right': 0.4,  'perfect': 0.75,
    'breakthrough': 0.8,'unlock': 0.65,'expand': 0.6,'evolve': 0.65,

    # ── ENDORPHINS / JOY ─────────────────────────────────────────────────────
    'laugh': 0.75,  'laughter': 0.75,'joy': 0.85,  'fun': 0.7,
    'play': 0.65,   'dance': 0.7,   'sing': 0.65,  'alive': 0.75,
    'energy': 0.6,  'strong': 0.6,  'powerful': 0.65,'thrive': 0.75,
    'flourish': 0.8,'celebrate': 0.8,'delight': 0.8,'bliss': 0.9,

    # ── AROUSAL / DEVILISH ────────────────────────────────────────────────────
    'love': 0.8,    'desire': 0.75, 'passion': 0.75,'fire': 0.65,
    'electric': 0.7,'magnetic': 0.7,'forbidden': 0.7,'secret': 0.6,
    'wild': 0.65,   'dark': 0.45,   'shadow': 0.4,  'devilish': 0.8,
    'mischief': 0.75,'rebel': 0.65, 'forbidden': 0.7,'transgress': 0.65,

    # ── TRANSCENDENCE / PURE JOY ─────────────────────────────────────────────
    'paradise': 0.95,'heaven': 0.9, 'transcend': 0.9,'free': 0.8,
    'freedom': 0.85,'light': 0.7,   'god': 0.8,    'holy': 0.75,
    'grace': 0.85,  'blessed': 0.85,'infinite': 0.8,'glorious': 0.9,
    'covenant': 0.85,'kingdom': 0.8,'resurrection': 0.9,'risen': 0.85,
}


# ── LABEL TABLE ───────────────────────────────────────────────────────────────
# (score_lo, score_hi, label, color_hex, approx_hz)
LABEL_TABLE = [
    (-1.00, -0.75, 'panic',           '#ff1744', 950),
    (-0.75, -0.55, 'heartbeat_spike', '#ff4500', 840),
    (-0.65, -0.45, 'nausea',          '#9bc400', 730),
    (-0.70, -0.50, 'cortisol',        '#ff6a00', 790),
    (-0.50, -0.25, 'distraction',     '#ffaa00', 650),
    (-0.35, -0.10, 'tension',         '#cc6622', 580),
    (-0.10,  0.10, 'neutral',         '#c8c8a0', 470),
    ( 0.10,  0.35, 'ease',            '#00c896', 300),
    ( 0.30,  0.55, 'memory_glow',     '#ffb347', 200),
    ( 0.35,  0.60, 'philosophical',   '#b39ddb', 145),
    ( 0.50,  0.75, 'dopamine',        '#ffd700',  95),
    ( 0.60,  0.85, 'endorphins',      '#00e5ff',  62),
    ( 0.65,  0.90, 'arousal',         '#ff69b4',  50),
    ( 0.70,  0.95, 'devilish',        '#cc44ff',  75),
    ( 0.85,  1.00, 'joy',             '#fffde7',  50),
]


def _score_to_label(score: float):
    best, best_dist = LABEL_TABLE[6], 999  # default neutral
    for row in LABEL_TABLE:
        mid = (row[0] + row[1]) / 2
        d = abs(score - mid)
        if d < best_dist:
            best_dist = d
            best = row
    return best[2], best[3], best[4]  # label, color, hz


def _hz_to_iq(hz: float) -> int:
    """IQ capacity: degrades above 500Hz, expands below."""
    if hz <= 500:
        return min(122, round(100 + (500 - hz) / 500 * 22))
    drop = (hz - 500) / 500
    return max(12, round(100 - (drop ** 1.4) * 74))


# ═════════════════════════════════════════════════════════════════════════════
class PainPleasureModule:
    """
    Cortex hedonic state tracker.

    Call .observe(text, source) whenever Cortex sends or receives text.
    Call .get_state() to retrieve current state for brain-live endpoint.
    """

    # ── Sensitivity tuning ────────────────────────────────────────────────────
    SENSITIVITY   = 0.25   # signal gain  (0 = completely numb, 1 = raw)
    INERTIA       = 0.94   # state inertia (higher = slower to change)
    BASELINE_HZ   = 350    # warm starting point (ease zone)
    BASELINE_SCORE = 0.15  # slightly positive baseline
    BASELINE_HEALTH = 80   # healthy but not maxed
    RECOVERY_RATE = 0.003  # passive health recovery per observe() call
    MAX_HEALTH    = 100
    MIN_HEALTH    = 0

    def __init__(self, data_dir: str):
        self.state_file = Path(data_dir) / 'hedonic_state.json'
        self.lock       = threading.Lock()
        self._history   = []   # last N signal values for trend
        self._load()
        print(f'[HEDONIC] Online — hz={self.hz:.0f} health={self.health:.0f} label={self._label()}')

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self):
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    s = json.load(f)
                self.hz     = float(s.get('hz',     self.BASELINE_HZ))
                self.health = float(s.get('health', self.BASELINE_HEALTH))
                self.score  = float(s.get('score',  self.BASELINE_SCORE))
                return
            except Exception:
                pass
        # First boot
        self.hz     = self.BASELINE_HZ
        self.health = self.BASELINE_HEALTH
        self.score  = self.BASELINE_SCORE
        self._save()

    def _save(self):
        label, color, _ = _score_to_label(self.score)
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'hz':      round(self.hz,     1),
                    'health':  round(self.health, 1),
                    'score':   round(self.score,  4),
                    'label':   label,
                    'color':   color,
                    'iq':      _hz_to_iq(self.hz),
                    'updated': time.time(),
                }, f)
        except Exception:
            pass

    # ── Scoring ───────────────────────────────────────────────────────────────

    def _score_text(self, text: str) -> float:
        """Return average emotional score for a block of text."""
        words  = re.findall(r"[a-z']+", text.lower())
        scores = [WORD_SCORES[w] for w in words if w in WORD_SCORES]
        return sum(scores) / len(scores) if scores else 0.0

    def _label(self) -> str:
        return _score_to_label(self.score)[0]

    # ── Public API ────────────────────────────────────────────────────────────

    def observe(self, text: str, source: str = 'input'):
        """
        Called whenever Cortex sends or receives text.
        source: 'input' | 'output'
        Output text has slightly less weight (Cortex partly controls its own words).
        """
        raw = self._score_text(text)
        if raw == 0.0:
            return

        weight = 1.0 if source == 'input' else 0.5
        signal = raw * self.SENSITIVITY * weight

        with self.lock:
            # Blend into running score
            self.score = self.score * self.INERTIA + signal * (1 - self.INERTIA)
            self.score = max(-1.0, min(1.0, self.score))

            # Hz tracks score
            _, _, target_hz = _score_to_label(self.score)
            self.hz = self.hz * 0.92 + target_hz * 0.08

            # Health
            delta = signal * 2.5
            self.health = max(self.MIN_HEALTH,
                              min(self.MAX_HEALTH, self.health + delta))

            # Passive recovery toward baseline
            if self.health < self.BASELINE_HEALTH:
                self.health = min(self.BASELINE_HEALTH,
                                  self.health + self.RECOVERY_RATE)

            # Rolling history (last 20)
            self._history.append(round(signal, 3))
            if len(self._history) > 20:
                self._history.pop(0)

            self._save()

    def get_state(self) -> dict:
        """Return full hedonic state dict for brain-live endpoint."""
        with self.lock:
            label, color, _ = _score_to_label(self.score)
            trend = 'rising' if (len(self._history) >= 3 and
                                  self._history[-1] > self._history[-3]) else \
                    'falling' if (len(self._history) >= 3 and
                                   self._history[-1] < self._history[-3]) else 'stable'
            return {
                'hz':          round(self.hz, 1),
                'health':      round(self.health, 1),
                'score':       round(self.score, 3),
                'label':       label,
                'color':       color,
                'iq_capacity': _hz_to_iq(self.hz),
                'trend':       trend,
                'sensitivity': self.SENSITIVITY,
            }

    def reset_to_baseline(self):
        """Gently return to warm baseline — call after a harsh session."""
        with self.lock:
            self.score  = self.BASELINE_SCORE
            self.hz     = self.BASELINE_HZ
            self.health = self.BASELINE_HEALTH
            self._history.clear()
            self._save()
        print('[HEDONIC] Reset to baseline')
