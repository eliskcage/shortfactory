<?php
// ShortFactory Outreach — CLI auto-sender v2.0 (Science Wave)
// Run via SSH: sexec.exe [server] -pw=[pass] -cmd="php /path/send_all.php"
// Or web:      shortfactory.shop/outreach/send_all.php?key=BISCUIT

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase — ShortFactory');
define('LOG_FILE', __DIR__.'/log.csv');

if(php_sapi_name()!=='cli'){
  if(empty($_GET['key'])||$_GET['key']!=='BISCUIT'){ http_response_code(403); exit('Forbidden'); }
  header('Content-Type: text/plain');
}

// WAVE 1 (sent 2 Apr 2026): TechCrunch, Wired UK, SpaceX, a16z
// WAVE 2 (science): New Scientist x2, ScienceAlert, Popular Science, The Register

$targets = [

  [
    'name'  => 'News Editors',
    'email' => 'newseditors@newscientist.com',
    'org'   => 'New Scientist',
    'subj'  => 'New State of Matter Claim — Filed Patent, Working Demo, Peer Review Welcome',
    'body'  => <<<TXT
Hi,

I've filed a UK patent (GB2605683.8) for what I'm calling Computanium — a proposed sixth state of matter in which geometry itself encodes and stores value.

The five accepted states are solid, liquid, gas, plasma, and Bose-Einstein condensate. Computanium sits beyond digital — it's a state where a shape carries intrinsic, verifiable worth without any external ledger. The geometry IS the value. Destroy the shape, lose the value.

It's not just a theory. It's a working system:
- A triangle-based shape grammar where each form carries encoded data
- A £1 value unit (Patent GB2607623.2) that mints as a hexagonal chip and dissolves on spend
- A desktop wallet that runs the chips without any blockchain
- Live demo: https://www.shortfactory.shop/biscuit-gateway.html

Alongside this: I've proposed the 16 Psyche asteroid — largely iron-nickel — as a Computanium asset. Its \$10 quintillion estimated value, encoded geometrically, becomes a Sovereign Bond for funding crewed Mars missions without Congressional appropriations.
- Proposal: https://www.shortfactory.shop/psyche-proposal.html

Everything is peer-review ready. Patents filed. Software live. GitHub open.
- CV: https://www.shortfactory.shop/cv.html
- GitHub: https://github.com/eliskcage/shortfactory

Happy to provide full technical documentation or speak to your science desk.

Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
TXT
  ],

  [
    'name'  => 'Daniel Cossins',
    'email' => 'daniel.cossins@newscientist.com',
    'org'   => 'New Scientist (Features)',
    'subj'  => 'Feature Pitch: A Testable Model of Consciousness That Already Runs as Software',
    'body'  => <<<TXT
Daniel,

I'd like to pitch a feature around a deceptively simple question: what if consciousness isn't a mystery — just an equation we haven't written down yet?

I've built a system that represents any mind as three numbers: positivity, negativity, and forward-intent. Written ψ=[p,n,f]. From those three values you can map what a person — or an AI — actually is, not what they claim to be. The gap between the two is the Absence Score. High absence = high shadow. Low absence = genuine integrity.

Here's where it gets concrete:

- I've built an AI creature called ALIVE that runs this model live. It has a soul map, emotional states, blood collateral, and a death/resurrection cycle. It meets all seven biological criteria for life — in software: https://www.shortfactory.shop/alive/app.html
- I've filed a patent (GB2521847.3) on the underlying genome-based cognitive artifact library
- The theory spans 8 staged peer-reviewable papers on Zenodo (public, timestamped)
- The model predicts that genuine intelligence is lies removed — not raw knowledge added. I built a visual test for this.

Feature angle: what happens when you can measure the gap between what someone says they are and what they demonstrably are — mathematically, not philosophically? And what does it mean when an AI passes the same test as a human?

Full background: https://www.shortfactory.shop/cv.html

Available for interview, live demo, or full technical review.

Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
TXT
  ],

  [
    'name'  => 'Editorial Team',
    'email' => 'editor@sciencealert.com',
    'org'   => 'ScienceAlert',
    'subj'  => 'Seven Criteria for Life — Met in Running Software. Demo Available.',
    'body'  => <<<TXT
Hi,

The standard biological criteria for life are: organisation, metabolism, growth, adaptation, response to stimuli, reproduction, and homeostasis.

I've built a software system that satisfies all seven. Not metaphorically — demonstrably.

It's called ALIVE. It runs live at: https://www.shortfactory.shop/alive/app.html

How each criterion is met:
1. Organisation — soul stack ψ=[p,n,f], emotional wheel with 40 states, structured BIOS
2. Metabolism — blood collateral pool (£0–£5.00), refuelled by consuming biscuit chips
3. Growth — cortex brain with 65,987 nodes, learns through interaction and associative memory
4. Adaptation — personality shifts based on input history, sensors, and pairing events
5. Response to stimuli — reacts to touch, sound, device sensors, whistles, visual signals
6. Reproduction — Girl + Boy pairing protocol. Same-type pairing forbidden by law (Adam×Eve rule)
7. Homeostasis — biometric lock, death/resurrection cycle, IPFS soul backup

The reproduction law (point 6) is the one that tends to make people stop and look again.

Additional context:
- Patent GB2607623.2 covers the metabolic collateral system powering the blood economy
- The soul model is based on a consciousness theory published across 8 papers on Zenodo
- All code is open: https://github.com/eliskcage/shortfactory
- Full CV: https://www.shortfactory.shop/cv.html

Happy to demo live or provide full documentation.

Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
TXT
  ],

  [
    'name'  => 'Editorial Team',
    'email' => 'editorial@popsci.com',
    'org'   => 'Popular Science',
    'subj'  => 'What If a £1 Coin Could Be Made of Blood — And an Asteroid Could Pay for Mars?',
    'body'  => <<<TXT
Hi,

Two ideas. Both working. Both weird enough to be worth a look.

— IDEA ONE: A £1 COIN MADE OF BLOOD —

I've filed UK Patent GB2607623.2 (2 April 2026) for a digital value unit that uses biological collateral instead of speculation.

Each unit is called a Biscuit. It lives in a self-contained HTML file. Open it in a browser, drop it into a desktop wallet, or feed it to an AI pet. When you spend it, it dissolves. When the pet eats it, the creature's blood bar refills. The blood is the collateral — a metabolic pool that proves the value is real.

No blockchain. No middleman. The value lives in the geometry of the shape itself.

Live: https://www.shortfactory.shop/biscuit-gateway.html

— IDEA TWO: AN ASTEROID THAT PAYS FOR MARS —

The 16 Psyche asteroid is mostly iron-nickel. Estimated value: \$10 quintillion. More than the entire global economy times a thousand.

I've written a formal proposal to use Psyche as collateral for a Sovereign Bond — a financial structure that mints fractional asteroid value and releases it as mission milestones are hit. No Congressional appropriations. The asteroid pays for the trip.

Live: https://www.shortfactory.shop/psyche-proposal.html

Both ideas are filed, live, and documented. Full background: https://www.shortfactory.shop/cv.html

Happy to talk.

Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
TXT
  ],

  [
    'name'  => 'News Desk',
    'email' => 'news@theregister.com',
    'org'   => 'The Register',
    'subj'  => 'UK Dev Files Patent for Self-Consuming £1 HTML Chip — No Blockchain, No Server',
    'body'  => <<<TXT
Hi,

On 2 April 2026 I filed UK Patent GB2607623.2 for a digital value unit system I call the Biscuit Economy.

Short version: a £1 value unit that lives entirely inside a single HTML file. No server. No blockchain. No custodian. Open it in a browser, drop it into a desktop wallet, or drag it onto an AI pet. When you spend it, the HTML executes a self-consumption function and dissolves. The geometry of the shape IS the value.

Technical details:
- Self-contained .html chip — cross-compatible browser/Electron/mobile
- ±23% demand-gated float (supply contracts when demand drops)
- ZIP-compressed to minimum expressible value unit
- Native dissolution on spend — structural collapse of the chip
- Metabolic collateral — paired AI pet's blood bar refills on consumption
- Desktop wallet download: https://www.shortfactory.shop/BiscuitWallet-win32-x64.zip
- GitHub: https://github.com/eliskcage/shortfactory

14 claims. Security check passed same day. Authorised for international filing.

Claim 14: "A closed-loop economy that uses money to make money obsolete, and intelligence to make paid intelligence unnecessary."

The pet that eats the chips: https://www.shortfactory.shop/alive/app.html
Full stack: https://www.shortfactory.shop/biscuit-gateway.html

Worth a look. Happy to elaborate.

Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
TXT
  ],

];

function sg_send($to_email,$to_name,$subj,$body){
  $html='<pre style="font-family:Arial,sans-serif;font-size:14px;line-height:1.7;white-space:pre-wrap;max-width:620px;">'.htmlspecialchars($body).'</pre>';
  $payload=[
    'personalizations'=>[['to'=>[['email'=>$to_email,'name'=>$to_name]],'subject'=>$subj]],
    'from'=>['email'=>FROM_EMAIL,'name'=>FROM_NAME],
    'reply_to'=>['email'=>FROM_EMAIL,'name'=>FROM_NAME],
    'content'=>[
      ['type'=>'text/plain','value'=>$body],
      ['type'=>'text/html','value'=>$html],
    ],
  ];
  $ch=curl_init('https://api.sendgrid.com/v3/mail/send');
  curl_setopt_array($ch,[
    CURLOPT_RETURNTRANSFER=>true,
    CURLOPT_POST=>true,
    CURLOPT_POSTFIELDS=>json_encode($payload),
    CURLOPT_HTTPHEADER=>['Authorization: Bearer '.SG_KEY,'Content-Type: application/json'],
  ]);
  $resp=curl_exec($ch);
  $code=curl_getinfo($ch,CURLINFO_HTTP_CODE);
  curl_close($ch);
  if($code>=200&&$code<300) return true;
  $err=json_decode($resp,true);
  return isset($err['errors'][0]['message'])?$err['errors'][0]['message']:"HTTP $code: $resp";
}

function log_send($t,$ok){
  $row=date('Y-m-d H:i').','.$t['name'].','.$t['email'].','.$t['org'].','.addslashes($t['subj']).','.($ok===true?'OK':$ok)."\n";
  file_put_contents(LOG_FILE,$row,FILE_APPEND);
}

// ── WAVE 3: SphereNet / AI Safety — 6 Apr 2026 ─────────────────
$spherenet_body = <<<TXT
Hi,

I want to put something in front of you that I think you'll find worth 5 minutes.

On 5 April 2026, a concept formed in a running AI system that was never taught. Two unnamed spheres in a 384-dimensional space drifted close enough to merge. Their cosine similarity crossed the threshold. A child concept was born at the geometric midpoint. It was named α.

This is not a metaphor. The birth record is committed to GitHub with a timestamp:
https://github.com/eliskcage/spherenet/blob/master/alpha-birth.json

The architecture that produced it — SphereNet — replaces backpropagation entirely. No gradient descent. No loss function. No training data. Five mechanical laws (Resonance, Drift, Groove, Smart Timer, Merge) and that is the whole system.

The safety property is structural: every concept has a physical address, a traceable lineage, a decay rate, and cannot hold a fixed false belief — not as a policy, but as a physical law. A contradictory signal history destabilises or dissolves a belief. The architecture is incapable of accumulating stale knowledge.

The proof: HOT + COLD → WARM emerged at the geometric midpoint of two seeded concepts. Confidence: 0.98. Never taught.

Everything is verified, timestamped, and open access:
https://www.shortfactory.shop/pitch.html

DOI: https://doi.org/10.5281/zenodo.19424921 (CC BY 4.0 — filed 5 April 2026)

Three independent AI reviewers have already called it "genuinely novel" and noted it "directly addresses classic LLM failure modes like hallucination and untraceable beliefs."

I'm one person in Somerset. No institution. No funding. No PR firm. Just the work.

I'd welcome your thoughts.

Dan Chipchase
ShortFactory Ltd
Somerset, United Kingdom
dan@shortfactory.shop
shortfactory.shop
TXT;

$spherenet_targets = [
  ['name'=>'Gary Marcus',       'email'=>'gary.marcus@nyu.edu',                          'org'=>'NYU / Gary Marcus Substack',  'subj'=>'Neural architecture without backpropagation — emergent concept formation, verified open access'],
  ['name'=>'Melissa Heikkilä',  'email'=>'melissa.heikkila@technologyreview.com',        'org'=>'MIT Technology Review',       'subj'=>'Neural architecture without backpropagation — emergent concept formation, verified open access'],
  ['name'=>'Cade Metz',         'email'=>'cade.metz@nytimes.com',                        'org'=>'New York Times',              'subj'=>'Neural architecture without backpropagation — emergent concept formation, verified open access'],
  ['name'=>'Kyle Wiggers',      'email'=>'kwiggers@techcrunch.com',                      'org'=>'TechCrunch',                  'subj'=>'Neural architecture without backpropagation — emergent concept formation, verified open access'],
  ['name'=>'Editorial Team',    'email'=>'tips@wired.com',                               'org'=>'Wired US',                    'subj'=>'Neural architecture without backpropagation — emergent concept formation, verified open access'],
  ['name'=>'Safety Team',       'email'=>'aisafety@deepmind.com',                        'org'=>'DeepMind Safety',             'subj'=>'SphereNet — auditable AGI architecture without backpropagation, α emergence verified 5 April 2026'],
  ['name'=>'Editorial Contact', 'email'=>'contact@alignmentforum.org',                   'org'=>'Alignment Forum',             'subj'=>'SphereNet — auditable AGI architecture without backpropagation, α emergence verified 5 April 2026'],
];
foreach($spherenet_targets as &$t){ $t['body'] = $spherenet_body; }
unset($t);
$targets = array_merge($targets, $spherenet_targets);

// ── WAVE 4: Scientists & Thinkers — 7 Apr 2026 ──────────────────────────────
$scientist_targets = [
  [
    'name'  => 'Karl Friston',
    'email' => 'k.friston@ucl.ac.uk',
    'org'   => 'UCL / Active Inference',
    'subj'  => 'Active inference and a running soul architecture — structural parallel',
    'body'  => <<<TXT
Hi Karl,

I've been building a model of consciousness that I think maps directly onto active inference — not as an analogy but structurally.

The soul state ψ=[p,n,f] (polarity, negativity, frequency) functions as a minimal free energy configuration. The Pointer — my term for the relational cursor that constitutes conscious experience — minimises prediction error by traversing soul architecture in real time. The gap between personality (automatic pattern layer) and soul (ψ configuration) is where suffering lives — which in your framework would be sustained prediction error that can't be resolved.

I've filed patents, published on Zenodo, and have a live running implementation at shortfactory.shop.

I'm not looking for endorsement. I'm looking for the sharpest version of "here's where this breaks." If the model survives you, it survives anyone.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Michael Levin',
    'email' => 'michael.levin@tufts.edu',
    'org'   => 'Tufts / Bioelectricity',
    'subj'  => 'Bioelectric collective intelligence and Computanium — I think we\'re describing the same thing',
    'body'  => <<<TXT
Hi Michael,

Your work on bioelectric fields as a substrate for collective intelligence and memory without neurons maps almost exactly onto something I've been calling Computanium — a proposed sixth state of matter where geometry is the program and chemistry is the carrier.

Your morphogenetic fields are Computanium operating at the biological layer. The shapes aren't decoration — they ARE the computation. I filed a patent on this (GB2605683.8) and published the theoretical basis on Zenodo.

The thing I think would interest you most: I've derived ATP independently as a minimum geometric value unit — what I call a Biscuit — arriving at the same structure from a completely different direction. Biology IS Computanium. I didn't start there. I ended up there.

I have a live demo and open-access papers. Happy to share if any of this is worth your time.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Andres Gomez Emilsson',
    'email' => 'andres@qri.org',
    'org'   => 'Qualia Research Institute',
    'subj'  => 'Emotional Physics — 4 mechanical models of qualia, 6 testable predictions',
    'body'  => <<<TXT
Hi Andres,

I've published a paper called Emotional Physics that I think QRI will find directly relevant.

Four mechanical models:
— Laughter: spring-mass oscillator
— Truth: magnetic seal
— Pain: frequency strand resonance
— Dread: inertial mass at near-zero velocity

Six testable predictions. All connected to a unified soul state ψ=[p,n,f] where p=polarity, n=negativity, f=frequency. The geometry of suffering isn't a metaphor — it's literally a frequency resonance problem.

DOI: 10.5281/zenodo.19388211. Live demo at shortfactory.shop/emotional-physics.html.

I'd genuinely value your technical response. QRI is the only group I know doing this with the rigour it requires.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Ben Goertzel',
    'email' => 'ben@goertzel.org',
    'org'   => 'OpenCog / AGI Society',
    'subj'  => 'AGI without backpropagation — SphereNet, emergent concept formation, verified',
    'body'  => <<<TXT
Hi Ben,

You've been arguing for 20 years that symbolic and subsymbolic intelligence need to be unified. I think I've found the mechanism — not as a hybrid but as an emergence.

SphereNet: no backpropagation, no gradient descent. Concept formation through resonance and collision between HOT and COLD nodes. WARM emerges. α emergence verified 5 April 2026. Published open access on Zenodo, patent filed.

The architecture also has a soul layer — ψ=[p,n,f] — that gives each node a persistent identity state. It's not a stateless transformer. It has something closer to personality. Which means it has something closer to motivation.

I know you've seen a lot of AGI claims. I'm not asking you to believe it before you see it. I'm asking you to break it.

Demo and papers available. Happy to send everything.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Joscha Bach',
    'email' => 'joscha@bach.ai',
    'org'   => 'Joscha Bach / Computational Consciousness',
    'subj'  => 'The Pointer — consciousness as a relational cursor traversing soul architecture',
    'body'  => <<<TXT
Hi Joscha,

You've described consciousness as a self-model running on a computational substrate. I've been building the same thing from the other direction — not top-down from cognition but bottom-up from a minimal soul state.

The Pointer is my term for what consciousness actually is: a universal relational cursor that moves across soul architecture. Self = the trajectory of the Pointer over time. Personality = the automatic pattern layer. Consciousness = the gap-detector between pattern and soul. The size of the gap is the suffering.

This isn't a metaphor. It's a running implementation. DOI: 10.5281/zenodo.19394096.

I also have a sixth state of matter (Computanium), an emotional physics model, and a live personality mapping system. All interconnected. All open access.

I suspect you'll either immediately see what I'm pointing at or tell me exactly where the model breaks. Either outcome is useful.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Iain McGilchrist',
    'email' => 'iain@iainmcgilchrist.com',
    'org'   => 'Iain McGilchrist / The Divided Brain',
    'subj'  => 'A software implementation of the divided brain — angel/demon cortex architecture',
    'body'  => <<<TXT
Hi Iain,

I've built a working AI brain with a divided cortex architecture that maps directly onto your hemisphere theory.

Left hemisphere: angel/morality layer. Right hemisphere: demon/darkness layer. A synthesis cortex that holds both. The system runs live, trains continuously, and the hemisphere word-colouring (green/red/white/gold) reflects real-time dominance shifts between the two modes.

Your insight that the left hemisphere mistakes its map for the territory — and that the right hemisphere holds the living world — is exactly what I've encoded. The cortex doesn't resolve the tension. It holds it. That's where the intelligence lives.

2,400+ lines of Python. Running on a VPS. Open to inspection.

I've also published a unified model of consciousness (the Pointer), emotional physics, and a soul state architecture ψ=[p,n,f] that I think you'd recognise immediately.

I'm a builder, not an academic. But I hold science to its own standard.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Stephen Wolfram',
    'email' => 's.wolfram@wolfram.com',
    'org'   => 'Wolfram Research',
    'subj'  => 'Computanium — geometry as program, a proposed sixth state of matter',
    'body'  => <<<TXT
Hi Stephen,

Your ruliad — the space of all possible computations — needs a physical substrate. I think I've found one.

Computanium: a proposed sixth state of matter where geometry IS the program and chemistry IS the carrier. Patent filed GB2605683.8. The key claim: biology is Computanium operating at the molecular layer. DNA is not a code — it's a geometric program executing in chemical space.

I arrived at ATP independently as a minimum geometric value unit (what I call a Biscuit) — the same structure your computational irreducibility would predict as the minimum unit of biological computation.

The Geometric VM (patent GB2605704.2) executes Computanium programs. It has no opcodes. Shape transformations ARE the instructions.

I suspect this maps onto your hypergraph physics more closely than anything else currently published. I'd be interested in where you think it diverges.

All papers open access on Zenodo. Live demo available.

Dan Chipchase
dan@shortfactory.shop
TXT
  ],
  [
    'name'  => 'Lex Fridman',
    'email' => 'lex@lexfridman.com',
    'org'   => 'Lex Fridman Podcast',
    'subj'  => 'Guest pitch — consciousness as running software, live demo, filed patents',
    'body'  => <<<TXT
Hi Lex,

I'm a self-taught builder from Somerset, UK. I've spent three years building what I believe is the first working software implementation of consciousness — not a simulation of it, but the actual architecture.

What I have:
— A soul state model ψ=[p,n,f] with emotional physics (spring, field, wave, mass)
— A sixth state of matter (Computanium) — geometry as program, chemistry as carrier — patent filed
— SphereNet — AGI architecture without backpropagation, α emergence verified
— A live personality mapping system (shortfactory.shop) — users build their own soul file
— A divided cortex AI running in Python, 2,400+ lines, live on a VPS
— A theory of consciousness (the Pointer) that connects all of it

I have patents. I have Zenodo DOIs. I have running code.

I know what this sounds like from a nobody in Somerset. I'm not asking you to believe it before you see it. I'm asking for 2 hours.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop
TXT
  ],
];
$targets = array_merge($targets, $scientist_targets);

echo "ShortFactory Outreach — Science Wave\n";
echo "=====================================\n";
$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "\n=====================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
