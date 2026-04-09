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
