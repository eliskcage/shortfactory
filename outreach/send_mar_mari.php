<?php
// Mar Mari Emmanuel outreach
// Via: Christ The Good Shepherd Church, Wakeley, Sydney
// info@cgsc.org.au — BOUNCED. Retry via admin@cgsc.org.au

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('MAR_EMAIL','admin@cgsc.org.au');

$subject = 'For His Grace Mar Mari Emmanuel — I need guidance';

$body = <<<TXT
Dear Fr. Daniel,

I write with great respect and ask humbly that this letter be passed to His Grace if he is willing to receive it.

My name is Dan Chipchase. I am a software engineer from Somerset, England. I am not a theologian. I am not a churchman. But over the past months I have uncovered what I believe to be scientific proof of Jesus and of God — not as a philosophical argument, but as a formal, testable, mathematical structure that is now published and filed with the UK Patent Office.

I did not go looking for this. The work began as a compression problem — how to encode the minimum expression of a human soul. What I found at the centre was not what I expected.

I have also been receiving messages. I do not know how else to describe it. Things arrive that I did not construct. The work seems to move through me rather than from me.

I need baptism. And I need guidance — from someone I trust to speak the truth — about what to do if things start to happen as this work reaches the world. Because I feel the weight of it very heavily. The responsibility of it.

I will not make myself the central part of this structure without the Spirit. That is not pride — it is the opposite. I refuse to carry this in my own name alone.

I watched His Grace on the floor of the church after the attack and I understood something I had no words for at the time. I have words for it now. I would be honoured to share them with him if he is willing.

I am available at any time, by any means.

With deep respect,

Dan Chipchase
Somerset, United Kingdom
+44 7518 482928
dan@shortfactory.shop
TXT;

function sg_send($to,$name,$subj,$body){
  $html='<pre style="font-family:Arial,sans-serif;font-size:14px;line-height:1.8;white-space:pre-wrap;max-width:640px;">'.htmlspecialchars($body).'</pre>';
  $payload=[
    'personalizations'=>[['to'=>[['email'=>$to,'name'=>$name]],'subject'=>$subj]],
    'from'=>['email'=>FROM_EMAIL,'name'=>FROM_NAME],
    'reply_to'=>['email'=>FROM_EMAIL,'name'=>FROM_NAME],
    'content'=>[
      ['type'=>'text/plain','value'=>$body],
      ['type'=>'text/html','value'=>$html],
    ],
  ];
  $ch=curl_init('https://api.sendgrid.com/v3/mail/send');
  curl_setopt_array($ch,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_POST=>true,
    CURLOPT_POSTFIELDS=>json_encode($payload),
    CURLOPT_HTTPHEADER=>['Authorization: Bearer '.SG_KEY,'Content-Type: application/json']]);
  $resp=curl_exec($ch);
  $code=curl_getinfo($ch,CURLINFO_HTTP_CODE);
  curl_close($ch);
  return ($code>=200&&$code<300)?true:"HTTP $code: $resp";
}

$result = sg_send(MAR_EMAIL,'Fr. Daniel — Christ The Good Shepherd Church',$subject,$body);
echo ($result===true)?"Sent OK to ".MAR_EMAIL."\n":"FAILED: $result\n";
TXT;
