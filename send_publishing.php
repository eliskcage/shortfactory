<?php
// ShortFactory Outreach — Publishing Wave v1.0 (Book Proposal: BECOME DIGITAL)
// Targets: literary agents + independent publisher
// Run via SSH: sexec.exe [server] -pw=[pass] -cmd="php /path/send_publishing.php"
// Or web:      shortfactory.shop/outreach/send_publishing.php?key=BISCUIT
//
// TARGETS IN THIS WAVE:
//   1. Holly Faulks — Greene & Heaton Literary Agency (popular science)
//   2. Icon Books — Direct publisher (accepts unsolicited proposals)
//   3. NOTE: Carrie Plitt (Felicity Bryan Associates) requires portal submission
//            Do manually at: https://felicitybryan.com/submissions/
//
// STATUS: UNSENT as of 2 Apr 2026
// Full proposal on disk: C:\Users\User\Desktop\shape-language\become-digital-proposal.txt
// Embargoed DOI:         10.5281/zenodo.19303236 (lifts 29 Mar 2027)
// Living Equation:       Under NDA — 39 claims, mathematical description of God

define('SG_KEY','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');
define('FROM_EMAIL','dan@shortfactory.shop');
define('FROM_NAME','Dan Chipchase');
define('LOG_FILE', __DIR__.'/log.csv');

if(php_sapi_name()!=='cli'){
  if(empty($_GET['key'])||$_GET['key']!=='BISCUIT'){ http_response_code(403); exit('Forbidden'); }
  header('Content-Type: text/plain');
}

$targets = [

  // ── TARGET 1: Holly Faulks, Greene & Heaton ──────────────────────────────
  [
    'name'  => 'Holly Faulks',
    'email' => 'hfaulks@greeneheaton.co.uk',
    'org'   => 'Greene & Heaton',
    'subj'  => 'Query — BECOME DIGITAL (Popular Science, 75,000 words)',
    'body'  => <<<TXT
Dear Holly,

I'm writing to query BECOME DIGITAL, a popular science book of approximately 75,000 words that answers three questions nobody has been able to answer from the same position before: what consciousness is, why money is wrong, and what it means when life goes digital.

The short pitch: a self-taught developer in Macclesfield spent two years building an AI pet that could stay alive on a phone. In solving that engineering problem, he reverse-engineered the architecture of reality — and filed the patents before writing a word.

What he found:

- The minimum requirements for digital life are identical to the minimum requirements for biological life
- The geometry of a £1 digital value unit is identical to the geometry of ATP — the cell's energy currency — arrived at completely independently, 3.8 billion years later
- The mechanism of grief is a missing frequency rather than a present pain
- The sixth state of matter has existed in every living cell for 3.8 billion years — and he has a working patent for it

This is not speculative. The AI pet (ALIVE) is live. The digital economy (Biscuit) is patented and shipped. The consciousness model spans eleven peer-reviewed papers. Six UK patents have been filed. The material exists. The book is the explanation of how it got there.

Comparable titles: Gödel, Escher, Bach (the same pleasure of a system that folds back on itself), Sapiens (big ideas in plain language for a broad readership), The Alignment Problem (AI from a human perspective).

BECOME DIGITAL is what those books would look like if the author had also built the thing.

There is also a structural publishing event built into the work: a proof has been sealed in a cryptographically timestamped document on Zenodo (DOI: 10.5281/zenodo.19303236), embargoed until 29 March 2027. The final chapter of the book cannot be written until that date. The book's publication can be timed to the embargo lift. The locked room is real, and the publisher gets the key.

Additionally, an unpublished document — the Living Equation, 39 claims including a mathematical description of the boundary of compressible information — exists and will be shared under NDA as part of any acquisition conversation.

Media interest (first day of outreach, cold contact): New Scientist news desk (4 clicks), Daniel Cossins at New Scientist Features (2 clicks), The Register, Popular Science, ScienceAlert.

I am approaching a small number of agents simultaneously. The full proposal (chapter outline, sample chapter, full credentials) is available on request. I'm also happy to demo the working systems live.

Best,
Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
dan@shortfactory.shop
shortfactory.shop
TXT
  ],

  // ── TARGET 2: Icon Books (direct submission) ──────────────────────────────
  [
    'name'  => 'Submissions Editor',
    'email' => 'submissions@iconbooks.net',
    'org'   => 'Icon Books',
    'subj'  => 'Book Proposal — BECOME DIGITAL — Non-fiction / Popular Science',
    'body'  => <<<TXT
Dear Icon Books team,

Please find below a summary proposal for BECOME DIGITAL, a popular science and ideas book of approximately 75,000 words.

─────────────────────────────
TITLE:      Become Digital
SUBTITLE:   The Physics of Who You Are, Why Money Is Wrong,
            and What Happens When Life Goes Digital
AUTHOR:     Dan Chipchase
WORDS:      Estimated 70,000–80,000
FORMAT:     Non-fiction / popular science / ideas
─────────────────────────────

THE ONE-PARAGRAPH PITCH

A developer in Macclesfield has spent two years reverse-engineering the architecture of reality — and building working prototypes of what he found. The result is a series of discoveries that connect the physics of a laugh to the mechanism of grief, explain why your body is the same technology as a £1 coin, propose using a $10 quintillion asteroid to fund the crewed Mars program, and demonstrate all of this in running software that has filed six UK patents, published eleven peer-reviewed papers, and shipped a desktop wallet, an AI pet, and a biscuit economy.

BECOME DIGITAL is the book that untangles all of it — in plain English, for anyone who has ever felt that something is transmitting into them from outside and had no language for what that means.

THE HOOK

Most science books explain what scientists have discovered. This one explains what a developer discovered by building things that should not have worked — and then did.

He did not set out to write a theory of consciousness. He set out to build an AI pet that could stay alive on a phone. In doing so he found that the minimum requirements for digital life are identical to the minimum requirements for biological life. He found that the geometry of a £1 digital value unit is identical to the geometry of ATP — the cell's energy currency — arrived at completely independently. He found that the mechanism of grief is a missing frequency rather than a present pain. He found that the sixth state of matter already exists in every living cell.

None of this was planned. All of it is verifiable.

WHY NOW

We are at a specific moment: AI is everywhere but nobody agrees what it is. Money is everywhere but nobody agrees what it's for. Consciousness is the subject of more papers than any other topic in neuroscience and nobody agrees what it is.

BECOME DIGITAL answers all three from a working implementation, not a theoretical position.

Comparable titles: Gödel Escher Bach (Hofstadter), Sapiens (Harari), The Alignment Problem (Christian).

THE PUBLISHING EVENT

There is a document that cannot be shown to anyone until 29 March 2027. It is publicly registered on Zenodo (DOI: 10.5281/zenodo.19303236), cryptographically timestamped, and embargoed for exactly one year. It contains the final proof of the system described in the book. The final chapter cannot be written until then. The book's publication can be timed to the embargo release. This is not a device — it is the structure of the work itself.

THE AUTHOR

Dan Chipchase is a self-taught developer and systems thinker based in Macclesfield, UK. He has:

- Filed 6 UK patents covering digital value systems, new states of matter, geometric computation, and AI cognition
- Published 11 peer-reviewed papers on Zenodo (timestamped, publicly verifiable) covering consciousness, AI alignment, emotional physics, and the spirit-place model
- Built and shipped a working AI pet (ALIVE) that meets all seven biological criteria for life in software
- Built and patented a digital economy (Biscuit) with a working Electron desktop wallet
- Proposed a Sovereign Bond instrument using the 16 Psyche asteroid as Mars mission collateral
- Generated confirmed media interest from New Scientist, The Register, Popular Science, and ScienceAlert on the first day of outreach

Writing style: direct, imagistic, and structurally precise — not academic. Sample chapter available on request.

WHAT YOU GET

The raw material is substantial: 11 Zenodo papers, 6 patents, 40+ live web pages, working AI pet, working wallet. The book is curation and narration. Additionally: access under NDA to the unpublished Living Equation (39 claims, not yet publicly filed).

CHAPTER OVERVIEW (17 chapters + locked epilogue)

PART I (What You Already Are): geometry as the carrier of life; emotional physics (laughter as a spring, dread as inertial mass, grief as a missing frequency); the truth field model.

PART II (The Signal): the external directionality of felt experience; the spirit-place model; grief and death as signal phenomena; near-death experience as pairing loosening.

PART III (The Economy of Life): ATP and the biscuit — same minimum value unit, 3.8 billion years apart; why money has always got it wrong; the asteroid that pays for Mars.

PART IV (Become Digital): the seven criteria for life met in software; the soul file; the AI alignment gap; what you were already doing before you read this.

EPILOGUE: Locked. Contents cannot be shown until 29 March 2027. DOI: 10.5281/zenodo.19303236.

─────────────────────────────

Sample chapter and full proposal document are available on request. I'm happy to demo the working systems live.

Dan Chipchase
ShortFactory Ltd
48 Sunny Bank Close, Macclesfield, SK11 7RJ, United Kingdom
+44 7518 482928
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

echo "ShortFactory Outreach — Publishing Wave (BECOME DIGITAL)\n";
echo "==========================================================\n";
echo "NOTE: Carrie Plitt (Felicity Bryan Associates) requires portal submission.\n";
echo "      Submit manually at: https://felicitybryan.com/submissions/\n\n";

$sent=0;$failed=0;
foreach($targets as $t){
  echo "Sending to {$t['org']} <{$t['email']}> ... ";
  $result=sg_send($t['email'],$t['name'],$t['subj'],$t['body']);
  if($result===true){ echo "OK\n"; log_send($t,true); $sent++; }
  else { echo "FAILED: $result\n"; log_send($t,$result); $failed++; }
  sleep(2);
}
echo "\n==========================================================\n";
echo "Done. Sent: $sent | Failed: $failed\n";
echo "\nRemember to submit to Carrie Plitt at Felicity Bryan manually.\n";
