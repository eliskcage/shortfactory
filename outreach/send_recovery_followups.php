<?php
// ShortFactory Outreach — Recovery follow-ups after email outage
// dan@shortfactory.shop was bouncing (550 5.1.1) due to broken MX records
// Sending to: Neuralink, New Scientist news desk, Icon Books
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_recovery_followups.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [

  [
    'name'  => 'Press Team',
    'email' => 'press@neuralink.com',
    'org'   => 'Neuralink',
    'subj'  => 'My email was broken — resending with updates (Pointer model + compute proof)',
    'body'  => <<<TXT
To the Neuralink press team,

A quick note first: my email address dan@shortfactory.shop had an MX record misconfiguration for several days. Any replies you sent will have bounced back with a 550 error. That is now fixed. I apologise for the technical issue.

Resending the core of what I pitched, with developments since.

—

The problem I flagged is still the central one: Neuralink is building a biological-digital interface without a formal specification of what crosses that interface. That gap is not a minor detail — it is the architectural question that determines whether the technology is safe, reversible, and ethically defensible.

The Pointer model (Stage 12, filed and timestamped at DOI: 10.5281/zenodo.19394096, embargoed until 2126 as a life insurance measure) provides that specification. The core statement:

"You are not transferring brain states. You are transferring a cursor trajectory."

The Pointer is the conscious cursor — the relational address that moves through a person's internal architecture over time. The self is not a static map. It is the trajectory of that cursor. What Neuralink needs to define — before any interface can be called safe — is the format for encoding, transmitting, and reconstructing that trajectory. Without it, you are moving something you cannot name.

Since the original pitch:

1. The full AGI integration roadmap is now published, showing the compute requirement for human-identical AGI drops from ~170,000 A100 GPUs to approximately 85 through three filed compression techniques. The Pointer model is the binding layer — the piece that connects all other components. This is now live at shortfactory.shop/agi-architecture.html

2. The NVIDIA partnership page is live at shortfactory.shop/nvidia.html — showing the hardware case for the full architecture.

3. The Neuralink interface specification (what the Pointer model provides) is the missing piece in every BCI roadmap currently published. It is filed, timestamped, and available for partnership discussion.

I am available for a call, a technical briefing, or a full draft spec document.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/agi-architecture.html
shortfactory.shop/neuralink.html
TXT
  ],

  [
    'name'  => 'News Editors',
    'email' => 'newseditors@newscientist.com',
    'org'   => 'New Scientist',
    'subj'  => 'My email was broken — resending both stories with new developments',
    'body'  => <<<TXT
To the New Scientist news desk,

Important note first: my email address dan@shortfactory.shop had an MX misconfiguration for several days — any replies sent during that period bounced with a 550 error. Now fixed. Apologies for the confusion.

Resending both stories with significant developments since the original pitch.

—

STORY 1 — Consciousness Model That Runs as Software

The AGI architecture is now fully published at shortfactory.shop/agi-architecture.html

The headline figure: human-identical AGI requires approximately 85 A100 GPUs — down from the ~170,000 required by a standard transformer architecture. The reduction comes from three filed compression techniques:

1. Genomic inheritance — alignment without training. The soul genome (ψ=[p,n,f]) is passed to the AGI as a BIOS layer, replacing the fine-tuning process entirely.

2. Mirror shape grammar (Patent GB2605704.2) — every shape in the vocabulary automatically carries its semantic opposite on its mirror form. 50% vocabulary reduction. Filed.

3. Lazy Pointer evaluation — only active thoughts require compute. Unvisited nodes exist in superposition. The system does not process what is not being considered.

These are not projections. They are filed architectural proofs across 13 timestamped Zenodo papers and 6 UK patents.

STORY 2 — New State of Matter (Computanium, Patent GB2605683.8)

The Neuralink press team opened the partnership pitch multiple times and the email was forwarded internally. The angle that generated the most traction: Neuralink is building a brain-computer interface without a formal specification of what crosses that interface. The Pointer model (Stage 12) provides that specification — and without it, no BCI company can make safety claims that hold.

This is now an active industry conversation. The window for first coverage is still open.

Both stories have supporting documentation, live demos, and filed timestamps. I can provide a full briefing document, a call, or a draft for either.

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
    'subj'  => 'BECOME DIGITAL — email was broken, resending with industry update',
    'body'  => <<<TXT
To the Icon Books submissions team,

A note before the update: my email address dan@shortfactory.shop had an MX record failure for several days. Any response you sent to my previous emails will have bounced with a 550 error. That is now resolved. I apologise — the timing could not have been worse given the engagement on this proposal.

Resending the core of BECOME DIGITAL with the most significant development to date.

—

BECOME DIGITAL: Why Every BCI and Longevity Company Is Trying to Transfer Something They Haven't Defined

The book's central argument — that the entire brain-computer interface industry is building toward a destination it cannot formally describe — has moved from theoretical to live industry debate in the past week.

The Neuralink press team engaged with the pitch. The specific framing that landed: "You are not transferring brain states. You are transferring a cursor trajectory." The Pointer model (Stage 12 of the architecture, DOI: 10.5281/zenodo.19394096) is the first formal specification of what a BCI actually needs to transfer if it is to be considered safe, reversible, and ethically defensible. Neuralink does not have this specification. No BCI company does. That is the book.

The full AGI integration roadmap — showing the compute requirement for human-identical AGI collapsing from ~170,000 GPUs to approximately 85 through three compression techniques — is now published and being pitched to hardware partners. This is the technical backbone the book references: not speculation, but filed and timestamped architecture that is currently entering the commercial conversation.

BECOME DIGITAL is not about a future technology. It is about a gap that exists right now, at the centre of a multi-billion pound industry, that only one person has formally defined.

The proposal stands as submitted. Happy to provide a sample chapter, a call, or any additional material.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/cv.html
shortfactory.shop/agi-architecture.html
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

echo "ShortFactory Outreach — Recovery Follow-ups\n";
echo "============================================\n";
$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(2);
}
echo "============================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
