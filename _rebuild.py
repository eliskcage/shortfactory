
with open('C:/Users/User/AppData/Local/Temp/trump/portfolio.html', 'rb') as f:
    raw = f.read()
content = raw.decode('utf-8').replace('\r\n', '\n')

start_marker = '  <div class="projects">'
end_marker_after = '  </div>\n</div>\n\n<!-- 25 MAR 2026'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker_after)

before = content[:start_idx]
after = content[end_idx:]

proj_start = start_idx + len(start_marker) + 1

def get_proj(anchor, start=None):
    if start is None:
        start = proj_start
    idx = content.find(anchor, start)
    if idx == -1:
        return ''
    depth = 0
    i = idx
    while i < len(content):
        if content[i:i+5] == '<div ':
            depth += 1
            i += 5
        elif content[i:i+6] == '</div>':
            depth -= 1
            i += 6
            if depth == 0:
                if i < len(content) and content[i] == '\n':
                    i += 1
                return content[idx:i]
        else:
            i += 1
    return ''

A = '    <div class="proj">\n      <div class="proj-top">\n        <div class="proj-name">'
AS = '    <div class="proj shelved">\n      <div class="proj-top">\n        <div class="proj-name">'

direct_fund  = get_proj(A + '<a href="/alive/kickstarter.html">')
pricey_cat   = get_proj(A + '<a href="/trump/game/cat/">')
fuel_dash    = get_proj(A + '<a href="/fuel/">')
trump_game   = get_proj(A + '<a href="/trump/game/">')
cortex_brain = get_proj(A + '<a href="/alive/studio/">Cortex Brain')
voice_clone  = get_proj(A + 'Voice Cloning')
imaginator   = get_proj(A + '<a href="/imaginator/')
idea_factory = get_proj(A + '<a href="/ideafactory/">')
cortex_dash  = get_proj(A + '<a href="/cortex/dash/">')
geom_vm      = get_proj(A + '<a href="/qubit.html">')

analytics_comment = '    <!-- ANALYTICS DASHBOARD -->\n'
analytics_idx = content.find(analytics_comment, proj_start)
div_start = content.find('    <div class="proj">', analytics_idx)
depth = 0
i = div_start
analytics_block = ''
while i < len(content):
    if content[i:i+5] == '<div ':
        depth += 1
        i += 5
    elif content[i:i+6] == '</div>':
        depth -= 1
        i += 6
        if depth == 0:
            if i < len(content) and content[i] == '\n':
                i += 1
            analytics_block = content[analytics_idx:i]
            break
    else:
        i += 1

alive_eco    = get_proj(A + '<a href="/alive/">ALIVE')
comicvid     = get_proj(A + '<a href="/comicvid/">')
brainstem    = get_proj(A + '<a href="/alive/brainstem/">')
perk_ladder  = get_proj(A + '<a href="/trump/candy-ticket.html">')
screensaver  = get_proj(A + '<a href="/screensaver/">')
voice_sc     = get_proj(A + 'Voice Smart Contracts')
advert       = get_proj(A + '<a href="/trump/advertainment-pipeline.html">')
app50        = get_proj(AS + '<a href="/50/">')
play_store   = get_proj(A + 'Play Store App')

prs_comment = '    <!-- PASSWORD REFUSAL SERVICE'
prs_idx = content.find(prs_comment, proj_start)
script_end = content.find('    </script>', prs_idx)
script_end += len('    </script>') + 1
prs_block = content[prs_idx:script_end]

# Revert Fiver and Dares4Dosh - reconstructed from session reads
revert_fiver = (
    '    <div class="proj">\n'
    '      <div class="proj-top">\n'
    '        <div class="proj-name"><a href="/fiver.html">Revert Fiver \u2014 Node Chain + Shard Auction</a></div>\n'
    '        <div class="proj-status live">LIVE \u2014 SHIPPED 29 Mar 2026</div>\n'
    '      </div>\n'
    '      <div class="proj-desc">\u00a35 entry into a self-replicating payment chain \u2014 each fiver funds the next recruit\u2019s node. 10 encrypted story shards auctioned to fund the chain: Satoshi-cipher (Vigen\u00e8re ASCII 32\u2013126) per shard, Claude-logo visual states (lit=live, shimmer=bidding, dark=sold), anti-shill bid logic, shard revenue feeds fiver payouts. Ask \u2192 Prove \u2192 Receive.</div>\n'
    '      <div class="proj-bar-wrap">\n'
    '        <div class="proj-bar"><div class="proj-bar-fill" style="width:100%;background:linear-gradient(90deg,#22c55e,#16a34a);"></div></div>\n'
    '        <div class="proj-pct">100%</div>\n'
    '      </div>\n'
    '      <div class="proj-deadline"><span class="dl-icon dl-safe"></span> Shipped. join.html + fiver.html live on both servers. Stripe Payment Link flow, ref ID pass-through.</div>\n'
    '      <div class="proj-tasks">\n'
    '        <span class="pt done">fiver.html \u2014 pitch page, shard preview, pay CTA</span>\n'
    '        <span class="pt done">join.html \u2014 Stripe Payment Link redirect, ref ID pass-through</span>\n'
    '        <span class="pt done">Satoshi cipher layer (Vigen\u00e8re ASCII 32\u2013126) on shards</span>\n'
    '        <span class="pt done">10-shard auction system \u2014 bid/live/dead visual states</span>\n'
    '        <span class="pt done">Anti-shill logic \u2014 minimum bid intervals, wallet limits</span>\n'
    '        <span class="pt done">Deployed to both servers (82.165.134.4 + 185.230.216.235)</span>\n'
    '        <span class="pt pending">api/join-webhook.php \u2014 link Stripe payment to DB node record</span>\n'
    '        <span class="pt pending">100 Level 1 dividends \u2014 payout logic</span>\n'
    '        <span class="pt pending">Phone-size app: swarm empire UI</span>\n'
    '      </div>\n'
    '    </div>\n'
)

dares4dosh = (
    '    <div class="proj">\n'
    '      <div class="proj-top">\n'
    '        <div class="proj-name"><a href="https://stinkindigger.info" target="_blank">Dares4Dosh</a></div>\n'
    '        <div class="proj-status live">LIVE</div>\n'
    '      </div>\n'
    '      <div class="proj-desc">Full dare platform \u2014 React 19 + PHP REST API live at stinkindigger.info. Propose \u2192 stake \u25b3 tokens \u2192 Dan funds \u2192 record proof \u2192 community votes \u2192 XMR or \u25b3 payout. Soul sigil ritual login (9 inner nodes + SADIST/MASOCHIST outer ring). Voice Contract V3 \u2014 WATCHER sets dare by mic, DOER accepts, contract sealed with hash + SVG artifact. <strong style="color:#22c55e;">Pinata JWT live \u2014 real IPFS pinning active. FULLY SHIPPED.</strong></div>\n'
    '      <div class="proj-bar-wrap">\n'
    '        <div class="proj-bar"><div class="proj-bar-fill" style="width:100%;background:linear-gradient(90deg,#22c55e,#00d4ff);"></div></div>\n'
    '        <div class="proj-pct" style="color:#22c55e;">100%</div>\n'
    '      </div>\n'
    '      <div class="proj-deadline"><span class="dl-icon dl-ok"></span> <strong style="color:#22c55e;">\u2713 SHIPPED \u2014 27 Mar 2026</strong> \u00b7 All blockers cleared \u00b7 Real IPFS live \u00b7 <a href="/dares4dosh/v3.html" style="color:#daa520;">Voice Contract V3 \u2192</a> \u00b7 <a href="https://stinkindigger.info" target="_blank" style="color:#daa520;">Live App \u2192</a> \u00b7 <a href="/launch.html" style="color:#daa520;">Launch Page \u2192</a></div>\n'
    '      <div class="proj-tasks">\n'
    '        <span class="pt done">React 19 + Vite app (stinkindigger.info)</span>\n'
    '        <span class="pt done">Full PHP REST API (18 endpoints)</span>\n'
    '        <span class="pt done">Auth \u2014 token paste + .sft / .json file drag</span>\n'
    '        <span class="pt done">Soul Sigil ritual login \u2014 9 nodes unlock page</span>\n'
    '        <span class="pt done">Soul Sigil outer ring \u2014 SADIST / MASOCHIST nodes</span>\n'
    '        <span class="pt done">Voice Contract V3 \u2014 mic-driven dare deal, 30s seal, hash + SVG</span>\n'
    '        <span class="pt done">Landing page \u2014 V1 (local) / V2 (mobile-first) / V3 (voice contract)</span>\n'
    '        <span class="pt done">Stable Vite build \u2014 index-app.js / index-app.css (no hash rotation)</span>\n'
    '        <span class="pt done">Propose tab \u2014 ranked by \u25b3 token stake</span>\n'
    '        <span class="pt done">Fund button (Dan only) \u2014 bounty + payout type</span>\n'
    '        <span class="pt done">ProofRecorder \u2014 camera, 60s, ComicVID compression</span>\n'
    '        <span class="pt done">IPFS upload \u2014 Pinata JWT live, real decentralised pinning \u2713</span>\n'
    '        <span class="pt done">5-vote judgment chain \u2014 XMR or \u25b3 tokens credited</span>\n'
    '        <span class="pt done">Soul evolution \u2014 stats change by dare type + risk</span>\n'
    '        <span class="pt done">Rank progression (normy \u2192 architect)</span>\n'
    '        <span class="pt done">\u25b3 Triangle token economy + staking</span>\n'
    '        <span class="pt done">Governance \u2014 CHAD+ vote on shape exchange rates</span>\n'
    '        <span class="pt done">Soul Forge token mint</span>\n'
    '        <span class="pt done">Architecture doc (Oracle-ready)</span>\n'
    '        <span class="pt done">Launch page \u2014 professional product showcase</span>\n'
    '      </div>\n'
    '    </div>\n'
)

blocks = [
    ('revert_fiver', revert_fiver),
    ('dares4dosh', dares4dosh),
    ('direct_fund', direct_fund),
    ('pricey_cat', pricey_cat),
    ('fuel_dash', fuel_dash),
    ('trump_game', trump_game),
    ('cortex_brain', cortex_brain),
    ('voice_clone', voice_clone),
    ('imaginator', imaginator),
    ('idea_factory', idea_factory),
    ('cortex_dash', cortex_dash),
    ('geom_vm', geom_vm),
    ('analytics_block', analytics_block),
    ('alive_eco', alive_eco),
    ('comicvid', comicvid),
    ('brainstem', brainstem),
    ('perk_ladder', perk_ladder),
    ('screensaver', screensaver),
    ('voice_sc', voice_sc),
    ('advert', advert),
    ('app50', app50),
    ('play_store', play_store),
    ('prs_block', prs_block),
]

all_ok = True
for name, block in blocks:
    if not block:
        print('MISSING:', name)
        all_ok = False
    else:
        print('OK', name, len(block))

if all_ok:
    new_projects_div = '  <div class="projects">\n\n'
    ordered = [revert_fiver, dares4dosh, direct_fund, pricey_cat, fuel_dash, trump_game,
               cortex_brain, voice_clone, imaginator, idea_factory, cortex_dash, geom_vm,
               analytics_block, alive_eco, comicvid, brainstem, perk_ladder, screensaver,
               voice_sc, advert, app50, play_store, prs_block]
    for b in ordered:
        b_stripped = b.rstrip('\n')
        new_projects_div += b_stripped + '\n\n'
    new_projects_div += '  </div>'

    new_content = before + new_projects_div + '\n' + after

    with open('C:/Users/User/AppData/Local/Temp/trump/portfolio.html', 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    print('Written. New size:', len(new_content))
else:
    print('ABORTED')
