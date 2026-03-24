"""
Targeted purge: ONLY remove the specific node we KNOW was planted by tamperers.
Everything else stays — Dan uses questions as definitions legitimately.
"""
import json, os, time, shutil

STUDIO = '/var/www/vhosts/shortfactory.shop/httpdocs/alive/studio'

# The ONLY nodes we are certain were planted
CONFIRMED_BAD = {'invisible_bonds', 'invisible_bond'}

def purge_brain(filepath, label):
    print(f'\n=== {label} ===')
    with open(filepath, 'r') as f:
        data = json.load(f)
    nodes = data.get('nodes', {})
    removed = []
    for word in CONFIRMED_BAD:
        if word in nodes:
            print(f'  FOUND and removing: [{word}] = "{nodes[word].get("means","?")}"')
            del nodes[word]
            removed.append(word)
        else:
            print(f'  Not present: [{word}]')
    if removed:
        bak = filepath + '.pre_purge_' + time.strftime('%Y%m%d_%H%M%S')
        shutil.copy2(filepath, bak)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        print(f'  Saved. Removed: {removed}')
    else:
        print('  Nothing removed.')
    return removed

# Check truth engine for planted "beauty -> bad" cross link
def check_truth_engine():
    te_path = os.path.join(STUDIO, 'truth_engine.json')
    if not os.path.exists(te_path):
        return
    print('\n=== TRUTH ENGINE ===')
    with open(te_path, 'r') as f:
        data = json.load(f)
    # Print top-level keys and size
    for k, v in data.items():
        if isinstance(v, dict):
            print(f'  [{k}]: {len(v)} entries')
        elif isinstance(v, list):
            print(f'  [{k}]: {len(v)} items')
        else:
            print(f'  [{k}]: {str(v)[:60]}')

    # Scan word_truth for beauty/demon/invisible specifically
    wt = data.get('word_truth', {})
    for word in ['beauty', 'invisible_bonds', 'demon', 'evil', 'bad']:
        if word in wt:
            print(f'  word_truth[{word}] = {str(wt[word])[:120]}')

purge_brain(os.path.join(STUDIO, 'left',  'brain.json'), 'LEFT')
purge_brain(os.path.join(STUDIO, 'right', 'brain.json'), 'RIGHT')
check_truth_engine()
print('\nDone.')
