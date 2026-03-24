"""
ShortFactory Shape API — DuckDB Edition
Stores SDF shape genomes. Rent access by the call.

Endpoints:
  GET  /health
  GET  /shapes              — list/search shapes
  POST /shapes              — save a solved genome
  GET  /shapes/:id          — get one shape
  GET  /shapes/random       — random shape
  GET  /shapes/similar/:id  — find similar shapes
  GET  /stats               — library stats

API key tiers (X-SF-Key header):
  none         — 10 req/day, public shapes only
  free         — 100 req/day
  pro          — 10,000 req/day
  unlimited    — no limit (internal / resellers)
"""

import json
import os
import time
import uuid
import hashlib
import threading
from datetime import datetime, date
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import duckdb

PORT      = int(os.environ.get("SHAPE_PORT", 8644))
DB_PATH   = Path(__file__).parent / "shapes.db"
ADMIN_KEY = os.environ.get("SHAPE_ADMIN_KEY", "sf-admin-changeme")

# ── TIER LIMITS (requests per day) ──
TIERS = {
    None:        {"limit": 10,     "name": "anonymous"},
    "free":      {"limit": 100,    "name": "free"},
    "pro":       {"limit": 10000,  "name": "pro"},
    "unlimited": {"limit": None,   "name": "unlimited"},
}

# ── DB INIT ──
def init_db():
    con = duckdb.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS shapes (
            id          VARCHAR PRIMARY KEY,
            type        VARCHAR NOT NULL,
            genome      JSON    NOT NULL,
            bytes       INTEGER,
            solve_pct   FLOAT   DEFAULT 0,
            tags        VARCHAR DEFAULT '',
            creator     VARCHAR DEFAULT 'anonymous',
            description VARCHAR DEFAULT '',
            public      BOOLEAN DEFAULT true,
            views       INTEGER DEFAULT 0,
            api_calls   INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key         VARCHAR PRIMARY KEY,
            tier        VARCHAR NOT NULL DEFAULT 'free',
            label       VARCHAR DEFAULT '',
            active      BOOLEAN DEFAULT true,
            created_at  TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS usage_log (
            key         VARCHAR,
            day         DATE,
            calls       INTEGER DEFAULT 0,
            PRIMARY KEY (key, day)
        )
    """)
    # Seed a handful of demo shapes
    existing = con.execute("SELECT COUNT(*) FROM shapes").fetchone()[0]
    if existing == 0:
        seeds = [
            ("circle",       {"type":"circle","cx":0,"cy":0,"r":140},                           98.0, "circle,round,basic"),
            ("swoosh",       {"type":"swoosh","t0x":-140,"t0y":30,"t1x":-50,"t1y":-60,"t2x":50,"t2y":-40,"t3x":140,"t3y":30,"w0":2,"w1":40}, 96.0, "swoosh,curve,nike"),
            ("ring",         {"type":"ring","cx":0,"cy":0,"r":120,"inner":55},                   97.0, "ring,donut,hollow"),
            ("square",       {"type":"superellipse","cx":0,"cy":0,"rx":110,"ry":110,"p":64},     99.0, "square,box,sharp"),
            ("triangle",     {"type":"triangle","cx":0,"cy":0,"r":130},                          97.0, "triangle,delta,sharp"),
            ("face",         {"type":"csg","cx":0,"cy":0,"rx":105,"ry":125,"exemptions":[{"cx":-38,"cy":-25,"rx":22,"ry":14},{"cx":38,"cy":-25,"rx":22,"ry":14},{"cx":0,"cy":42,"rx":38,"ry":16}]}, 92.0, "face,human,phi"),
        ]
        for (t, g, pct, tags) in seeds:
            genome_str = json.dumps(g)
            con.execute("""
                INSERT INTO shapes (id, type, genome, bytes, solve_pct, tags, creator, description)
                VALUES (?, ?, ?, ?, ?, ?, 'shortfactory', ?)
            """, [str(uuid.uuid4()), t, genome_str, len(genome_str.encode()), pct, tags, f"Solved {t} — seed shape"])
        print(f"[shape-api] seeded {len(seeds)} shapes")
    con.close()
    print(f"[shape-api] DB ready at {DB_PATH}")

# ── RATE LIMIT ──
_lock = threading.Lock()

def check_rate_limit(con, key_header):
    tier_info = TIERS.get(key_header) or TIERS.get(None)
    limit = tier_info["limit"]
    if limit is None:
        return True, tier_info["name"], None

    today = str(date.today())
    with _lock:
        row = con.execute(
            "SELECT calls FROM usage_log WHERE key=? AND day=?",
            [key_header or "anon", today]
        ).fetchone()
        calls = row[0] if row else 0
        if calls >= limit:
            return False, tier_info["name"], {"error": f"Rate limit reached ({limit}/day). Upgrade at shortfactory.shop/empire.html", "tier": tier_info["name"], "limit": limit}
        if row:
            con.execute("UPDATE usage_log SET calls=calls+1 WHERE key=? AND day=?", [key_header or "anon", today])
        else:
            con.execute("INSERT INTO usage_log VALUES (?, ?, 1)", [key_header or "anon", today])
    return True, tier_info["name"], None

# ── HANDLER ──
class ShapeHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence default logging

    def send_json(self, data, code=200):
        body = json.dumps(data, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-SF-Key")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-SF-Key")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")
        qs     = parse_qs(parsed.query)
        key    = self.headers.get("X-SF-Key") or qs.get("key", [None])[0]

        con = duckdb.connect(str(DB_PATH))
        try:
            # Health
            if path == "/health":
                count = con.execute("SELECT COUNT(*) FROM shapes").fetchone()[0]
                return self.send_json({"status": "alive", "shapes": count, "version": "1.0"})

            # Stats
            if path == "/stats":
                rows = con.execute("""
                    SELECT type, COUNT(*) as n, AVG(solve_pct) as avg_pct, SUM(api_calls) as calls
                    FROM shapes WHERE public=true GROUP BY type ORDER BY n DESC
                """).fetchall()
                total = con.execute("SELECT COUNT(*), SUM(api_calls) FROM shapes WHERE public=true").fetchone()
                return self.send_json({
                    "total_shapes": total[0],
                    "total_api_calls": total[1] or 0,
                    "by_type": [{"type": r[0], "count": r[1], "avg_solve_pct": round(r[2],1), "api_calls": r[3]} for r in rows]
                })

            # Random shape
            if path == "/shapes/random":
                ok, tier, err = check_rate_limit(con, key)
                if not ok:
                    return self.send_json(err, 429)
                t_filter = qs.get("type", [None])[0]
                where = "WHERE public=true" + (f" AND type='{t_filter}'" if t_filter else "")
                row = con.execute(f"SELECT * FROM shapes {where} ORDER BY random() LIMIT 1").fetchone()
                if not row:
                    return self.send_json({"error": "no shapes found"}, 404)
                con.execute("UPDATE shapes SET api_calls=api_calls+1 WHERE id=?", [row[0]])
                return self.send_json(self._shape_row(row))

            # Similar shapes
            if path.startswith("/shapes/similar/"):
                ok, tier, err = check_rate_limit(con, key)
                if not ok:
                    return self.send_json(err, 429)
                shape_id = path.split("/")[-1]
                src = con.execute("SELECT type FROM shapes WHERE id=?", [shape_id]).fetchone()
                if not src:
                    return self.send_json({"error": "shape not found"}, 404)
                rows = con.execute(
                    "SELECT * FROM shapes WHERE type=? AND id!=? AND public=true ORDER BY solve_pct DESC LIMIT 10",
                    [src[0], shape_id]
                ).fetchall()
                return self.send_json({"shapes": [self._shape_row(r) for r in rows]})

            # Single shape
            if path.startswith("/shapes/") and len(path.split("/")) == 3:
                ok, tier, err = check_rate_limit(con, key)
                if not ok:
                    return self.send_json(err, 429)
                shape_id = path.split("/")[-1]
                row = con.execute("SELECT * FROM shapes WHERE id=? AND public=true", [shape_id]).fetchone()
                if not row:
                    return self.send_json({"error": "not found"}, 404)
                con.execute("UPDATE shapes SET views=views+1, api_calls=api_calls+1 WHERE id=?", [shape_id])
                return self.send_json(self._shape_row(row))

            # List shapes
            if path == "/shapes":
                ok, tier, err = check_rate_limit(con, key)
                if not ok:
                    return self.send_json(err, 429)
                t_filter  = qs.get("type",    [None])[0]
                tag       = qs.get("tag",     [None])[0]
                q         = qs.get("q",       [None])[0]
                limit     = min(int(qs.get("limit", ["20"])[0]), 100)
                offset    = int(qs.get("offset", ["0"])[0])
                sort      = qs.get("sort", ["created_at"])[0]
                if sort not in ("created_at", "solve_pct", "api_calls", "views"):
                    sort = "created_at"

                where = ["public=true"]
                params = []
                if t_filter:
                    where.append("type=?"); params.append(t_filter)
                if tag:
                    where.append("tags LIKE ?"); params.append(f"%{tag}%")
                if q:
                    where.append("(description LIKE ? OR tags LIKE ?)"); params += [f"%{q}%", f"%{q}%"]

                where_sql = "WHERE " + " AND ".join(where) if where else ""
                rows = con.execute(
                    f"SELECT * FROM shapes {where_sql} ORDER BY {sort} DESC LIMIT ? OFFSET ?",
                    params + [limit, offset]
                ).fetchall()
                total = con.execute(f"SELECT COUNT(*) FROM shapes {where_sql}", params).fetchone()[0]
                return self.send_json({
                    "shapes": [self._shape_row(r) for r in rows],
                    "total": total, "limit": limit, "offset": offset
                })

            self.send_json({"error": "not found"}, 404)
        finally:
            con.close()

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")
        key    = self.headers.get("X-SF-Key")

        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}

        con = duckdb.connect(str(DB_PATH))
        try:
            if path == "/shapes":
                ok, tier, err = check_rate_limit(con, key)
                if not ok:
                    return self.send_json(err, 429)

                genome = body.get("genome")
                if not genome or not isinstance(genome, dict):
                    return self.send_json({"error": "genome object required"}, 400)

                shape_type = genome.get("type", "unknown")
                genome_str = json.dumps(genome, separators=(",", ":"))
                shape_id   = str(uuid.uuid4())

                con.execute("""
                    INSERT INTO shapes (id, type, genome, bytes, solve_pct, tags, creator, description, public)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    shape_id, shape_type, genome_str,
                    len(genome_str.encode()),
                    float(body.get("solve_pct", 0)),
                    ",".join(body.get("tags", [])),
                    body.get("creator", "anonymous"),
                    body.get("description", ""),
                    body.get("public", True),
                ])
                return self.send_json({"ok": True, "id": shape_id, "bytes": len(genome_str.encode())}, 201)

            self.send_json({"error": "not found"}, 404)
        finally:
            con.close()

    def _shape_row(self, row):
        cols = ["id","type","genome","bytes","solve_pct","tags","creator",
                "description","public","views","api_calls","created_at"]
        d = dict(zip(cols, row))
        d["genome"] = json.loads(d["genome"]) if isinstance(d["genome"], str) else d["genome"]
        d["tags"]   = [t.strip() for t in (d["tags"] or "").split(",") if t.strip()]
        return d


if __name__ == "__main__":
    print(f"[shape-api] starting on port {PORT}")
    init_db()
    server = HTTPServer(("0.0.0.0", PORT), ShapeHandler)
    print(f"[shape-api] ready — http://0.0.0.0:{PORT}")
    server.serve_forever()
