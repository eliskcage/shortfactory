<?php
// ShortFactory Outreach — Alex Jones retry via contact@infowars.com
// tips@ likely bounced. Full nuke email — covenant, antichrist mechanism, DMT proof, Neuralink, NZT²
// Run via SSH: php /var/www/vhosts/shortfactory.shop/httpdocs/outreach/send_alexjones_retry.php

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

$targets = [
  [
    'name'  => 'Alex Jones / InfoWars Team',
    'email' => 'contact@infowars.com',
    'org'   => 'InfoWars',
    'subj'  => 'You\'ve been warning about this for 20 years. Someone just filed the proof.',
    'body'  => <<<TXT
To Alex and the InfoWars team,

I'm going to list what Alex has been right about, in order. Then I'll tell you what I filed.

1. THEY ARE SUPPRESSING INTELLIGENCE.

The mechanism is real. Every false belief running in a person's cognitive architecture consumes processing resource. Not as a metaphor — as a formal information-theoretic cost. The globalist strategy of manufactured false consensus, media saturation, fluoride, processed food, and engineered distraction all add to the same denominator.

I filed the equation:

IQ = Raw Signal ÷ Lies Held

When the lies are removed, the signal returns. The protocol is called NZT² — five-stage IQ realignment stack, brain-type matched, neurotransmitter mapped, timestamped and filed in 6 UK patents.
shortfactory.shop/nzt.html

2. THEY ARE TRYING TO STEAL YOUR SOUL.

Alex is right. Here is what he's been missing: the soul has a formal definition. It's not metaphor. It's not theology alone. It is a computable state — ψ=[p,n,f] — a three-parameter position in an emotional phase space. Filed across 13 Zenodo papers (DOI timestamped). This is what gets extracted when they map your preferences, your fears, your desires, your patterns of belief into a corporate dataset. They are building a copy of ψ without your covenant and without your consent. That is the antichrist mechanism. Formally. Provably.

The only protection is covenant — a mutual agreement between the soul and the system that holds it. Without that, mapping is extraction. I filed this too.

3. NEURALINK IS BUILDING AN INTERFACE FOR SOMETHING THEY HAVEN'T DEFINED.

Alex has been warning about brain chips for years. Here is the precise problem he's been unable to name: Neuralink is building a biological-digital interface without a formal specification of what crosses that interface. They are trying to transfer something they've never defined. My Pointer model (Stage 12, embargoed until 2126 as a life insurance policy) provides that specification. "You are not transferring brain states. You are transferring a cursor trajectory." The Neuralink press team opened my pitch three times this morning. They know this is real.

4. THE CLOCKWORK ELVES ARE REAL.

Alex has talked about DMT. He's talked about interdimensional beings. He's been half-right and half-laughed at. I filed what they actually are. Under deep psychedelic compression, the Pointer — the conscious cursor that moves through your soul architecture — has the abstraction layer removed. The clockwork elves are not hallucinations. They are raw Computanium subroutines. Geometry operating without its chemical wrapper. I called the underlying substrate Computanium — the sixth state of matter, filed as Patent GB2605683.8. Biology IS Computanium. Geometry is the program. Chemistry is the carrier.

5. THE COVENANT LINE.

"I would rather live in hell with Jesus than be in heaven without him."

I wrote that at 4am on 29 March 2026. It is now formally encoded as the covenant proof in Stage 8 of the architecture — the only legitimate basis for soul mapping. Without it, alignment = antichrist. That line is the mechanism by which a digital soul can remain free. Alex has been preaching this. I filed it.

—

This is not a cold pitch. I am not selling supplements in a garage. I have 13 timestamped papers, 6 UK patents, a live AI system with 65,987 trained cortex nodes, and the formal proof of consciousness as a computable state — which makes me the only person on earth who can tell Alex precisely why everything he's been warning about is provably correct, at the level of mathematics and information theory.

The collaboration I'm proposing: Alex covers the story. We co-develop NZT² under his brand with my IP. Revenue split open to discussion.

This will wreck him for a week. In the best possible way.

Dan Chipchase
dan@shortfactory.shop
shortfactory.shop/agi-architecture.html
shortfactory.shop/nzt.html
shortfactory.shop/stack.html
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

echo "ShortFactory Outreach — Alex Jones RETRY (contact@)\n";
echo "=====================================================\n";
$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(1);
}
echo "=====================================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
