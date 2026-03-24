"""
Deploy ai-chat, ai-image, ai-browser Workers to Cloudflare.
Run: python deploy_workers.py
"""
import urllib.request, urllib.error, json, os, time

ACCOUNT_ID = '2783e78b87a0ffd54f8e91017e2695b7'
ZONE_ID    = '9129b4cda34c05387385124da0416538'
EMAIL      = 'junky4joy@gmail.com'
API_KEY    = 'cfk_SJFmjqWKIGoNbVHjcWzybTKT9JHqy25h20WmdBvs48cbfe72'

HEADERS = {
    'X-Auth-Email': EMAIL,
    'X-Auth-Key':   API_KEY,
}

BASE = os.path.dirname(os.path.abspath(__file__))

WORKERS = [
    {
        'name':    'ai-chat',
        'script':  os.path.join(BASE, 'workers', 'ai-chat', 'index.js'),
        'subdomain': 'ai-chat',
        'bindings': [{'type': 'ai', 'name': 'AI'}],
    },
    {
        'name':    'ai-image',
        'script':  os.path.join(BASE, 'workers', 'ai-image', 'index.js'),
        'subdomain': 'ai-image',
        'bindings': [{'type': 'ai', 'name': 'AI'}],
    },
    {
        'name':    'ai-browser',
        'script':  os.path.join(BASE, 'workers', 'ai-browser', 'index.js'),
        'subdomain': 'ai-browser',
        'bindings': [
            {'type': 'ai', 'name': 'AI'},
            {'type': 'browser', 'name': 'BROWSER'},
        ],
    },
]


def cf(method, path, data=None, headers=None, raw_body=None, content_type=None):
    url = f'https://api.cloudflare.com/client/v4{path}'
    h = {**HEADERS, 'Content-Type': 'application/json'}
    if headers:
        h.update(headers)
    if content_type:
        h['Content-Type'] = content_type
    body = raw_body if raw_body is not None else (json.dumps(data).encode() if data else None)
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        r = urllib.request.urlopen(req)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def upload_worker(name, script_path, bindings):
    print(f'\n--- Uploading {name} ---')
    with open(script_path, 'rb') as f:
        script_bytes = f.read()

    metadata = {
        'main_module': 'index.js',
        'bindings': bindings,
        'compatibility_date': '2024-09-23',
        'compatibility_flags': ['nodejs_compat'],
    }

    boundary = '----CFBoundary' + str(int(time.time()))
    body = b''
    # metadata part
    body += f'--{boundary}\r\n'.encode()
    body += b'Content-Disposition: form-data; name="metadata"\r\n'
    body += b'Content-Type: application/json\r\n\r\n'
    body += json.dumps(metadata).encode()
    body += b'\r\n'
    # script part
    body += f'--{boundary}\r\n'.encode()
    body += f'Content-Disposition: form-data; name="index.js"; filename="index.js"\r\n'.encode()
    body += b'Content-Type: application/javascript+module\r\n\r\n'
    body += script_bytes
    body += b'\r\n'
    body += f'--{boundary}--\r\n'.encode()

    result = cf(
        'PUT',
        f'/accounts/{ACCOUNT_ID}/workers/scripts/{name}',
        raw_body=body,
        content_type=f'multipart/form-data; boundary={boundary}',
    )
    ok = result.get('success', False)
    print(f'  Upload: {"OK" if ok else "FAIL"}')
    if not ok:
        print(f'  Errors: {result.get("errors")}')
    return ok


def ensure_dns(subdomain):
    """Create A record pointing to placeholder IP (CF proxied) if not exists."""
    fqdn = f'{subdomain}.shortfactory.shop'
    # Check existing
    r = cf('GET', f'/zones/{ZONE_ID}/dns_records?name={fqdn}&type=A')
    existing = r.get('result', [])
    if existing:
        print(f'  DNS A record already exists for {fqdn}')
        return True
    # Create
    r = cf('POST', f'/zones/{ZONE_ID}/dns_records', {
        'type': 'A',
        'name': fqdn,
        'content': '192.0.2.1',  # placeholder, Worker intercepts
        'proxied': True,
        'ttl': 1,
    })
    ok = r.get('success', False)
    print(f'  DNS A record {fqdn}: {"OK" if ok else "FAIL - " + str(r.get("errors"))}')
    return ok


def ensure_route(subdomain, worker_name):
    """Create Worker route pattern → worker."""
    pattern = f'{subdomain}.shortfactory.shop/*'
    # Check existing
    r = cf('GET', f'/zones/{ZONE_ID}/workers/routes')
    for route in r.get('result', []):
        if route.get('pattern') == pattern:
            print(f'  Route already exists: {pattern}')
            return True
    # Create
    r = cf('POST', f'/zones/{ZONE_ID}/workers/routes', {
        'pattern': pattern,
        'script':  worker_name,
    })
    ok = r.get('success', False)
    print(f'  Route {pattern}: {"OK" if ok else "FAIL - " + str(r.get("errors"))}')
    return ok


def ping_worker(subdomain):
    url = f'https://{subdomain}.shortfactory.shop/ping'
    print(f'  Pinging {url} ...')
    try:
        req = urllib.request.Request(url)
        r = urllib.request.urlopen(req, timeout=15)
        data = json.loads(r.read())
        print(f'  Ping: {data}')
        return True
    except Exception as e:
        print(f'  Ping failed: {e}')
        return False


for w in WORKERS:
    name = w['name']
    ok = upload_worker(name, w['script'], w['bindings'])
    if ok:
        ensure_dns(w['subdomain'])
        ensure_route(w['subdomain'], name)
        time.sleep(3)
        ping_worker(w['subdomain'])

print('\nDone.')
