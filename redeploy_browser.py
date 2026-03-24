"""
Redeploy ai-browser Worker with updated timeout fix.
Uses wrangler via subprocess with env vars set cleanly (no shell escaping issues).
"""
import subprocess, os, sys

ACCOUNT_ID = '2783e78b87a0ffd54f8e91017e2695b7'
EMAIL      = 'junky4joy@gmail.com'
API_KEY    = 'cfk_SJFmjqWKIGoNbVHjcWzybTKT9JHqy25h20WmdBvs48cbfe72'

worker_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workers', 'ai-browser-bundled')

env = os.environ.copy()
env['CLOUDFLARE_EMAIL']      = EMAIL
env['CLOUDFLARE_API_KEY']    = API_KEY
env['CLOUDFLARE_ACCOUNT_ID'] = ACCOUNT_ID
env.pop('CLOUDFLARE_API_TOKEN', None)

print('Deploying ai-browser from:', worker_dir)
result = subprocess.run(
    [r'C:\Program Files\nodejs\npx.cmd', 'wrangler', 'deploy'],
    cwd=worker_dir,
    env=env,
    capture_output=True,
)
import re
ansi = re.compile(r'\x1b\[[0-9;]*m')
stdout = ansi.sub('', result.stdout.decode('utf-8', errors='replace'))
stderr = ansi.sub('', result.stderr.decode('utf-8', errors='replace'))
with open('deploy_browser.log', 'w', encoding='utf-8') as f:
    f.write('RETURN CODE: ' + str(result.returncode) + '\n\nSTDOUT:\n' + stdout + '\n\nSTDERR:\n' + stderr)
print('Done. Return code:', result.returncode, '— see deploy_browser.log')
