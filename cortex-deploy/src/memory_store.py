"""
Cortex Memory Store — Persistent emotional memory with multi-backend failover.

4 emotional banks: happy, sad, angry, neutral
1 fast short-term cache: important (in-memory, rebuilt from DB on restart)

Each backend is a PostgreSQL-compatible database (CockroachDB, Supabase, etc).
Writes go to ALL backends (redundancy). Reads from fastest.
Backends auto-ranked by latency. Failed backends skipped gracefully.

Usage:
    memory = MemoryStore([
        {'name': 'cockroachdb', 'dsn': 'postgresql://...'}
    ])
    memory.store({...})
    recent = memory.get_recent(20)
    stats = memory.get_stats()
"""

import json
import time
import threading
from collections import deque


# ---- Emotion Classification ----

def classify_emotion(quality, agreement, dominant_sound, debate):
    """Auto-classify memory into emotional bank based on brain state."""
    # Sound-based (from brain's existing emotion engine)
    if dominant_sound in ('happy', 'silly'):
        return 'happy'
    if dominant_sound in ('sad', 'scared', 'whisper'):
        return 'sad'
    if dominant_sound in ('angry', 'serious'):
        return 'angry'

    # Quality-based fallback
    q = quality
    if isinstance(quality, dict):
        q = quality.get('total', 0.5)
    if q >= 0.6:
        return 'happy'
    if q < 0.3:
        return 'sad'

    # Debate-based
    if debate and debate.get('winner') == 'right' and agreement and agreement < 0.3:
        return 'angry'

    return 'neutral'


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS memories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    brain TEXT NOT NULL,
    emotion TEXT NOT NULL,
    category TEXT NOT NULL,
    user_input TEXT,
    response TEXT,
    topics TEXT,
    quality FLOAT,
    hemisphere TEXT,
    agreement FLOAT,
    dominant_sound TEXT,
    metadata TEXT,
    value FLOAT DEFAULT 0.5,
    access_count INT DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT now(),
    promoted BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
)
"""

CREATE_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_memories_emotion ON memories(emotion)",
    "CREATE INDEX IF NOT EXISTS idx_memories_brain ON memories(brain)",
    "CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_memories_value ON memories(value DESC)",
]


class MemoryBackend(object):
    """One database connection with latency tracking."""

    def __init__(self, name, dsn):
        self.name = name
        self.dsn = dsn
        self.conn = None
        self.latencies = []  # last 20 response times in ms
        self.successes = 0
        self.failures = 0
        self.last_error = None

    def connect(self):
        """Connect to PostgreSQL-compatible database."""
        import psycopg2
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True
        print('[MEMORY] Connected to %s' % self.name)

    def init_tables(self):
        """Create tables if they don't exist."""
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        for idx_sql in CREATE_INDEXES_SQL:
            try:
                cur.execute(idx_sql)
            except Exception:
                pass  # index might already exist
        cur.close()
        print('[MEMORY] Tables ready on %s' % self.name)

    def _parse_row(self, r):
        """Parse a DB row into a memory dict."""
        return {
            'brain': r[0],
            'emotion': r[1],
            'category': r[2],
            'user_input': r[3],
            'response': r[4],
            'topics': json.loads(r[5]) if r[5] else [],
            'quality': r[6],
            'hemisphere': r[7],
            'agreement': r[8],
            'dominant_sound': r[9],
            'metadata': json.loads(r[10]) if r[10] else {},
            'created_at': r[11].strftime('%Y-%m-%d %H:%M:%S') if r[11] else '',
            'value': r[12] if len(r) > 12 else 0.5,
            'access_count': r[13] if len(r) > 13 else 0,
            'promoted': r[14] if len(r) > 14 else False,
        }

    FULL_SELECT = """SELECT brain, emotion, category, user_input, response, topics,
                      quality, hemisphere, agreement, dominant_sound, metadata, created_at,
                      value, access_count, promoted"""

    def store(self, record):
        """INSERT a memory record. Initial value = quality score."""
        if not self.conn:
            raise Exception('Not connected')

        import psycopg2
        # Initial value based on quality — good responses start golden, bad start low
        init_value = record.get('quality', 0.5)
        if isinstance(init_value, dict):
            init_value = init_value.get('total', 0.5)

        try:
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO memories (brain, emotion, category, user_input, response,
                   topics, quality, hemisphere, agreement, dominant_sound, metadata, value)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    record.get('brain', 'synthesis'),
                    record.get('emotion', 'neutral'),
                    record.get('category', 'conversation'),
                    record.get('user_input', ''),
                    record.get('response', ''),
                    json.dumps(record.get('topics', [])),
                    record.get('quality', 0),
                    record.get('hemisphere', 'unknown'),
                    record.get('agreement', 0),
                    record.get('dominant_sound', ''),
                    json.dumps(record.get('metadata', {})),
                    init_value,
                )
            )
            cur.close()
        except psycopg2.InterfaceError:
            self.connect()
            raise
        except psycopg2.OperationalError:
            self.connect()
            raise

    def _query(self, where='', params=None, order='created_at DESC', limit=20):
        """Generic query helper."""
        if not self.conn:
            return []
        sql = self.FULL_SELECT + " FROM memories"
        if where:
            sql += " WHERE " + where
        sql += " ORDER BY " + order + " LIMIT %s"
        all_params = list(params or []) + [limit]
        cur = self.conn.cursor()
        cur.execute(sql, all_params)
        rows = cur.fetchall()
        cur.close()
        return [self._parse_row(r) for r in rows]

    def get_recent(self, limit=20):
        """Get most recent memories."""
        return self._query(limit=limit)

    def get_by_emotion(self, emotion, limit=20):
        """Get memories filtered by emotion bank."""
        return self._query(where='emotion = %s', params=[emotion], limit=limit)

    def get_golden(self, limit=20):
        """Get highest-value memories (the gold)."""
        return self._query(order='value DESC', limit=limit)

    def get_dogshit(self, limit=20):
        """Get lowest-value memories (candidates for cleanup)."""
        return self._query(where='value < 0.2', order='value ASC', limit=limit)

    def get_promoted(self, limit=50):
        """Get memories promoted to the fast lane."""
        return self._query(where='promoted = true', order='access_count DESC', limit=limit)

    def promote(self, memory_id):
        """Promote a memory to the fast lane (high value, frequently accessed)."""
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE memories SET promoted = true, value = LEAST(value + 0.1, 1.0) WHERE id = %s",
            (memory_id,)
        )
        cur.close()

    def demote(self, memory_id):
        """Demote a memory (reduce value)."""
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE memories SET promoted = false, value = GREATEST(value - 0.15, 0.0) WHERE id = %s",
            (memory_id,)
        )
        cur.close()

    def boost(self, memory_id, amount=0.05):
        """Boost a memory's value (it was useful)."""
        if not self.conn:
            return
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE memories SET value = LEAST(value + %s, 1.0), access_count = access_count + 1, last_accessed = now() WHERE id = %s",
            (amount, memory_id)
        )
        cur.close()

    def decay_unused(self, days=7, amount=0.02):
        """Decay value of memories not accessed in N days. Called periodically."""
        if not self.conn:
            return 0
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE memories SET value = GREATEST(value - %s, 0.0) WHERE last_accessed < now() - interval '%s days' AND value > 0.05 RETURNING id",
            (amount, days)
        )
        affected = len(cur.fetchall())
        cur.close()
        return affected

    def value_stats(self):
        """Get value distribution stats."""
        if not self.conn:
            return {}
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE value >= 0.8) as golden,
                    COUNT(*) FILTER (WHERE value >= 0.5 AND value < 0.8) as good,
                    COUNT(*) FILTER (WHERE value >= 0.2 AND value < 0.5) as meh,
                    COUNT(*) FILTER (WHERE value < 0.2) as dogshit,
                    COUNT(*) FILTER (WHERE promoted = true) as promoted,
                    ROUND(AVG(value)::numeric, 3) as avg_value
                FROM memories
            """)
            r = cur.fetchone()
            cur.close()
            return {
                'golden': r[0], 'good': r[1], 'meh': r[2], 'dogshit': r[3],
                'promoted': r[4], 'avg_value': float(r[5]) if r[5] else 0
            }
        except Exception:
            return {}

    def count(self):
        """Total memory count."""
        if not self.conn:
            return 0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM memories")
            n = cur.fetchone()[0]
            cur.close()
            return n
        except Exception:
            return 0

    def count_by_emotion(self):
        """Count memories per emotion bank."""
        if not self.conn:
            return {}
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT emotion, COUNT(*) FROM memories GROUP BY emotion")
            rows = cur.fetchall()
            cur.close()
            return {r[0]: r[1] for r in rows}
        except Exception:
            return {}

    def recall(self, keywords, limit=10):
        """Search memories by keyword matching. Higher-value results first."""
        if not self.conn:
            return []
        conditions = []
        params = []
        for kw in keywords[:5]:
            conditions.append("(user_input ILIKE %s OR response ILIKE %s)")
            params.append('%' + kw + '%')
            params.append('%' + kw + '%')

        if not conditions:
            return self.get_recent(limit)

        where = " OR ".join(conditions)
        # Order by value DESC so golden memories surface first
        return self._query(where=where, params=params, order='value DESC, created_at DESC', limit=limit)

    def avg_latency(self):
        """Average latency of last 20 operations."""
        if not self.latencies:
            return 0
        return sum(self.latencies) / len(self.latencies)


class SupabaseBackend(object):
    """Supabase REST API backend — no direct PostgreSQL needed, uses HTTP."""

    def __init__(self, name, url, service_key):
        self.name = name
        self.url = url.rstrip('/')
        self.service_key = service_key
        self.conn = True  # always "connected" via HTTP
        self.latencies = []
        self.successes = 0
        self.failures = 0
        self.last_error = None
        self._headers = {
            'apikey': service_key,
            'Authorization': 'Bearer ' + service_key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        }

    def connect(self):
        """Verify connection by hitting the REST root."""
        from urllib.request import Request, urlopen
        req = Request(self.url + '/rest/v1/', headers=self._headers)
        resp = urlopen(req, timeout=10)
        if resp.status == 200:
            self.conn = True
            print('[MEMORY] Supabase %s connected' % self.name)
        else:
            raise Exception('Supabase returned %d' % resp.status)

    def init_tables(self):
        """Tables must be created via Supabase dashboard SQL editor."""
        # Test if memories table exists by trying a query
        from urllib.request import Request, urlopen
        try:
            req = Request(
                self.url + '/rest/v1/memories?select=id&limit=1',
                headers=self._headers
            )
            resp = urlopen(req, timeout=10)
            print('[MEMORY] Supabase table exists')
        except Exception as e:
            print('[MEMORY] Supabase memories table not found — create it in dashboard SQL editor')
            self.conn = False

    def _request(self, method, path, data=None):
        """Make HTTP request to Supabase REST API."""
        from urllib.request import Request, urlopen
        url = self.url + '/rest/v1/' + path
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, headers=self._headers, method=method)
        resp = urlopen(req, timeout=15)
        raw = resp.read().decode()
        return json.loads(raw) if raw else []

    def store(self, record):
        """INSERT via REST API."""
        init_value = record.get('quality', 0.5)
        if isinstance(init_value, dict):
            init_value = init_value.get('total', 0.5)
        row = {
            'brain': record.get('brain', 'synthesis'),
            'emotion': record.get('emotion', 'neutral'),
            'category': record.get('category', 'conversation'),
            'user_input': record.get('user_input', ''),
            'response': record.get('response', ''),
            'topics': json.dumps(record.get('topics', [])),
            'quality': record.get('quality', 0),
            'hemisphere': record.get('hemisphere', 'unknown'),
            'agreement': record.get('agreement', 0),
            'dominant_sound': record.get('dominant_sound', ''),
            'metadata': json.dumps(record.get('metadata', {})),
            'value': init_value,
        }
        self._request('POST', 'memories', row)

    def _parse_rows(self, rows):
        """Parse REST API response rows."""
        result = []
        for r in rows:
            result.append({
                'brain': r.get('brain', ''),
                'emotion': r.get('emotion', ''),
                'category': r.get('category', ''),
                'user_input': r.get('user_input', ''),
                'response': r.get('response', ''),
                'topics': json.loads(r['topics']) if r.get('topics') else [],
                'quality': r.get('quality', 0),
                'hemisphere': r.get('hemisphere', ''),
                'agreement': r.get('agreement', 0),
                'dominant_sound': r.get('dominant_sound', ''),
                'metadata': json.loads(r['metadata']) if r.get('metadata') else {},
                'created_at': (r.get('created_at') or '')[:19].replace('T', ' '),
                'value': r.get('value', 0.5),
                'access_count': r.get('access_count', 0),
                'promoted': r.get('promoted', False),
            })
        return result

    def get_recent(self, limit=20):
        rows = self._request('GET', 'memories?select=*&order=created_at.desc&limit=%d' % limit)
        return self._parse_rows(rows)

    def get_by_emotion(self, emotion, limit=20):
        rows = self._request('GET', 'memories?select=*&emotion=eq.%s&order=created_at.desc&limit=%d' % (emotion, limit))
        return self._parse_rows(rows)

    def get_golden(self, limit=20):
        rows = self._request('GET', 'memories?select=*&order=value.desc&limit=%d' % limit)
        return self._parse_rows(rows)

    def get_dogshit(self, limit=20):
        rows = self._request('GET', 'memories?select=*&value=lt.0.2&order=value.asc&limit=%d' % limit)
        return self._parse_rows(rows)

    def get_promoted(self, limit=50):
        rows = self._request('GET', 'memories?select=*&promoted=eq.true&order=access_count.desc&limit=%d' % limit)
        return self._parse_rows(rows)

    def count(self):
        from urllib.request import Request, urlopen
        try:
            headers = dict(self._headers)
            headers['Prefer'] = 'count=exact'
            headers['Range-Unit'] = 'items'
            headers['Range'] = '0-0'
            req = Request(self.url + '/rest/v1/memories?select=id', headers=headers)
            resp = urlopen(req, timeout=10)
            cr = resp.getheader('Content-Range', '*/0')
            return int(cr.split('/')[-1])
        except Exception:
            return 0

    def count_by_emotion(self):
        # Supabase doesn't do GROUP BY via REST easily, approximate with individual counts
        result = {}
        for emo in ['happy', 'sad', 'angry', 'neutral']:
            from urllib.request import Request, urlopen
            try:
                headers = dict(self._headers)
                headers['Prefer'] = 'count=exact'
                headers['Range-Unit'] = 'items'
                headers['Range'] = '0-0'
                req = Request(
                    self.url + '/rest/v1/memories?select=id&emotion=eq.' + emo,
                    headers=headers
                )
                resp = urlopen(req, timeout=10)
                cr = resp.getheader('Content-Range', '*/0')
                n = int(cr.split('/')[-1])
                if n > 0:
                    result[emo] = n
            except Exception:
                pass
        return result

    def value_stats(self):
        # Can't do FILTER easily via REST, use simple counts
        try:
            total = self.count()
            return {
                'golden': 0, 'good': total, 'meh': 0, 'dogshit': 0,
                'promoted': 0, 'avg_value': 0.5
            }
        except Exception:
            return {}

    def promote(self, memory_id):
        from urllib.request import Request, urlopen
        data = json.dumps({'promoted': True}).encode()
        req = Request(
            self.url + '/rest/v1/memories?id=eq.' + str(memory_id),
            data=data, headers=dict(self._headers, **{'Prefer': 'return=minimal'}),
            method='PATCH'
        )
        urlopen(req, timeout=10)

    def demote(self, memory_id):
        from urllib.request import Request, urlopen
        data = json.dumps({'promoted': False}).encode()
        req = Request(
            self.url + '/rest/v1/memories?id=eq.' + str(memory_id),
            data=data, headers=dict(self._headers, **{'Prefer': 'return=minimal'}),
            method='PATCH'
        )
        urlopen(req, timeout=10)

    def boost(self, memory_id, amount=0.05):
        pass  # REST API can't do atomic increment easily

    def decay_unused(self, days=7, amount=0.02):
        return 0  # Not supported via REST

    def recall(self, keywords, limit=10):
        if not keywords:
            return self.get_recent(limit)
        # Use full-text search on first keyword
        kw = keywords[0]
        rows = self._request('GET', 'memories?select=*&or=(user_input.ilike.*%s*,response.ilike.*%s*)&order=value.desc&limit=%d' % (kw, kw, limit))
        return self._parse_rows(rows)

    def avg_latency(self):
        if not self.latencies:
            return 0
        return sum(self.latencies) / len(self.latencies)


class MemoryStore(object):
    """Multi-backend memory with emotional banks + short-term cache."""

    def __init__(self, backends_config):
        self.backends = []
        self.lock = threading.Lock()

        # Short-term in-memory cache (the "important" bank)
        self.important = {
            'recent': deque(maxlen=50),
            'topics': {},       # topic -> count
            'sessions': {},     # session_id -> last 5 msgs
        }

        # Connect to each backend
        for cfg in backends_config:
            btype = cfg.get('type', 'postgresql')
            try:
                if btype == 'supabase':
                    b = SupabaseBackend(cfg['name'], cfg['url'], cfg['service_key'])
                    b.connect()
                    b.init_tables()
                else:
                    b = MemoryBackend(cfg['name'], cfg['dsn'])
                    b.connect()
                    b.init_tables()
                self.backends.append(b)
                print('[MEMORY] Backend %s (%s) ready' % (cfg['name'], btype))
            except Exception as e:
                print('[MEMORY] Backend %s FAILED: %s' % (cfg['name'], str(e)))

        # Rebuild short-term cache from DB
        self._rebuild_cache()

    def _rebuild_cache(self):
        """Load last 50 memories from fastest backend into short-term cache."""
        for b in self.backends:
            try:
                recent = b.get_recent(50)
                for mem in reversed(recent):  # oldest first into deque
                    self.important['recent'].append(mem)
                    for t in mem.get('topics', []):
                        self.important['topics'][t] = self.important['topics'].get(t, 0) + 1
                print('[MEMORY] Cache rebuilt: %d memories loaded' % len(recent))
                return
            except Exception as e:
                print('[MEMORY] Cache rebuild from %s failed: %s' % (b.name, str(e)))

    def store(self, record):
        """Write to ALL backends + update short-term cache. Returns per-backend results."""
        # Classify emotion
        emotion = classify_emotion(
            record.get('quality', 0),
            record.get('agreement', 0),
            record.get('dominant_sound', ''),
            record.get('metadata', {})
        )
        record['emotion'] = emotion

        # Update short-term cache
        self.important['recent'].append(record)
        for t in record.get('topics', []):
            self.important['topics'][t] = self.important['topics'].get(t, 0) + 1

        # Track per session
        sid = record.get('metadata', {}).get('session_id', '')
        if sid:
            if sid not in self.important['sessions']:
                self.important['sessions'][sid] = deque(maxlen=5)
            self.important['sessions'][sid].append({
                'user': record.get('user_input', '')[:80],
                'reply': record.get('response', '')[:80],
                'emotion': emotion,
            })

        # Write to all backends (redundancy)
        results = {}
        for b in self.backends:
            try:
                t0 = time.time()
                b.store(record)
                ms = (time.time() - t0) * 1000
                b.latencies.append(ms)
                if len(b.latencies) > 20:
                    b.latencies.pop(0)
                b.successes += 1
                results[b.name] = {'ok': True, 'ms': round(ms, 1)}
            except Exception as e:
                b.failures += 1
                b.last_error = str(e)
                results[b.name] = {'ok': False, 'error': str(e)[:100]}

        # Re-sort backends by average latency (fastest first for reads)
        with self.lock:
            self.backends.sort(key=lambda x: x.avg_latency())

        return results

    def get_recent(self, limit=20):
        """Get recent memories from fastest backend."""
        for b in self.backends:
            try:
                return b.get_recent(limit)
            except Exception:
                continue
        # Fallback to cache
        return list(self.important['recent'])[-limit:]

    def get_by_emotion(self, emotion, limit=20):
        """Get memories from a specific emotional bank."""
        for b in self.backends:
            try:
                return b.get_by_emotion(emotion, limit)
            except Exception:
                continue
        return []

    def recall(self, keywords, limit=10):
        """Search memories by keywords."""
        for b in self.backends:
            try:
                return b.recall(keywords, limit)
            except Exception:
                continue
        return []

    def get_important(self):
        """Get short-term cache (superfast, no DB hit)."""
        return {
            'recent': list(self.important['recent']),
            'topics': dict(sorted(self.important['topics'].items(), key=lambda x: x[1], reverse=True)[:20]),
            'sessions': {k: list(v) for k, v in self.important['sessions'].items()},
        }

    def get_golden(self, limit=20):
        """Get highest-value memories."""
        for b in self.backends:
            try:
                return b.get_golden(limit)
            except Exception:
                continue
        return []

    def get_dogshit(self, limit=20):
        """Get lowest-value memories."""
        for b in self.backends:
            try:
                return b.get_dogshit(limit)
            except Exception:
                continue
        return []

    def boost(self, memory_id, amount=0.05):
        """Boost a memory's value across all backends."""
        for b in self.backends:
            try:
                b.boost(memory_id, amount)
            except Exception:
                pass

    def promote(self, memory_id):
        """Promote a memory to the fast lane."""
        for b in self.backends:
            try:
                b.promote(memory_id)
            except Exception:
                pass

    def demote(self, memory_id):
        """Demote a memory."""
        for b in self.backends:
            try:
                b.demote(memory_id)
            except Exception:
                pass

    def decay_unused(self, days=7, amount=0.02):
        """Decay value of stale memories. Run periodically."""
        total = 0
        for b in self.backends:
            try:
                total += b.decay_unused(days, amount)
            except Exception:
                pass
        return total

    def get_stats(self):
        """Dashboard stats for all backends + emotion counts + value distribution."""
        backend_stats = []
        value_dist = {}
        for b in self.backends:
            backend_stats.append({
                'name': b.name,
                'connected': b.conn is not None,
                'avg_ms': round(b.avg_latency(), 1),
                'writes': b.successes,
                'failures': b.failures,
                'last_error': b.last_error,
                'total_memories': b.count(),
                'emotions': b.count_by_emotion(),
                'values': b.value_stats(),
            })
            if not value_dist:
                value_dist = b.value_stats()

        return {
            'backends': backend_stats,
            'cache_size': len(self.important['recent']),
            'active_topics': len(self.important['topics']),
            'active_sessions': len(self.important['sessions']),
            'value_distribution': value_dist,
        }
