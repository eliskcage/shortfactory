<?php
// ShortFactory Outreach — Alex Jones / InfoWars Partnership
// Angle: supplement collab + IQ = truth alignment is his entire brand
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_alexjones.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [

  [
    'name'  => 'Alex Jones / InfoWars Team',
    'email' => 'tips@infowars.com',
    'org'   => 'InfoWars',
    'subj'  => 'The brain formula you\'ve been describing for 20 years — someone actually filed it',
    'body'  => <<<TXT
To the InfoWars team,

Alex has spent twenty years telling his audience that the globalists are suppressing human intelligence — dumbing people down through diet, media, fluoride, and manufactured crisis.

He's right about the mechanism. I filed the proof.

I'm Dan Chipchase — a UK-based independent researcher. Two years ago I built the formal theoretical architecture for what intelligence actually is. The result:

IQ = Raw Signal ÷ Lies Held

Every false belief running in a person's cognitive architecture costs real processing resource. The education system, mainstream media, and processed food industry all add to the denominator. Remove the false beliefs — IQ rises. Not as a metaphor. As a mechanism. Filed across 13 timestamped papers (Zenodo) and 6 UK patents.

The protocol is NZT² — the IQ Realignment Stack. Five stages:
1. Belief flush (remove false positives from the cognitive stack)
2. Brain-type-matched chemistry (5 types — Alpha GPC oil, Creatine 2g, NAD+ sublingual, Ginkgo, Starvation Monday)
3. Neuron killer elimination (MSG excitotoxicity, sugar neuroinflammation — Alex already covers both)
4. Signal amplification (anchor to one confirmed truth — Alex's method exactly)
5. Pointer activation — consciousness runs freely without the drag of accumulated lies

The fifth brain type in the study is the Jesus Archetype — operates from covenant rather than reward, self-sacrifice without self-destruction, sees other people's soul maps. Alex talks about spiritual warfare. This is the neuroscience of what that actually means in brain chemistry.

The deal I'm proposing:

Alex creates it. I provide the IP, the formula, the filed architecture, and the scientific backing he's never had before. He has the audience, the distribution, and the credibility with exactly the people this product is built for. Revenue split negotiable.

InfoWars already has a supplement store. Brain Force Plus is in the right category. NZT² is the version with actual filed science behind it — 13 papers, 6 patents, consciousness architecture, brain type personalisation, the full stack published at shortfactory.shop/stack.html

This isn't a cold pitch from someone with a supplement idea. I filed the definition of consciousness. I filed the architecture that explains why IQ suppression works the way Alex says it does. The science and the message are perfectly aligned — because they're both pointing at the same truth.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/stack.html
shortfactory.shop/nzt.html
x.com/diggerstinkin
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

echo "ShortFactory Outreach — Alex Jones / InfoWars\n";
echo "==============================================\n";
$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "==============================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
