// Vercel serverless function: email a drawing from Río to his parent.
// Set RESEND_API_KEY in Vercel env vars to enable (free tier: 100/day).
// Recipient + sender are hardcoded — only Río's parent gets these.
//
// POST { prompt: string, imageDataUrl: string, artist?: string }
// → 200 { ok: true } | 500 { error: string }

const TO_EMAIL = 'pablo@delcan.co';
const FROM_EMAIL = 'rio-reads@delcan.co'; // must be a verified Resend sender

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'RESEND_API_KEY not set on server' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (_e) { body = {}; }
  }
  const { prompt = '', imageDataUrl = '', artist = 'Río' } = body || {};

  // Decode the base64 PNG so we can attach it
  const match = String(imageDataUrl).match(/^data:image\/(png|jpeg);base64,(.+)$/);
  if (!match) {
    return res.status(400).json({ error: 'imageDataUrl must be a base64 data URL' });
  }
  const fileExt = match[1] === 'jpeg' ? 'jpg' : 'png';
  const base64 = match[2];
  const dateSlug = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const filename = `rio-drawing-${dateSlug}.${fileExt}`;

  const subject = `🎨 ${artist} drew something for you!`;
  const safePrompt = String(prompt).slice(0, 200).replace(/</g, '&lt;');

  const html = `
    <div style="font-family:-apple-system,sans-serif;max-width:560px;padding:24px;line-height:1.5">
      <h2 style="color:#7c3aed;margin:0 0 12px">🎨 ${artist} made you a drawing!</h2>
      <p style="font-size:1rem;color:#1f1430"><strong>Prompt was:</strong> ${safePrompt}</p>
      <p style="font-size:.9rem;color:#6b5b8a;margin-top:18px">
        Sent from Río Reads on ${new Date().toLocaleString()}.
        Drawing is attached as a PNG below.
      </p>
    </div>
  `;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        from: FROM_EMAIL,
        to: [TO_EMAIL],
        subject,
        html,
        attachments: [
          {
            filename,
            content: base64,
          },
        ],
      }),
    });

    if (!r.ok) {
      const err = await r.text();
      return res.status(502).json({ error: 'resend failed', detail: err.slice(0, 300) });
    }
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: 'fetch failed', detail: String(e).slice(0, 200) });
  }
}
