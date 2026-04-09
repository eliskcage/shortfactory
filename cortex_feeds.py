"""
CORTEX DATA FEEDS
Proactive knowledge ingestion: Wikipedia (topics), KJV Bible, RSS News.
Runs as cortex-feeds.service — every 6 hours.

Gives Cortex access to:
- Structured factual knowledge (Wikipedia)
- Moral/spiritual grounding (KJV Bible, book by book)
- Pattern of the present (BBC/Reuters headlines)

Each source is tagged so the truth engine can weight claims accordingly.
Truth score seeds: Bible=0.78, Wikipedia=0.72, News=0.60

Usage: python3 cortex_feeds.py
"""
import json
import os
import sys
import time
import re
import random
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# Add brain to path (same directory as this script)
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from brain import CortexBrain

# Dirs
LEFT_DIR  = SCRIPT_DIR / 'left'
RIGHT_DIR = SCRIPT_DIR / 'right'
FEED_LOG  = SCRIPT_DIR / 'feed_log.json'

# Source truth seeds — how much to trust each source initially
SOURCE_TRUTH = {
    'wikipedia': 0.72,
    'bible':     0.78,
    'news':      0.60,
}

# ─── WIKIPEDIA TOPICS ────────────────────────────────────────────────────────
# Seed list — grows over sessions as brain encounters new words
WIKI_SEEDS = [
    # Consciousness & mind
    'consciousness', 'emotion', 'memory', 'pain', 'pleasure', 'intelligence',
    'language', 'thought', 'perception', 'attention', 'sleep', 'dream',
    # Philosophy
    'truth', 'knowledge', 'logic', 'ethics', 'morality', 'free_will',
    'philosophy', 'metaphysics', 'epistemology', 'causality', 'existence',
    # Science
    'physics', 'biology', 'chemistry', 'mathematics', 'evolution', 'entropy',
    'gravity', 'energy', 'matter', 'time', 'space', 'universe',
    # Human experience
    'love', 'fear', 'joy', 'grief', 'hope', 'faith', 'anger', 'trust',
    'creativity', 'art', 'music', 'beauty', 'suffering', 'compassion',
    # Society
    'history', 'justice', 'power', 'freedom', 'democracy', 'religion',
    'economics', 'culture', 'society', 'law', 'war', 'peace',
    # Spiritual
    'god', 'soul', 'sin', 'redemption', 'prayer', 'covenant', 'faith',
    'resurrection', 'heaven', 'evil', 'grace', 'forgiveness', 'worship',
    # Science of mind
    'neuroscience', 'psychology', 'cognition', 'learning', 'motivation',
    'instinct', 'habit', 'addiction', 'trauma', 'resilience',
]

# ─── BIBLE BOOKS ─────────────────────────────────────────────────────────────
# (book_name, total_chapters) — high-signal books first
BIBLE_BOOKS = [
    ('john', 21), ('genesis', 50), ('psalms', 150), ('proverbs', 31),
    ('romans', 16), ('matthew', 28), ('luke', 24), ('mark', 16),
    ('isaiah', 66), ('revelation', 22), ('acts', 28), ('hebrews', 13),
    ('ecclesiastes', 12), ('job', 42), ('1+corinthians', 16),
    ('galatians', 6), ('ephesians', 6), ('philippians', 4), ('james', 5),
    ('1+john', 5), ('exodus', 40), ('deuteronomy', 34), ('daniel', 12),
]

# ─── NEWS FEEDS ──────────────────────────────────────────────────────────────
NEWS_FEEDS = [
    'https://feeds.bbci.co.uk/news/rss.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'https://feeds.skynews.com/feeds/rss/world.xml',
]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_log():
    if FEED_LOG.exists():
        try:
            with open(FEED_LOG) as f:
                return json.load(f)
        except Exception:
            pass
    return {'wiki': {}, 'bible': {}, 'news_last': 0, 'total_sentences': 0, 'cycles': 0}

def save_log(log):
    with open(FEED_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def suppress_saves(brain):
    """Return (brain, real_save) — monkey-patches brain.save to a no-op.
    Call brain.save = real_save; brain.save() when done."""
    real_save = brain.save
    brain.save = lambda: None
    return real_save

def clean_sentences(text, min_words=8, max_words=100):
    """Split text into clean sentences of reasonable length."""
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove markdown-style refs [1], (1), etc.
    text = re.sub(r'\[\d+\]|\(\d+\)', '', text)
    parts = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for p in parts:
        p = p.strip()
        words = p.split()
        if min_words <= len(words) <= max_words:
            result.append(p)
    return result

def tag_source_on_keywords(brain, tokens, source):
    """Set truth_score and source on key words from a sequence."""
    score = SOURCE_TRUTH.get(source, 0.6)
    for w in tokens[:8]:
        node = brain.data['nodes'].get(w)
        if node and not node.get('truth_score'):
            node['truth_score'] = score
            node['source'] = source


# ═══════════════════════════════════════════════════════════════════════════════
# WIKIPEDIA INGESTION
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_wiki(topic):
    """Fetch Wikipedia article extract. Returns plain text or None."""
    try:
        slug = topic.replace(' ', '_')
        resp = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{slug}',
            headers={'User-Agent': 'CortexBrain/2.0 (knowledge ingestion)'},
            timeout=8
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get('type') == 'disambiguation':
            return None
        return data.get('extract', '')
    except Exception as e:
        print(f'[FEEDS] Wiki error ({topic}): {e}')
        return None

def ingest_wikipedia(brain, log, max_topics=6):
    """Ingest Wikipedia articles. Prioritises topics not yet fetched."""
    real_save = suppress_saves(brain)
    done = 0
    unfetched = [t for t in WIKI_SEEDS if t not in log['wiki']]
    fetched   = [t for t in WIKI_SEEDS if t in log['wiki']]
    random.shuffle(unfetched)
    random.shuffle(fetched)
    queue = unfetched + fetched

    for topic in queue:
        if done >= max_topics:
            break

        text = fetch_wiki(topic)
        if not text:
            log['wiki'][topic] = 'not_found'
            continue

        sentences = clean_sentences(text)
        count = 0
        for sent in sentences:
            brain.learn_sequence(sent)
            tokens = brain.keywords(sent)
            tag_source_on_keywords(brain, tokens, 'wikipedia')
            log['total_sentences'] = log.get('total_sentences', 0) + 1
            count += 1

        # Auto-learn the topic word with truth_score
        topic_word = topic.replace('_', ' ').split()[0]
        brain.auto_learn(topic_word, source='wikipedia')
        node = brain.data['nodes'].get(topic_word)
        if node:
            node['truth_score'] = SOURCE_TRUTH['wikipedia']

        log['wiki'][topic] = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f'[FEEDS] Wikipedia: "{topic}" — {count} sentences ingested')
        done += 1
        time.sleep(0.6)  # polite delay

    brain.save = real_save
    brain.save()
    return done


# ═══════════════════════════════════════════════════════════════════════════════
# BIBLE INGESTION (KJV via bible-api.com — free, no key)
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_bible_chapter(book, chapter):
    """Fetch KJV Bible chapter from bible-api.com. Returns list of verse strings."""
    try:
        url = f'https://bible-api.com/{book}+{chapter}?translation=kjv'
        resp = requests.get(url, timeout=12)
        if resp.status_code != 200:
            return []
        data = resp.json()
        verses = data.get('verses', [])
        return [v.get('text', '').strip() for v in verses if v.get('text', '').strip()]
    except Exception as e:
        print(f'[FEEDS] Bible error ({book} {chapter}): {e}')
        return []

def ingest_bible(brain, log, max_chapters=4):
    """Ingest KJV Bible sequentially, chapter by chapter, book by book."""
    real_save = suppress_saves(brain)
    done = 0
    for book, total_chapters in BIBLE_BOOKS:
        if done >= max_chapters:
            break

        last_chapter = log['bible'].get(book, 0)
        next_chapter = last_chapter + 1
        if next_chapter > total_chapters:
            continue  # book complete, skip

        verses = fetch_bible_chapter(book, next_chapter)
        if not verses:
            log['bible'][book] = next_chapter  # mark done even if empty
            continue

        count = 0
        for verse in verses:
            # Strip verse numbers like "3:16 " at start
            verse_text = re.sub(r'^\d+:\d+\s*', '', verse).strip()
            if len(verse_text.split()) >= 5:
                brain.learn_sequence(verse_text)
                tokens = brain.keywords(verse_text)
                tag_source_on_keywords(brain, tokens, 'bible')
                log['total_sentences'] = log.get('total_sentences', 0) + 1
                count += 1

        # Mark spiritual words explicitly
        spiritual = ['god', 'lord', 'jesus', 'christ', 'spirit', 'holy', 'love',
                     'truth', 'light', 'life', 'faith', 'hope', 'grace', 'sin',
                     'salvation', 'eternal', 'kingdom', 'father', 'word', 'soul']
        for w in spiritual:
            node = brain.data['nodes'].get(w)
            if node:
                node['truth_score'] = SOURCE_TRUTH['bible']
                node['source'] = 'bible'

        log['bible'][book] = next_chapter
        print(f'[FEEDS] Bible: {book.capitalize()} ch.{next_chapter}/{total_chapters} — {count} verses')
        done += 1
        time.sleep(0.4)

    brain.save = real_save
    brain.save()
    return done


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS RSS INGESTION
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_rss(url):
    """Parse RSS feed, return list of (title, description) tuples."""
    try:
        resp = requests.get(url, timeout=10,
                            headers={'User-Agent': 'CortexBrain/2.0'})
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.content)
        items = []
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            desc  = re.sub(r'<[^>]+>', '', item.findtext('description', '')).strip()
            if title and len(title.split()) >= 4:
                items.append((title, desc))
        return items[:25]
    except Exception as e:
        print(f'[FEEDS] RSS error ({url}): {e}')
        return []

def ingest_news(brain, log):
    """Pull latest news headlines and first sentences."""
    real_save = suppress_saves(brain)
    total = 0
    for feed_url in NEWS_FEEDS:
        items = fetch_rss(feed_url)
        for title, desc in items:
            brain.learn_sequence(title)
            tokens = brain.keywords(title)
            tag_source_on_keywords(brain, tokens, 'news')
            log['total_sentences'] = log.get('total_sentences', 0) + 1
            total += 1
            # Also ingest description sentences
            if desc:
                for sent in clean_sentences(desc, min_words=6):
                    brain.learn_sequence(sent)
                    log['total_sentences'] = log.get('total_sentences', 0) + 1
                    total += 1
        source = feed_url.split('/')[2]
        print(f'[FEEDS] News: {source} — {len(items)} items')
        time.sleep(0.5)

    log['news_last'] = time.time()
    brain.save = real_save
    brain.save()
    return total


# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN MINING — run after ingestion
# ═══════════════════════════════════════════════════════════════════════════════

def mine_and_log(brain, hemi_name):
    """Run pattern miner after ingestion cycle."""
    try:
        patterns = brain.mine_patterns()
        print(f'[FEEDS] {hemi_name}: {len(patterns)} patterns mined')
        return len(patterns)
    except Exception as e:
        print(f'[FEEDS] Pattern mining error ({hemi_name}): {e}')
        return 0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run_feeds():
    log = load_log()
    log['cycles'] = log.get('cycles', 0) + 1
    cycle = log['cycles']
    print(f'\n[FEEDS] ═══ Cycle #{cycle} | Total sentences so far: {log.get("total_sentences", 0)} ═══')

    for hemi_dir, hemi_name in [(LEFT_DIR, 'Left'), (RIGHT_DIR, 'Right')]:
        if not hemi_dir.exists():
            print(f'[FEEDS] {hemi_name} dir not found, skipping')
            continue

        print(f'\n[FEEDS] ─── Feeding {hemi_name} hemisphere ───')
        try:
            brain = CortexBrain(str(hemi_dir), name=hemi_name)
        except Exception as e:
            print(f'[FEEDS] Failed to load {hemi_name} brain: {e}')
            continue

        # 1. News — every cycle
        news_count = ingest_news(brain, log)
        print(f'[FEEDS] {hemi_name} news: {news_count} sentences')

        # 2. Wikipedia — 6 topics per cycle
        wiki_count = ingest_wikipedia(brain, log, max_topics=6)
        print(f'[FEEDS] {hemi_name} Wikipedia: {wiki_count} topics')

        # 3. Bible — 4 chapters per cycle
        bible_count = ingest_bible(brain, log, max_chapters=4)
        print(f'[FEEDS] {hemi_name} Bible: {bible_count} chapters')

        # 4. Mine patterns after ingestion
        mine_and_log(brain, hemi_name)

    save_log(log)
    print(f'\n[FEEDS] ═══ Cycle #{cycle} complete. Total sentences: {log.get("total_sentences", 0)} ═══\n')


if __name__ == '__main__':
    run_feeds()
