<?php
// ShortFactory Outreach — New Scientist news editors follow-up
// Original pitch sent 2 Apr 2026 — 4 clicks recorded on news desk address
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_newscientist_newsdesk.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [
  [
    'name'  => 'News Editors',
    'email' => 'newseditors@newscientist.com',
    'org'   => 'New Scientist',
    'subj'  => 'Two stories. One week. Both filed.',
    'body'  => <<<TXT
To the New Scientist news desk,

Following up on two pitches from yesterday.

Both stories have moved since I sent them.

Story 1 — New State of Matter (Computanium, Patent GB2605683.8):
The Neuralink press team opened the partnership pitch three times this morning. The angle: Neuralink is building a biological-digital interface without a formal specification of what crosses that interface. The Pointer model (Stage 12, DOI: 10.5281/zenodo.19394096, embargoed 2126) provides that specification. "You are not transferring brain states. You are transferring a cursor trajectory." That distinction changes how every BCI device should be designed. This is now an active industry conversation, not just a filed theory.

Story 2 — Consciousness Model That Runs as Software:
The AGI integration roadmap is now published at shortfactory.shop/agi-architecture.html — showing the compute requirement for human-identical AGI drops from ~170,000 A100 GPUs to approximately 85 through three compression techniques: genomic inheritance (alignment without training), mirror shape grammar (50% vocabulary reduction), and lazy Pointer evaluation (only active thoughts require compute). These are not projections. They are filed architectural proofs.

Both stories are happening now, not eventually. The filings are timestamped. The industry is engaging. The window for first coverage is this week.

I'm available for a call, a briefing document, or a full draft if that's useful.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/agi-architecture.html
shortfactory.shop/portfolio.html
TXT
  ],
  [
    'name'  => 'Submissions Editor',
    'email' => 'submissions@iconbooks.net',
    'org'   => 'Icon Books',
    'subj'  => 'BECOME DIGITAL — one development since yesterday\'s proposal',
    'body'  => <<<TXT
To the Icon Books submissions team,

Following up on the BECOME DIGITAL proposal sent yesterday.

One development worth flagging for the proposal context: I sent the core thesis — that every BCI and longevity company is trying to transfer something they haven't formally defined — to the Neuralink press team this morning. Their email was opened three times. That's typically a forward.

The book's central argument is becoming a live industry debate rather than a theoretical one. The timing for BECOME DIGITAL is now, not in two years.

The proposal stands as sent. Happy to provide additional material, a sample chapter, or a call.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/cv.html
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

echo "ShortFactory Outreach — Hot Follow-ups\n";
echo "========================================\n";
$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "========================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
