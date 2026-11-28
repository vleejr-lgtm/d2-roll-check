/* D2 Roll Check sign-in worker (Cloudflare Workers, free plan).
   Bungie only gives refresh tokens to "Confidential" OAuth apps, and those need a client secret that must never be
   in the website. This worker holds the secret and does the two token calls for the site:
     POST /token    { code }           -> exchanges the sign-in code      (Bungie: grant_type=authorization_code)
     POST /refresh  { refresh_token }  -> gets a fresh 1 hour token       (Bungie: grant_type=refresh_token)
   It answers only the site's own origin (ALLOWED_ORIGIN) and passes Bungie's JSON straight back
   (access_token, expires_in, refresh_token, refresh_expires_in, membership_id). It stores nothing.
   Secrets (wrangler secret put ...): BUNGIE_CLIENT_ID, BUNGIE_CLIENT_SECRET, BUNGIE_API_KEY.
   Variable (wrangler.toml): ALLOWED_ORIGIN, e.g. https://vleejr-lgtm.github.io */
export default {
  async fetch(req, env){
    const origin = req.headers.get('Origin') || '';
    const allowed = origin === env.ALLOWED_ORIGIN;
    const cors = { 'Access-Control-Allow-Origin': allowed ? origin : 'null', 'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400', 'Vary': 'Origin' };
    if (req.method === 'OPTIONS') return new Response(null, { status: allowed ? 204 : 403, headers: cors });
    if (!allowed) return json({ error: 'origin_not_allowed' }, 403, cors);
    if (req.method !== 'POST') return json({ error: 'method_not_allowed' }, 405, cors);
    const path = new URL(req.url).pathname;
    let body = {}; try { body = await req.json(); } catch {}
    let form;
    if (path === '/token' && typeof body.code === 'string' && body.code.length < 512) form = 'grant_type=authorization_code&code=' + encodeURIComponent(body.code);
    else if (path === '/refresh' && typeof body.refresh_token === 'string' && body.refresh_token.length < 4096) form = 'grant_type=refresh_token&refresh_token=' + encodeURIComponent(body.refresh_token);
    else return json({ error: 'bad_request' }, 400, cors);
    const r = await fetch('https://www.bungie.net/Platform/App/OAuth/Token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-API-Key': env.BUNGIE_API_KEY,
        'Authorization': 'Basic ' + btoa(env.BUNGIE_CLIENT_ID + ':' + env.BUNGIE_CLIENT_SECRET) },
      body: form
    });
    const text = await r.text();
    return new Response(text, { status: r.status, headers: Object.assign({ 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }, cors) });
  }
};
const json = (o, status, headers) => new Response(JSON.stringify(o), { status, headers: Object.assign({ 'Content-Type': 'application/json' }, headers) });
