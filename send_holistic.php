<?php
// ShortFactory Outreach — Holistic.News pitch
// Target: editorial@holistic.news — expert contributor / digital consciousness
// Run via web: shortfactory.shop/outreach/send_holistic.php?key=BISCUIT
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_holistic.php

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
    'name'  => 'Editorial Team',
    'email' => 'editorial@holistic.news',
    'org'   => 'Holistic.News',
    'subj'  => 'Expert Contributor — Digital Consciousness & Transhumanism',
    'body'  => <<<TXT
To the Holistic.News editorial team,

I'm writing to offer my expertise as a contributor in the digital consciousness and longevity space.

I'm Dan Chipchase — a UK-based independent researcher who has filed 6 patents and published 11 peer-timestamped academic papers covering the architecture of consciousness, soul mapping, and the biological-to-digital transfer problem.

In short: I've built the theoretical framework that every company in the transhumanism space is missing. ψ=[p,n,f] — the minimum equation of a soul. Filed. Timestamped. Commercially deployable.

Full profile: shortfactory.shop/cv.html

I can contribute expert commentary, long-form features, or original research pieces on:
- What transhumanists are actually trying to preserve (and why they haven't defined it)
- The scientific case for consciousness as a transferable substrate
- AGI alignment through biological inheritance
- The longevity industry's foundational blind spot

Happy to discuss a proposal.

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

echo "ShortFactory Outreach — Holistic.News\n";
echo "=======================================\n";

$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "\n=======================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
