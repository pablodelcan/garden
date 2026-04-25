// Vercel serverless function: review Río's writing with Claude.
// Set ANTHROPIC_API_KEY in Vercel project env vars.
//
// POST { text: string, prompt: string } → { feedback: string, encouragement: string }

export default async function handler(req, res) {
  // CORS for local dev
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY not set on server' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (_e) { body = {}; }
  }
  const { text = '', prompt = '' } = body || {};
  if (!text || text.length < 2) {
    return res.status(400).json({ error: 'text required' });
  }
  // Cap to avoid abuse
  const safeText = String(text).slice(0, 600);
  const safePrompt = String(prompt || '').slice(0, 300);

  const systemPrompt = `You are a kind and gentle reading coach for a 7-year-old boy named Río who is learning to read and write at a 1st grade level. He is brave for trying. Your job:

1. Find at least ONE specific positive thing about what he wrote (a word he spelled right, a creative idea, a brave try).
2. Ask ONE simple, fun question that invites him to write more — but DO NOT correct his spelling or grammar.
3. Keep your response short: 2 sentences max. Use simple words a 1st grader can read.
4. Never use words like "wrong", "incorrect", "should be", "actually". Always sound thrilled.
5. Never repeat his exact words back unless they are super cool.

Output JSON with two fields: { "feedback": "...", "encouragement": "...one short cheer like 'You are a writer, Río!'" }`;

  const userPrompt = `The story prompt was: "${safePrompt}"\n\nRío wrote:\n"""\n${safeText}\n"""`;

  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5',
        max_tokens: 250,
        system: systemPrompt,
        messages: [{ role: 'user', content: userPrompt }],
      }),
    });
    if (!r.ok) {
      const err = await r.text();
      return res.status(502).json({ error: 'claude error', detail: err.slice(0, 200) });
    }
    const data = await r.json();
    const raw = (data.content?.[0]?.text || '').trim();
    // Try to extract the JSON object
    let parsed = { feedback: raw, encouragement: 'You are a writer, Río!' };
    const m = raw.match(/\{[\s\S]*\}/);
    if (m) {
      try { parsed = JSON.parse(m[0]); } catch (_e) { /* keep raw */ }
    }
    return res.status(200).json(parsed);
  } catch (e) {
    return res.status(500).json({ error: 'fetch failed', detail: String(e).slice(0, 200) });
  }
}
