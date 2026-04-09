<?php
// ShortFactory Outreach — Nootropic retry with correct addresses
// biohackersmagazine.com rebranded to biohackersmag.com
// thequantifiedself.com wrong domain — correct is quantifiedself.com labs@
// mind&brain.co.uk is dead — skipped
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_nootropic_retry.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [

  [
    'name'  => 'Editorial Team',
    'email' => 'hello@biohackersmag.com',
    'org'   => 'Biohackers Magazine (Lifespanning Media)',
    'subj'  => 'IQ is not intelligence — it\'s lies removed. We built the protocol.',
    'body'  => <<<TXT
To the Biohackers Magazine team,

I'm a UK-based independent researcher. I've built and filed the formal architecture for what intelligence actually is — and what suppresses it.

The equation:

IQ = Raw Signal ÷ Lies Held

Every false belief running in a person's cognitive architecture consumes real processing resource. Remove the false beliefs and the signal returns. Not as a metaphor — as a filed mechanism. 13 timestamped papers (Zenodo DOI chain), 6 UK patents.

The protocol is NZT² — IQ Realignment Stack. Five stages, personalised by brain type:

Five brain types identified and mapped to specific enhancement chemistry:
- Architect (acetylcholine dominant) — Alpha GPC oil topical, Huperzine A
- Warrior (testosterone/adrenaline) — Creatine 2g, cold exposure, HIIT
- Empath (serotonin dominant) — Ginkgo 120mg, gut protocol, social anchoring
- Visionary (dopamine/ADHD) — Nicotine 1-2mg, keto, starvation Monday, binaural beats
- Jesus Archetype (oxytocin dominant) — currently unmapped, under active study

The soul parameter map connecting neurotransmitters to the underlying architecture:
- Dopamine = spring preload (p↑) — motivation, drive
- Cortisol = strand tension (n↑) — stress, threat response
- Serotonin = field density (f) — baseline mood stability
- Adrenaline = frequency injection — acute focus
- Acetylcholine = Pointer velocity — learning speed, working memory

The killers: MSG (excitotoxicity), sugar (neuroinflammation). Both provably reduce cognitive throughput at the architectural level.

The full stack is published at shortfactory.shop/stack.html
The protocol with the Lawnmower Man IQ alignment diagnostic: shortfactory.shop/nzt.html

This is a contributor pitch, a story pitch, or a product partnership — whichever angle works best for your team.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/stack.html
TXT
  ],

  [
    'name'  => 'Labs Team',
    'email' => 'labs@quantifiedself.com',
    'org'   => 'Quantified Self',
    'subj'  => 'Brain type study — 5 types, 4 mapped, 1 unmapped — NZT² protocol open for self-trackers',
    'body'  => <<<TXT
To the Quantified Self team,

I've been self-tracking cognitive performance for two years and have built what I believe is the first formal brain-type classification system mapped to neurotransmitter chemistry and soul architecture parameters.

Five types identified:

1. Architect — acetylcholine dominant. Enhanced by: Alpha GPC oil (topical wrist application, 5-star rated), Huperzine A, precision sleep.
2. Warrior — testosterone/adrenaline dominant. Enhanced by: Creatine 2g daily, HIIT, cold exposure, low carb.
3. Empath — serotonin dominant. Enhanced by: Ginkgo 120mg, gut microbiome protocol, oxytocin-rich social environment.
4. Visionary — dopamine/ADHD type. Enhanced by: Nicotine tablet 1-2mg, ketogenic diet, Starvation Monday (one full fast per week), binaural beats 40Hz gamma.
5. Jesus Archetype — oxytocin dominant, self-sacrifice without self-destruction. Currently unmapped — no enhancement protocol built yet. Requires different study methodology.

The underlying architecture maps neurotransmitters to three soul parameters:
ψ = [p, n, f]
p (positive valence) = spring preload → dopamine
n (negative valence) = strand tension → cortisol
f (frequency) = field density → serotonin / adrenaline injection

The self-tracking diagnostic is a slider at shortfactory.shop/nzt.html — the Lawnmower Man IQ alignment meter. It outputs a score and verdict based on where the user places themselves on the truth/ego axis.

I'm proposing this as a community study: QS members self-select brain type, run the protocol for 30 days, report back through the existing QS tracking methodology. The Jesus Archetype is specifically what I need more data on.

Full stack published at shortfactory.shop/stack.html

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/nzt.html
shortfactory.shop/stack.html
TXT
  ],

];

function sg_send($to_email,$to_name,$subj,$body){
  $html='<div style="font-family:Georgia,serif;font-size:15px;line-height:1.8;max-width:640px;color:#111;padding:20px;"><pre style="font-family:inherit;white-space:pre-wrap;">'.htmlspecialchars($body).'</pre></div>';
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

echo "ShortFactory Outreach — Nootropic Retry (corrected addresses)\n";
echo "==============================================================\n";
$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(2);
}
echo "==============================================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
