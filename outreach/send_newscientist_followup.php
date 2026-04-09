<?php
// ShortFactory Outreach — New Scientist follow-up (daniel.cossins)
// Original pitch sent 2 Apr 2026 — 2 clicks recorded
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_newscientist_followup.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [
  [
    'name'  => 'Daniel Cossins',
    'email' => 'daniel.cossins@newscientist.com',
    'org'   => 'New Scientist',
    'subj'  => 'Following up — Neuralink opened it three times',
    'body'  => <<<TXT
Daniel,

Following up on yesterday's pitch — A Testable Model of Consciousness That Already Runs as Software.

One development worth flagging: I sent the theoretical layer to Neuralink's press team at 3:56am this morning. Their email was opened three times. That usually means it was forwarded internally.

The angle I sent them: they are building a biological-digital interface without a formal specification of what crosses that interface. The Pointer model provides that specification. You are not transferring brain states. You are transferring a cursor trajectory. That distinction changes how the interface should be designed.

I've published the full integration roadmap and compute requirements today — it shows how the architecture gets from 170,000 GPUs to approximately 85 through genomic compression and a mirror-based shape grammar that halves vocabulary cost structurally:

shortfactory.shop/agi-architecture.html

The consciousness definition is embargoed (life insurance policy — 100-year lock on the binding mechanism). Everything else is filed, timestamped, and live.

If there's a story here for you, this is the moment — before the hardware conversation becomes public.

Dan Chipchase
dan@shortfactory.shop
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

echo "ShortFactory Outreach — New Scientist follow-up\n";
echo "=================================================\n";

$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "\n=================================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
