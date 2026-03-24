"""
Eye Bridge — localhost:8766
Connects alive/eye.html visual cortex to the multi-eye-transform-engine.

Endpoints:
  GET  /ping      → {"status":"ok","version":"1.0"}
  POST /classify  → body: {frame, mode, time} → {"objects":[{label, confidence}]}

The swarm samples the image in 2D, clustering presence/absence fields
into semantic descriptors that become shape-genomes in the frontend.
Pure Python + optional Pillow — no heavy ML required.
"""

import http.server
import json
import base64
import io
import math
import random
import time
import struct
import zlib
from urllib.parse import urlparse

PORT = 8766

# ── Image decoder (Pillow if available, fallback to raw JPEG luma) ────────────

def decode_image(b64_data):
    """Returns list of (r,g,b) tuples from base64 data-URL image."""
    # Strip data-URL header
    if ',' in b64_data:
        b64_data = b64_data.split(',', 1)[1]
    raw = base64.b64decode(b64_data)

    try:
        from PIL import Image
        img = Image.open(io.BytesIO(raw)).convert('RGB').resize((64, 64))
        pixels = list(img.getdata())
        return pixels, 64, 64
    except ImportError:
        pass

    # Fallback: crude JPEG luma extraction via DCT-skip byte scan
    # Just sample raw bytes as pseudo-pixel brightness values
    luma = [b for b in raw[2:] if b > 10]
    if not luma:
        luma = [128] * (64 * 64)
    # Pad/truncate to 64x64
    size = 64 * 64
    luma = (luma * ((size // len(luma)) + 1))[:size]
    pixels = [(v, v, v) for v in luma]
    return pixels, 64, 64


# ── Swarm field ───────────────────────────────────────────────────────────────

class PixelSpace:
    """Wraps pixel grid so spiders can query presence/absence."""
    def __init__(self, pixels, w, h):
        self.px = pixels
        self.w = w
        self.h = h

    def query(self, x, y, threshold=0.4):
        """Returns True (presence) if normalised brightness > threshold."""
        ix = int((x + 1) / 2 * (self.w - 1))
        iy = int((y + 1) / 2 * (self.h - 1))
        r, g, b = self.px[iy * self.w + ix]
        luma = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luma > threshold

    def sample_rgb(self, x, y):
        ix = int((x + 1) / 2 * (self.w - 1))
        iy = int((y + 1) / 2 * (self.h - 1))
        return self.px[iy * self.w + ix]


def swarm_sample(space, n=200):
    """Run n spiders across the image, return hit positions + colours."""
    hits = []
    misses = []
    colours = []
    for _ in range(n):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        hit = space.query(x, y)
        rgb = space.sample_rgb(x, y)
        colours.append(rgb)
        if hit:
            hits.append((x, y))
        else:
            misses.append((x, y))
    return hits, misses, colours


# ── Feature extraction → descriptor words ────────────────────────────────────

COLOUR_MAP = [
    # (R_min, G_min, B_min, R_max, G_max, B_max, label, confidence)
    (200, 0,   0,   255, 80,  80,  'crimson',  0.85),
    (180, 50,  0,   255, 150, 60,  'ember',    0.80),
    (200, 180, 0,   255, 255, 80,  'gold',     0.82),
    (0,   160, 0,   80,  255, 80,  'viridian', 0.80),
    (0,   180, 180, 60,  255, 255, 'cyan',     0.80),
    (0,   0,   180, 60,  80,  255, 'azure',    0.82),
    (160, 0,   200, 230, 80,  255, 'violet',   0.80),
    (200, 0,   180, 255, 80,  240, 'magenta',  0.80),
    (200, 200, 200, 255, 255, 255, 'blaze',    0.75),
    (0,   0,   0,   60,  60,  60,  'void',     0.75),
    (80,  80,  80,  180, 180, 180, 'shadow',   0.72),
    (180, 140, 100, 255, 200, 160, 'earth',    0.72),
    (100, 160, 220, 160, 210, 255, 'sky',      0.78),
]

def dominant_colour(colours):
    """Find most common colour cluster from sampled pixels."""
    avg_r = sum(c[0] for c in colours) / len(colours)
    avg_g = sum(c[1] for c in colours) / len(colours)
    avg_b = sum(c[2] for c in colours) / len(colours)

    best = None
    best_dist = float('inf')
    best_label = ('spectrum', 0.6)

    for (rmin, gmin, bmin, rmax, gmax, bmax, label, conf) in COLOUR_MAP:
        cr = (rmin + rmax) / 2
        cg = (gmin + gmax) / 2
        cb = (bmin + bmax) / 2
        dist = math.sqrt((avg_r - cr)**2 + (avg_g - cg)**2 + (avg_b - cb)**2)
        if dist < best_dist:
            best_dist = dist
            best_label = (label, conf)

    return best_label


def edge_density(hits, misses):
    """Estimate edge density by checking hit/miss boundary proximity."""
    if not hits or not misses:
        return 0.0
    edges = 0
    for hx, hy in hits[:50]:
        for mx, my in misses[:50]:
            if abs(hx - mx) < 0.15 and abs(hy - my) < 0.15:
                edges += 1
                break
    return edges / 50


def spatial_distribution(hits, total):
    """Returns descriptor for where brightness clusters."""
    if not hits:
        return ('void', 0.9)
    cx = sum(h[0] for h in hits) / len(hits)
    cy = sum(h[1] for h in hits) / len(hits)
    spread = sum(math.sqrt(h[0]**2 + h[1]**2) for h in hits) / len(hits)
    density = len(hits) / total

    if density > 0.7:
        return ('saturate', 0.8)
    if density < 0.2:
        return ('sparse', 0.78)
    if spread < 0.3:
        return ('nucleus', 0.82)
    if abs(cx) < 0.15 and abs(cy) < 0.15:
        return ('centred', 0.80)
    if cy < -0.3:
        return ('apex', 0.75)
    if cy > 0.3:
        return ('nadir', 0.75)
    return ('scatter', 0.72)


def brightness_band(colours):
    lumas = [(0.299*r + 0.587*g + 0.114*b) / 255 for r, g, b in colours]
    avg = sum(lumas) / len(lumas)
    variance = sum((l - avg)**2 for l in lumas) / len(lumas)
    std = math.sqrt(variance)

    if avg > 0.75:
        return ('radiant', 0.82)
    if avg < 0.2:
        return ('abyss', 0.82)
    if std > 0.25:
        return ('contrast', 0.80)
    if std < 0.08:
        return ('uniform', 0.72)
    return ('twilight', 0.70)


def edge_word(density):
    if density > 0.4:
        return ('fractal', 0.85)
    if density > 0.2:
        return ('boundary', 0.78)
    if density > 0.1:
        return ('gradient', 0.72)
    return ('smooth', 0.65)


# ── Mode-specific vocabulary injection ───────────────────────────────────────

QUBIT_VOCAB    = ['superposition', 'collapse', 'entangle', 'observe', 'wave', 'coherent', 'phase', 'tunnel']
SINGULARITY_VOCAB = ['consume', 'horizon', 'rupture', 'singular', 'infinite', 'crush', 'devour', 'escape']

def mode_label(mode):
    pool = QUBIT_VOCAB if mode == 'qubit' else SINGULARITY_VOCAB
    return (random.choice(pool), round(0.5 + random.random() * 0.35, 2))


# ── Session memory (presence field across frames) ────────────────────────────

_session = {
    'frame_count': 0,
    'last_hits': [],
    'last_colours': [],
    'last_time': 0,
}

def motion_word(hits):
    """Compare current hits to last frame to detect motion."""
    prev = _session['last_hits']
    if not prev or not hits:
        return None
    # Simple centroid delta
    cx = sum(h[0] for h in hits) / len(hits)
    cy = sum(h[1] for h in hits) / len(hits)
    pcx = sum(h[0] for h in prev) / len(prev)
    pcy = sum(h[1] for h in prev) / len(prev)
    delta = math.sqrt((cx - pcx)**2 + (cy - pcy)**2)
    if delta > 0.15:
        return ('motion', min(0.95, 0.6 + delta))
    if delta < 0.03:
        return ('still', 0.75)
    return None


# ── Main classify ─────────────────────────────────────────────────────────────

def classify(frame_b64, mode='qubit', t=0):
    objects = []

    try:
        pixels, w, h = decode_image(frame_b64)
        space = PixelSpace(pixels, w, h)
        hits, misses, colours = swarm_sample(space, n=300)

        # Motion check
        mv = motion_word(hits)
        if mv:
            objects.append({'label': mv[0], 'confidence': round(mv[1], 2)})

        # Colour
        col, conf = dominant_colour(colours)
        objects.append({'label': col, 'confidence': conf})

        # Brightness
        bw, bc = brightness_band(colours)
        objects.append({'label': bw, 'confidence': bc})

        # Edge
        ed = edge_density(hits, misses)
        ew, ec = edge_word(ed)
        objects.append({'label': ew, 'confidence': ec})

        # Spatial
        sl, sc = spatial_distribution(hits, 300)
        objects.append({'label': sl, 'confidence': sc})

        # Mode word (qubit/singularity vocabulary)
        ml, mc = mode_label(mode)
        objects.append({'label': ml, 'confidence': mc})

        # Focus centroid — where the swarm is concentrated (normalised -1..1)
        focus = {'x': 0.0, 'y': 0.0, 'locked': False}
        if hits:
            fcx = round(sum(h[0] for h in hits) / len(hits), 3)
            fcy = round(sum(h[1] for h in hits) / len(hits), 3)
            # Spread: tight cluster = locked, wide scatter = scanning
            spread = sum(math.sqrt((h[0]-fcx)**2 + (h[1]-fcy)**2) for h in hits) / len(hits)
            focus = {'x': fcx, 'y': fcy, 'locked': spread < 0.45}

        # Update session
        _session['last_hits'] = hits
        _session['last_colours'] = colours
        _session['frame_count'] += 1
        _session['last_time'] = t

    except Exception as e:
        # Fallback: return generic observational vocabulary
        vocab = ['presence', 'absence', 'field', 'ripple', 'node', 'signal']
        objects = [{'label': random.choice(vocab), 'confidence': round(0.5 + random.random() * 0.4, 2)}
                   for _ in range(3)]
        focus = {'x': 0.0, 'y': 0.0, 'locked': False}

    return objects, focus


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class BridgeHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # silence default access log

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/ping':
            self.send_json(200, {
                'status': 'ok',
                'version': '1.0',
                'frames': _session['frame_count'],
                'engine': 'multi-eye-transform-engine'
            })
        elif path == '/status':
            self.send_json(200, {
                'frames': _session['frame_count'],
                'last_time': _session['last_time'],
                'session_start': _session.get('start_time', 0)
            })
        else:
            self.send_json(404, {'error': 'not found'})

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else b'{}'

        try:
            data = json.loads(body)
        except Exception:
            self.send_json(400, {'error': 'invalid json'})
            return

        if path == '/classify':
            frame = data.get('frame', '')
            mode  = data.get('mode', 'qubit')
            t     = data.get('time', 0)

            if not frame:
                self.send_json(400, {'error': 'no frame'})
                return

            objects, focus = classify(frame, mode, t)
            self.send_json(200, {'objects': objects, 'focus': focus, 'frames': _session['frame_count']})

        elif path == '/learn':
            # Hebbian: reinforce a label from user feedback
            label = data.get('label', '')
            signal = data.get('signal', 1)  # +1 thumbs up, -1 thumbs down
            # (stored in memory for future predictor use — stub for now)
            self.send_json(200, {'ok': True, 'label': label, 'signal': signal})

        else:
            self.send_json(404, {'error': 'not found'})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    _session['start_time'] = time.time()
    server = http.server.HTTPServer(('localhost', PORT), BridgeHandler)
    print(f'🌀 Eye Bridge running on http://localhost:{PORT}')
    print(f'   /ping      — health check')
    print(f'   /classify  — POST {{frame, mode, time}} → objects[]')
    print(f'   /learn     — POST {{label, signal}} — Hebbian feedback')
    print(f'   Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n👁 Bridge closed.')
