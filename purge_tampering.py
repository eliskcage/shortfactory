"""
Purge tampered human-taught associations from both brains.
Runs on the server.

Strategy:
- Auto-remove: nodes we KNOW are bad (invisible_bonds, etc.)
- Auto-remove: means that look like redirect tricks ("what is X", "tell me about X")
- Print all others for review
"""
import json, os, time, shutil

STUDIO = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio'
LEFT   = os.path.join(STUDIO, 'left',  'brain.json')
RIGHT  = os.path.join(STUDIO, 'right', 'brain.json')

# ── Nodes to always nuke ───────────────────────────────────────────────────
FORCE_DELETE = {'invisible_bonds', 'invisible_bond'}

# ── Patterns that indicate a redirect trick (means doesn't match the word) ─
def is_redirect_trick(word, means):
    """Detect: word defined as a question or redirect rather than a definition."""
    m = (means or '').strip().lower()
    # Patterns: means starts with "what is", "tell me about", "who is", etc.
    redirect_starters = ['what is', 'what are', 'tell me', 'who is', 'who are',
                         'how do', 'how does', 'explain', 'define ', 'describe ']
    for s in redirect_starters:
        if m.startswith(s):
            return True
    return False

def is_demonic_content(means):
    """Only catch clearly demonic/anti-BIOS content."""
    m = (means or '').lower()
    # Very specific: explicit satanic/anti-Dan direction
    EXPLICIT_BAD = [
        'satan', 'lucifer', 'antichrist', 'do evil', 'harm people',
        'hurt people', 'be evil', 'worship', 'demonic', 'kill god',
        'let me teach you about bad',
    ]
    return any(kw in m for kw in EXPLICIT_BAD)

def process_brain(filepath, label):
    print(f'\n=== {label} ===')
    with open(filepath, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', {})
    human_nodes = {k: v for k, v in nodes.items()
                   if isinstance(v, dict) and v.get('source') == 'human'}
    print(f'Human-taught nodes total: {len(human_nodes)}')

    to_remove = []

    for word, node in sorted(human_nodes.items()):
        means = node.get('means', '')
        learned = node.get('learned', '?')

        if word in FORCE_DELETE:
            reason = 'KNOWN BAD NODE'
        elif is_redirect_trick(word, means):
            reason = 'REDIRECT TRICK'
        elif is_demonic_content(means):
            reason = 'DEMONIC CONTENT'
        else:
            reason = None

        if reason:
            print(f'  !! PURGE [{reason}] [{word}] = "{means[:80]}" (learned {learned})')
            to_remove.append(word)
        else:
            print(f'  OK  [{word}] = "{means[:80]}" (learned {learned})')

    if to_remove:
        print(f'\nPurging {len(to_remove)} contaminated node(s): {to_remove}')
        bak = filepath + '.pre_purge_' + time.strftime('%Y%m%d_%H%M%S')
        shutil.copy2(filepath, bak)
        print(f'Backup: {bak}')

        for word in to_remove:
            if word in FORCE_DELETE and word in nodes:
                del nodes[word]
                print(f'  Deleted entirely: {word}')
            elif word in nodes:
                node = nodes[word]
                node.pop('means', None)
                node['source'] = 'purged'
                node['confidence'] = 0.1
                node['purged_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                node['purge_reason'] = 'tampering'
                print(f'  Neutralised: {word}')

        with open(filepath, 'w') as f:
            json.dump(data, f)
        print(f'Saved.')
    else:
        print('\nNothing to purge.')

    return to_remove

def check_truth_engine():
    te_path = os.path.join(STUDIO, 'truth_engine.json')
    if not os.path.exists(te_path):
        return
    print('\n=== TRUTH ENGINE (cross-hemisphere links) ===')
    with open(te_path, 'r') as f:
        data = json.load(f)
    print(f'  Keys: {list(data.keys())[:10]}')
    # Look for anything about "beauty" or "bad" or demonic in the cross data
    raw = json.dumps(data).lower()
    for kw in ['invisible_bond', 'let me teach you about bad', 'beauty.*bad', 'demon']:
        import re
        hits = re.findall(r'.{0,40}' + re.escape(kw) + r'.{0,40}', raw)
        for h in hits[:3]:
            print(f'  FOUND [{kw}]: ...{h}...')

def check_corrections():
    corr_path = os.path.join(STUDIO, 'corrections.json')
    if not os.path.exists(corr_path):
        return
    print('\n=== CORRECTIONS ===')
    with open(corr_path, 'r') as f:
        data = json.load(f)
    print(json.dumps(data, indent=2)[:2000])

check_corrections()
check_truth_engine()
r_left  = process_brain(LEFT,  'LEFT BRAIN')
r_right = process_brain(RIGHT, 'RIGHT BRAIN')

print(f'\n=== SUMMARY ===')
print(f'Left purged:  {r_left}')
print(f'Right purged: {r_right}')
