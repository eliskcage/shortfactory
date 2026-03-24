import html as html_mod

KEY = 'SKYDADDY'
FILE = r'C:\Users\User\AppData\Local\Temp\trump\about.html'

def satoshi_encode(text, key):
    result = []
    for i, c in enumerate(text):
        if 32 <= ord(c) <= 126:
            k = key[i % len(key)]
            encoded = chr(((ord(c) - 32) + (ord(k) - 32)) % 95 + 32)
            result.append(encoded)
        else:
            result.append(c)
    return ''.join(result)

def enc(text):
    return html_mod.escape(satoshi_encode(text, KEY))

lbl  = enc('21 March 2026 - SIGHT & INVERSE PROGRAMS')
hdg  = enc('The creatures can see now. And the machine can find the program from the answer.')
p1   = enc("Two fundamental capabilities arrived in the same session. First: the ALIVE creatures got eyes. Not a camera feed - a distributed swarm intelligence that builds a probabilistic 3D model of the world from partial observations, exactly as a brain builds a model of a room from a handful of glances. Second: the inverse program engine - given an input and a desired output, the system finds the chain of transforms that produces it, learns from every solution, and gets faster each time. The first is sight. The second is something older than sight: the ability to ask what had to happen for this to be true.")
p2   = enc("Multi-Eye Transform Engine. A swarm of 50 sampling agents - spiders - explore 3D space and report back. Each spider operates independently and as part of a coordinated swarm, detecting presence of structure and confirming absence in empty regions. The system maintains two complementary fields simultaneously: a presence field (where structure IS, with confidence scores increasing through repeated observation) and an absence field (regions confirmed empty, acting as a constraint that eliminates impossible geometries). The result is a probabilistic node field - a shape genome - representing the object as a distribution of possible forms rather than a single fixed mesh. Context priors boost early prediction: a spider swarm deployed in a shoe shop already knows what it is likely looking at before the scan completes. Multiple user devices aggregate their observations - every scan from every phone reinforces the same shared genome. Crowd-sourced 3D sight, incentivised by credits.")
p3   = enc("Inverse Programs. Traditional programming: you write the program, it produces output. Inverse programs: you have the input and the output, and the system finds the program that connects them. The engine tries predicted chains first (the transforms that have worked most often before), falls back to exhaustive permutation search if needed, reinforces every successful solution in memory, and converges faster on each new problem. Currently demonstrated on text transforms - lower, clean, sort, reverse - but the architecture is universal. The same principle applies to any transform space: images, genomes, 3D shapes, code. Given any before and after, find the procedure. This is what the Cortex brain does with language. This is what sight does with space. This is what the shape genome does with matter. One principle, everywhere.")
p4   = enc("Genomic Cat - shipped. The 3D genomic cat demo reached production state: real genome-driven cat with emotion HUD, angular SVG shape rendering, Satoshi cookie persistence, carousel insertion, deployed to both servers.")
q1   = enc("The spider swarm and the inverse engine are the same idea from opposite directions. One asks: what is out there? The other asks: what had to happen for this to exist? Both are sight.")
qa   = enc("- Dan & Claude, 21 March 2026")
shp  = enc('SHIPPED - 21 MAR 2026')
f1n  = enc('multi-eye-transform-engine/')
f1d  = enc('Distributed spider swarm, dual presence/absence fields, probabilistic shape genome, context-aware prediction, crowdsourced 3D object reconstruction. Python skeleton + patent in principle.')
f2n  = enc('engine.py / brain_shredder.py')
f2d  = enc('Inverse program synthesis. Memory-guided transform chain prediction, exhaustive fallback search, Hebbian reinforcement. Given input + target: find the program.')
f3n  = enc('genomic-cats2.html')
f3d  = enc('3D genome-driven cat. Emotion HUD, angular SVG shape rendering, Satoshi cookie persistence, carousel insertion, deployed to both servers.')

new_section = (
    '<!-- SESSION: 21 MARCH 2026 \u2014 SIGHT + INVERSE PROGRAMS -->\n'
    '  <div class="section">\n'
    '    <div class="section-label" style="color:#00e5ff;text-shadow:0 0 20px rgba(0,229,255,0.4)">' + lbl + '</div>\n'
    '    <div class="section-heading" style="color:#00e5ff;text-shadow:0 0 30px rgba(0,229,255,0.3)">' + hdg + '</div>\n\n'
    '    <p style="font-size:17px;line-height:1.9;margin-bottom:28px;">' + p1 + '</p>\n\n'
    '    <p style="font-size:16px;line-height:1.9;margin-bottom:20px;">' + p2 + '</p>\n\n'
    '    <p style="font-size:16px;line-height:1.9;margin-bottom:20px;">' + p3 + '</p>\n\n'
    '    <p style="font-size:16px;line-height:1.9;margin-bottom:20px;">' + p4 + '</p>\n\n'
    '    <div class="quote" style="border-left-color:#00e5ff">\n'
    '      ' + q1 + '\n'
    '      <div class="quote-attr">' + qa + '</div>\n'
    '    </div>\n\n'
    '    <div style="font-family:\'Press Start 2P\',monospace;font-size:9px;color:#00e5ff;letter-spacing:2px;margin-bottom:16px;margin-top:28px;text-align:center">' + shp + '</div>\n'
    '    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;margin-bottom:20px">\n'
    '      <div style="padding:10px 14px;background:rgba(0,229,255,0.05);border:1px solid rgba(0,229,255,0.15);border-radius:8px;font-size:12px"><span style="color:#00e5ff;font-weight:700">' + f1n + '</span> <span style="color:#666">' + f1d + '</span></div>\n'
    '      <div style="padding:10px 14px;background:rgba(0,229,255,0.05);border:1px solid rgba(0,229,255,0.15);border-radius:8px;font-size:12px"><span style="color:#00e5ff;font-weight:700">' + f2n + '</span> <span style="color:#666">' + f2d + '</span></div>\n'
    '      <div style="padding:10px 14px;background:rgba(0,229,255,0.05);border:1px solid rgba(0,229,255,0.15);border-radius:8px;font-size:12px"><span style="color:#00e5ff;font-weight:700">' + f3n + '</span> <span style="color:#666">' + f3d + '</span></div>\n'
    '    </div>\n'
    '  </div>\n\n  '
)

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = '<!-- SESSION: 21 MARCH 2026'
end_marker   = '<!-- PENDING JOBS -->'

start_idx = content.find(start_marker)
end_idx   = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("ERROR: markers not found", start_idx, end_idx)
else:
    new_content = content[:start_idx] + new_section + content[end_idx:]
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Done. Replaced", end_idx - start_idx, "chars with", len(new_section))
