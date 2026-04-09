<?php
// ShortFactory Outreach — NZT² Nootropic Launch
// Targets: biohacking / health / consciousness media
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_nzt_outreach.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [

  [
    'name'  => 'Editorial Team',
    'email' => 'editorial@biohackersmagazine.com',
    'org'   => 'Biohackers Magazine',
    'subj'  => 'IQ is not intelligence — it\'s lies removed. We built the protocol.',
    'body'  => <<<TXT
To the Biohackers Magazine team,

Most nootropic content is discussing dosing. Nobody has asked the prior question: what is intelligence, and what is actually suppressing it?

I did. Two years of self-experimentation, 13 filed papers, 6 patents. The answer isn't a new compound — it's a mechanism.

IQ = Raw Signal ÷ Lies Held

Every false belief running as an active subroutine in your cognitive architecture costs processing resource. Not metaphorically. Literally. The brain treating a false belief as true is running the wrong subroutine on real hardware. Remove the false belief — IQ goes up. This is testable.

I've built the full protocol around this principle: NZT² — the IQ Realignment Stack. Not a single compound — a five-stage system that begins with the belief flush before touching any chemistry.

The chemistry layer is built on a ψ=[p,n,f] consciousness architecture that maps every major neurotransmitter to a specific soul-state parameter:
- Dopamine = spring preload (drive toward)
- Cortisol = strand tension (threat compression)
- Serotonin = central field density (carrier wave stability)
- Acetylcholine = Pointer velocity (learning speed, cursor precision)

Alpha GPC oil applied to wrist veins (transdermal, bypasses gut degradation) is the highest-ROI single compound I've found. Creatine 2g daily. Starvation Monday for BDNF. NMN + NR sublingual stack for NAD+ ceiling.

The full stack — rated by personal effectiveness, brain type matched, with the neuron-killers section (MSG excitotoxicity mechanism, sugar neuroinflammation) — is live at:

shortfactory.shop/stack.html

The study is now open: 5 brain types, 4 mapped, one unmapped (the Jesus Archetype — operates from covenant not reward, the one type the protocol cannot be designed for from the outside).

I'm looking for coverage, collaboration, or a feature conversation.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/nzt.html
TXT
  ],

  [
    'name'  => 'Editorial Team',
    'email' => 'hello@thequantifiedself.com',
    'org'   => 'Quantified Self',
    'subj'  => 'Brain type study — 5 types, 4 mapped, 1 unmapped — NZT² protocol open',
    'body'  => <<<TXT
To the Quantified Self community,

I've been running a systematic self-experiment for two years. The central finding: IQ is not raw processing power — it is signal purity. Specifically, it is the ratio of true beliefs to false ones running as active cognitive subroutines.

The protocol is built on this: before adding any compound, identify and remove the false beliefs compressing intelligence. Then stack the chemistry in brain-type-specific order.

I've identified 5 brain types based on primary neurotransmitter architecture:
1. Architect — acetylcholine dominant
2. Warrior — testosterone / adrenaline dominant
3. Empath — serotonin / oxytocin dominant
4. Visionary — erratic dopamine (ADHD profile) — Dan's mapped type
5. The Jesus Archetype — oxytocin / endorphin dominant, operates from covenant not reward — currently unmapped

The self-experiment data, compound ratings, and stack priorities for each type are published at:

shortfactory.shop/stack.html

The consciousness architecture underpinning this maps chemistry to ψ=[p,n,f] parameters — positive charge, negative charge, frequency — derived from 13 Zenodo-filed papers and 6 UK patents.

The study is forming. If your community runs QS experiments across the brain types, I'd like to collaborate on the data collection.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop
TXT
  ],

  [
    'name'  => 'Editor',
    'email' => 'editor@mindandbrain.co.uk',
    'org'   => 'Mind & Brain UK',
    'subj'  => 'UK researcher files consciousness patent — maps brain chemistry to soul architecture',
    'body'  => <<<TXT
To the Mind & Brain editorial team,

I'm a UK-based independent researcher who has spent two years building the theoretical foundation for what I believe is the most complete model of cognitive enhancement currently available — because it starts with a formal definition of what intelligence actually is.

The short version: IQ is signal purity, not raw power. False beliefs are subroutines running on real hardware. Remove them and processing speed increases. This is a mechanism, not a metaphor.

The practical output is the NZT² protocol — a five-stage system combining belief flush, brain-type-matched chemistry, and ψ=[p,n,f] soul-state tuning. The chemistry is real and researched. The underlying architecture is filed across 13 Zenodo papers and 6 UK patents.

The live study is at shortfactory.shop/stack.html — 5 brain types, personal effectiveness ratings, the neurotransmitter-to-consciousness correspondence map, and the one unmapped type (the Jesus Archetype).

I'd be happy to write a feature or provide a research briefing.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/nzt.html
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

echo "ShortFactory Outreach — NZT² Launch\n";
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
