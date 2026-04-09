"""
PHONEME ENGINE — Frequency Genome for Word Communication
=========================================================
Every word gets a sound_genome: [base_hz, harmonic, rhythm]
derived from its existing emotional sound weights.

Cross-hemisphere protocol:
  Left encodes word → frequency sequence
  Right decodes frequency sequence → word guess
  Match  → genome confirmed, confidence rises
  No match → genome mutates, retry

This is how babies learn. Trial, failure, mutation, lock.
The brain talking to itself until it understands itself.
"""

import math
import random
import time
import threading
import json
import os
from pathlib import Path
from collections import defaultdict

# ── Emotional tone → Hz centre frequency ──────────────────────────────────────
# Maps each sound script tag to a frequency on the hedonic scale
TONE_HZ = {
    'happy':    210.0,
    'warm':     260.0,
    'soft':     290.0,
    'bright':   320.0,
    'deep':     370.0,
    'resonant': 390.0,
    'whisper':  340.0,
    'serious':  440.0,
    'neutral':  480.0,
    'sad':      530.0,
    'scared':   650.0,
    'angry':    740.0,
}

# Script role → harmonic multiplier
ROLE_HARMONIC = {
    'noun':      1.0,
    'verb':      1.618,   # golden ratio — dynamic
    'adj':       1.25,
    'adverb':    1.33,
    'starter':   0.9,
    'ender':     1.1,
    'after_aux': 1.15,
    'after_prep':1.05,
}

GENOME_KEY = 'sound_genome'


# ── Genome seeder ─────────────────────────────────────────────────────────────

def seed_genome(word, node):
    """Derive sound_genome from existing sound weights and scripts.
    Returns genome dict without modifying node."""
    sounds = node.get('sound', {})
    scripts = node.get('scripts', {})
    freq    = node.get('freq', 1)

    # base_hz: weighted average of tone-mapped sound weights
    total_w = sum(sounds.values()) or 1
    base_hz = sum(TONE_HZ.get(tone, 480.0) * count
                  for tone, count in sounds.items()) / total_w if sounds else 480.0

    # harmonic: dominant script role shapes the overtone structure
    harmonic = 1.0
    best_role_count = 0
    for role, multiplier in ROLE_HARMONIC.items():
        count = scripts.get(role, 0)
        if count > best_role_count:
            best_role_count = count
            harmonic = multiplier

    # rhythm: word usage frequency → temporal density (normalised log scale)
    rhythm = min(1.0, math.log10(max(freq, 1)) / 5.0)

    # confidence starts at 0 — rises with successful cross-hemisphere matches
    return {
        'base_hz':    round(base_hz, 2),
        'harmonic':   round(harmonic, 4),
        'rhythm':     round(rhythm, 4),
        'confidence': 0.0,
        'attempts':   0,
        'successes':  0,
        'locked':     False,   # True when genome is stable (>80% success rate)
    }


def seed_all(brain_data, force=False):
    """Seed sound_genome for all nodes that have sound data.
    Returns count of nodes seeded."""
    nodes = brain_data.get('nodes', {})
    seeded = 0
    for word, node in nodes.items():
        if force or GENOME_KEY not in node:
            if node.get('sound') or node.get('freq', 0) > 10:
                node[GENOME_KEY] = seed_genome(word, node)
                seeded += 1
    return seeded


# ── Encoder ───────────────────────────────────────────────────────────────────

def encode(word, brain_data, noise=0.05):
    """Encode a word as a frequency sequence.
    Returns [f1, f2, f3] or None if word has no genome."""
    node = brain_data.get('nodes', {}).get(word)
    if not node:
        return None
    genome = node.get(GENOME_KEY)
    if not genome:
        return None

    base = genome['base_hz']
    har  = genome['harmonic']
    rhy  = genome['rhythm']

    # Add realistic noise (less noise as confidence grows)
    conf   = genome.get('confidence', 0.0)
    spread = noise * (1.0 - conf * 0.8)

    def noisy(v):
        return v * (1.0 + random.gauss(0, spread))

    return [
        round(noisy(base), 2),                    # fundamental
        round(noisy(base * har), 2),              # harmonic overtone
        round(noisy(base * har * (0.5 + rhy)), 2) # rhythmic modulation
    ]


# ── Decoder ───────────────────────────────────────────────────────────────────

def decode(freq_seq, brain_data, top_n=5):
    """Find words whose genome best matches a frequency sequence.
    Returns list of (word, score) sorted by closeness."""
    if not freq_seq or len(freq_seq) < 2:
        return []

    nodes   = brain_data.get('nodes', {})
    f1, f2  = freq_seq[0], freq_seq[1]
    f3      = freq_seq[2] if len(freq_seq) > 2 else None

    scores = []
    for word, node in nodes.items():
        genome = node.get(GENOME_KEY)
        if not genome:
            continue
        base = genome['base_hz']
        har  = genome['harmonic']
        rhy  = genome['rhythm']

        g1 = base
        g2 = base * har
        g3 = base * har * (0.5 + rhy) if f3 is not None else None

        # Euclidean distance in frequency space (normalised to 0-900 scale)
        d1 = ((f1 - g1) / 900.0) ** 2
        d2 = ((f2 - g2) / 900.0) ** 2
        d3 = ((f3 - g3) / 900.0) ** 2 if f3 is not None and g3 else 0.0

        dist = math.sqrt(d1 + d2 + d3)
        score = 1.0 / (1.0 + dist * 10)  # closer = higher score
        scores.append((word, round(score, 4)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]


# ── Cross-hemisphere training cycle ───────────────────────────────────────────

def train_cycle(left_brain, right_brain, n_words=30, max_retries=3):
    """
    Left encodes a word → Right tries to decode.
    On failure: mutate genome, retry.
    Returns training report.
    """
    left_nodes  = left_brain.data.get('nodes', {})
    right_data  = right_brain.data

    # Pick words that have genomes on left AND are known on right
    candidates = [
        w for w, n in left_nodes.items()
        if n.get(GENOME_KEY) and n.get('means') and w in right_data.get('nodes', {})
    ]

    if not candidates:
        return {'ok': False, 'reason': 'no candidates'}

    sample = random.sample(candidates, min(n_words, len(candidates)))

    results    = []
    successes  = 0
    failures   = 0
    mutations  = 0

    for word in sample:
        node   = left_nodes[word]
        genome = node[GENOME_KEY]
        genome['attempts'] = genome.get('attempts', 0) + 1

        matched = False
        for attempt in range(max_retries):
            freq_seq = encode(word, left_brain.data, noise=0.08)
            if not freq_seq:
                break

            # Right brain decodes
            guesses = decode(freq_seq, right_data, top_n=3)
            top_word = guesses[0][0] if guesses else None
            top_score = guesses[0][1] if guesses else 0.0

            if top_word == word:
                # SUCCESS
                genome['successes'] = genome.get('successes', 0) + 1
                genome['confidence'] = min(1.0, genome.get('confidence', 0) + 0.05)
                if genome['confidence'] >= 0.8:
                    genome['locked'] = True
                matched = True
                successes += 1
                results.append({
                    'word': word, 'status': 'match',
                    'attempts': attempt + 1,
                    'confidence': round(genome['confidence'], 3),
                    'freq': freq_seq,
                })
                break
            else:
                # FAIL → mutate genome
                genome['confidence'] = max(0.0, genome.get('confidence', 0) - 0.01)
                # Nudge base_hz toward the midpoint between current and what right brain expected
                if guesses:
                    right_genome = right_data['nodes'].get(top_word, {}).get(GENOME_KEY)
                    if right_genome:
                        # Pull base_hz slightly toward what right brain decoded
                        genome['base_hz'] = genome['base_hz'] * 0.97 + right_genome['base_hz'] * 0.03
                        genome['base_hz'] = round(genome['base_hz'], 2)
                        mutations += 1

        if not matched:
            failures += 1
            results.append({
                'word': word, 'status': 'fail',
                'attempts': max_retries,
                'confidence': round(genome.get('confidence', 0), 3),
            })

    # Save both brains (genome changes are in left_brain.data)
    left_brain.save()

    total_attempts = genome.get('attempts', 0) if candidates else 0
    locked_count = sum(1 for n in left_nodes.values()
                       if n.get(GENOME_KEY, {}).get('locked'))

    return {
        'ok': True,
        'words_trained': len(sample),
        'successes': successes,
        'failures': failures,
        'mutations': mutations,
        'success_rate': round(successes / max(len(sample), 1), 3),
        'locked_genomes': locked_count,
        'sample': results[:10],
    }


def get_stats(brain_data):
    """Return genome statistics for dashboard."""
    nodes = brain_data.get('nodes', {})
    genomes = [n[GENOME_KEY] for n in nodes.values() if GENOME_KEY in n]
    if not genomes:
        return {'seeded': 0}

    locked    = sum(1 for g in genomes if g.get('locked'))
    attempted = sum(1 for g in genomes if g.get('attempts', 0) > 0)
    avg_conf  = sum(g.get('confidence', 0) for g in genomes) / len(genomes)

    # Hz distribution
    hz_vals = [g['base_hz'] for g in genomes]
    joy_zone    = sum(1 for h in hz_vals if h < 300)
    calm_zone   = sum(1 for h in hz_vals if 300 <= h < 450)
    neutral_zone= sum(1 for h in hz_vals if 450 <= h < 550)
    tension_zone= sum(1 for h in hz_vals if 550 <= h < 700)
    pain_zone   = sum(1 for h in hz_vals if h >= 700)

    # Top confident words
    with_conf = [(w, n[GENOME_KEY]) for w, n in nodes.items() if GENOME_KEY in n]
    top = sorted(with_conf, key=lambda x: x[1].get('confidence', 0), reverse=True)[:10]

    return {
        'seeded':       len(genomes),
        'locked':       locked,
        'attempted':    attempted,
        'avg_confidence': round(avg_conf, 4),
        'hz_distribution': {
            'joy':     joy_zone,
            'calm':    calm_zone,
            'neutral': neutral_zone,
            'tension': tension_zone,
            'pain':    pain_zone,
        },
        'top_confident': [
            {'word': w, 'hz': round(g['base_hz'], 1), 'confidence': round(g.get('confidence', 0), 3), 'locked': g.get('locked', False)}
            for w, g in top
        ],
    }
