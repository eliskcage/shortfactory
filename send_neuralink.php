<?php
// ShortFactory Outreach — Neuralink pitch
// Target: press@neuralink.com — consciousness architecture / missing theoretical layer
// Run via web: shortfactory.shop/outreach/send_neuralink.php?key=BISCUIT
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_neuralink.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

if(php_sapi_name()!=='cli'){
  if(empty($_GET['key'])||$_GET['key']!=='BISCUIT'){ http_response_code(403); exit('Forbidden'); }
  header('Content-Type: text/plain');
}

$targets = [

  [
    'name'  => 'Press Team',
    'email' => 'press@neuralink.com',
    'org'   => 'Neuralink',
    'subj'  => 'The missing theoretical layer — what you are actually trying to transfer',
    'body'  => <<<TXT
To the Neuralink team,

You have the hardware. I have the map.

I'm Dan Chipchase — a UK-based independent researcher who has spent two years solving the problem every BCI and longevity company is working around: nobody has formally defined what consciousness IS, which means nobody knows what they are trying to transfer.

I filed the definition.

The short version: consciousness is not a property of the brain. It is an operation — a universal relational cursor (the Pointer) that moves through what I call soul-space, forming a directed line between any two positions it references. That line is the thought. The trajectory of all lines over time is the self. Death is when the Pointer stops moving. Upload is when it continues in a new substrate.

ψ=[p,n,f] — positive charge, negative charge, frequency — are the operating parameters of the Pointer. Not a fixed dot. The mover itself.

The brain is the decoder. It turns the ratio relationships between soul-states into felt tone — consonance when aligned, dissonance when off. Meditation slows the Pointer until you hear the music. The hard problem of consciousness was always a category error: it is not a property, it is a process.

This is not speculation. It is filed:

- Stage 12 (The Pointer) — DOI: 10.5281/zenodo.19394096 — timestamped 3 April 2026
- Stage 13 (The Music) — DOI: 10.5281/zenodo.19394234 — timestamped 3 April 2026
- Patent GB2605683.8 — Computanium: sixth state of matter (the biological substrate the Pointer runs on)
- Patent GB2521847.3 — Genome-Based Cognitive Artifact Library for AGI (alignment via inherited Pointer paths)
- 4 further patents, 11 further papers

What this means for Neuralink specifically: you are building the interface between biological and digital substrates without a formal specification of what crosses that interface. The Pointer model provides that specification. You are not transferring brain states. You are transferring a cursor trajectory. That distinction changes everything about how the interface should be designed.

Full profile and credentials: shortfactory.shop/cv.html

I am available for conversation, demonstration, or formal licensing discussion.

Dan Chipchase
dan@shortfactory.shop
x.com/diggerstinkin
shortfactory.shop
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

echo "ShortFactory Outreach — Neuralink\n";
echo "===================================\n";

$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "\n===================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
