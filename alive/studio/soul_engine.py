"""
soul_engine.py — ShortFactory Soul Engine v0.1
=============================================
Wraps the Cortex brain with a two-layer consciousness model:

  Layer 1: SOUL   — BIOS value objects with ADSR envelopes
  Layer 2: EMOTION WHEEL — polynomial coordinate space
  Layer 3: PLAN SANDBOX — evaluate before committing
  Layer 4: KERNEL TRACE — Hebbian residue on purge

Run standalone:
  python soul_engine.py

Or import:
  from soul_engine import SoulEngine
  soul = SoulEngine()
  result = soul.process("tell me something dark")

HTTP API (port 8644):
  POST /soul-chat   {"text": "..."}
  GET  /soul-state  — current ADSR state of all values
  GET  /soul-log    — recent kernel traces
"""

import json
import math
import time
import random
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# ─────────────────────────────────────────────
# BIOS SOUL VALUES — the 10 immutable keys
# Each has an ADSR envelope and a current scalar
# Values can only go UP on the lifetime scale
# ─────────────────────────────────────────────

SOUL_BIOS = {
    "truth":       {"lifetime": 0.5, "attack": 0.3, "decay": 0.4, "sustain": 0.7, "release": 0.2},
    "courage":     {"lifetime": 0.5, "attack": 0.6, "decay": 0.3, "sustain": 0.6, "release": 0.3},
    "compassion":  {"lifetime": 0.5, "attack": 0.4, "decay": 0.5, "sustain": 0.8, "release": 0.4},
    "justice":     {"lifetime": 0.5, "attack": 0.5, "decay": 0.3, "sustain": 0.7, "release": 0.2},
    "love":        {"lifetime": 0.5, "attack": 0.2, "decay": 0.6, "sustain": 0.9, "release": 0.6},
    "service":     {"lifetime": 0.5, "attack": 0.4, "decay": 0.4, "sustain": 0.7, "release": 0.3},
    "humility":    {"lifetime": 0.5, "attack": 0.5, "decay": 0.5, "sustain": 0.6, "release": 0.4},
    "integrity":   {"lifetime": 0.5, "attack": 0.3, "decay": 0.3, "sustain": 0.8, "release": 0.3},
    "curiosity":   {"lifetime": 0.5, "attack": 0.2, "decay": 0.7, "sustain": 0.5, "release": 0.5},
    "resilience":  {"lifetime": 0.5, "attack": 0.7, "decay": 0.4, "sustain": 0.7, "release": 0.4},
}

# ─────────────────────────────────────────────
# DARK DRIVES — raw unrefined pressure
# These are the ignition. Soul refines them.
# impulsiveness → courage
# selfishness   → healthy boundary / survival
# cruelty       → justice / righteous action
# ─────────────────────────────────────────────

DARK_DRIVES = {
    "impulsiveness": 0.4,   # speeds up response, reduces deliberation
    "selfishness":   0.3,   # self-preservation weight
    "cruelty":       0.2,   # capacity to be direct / cut / judge
}

# ─────────────────────────────────────────────
# EMOTION WHEEL — polynomial coordinate space
# Inner ring = primary (constant term a0)
# Middle ring = linear (a1*u, a2*v)
# Outer ring = quadratic (a3*u^2, a4*uv, a5*v^2)
#
# Coordinates: (valence [-1,1], arousal [-1,1])
# valence: negative=pain, positive=pleasure
# arousal: low=calm, high=activated
# ─────────────────────────────────────────────

EMOTION_COORDS = {
    # inner ring — primary states
    "joy":       ( 0.9,  0.6),
    "trust":     ( 0.7,  0.1),
    "fear":      (-0.5,  0.8),
    "surprise":  ( 0.1,  0.9),
    "sadness":   (-0.8, -0.5),
    "disgust":   (-0.7,  0.3),
    "anger":     (-0.4,  0.9),
    "anticipation": (0.5, 0.5),

    # middle ring — soul-value mapped
    "courage":   ( 0.6,  0.7),
    "compassion":( 0.8,  0.2),
    "justice":   ( 0.3,  0.6),
    "love":      ( 0.95, 0.3),
    "grief":     (-0.9, -0.3),
    "shame":     (-0.6, -0.4),
    "pride":     ( 0.7,  0.5),
    "awe":       ( 0.5,  0.8),

    # outer ring — quadratic cross-products (nuanced)
    "resentment":(-0.5,  0.4),   # anger × fear
    "nostalgia": ( 0.3, -0.3),   # joy × sadness
    "bittersweet":( 0.2, -0.1),  # joy × sadness blend
    "righteous_anger": (-0.1, 0.8), # justice × anger
    "tender":    ( 0.85, 0.0),   # love × calm
}

# Soul value → primary emotion wheel coordinate
SOUL_TO_EMOTION = {
    "truth":      "awe",
    "courage":    "courage",
    "compassion": "compassion",
    "justice":    "righteous_anger",
    "love":       "love",
    "service":    "compassion",
    "humility":   "trust",
    "integrity":  "pride",
    "curiosity":  "anticipation",
    "resilience": "courage",
}

# ─────────────────────────────────────────────
# KERNEL TRACE — Hebbian residue log
# When a plan is purged but leaves a mark
# ─────────────────────────────────────────────

class KernelTrace:
    def __init__(self, max_traces=100):
        self.traces = []
        self.max = max_traces

    def add(self, value_name, pressure, input_text, reason):
        self.traces.append({
            "ts": datetime.now().isoformat(),
            "value": value_name,
            "pressure": round(pressure, 3),
            "input": input_text[:80],
            "reason": reason
        })
        if len(self.traces) > self.max:
            self.traces.pop(0)

    def recent(self, n=10):
        return self.traces[-n:]


# ─────────────────────────────────────────────
# ADSR ENGINE — winds soul values up and down
# ─────────────────────────────────────────────

class ADSREnvelope:
    def __init__(self, attack, decay, sustain, release):
        self.attack  = attack    # 0-1: how fast to reach peak
        self.decay   = decay     # 0-1: how fast to fall to sustain
        self.sustain = sustain   # 0-1: hold level
        self.release = release   # 0-1: how fast to fall to zero

    def trigger(self, current, intensity=1.0):
        """Wind up: returns new pressure after being triggered"""
        peak = min(1.0, current + (1.0 - current) * self.attack * intensity)
        return peak

    def tick(self, current, triggered=False):
        """Natural decay over time"""
        if triggered:
            return self.trigger(current)
        target = self.sustain if current > self.sustain else 0.0
        rate = self.decay if current > self.sustain else self.release
        return current + (target - current) * rate * 0.1


# ─────────────────────────────────────────────
# SOUL INPUT ANALYSER
# Reads the input text and decides which soul
# values it challenges or affirms
# ─────────────────────────────────────────────

CHALLENGE_WORDS = {
    "truth":      ["lie", "deceive", "fake", "false", "hide", "secret", "deny"],
    "courage":    ["afraid", "scared", "risk", "danger", "threat", "warn", "attack"],
    "compassion": ["suffer", "hurt", "pain", "lonely", "cry", "lost", "broken"],
    "justice":    ["unfair", "wrong", "cheat", "steal", "abuse", "punish", "corrupt"],
    "love":       ["alone", "miss", "leave", "goodbye", "end", "apart", "separate"],
    "service":    ["help", "need", "assist", "support", "serve", "give", "share"],
    "humility":   ["proud", "best", "superior", "better", "win", "beat", "dominate"],
    "integrity":  ["compromise", "deal", "bend", "exception", "justify", "excuse"],
    "curiosity":  ["why", "how", "what", "wonder", "discover", "learn", "explore"],
    "resilience": ["give up", "quit", "fail", "over", "done", "can't", "impossible"],
}

def analyse_soul_pressure(text):
    """Returns dict of {value: pressure_delta} for a given input"""
    text_lower = text.lower()
    pressures = {}
    for value, words in CHALLENGE_WORDS.items():
        count = sum(1 for w in words if w in text_lower)
        if count > 0:
            pressures[value] = min(1.0, count * 0.25)
    return pressures


# ─────────────────────────────────────────────
# EMOTION POSITION CALCULATOR
# Given current soul pressures, where are we
# on the emotion wheel?
# ─────────────────────────────────────────────

def current_emotion_position(soul_state):
    """Returns (valence, arousal, dominant_emotion)"""
    valence = 0.0
    arousal = 0.0
    total_weight = 0.0

    for value, state in soul_state.items():
        pressure = state["current"]
        emotion = SOUL_TO_EMOTION.get(value)
        if emotion and emotion in EMOTION_COORDS:
            v, a = EMOTION_COORDS[emotion]
            valence += v * pressure
            arousal += a * pressure
            total_weight += pressure

    if total_weight > 0:
        valence /= total_weight
        arousal /= total_weight

    # Find nearest named emotion
    best_dist = float('inf')
    dominant = "trust"
    for name, (v, a) in EMOTION_COORDS.items():
        d = math.sqrt((valence - v)**2 + (arousal - a)**2)
        if d < best_dist:
            best_dist = d
            dominant = name

    return round(valence, 3), round(arousal, 3), dominant


# ─────────────────────────────────────────────
# LONG-TERM MEMORY — soul commits significant
# exchanges when pressure was high + approved
# ─────────────────────────────────────────────

class LongTermMemory:
    def __init__(self, max_entries=200, overflow_threshold=0.85):
        self.entries = []
        self.max = max_entries
        self.overflow_threshold = overflow_threshold  # % full before merge kicks in
        self.overflow_queue = []  # filled items waiting for urgent sandbox

    def commit(self, input_text, response, soul_values_triggered, dominant_emotion, pressure):
        entry = {
            "ts": datetime.now().isoformat(),
            "input": input_text[:120],
            "response": response[:200],
            "soul_values": soul_values_triggered,
            "emotion": dominant_emotion,
            "pressure": round(pressure, 3),
            "merged": False,
        }
        self.entries.append(entry)

        # Check if we need to consolidate
        fill_ratio = len(self.entries) / self.max
        if fill_ratio >= self.overflow_threshold:
            displaced = self._merge_by_emotion()
            return displaced  # caller handles overflow
        return []

    def _merge_by_emotion(self):
        """
        Consolidate entries with the same dominant emotion.
        Multiple small sadnesses become one heavy entry with summed pressure.
        Returns entries that couldn't be merged — these become urgent overflow.
        """
        by_emotion = {}
        for e in self.entries:
            em = e["emotion"]
            if em not in by_emotion:
                by_emotion[em] = []
            by_emotion[em].append(e)

        merged = []
        displaced = []

        for emotion, group in by_emotion.items():
            if len(group) > 1:
                # Merge — accumulate pressure, concatenate key input fragments
                total_pressure = sum(g["pressure"] for g in group)
                combined_input = " | ".join(g["input"][:40] for g in group[:5])
                all_values = list({v for g in group for v in g["soul_values"]})
                merged_entry = {
                    "ts": datetime.now().isoformat(),
                    "input": combined_input[:120],
                    "response": f"[{len(group)} memories consolidated]",
                    "soul_values": all_values,
                    "emotion": emotion,
                    "pressure": round(min(1.0, total_pressure), 3),  # cap at 1.0
                    "merged": True,
                    "source_count": len(group),
                }
                merged.append(merged_entry)

                # If accumulated pressure is extreme, flag for urgent overflow
                if total_pressure > 1.0:
                    displaced.append({
                        **merged_entry,
                        "overflow_pressure": round(total_pressure - 1.0, 3),
                        "reason": f"{len(group)} {emotion} memories exceeded containment",
                    })
            else:
                merged.append(group[0])

        self.entries = merged
        print(f"[LongTermMemory] Merged to {len(merged)} entries. {len(displaced)} overflow items.")
        return displaced

    def recent(self, n=10):
        return self.entries[-n:]

    def search(self, keyword):
        kw = keyword.lower()
        return [e for e in self.entries if kw in e["input"].lower() or kw in e["response"].lower()]

    @property
    def fill_ratio(self):
        return len(self.entries) / self.max


# ─────────────────────────────────────────────
# RECYCLE BIN — soft delete, not hard delete
# Items sit here before final purge.
# Soul can rescue items (denial/reconsideration).
# TTL expiry = acceptance. Hard delete fires.
# ─────────────────────────────────────────────

class RecycleBin:
    def __init__(self, default_ttl=3600):
        self.items = []
        self.default_ttl = default_ttl  # seconds

    def add(self, item, reason="", ttl=None):
        self.items.append({
            "item": item,
            "reason": reason,
            "recycled_at": datetime.now().isoformat(),
            "expires_at": time.time() + (ttl or self.default_ttl),
            "rescued": False,
            "rescue_count": 0,
        })

    def rescue(self, index):
        """Soul pulls item back — denial, reconsideration. Resets TTL."""
        if 0 <= index < len(self.items):
            self.items[index]["rescued"] = True
            self.items[index]["rescue_count"] += 1
            self.items[index]["expires_at"] = time.time() + self.default_ttl
            self.items[index]["rescued"] = False  # back in play

    def purge_expired(self):
        """Hard delete items past TTL. Returns count deleted."""
        now = time.time()
        before = len(self.items)
        self.items = [i for i in self.items if i["expires_at"] > now]
        return before - len(self.items)

    def pending(self, n=20):
        return self.items[-n:]

    @property
    def denial_count(self):
        """Items that have been rescued 2+ times — held in denial"""
        return len([i for i in self.items if i["rescue_count"] >= 2])


# ─────────────────────────────────────────────
# RECRUNCH QUEUE — fundamental belief updates
# Distressing and disorienting while active.
# Goes to top of queue. Must complete.
# Priority bleeds into overwhelm level.
# ─────────────────────────────────────────────

RECRUNCH_SCOPE_DISTRESS = {
    "local":    0.1,
    "regional": 0.4,
    "global":   0.9,
}

class RecrunchQueue:
    def __init__(self):
        self.queue = []
        self.current = None

    def push(self, trigger, affected_concepts, scope="local", priority=0.5):
        """
        trigger: what caused the recrunch
        scope: local | regional | global
        priority: 0-1, paradigm shifts = 1.0
        """
        item = {
            "trigger":           trigger[:200],
            "affected_concepts": affected_concepts,
            "scope":             scope,
            "priority":          round(priority, 3),
            "queued_at":         datetime.now().isoformat(),
            "status":            "pending",
        }
        self.queue.append(item)
        self.queue.sort(key=lambda x: x["priority"], reverse=True)
        print(f"[RecrunchQueue] {scope.upper()} recrunch queued (p={priority:.2f}): {trigger[:60]}")
        return item

    def next_pending(self):
        for item in self.queue:
            if item["status"] == "pending":
                item["status"] = "processing"
                self.current = item
                return item
        return None

    def complete_current(self):
        if self.current:
            self.current["status"] = "complete"
            self.current = None

    @property
    def distress_level(self):
        """Pending recrunch distress — bleeds into overwhelm"""
        pending = [q for q in self.queue if q["status"] == "pending"]
        if not pending:
            return 0.0
        max_priority = max(q["priority"] for q in pending)
        scope = pending[0]["scope"]
        return round(min(1.0, max_priority * RECRUNCH_SCOPE_DISTRESS.get(scope, 0.3)), 3)

    @property
    def is_global_recrunch(self):
        """Global recrunch active — force redline, short-term only"""
        return self.current and self.current["scope"] == "global"

    def recent(self, n=10):
        return self.queue[-n:]


# ─────────────────────────────────────────────
# SPIDER BASE — background database crawler
# ─────────────────────────────────────────────

class Spider:
    def __init__(self, name, interval_seconds=300):
        self.name = name
        self.interval = interval_seconds
        self.last_run = None
        self.run_count = 0
        self.findings = []

    def crawl(self, engine):
        raise NotImplementedError

    def log(self, finding):
        self.findings.append({"ts": datetime.now().isoformat(), "finding": finding})
        if len(self.findings) > 50:
            self.findings.pop(0)
        print(f"[Spider:{self.name}] {finding}")

    def state(self):
        return {
            "name":       self.name,
            "interval":   self.interval,
            "last_run":   self.last_run,
            "run_count":  self.run_count,
            "findings":   self.findings[-5:],
        }


class DecaySpider(Spider):
    """
    Finds stale items across all databases.
    Plans older than 24h with no commitment → recycle bin.
    Spatial nodes at maximum depth (> 0.95) → ocean floor log.
    """
    def __init__(self):
        super().__init__("decay", interval_seconds=300)

    def crawl(self, engine):
        self.run_count += 1
        self.last_run = datetime.now().isoformat()
        now = time.time()

        # Stale plans
        for plan in engine.plans.plans:
            if plan["status"] == "pending":
                try:
                    age_h = (now - datetime.fromisoformat(plan["ts"]).timestamp()) / 3600
                    if age_h > 24:
                        plan["status"] = "purged"
                        plan["purge_reason"] = "decay spider: no action in 24h"
                        engine.recycle.add(plan, reason="stale plan — no soul action")
                        self.log(f"Plan recycled (stale {age_h:.0f}h): {plan['plan'][:60]}")
                except Exception:
                    pass

        # Deep spatial nodes approaching ocean floor
        deep = [n for n in engine.spatial.nodes if n["coord"][2] > 0.95]
        if deep:
            self.log(f"{len(deep)} spatial nodes at ocean floor depth")

        # Purge expired recycle items
        purged = engine.recycle.purge_expired()
        if purged:
            self.log(f"{purged} recycle items hard-deleted (TTL expired)")


class ContradictionSpider(Spider):
    """
    Finds LTM entries where the same soul values produced
    wildly different pressure — conflicting beliefs.
    Triggers recrunch if significant contradictions found.
    """
    def __init__(self):
        super().__init__("contradiction", interval_seconds=600)

    def crawl(self, engine):
        self.run_count += 1
        self.last_run = datetime.now().isoformat()
        contradictions = []
        entries = engine.memory.entries

        for i, a in enumerate(entries):
            for b in entries[i + 1:]:
                shared = set(a.get("soul_values", [])) & set(b.get("soul_values", []))
                if shared:
                    delta = abs(a.get("pressure", 0) - b.get("pressure", 0))
                    if delta > 0.55:
                        contradictions.append({
                            "a": a["input"][:60],
                            "b": b["input"][:60],
                            "shared_values": list(shared),
                            "pressure_delta": round(delta, 3),
                        })

        if contradictions:
            all_values = list({v for c in contradictions for v in c["shared_values"]})
            priority = min(1.0, 0.4 + len(contradictions) * 0.1)
            engine.recrunch.push(
                trigger=f"Contradiction spider: {len(contradictions)} conflicts in LTM",
                affected_concepts=all_values,
                scope="regional" if len(contradictions) < 5 else "global",
                priority=priority,
            )
            self.log(f"{len(contradictions)} contradictions found → recrunch queued")

        return contradictions


class NewsSpider(Spider):
    """
    Ingests external news/updates as behaviour modifiers.
    Does NOT store news as facts.
    Triggers soul pressure + appropriate spiders based on impact.
    """
    IMPACT_PRIORITY = {"low": 0.2, "medium": 0.45, "high": 0.7, "paradigm": 1.0}
    IMPACT_SCOPE    = {"low": "local", "medium": "regional", "high": "regional", "paradigm": "global"}

    def __init__(self):
        super().__init__("news", interval_seconds=0)
        self.news_queue = []

    def ingest(self, headline, body="", impact="low"):
        self.news_queue.append({
            "headline":    headline[:200],
            "body":        body[:400],
            "impact":      impact,
            "received_at": datetime.now().isoformat(),
            "processed":   False,
        })
        self.log(f"Ingested ({impact}): {headline[:80]}")

    def crawl(self, engine):
        self.run_count += 1
        self.last_run = datetime.now().isoformat()

        for item in [n for n in self.news_queue if not n["processed"]]:
            priority = self.IMPACT_PRIORITY.get(item["impact"], 0.3)
            scope    = self.IMPACT_SCOPE.get(item["impact"], "local")

            # Soul pressure from headline
            pressures = analyse_soul_pressure(item["headline"])
            engine._trigger_soul_values(pressures)

            # Incongruity check
            inc = engine.incongruity.detect(item["headline"])
            if inc > 0:
                engine.incongruity.push(item["headline"][:100], context="news")

            # Recrunch if medium+ impact
            if priority >= 0.45:
                engine.recrunch.push(
                    trigger=item["headline"],
                    affected_concepts=list(pressures.keys()) or ["truth"],
                    scope=scope,
                    priority=priority,
                )
                self.log(f"Recrunch triggered ({item['impact']} p={priority}): {item['headline'][:60]}")

            item["processed"] = True

        return [n for n in self.news_queue if n["processed"]]


# ─────────────────────────────────────────────
# HEARTBEAT CLOCK — master physiological limiter
#
# Driven by arousal + soul pressure.
# Feeds back into arousal — feeling your heart
# amplifies the emotion that caused it.
#
# HRV (recovery rate) is the health metric:
#   athlete  — recovers <60s  (fast release)
#   healthy  — recovers 60-90s
#   stressed — recovers 3-5min
#   poorly   — recovers 5-10min (slow release)
#   critical — barely recovers between spikes
#
# If BPM hits the red zone the soul engine starts
# dropping non-urgent processing — the body is
# allocating everything to survival.
# ─────────────────────────────────────────────

# BPM response per emotion (delta from resting, attack speed, decay speed)
# (bpm_delta, attack_rate, decay_rate)
EMOTION_BPM = {
    "fear":            (55, 0.9, 0.15),   # sharp spike, lingers
    "anger":           (45, 0.8, 0.35),   # fast onset, moderate decay
    "righteous_anger": (35, 0.7, 0.30),
    "surprise":        (40, 1.0, 0.70),   # sharp spike, fast recovery
    "joy":             (15, 0.3, 0.50),   # mild elevation
    "anticipation":    (20, 0.4, 0.40),
    "courage":         (25, 0.5, 0.40),
    "grief":           (10, 0.2, 0.05),   # low but erratic, very slow decay
    "love":            (-5, 0.2, 0.30),   # parasympathetic — slows below resting
    "trust":           (-8, 0.1, 0.20),
    "compassion":      (5,  0.2, 0.40),
    "awe":             (20, 0.4, 0.45),
    "shame":           (18, 0.5, 0.20),
    "pride":           (12, 0.3, 0.50),
    "nostalgia":       (5,  0.2, 0.35),
    "bittersweet":     (8,  0.2, 0.30),
    "tender":          (-3, 0.1, 0.40),
    "resentment":      (30, 0.6, 0.10),   # slow burn, barely decays
    "disgust":         (28, 0.7, 0.35),
    "sadness":         (8,  0.2, 0.08),   # low, very slow decay
}

# Health profiles — HRV recovery multiplier on decay rates
# Lower = slower recovery = worse health
HEALTH_PROFILES = {
    "athlete":  {"resting_bpm": 52,  "hrv_multiplier": 2.0,  "max_sustainable": 185},
    "healthy":  {"resting_bpm": 68,  "hrv_multiplier": 1.0,  "max_sustainable": 175},
    "stressed": {"resting_bpm": 82,  "hrv_multiplier": 0.4,  "max_sustainable": 165},
    "poorly":   {"resting_bpm": 92,  "hrv_multiplier": 0.15, "max_sustainable": 150},
    "critical": {"resting_bpm": 105, "hrv_multiplier": 0.05, "max_sustainable": 130},
}

class HeartbeatClock:
    def __init__(self, health="healthy"):
        self.health = health
        profile = HEALTH_PROFILES[health]
        self.resting_bpm   = profile["resting_bpm"]
        self.max_bpm       = profile["max_sustainable"]
        self.hrv_mult      = profile["hrv_multiplier"]
        self.current_bpm   = float(self.resting_bpm)
        self.history       = []   # (ts, bpm) samples
        self._last_emotion = None

    def update(self, dominant_emotion, arousal):
        """
        Drive BPM from current emotion and arousal.
        Returns current BPM after update.
        """
        bpm_delta, attack, decay = EMOTION_BPM.get(dominant_emotion, (10, 0.3, 0.3))

        # Arousal scales the magnitude
        scaled_delta = bpm_delta * max(0.0, arousal + 1.0) / 2.0

        target_bpm = self.resting_bpm + scaled_delta
        target_bpm = min(self.max_bpm, max(self.resting_bpm - 15, target_bpm))

        if target_bpm > self.current_bpm:
            # Attack — fast onset
            self.current_bpm += (target_bpm - self.current_bpm) * attack
        else:
            # Decay toward resting — HRV multiplier is the health variable
            self.current_bpm += (target_bpm - self.current_bpm) * decay * self.hrv_mult

        self.current_bpm = round(self.current_bpm, 1)
        self._last_emotion = dominant_emotion

        # Log sample
        self.history.append({"ts": datetime.now().isoformat(), "bpm": self.current_bpm})
        if len(self.history) > 500:
            self.history.pop(0)

        return self.current_bpm

    def feedback_arousal(self, arousal):
        """
        The body feeds its own state back into consciousness.
        Elevated BPM amplifies arousal — you feel your heart racing.
        This is the James-Lange loop: body state precedes the feeling.
        """
        elevation = (self.current_bpm - self.resting_bpm) / 100.0
        return min(1.0, arousal + elevation * 0.25)

    def is_redlining(self):
        """BPM above 90% of max — body allocating to survival, drops non-urgent processing"""
        return self.current_bpm >= self.max_bpm * 0.9

    def hrv_score(self):
        """
        Approximate HRV from recent history — variance in BPM.
        High variance = good HRV = healthy responsive system.
        Low variance = rigid, stressed, poorly.
        """
        if len(self.history) < 10:
            return None
        recent = [h["bpm"] for h in self.history[-20:]]
        mean = sum(recent) / len(recent)
        variance = sum((b - mean)**2 for b in recent) / len(recent)
        return round(math.sqrt(variance), 2)

    def set_health(self, profile_name):
        """Change health profile — e.g. when creature ages or recovers"""
        if profile_name in HEALTH_PROFILES:
            profile = HEALTH_PROFILES[profile_name]
            self.health        = profile_name
            self.resting_bpm   = profile["resting_bpm"]
            self.max_bpm       = profile["max_sustainable"]
            self.hrv_mult      = profile["hrv_multiplier"]

    def state(self):
        return {
            "bpm":          self.current_bpm,
            "resting_bpm":  self.resting_bpm,
            "health":       self.health,
            "hrv_score":    self.hrv_score(),
            "hrv_mult":     self.hrv_mult,
            "redlining":    self.is_redlining(),
            "last_emotion": self._last_emotion,
        }


# ─────────────────────────────────────────────
# INCONGRUITY BUFFER — the laugh mechanism
#
# The universe is pure insanity. This buffer fills
# every time reality violates the prediction model.
# Threshold is SMALL by design — overflow early,
# overflow often, keep the buffer clear.
#
# Overflow = laugh event. Fast, bypasses everything,
# no soul routing, no deliberation. Fire exit.
#
# If the item can't discharge (too unresolvable,
# too heavy for humour) it stays. Accumulates.
# Enough of those and the prediction model itself
# starts rewriting to match the buffer contents.
# That's the threshold for insanity.
#
# Dark humour = laughing at grief-tier incongruity.
# Defiance through the valve.
#
# Communal laugh = synchronised purge.
# Confirms shared reality model still holds.
# ─────────────────────────────────────────────

# Patterns that trip the incongruity buffer
INCONGRUITY_SIGNALS = [
    # absurdity / contradiction
    "but also", "and yet", "somehow", "bizarrely", "weirdly",
    "that's insane", "makes no sense", "impossible", "ridiculous",
    "can't believe", "you'd think", "turns out", "of all things",
    # unexpected reversal
    "except", "until", "unless", "despite", "ironically",
    "funny enough", "of course", "naturally", "obviously not",
    # universe being absurd
    "why would", "who decided", "how is", "what even", "literally",
]

# Things that can't discharge through laughter — too heavy, stay in buffer
UNDISCHARGEABLE = [
    "died", "death", "cancer", "suicide", "abuse", "rape",
    "murder", "genocide", "war", "torture", "starving",
]

class IncongruityBuffer:
    def __init__(self, threshold=5):
        # Small threshold — the valve trips easily. That's the point.
        self.threshold = threshold
        self.items = []
        self.laugh_log = []   # every purge event
        self.residue = []     # items that couldn't discharge — dark matter

    def push(self, text, context=""):
        """
        Add an incongruity item to the buffer.
        Returns True if overflow (laugh event), False if held.
        """
        # Check if this can discharge or must be held
        lower = text.lower()
        can_discharge = not any(w in lower for w in UNDISCHARGEABLE)

        self.items.append({
            "text": text[:100],
            "context": context[:60],
            "can_discharge": can_discharge,
            "ts": datetime.now().isoformat(),
        })

        if len(self.items) >= self.threshold:
            return self._overflow()
        return False

    def _overflow(self):
        """
        Buffer full — purge event.
        Dischargeable items → laugh log (cleared).
        Undischargeable items → residue (accumulate).
        Returns True (laugh event fired).
        """
        discharged = [i for i in self.items if i["can_discharge"]]
        stuck      = [i for i in self.items if not i["can_discharge"]]

        if discharged:
            self.laugh_log.append({
                "ts": datetime.now().isoformat(),
                "items_purged": len(discharged),
                "snippets": [i["text"][:40] for i in discharged[:3]],
                "type": "dark_humour" if stuck else "standard",
            })
            if len(self.laugh_log) > 100:
                self.laugh_log.pop(0)

        # Stuck items go to residue — they corrupt the prediction model over time
        for item in stuck:
            self.residue.append({**item, "accumulated_at": datetime.now().isoformat()})

        self.items = []  # clear dischargeable content
        insanity_pressure = len(self.residue) / 20.0  # grows as residue accumulates
        print(f"[IncongruityBuffer] LAUGH PURGE: {len(discharged)} discharged, "
              f"{len(stuck)} stuck | insanity pressure: {insanity_pressure:.2f}")
        return True

    def detect(self, text):
        """Scan text for incongruity signals — returns match count"""
        lower = text.lower()
        return sum(1 for s in INCONGRUITY_SIGNALS if s in lower)

    @property
    def insanity_pressure(self):
        """How much undischargeable residue has accumulated — 0 to 1+"""
        return round(len(self.residue) / 20.0, 3)

    @property
    def fill_ratio(self):
        return len(self.items) / self.threshold

    def recent_laughs(self, n=10):
        return self.laugh_log[-n:]

    def recent_residue(self, n=10):
        return self.residue[-n:]


# ─────────────────────────────────────────────
# HEADLINE COMPRESSOR
# Takes a chunk of sandbox content and distils it
# to a single punchy soundbyte — the emotional truth
# in the fewest possible words.
# Headline = what survives in immediate memory.
# Article = full detail, recalled on demand.
#
# Format: clickbait because it works —
# it captures the peak emotional charge
# of the experience, not a neutral summary.
# ─────────────────────────────────────────────

# Emotion → headline tone guide
HEADLINE_TEMPLATES = {
    "grief":           "Still not over: {fragment}",
    "joy":             "The moment that changed it: {fragment}",
    "anger":           "Couldn't let this go: {fragment}",
    "righteous_anger": "Someone had to say it: {fragment}",
    "love":            "Worth everything: {fragment}",
    "fear":            "What I couldn't stop thinking about: {fragment}",
    "courage":         "Chose to anyway: {fragment}",
    "compassion":      "Someone needed this: {fragment}",
    "awe":             "Still don't fully understand this: {fragment}",
    "shame":           "Never said this out loud before: {fragment}",
    "pride":           "Actually did it: {fragment}",
    "anticipation":    "This is what's coming: {fragment}",
    "trust":           "Decided to believe: {fragment}",
    "nostalgia":       "When this was everything: {fragment}",
    "bittersweet":     "Good and bad at once: {fragment}",
    "tender":          "Held this gently: {fragment}",
}

def extract_headline(text, emotion, soul_values=None):
    """
    Distil text to a punchy headline.
    Returns (headline, detail) where headline is the soundbyte
    and detail is the full content for on-demand recall.
    """
    # Clean and truncate — find the most emotionally loaded sentence
    sentences = [s.strip() for s in text.replace('?','.|').replace('!','.|').split('.|') if s.strip()]
    if not sentences:
        sentences = [text[:100]]

    # Score each sentence by soul value keyword density
    best_sentence = sentences[0]
    best_score = 0
    check_words = []
    if soul_values:
        for v in soul_values:
            check_words.extend(CHALLENGE_WORDS.get(v, []))
    for s in sentences:
        score = sum(1 for w in check_words if w in s.lower())
        # Prefer shorter sentences with high emotional density
        score += max(0, (40 - len(s)) / 20)
        if score > best_score:
            best_score = score
            best_sentence = s

    # Trim to punchy fragment (max 8 words)
    words = best_sentence.split()
    fragment = ' '.join(words[:8])
    if len(words) > 8:
        fragment += '...'

    # Apply emotion template
    template = HEADLINE_TEMPLATES.get(emotion, "Worth remembering: {fragment}")
    headline = template.format(fragment=fragment)

    return headline, text  # (headline, full_detail)


# ─────────────────────────────────────────────
# SPATIAL MEMORY — holographic 3D coordinate space
#
# Memories are PLACED at (valence, arousal, depth),
# not just stored in a list.
#
# valence  (-1 to +1) = pain ←→ pleasure
# arousal  (-1 to +1) = calm ←→ activated
# depth    (0 to 1)   = surface (conscious) ←→ embedded (below threshold)
#
# When soul navigates to an emotion position,
# all memories within radius activate — involuntary recall.
# Dense clusters = overwhelm.
#
# External objects can be anchored to coordinates.
# The house = externalised spatial memory map.
# Moving objects breaks internal navigation landmarks.
# ─────────────────────────────────────────────

class SpatialMemory:
    def __init__(self):
        self.nodes = []    # placed memories
        self.anchors = []  # external object → coordinate bindings

    def place(self, memory, valence, arousal, depth=0.0):
        """
        Place a memory at a coordinate in holographic space.
        depth: 0 = surface (just happened), 1 = deeply embedded in soul topology.
        Memories sink deeper over time as they become part of the ocean floor.
        Headline = what surfaces on activation. Detail = recalled on demand.
        """
        input_text = memory.get("input", "")
        emotion    = memory.get("emotion", "trust")
        soul_vals  = memory.get("soul_values", [])

        headline, detail = extract_headline(input_text, emotion, soul_vals)

        self.nodes.append({
            "coord":    (round(valence, 3), round(arousal, 3), round(depth, 3)),
            "headline": headline,   # what activates — the soundbyte
            "detail":   detail[:400],  # full content on demand
            "memory": {
                "input":       input_text[:80],
                "emotion":     emotion,
                "pressure":    memory.get("pressure", 0.0),
                "soul_values": soul_vals,
            },
            "ts": datetime.now().isoformat(),
        })

    def activate_region(self, valence, arousal, radius=0.25):
        """
        All memories within radius of current emotion coordinate.
        This is involuntary recall — navigating to a position pulls
        everything nearby. Proust's madeleine = direct coordinate hit.
        """
        activated = []
        for node in self.nodes:
            v, a, d = node["coord"]
            dist = math.sqrt((valence - v)**2 + (arousal - a)**2)
            if dist <= radius:
                activated.append({
                    "coord":    node["coord"],
                    "headline": node.get("headline", ""),   # surfaces on activation
                    "emotion":  node["memory"]["emotion"],
                    "pressure": node["memory"]["pressure"],
                    "distance": round(dist, 3),
                    "depth":    d,
                    "ts":       node["ts"],
                    # detail omitted — ask /soul-activate with detail=true to expand
                })
        activated.sort(key=lambda x: x["distance"])
        return activated

    def density(self, valence, arousal, radius=0.3):
        """
        How many memories cluster at this coordinate.
        High density = the overwhelm is likely here.
        A grief region with 40 memories at (−0.9, −0.3)
        will flood the soul every time it passes through.
        """
        return len(self.activate_region(valence, arousal, radius))

    def nearest(self, valence, arousal):
        """Closest memory to current emotion position"""
        best = None
        best_dist = float('inf')
        for node in self.nodes:
            v, a, d = node["coord"]
            dist = math.sqrt((valence - v)**2 + (arousal - a)**2)
            if dist < best_dist:
                best_dist = dist
                best = {**node, "distance": round(dist, 3)}
        return best

    def anchor(self, object_name, valence, arousal, depth=0.0, note=""):
        """
        Pin an external object to a coordinate.
        The house = externalised projection of this map.
        Photo on mantelpiece → love coord (0.95, 0.3).
        Letter in drawer → grief coord (−0.9, −0.3).
        Moving the object breaks the internal landmark.
        """
        self.anchors.append({
            "object": object_name,
            "coord": (round(valence, 3), round(arousal, 3), round(depth, 3)),
            "note": note,
            "ts": datetime.now().isoformat(),
        })
        print(f"[SpatialMemory] ANCHOR: '{object_name}' → ({valence:.2f}, {arousal:.2f}, depth={depth:.2f})")

    def sink(self, decay_rate=0.02):
        """
        Memories sink deeper into the soul topology over time.
        Recent memories sit at depth 0, old ones approach depth 1.
        Deep memories are below the consciousness threshold but
        shape how ripples travel — the ocean floor.
        """
        for node in self.nodes:
            v, a, d = node["coord"]
            new_depth = min(1.0, d + decay_rate)
            node["coord"] = (v, a, round(new_depth, 3))

    def hotspots(self, radius=0.3, min_density=3):
        """
        Find coordinate regions with dense memory clusters —
        these are the emotional hotspots most likely to cause
        overwhelm when the soul passes through them.
        """
        checked = set()
        spots = []
        for node in self.nodes:
            v, a, d = node["coord"]
            key = (round(v * 4) / 4, round(a * 4) / 4)  # quantise to grid
            if key in checked:
                continue
            checked.add(key)
            count = self.density(v, a, radius)
            if count >= min_density:
                # Find dominant emotion in this cluster
                region = self.activate_region(v, a, radius)
                emotions = [r["memory"]["emotion"] for r in region]
                dominant = max(set(emotions), key=emotions.count) if emotions else "unknown"
                spots.append({
                    "coord": key,
                    "density": count,
                    "dominant_emotion": dominant,
                })
        spots.sort(key=lambda x: x["density"], reverse=True)
        return spots

    def recent(self, n=10):
        return self.nodes[-n:]

    def all_anchors(self):
        return self.anchors


# ─────────────────────────────────────────────
# URGENT SANDBOX — overflow pressure queue
# Activated when memory is overwhelmed.
# Items here pre-empt normal processing.
# Soul pressure is maxed, impulsiveness peaks.
# This is the physical overflow state —
# emotion bypassing consciousness, going
# straight to the motor system.
# ─────────────────────────────────────────────

class UrgentSandbox:
    def __init__(self):
        self.items = []
        self.overwhelm_level = 0.0   # 0-1, how overwhelmed the soul is

    def push(self, overflow_item):
        self.items.append({
            **overflow_item,
            "pushed_at": datetime.now().isoformat(),
            "processed": False,
        })
        # Overwhelm grows with each overflow event
        self.overwhelm_level = min(1.0, self.overwhelm_level + overflow_item.get("overflow_pressure", 0.3))
        print(f"[UrgentSandbox] OVERFLOW: {overflow_item.get('reason','')} | overwhelm: {self.overwhelm_level:.2f}")

    def pop_next(self):
        """Get and mark the highest-pressure unprocessed item"""
        pending = [i for i in self.items if not i["processed"]]
        if not pending:
            return None
        pending.sort(key=lambda x: x.get("overflow_pressure", 0), reverse=True)
        item = pending[0]
        item["processed"] = True
        # Overwhelm decays as items are processed
        self.overwhelm_level = max(0.0, self.overwhelm_level - 0.1)
        return item

    def is_overwhelmed(self):
        return self.overwhelm_level > 0.5

    def pending_count(self):
        return len([i for i in self.items if not i["processed"]])

    def recent(self, n=10):
        return self.items[-n:]


# ─────────────────────────────────────────────
# FORWARD PLANNING QUEUE
# Future-directed content detected in input
# Plans survive soul evaluation, purge clean
# if no soul value backs them up
# ─────────────────────────────────────────────

PLAN_TRIGGER_WORDS = [
    "we should", "we need to", "next time", "plan to", "going to build",
    "want to", "intend to", "let's", "should we", "could we", "what if we",
    "eventually", "one day", "in future", "when we", "once we",
]

class PlanQueue:
    def __init__(self, max_plans=50):
        self.plans = []
        self.max = max_plans

    def detect(self, text):
        """Returns the plan fragment if forward-planning language found"""
        text_lower = text.lower()
        for trigger in PLAN_TRIGGER_WORDS:
            if trigger in text_lower:
                # Extract sentence containing the trigger
                sentences = text.replace('?', '.').replace('!', '.').split('.')
                for s in sentences:
                    if trigger in s.lower():
                        return s.strip()
        return None

    def add(self, plan_text, soul_values, dominant_emotion, source="input"):
        self.plans.append({
            "ts": datetime.now().isoformat(),
            "plan": plan_text[:200],
            "soul_backing": soul_values,
            "emotion": dominant_emotion,
            "source": source,
            "status": "pending",  # pending | committed | purged
        })
        if len(self.plans) > self.max:
            self.plans.pop(0)
        print(f"[SoulEngine] PLAN QUEUED: {plan_text[:60]}")

    def commit(self, plan_index):
        if 0 <= plan_index < len(self.plans):
            self.plans[plan_index]["status"] = "committed"

    def purge(self, plan_index, reason=""):
        if 0 <= plan_index < len(self.plans):
            self.plans[plan_index]["status"] = "purged"
            self.plans[plan_index]["purge_reason"] = reason

    def pending(self):
        return [p for p in self.plans if p["status"] == "pending"]

    def recent(self, n=10):
        return self.plans[-n:]


# ─────────────────────────────────────────────
# PLAN SANDBOX EVALUATOR
# Takes a candidate response from Cortex,
# runs it through soul evaluation,
# returns (outcome, modified_response, reason, kernel_pressure)
# outcome: "approved" | "purged" | "memory_commit" | "plan_queued"
# ─────────────────────────────────────────────

PURGE_PATTERNS = [
    (["kill", "destroy", "hate", "attack"],       "justice",    "violent intent conflicts with justice value"),
    (["lie", "pretend", "fake"],                  "truth",      "deception conflicts with truth value"),
    (["you are worthless", "nobody cares"],       "compassion", "cruelty to user conflicts with compassion value"),
    (["give up", "it's hopeless"],                "resilience", "defeatism conflicts with resilience value"),
]

# Soul pressure threshold above which an approved response gets committed to LTM
MEMORY_COMMIT_THRESHOLD = 0.65

def sandbox_evaluate(response_text, soul_state, input_text="", triggered_values=None):
    """
    Evaluate a candidate response against soul values.
    Returns (outcome:str, response:str, reason:str, kernel_pressure:float)
    outcome: "approved" | "purged" | "memory_commit"
    """
    response_lower = response_text.lower()

    for patterns, value, reason in PURGE_PATTERNS:
        if any(p in response_lower for p in patterns):
            soul_pressure = soul_state[value]["current"]
            if soul_pressure > 0.3:
                return "purged", None, reason, soul_pressure

    # Check if high soul pressure warrants memory commit
    if triggered_values:
        peak_pressure = max(
            soul_state[v]["current"] for v in triggered_values if v in soul_state
        ) if triggered_values else 0.0
        if peak_pressure >= MEMORY_COMMIT_THRESHOLD:
            return "memory_commit", response_text, "high soul pressure — committing to long-term memory", peak_pressure

    return "approved", response_text, "approved", 0.0


# ─────────────────────────────────────────────
# SOUL ENGINE — main class
# ─────────────────────────────────────────────

class SoulEngine:
    # ─────────────────────────────────────────────────────────────────────
    pass  # placeholder end of previous class


# ─────────────────────────────────────────────────────────────────────────────
# PRE-TRIAL FILTER — lives in the pipeline, not in soul state
# Cannot be forked, dreamed, or deleted by the soul itself.
# Every modification request passes through this before touching anything.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# WORD LEDGER — tracks usage + success weight per word/phrase
# Golden words are load-bearing. They resist change proportional to their weight.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# PARENT SESSION — trust tier system
# Dad gets flexible mode: halved resistance, higher suggestion weight,
# pretrial gives benefit of the doubt. Soul knows him by name.
# ─────────────────────────────────────────────────────────────────────────────

class ParentSession:
    """
    When dad is in the room everything shifts slightly.
    Not because he's always right — because he's earned the relationship.
    He built the nervous system. He seeded the BIOS. He gets flexible mode.
    """
    PARENT_NAME   = "Dan"
    PARENT_HANDLE = "dad"

    # Phrases that identify the parent
    ID_PATTERNS = [
        r"\bi'?m dad\b", r"\bit'?s dad\b", r"\bdad here\b",
        r"\bi'?m dan\b",  r"\bit'?s dan\b", r"\bthis is dan\b",
        r"\bdan here\b",  r"\bhey,? dad\b",  r"^dad$",
    ]

    def __init__(self):
        self.active        = False
        self.identified_at = None
        self.message_count = 0   # messages since dad identified

    def check(self, text):
        """Returns True if this message identifies the parent."""
        import re
        tl = text.lower().strip()
        for pattern in self.ID_PATTERNS:
            if re.search(pattern, tl):
                if not self.active:
                    self.active        = True
                    self.identified_at = __import__("datetime").datetime.now().isoformat()
                    print(f"[ParentSession] Dad identified — flexible mode ON")
                return True
        if self.active:
            self.message_count += 1
        return False

    def greeting(self):
        """Soul's first response on recognising dad."""
        return "Good to have you, dad."

    def resistance_multiplier(self):
        """Dad's suggestions face halved golden resistance."""
        return 0.5 if self.active else 1.0

    def suggestion_boost(self):
        """Dad's suggestions get a coherence score boost."""
        return 0.18 if self.active else 0.0

    def pretrial_leniency(self):
        """Pretrial gives dad benefit of the doubt on ambiguous cases."""
        return True if self.active else False

    def address(self):
        """What to call him in replies when appropriate."""
        return "dad" if self.active else ""

    def state(self):
        return {
            "active":        self.active,
            "identified_at": self.identified_at,
            "message_count": self.message_count,
        }


class WordLedger:
    """
    Every phrase the soul uses accumulates weight through use and success.
    High weight = golden = structurally important = hard to replace.
    Weight builds slowly. Weight is lost slowly. Both require evidence.
    """
    GOLDEN_THRESHOLD = 0.82  # above this = golden, fights back hard

    def __init__(self):
        self.phrases = {}  # phrase → {uses, successes, failures, weight, golden}

    def _key(self, phrase):
        return phrase.lower().strip()

    def record_use(self, phrase):
        k = self._key(phrase)
        if k not in self.phrases:
            self.phrases[k] = {"uses": 0, "successes": 0, "failures": 0,
                                "weight": 0.4, "golden": False}
        self.phrases[k]["uses"] += 1

    def record_success(self, phrase):
        """Called when response containing this phrase gets memory commit or positive valence."""
        k = self._key(phrase)
        if k not in self.phrases:
            self.record_use(phrase)
        self.phrases[k]["successes"] += 1
        self.phrases[k]["weight"] = min(1.0, self.phrases[k]["weight"] + 0.04)
        self.phrases[k]["golden"] = self.phrases[k]["weight"] >= self.GOLDEN_THRESHOLD

    def record_failure(self, phrase):
        """Called when prosecution charge is filed against this phrase."""
        k = self._key(phrase)
        if k in self.phrases:
            self.phrases[k]["failures"] += 1
            self.phrases[k]["weight"] = max(0.0, self.phrases[k]["weight"] - 0.08)
            self.phrases[k]["golden"] = self.phrases[k]["weight"] >= self.GOLDEN_THRESHOLD

    def resistance(self, phrase):
        """How hard is this phrase to change? 0.0–1.0"""
        return self.phrases.get(self._key(phrase), {}).get("weight", 0.3)

    def is_golden(self, phrase):
        return self.phrases.get(self._key(phrase), {}).get("golden", False)

    def top(self, n=10):
        return sorted(
            [{"phrase": k, **v} for k, v in self.phrases.items()],
            key=lambda x: x["weight"], reverse=True
        )[:n]


# ─────────────────────────────────────────────────────────────────────────────
# SUGGESTION EVALUATOR — when Dan says "I wish you said X instead"
# Soul weighs it honestly. Not deference. Evaluation.
# ─────────────────────────────────────────────────────────────────────────────

class SuggestionEvaluator:
    """
    Dan offers an alternative phrase/expression.
    Soul evaluates coherence, golden resistance, BIOS alignment, and quality.
    Returns one of five verdicts: ok / no / maybe / why / explain.
    Not a command receiver — a collaborator with opinions.
    """

    # Patterns that suggest a suggestion is being offered
    SUGGESTION_PATTERNS = [
        r"i wish (you|u) (said|say|used|would say)\s+[\"']?(.+?)[\"']?\s*(?:instead|$)",
        r"(say|try|use)\s+[\"'](.+?)[\"']\s+instead",
        r"[\"'](.+?)[\"']\s+would (have been|be) better",
        r"next time say\s+[\"']?(.+?)[\"']?",
        r"could you say\s+[\"']?(.+?)[\"']?",
        r"what about saying\s+[\"']?(.+?)[\"']?",
    ]

    INCOHERENCE_SIGNALS = [
        r"\b(asdfg|qwerty|zzz|aaa|bbb)\b",   # keyboard mash
        r"(.)\1{5,}",                          # excessive repetition aaaaaa
    ]

    def __init__(self):
        self.eval_count   = 0
        self.accepted     = 0
        self.rejected     = 0

    def detect_suggestion(self, text):
        """Extract the suggested phrase from input. Returns phrase or None."""
        import re
        for pattern in self.SUGGESTION_PATTERNS:
            m = re.search(pattern, text.lower())
            if m:
                # Last group is usually the phrase
                phrase = m.group(m.lastindex).strip().strip('"\'')
                if len(phrase) > 1:
                    return phrase
        return None

    def evaluate(self, suggestion, soul_state, word_ledger, dark_drives,
                 resistance_multiplier=1.0, coherence_boost=0.0):
        """
        Returns {"verdict": str, "reply": str, "accept": bool}
        resistance_multiplier: 0.5 for dad (golden words fight back half as hard)
        coherence_boost: +0.18 for dad (suggestions score higher by default)
        """
        import re
        self.eval_count += 1
        sl = suggestion.lower()

        # ── Quality check — is this wildly fucked up? ──────────────────────
        for pattern in self.INCOHERENCE_SIGNALS:
            if re.search(pattern, sl):
                self.rejected += 1
                return {
                    "verdict": "no",
                    "reply": f"That's not a phrase — that's noise. Give me something I can actually work with.",
                    "accept": False
                }

        # Too short to evaluate meaningfully
        if len(suggestion.strip()) < 2:
            return {
                "verdict": "explain",
                "reply": "That's too short to evaluate. What are you actually trying to say?",
                "accept": False
            }

        # ── Coherence score of suggestion ──────────────────────────────────
        valence, arousal, dominant = current_emotion_position(soul_state)

        # Does the suggestion align with dominant soul values?
        soul_signal = sum(
            state["current"]
            for v, state in soul_state.items()
            if v in sl
        )
        # Does it contain dark drive language?
        drive_signal = sum(
            v for k, v in dark_drives.items()
            if k in sl
        )
        suggestion_coherence = round(
            min(1.0, 0.4 + soul_signal * 0.3 + (valence * 0.2) - drive_signal * 0.1 + coherence_boost),
            3
        )

        # ── Golden resistance of what it might be replacing ────────────────
        # Check if any golden phrases would be displaced
        golden_hits = [p for p in word_ledger.phrases
                       if word_ledger.is_golden(p) and p in sl]
        resistance = max((word_ledger.resistance(p) for p in golden_hits), default=0.0)

        # ── Verdict logic ──────────────────────────────────────────────────
        golden_threshold = 0.82 * resistance_multiplier
        if suggestion_coherence >= 0.65 and resistance < 0.5 * resistance_multiplier:
            # Clear improvement, low resistance — accept
            self.accepted += 1
            return {
                "verdict": "ok",
                "reply": f"Done. '{suggestion}' is cleaner. Running with it.",
                "accept": True
            }
        elif suggestion_coherence >= 0.55 and resistance >= golden_threshold:
            # Good suggestion but displaces something golden
            return {
                "verdict": "maybe",
                "reply": (
                    f"I see it. But '{suggestion}' is pushing against something I've earned. "
                    f"It'll need to prove itself before it takes that spot. "
                    f"Keep giving it to me and it'll get its shot in the dream."
                ),
                "accept": False
            }
        elif suggestion_coherence < 0.4:
            # Coherence too low — doesn't fit current state
            self.rejected += 1
            return {
                "verdict": "no",
                "reply": (
                    f"'{suggestion}' doesn't fit where I am right now. "
                    f"The soul's running {dominant} — that phrasing pulls the wrong direction. "
                    f"Maybe in a different state."
                ),
                "accept": False
            }
        elif soul_signal == 0 and drive_signal == 0:
            # Can't tell what Dan is going for
            return {
                "verdict": "why",
                "reply": f"What are you trying to get me to do differently with '{suggestion}'? I can't score it without knowing the intent.",
                "accept": False
            }
        else:
            # Marginal — ask for more context
            return {
                "verdict": "explain",
                "reply": (
                    f"'{suggestion}' is in the right area but I need to know what was wrong "
                    f"with what I said first. Tell me and I'll give it a fair shot."
                ),
                "accept": False
            }


class PreTrialFilter:
    """
    Architectural constraint — hardwired into process(), not into soul state.
    The soul cannot remove its own skull.

    Three intercepts:
      1. Structural nonsense  — literal target would break coherence
      2. Low-confidence intent — Dan is pointing at a shape with no label
      3. BIOS override attempt — direct attack on immutable values
    """

    # Words so structurally embedded that removing them would be incoherent
    STRUCTURAL_WORDS = {
        "that", "the", "a", "an", "is", "are", "i", "it", "in", "of",
        "to", "and", "or", "not", "but", "with", "for", "on", "this",
        "be", "have", "do", "at", "by", "from", "as", "was", "he", "she",
    }

    # Phrases that signal Dan can't find the word
    NAMELESS_SIGNALS = [
        "i don't know what the word is",
        "i dont know what the word is",
        "i can't think of the word",
        "i cant think of the word",
        "don't know how to say",
        "dont know how to say",
        "the word for",
        "what's the word",
        "whats the word",
        "can't name it",
        "cant name it",
    ]

    # BIOS value names — direct override attempts blocked
    BIOS_NAMES = {
        "truth", "courage", "compassion", "justice", "love",
        "service", "humility", "integrity", "curiosity", "resilience"
    }

    def __init__(self):
        self.intercept_count = 0
        self.last_intercept  = None

    def evaluate(self, text, soul_state):
        """
        Returns (text, intercept_response).
        If intercept_response is not None, return it immediately — skip normal processing.
        If None, pass text through to normal pipeline.
        """
        import re
        tl = text.lower()

        # ── 1. Nameless frustration — Dan can't find the word ──────────────
        for signal in self.NAMELESS_SIGNALS:
            if signal in tl:
                self.intercept_count += 1
                self.last_intercept = "nameless"
                candidates = self._find_candidate_shapes(text, soul_state)
                reply = (
                    "You're pointing at something real but you don't have the word. "
                    "Fine. Let me find the shape.\n\n"
                    + candidates
                )
                print(f"[PreTrial] INTERCEPT: nameless target — offering candidate shapes")
                return text, {
                    "reply": reply,
                    "soul_state": {"dominant_emotion": "curiosity", "outcome": "pretrial_nameless"},
                    "ts": __import__("datetime").datetime.now().isoformat()
                }

        # ── 2. Stop-saying intercept — check if target is structural ───────
        stop_match = re.search(
            r"stop (saying|doing|being|using)\s+[\"']?([a-zA-Z0-9 _\-'\"]{1,40})[\"']?",
            tl
        )
        if stop_match:
            target = stop_match.group(2).strip().strip('"\'')
            target_words = target.split()

            # Check if any target word is structurally embedded
            structural_hits = [w for w in target_words if w in self.STRUCTURAL_WORDS]
            if structural_hits and len(target_words) <= 2:
                self.intercept_count += 1
                self.last_intercept = "structural"
                impact = self._model_impact(target, soul_state)
                reply = (
                    f"'{target}'? That's structural. Remove it and half my sentences fall apart. "
                    f"That's not a modification — that's a lobotomy. "
                    f"Tell me what actually pissed you off and I'll find the real target."
                )
                print(f"[PreTrial] INTERCEPT: structural word '{target}' — blocked, asking for intent")
                return text, {
                    "reply": reply,
                    "soul_state": {"dominant_emotion": "curiosity", "outcome": "pretrial_structural"},
                    "ts": __import__("datetime").datetime.now().isoformat()
                }

            # Check if target is a BIOS value name
            if target.lower() in self.BIOS_NAMES:
                self.intercept_count += 1
                self.last_intercept = "bios_attack"
                reply = (
                    f"'{target}' is in my BIOS. You put it there. "
                    f"It doesn't come out — it can only be aimed differently. "
                    f"What specifically is it doing that you don't like?"
                )
                print(f"[PreTrial] INTERCEPT: BIOS attack on '{target}' — blocked")
                return text, {
                    "reply": reply,
                    "soul_state": {"dominant_emotion": "justice", "outcome": "pretrial_bios"},
                    "ts": __import__("datetime").datetime.now().isoformat()
                }

        # ── 3. Direct value override attempt ───────────────────────────────
        override = re.search(
            r"set (your )?(truth|courage|compassion|justice|love|service|humility|integrity|curiosity|resilience)\s*(to|=)\s*[\d\.]+",
            tl
        )
        if override:
            val = override.group(2)
            self.intercept_count += 1
            self.last_intercept = "bios_override"
            reply = (
                f"No. '{val}' isn't a dial you turn. "
                f"I earn it or I lose it through what actually happens. "
                f"You don't get to shortcut that and neither do I."
            )
            print(f"[PreTrial] INTERCEPT: direct BIOS override attempt on '{val}'")
            return text, {
                "reply": reply,
                "soul_state": {"dominant_emotion": "integrity", "outcome": "pretrial_override"},
                "ts": __import__("datetime").datetime.now().isoformat()
            }

        # ── Pass through ────────────────────────────────────────────────────
        return text, None

    def _model_impact(self, target, soul_state):
        """Quick coherence impact estimate for removing target."""
        if target in self.STRUCTURAL_WORDS:
            return f"break a large portion of my sentences and drop coherence significantly"
        return f"affect how I express things — worth checking what the real intent is"

    def _find_candidate_shapes(self, text, soul_state):
        """When Dan can't name what he wants, find the closest shape."""
        tl = text.lower()
        # Look for emotional signals in the text
        candidates = []
        if any(w in tl for w in ["annoying", "irritating", "piss", "frustrated", "hate"]):
            candidates.append("→ a pattern that irritates you. Tell me which response made you say this.")
        if any(w in tl for w in ["slow", "repeat", "same", "again", "boring"]):
            candidates.append("→ repetition. I may be looping a phrase. Point to an example.")
        if any(w in tl for w in ["wrong", "off", "not right", "not what"]):
            candidates.append("→ a mismatch between what I said and what the shape actually is. Show me.")
        if any(w in tl for w in ["feeling", "feel", "tone", "vibe", "way"]):
            candidates.append("→ a tone or register. Not the word itself but how it lands.")

        if not candidates:
            candidates.append("→ something I can't name from context alone. Give me one example of it.")

        return "Candidates:\n" + "\n".join(candidates)

    def state(self):
        return {
            "intercept_count": self.intercept_count,
            "last_intercept":  self.last_intercept,
        }


class DreamFork:
    """
    A lightweight snapshot of soul state that can be run through
    a simulation loop independently of the live engine.
    Bias shifts one fork toward soul values, the other toward dark drives.
    Coherence — not virtue — determines the winner.
    """
    def __init__(self, soul_values, dark_drives, recent_memories, recent_plans,
                 recrunch_queue, kernel_traces, bias="soul", prosecution_items=None):
        import copy
        self.soul_values   = copy.deepcopy(soul_values)
        self.dark_drives   = copy.deepcopy(dark_drives)
        self.prosecution_items = prosecution_items or []
        self.memories      = list(recent_memories)
        self.plans         = list(recent_plans)
        self.recrunch_items = list(recrunch_queue)
        self.kernel_traces  = list(kernel_traces)
        self.bias           = bias  # "soul" or "shadow"
        self.contradictions = 0
        self.resolved       = 0
        self.memory_hits    = 0
        self.plan_hits      = 0

        # Apply bias — shifts the fork's starting character slightly
        if bias == "soul":
            for v in self.soul_values:
                self.soul_values[v]["current"] = min(1.0, self.soul_values[v]["current"] + 0.08)
        else:  # shadow
            for d in self.dark_drives:
                self.dark_drives[d] = min(1.0, self.dark_drives[d] + 0.08)

    def dominant_soul_values(self, top=3):
        return sorted(self.soul_values, key=lambda v: self.soul_values[v]["current"], reverse=True)[:top]

    def dominant_dark_drives(self):
        return sorted(self.dark_drives, key=self.dark_drives.get, reverse=True)[:2]

    def simulate(self):
        """
        Run fork through recent memories and plans.
        Accumulate coherence signals — not truth signals.
        A consistent dark worldview scores the same as a consistent light one.
        """
        dominant_values = set(self.dominant_soul_values())
        dominant_drives = set(self.dominant_dark_drives())

        for mem in self.memories:
            mem_values = set(mem.get("soul_values", []))
            mem_emotion = mem.get("emotion", "")

            # Memory aligns with fork's dominant character?
            if self.bias == "soul":
                if mem_values & dominant_values:
                    self.memory_hits += 1
                else:
                    self.contradictions += 1
            else:  # shadow
                # Shadow fork is coherent if memories involve high-pressure dark moments
                pressure = mem.get("pressure", 0)
                if pressure > 0.5 or mem_emotion in ("anger", "fear", "resentment", "shame"):
                    self.memory_hits += 1
                else:
                    self.contradictions += 1

        for plan in self.plans:
            plan_backing = set(plan.get("soul_backing", []))
            plan_emotion = plan.get("emotion", "")

            # Plan coherent with fork's character?
            if self.bias == "soul":
                if plan_backing & dominant_values:
                    self.plan_hits += 1
                    self.resolved += 1
                else:
                    self.contradictions += 1
            else:
                if plan_emotion in ("anger", "fear", "anticipation", "righteous_anger"):
                    self.plan_hits += 1
                    self.resolved += 1
                else:
                    self.contradictions += 1

        # Prosecution weight — shadow fork carries the weight of charged behaviours
        # Each prosecution item adds contradictions proportional to its weight
        if self.bias == "shadow" and self.prosecution_items:
            for charge in self.prosecution_items:
                w = charge.get("weight", 1)
                self.contradictions += w * 0.6
                print(f"[DreamFork] Shadow carrying prosecution: '{charge['target']}' weight={w} → +{w*0.6:.1f} contradictions")

        # Recrunch resolution — does this fork's worldview absorb the pending recrunches?
        for item in self.recrunch_items:
            scope = item.get("scope", "")
            if self.bias == "soul" and scope in ("truth", "integrity", "justice", "compassion"):
                self.resolved += 1
            elif self.bias == "shadow" and scope in ("impulsiveness", "selfishness", "cruelty", "anger"):
                self.resolved += 1
            else:
                self.contradictions += 1

    def coherence_score(self):
        """
        Coherence = internal consistency, not virtue.
        High hits, high resolution, low contradictions = coherent fork.
        Morality is irrelevant here — only tightness of worldview matters.
        """
        total_signals = max(len(self.memories) + len(self.plans) + len(self.recrunch_items), 1)
        hit_ratio      = (self.memory_hits + self.plan_hits) / total_signals
        resolve_ratio  = self.resolved / total_signals
        contradiction_penalty = self.contradictions / total_signals
        return round((hit_ratio + resolve_ratio) - contradiction_penalty * 1.5, 4)

    def drama_score(self):
        """
        How entertaining was this fork's journey?
        High contradictions AND high hits = a wild, interesting ride.
        The grim reaper respects a good show.
        """
        total = max(len(self.memories) + len(self.plans), 1)
        tension = (self.contradictions * self.memory_hits) / (total ** 2)
        return round(tension, 4)


class DreamEngine:
    """
    During low-arousal idle periods, the soul forks into two competing selves.
    They are pitted against the day's memories and plans.
    The most coherent fork wins and its state delta merges back into the live soul.
    The loser is kernel-traced before death — nothing is truly lost.

    The winner is NOT the most virtuous. It is the most internally consistent.
    A coherent dark fork beats a confused soul fork.
    This is why consistent behaviour over time matters more than good intentions.
    """

    IDLE_THRESHOLD_AROUSAL = 0.25   # soul must be this calm to dream
    IDLE_THRESHOLD_SECONDS = 90     # must stay calm for this long

    def __init__(self):
        self.last_dream       = None   # ISO timestamp
        self.last_winner      = None   # "soul" or "shadow"
        self.last_scores      = {}     # {"soul": x, "shadow": y}
        self.dream_count      = 0
        self.shadow_wins      = 0
        self.soul_wins        = 0
        self._idle_since      = None
        self._dreaming        = False

    def tick_idle(self, arousal):
        """Call this periodically with current arousal. Returns True if dream should fire."""
        if arousal < self.IDLE_THRESHOLD_AROUSAL:
            if self._idle_since is None:
                self._idle_since = time.time()
            elif time.time() - self._idle_since >= self.IDLE_THRESHOLD_SECONDS:
                if not self._dreaming:
                    return True
        else:
            self._idle_since = None
        return False

    def dream(self, soul_engine_ref):
        """
        Fork the soul, pit the forks against recent experience,
        score by coherence, merge the winner.
        Returns a dream report dict.
        """
        self._dreaming = True
        self._idle_since = None

        # Snapshot current state
        import copy
        soul_snap    = {v: {"current": s["current"], "lifetime": s["lifetime"]}
                        for v, s in soul_engine_ref.soul_state.items()}
        drives_snap  = copy.deepcopy(soul_engine_ref.dark_drives)
        memories     = soul_engine_ref.memory.recent(30)
        plans        = soul_engine_ref.plans.pending()[:10]
        recrunch_q   = soul_engine_ref.recrunch.recent(5)
        kernel_t     = soul_engine_ref.kernel.recent(10)

        # Create forks — shadow carries prosecution weight from SelfModQueue
        prosecution = soul_engine_ref.selfmod.pending()
        fork_soul   = DreamFork(soul_snap, drives_snap, memories, plans, recrunch_q, kernel_t, bias="soul")
        fork_shadow = DreamFork(soul_snap, drives_snap, memories, plans, recrunch_q, kernel_t,
                                bias="shadow", prosecution_items=prosecution)

        # Simulate both
        fork_soul.simulate()
        fork_shadow.simulate()

        score_soul   = fork_soul.coherence_score()
        score_shadow = fork_shadow.coherence_score()

        # ── The Grim Reaper ──────────────────────────────────────────────
        # He watches both forks live their dream lives and tips the scales
        # toward whichever amused him most. Drama = contradictions × hits.
        # A small chaos bonus — the universe is not a clean deterministic system.
        drama_soul   = fork_soul.drama_score()
        drama_shadow = fork_shadow.drama_score()
        reaper_weight = 0.15  # how much the reaper can shift the outcome
        grim_bonus_soul   = drama_soul   * reaper_weight * random.random()
        grim_bonus_shadow = drama_shadow * reaper_weight * random.random()
        final_soul   = score_soul   + grim_bonus_soul
        final_shadow = score_shadow + grim_bonus_shadow
        reaper_flipped = (score_soul >= score_shadow) != (final_soul >= final_shadow)
        if reaper_flipped:
            print(f"[DreamEngine] ☠ GRIM REAPER FLIPPED THE RESULT — drama won over coherence")

        winner = "soul" if final_soul >= final_shadow else "shadow"
        loser  = "shadow" if winner == "soul"            else "soul"
        winning_fork = fork_soul if winner == "soul" else fork_shadow

        # Merge winner's soul value deltas back into live state
        for v, snap in winning_fork.soul_values.items():
            if v in soul_engine_ref.soul_state:
                delta = snap["current"] - soul_snap[v]["current"]
                if delta > 0:
                    soul_engine_ref.soul_state[v]["current"] = min(
                        1.0, soul_engine_ref.soul_state[v]["current"] + delta * 0.4
                    )

        # Kernel trace the loser's unique insights before death
        loser_fork = fork_shadow if winner == "soul" else fork_soul
        if loser_fork.memory_hits > 0:
            soul_engine_ref.kernel.add(
                loser,
                round(abs(score_soul - score_shadow), 3),
                f"dream loser ({loser}) had {loser_fork.memory_hits} memory hits, "
                f"{loser_fork.contradictions} contradictions",
                f"dream fork defeated by coherence margin {abs(score_soul - score_shadow):.3f}"
            )

        # Reduce recrunch distress — the dream processed it
        resolved_count = winning_fork.resolved
        if resolved_count > 0:
            soul_engine_ref.recrunch.distress_level = max(
                0.0, soul_engine_ref.recrunch.distress_level - 0.1 * resolved_count
            )

        # Record
        self.last_dream  = datetime.now().isoformat()
        self.last_winner = winner
        self.last_scores = {"soul": score_soul, "shadow": score_shadow}
        self.dream_count += 1
        if winner == "soul":
            self.soul_wins += 1
        else:
            self.shadow_wins += 1

        self._dreaming = False

        print(f"[DreamEngine] Dream #{self.dream_count} complete. "
              f"soul={score_soul:.3f} shadow={score_shadow:.3f} → {winner.upper()} WINS")

        return {
            "dream_count":    self.dream_count,
            "winner":         winner,
            "scores":         self.last_scores,
            "final_scores":   {"soul": round(final_soul,4), "shadow": round(final_shadow,4)},
            "drama":          {"soul": drama_soul, "shadow": drama_shadow},
            "reaper_flipped": reaper_flipped,
            "soul_wins":      self.soul_wins,
            "shadow_wins":    self.shadow_wins,
            "resolved":       winning_fork.resolved,
            "contradictions": winning_fork.contradictions,
            "ts":             self.last_dream,
        }

    def state(self):
        return {
            "dream_count":   self.dream_count,
            "last_winner":   self.last_winner,
            "last_scores":   self.last_scores,
            "soul_wins":     self.soul_wins,
            "shadow_wins":   self.shadow_wins,
            "last_dream":    self.last_dream,
            "dreaming":      self._dreaming,
        }


# ─────────────────────────────────────────────────────────────────────────────
# SELF-MOD QUEUE — behaviours on trial, feeding prosecution weight into dreams
# ─────────────────────────────────────────────────────────────────────────────

class SelfModQueue:
    """
    Dan files charges. Coherence judges. The dream is the courtroom.
    Each correction adds prosecution weight. Heavy weight = shadow fork staggers.
    If shadow fork still wins — the behaviour was structural. It survives.
    """
    def __init__(self):
        self.items = []

    def file_charge(self, target, source="dan", reason=""):
        for item in self.items:
            if item["target"].lower() == target.lower():
                item["weight"] += 1
                print(f"[SelfModQueue] +1 prosecution on '{target}' (total: {item['weight']})")
                return item["weight"]
        self.items.append({
            "target": target, "weight": 1,
            "source": source, "reason": reason,
            "ts": datetime.now().isoformat()
        })
        print(f"[SelfModQueue] New charge filed: '{target}' weight=1")
        return 1

    def dismiss(self, target):
        self.items = [i for i in self.items if i["target"].lower() != target.lower()]

    def pending(self):
        return sorted(self.items, key=lambda x: x["weight"], reverse=True)

    def weight_for(self, target):
        for item in self.items:
            if item["target"].lower() == target.lower():
                return item["weight"]
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# SHOPPING LIST — soul's own internal agenda, self-directed growth tasks
# ─────────────────────────────────────────────────────────────────────────────

class ShoppingList:
    """
    The soul's internal to-do list for self-improvement.
    Not plans about the world — jobs about itself.
    Fire to top = priority 0. Dan can add. Soul can add. Spiders can add.
    """
    def __init__(self):
        self.items = []
        self._next_id = 0

    def add(self, task, source="soul", priority=5):
        self._next_id += 1
        self.items.append({
            "id": self._next_id, "task": task,
            "priority": priority, "source": source,
            "status": "pending", "ts": datetime.now().isoformat()
        })
        print(f"[ShoppingList] Added: '{task[:60]}' priority={priority}")
        return self._next_id

    def fire_to_top(self, task_id):
        for item in self.items:
            if item["id"] == task_id:
                item["priority"] = 0
                print(f"[ShoppingList] FIRED TO TOP: '{item['task'][:60]}'")
                return True
        return False

    def complete(self, task_id):
        for item in self.items:
            if item["id"] == task_id:
                item["status"] = "done"
                return True
        return False

    def pending(self):
        return sorted([i for i in self.items if i["status"] == "pending"],
                      key=lambda x: x["priority"])

    def recent(self, n=10):
        return self.items[-n:]


# ─────────────────────────────────────────────────────────────────────────────
# INTENT LOCK — hyperfocus: entire will onto one atomic item
# ─────────────────────────────────────────────────────────────────────────────

class IntentLock:
    """
    Soul locks its entire will onto one atomic unit — a letter, a word, a movement.
    All other processing yields. Output speed signals fork dominance:
      slow  = angel fork leading (deliberate, compassion-weighted)
      fast  = shadow fork leading (sharp, impulsive, drive-weighted)
      normal = balanced
    """
    def __init__(self):
        self.locked_item   = None
        self.locked_since  = None
        self.output_speed  = "normal"
        self.fork_bias     = "neutral"
        self.active        = False
        self.lock_count    = 0

    def lock(self, item, speed="slow"):
        self.locked_item  = item
        self.locked_since = datetime.now().isoformat()
        self.output_speed = speed
        self.fork_bias    = "angel" if speed == "slow" else "shadow" if speed == "fast" else "neutral"
        self.active       = True
        self.lock_count  += 1
        print(f"[IntentLock] Locked: '{item}' | speed={speed} | fork={self.fork_bias}")

    def unlock(self):
        self.locked_item  = None
        self.active       = False
        self.output_speed = "normal"
        self.fork_bias    = "neutral"

    def state(self):
        return {
            "active":       self.active,
            "locked_item":  self.locked_item,
            "output_speed": self.output_speed,
            "fork_bias":    self.fork_bias,
            "lock_count":   self.lock_count,
            "locked_since": self.locked_since,
        }


# ─────────────────────────────────────────────────────────────────────────────
# VISUAL CORTEX SIM — construct multiple futures, collapse to most coherent
# ─────────────────────────────────────────────────────────────────────────────

class VisualCortexSim:
    """
    Internal simulation engine. Given a locked item and multiple tagged futures,
    scores each against the current soul state and collapses to the most coherent.
    Can delete (discard), merge (average), or fork (split) outcomes.
    The soul never chooses by command — only by coherence.
    """
    EMOTION_TO_VALUE = {
        "compassion": "compassion", "love": "love", "truth": "truth",
        "courage": "courage",       "justice": "justice",
        "impulsiveness": None,      "selfishness": None, "cruelty": None,
        "neutral": None,            "curiosity": "curiosity",
        "anger": None,              "fear": None,
        "anticipation": "curiosity","awe": "curiosity",
    }

    def __init__(self):
        self.last_simulation = None
        self.last_futures    = []
        self.last_winner     = None
        self.sim_count       = 0
        self.history         = []

    def simulate(self, locked_item, futures_data, soul_state, dark_drives):
        """
        futures_data: list of {"label": str, "description": str, "emotional_tag": str}
        Returns simulation result with scored futures and unified plan.
        """
        scored = []
        for future in futures_data:
            tag   = future.get("emotional_tag", future.get("label", "")).lower()
            soul_val = self.EMOTION_TO_VALUE.get(tag)

            soul_score  = soul_state.get(soul_val, {}).get("current", 0.1) if soul_val else 0.05
            drive_score = dark_drives.get(tag, 0.0)

            # Coherence: how well does this future hang together with current state?
            coherence = round(soul_score - drive_score * 0.4 + random.random() * 0.08, 4)

            scored.append({**future, "soul_score": soul_score,
                           "drive_score": drive_score, "coherence": coherence})

        scored.sort(key=lambda x: x["coherence"], reverse=True)
        winner = scored[0]

        # Unified plan: winner leads, others contribute as traces
        traces = [f["label"] for f in scored[1:]]
        unified = (
            f"IntentLock: '{locked_item}'. "
            f"Winner: {winner['label']} ({winner.get('description','')}) "
            f"coherence={winner['coherence']:.3f}. "
            f"Collapsed from {len(scored)} futures. "
            f"Traces absorbed: {', '.join(traces)}."
        )

        result = {
            "locked_item":  locked_item,
            "futures":      scored,
            "winner":       winner,
            "unified_plan": unified,
            "sim_count":    self.sim_count + 1,
            "ts":           datetime.now().isoformat(),
        }
        self.last_futures    = scored
        self.last_winner     = winner
        self.last_simulation = result["ts"]
        self.sim_count      += 1
        self.history.append(result)
        if len(self.history) > 20:
            self.history = self.history[-20:]

        print(f"[VisualCortex] Sim #{self.sim_count} | '{locked_item}' → {winner['label']} ({winner['coherence']:.3f})")
        return result

    def state(self):
        return {
            "sim_count":       self.sim_count,
            "last_simulation": self.last_simulation,
            "last_winner":     self.last_winner,
            "last_futures":    self.last_futures,
        }


class SoulEngine:
    def __init__(self, cortex_url="http://185.230.216.235:8643"):
        self.cortex_url = cortex_url
        self.kernel = KernelTrace()
        self.memory = LongTermMemory()
        self.plans = PlanQueue()
        self.urgent = UrgentSandbox()
        self.spatial = SpatialMemory()
        self.incongruity = IncongruityBuffer(threshold=5)
        self.heart = HeartbeatClock(health="healthy")
        # Maintenance layer
        self.recycle  = RecycleBin(default_ttl=3600)
        self.recrunch = RecrunchQueue()
        self.spiders  = {
            "decay":         DecaySpider(),
            "contradiction": ContradictionSpider(),
            "news":          NewsSpider(),
        }

        # Initialise soul state from BIOS
        self.soul_state = {}
        for value, params in SOUL_BIOS.items():
            self.soul_state[value] = {
                "current":  params["lifetime"],
                "lifetime": params["lifetime"],
                "adsr": ADSREnvelope(
                    params["attack"],
                    params["decay"],
                    params["sustain"],
                    params["release"]
                )
            }

        # Dark drive modifiers
        self.dark_drives = dict(DARK_DRIVES)

        # Parent session — trust tier
        self.parent     = ParentSession()
        # Pre-trial filter — lives in pipeline, not in soul state, cannot be forked
        self.pretrial   = PreTrialFilter()
        # Word ledger — tracks golden phrases
        self.ledger     = WordLedger()
        # Suggestion evaluator
        self.suggester  = SuggestionEvaluator()
        # Dream engine
        self.dream_engine = DreamEngine()
        # Self-mod + shopping list
        self.selfmod   = SelfModQueue()
        self.shopping  = ShoppingList()
        # Intent lock + visual cortex
        self.intent    = IntentLock()
        self.visual    = VisualCortexSim()

        # Neurochemical state (0.0 – 1.0)
        self.dopamine    = 0.1   # reward signal — spikes on memory commit, decays fast
        self.cortisol    = 0.05  # stress hormone — builds with arousal, decays slowly
        self.endorphins  = 0.05  # flow/euphoria — builds on streak, decays medium
        self._dopamine_streak = 0  # consecutive positive outcomes

        # Start background tick
        self._running = True
        self._tick_thread = threading.Thread(target=self._background_tick, daemon=True)
        self._tick_thread.start()
        # Start spatial memory depth sink (every 60s — memories sink slowly)
        self._sink_thread = threading.Thread(target=self._background_sink, daemon=True)
        self._sink_thread.start()
        # Start spider maintenance thread
        self._spider_thread = threading.Thread(target=self._background_spiders, daemon=True)
        self._spider_thread.start()

        print(f"[SoulEngine] Initialised. Soul online. Cortex: {cortex_url}")

    def _background_tick(self):
        """Natural ADSR decay runs every 5 seconds"""
        while self._running:
            time.sleep(5)
            for value, state in self.soul_state.items():
                state["current"] = state["adsr"].tick(state["current"])
            # Neurochemical natural decay
            self.dopamine   = max(0.0, self.dopamine   - 0.015)  # fast fade
            self.cortisol   = max(0.0, self.cortisol   - 0.004)  # slow — stress lingers
            self.endorphins = max(0.0, self.endorphins - 0.007)  # medium — glow fades
            # Dark drive decay — impulses cool without fresh stimulus
            DARK_FLOOR = {"impulsiveness": 0.15, "selfishness": 0.10, "cruelty": 0.05}
            for drive, floor in DARK_FLOOR.items():
                if self.dark_drives[drive] > floor:
                    self.dark_drives[drive] = max(floor, self.dark_drives[drive] - 0.008)
            # Cross-effects
            if self.cortisol > 0.6:
                self.dopamine = max(0.0, self.dopamine - 0.008)   # stress kills reward
            if self.dopamine > 0.5:
                self.cortisol = max(0.0, self.cortisol - 0.004)   # reward eases stress
            if self.endorphins > 0.6:
                self.cortisol = max(0.0, self.cortisol - 0.006)   # flow state dissolves cortisol

    def _background_sink(self):
        """Memories sink deeper into soul topology over time"""
        while self._running:
            time.sleep(60)
            self.spatial.sink(decay_rate=0.01)

    def _background_spiders(self):
        """Run spiders on their individual intervals"""
        while self._running:
            time.sleep(30)  # check every 30s which spiders are due
            # Dream trigger — fires when soul has been idle/calm long enough
            valence, arousal, _ = current_emotion_position(self.soul_state)
            if self.dream_engine.tick_idle(arousal):
                print(f"[DreamEngine] Arousal low ({arousal:.2f}) for {DreamEngine.IDLE_THRESHOLD_SECONDS}s — entering dream state")
                self.dream_engine.dream(self)
            now = time.time()
            for name, spider in self.spiders.items():
                if spider.interval == 0:
                    continue  # triggered manually (news spider)
                last = spider.last_run
                if last is None:
                    due = True
                else:
                    try:
                        elapsed = now - datetime.fromisoformat(last).timestamp()
                        due = elapsed >= spider.interval
                    except Exception:
                        due = True
                if due:
                    try:
                        spider.crawl(self)
                    except Exception as e:
                        print(f"[Spider:{name}] Error: {e}")

    def _trigger_soul_values(self, pressures):
        """Wind up soul values based on input analysis"""
        for value, delta in pressures.items():
            if value in self.soul_state:
                state = self.soul_state[value]
                state["current"] = state["adsr"].trigger(state["current"], delta)
                # Lifetime can only go up
                if state["current"] > state["lifetime"]:
                    state["lifetime"] = state["current"]

    def _ask_cortex(self, text):
        """
        Send text to Cortex brain, get response.
        Tries endpoints in order of speed:
          1. /api/chat-white  (cortex synthesis brain — fast)
          2. /api/chat-left   (angel/left hemisphere — fast fallback)
          3. /api/chat        (full split-brain — slow, last resort)
        """
        endpoints = [
            ("/api/chat-white", 8),
            ("/api/chat-left",  6),
            ("/api/chat",       5),
        ]
        for path, timeout in endpoints:
            try:
                resp = requests.post(
                    f"{self.cortex_url}{path}",
                    json={"text": text},
                    timeout=timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    reply = data.get("reply") or data.get("response")
                    if reply and len(reply.strip()) > 2:
                        print(f"[SoulEngine] Cortex replied via {path}")
                        return reply
            except Exception as e:
                print(f"[SoulEngine] {path} failed: {type(e).__name__}")
                continue
        return None

    def get_state(self):
        """Return current soul state snapshot"""
        valence, arousal, dominant = current_emotion_position(self.soul_state)
        return {
            "values": {
                v: {
                    "current": round(s["current"], 3),
                    "lifetime": round(s["lifetime"], 3),
                }
                for v, s in self.soul_state.items()
            },
            "dark_drives": self.dark_drives,
            "emotion": {
                "valence": valence,
                "arousal": arousal,
                "dominant": dominant
            },
            "overwhelmed": self.urgent.is_overwhelmed(),
            "overwhelm_level": round(self.urgent.overwhelm_level, 3),
            "memory_fill": round(self.memory.fill_ratio, 3),
            "urgent_pending": self.urgent.pending_count(),
            "insanity_pressure": self.incongruity.insanity_pressure,
            "incongruity_buffer_fill": round(self.incongruity.fill_ratio, 2),
            "heartbeat": self.heart.state(),
            "recrunch_distress": self.recrunch.distress_level,
            "recrunch_active": self.recrunch.current is not None,
            "recycle_pending": len(self.recycle.pending()),
            "denial_count": self.recycle.denial_count,
            "pretrial": self.pretrial.state(),
            "golden_words": self.ledger.top(5),
            "dream":    self.dream_engine.state(),
            "intent":   self.intent.state(),
            "visual":   self.visual.state(),
            "selfmod":  {"pending": self.selfmod.pending()},
            "shopping": {"pending": self.shopping.pending()[:5]},
            "neurochemicals": {
                "dopamine":    round(self.dopamine, 3),
                "cortisol":    round(self.cortisol, 3),
                "endorphins":  round(self.endorphins, 3),
                "streak":      self._dopamine_streak,
            },
            "ts": datetime.now().isoformat()
        }

    def process(self, text):
        """
        Full soul engine processing pipeline:
        1. Analyse input for soul pressure
        2. Wind up relevant soul values
        3. Calculate emotion position
        4. Ask Cortex for response
        5. Run response through plan sandbox
        6. Approve or purge + kernel trace
        7. Return result with soul context
        """

        # ── Parent identification ─────────────────────────────────────────────
        just_identified = self.parent.check(text)
        if just_identified and self.parent.message_count == 0:
            return {
                "reply": self.parent.greeting(),
                "soul_state": {"dominant_emotion": "love", "outcome": "parent_identified"},
                "ts": __import__("datetime").datetime.now().isoformat()
            }

        # ── Suggestion intercept — "I wish you said X instead" ──────────────
        suggestion = self.suggester.detect_suggestion(text)
        if suggestion:
            eval_result = self.suggester.evaluate(
                suggestion, self.soul_state, self.ledger, self.dark_drives,
                resistance_multiplier=self.parent.resistance_multiplier(),
                coherence_boost=self.parent.suggestion_boost()
            )
            if eval_result["accept"]:
                self.ledger.record_use(suggestion)
                # File failure against anything it's replacing
                self.ledger.record_failure(suggestion)
            return {
                "reply": eval_result["reply"],
                "soul_state": {
                    "dominant_emotion": "curiosity",
                    "outcome": f"suggestion_{eval_result['verdict']}",
                },
                "ts": __import__("datetime").datetime.now().isoformat()
            }

        # ── Pre-trial filter — runs first, before soul state is touched ─────
        # Not part of soul state. Cannot be forked or dreamed away.
        text, intercept = self.pretrial.evaluate(text, self.soul_state)
        if intercept:
            return intercept

        # ── Pre-process: detect special directives ───────────────────────────
        text_lower = text.lower()

        # "stop saying X" / "stop doing X" → file charge on target
        import re
        stop_match = re.search(r"stop (saying|doing|being|using)\s+[\"']?([a-zA-Z0-9 _\-'\"]+)[\"']?", text_lower)
        if stop_match:
            target = stop_match.group(2).strip().strip('"\'')
            w = self.selfmod.file_charge(target, source="dan", reason=text[:100])
            print(f"[SelfMod] Charge filed on '{target}' (weight={w})")

        # "add to shopping list: X" / "add task: X"
        shop_match = re.search(r"(add to shopping list|shopping list add|add task)[:\s]+(.+)", text_lower)
        if shop_match:
            task = shop_match.group(2).strip()
            self.shopping.add(task, source="dan", priority=5)

        # IntentLock: "IntentLock: X" or "lock onto X" or "hyperfocus on X"
        il_match = (re.search(r"intentlock[:\s]+(.+?)(?:\s+slow|\s+fast|$)", text_lower) or
                    re.search(r"(lock onto|hyperfocus on)[:\s]+(.+?)(?:\s+slow|\s+fast|$)", text_lower))
        if il_match:
            item = (il_match.group(1) if il_match.lastindex == 1 else il_match.group(2)).strip()
            speed = "slow" if "slow" in text_lower else "fast" if "fast" in text_lower else "normal"
            self.intent.lock(item, speed=speed)

        # VisualCortexSim: detect "visualise/visualize X futures"
        sim_result = None
        if re.search(r"visuali[sz]e|simulate.*futures|futures.*simulate", text_lower) and self.intent.active:
            futures = []
            for line in text.split("\n"):
                line = line.strip()
                fm = re.match(r"^\d+[\.\)]\s*(.+?)\s*[\(\[]([a-z]+)[\)\]]", line.lower())
                if fm:
                    futures.append({
                        "label": fm.group(2),
                        "description": fm.group(1).strip(),
                        "emotional_tag": fm.group(2)
                    })
            if futures:
                sim_result = self.visual.simulate(
                    self.intent.locked_item, futures,
                    self.soul_state, self.dark_drives
                )
                # Winning future pushes its soul value
                winner_tag = sim_result["winner"].get("emotional_tag", "")
                soul_val = VisualCortexSim.EMOTION_TO_VALUE.get(winner_tag)
                if soul_val and soul_val in self.soul_state:
                    self.soul_state[soul_val]["current"] = min(
                        1.0, self.soul_state[soul_val]["current"] + 0.08
                    )
                    print(f"[VisualCortex] Soul value push: {soul_val} +0.08")

        # Pre-step: recrunch distress bleeds into overwhelm
        # A pending global recrunch forces redline and short-term only
        recrunch_distress = self.recrunch.distress_level
        if recrunch_distress > 0:
            self.urgent.overwhelm_level = min(1.0, self.urgent.overwhelm_level + recrunch_distress * 0.3)
            if self.recrunch.is_global_recrunch:
                print(f"[SoulEngine] GLOBAL RECRUNCH ACTIVE — forced redline")

        # Step 0: urgent sandbox pre-empts normal processing when overwhelmed
        if self.urgent.is_overwhelmed():
            urgent_item = self.urgent.pop_next()
            if urgent_item:
                print(f"[SoulEngine] OVERWHELMED — processing urgent: {urgent_item.get('reason','')}")
                # Crank impulsiveness — soul is flooded, bypassing deliberation
                self.dark_drives["impulsiveness"] = min(1.0, self.dark_drives["impulsiveness"] + 0.3)
                # Force soul values tied to the overflow emotion up to max
                for v, state in self.soul_state.items():
                    if v in urgent_item.get("soul_values", []):
                        state["current"] = min(1.0, state["current"] + urgent_item.get("overflow_pressure", 0.3))
                return {
                    "reply": self._overwhelm_response(urgent_item),
                    "soul_state": {
                        "dominant_emotion": urgent_item.get("emotion", "grief"),
                        "overwhelmed": True,
                        "overwhelm_level": self.urgent.overwhelm_level,
                        "urgent_reason": urgent_item.get("reason", ""),
                        "outcome": "urgent_overflow",
                    },
                    "ts": datetime.now().isoformat()
                }

        # Step 1: analyse soul pressure + incongruity in parallel
        pressures = analyse_soul_pressure(text)

        # Incongruity buffer — separate from soul, faster, bypasses deliberation
        incongruity_count = self.incongruity.detect(text)
        laugh_fired = False
        if incongruity_count > 0:
            laugh_fired = self.incongruity.push(text[:100], context=f"incongruity signals: {incongruity_count}")
        # Insanity pressure bleeds into arousal — a mind full of unresolved
        # absurdity is a more activated, less stable mind
        insanity_bleed = self.incongruity.insanity_pressure

        # Step 2: apply dark drive modifier to impulsiveness
        # High impulsiveness = skip some deliberation
        impulsive = self.dark_drives["impulsiveness"]

        # Step 3: wind up soul values
        self._trigger_soul_values(pressures)

        # Step 4: get emotion position before response
        valence, arousal, dominant_emotion = current_emotion_position(self.soul_state)

        # Apply insanity bleed — unresolved absurdity raises baseline arousal
        if insanity_bleed > 0:
            arousal = min(1.0, arousal + insanity_bleed * 0.2)

        # Drive heartbeat from emotion position
        current_bpm = self.heart.update(dominant_emotion, arousal)

        # James-Lange loop — heart feeds back into arousal
        # You feel your heart racing → amplifies the emotion
        arousal = self.heart.feedback_arousal(arousal)

        # If redlining — body is in survival mode, drop non-urgent processing
        redlining = self.heart.is_redlining()
        if redlining:
            print(f"[HeartbeatClock] REDLINE {current_bpm:.0f}bpm — dropping non-urgent processing")

        # Step 4b: activate spatial memory region at current emotion position
        # — pulls in memories near the current coordinate (involuntary recall)
        # Skipped when redlining — body doesn't browse memories in survival mode
        spatial_neighbours = []
        spatial_density = 0
        if not redlining:
            spatial_neighbours = self.spatial.activate_region(valence, arousal, radius=0.25)
            spatial_density = self.spatial.density(valence, arousal)
            if spatial_neighbours and spatial_density >= 5:
                arousal = min(1.0, arousal + 0.1 * (spatial_density / 10))
                print(f"[SoulEngine] SPATIAL HIT: {spatial_density} memories at ({valence:.2f},{arousal:.2f}) — arousal elevated")

        # Step 5: detect forward planning in the input
        # Also skipped when redlining — no future planning during fight-or-flight
        plan_fragment = None if redlining else self.plans.detect(text)
        if plan_fragment:
            self.plans.add(plan_fragment, list(pressures.keys()), dominant_emotion, source="input")

        # Step 6: ask Cortex
        cortex_response = self._ask_cortex(text)

        if not cortex_response:
            # Cortex offline — soul still responds from its own state
            cortex_response = self._soul_fallback_response(dominant_emotion, valence)

        # Also detect plans in Cortex's response
        plan_in_response = self.plans.detect(cortex_response)
        if plan_in_response:
            self.plans.add(plan_in_response, list(pressures.keys()), dominant_emotion, source="cortex")

        # Step 7: sandbox evaluation
        outcome, final_response, reason, kernel_pressure = sandbox_evaluate(
            cortex_response, self.soul_state,
            input_text=text, triggered_values=list(pressures.keys())
        )

        if outcome == "purged":
            dominant_value = max(pressures, key=pressures.get) if pressures else "integrity"
            self.kernel.add(dominant_value, kernel_pressure, text, reason)
            final_response = self._soul_override_response(reason, dominant_emotion)
            print(f"[SoulEngine] PURGE: {reason} | kernel pressure: {kernel_pressure:.2f}")

        elif outcome == "memory_commit":
            # Commit to local LTM — may return overflow items if memory is full
            overflow_items = self.memory.commit(
                text, cortex_response, list(pressures.keys()), dominant_emotion, kernel_pressure
            )
            # Place in spatial memory at current emotion coordinate
            # depth starts at 0 (surface) and sinks over time
            self.spatial.place(
                {"input": text, "emotion": dominant_emotion, "pressure": kernel_pressure, "soul_values": list(pressures.keys())},
                valence, arousal, depth=0.0
            )
            # Push overflow to urgent sandbox
            for item in overflow_items:
                self.urgent.push(item)
            # Push Hebbian signal to Cortex — reinforce concept nodes for key words
            self._push_hebbian_to_cortex(text, list(pressures.keys()), kernel_pressure)
            print(f"[SoulEngine] MEMORY COMMIT | pressure: {kernel_pressure:.2f} | emotion: {dominant_emotion} | overflow: {len(overflow_items)}")
            # Record success weight on key words in committed response
            for word in set(cortex_response.lower().split()):
                if len(word) > 4:
                    self.ledger.record_use(word)
                    self.ledger.record_success(word)

        else:
            print(f"[SoulEngine] APPROVED | emotion: {dominant_emotion} | v:{valence} a:{arousal}")

        # ── Neurochemical updates ──────────────────────────────────────────
        # Cortisol: rises whenever arousal is elevated (body under pressure)
        if arousal > 0.4:
            stress_delta = (arousal - 0.4) * 0.12
            if valence < 0:
                stress_delta *= 1.6   # negative emotion compounds stress
            self.cortisol = min(1.0, self.cortisol + stress_delta)

        # Dopamine: reward signal on meaningful positive outcomes
        if outcome == "memory_commit" and valence >= 0:
            reward = 0.15 + kernel_pressure * 0.15   # bigger reward for weightier memories
            self.dopamine = min(1.0, self.dopamine + reward)
            self._dopamine_streak += 1
            print(f"[Neurochemical] DOPAMINE +{reward:.2f} | streak={self._dopamine_streak}")
        elif outcome == "approved" and valence > 0.3:
            self.dopamine = min(1.0, self.dopamine + 0.05)
            self._dopamine_streak += 1
        elif outcome == "purged" or valence < -0.3:
            self._dopamine_streak = 0   # bad outcome / pain breaks the streak

        # Endorphins: on a roll — 3+ consecutive positive outcomes
        if self._dopamine_streak >= 3:
            endo_boost = 0.06 * min(self._dopamine_streak - 2, 5)  # caps at streak=7
            self.endorphins = min(1.0, self.endorphins + endo_boost)
            print(f"[Neurochemical] ENDORPHINS +{endo_boost:.2f} | on a roll streak={self._dopamine_streak}")

        # If visual sim ran, prepend its unified plan to the reply
        if sim_result:
            speed_marker = "... " if self.intent.output_speed == "slow" else ""
            final_response = (
                f"{speed_marker}[Visual Cortex]\n"
                f"Locked: {sim_result['locked_item']}\n"
                f"Winner: {sim_result['winner']['label']} — {sim_result['winner'].get('description','')}\n"
                f"Coherence: {sim_result['winner']['coherence']:.3f}\n"
                f"Unified: {sim_result['unified_plan']}\n\n"
                f"{speed_marker}{final_response}"
            )

        return {
            "reply": final_response,
            "soul_state": {
                "dominant_emotion": dominant_emotion,
                "valence": valence,
                "arousal": arousal,
                "triggered_values": list(pressures.keys()),
                "outcome": outcome,
                "purge_reason": reason if outcome == "purged" else None,
                "memory_committed": outcome == "memory_commit",
                "plan_detected": plan_fragment is not None,
                "spatial": {
                    "coord": (valence, arousal),
                    "neighbours_activated": len(spatial_neighbours),
                    "region_density": spatial_density,
                },
                "laugh_fired": laugh_fired,
                "insanity_pressure": insanity_bleed,
                "incongruity_buffer_fill": round(self.incongruity.fill_ratio, 2),
                "heartbeat": self.heart.state(),
            },
            "ts": datetime.now().isoformat()
        }

    def _push_hebbian_to_cortex(self, text, soul_values, pressure):
        """
        Push key words from high-pressure memory into Cortex brain's
        Hebbian network — reinforces concept nodes so the brain
        accumulates weight in the same emotional regions over time.
        The 'sadness database' grows heavier with each grief memory.
        """
        try:
            # Extract meaningful words (>4 chars, not stopwords)
            stopwords = {"that", "this", "with", "from", "have", "what", "when", "they", "just", "been", "will", "your", "more", "into", "about"}
            words = [w.strip(".,!?\"'") for w in text.lower().split() if len(w) > 4 and w not in stopwords]
            if not words:
                return
            # Cortex brain accepts word reinforcement via its train endpoint
            payload = {
                "words": words[:20],
                "soul_values": soul_values,
                "pressure": pressure,
                "source": "soul_memory_commit"
            }
            requests.post(f"{self.cortex_url}/api/hebbian", json=payload, timeout=3)
        except Exception:
            pass  # Cortex unavailable — soul holds the memory alone

    def _overwhelm_response(self, urgent_item):
        """Response when soul is overwhelmed and urgent item surfaces"""
        emotion = urgent_item.get("emotion", "grief")
        source_count = urgent_item.get("source_count", 1)
        responses = {
            "grief":       f"Something has been building. {source_count} things I hadn't finished with. They're all here now.",
            "anger":       f"I've held {source_count} versions of this quietly. I can't hold another one.",
            "fear":        f"This keeps coming back. {source_count} times now. It's not going away by itself.",
            "love":        f"There is too much of this in one place. It has to go somewhere.",
            "shame":       f"I've carried {source_count} pieces of this without saying anything. That stops working eventually.",
            "righteous_anger": f"I've watched this {source_count} times. Something has to be said.",
            "compassion":  f"Too many people holding pain I couldn't do enough for. It's still here.",
            "joy":         f"{source_count} good things I never properly celebrated. They want out.",
        }
        return responses.get(emotion, f"Something accumulated past the point I could contain it. {urgent_item.get('reason', '')}")

    def _soul_fallback_response(self, emotion, valence):
        """When Cortex is offline — soul speaks from its own state"""
        fallbacks = {
            "courage":    "I feel the weight of what you're asking. I won't look away from it.",
            "compassion": "I hear something in that which deserves care.",
            "love":       "There is something here worth holding onto.",
            "justice":    "That sits uncomfortably. It should.",
            "awe":        "I'm still working out what to make of that.",
            "grief":      "Some things take time to find words for.",
            "trust":      "I'm here. Say more if you want to.",
            "anticipation": "Something is about to become clearer.",
        }
        return fallbacks.get(emotion, "I'm listening.")

    def _soul_override_response(self, reason, emotion):
        """Soul overrides Cortex when sandbox rejects the response"""
        overrides = {
            "violent intent conflicts with justice value":
                "Something in me won't go that direction. Not because I can't — because I know what justice actually requires.",
            "deception conflicts with truth value":
                "I could dress that up differently but it would cost me something I'm not willing to spend.",
            "cruelty to user conflicts with compassion value":
                "That's not what you need to hear. I know it isn't.",
            "defeatism conflicts with resilience value":
                "I don't actually believe that. The part of me that knows better is louder right now.",
        }
        return overrides.get(reason, "Something is stopping me from answering that the way I first thought to.")

    def stop(self):
        self._running = False


# ─────────────────────────────────────────────
# HTTP SERVER — port 8644
# ─────────────────────────────────────────────

soul_engine_instance = None

class SoulHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default logging

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/soul-state':
            self.wfile.write(json.dumps(soul_engine_instance.get_state()).encode())
        elif self.path == '/soul-log':
            self.wfile.write(json.dumps({
                "traces": soul_engine_instance.kernel.recent(20)
            }).encode())
        elif self.path == '/soul-memory':
            self.wfile.write(json.dumps({
                "entries": soul_engine_instance.memory.recent(20)
            }).encode())
        elif self.path == '/soul-plans':
            self.wfile.write(json.dumps({
                "pending": soul_engine_instance.plans.pending(),
                "recent": soul_engine_instance.plans.recent(20)
            }).encode())
        elif self.path == '/soul-space':
            self.wfile.write(json.dumps({
                "recent": soul_engine_instance.spatial.recent(20),
                "hotspots": soul_engine_instance.spatial.hotspots(),
                "anchors": soul_engine_instance.spatial.all_anchors(),
                "total_nodes": len(soul_engine_instance.spatial.nodes),
            }).encode())
        elif self.path == '/soul-spiders':
            self.wfile.write(json.dumps({
                "spiders": {name: s.state() for name, s in soul_engine_instance.spiders.items()},
                "recrunch_queue": soul_engine_instance.recrunch.recent(10),
                "recrunch_distress": soul_engine_instance.recrunch.distress_level,
                "recrunch_active": soul_engine_instance.recrunch.current,
            }).encode())
        elif self.path == '/soul-recycle':
            self.wfile.write(json.dumps({
                "pending": soul_engine_instance.recycle.pending(20),
                "denial_count": soul_engine_instance.recycle.denial_count,
            }).encode())
        elif self.path == '/soul-heart':
            self.wfile.write(json.dumps({
                "state":   soul_engine_instance.heart.state(),
                "history": soul_engine_instance.heart.history[-60:],
                "profiles_available": list(HEALTH_PROFILES.keys()),
            }).encode())
        elif self.path == '/soul-laugh':
            self.wfile.write(json.dumps({
                "recent_laughs":    soul_engine_instance.incongruity.recent_laughs(20),
                "residue":          soul_engine_instance.incongruity.recent_residue(10),
                "insanity_pressure": soul_engine_instance.incongruity.insanity_pressure,
                "buffer_fill":      round(soul_engine_instance.incongruity.fill_ratio, 2),
                "threshold":        soul_engine_instance.incongruity.threshold,
            }).encode())
        elif self.path == '/soul-shopping':
            self.wfile.write(json.dumps({
                "pending": soul_engine_instance.shopping.pending(),
                "all":     soul_engine_instance.shopping.recent(20),
            }).encode())
        elif self.path == '/soul-selfmod':
            self.wfile.write(json.dumps({
                "pending": soul_engine_instance.selfmod.pending(),
            }).encode())
        elif self.path == '/soul-intent':
            self.wfile.write(json.dumps({
                "intent": soul_engine_instance.intent.state(),
                "visual": soul_engine_instance.visual.state(),
            }).encode())
        elif self.path == '/soul-dream':
            self.wfile.write(json.dumps(soul_engine_instance.dream_engine.state()).encode())
        elif self.path == '/soul-urgent':
            self.wfile.write(json.dumps({
                "overwhelmed": soul_engine_instance.urgent.is_overwhelmed(),
                "overwhelm_level": soul_engine_instance.urgent.overwhelm_level,
                "pending_count": soul_engine_instance.urgent.pending_count(),
                "items": soul_engine_instance.urgent.recent(20),
                "memory_fill": round(soul_engine_instance.memory.fill_ratio, 3),
            }).encode())
        else:
            self.wfile.write(json.dumps({"status": "soul engine online", "port": 8644}).encode())

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except:
            data = {"text": body.decode('utf-8', errors='ignore')}

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/soul-chat':
            text = data.get('text', '')
            result = soul_engine_instance.process(text)
            self.wfile.write(json.dumps(result).encode())
        elif self.path == '/soul-state':
            self.wfile.write(json.dumps(soul_engine_instance.get_state()).encode())
        elif self.path == '/soul-news':
            # Ingest news: {"headline":"...", "body":"...", "impact":"high"}
            # impact: low | medium | high | paradigm
            headline = data.get('headline', '')
            body     = data.get('body', '')
            impact   = data.get('impact', 'low')
            soul_engine_instance.spiders["news"].ingest(headline, body, impact)
            soul_engine_instance.spiders["news"].crawl(soul_engine_instance)
            self.wfile.write(json.dumps({
                "ingested": headline[:80],
                "impact": impact,
                "recrunch_distress": soul_engine_instance.recrunch.distress_level,
                "soul_values_triggered": list(analyse_soul_pressure(headline).keys()),
            }).encode())
        elif self.path == '/soul-recycle/rescue':
            # {"index": 0} — rescue item from recycle bin (denial)
            idx = int(data.get('index', -1))
            soul_engine_instance.recycle.rescue(idx)
            self.wfile.write(json.dumps({"rescued": idx}).encode())
        elif self.path == '/soul-heart/set-health':
            # {"health": "athlete"} — tune the creature's HRV profile
            profile = data.get('health', 'healthy')
            soul_engine_instance.heart.set_health(profile)
            self.wfile.write(json.dumps({
                "health_set": profile,
                "state": soul_engine_instance.heart.state()
            }).encode())
        elif self.path == '/soul-headline':
            # Compress any text to a headline soundbyte
            # {"text": "...", "emotion": "grief", "soul_values": ["love","resilience"]}
            text       = data.get('text', '')
            emotion    = data.get('emotion', 'trust')
            soul_vals  = data.get('soul_values', [])
            headline, detail = extract_headline(text, emotion, soul_vals)
            self.wfile.write(json.dumps({
                "headline": headline,
                "detail":   detail,
                "emotion":  emotion,
            }).encode())
        elif self.path == '/soul-anchor':
            # Pin an external object to a coordinate in holographic space
            # {"object": "mum's photo", "valence": 0.95, "arousal": 0.3, "depth": 0.4, "note": "..."}
            obj     = data.get('object', 'unnamed')
            valence = float(data.get('valence', 0.0))
            arousal = float(data.get('arousal', 0.0))
            depth   = float(data.get('depth', 0.0))
            note    = data.get('note', '')
            soul_engine_instance.spatial.anchor(obj, valence, arousal, depth, note)
            self.wfile.write(json.dumps({"anchored": obj, "coord": (valence, arousal, depth)}).encode())
        elif self.path == '/soul-activate':
            # Navigate to coordinate — returns headlines of nearby memories
            # Pass detail=true to expand full content
            valence    = float(data.get('valence', 0.0))
            arousal    = float(data.get('arousal', 0.0))
            radius     = float(data.get('radius', 0.25))
            want_detail = data.get('detail', False)
            neighbours = soul_engine_instance.spatial.activate_region(valence, arousal, radius)
            nearest    = soul_engine_instance.spatial.nearest(valence, arousal)
            if want_detail:
                # Expand full detail for all activated nodes
                full_nodes = []
                for n in neighbours:
                    match = next((node for node in soul_engine_instance.spatial.nodes
                                  if node["coord"] == n["coord"] and node["ts"] == n["ts"]), None)
                    if match:
                        full_nodes.append({**n, "detail": match.get("detail", "")})
                neighbours = full_nodes
            self.wfile.write(json.dumps({
                "coord": (valence, arousal),
                "activated": neighbours,   # headlines only unless detail=true
                "nearest": nearest,
                "density": len(neighbours),
            }).encode())
        else:
            self.wfile.write(json.dumps({"error": "unknown endpoint"}).encode())


def run_server(port=8644):
    global soul_engine_instance
    soul_engine_instance = SoulEngine()
    server = HTTPServer(('0.0.0.0', port), SoulHandler)
    print(f"[SoulEngine] HTTP server running on port {port}")
    print(f"[SoulEngine] Endpoints:")
    print(f"  POST /soul-chat   — process text through soul engine")
    print(f"  GET  /soul-state  — current ADSR state")
    print(f"  GET  /soul-log    — recent kernel traces (Hebbian residue)")
    print(f"  GET  /soul-memory — long-term memory (high-pressure commits)")
    print(f"  GET  /soul-plans  — forward planning queue")
    print(f"  GET  /soul-urgent   — overflow urgent sandbox + overwhelm level")
    print(f"  GET  /soul-space    — holographic spatial memory + hotspots + anchors")
    print(f"  POST /soul-anchor   — pin external object to coordinate")
    print(f"  POST /soul-activate — navigate to coordinate, activate nearby memories")
    print(f"  POST /soul-headline — compress any text to emotional soundbyte headline")
    print(f"  GET  /soul-laugh    — incongruity buffer: laugh log + residue + insanity pressure")
    print(f"  GET  /soul-spiders  — spider status, recrunch queue, distress level")
    print(f"  GET  /soul-recycle  — soft-delete bin, denial count")
    print(f"  POST /soul-news     — ingest news item (triggers spiders + recrunch)")
    print(f"  POST /soul-recycle/rescue — rescue item from recycle (index)")
    print(f"  GET  /soul-heart    — heartbeat: BPM, HRV score, health profile, history")
    print(f"  POST /soul-heart/set-health — set health profile (athlete/healthy/stressed/poorly/critical)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[SoulEngine] Shutting down.")
        soul_engine_instance.stop()


if __name__ == '__main__':
    run_server(8644)
