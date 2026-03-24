/**
 * ai-outreach.shortfactory.shop
 * Automated outreach pipeline — runs on cron schedule.
 * Every hour: grabs new leads → enriches → drafts email → queues send.
 *
 * Cron: 0 * * * * (every hour)
 * POST /run  → manual trigger
 * GET  /status → pipeline stats
 * GET  /ping
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json',
};

const LEADS_URL = 'https://ai-leads.shortfactory.shop';
const RESEND_API = 'https://api.resend.com/emails';
const FROM_EMAIL = 'dan@shortfactory.shop';
const FROM_NAME = 'Dan @ ShortFactory';
const GCAL_API = 'https://www.googleapis.com/calendar/v3';

async function processLead(lead, env) {
  const log = [];

  // 1. Enrich if not yet profiled
  if (!lead.profile) {
    const er = await fetch(`${LEADS_URL}/enrich`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lead_id: lead.id }),
    });
    const enriched = await er.json();
    log.push(`Enriched: score ${enriched.score}/10`);
    if (enriched.score < 4) {
      log.push('Score too low, skipping');
      return { lead_id: lead.id, skipped: true, reason: 'low score', log };
    }
  }

  // 2. Draft email
  const dr = await fetch(`${LEADS_URL}/draft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lead_id: lead.id }),
  });
  const drafted = await dr.json();
  if (!drafted.ok) { log.push('Draft failed'); return { lead_id: lead.id, error: 'draft failed', log }; }
  log.push('Email drafted');

  // 3. Send email via Resend (if API key configured)
  if (env.RESEND_API_KEY) {
    const draft = drafted.draft || '';
    const subjectMatch = draft.match(/SUBJECT:\s*(.+)/i);
    const subject = subjectMatch ? subjectMatch[1].trim() : `ShortFactory — AI video ads for ${lead.company || 'your business'}`;
    const body = draft.replace(/SUBJECT:\s*.+\n?/i, '').trim();

    const emailRes = await fetch(RESEND_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: `${FROM_NAME} <${FROM_EMAIL}>`,
        to: [lead.email],
        subject,
        text: body,
      }),
    });
    const emailData = await emailRes.json();
    if (emailRes.ok) {
      log.push(`Email sent: ${emailData.id}`);
      // Mark as contacted
      await fetch(`${LEADS_URL}/mark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_id: lead.id, status: 'contacted' }),
      });
    } else {
      log.push(`Email failed: ${JSON.stringify(emailData)}`);
    }
  } else {
    log.push('RESEND_API_KEY not set — email queued only');
  }

  // 4. Create follow-up calendar event (7 days from now)
  if (env.GCAL_TOKEN) {
    const followUp = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    const start = followUp.toISOString().split('.')[0];
    const end = new Date(followUp.getTime() + 30 * 60 * 1000).toISOString().split('.')[0];

    await fetch(`${GCAL_API}/calendars/primary/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.GCAL_TOKEN}`,
      },
      body: JSON.stringify({
        summary: `Follow up: ${lead.name} @ ${lead.company || lead.email}`,
        description: `Lead from ShortFactory pipeline.\nEmail: ${lead.email}\n\nDraft sent — check response.`,
        start: { dateTime: `${start}+00:00` },
        end: { dateTime: `${end}+00:00` },
        reminders: { useDefault: false, overrides: [{ method: 'popup', minutes: 60 }] },
      }),
    });
    log.push('Follow-up calendar event created');
  }

  return { lead_id: lead.id, ok: true, log };
}

export default {
  // Cron handler — runs every hour
  async scheduled(event, env, ctx) {
    ctx.waitUntil(runPipeline(env));
  },

  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: CORS });
    const json = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: CORS });

    if (url.pathname === '/ping') return json({ status: 'ok', version: '1.0', service: 'ai-outreach' });

    if (url.pathname === '/run' && request.method === 'POST') {
      const results = await runPipeline(env);
      return json({ ok: true, results });
    }

    if (url.pathname === '/status') {
      const leadsRes = await fetch(`${LEADS_URL}/leads?status=new&limit=5`);
      const leads = await leadsRes.json();
      return json({ ok: true, pending: leads.count, sample: leads.leads?.slice(0, 3) });
    }

    return json({ error: 'not found' }, 404);
  },
};

async function runPipeline(env) {
  const res = await fetch(`${LEADS_URL}/leads?status=new&limit=10`);
  const data = await res.json();
  if (!data.leads?.length) return { processed: 0, message: 'No new leads' };

  const results = [];
  for (const lead of data.leads) {
    try {
      const r = await processLead(lead, env);
      results.push(r);
      // Throttle — don't spam
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (e) {
      results.push({ lead_id: lead.id, error: e.message });
    }
  }
  return { processed: results.length, results };
}
