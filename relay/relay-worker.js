/**
 * ReaderWrangler Relay Worker
 * Cloudflare Worker that relays encrypted library data between
 * the bookmarklet (amazon.com) and the app (readerwrangler.com).
 *
 * KV Namespace binding: RELAY_KV
 *
 * Key layout (legacy, single-generation — being replaced by the redesign below):
 *   relay:{channelId}:manifest         → upload manifest (TTL: 10 days)
 *   relay:{channelId}:chunk:{n}        → encrypted library chunk (TTL: 10 days)
 *   relay:{channelId}:device-state     → encrypted device state (TTL: 90 days)
 *
 * Key layout (relay write redesign Phase 1 — see docs/design/RELAY-WRITE-REDESIGN.md):
 *   relay:{channelId}:mail:{runId}:{seq}      → mailbox letter, encrypted (TTL: 90 days)
 *   relay:{channelId}:mail:{runId}:manifest   → run manifest JSON; presence = run committed (TTL: 90 days)
 *                                               (single-letter runs inline manifest+payload at seq 0, no separate manifest)
 *   relay:{channelId}:gen:{gen}:chunk:{i}     → generation chunk, encrypted (NO TTL — GC'd by keep-2)
 *   relay:{channelId}:gen:{gen}:manifest      → generation manifest JSON incl. absorbedRuns (NO TTL)
 *   relay:{channelId}:pointer                 → JSON { gen } naming the current generation (NO TTL)
 *   relay:{channelId}:dstate:{gen}:chunk:{i}  → device-state journal chunk (TTL: 90 days) — Phase 1b
 *   relay:{channelId}:dstate:{gen}:manifest   → device-state generation manifest (TTL: 90 days)
 *   relay:{channelId}:dstate-pointer          → JSON { gen } naming the live device-state (TTL: 90 days)
 *   runId/gen format: {workerTimestampMs}-{deviceId}-{rand4hex} — minted server-side so
 *   timestamps can't be skewed by client clocks; '-' internal separator, ':' reserved for key layout.
 *
 * Shared:
 *   relay:{channelId}:revocation-proof → SHA-256 proof hash (permanent)
 *   ratelimit:{channelId}              → write counter per hour (TTL: 2 hours)
 *   blocklist:{channelId}              → permanently blocked channel (no TTL)
 *   lifecycle:{channelId}:used         → ISO timestamp of first successful manifest upload (permanent, lifecycle telemetry)
 *   test-alert-counter                 → test alert sequence number
 *   usage-alert:{YYYY-MM-DD}           → counter-threshold alerts already sent today (TTL: 2 days)
 *   usage-alert:storage-band           → last alerted storage band: 0/25/50/75/90 (no TTL)
 *   cron-mistriggers                   → schedules that fired but aren't this relay's, since the last summary (TTL: 7 days)
 *   (both usage-alert keys exist only in PRODUCTION's namespace — only prod sends threshold alerts; since 7.22.0
 *    they track the TOTAL across both relays)
 *
 * Deployed twice from this one file (wrangler.toml): RELAY_ENV = "prod" | "dev" names the deployment — see RELAYS.
 */

const LIBRARY_TTL = 864000;    // 10 days in seconds (legacy fetcher→app relay data)
const PERSISTENT_TTL = 7776000; // 90 days in seconds (device-state sync)
const LETTER_TTL = 7776000;    // 90 days in seconds (mailbox letters — sized to absence windows, not merge cadence)
const MAX_CHUNK_SIZE = 25 * 1024 * 1024; // 25 MB (KV value limit)
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
// Server-minted ids: {timestampMs}-{deviceId}-{rand4hex}. Device id is client-chosen but sanitized.
const MINTED_ID_REGEX = /^\d{13}-[A-Za-z0-9_]{1,32}-[0-9a-f]{4}$/;
const DEVICE_ID_REGEX = /^[A-Za-z0-9_]{1,32}$/;
const LIST_PAGE_CAP = 10; // safety cap on KV list pagination loops (10 × 1000 keys)

// Phase 1b: generational stores share ONE implementation — the canonical library and the
// device-state journal differ only in key segment, pointer key, and TTL policy.
//   canonical: no TTL (lifecycle = keep-2 + GC; a rarely-rewritten library must never expire)
//   dstate:    90d TTL, refreshed by every push (mobile snapshot; old single-key behavior kept)
const GEN_STORES = {
  canonical: { seg: 'gen',    ptr: 'pointer',        ttl: null },
  dstate:    { seg: 'dstate', ptr: 'dstate-pointer', ttl: PERSISTENT_TTL }
};
const RATE_LIMIT_WINDOW_MS = 3600000; // 1 hour
const RATE_LIMIT_MAX_WRITES = 200;    // per channelId per hour (normal: ~10-20)
const RATE_LIMIT_AUTO_BLOCK = 2000;   // 10x limit → permanent blocklist
const RATE_LIMIT_SAMPLE = 5;          // v7.5.0 - persist the counter 1-in-N (counting by N):
                                      // the counter write was ~HALF of ALL KV writes (one per
                                      // authenticated request). The counter has always been
                                      // best-effort/approximate; sampling changes no semantics,
                                      // only granularity (200/hr limit ± ~5).

// Cloudflare free tier daily limits — ACCOUNT-WIDE (both relays share them), so alerts compare the TOTAL.
// Storage is in decimal MB (bytes / 1,000,000) to match the Cloudflare dashboard; "1 GB" is taken as 1,000 MB (the
// stricter reading — Cloudflare doesn't say which GB it means). Until 7.22.0 the email divided by 1024² (design §14a F6).
const CF_LIMITS = {
  requests:   { limit: 100000, label: 'Worker requests' },
  kvReads:    { limit: 100000, label: 'KV reads' },
  kvWrites:   { limit: 1000,   label: 'KV writes' },
  kvDeletes:  { limit: 1000,   label: 'KV deletes' },
  kvLists:    { limit: 1000,   label: 'KV lists' },
  kvStorageMB:{ limit: 1000,   label: 'KV storage' },
};
// Cloudflare's KV actionType → our counter. An action type not listed here is reported in the email, never dropped.
const KV_ACTION_FIELDS = { read: 'kvReads', write: 'kvWrites', delete: 'kvDeletes', list: 'kvLists' };

const WORKER_VERSION = '7.23.0'; // printed in every daily summary, so an email shows which deploy sent it

// THE list of relays (7.22.0, design §14a fix 2). One codebase, deployed twice; RELAY_ENV in wrangler.toml says which
// deployment this is. Every daily summary reports ALL relays here (the free limits are shared account-wide); each
// worker inspects only its OWN storage (it can only reach its own bound namespace). Names/ids mirror wrangler.toml.
const RELAYS = {
  prod: { label: 'Production', worker: 'readerwrangler-relay',     kvId: '4a445b412fb34860a896cfc145a67b9b',
          sendsThresholdAlerts: true },
  dev:  { label: 'Dev',        worker: 'readerwrangler-relay-dev', kvId: '58116108eead40d18a55e59d799472b3',
          sendsThresholdAlerts: false }, // prod alone alerts for now (step C adds a dev backup alerter)
};
// Each schedule's ONE job (7.22.0-alpha.4). A schedule not listed here — or the threshold check on a relay that doesn't
// alert — does NOTHING but get counted: on 2026-10-13/14 a Cloudflare incident kept firing dev's old 10-minute test
// schedule for hours after it was replaced, mailing a summary every time. Matched by the schedule's TEXT (Cloudflare
// hands the firing schedule to scheduled() as event.cron), never by clock time — so a late run is still recognized.
// Schedules must also match wrangler.toml.
const SUMMARY_CRON = '55 23 * * *';
const THRESHOLD_CRON = '*/30 * * * *';
const MISTRIGGER_KEY = 'cron-mistriggers';  // { crons: { "<cron>": count }, first, last } since the last summary
const MISTRIGGER_WRITE_CAP = 24;            // tally saves between summaries — a stuck every-minute schedule must not
                                            // eat the 1,000/day KV write quota; past the cap the email says "24 or more"

// This deployment's RELAYS entry. Fails LOUD on a missing/unknown RELAY_ENV (the cron error mail names the fix).
function thisRelay(env) {
  const relay = RELAYS[env.RELAY_ENV];
  if (!relay) throw new Error(`RELAY_ENV is "${env.RELAY_ENV}" — must be ${Object.keys(RELAYS).join(' or ')} (set in wrangler.toml)`);
  return { key: env.RELAY_ENV, ...relay };
}
const THRESHOLDS = [25, 50, 75, 90];

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return corsResponse(request, env, new Response(null, { status: 204 }));
    }

    // CORS origin check
    const origin = request.headers.get('Origin');
    if (origin && !isAllowedOrigin(origin, env)) {
      return new Response('Forbidden', { status: 403 });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      const response = await route(request, path, env);
      return corsResponse(request, env, response);
    } catch (err) {
      return corsResponse(request, env,
        new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        })
      );
    }
  },

  async scheduled(event, env, ctx) {
    const cron = event.cron;
    try {
      const self = thisRelay(env);
      if (cron === SUMMARY_CRON) await sendDailySummary(env);
      else if (cron === THRESHOLD_CRON && self.sendsThresholdAlerts) await checkUsageThresholds(env);
      else await recordMistrigger(env, cron); // not this relay's schedule — count it, run nothing
    } catch (err) {
      await sendAlert(env, 'Cron error', `Cron "${cron}" failed: ${err.message}\nTime: ${new Date().toISOString()}`);
    }
  }
};

async function route(request, path, env) {
  // POST /upload/{channelId}/chunk/{n}
  let match = path.match(/^\/upload\/([^/]+)\/chunk\/(\d+)$/);
  if (match && request.method === 'POST') {
    return handleUploadChunk(request, env, match[1], parseInt(match[2]));
  }

  // POST /upload/{channelId}/manifest
  match = path.match(/^\/upload\/([^/]+)\/manifest$/);
  if (match && request.method === 'POST') {
    return handleUploadManifest(request, env, match[1]);
  }

  // GET /status/{channelId}
  match = path.match(/^\/status\/([^/]+)$/);
  if (match && request.method === 'GET') {
    return handleStatus(env, match[1]);
  }

  // GET /download/{channelId}/chunk/{n}
  match = path.match(/^\/download\/([^/]+)\/chunk\/(\d+)$/);
  if (match && request.method === 'GET') {
    return handleDownloadChunk(env, match[1], parseInt(match[2]));
  }

  // DELETE /cleanup/{channelId}
  match = path.match(/^\/cleanup\/([^/]+)$/);
  if (match && request.method === 'DELETE') {
    return handleCleanup(env, match[1]);
  }

  // PUT /device-state/{channelId}
  match = path.match(/^\/device-state\/([^/]+)$/);
  if (match && request.method === 'PUT') {
    return handlePutDeviceState(request, env, match[1]);
  }

  // GET /device-state/{channelId}
  match = path.match(/^\/device-state\/([^/]+)$/);
  if (match && request.method === 'GET') {
    return handleGetDeviceState(env, match[1]);
  }

  // POST /revoke/{channelId}
  match = path.match(/^\/revoke\/([^/]+)$/);
  if (match && request.method === 'POST') {
    return handleRevoke(request, env, match[1]);
  }

  // --- Relay write redesign Phase 1: mailbox ---

  // POST /mail/{channelId}/run — mint a runId (no KV write)
  match = path.match(/^\/mail\/([^/]+)\/run$/);
  if (match && request.method === 'POST') {
    return handleMintId(request, env, match[1], 'run');
  }

  // POST /mail/{channelId}/letter — single self-committing letter (inline manifest)
  match = path.match(/^\/mail\/([^/]+)\/letter$/);
  if (match && request.method === 'POST') {
    return handleSingleLetter(request, env, match[1]);
  }

  // POST /mail/{channelId}/{runId}/letter/{seq}
  match = path.match(/^\/mail\/([^/]+)\/([^/]+)\/letter\/(\d+)$/);
  if (match && request.method === 'POST') {
    return handlePutLetter(request, env, match[1], match[2], parseInt(match[3]));
  }

  // POST /mail/{channelId}/{runId}/manifest — commits the run (written last)
  match = path.match(/^\/mail\/([^/]+)\/([^/]+)\/manifest$/);
  if (match && request.method === 'POST') {
    return handlePutRunManifest(request, env, match[1], match[2]);
  }

  // GET /mail/{channelId}/list — enumerate mailbox keys (1 KV list op per page)
  match = path.match(/^\/mail\/([^/]+)\/list$/);
  if (match && request.method === 'GET') {
    return handleMailList(env, match[1]);
  }

  // GET /mail/{channelId}/{runId}/letter/{seq}
  match = path.match(/^\/mail\/([^/]+)\/([^/]+)\/letter\/(\d+)$/);
  if (match && request.method === 'GET') {
    return handleGetLetter(env, match[1], match[2], parseInt(match[3]));
  }

  // GET /mail/{channelId}/{runId}/manifest
  match = path.match(/^\/mail\/([^/]+)\/([^/]+)\/manifest$/);
  if (match && request.method === 'GET') {
    return handleGetRunManifest(env, match[1], match[2]);
  }

  // DELETE /mail/{channelId}/{runId} — early GC of an absorbed bulk run
  match = path.match(/^\/mail\/([^/]+)\/([^/]+)$/);
  if (match && request.method === 'DELETE') {
    return handleDeleteRun(env, match[1], match[2]);
  }

  // --- Relay write redesign Phase 1: generations + pointer ---

  // Generational stores: /gen + /pointer = canonical library; /dstate + /dstate-pointer =
  // device-state journal (Phase 1b). Same handlers, different GEN_STORES config.
  for (const [route, store] of [['gen', GEN_STORES.canonical], ['dstate', GEN_STORES.dstate]]) {
    // POST /{route}/{channelId}/begin — mint a generation id (no KV write)
    match = path.match(new RegExp(`^/${route}/([^/]+)/begin$`));
    if (match && request.method === 'POST') {
      return handleMintId(request, env, match[1], 'gen');
    }

    // POST /{route}/{channelId}/{gen}/chunk/{i}
    match = path.match(new RegExp(`^/${route}/([^/]+)/([^/]+)/chunk/([0-9]+)$`));
    if (match && request.method === 'POST') {
      return handlePutGenChunk(request, env, store, match[1], match[2], parseInt(match[3]));
    }

    // POST /{route}/{channelId}/{gen}/manifest — the atomic commit (written last)
    match = path.match(new RegExp(`^/${route}/([^/]+)/([^/]+)/manifest$`));
    if (match && request.method === 'POST') {
      return handlePutGenManifest(request, env, store, match[1], match[2]);
    }

    // GET /{route}/{channelId}/list — enumerate generation manifests (fallback discovery/GC)
    match = path.match(new RegExp(`^/${route}/([^/]+)/list$`));
    if (match && request.method === 'GET') {
      return handleGenList(env, store, match[1]);
    }

    // GET /{route}/{channelId}/{gen}/chunk/{i}
    match = path.match(new RegExp(`^/${route}/([^/]+)/([^/]+)/chunk/([0-9]+)$`));
    if (match && request.method === 'GET') {
      return handleGetGenChunk(env, store, match[1], match[2], parseInt(match[3]));
    }

    // GET /{route}/{channelId}/{gen}/manifest
    match = path.match(new RegExp(`^/${route}/([^/]+)/([^/]+)/manifest$`));
    if (match && request.method === 'GET') {
      return handleGetGenManifest(env, store, match[1], match[2]);
    }

    // DELETE /{route}/{channelId}/{gen} — GC (refuses the currently-pointed generation)
    match = path.match(new RegExp(`^/${route}/([^/]+)/([^/]+)$`));
    if (match && request.method === 'DELETE') {
      return handleDeleteGen(env, store, match[1], match[2]);
    }
  }

  // PUT|GET /pointer/{channelId} and /dstate-pointer/{channelId} — the atomic flips
  for (const [route, store] of [['pointer', GEN_STORES.canonical], ['dstate-pointer', GEN_STORES.dstate]]) {
    match = path.match(new RegExp(`^/${route}/([^/]+)$`));
    if (match && request.method === 'PUT') {
      return handlePutPointer(request, env, store, match[1]);
    }
    if (match && request.method === 'GET') {
      return handleGetPointer(env, store, match[1]);
    }
  }

  // POST /test-alert?key={TEST_ALERT_KEY} — send a test email alert
  match = path.match(/^\/test-alert$/);
  if (match && request.method === 'POST') {
    const testUrl = new URL(request.url);
    if (!env.TEST_ALERT_KEY || testUrl.searchParams.get('key') !== env.TEST_ALERT_KEY) {
      return jsonResponse({ error: 'Unauthorized' }, 401);
    }
    const countKey = 'test-alert-counter';
    const prev = parseInt(await env.RELAY_KV.get(countKey) || '0');
    const count = prev + 1;
    await env.RELAY_KV.put(countKey, String(count));
    await sendAlert(env, `Test Alert #${count}`, `Test alert #${count} from the ReaderWrangler relay worker.\nSent: ${new Date().toISOString()}`);
    return jsonResponse({ ok: true, message: `Alert #${count} sent` });
  }

  // POST /run-summary?key={TEST_ALERT_KEY} — send the daily summary NOW (7.22.0): the way to test it. A temporary test
  // schedule is not — Cloudflare can take 15 minutes to hours to apply (or remove) a schedule change.
  match = path.match(/^\/run-summary$/);
  if (match && request.method === 'POST') {
    if (!env.TEST_ALERT_KEY || new URL(request.url).searchParams.get('key') !== env.TEST_ALERT_KEY) {
      return jsonResponse({ error: 'Unauthorized' }, 401);
    }
    await sendDailySummary(env);
    return jsonResponse({ ok: true, message: 'Summary sent' });
  }

  return new Response('Not Found', { status: 404 });
}

// --- Handlers ---

async function handleUploadChunk(request, env, channelId, chunkNum) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);
  const body = await request.arrayBuffer();
  if (body.byteLength > MAX_CHUNK_SIZE) return badRequest('Chunk too large');

  await env.RELAY_KV.put(
    `relay:${channelId}:chunk:${chunkNum}`,
    body,
    { expirationTtl: LIBRARY_TTL }
  );

  return jsonResponse({ ok: true, chunk: chunkNum, bytes: body.byteLength });
}

async function handleUploadManifest(request, env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);
  const manifest = await request.text();

  // Validate it's parseable JSON
  try {
    JSON.parse(manifest);
  } catch {
    return badRequest('Manifest must be valid JSON');
  }

  await env.RELAY_KV.put(
    `relay:${channelId}:manifest`,
    manifest,
    { expirationTtl: LIBRARY_TTL }
  );

  // Lifecycle telemetry: first successful manifest upload per channel
  const usedKey = `lifecycle:${channelId}:used`;
  if (!await env.RELAY_KV.get(usedKey)) {
    await env.RELAY_KV.put(usedKey, new Date().toISOString());
    await fireGoatCounter(env, 'relay-channel-used');
  }

  return jsonResponse({ ok: true });
}

async function handleStatus(env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const manifest = await env.RELAY_KV.get(`relay:${channelId}:manifest`);
  if (!manifest) return new Response('No data available', { status: 404 });

  return new Response(manifest, {
    headers: { 'Content-Type': 'application/json' }
  });
}

async function handleDownloadChunk(env, channelId, chunkNum) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const chunk = await env.RELAY_KV.get(`relay:${channelId}:chunk:${chunkNum}`, 'arrayBuffer');
  if (!chunk) return new Response('Chunk not found', { status: 404 });

  return new Response(chunk, {
    headers: { 'Content-Type': 'application/octet-stream' }
  });
}

async function handleCleanup(env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  // Get manifest to find chunk count
  const manifestStr = await env.RELAY_KV.get(`relay:${channelId}:manifest`);
  const deletes = [env.RELAY_KV.delete(`relay:${channelId}:manifest`)];

  if (manifestStr) {
    try {
      const manifest = JSON.parse(manifestStr);
      for (let i = 0; i < (manifest.chunkCount || 1); i++) {
        deletes.push(env.RELAY_KV.delete(`relay:${channelId}:chunk:${i}`));
      }
    } catch {
      // If manifest isn't parseable, delete chunk:0 as best effort
      deletes.push(env.RELAY_KV.delete(`relay:${channelId}:chunk:0`));
    }
  }

  await Promise.all(deletes);
  return jsonResponse({ ok: true });
}

async function handlePutDeviceState(request, env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);
  const body = await request.arrayBuffer();
  if (body.byteLength > MAX_CHUNK_SIZE) return badRequest('Device state too large');

  await env.RELAY_KV.put(`relay:${channelId}:device-state`, body,
    { expirationTtl: PERSISTENT_TTL }
  );
  return jsonResponse({ ok: true });
}

async function handleGetDeviceState(env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const data = await env.RELAY_KV.get(`relay:${channelId}:device-state`, 'arrayBuffer');
  if (!data) return new Response('No device state', { status: 404 });

  return new Response(data, {
    headers: { 'Content-Type': 'application/octet-stream' }
  });
}

// --- Relay write redesign Phase 1: mailbox + generations + pointer ---
// See docs/design/RELAY-WRITE-REDESIGN.md. Invariants enforced here:
//   - runId/gen ids are MINTED SERVER-SIDE (worker timestamp — client clocks can't skew "newest").
//   - The worker never interprets payloads (ciphertext in, ciphertext out); manifests are
//     structural JSON the worker validates for parseability only.
//   - DELETE /gen refuses the currently-pointed generation (GC guard).

function mintId(deviceId) {
  const rand = Array.from(crypto.getRandomValues(new Uint8Array(2)))
    .map(b => b.toString(16).padStart(2, '0')).join('');
  return `${Date.now()}-${deviceId}-${rand}`;
}

// POST /mail/{ch}/run and POST /gen/{ch}/begin — mint an id; costs no KV operations.
async function handleMintId(request, env, channelId, kind) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  const deviceId = new URL(request.url).searchParams.get('device') || 'unknown';
  if (!DEVICE_ID_REGEX.test(deviceId)) return badRequest('Invalid device id');
  const id = mintId(deviceId);
  return jsonResponse(kind === 'run' ? { runId: id, timestamp: Date.now() }
                                     : { gen: id, timestamp: Date.now() });
}

// POST /mail/{ch}/letter — single-letter run: manifest fields + payload in ONE value,
// one atomic put, complete by definition (halves the cost of the most frequent op: wishlist add).
async function handleSingleLetter(request, env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);
  const deviceId = new URL(request.url).searchParams.get('device') || 'unknown';
  if (!DEVICE_ID_REGEX.test(deviceId)) return badRequest('Invalid device id');

  const body = await request.text();
  if (body.length > MAX_CHUNK_SIZE) return badRequest('Letter too large');
  try { JSON.parse(body); } catch { return badRequest('Single letter must be valid JSON (manifest fields + payload)'); }

  const runId = mintId(deviceId);
  await env.RELAY_KV.put(`relay:${channelId}:mail:${runId}:0`, body, { expirationTtl: LETTER_TTL });
  return jsonResponse({ ok: true, runId, inline: true });
}

async function handlePutLetter(request, env, channelId, runId, seq) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(runId)) return badRequest('Invalid run id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);

  const body = await request.arrayBuffer();
  if (body.byteLength > MAX_CHUNK_SIZE) return badRequest('Letter too large');

  await env.RELAY_KV.put(`relay:${channelId}:mail:${runId}:${seq}`, body, { expirationTtl: LETTER_TTL });
  return jsonResponse({ ok: true, runId, seq, bytes: body.byteLength });
}

// The run manifest is written LAST by the producer; its presence commits the run.
async function handlePutRunManifest(request, env, channelId, runId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(runId)) return badRequest('Invalid run id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);

  const manifest = await request.text();
  try { JSON.parse(manifest); } catch { return badRequest('Manifest must be valid JSON'); }

  await env.RELAY_KV.put(`relay:${channelId}:mail:${runId}:manifest`, manifest, { expirationTtl: LETTER_TTL });
  return jsonResponse({ ok: true, runId });
}

// GET /mail/{ch}/list — key names only (grouping/completeness is the client's job;
// completeness must be verified by GETs, not trusted from a list — see design M5).
async function handleMailList(env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const prefix = `relay:${channelId}:mail:`;
  const keys = [];
  let cursor;
  for (let page = 0; page < LIST_PAGE_CAP; page++) {
    const res = await env.RELAY_KV.list({ prefix, cursor });
    for (const k of res.keys) keys.push(k.name.slice(prefix.length)); // "{runId}:{seq}" or "{runId}:manifest"
    if (res.list_complete) break;
    cursor = res.cursor;
  }
  return jsonResponse({ ok: true, keys });
}

async function handleGetLetter(env, channelId, runId, seq) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(runId)) return badRequest('Invalid run id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const data = await env.RELAY_KV.get(`relay:${channelId}:mail:${runId}:${seq}`, 'arrayBuffer');
  if (!data) return new Response('Letter not found', { status: 404 });
  return new Response(data, { headers: { 'Content-Type': 'application/octet-stream' } });
}

async function handleGetRunManifest(env, channelId, runId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(runId)) return badRequest('Invalid run id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const manifest = await env.RELAY_KV.get(`relay:${channelId}:mail:${runId}:manifest`);
  if (!manifest) return new Response('Run manifest not found', { status: 404 });
  return new Response(manifest, { headers: { 'Content-Type': 'application/json' } });
}

// DELETE /mail/{ch}/{runId} — early storage reclamation for ABSORBED bulk runs (a full-fetch
// run holds real MBs for up to 90 days otherwise). Unabsorbed runs must never be deleted;
// the client enforces that (only calls this for runs in a committed generation's absorbedRuns).
async function handleDeleteRun(env, channelId, runId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(runId)) return badRequest('Invalid run id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const prefix = `relay:${channelId}:mail:${runId}:`;
  const res = await env.RELAY_KV.list({ prefix });
  await Promise.all(res.keys.map(k => env.RELAY_KV.delete(k.name)));
  return jsonResponse({ ok: true, deleted: res.keys.length });
}

async function handlePutGenChunk(request, env, store, channelId, gen, chunkNum) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(gen)) return badRequest('Invalid generation id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);

  const body = await request.arrayBuffer();
  if (body.byteLength > MAX_CHUNK_SIZE) return badRequest('Chunk too large');

  // TTL per store: canonical = none (lifecycle is keep-2 + GC — a rarely-rewritten library
  // must never expire, design H1); device-state = 90d, refreshed by every push.
  await env.RELAY_KV.put(`relay:${channelId}:${store.seg}:${gen}:chunk:${chunkNum}`, body,
    store.ttl ? { expirationTtl: store.ttl } : undefined);
  return jsonResponse({ ok: true, gen, chunk: chunkNum, bytes: body.byteLength });
}

// The generation manifest is the ATOMIC COMMIT: written last, single-key put.
async function handlePutGenManifest(request, env, store, channelId, gen) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(gen)) return badRequest('Invalid generation id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);

  const manifest = await request.text();
  try { JSON.parse(manifest); } catch { return badRequest('Manifest must be valid JSON'); }

  await env.RELAY_KV.put(`relay:${channelId}:${store.seg}:${gen}:manifest`, manifest,
    store.ttl ? { expirationTtl: store.ttl } : undefined);

  // Lifecycle telemetry: first successful commit per channel (mirrors legacy manifest upload)
  const usedKey = `lifecycle:${channelId}:used`;
  if (!await env.RELAY_KV.get(usedKey)) {
    await env.RELAY_KV.put(usedKey, new Date().toISOString());
    await fireGoatCounter(env, 'relay-channel-used');
  }

  return jsonResponse({ ok: true, gen });
}

async function handleGenList(env, store, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const prefix = `relay:${channelId}:${store.seg}:`;
  const manifested = new Set();
  const chunked = new Set();
  let cursor;
  for (let page = 0; page < LIST_PAGE_CAP; page++) {
    const res = await env.RELAY_KV.list({ prefix, cursor });
    for (const k of res.keys) {
      const rest = k.name.slice(prefix.length); // "{gen}:manifest" or "{gen}:chunk:{i}"
      if (rest.endsWith(':manifest')) {
        manifested.add(rest.slice(0, -':manifest'.length));
      } else {
        const m = rest.match(/^(.+):chunk:[0-9]+$/);
        if (m) chunked.add(m[1]);
      }
    }
    if (res.list_complete) break;
    cursor = res.cursor;
  }
  // v7.5.1 - Orphans: generations with chunks but NO manifest — a torn push (the tab died
  // between chunk upload and manifest write; flush-on-blur invites exactly this). Invisible
  // to readers by design, but until now also invisible to GC, so 17-20 MB chunks leaked
  // forever (the 2026-09-01 storage mystery: ~15 manifest-less chunks on prod alone).
  // The client reaps past-grace orphans via the ordinary DELETE endpoint.
  const gens = [...manifested];
  const orphans = [...chunked].filter(g => !manifested.has(g));
  return jsonResponse({ ok: true, gens, orphans });
}

async function handleGetGenChunk(env, store, channelId, gen, chunkNum) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(gen)) return badRequest('Invalid generation id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const chunk = await env.RELAY_KV.get(`relay:${channelId}:${store.seg}:${gen}:chunk:${chunkNum}`, 'arrayBuffer');
  if (!chunk) return new Response('Chunk not found', { status: 404 });
  return new Response(chunk, { headers: { 'Content-Type': 'application/octet-stream' } });
}

async function handleGetGenManifest(env, store, channelId, gen) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(gen)) return badRequest('Invalid generation id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const manifest = await env.RELAY_KV.get(`relay:${channelId}:${store.seg}:${gen}:manifest`);
  if (!manifest) return new Response('Generation manifest not found', { status: 404 });
  return new Response(manifest, { headers: { 'Content-Type': 'application/json' } });
}

// DELETE /gen/{ch}/{gen} — GC. The one server-side guard: never delete the generation the
// pointer currently names (a client bug must not be able to torch the live canonical).
// Keep-2 and the 1h grace age are client discipline.
async function handleDeleteGen(env, store, channelId, gen) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (!MINTED_ID_REGEX.test(gen)) return badRequest('Invalid generation id');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const pointerStr = await env.RELAY_KV.get(`relay:${channelId}:${store.ptr}`);
  if (pointerStr) {
    try {
      if (JSON.parse(pointerStr).gen === gen) {
        return jsonResponse({ error: 'Refusing to delete the currently-pointed generation' }, 409);
      }
    } catch { /* unparseable pointer — fall through, deletion allowed */ }
  }

  const manifestKey = `relay:${channelId}:${store.seg}:${gen}:manifest`;
  const manifestStr = await env.RELAY_KV.get(manifestKey);
  const deletes = [env.RELAY_KV.delete(manifestKey)];
  if (manifestStr) {
    let chunkCount = 1;
    try { chunkCount = JSON.parse(manifestStr).chunkCount || 1; } catch { /* best effort */ }
    for (let i = 0; i < chunkCount; i++) {
      deletes.push(env.RELAY_KV.delete(`relay:${channelId}:${store.seg}:${gen}:chunk:${i}`));
    }
  } else {
    // v7.5.1 - No manifest = torn/orphaned generation. The chunk count is unknowable without
    // a manifest, so enumerate the chunk keys by prefix and delete what actually exists
    // (the old chunkCount=1 guess left chunk:1+ of multi-chunk orphans behind forever).
    const prefix = `relay:${channelId}:${store.seg}:${gen}:chunk:`;
    let cursor;
    for (let page = 0; page < LIST_PAGE_CAP; page++) {
      const res = await env.RELAY_KV.list({ prefix, cursor });
      for (const k of res.keys) deletes.push(env.RELAY_KV.delete(k.name));
      if (res.list_complete) break;
      cursor = res.cursor;
    }
  }
  await Promise.all(deletes);
  return jsonResponse({ ok: true, gen, deleted: deletes.length });
}

// PUT /pointer/{ch} — the pointer flip. Single-key put = atomic; a race between two
// writers is benign (worst case: points at an older COMPLETE generation; self-heals).
async function handlePutPointer(request, env, store, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);
  if (!await checkRateLimit(env, channelId)) return jsonResponse({ error: 'Rate limit exceeded. Try again later.' }, 429);

  let gen;
  try { gen = (await request.json()).gen; } catch { return badRequest('Invalid JSON body'); }
  if (!gen || !MINTED_ID_REGEX.test(gen)) return badRequest('Invalid generation id');

  // Guard: only ever point at a generation whose manifest exists (commit-before-flip).
  const manifest = await env.RELAY_KV.get(`relay:${channelId}:${store.seg}:${gen}:manifest`);
  if (!manifest) return jsonResponse({ error: 'Generation not committed (no manifest)' }, 409);

  await env.RELAY_KV.put(`relay:${channelId}:${store.ptr}`, JSON.stringify({ gen, flippedAt: Date.now() }),
    store.ttl ? { expirationTtl: store.ttl } : undefined);
  return jsonResponse({ ok: true, gen });
}

async function handleGetPointer(env, store, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');
  if (await isBlocked(env, channelId)) return jsonResponse({ error: 'Channel revoked' }, 403);

  const pointer = await env.RELAY_KV.get(`relay:${channelId}:${store.ptr}`);
  if (!pointer) return new Response('No pointer', { status: 404 });
  return new Response(pointer, { headers: { 'Content-Type': 'application/json' } });
}

// --- Revocation & Blocklist ---

async function isBlocked(env, channelId) {
  const entry = await env.RELAY_KV.get(`blocklist:${channelId}`);
  return !!entry;
}

async function handleRevoke(request, env, channelId) {
  if (!validateChannelId(channelId)) return badRequest('Invalid channel ID');

  // Parse and validate proof
  let proof;
  try {
    const body = await request.json();
    proof = body.proof;
  } catch {
    return badRequest('Invalid JSON body');
  }
  if (!proof || typeof proof !== 'string' || !/^[0-9a-f]{64}$/i.test(proof)) {
    return badRequest('Invalid proof hash');
  }

  // Store revocation proof (permanent — allows future audit)
  await env.RELAY_KV.put(`relay:${channelId}:revocation-proof`, proof);

  // Delete all data for this channel (read manifest first for precise chunk count)
  const manifestStr = await env.RELAY_KV.get(`relay:${channelId}:manifest`);
  const deletes = [
    env.RELAY_KV.delete(`relay:${channelId}:manifest`),
    env.RELAY_KV.delete(`relay:${channelId}:device-state`)
  ];
  if (manifestStr) {
    try {
      const manifest = JSON.parse(manifestStr);
      for (let i = 0; i < (manifest.chunkCount || 1); i++) {
        deletes.push(env.RELAY_KV.delete(`relay:${channelId}:chunk:${i}`));
      }
    } catch {
      // If manifest isn't parseable, delete chunk:0 as best effort
      deletes.push(env.RELAY_KV.delete(`relay:${channelId}:chunk:0`));
    }
  }
  await Promise.all(deletes);

  // New-format keys (mailbox letters, generations, pointer) — enumerate by prefix and wipe.
  // Revocation's promise is "all data deleted"; it must cover the redesign layout too.
  for (const prefix of [`relay:${channelId}:mail:`, `relay:${channelId}:gen:`, `relay:${channelId}:dstate:`]) {
    let cursor;
    for (let page = 0; page < LIST_PAGE_CAP; page++) {
      const res = await env.RELAY_KV.list({ prefix, cursor });
      await Promise.all(res.keys.map(k => env.RELAY_KV.delete(k.name)));
      if (res.list_complete) break;
      cursor = res.cursor;
    }
  }
  await env.RELAY_KV.delete(`relay:${channelId}:pointer`);
  await env.RELAY_KV.delete(`relay:${channelId}:dstate-pointer`);

  // Add to blocklist
  await env.RELAY_KV.put(`blocklist:${channelId}`,
    JSON.stringify({ revokedAt: new Date().toISOString(), reason: 'user-revoked' }));

  // Lifecycle telemetry (user-initiated revocations are normal events, not security alerts)
  await fireGoatCounter(env, 'relay-channel-revoked');

  return jsonResponse({ ok: true, message: 'Channel revoked and data deleted' });
}

// --- Rate Limiting ---

async function checkRateLimit(env, channelId) {
  const key = `ratelimit:${channelId}`;
  const now = Date.now();

  const raw = await env.RELAY_KV.get(key);
  let data = raw ? JSON.parse(raw) : { count: 0, windowStart: now };

  // Reset window if expired
  if (now - data.windowStart > RATE_LIMIT_WINDOW_MS) {
    data = { count: 0, windowStart: now };
  }

  // v7.5.0 - SAMPLED counting: 1-in-SAMPLE requests bump the persisted count by SAMPLE
  // (expected value identical), dividing the counter's KV write cost by SAMPLE — it was
  // ~half of ALL KV writes (one per authenticated request). ENFORCEMENT runs on EVERY
  // request against the persisted approximate count; only the write-back is sampled.
  // The counter was always best-effort/approximate; this changes granularity, not semantics.
  const sampledThisRequest = Math.random() < 1 / RATE_LIMIT_SAMPLE;
  if (sampledThisRequest) data.count += RATE_LIMIT_SAMPLE;

  if (data.count > RATE_LIMIT_MAX_WRITES) {
    // Auto-blocklist on extreme abuse (10x normal limit)
    if (data.count >= RATE_LIMIT_AUTO_BLOCK) {
      await env.RELAY_KV.put(`blocklist:${channelId}`,
        JSON.stringify({ revokedAt: new Date().toISOString(), reason: 'rate-limit-auto' }));
      await sendAlert(env, 'Channel auto-blocked',
        `Channel ${channelId} exceeded ${RATE_LIMIT_AUTO_BLOCK} writes/hour and was auto-blocked.\nTime: ${new Date().toISOString()}`);
      await fireGoatCounter(env, 'relay-channel-blocked');
    }
    return false; // Rate limited
  }

  // Best-effort counter persist, only on sampled requests. (Still guarded: KV allows ~1
  // write/sec PER KEY; losing an increment must never fail the caller's actual write —
  // found by the Phase 1 harness when counter 429s were 500ing real writes.)
  if (sampledThisRequest) {
    try {
      await env.RELAY_KV.put(key, JSON.stringify(data), { expirationTtl: 7200 }); // 2hr TTL
    } catch { /* count update skipped — approximate counting is fine */ }
  }
  return true; // Allowed
}

// --- Telemetry ---

// Events are labeled prod-/dev- by the relay that fired them (7.22.0) — the same labels the app's trackEvent uses.
async function fireGoatCounter(env, eventName) {
    const prefix = RELAYS[env.RELAY_ENV] ? env.RELAY_ENV : 'unknown'; // never throws: telemetry must not fail a request
    try {
        await fetch(`https://readerwrangler.goatcounter.com/count?p=/event/${prefix}-${eventName}`, {
            method: 'GET',
            headers: { 'User-Agent': 'ReaderWrangler-Relay/1.0' }
        });
    } catch { /* best-effort — telemetry failure must not affect the request */ }
}

// --- Email Alerts ---

// Every email from a relay other than production starts its subject with that relay's label — "[Dev] …" (7.22.0).
async function sendAlert(env, subject, message) {
    if (!env.ALERT_TO_EMAIL || !env.RESEND_API_KEY) return;
    const tag = env.RELAY_ENV === 'prod' ? '' : `[${(RELAYS[env.RELAY_ENV] || { label: 'Unknown relay' }).label}] `;
    try {
        await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${env.RESEND_API_KEY}`
            },
            body: JSON.stringify({
                from: 'ReaderWrangler Relay <alerts@readerwrangler.com>',
                to: [env.ALERT_TO_EMAIL],
                subject: `${tag}🚨 ${subject}`,
                text: message.split(RED_START).join('').split(RED_END).join(''),
                // 7.22.0 - plus a preformatted HTML copy: mail programs reflow plain text (Outlook joined lines of the
                // summary); <pre> keeps every line break and the table's columns, in any client. red() lines show red.
                html: `<pre style="font-family:Consolas,Menlo,monospace;font-size:13px">${escapeHtml(message)
                    .split(RED_START).join('<span style="color:#c00;font-weight:bold">').split(RED_END).join('</span>')}</pre>`
            })
        });
    } catch { /* best-effort — don't let alert failure break the request */ }
}

// --- Usage Monitoring (Cron) ---

async function queryCloudflareGraphQL(env, query, variables) {
  const resp = await fetch('https://api.cloudflare.com/client/v4/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${env.CF_API_TOKEN}`
    },
    body: JSON.stringify({ query, variables })
  });
  if (!resp.ok) throw new Error(`GraphQL HTTP ${resp.status}`);
  const json = await resp.json();
  if (json.errors && json.errors.length) throw new Error(json.errors[0].message);
  return json.data;
}

// Usage for EVERY relay in RELAYS plus the account total (7.22.0, design §14a fix 2). The old version queried the
// account with no namespace filter and kept the first row — ONE relay's figure, never the sum (F4) — and printed a
// missing reading as 0 (F5). Now: one GraphQL request (aliased per relay — one subrequest), storage per namespace
// taken from the newest daily row (Cloudflare's documented shape), and a missing storage reading stays null.
// Counters stay 0 when Cloudflare returns no rows (it omits empty groups); storage, a level, is never shown as 0.
//   → { relays: { prod: {requests, kvReads, …, kvStorageMB, storageKeys, storageDate}, dev: {…} },
//       total: {requests, …, kvStorageMB}, storagePartial, otherWorkers: {name: requests}, otherActions: {type: n} }
async function fetchUsage(env) {
  const today = new Date().toISOString().slice(0, 10);
  const since = new Date(Date.now() - 2 * 86400000).toISOString().slice(0, 10);
  const relayKeys = Object.keys(RELAYS);
  const perRelay = relayKeys.map(k => `
          ${k}Ops: kvOperationsAdaptiveGroups(filter: { namespaceId: "${RELAYS[k].kvId}", date: $date }, limit: 20) {
            dimensions { actionType }
            sum { requests }
          }
          ${k}Storage: kvStorageAdaptiveGroups(filter: { namespaceId: "${RELAYS[k].kvId}", date_geq: $since, date_leq: $date },
                                               limit: 3, orderBy: [date_DESC]) {
            dimensions { date }
            max { byteCount keyCount }
          }`).join('');
  const data = await queryCloudflareGraphQL(env, `
    query ($accountTag: string!, $date: Date!, $since: Date!) {
      viewer {
        accounts(filter: { accountTag: $accountTag }) {
          workers: workersInvocationsAdaptive(filter: { date: $date }, limit: 100) {
            dimensions { scriptName }
            sum { requests }
          }${perRelay}
        }
      }
    }
  `, { accountTag: env.CF_ACCOUNT_ID, date: today, since });
  const acct = data.viewer.accounts[0] || {};

  const requestsByWorker = {};
  for (const row of acct.workers || []) {
    const name = row.dimensions.scriptName;
    requestsByWorker[name] = (requestsByWorker[name] || 0) + row.sum.requests;
  }

  const relays = {};
  const otherActions = {};
  for (const k of relayKeys) {
    const u = { requests: requestsByWorker[RELAYS[k].worker] || 0, kvReads: 0, kvWrites: 0, kvDeletes: 0, kvLists: 0 };
    for (const row of acct[`${k}Ops`] || []) {
      const field = KV_ACTION_FIELDS[row.dimensions.actionType];
      if (field) u[field] += row.sum.requests;
      else otherActions[`${k} ${row.dimensions.actionType}`] = row.sum.requests;
    }
    const newest = (acct[`${k}Storage`] || [])[0];
    u.kvStorageMB = newest ? Math.round(newest.max.byteCount / 1e5) / 10 : null;
    u.storageKeys = newest ? newest.max.keyCount : null;
    u.storageDate = newest ? newest.dimensions.date : null;
    relays[k] = u;
  }

  const otherWorkers = {};
  for (const [name, n] of Object.entries(requestsByWorker)) {
    if (!relayKeys.some(k => RELAYS[k].worker === name)) otherWorkers[name] = n;
  }

  const total = {};
  for (const metric of Object.keys(CF_LIMITS)) {
    const parts = relayKeys.map(k => relays[k][metric]).filter(v => v != null);
    total[metric] = parts.length ? Math.round(parts.reduce((a, b) => a + b, 0) * 10) / 10 : null;
  }
  // Requests are an account-wide limit: other workers on the account count against it too.
  total.requests += Object.values(otherWorkers).reduce((a, b) => a + b, 0);
  const storagePartial = relayKeys.some(k => relays[k].kvStorageMB == null);

  return { relays, total, storagePartial, otherWorkers, otherActions };
}

// Highest threshold band at-or-below pct (0 = below every threshold)
function bandOf(pct) {
  return THRESHOLDS.reduce((band, t) => (pct >= t ? t : band), 0);
}

const STORAGE_BAND_KEY = 'usage-alert:storage-band';
const STORAGE_BAND_HYSTERESIS = 5; // points below a boundary before the nightly re-baseline downgrades (flap guard)

// 2026-09-03 redesign: counters vs levels.
// COUNTERS (requests/reads/writes/deletes) reset each UTC day, so "you just crossed X%"
// is honest — but one check can discover several thresholds crossed at once (30-min
// cadence); alert ONLY the highest band, or a 10%→60% sprint emails a misleading
// 25%+50% pair implying a chronology nobody witnessed.
// STORAGE is a LEVEL: it doesn't reset at midnight, but the old per-day alert flags
// did — so every evening at 00:0x UTC (7 PM CDT) the first checks re-fired "reached
// 25%"+"reached 50%" while storage sat unchanged above 50%, implying a rise during
// what was actually a self-shrinking descent. Storage now alerts once per UPWARD band
// change, worded as a level, with the band remembered across days (no TTL). Downgrades
// happen only in the 23:55 UTC summary run — the partial-day analytics right after a
// UTC date roll UNDERSTATE storage (rows fill in lazily), so a 30-min-check downgrade
// would re-arm the nightly re-alert the moment the fuller reading arrived. A partial
// max can never overstate, so upward alerts stay safe at full cadence.
async function checkUsageThresholds(env) {
  if (!env.CF_API_TOKEN || !env.CF_ACCOUNT_ID) return;

  const usage = await fetchUsage(env);
  const todayStr = new Date().toISOString().slice(0, 10);
  const stateKey = `usage-alert:${todayStr}`;

  const raw = await env.RELAY_KV.get(stateKey);
  const alerted = raw ? JSON.parse(raw) : {};

  // 7.22.0 - every comparison is against the TOTAL across both relays (the free limits are account-wide).
  let alertsSent = false;
  for (const [key, { limit, label }] of Object.entries(CF_LIMITS)) {
    if (key === 'kvStorageMB') continue; // level metric — band logic below
    const current = usage.total[key];
    const band = bandOf((current / limit) * 100);
    if (band === 0) continue;

    if (!alerted[`${key}:${band}`]) {
      await sendAlert(env, `Usage threshold: ${label} at ${band}%`,
        `${label} has reached ${band}% of the daily free tier limit (production + dev combined).\n` +
        `Current: ${current.toLocaleString()} / ${limit.toLocaleString()}\n` +
        `Time: ${new Date().toISOString()}`
      );
      alertsSent = true;
    }
    // Mark the band AND everything below it (counters only rise within a day;
    // the skipped lower alerts would only add false chronology)
    for (const t of THRESHOLDS) { if (t <= band) alerted[`${key}:${t}`] = true; }
  }

  if (alertsSent) {
    await env.RELAY_KV.put(stateKey, JSON.stringify(alerted), { expirationTtl: 172800 }); // 2 day TTL
  }

  await checkStorageBand(env, usage);
}

async function checkStorageBand(env, usage) {
  const { limit, label } = CF_LIMITS.kvStorageMB;
  const current = usage.total.kvStorageMB;
  if (current == null) return; // no reading for either relay — nothing honest to alert on
  const pct = (current / limit) * 100;
  const band = bandOf(pct);

  const stored = parseInt(await env.RELAY_KV.get(STORAGE_BAND_KEY), 10) || 0;
  if (band > stored) {
    await sendAlert(env, `Usage alert: ${label} is ${pct.toFixed(1)}%`,
      `${label} is at ${current.toLocaleString()} MB of the ${limit.toLocaleString()} MB free tier cap (${pct.toFixed(1)}%, production + dev combined${usage.storagePartial ? ' — one relay had no reading, so at least this much' : ''}) — up into the ${band}% band.\n` +
      `Storage is a level, not a daily counter: no repeat alerts while it stays in this band. ` +
      `The daily summary tracks the exact figure (including drops).\n` +
      `Time: ${new Date().toISOString()}`
    );
    await env.RELAY_KV.put(STORAGE_BAND_KEY, String(band));
  }
}

// Nightly re-baseline (23:55 UTC, full-day reading): silently lower the remembered
// storage band so a genuine later re-climb alerts again. Hysteresis stops boundary flap.
async function rebaselineStorageBand(env, usage) {
  const { limit } = CF_LIMITS.kvStorageMB;
  // A partial total (one relay unread) could understate and wrongly downgrade — only a complete reading may lower it.
  if (usage.total.kvStorageMB == null || usage.storagePartial) return;
  const pct = (usage.total.kvStorageMB / limit) * 100;
  const band = bandOf(pct);
  const stored = parseInt(await env.RELAY_KV.get(STORAGE_BAND_KEY), 10) || 0;
  if (band < stored && pct < stored - STORAGE_BAND_HYSTERESIS) {
    await env.RELAY_KV.put(STORAGE_BAND_KEY, String(band));
  }
}

// 7.22.0 - BOTH relays send this (dev's subject says "[Dev]"); both report usage for ALL relays + the total, and each
// adds the storage check of its OWN namespace. Each section fails on its own: an error is printed, never a silent skip.
async function sendDailySummary(env) {
  const self = thisRelay(env);
  const today = new Date().toISOString().slice(0, 10);
  const sections = [
    `ReaderWrangler Relay - Daily Summary\nDate: ${today} (UTC) - sent by the ${self.label} relay (worker ${WORKER_VERSION})`
  ];

  let usage = null;
  if (env.CF_API_TOKEN && env.CF_ACCOUNT_ID) {
    try { usage = await fetchUsage(env); sections.push(formatUsage(usage)); }
    catch (err) { sections.push(`USAGE COULD NOT BE READ: ${err.message}`); }
  } else {
    sections.push('USAGE NOT AVAILABLE: this worker has no CF_API_TOKEN / CF_ACCOUNT_ID.');
  }

  // 7.23.0 - check, then (CLEANUP = "delete" in wrangler.toml) delete within the run's budget, then report — the email
  // goes out even if the check or a delete fails.
  try {
    const inv = await inspectStorage(env);
    const cleanup = env.CLEANUP === 'delete' ? await cleanStorage(env, inv) : null;
    sections.push(formatStorageCheck(self, inv, usage, cleanup));
  } catch (err) { sections.push(red(`STORAGE CHECK (${self.label}) FAILED: ${err.message}`)); }

  let mistriggers = null;
  try { mistriggers = await mistriggerSection(env, self); }
  catch (err) { mistriggers = red(`SCHEDULE CHECK FAILED: ${err.message}`); }
  if (mistriggers) sections.splice(1, 0, mistriggers); // right under the header — it's the thing to act on

  await sendAlert(env, `Daily usage summary - ${today}`, sections.join('\n\n'));
  if (mistriggers) await env.RELAY_KV.delete(MISTRIGGER_KEY); // reported → start a fresh tally

  // The remembered storage band is prod's threshold-alert state — only the relay that alerts maintains it.
  if (self.sendsThresholdAlerts && usage) await rebaselineStorageBand(env, usage); // full-day reading = the only trustworthy downgrade
}

// A schedule fired that isn't one of this relay's jobs. Tally it (by schedule text) for the next summary; at most
// MISTRIGGER_WRITE_CAP saves between summaries, so even a stuck every-minute schedule can't drain the write quota.
async function recordMistrigger(env, cron) {
  const tally = JSON.parse(await env.RELAY_KV.get(MISTRIGGER_KEY) || 'null') || { crons: {}, saves: 0 };
  if (tally.saves >= MISTRIGGER_WRITE_CAP) return;
  const now = new Date().toISOString();
  tally.crons[cron] = (tally.crons[cron] || 0) + 1;
  tally.saves++;
  tally.first = tally.first || now;
  tally.last = now;
  await env.RELAY_KV.put(MISTRIGGER_KEY, JSON.stringify(tally), { expirationTtl: 7 * 86400 });
}

// The summary's red section (or null): the mistrigger tally since the last summary. Caller clears it after mailing.
async function mistriggerSection(env, self) {
  const tally = JSON.parse(await env.RELAY_KV.get(MISTRIGGER_KEY) || 'null');
  if (!tally || !Object.keys(tally.crons).length) return null;
  const capped = tally.saves >= MISTRIGGER_WRITE_CAP;
  const jobs = [SUMMARY_CRON, ...(self.sendsThresholdAlerts ? [THRESHOLD_CRON] : [])].map(c => `"${c}"`).join(', ');
  return [
    `SCHEDULE PROBLEM - Cloudflare ran schedules that are not this relay's (its own: ${jobs}). They did nothing.`,
    ...Object.entries(tally.crons).map(([c, n]) => `  "${c}" fired ${n}${capped ? ' or more' : ''} time(s)`),
    `  first ${tally.first}, last counted ${tally.last} (UTC). Likely an old schedule Cloudflare still runs after a change`,
    `  (cloudflarestatus.com) - compare with the worker's Trigger events on the dashboard.`,
  ].map(red).join('\n');
}

// Marks a line to show in RED in the HTML copy of an email (the plain-text copy shows it unmarked). See sendAlert.
const RED_START = '\u0001', RED_END = '\u0002';
const red = line => `${RED_START}${line}${RED_END}`;

function fmtNum(n) {
  return n == null ? 'no data' : n.toLocaleString('en-US', { maximumFractionDigits: 1 });
}

function formatUsage(usage) {
  const relayKeys = Object.keys(RELAYS);
  const row = (label, cells) => label.padEnd(18) + cells.map(c => String(c).padStart(12)).join('');
  const lines = [
    'USAGE TODAY - both relays. The free limits are shared by the whole account, so Total is what counts.',
    row('', [...relayKeys.map(k => RELAYS[k].label), 'Total', 'Free limit', 'Used']),
  ];
  for (const [metric, { limit, label }] of Object.entries(CF_LIMITS)) {
    const total = usage.total[metric];
    const partial = metric === 'kvStorageMB' && usage.storagePartial && total != null;
    lines.push(row(label + (metric === 'kvStorageMB' ? ' (MB)' : ''), [
      ...relayKeys.map(k => fmtNum(usage.relays[k][metric])),
      fmtNum(total) + (partial ? '*' : ''),
      fmtNum(limit),
      total == null ? '-' : `${((total / limit) * 100).toFixed(1)}%`,
    ]));
  }
  if (usage.storagePartial) lines.push('* a relay had no storage reading, so the total is at least this much');
  lines.push('Storage readings: ' + relayKeys.map(k => {
    const u = usage.relays[k];
    return u.storageDate ? `${RELAYS[k].label} ${u.storageDate} (${fmtNum(u.storageKeys)} keys)` : `${RELAYS[k].label} none in 3 days`;
  }).join(', '));
  const others = Object.entries(usage.otherWorkers);
  if (others.length) lines.push('Other workers on the account (in the requests Total): ' + others.map(([n, c]) => `${n} ${fmtNum(c)}`).join(', '));
  const unknown = Object.entries(usage.otherActions);
  if (unknown.length) lines.push('UNRECOGNIZED KV action types (NOT counted above): ' + unknown.map(([n, c]) => `${n} ${fmtNum(c)}`).join(', '));
  return lines.join('\n');
}

// --- Daily storage check + cleanup (7.22.0 report-only; 7.23.0 deletes, design §14a fix 3) ---
// The rules are the app's own cleanup rules (relay-client.js commitGeneration + its device-state twin — KEEP_GENS /
// ORPHAN_GRACE_MS; git-hooks/check-shared-numbers.js refuses a commit where the two differ), so any hit means a save
// that was interrupted or never followed by another — not a judgment call:
//   - a committed generation beyond the newest 2 (no grace — the app deletes those at once too)
//   - a generation with no manifest (an interrupted save), over 10 minutes old
//   - a mailbox run of 2+ letters that the CURRENT library generation lists as absorbed, once that generation is over
//     10 minutes old (the saving device has had its chance to reclaim the run itself)
// NEVER: a mailbox run nothing has absorbed (it may be the only copy of a change), or the generation a pointer names.
// A store whose pointer is missing or unreadable is not judged at all.
// CLEANUP (wrangler.toml var) = "delete" deletes what it finds, within a per-run budget; anything else (or missing) only
// reports — the safe default. Deletion order lets a budget stop safely mid-item: a generation loses its MANIFEST first
// (readers stop seeing it at once; its remaining parts are then an interrupted save, finished next run), a mailbox run
// loses its letters first and its manifest LAST (so it stays recognizably absorbed until it's gone).
// Cost: one KV list per 1,000 keys + up to SWEEP_READ_BUDGET gets (only for channels with something to judge) + the
// deletes. Cloudflare's docs disagree on whether KV calls count toward a free-plan run's 50 subrequests (2026-02
// changelog: KV is in a separate 1,000) — until a test settles it, the whole run stays under SWEEP_CALL_CEILING.
const SWEEP_KEEP_GENS = 2;                    // mirrors relay-client.js KEEP_GENS
const SWEEP_ORPHAN_GRACE_MS = 10 * 60 * 1000; // mirrors relay-client.js ORPHAN_GRACE_MS (unfinished copies)
const SWEEP_ABSORBED_GRACE_MS = SWEEP_ORPHAN_GRACE_MS; // after a commit, before the worker judges its absorbed runs
const SWEEP_READ_BUDGET = 25;
const SWEEP_MAX_DELETES = 20;   // per run — a big backlog clears over several nights
const SWEEP_CALL_CEILING = 45;  // KV calls of the whole storage check + cleanup; leaves room for the email / statistics

function idTimestamp(mintedId) { // mirrors relay-client.js idTimestamp
  return parseInt(String(mintedId).split('-')[0], 10) || 0;
}
const dateOf = id => new Date(idTimestamp(id)).toISOString().slice(0, 10);
const shortId = id => `…${String(id).slice(-4)}`;

// Group every key name in the namespace by channel (keeping each generation's / run's actual key names, so a cleanup
// deletes exactly what was found) and count every KIND of key — the report names each with its expected count (7.23.0,
// Ron: "it needs to be clear if it is expected or not"). The layout is documented at the top of this file.
function groupKeys(names) {
  const channels = new Map(); // channelId → { runs: Map(runId → run), gen: Map(gen → g), dstate: Map(gen → g) }
  const kinds = { library: 0, deviceState: 0, mailbox: 0, pointers: 0, olderFormat: 0,
                  blocked: new Set(), proofs: new Set(), firstUsed: 0, rateLimit: 0, testAlert: 0, storageBand: 0,
                  alertsToday: 0, mistriggers: 0, unknown: [] };
  const channel = ch => {
    if (!channels.has(ch)) channels.set(ch, { runs: new Map(), gen: new Map(), dstate: new Map() });
    return channels.get(ch);
  };
  for (const name of names) {
    const p = name.split(':');
    const [head, ch, kind, id, part] = p;
    if (head === 'relay' && p.length >= 3) {
      if (kind === 'mail' && p.length === 5) {                                // relay:{ch}:mail:{runId}:{seq|manifest}
        kinds.mailbox++;
        const runs = channel(ch).runs;
        const run = runs.get(id) || { letters: 0, manifest: false, letterNames: [], manifestName: null };
        if (part === 'manifest') { run.manifest = true; run.manifestName = name; } else { run.letters++; run.letterNames.push(name); }
        runs.set(id, run);
      } else if ((kind === 'gen' || kind === 'dstate') && p.length >= 5) {   // relay:{ch}:{gen|dstate}:{gen}:{chunk:i|manifest}
        kinds[kind === 'gen' ? 'library' : 'deviceState']++;
        const gens = channel(ch)[kind];
        const g = gens.get(id) || { chunks: 0, manifest: false, chunkNames: [], manifestName: null };
        if (part === 'manifest') { g.manifest = true; g.manifestName = name; } else { g.chunks++; g.chunkNames.push(name); }
        gens.set(id, g);
      } else if (kind === 'pointer' || kind === 'dstate-pointer') {
        kinds.pointers++;
      } else if (kind === 'manifest' || kind === 'chunk' || kind === 'device-state') { // pre-7.0 single-copy layout (TTL'd)
        kinds.olderFormat++;
      } else if (kind === 'revocation-proof' && p.length === 3) {
        kinds.proofs.add(ch);
      } else {
        kinds.unknown.push(name);
      }
    } else if (head === 'blocklist' && p.length === 2) kinds.blocked.add(ch);
    else if (head === 'lifecycle' && p.length === 3 && kind === 'used') kinds.firstUsed++;
    else if (head === 'ratelimit' && p.length === 2) kinds.rateLimit++;
    else if (name === 'test-alert-counter') kinds.testAlert++;
    else if (name === 'usage-alert:storage-band') kinds.storageBand++;
    else if (head === 'usage-alert' && p.length === 2 && /^\d{4}-\d{2}-\d{2}$/.test(ch)) kinds.alertsToday++;
    else if (name === MISTRIGGER_KEY) kinds.mistriggers++;
    else kinds.unknown.push(name);
  }
  return { channels, kinds };
}

async function inspectStorage(env) {
  const names = [];
  let cursor, complete = false, listCalls = 0;
  for (let page = 0; page < LIST_PAGE_CAP; page++) {
    const res = await env.RELAY_KV.list({ cursor });
    listCalls++;
    for (const k of res.keys) names.push(k.name);
    if (res.list_complete) { complete = true; break; }
    cursor = res.cursor;
  }
  const { channels, kinds } = groupKeys(names);

  let reads = 0;
  const OUT_OF_BUDGET = 'out of read budget';
  const readJson = async key => { // null = missing, undefined = unreadable
    if (reads >= SWEEP_READ_BUDGET) throw new Error(OUT_OF_BUDGET);
    reads++;
    const raw = await env.RELAY_KV.get(key);
    if (raw == null) return null;
    try { return JSON.parse(raw); } catch { return undefined; }
  };

  const findings = [], notes = [], unchecked = [];
  for (const [ch, c] of channels) {
    try { await inspectChannel(ch, c, Date.now(), readJson, findings, notes); }
    catch (err) { if (err.message !== OUT_OF_BUDGET) throw err; unchecked.push(`${ch.slice(0, 8)}…`); }
  }
  // 7.23.0-alpha.2 - a block WITHOUT a revocation proof isn't necessarily an auto-block: dev holds two owner revocations
  // (2026-09-01) whose proofs are gone. Each block records its own reason — read it for the rare unpaired ones only.
  kinds.blockReasons = {};
  for (const ch of [...kinds.blocked].filter(c => !kinds.proofs.has(c))) {
    let reason;
    try { reason = (await readJson(`blocklist:${ch}`) || {}).reason || 'unreadable'; }
    catch (err) { if (err.message !== OUT_OF_BUDGET) throw err; reason = 'not read (read budget reached)'; }
    kinds.blockReasons[reason] = (kinds.blockReasons[reason] || 0) + 1;
  }
  return { keyCount: names.length, complete, kinds, channelCount: channels.size, findings, notes, unchecked, reads,
           calls: listCalls + reads };
}

// Each finding = { text, keys } — `keys` in the order a cleanup deletes them (see the header above).
async function inspectChannel(ch, c, now, readJson, findings, notes) {
  const who = `channel ${ch.slice(0, 8)}…`;
  const pastOrphanGrace = id => now - idTimestamp(id) >= SWEEP_ORPHAN_GRACE_MS;
  for (const [seg, store, what] of [['gen', GEN_STORES.canonical, 'library'], ['dstate', GEN_STORES.dstate, 'device-state']]) {
    const gens = c[seg];
    const committed = [...gens].filter(([, g]) => g.manifest).map(([id]) => id)
      .sort((a, b) => idTimestamp(b) - idTimestamp(a));
    const extra = committed.slice(SWEEP_KEEP_GENS);                     // no grace — the app deletes these at once too
    const torn = [...gens].filter(([, g]) => !g.manifest).map(([id]) => id).filter(pastOrphanGrace);
    const bulkRuns = seg === 'gen' ? [...c.runs].filter(([, r]) => r.letters >= 2) : [];
    if (!extra.length && !torn.length && !bulkRuns.length) continue; // nothing to judge — spend no reads

    const pointer = await readJson(`relay:${ch}:${store.ptr}`);
    if (!pointer || !pointer.gen) { notes.push(`${who}: ${what} pointer missing or unreadable - not judged`); continue; }
    for (const id of extra) {
      const g = gens.get(id);
      if (id !== pointer.gen) findings.push({ text: `${who}: extra ${what} generation ${shortId(id)} (${dateOf(id)}, ${g.chunks} part(s)) - beyond the newest ${SWEEP_KEEP_GENS}`,
                                              keys: [g.manifestName, ...g.chunkNames] });
    }
    for (const id of torn) {
      const g = gens.get(id);
      if (id !== pointer.gen) findings.push({ text: `${who}: interrupted ${what} save ${shortId(id)} (${dateOf(id)}, ${g.chunks} part(s), no manifest)`,
                                              keys: [...g.chunkNames] });
    }
    if (!bulkRuns.length) continue;

    const incomplete = bulkRuns.filter(([, r]) => !r.manifest).length;
    if (incomplete) notes.push(`${who}: ${incomplete} incomplete mailbox run(s) (never finished sending) - kept, they expire on their own`);
    const committedRuns = bulkRuns.filter(([, r]) => r.manifest);
    if (!committedRuns.length) continue;
    if (now - (pointer.flippedAt || idTimestamp(pointer.gen)) < SWEEP_ABSORBED_GRACE_MS) {
      notes.push(`${who}: library saved within the last 10 minutes - its mailbox runs are judged next time`);
      continue;
    }
    const manifest = await readJson(`relay:${ch}:gen:${pointer.gen}:manifest`);
    if (!manifest || !Array.isArray(manifest.absorbedRuns)) { notes.push(`${who}: current library manifest unreadable - mailbox not judged`); continue; }
    const absorbed = new Set(manifest.absorbedRuns);
    let waiting = 0;
    for (const [runId, r] of committedRuns) {
      if (absorbed.has(runId)) findings.push({ text: `${who}: absorbed mailbox run ${shortId(runId)} (${dateOf(runId)}, ${r.letters} letters) - already in the library`,
                                               keys: [...r.letterNames, r.manifestName] });
      else waiting++;
    }
    if (waiting) notes.push(`${who}: ${waiting} multi-part mailbox run(s) not yet imported - kept`);
  }
}

// Delete what inspectStorage found, in each finding's key order, within this run's budget (SWEEP_MAX_DELETES and the
// SWEEP_CALL_CEILING left after the check's own calls). Stops cleanly on any error; the rest waits for the next run.
// Sets finding.status: 'deleted' | 'partly' | 'left'; returns { deleted, budget, stoppedBy }.
async function cleanStorage(env, inv) {
  const budget = Math.max(0, Math.min(SWEEP_MAX_DELETES, SWEEP_CALL_CEILING - inv.calls));
  let left = budget, deleted = 0, stoppedBy = null;
  for (const f of inv.findings) {
    let done = 0;
    for (const key of f.keys) {
      if (stoppedBy || left === 0) break;
      try { await env.RELAY_KV.delete(key); } catch (err) { stoppedBy = err.message || String(err); break; }
      left--; deleted++; done++;
    }
    f.status = done === f.keys.length ? 'deleted' : done > 0 ? 'partly' : 'left';
  }
  return { deleted, budget, stoppedBy };
}

function formatStorageCheck(self, inv, usage, cleanup) {
  const lines = [cleanup
    ? `STORAGE CHECK + CLEANUP - ${self.label} relay's own storage`
    : `STORAGE CHECK - ${self.label} relay's own storage (REPORT ONLY: nothing was deleted)`];
  const cf = usage && usage.relays[self.key];
  let check = `Keys counted just now: ${inv.keyCount.toLocaleString('en-US')}${inv.complete ? '' : '+ (stopped at the listing cap)'}`;
  if (cf && cf.storageKeys != null) {
    // Cloudflare's keyCount is the day's HIGHEST count (max over the day), not a snapshot: keys that expired or were
    // deleted since (e.g. 2-hour rate-limit counters) leave the live count below it. Only live > highest is suspect.
    const diff = inv.keyCount - cf.storageKeys;
    check += `. Cloudflare's highest count for ${cf.storageDate}: ${cf.storageKeys.toLocaleString('en-US')} - ` + (diff > 0
      ? `LIVE IS ${diff} HIGHER, so Cloudflare's reading lags - the storage figure above may be out of date.`
      : diff === 0 ? 'the same, so the storage figure above is current.'
      : `${-diff} fewer now (keys expired or deleted since its high point) - consistent.`);
  } else {
    check += '. No Cloudflare reading to compare.';
  }
  lines.push(check);
  const k = inv.kinds;
  lines.push(`  library generations ${k.library}, device-state generations ${k.deviceState}, mailbox ${k.mailbox}, ` +
    `pointers ${k.pointers}, older format (expires on its own) ${k.olderFormat}`);
  lines.push(...otherKeyLines(self, k));

  const list = (title, fs) => fs.length ? [`${title} (${fs.length}):`, ...fs.map(f => `  - ${f.text}`)] : [];
  if (!inv.findings.length) {
    lines.push(`${cleanup ? 'Nothing to delete' : 'Would delete: nothing'} (${inv.channelCount} channel(s) checked).`);
  } else if (!cleanup) {
    lines.push(...list('Would delete', inv.findings));
  } else {
    const by = s => inv.findings.filter(f => f.status === s);
    lines.push(...list('Deleted', by('deleted')), ...list('Partly deleted - continues next run', by('partly')),
               ...list('Left for the next run', by('left')));
    // 7.23.0-alpha.3 - the limit counts storage KEYS, the list counts ITEMS (one saved copy can be several keys) — say so,
    // or "Deleted (4)" beside "7 … used" reads as 3 missing (Ron, 2026-10-20).
    const touched = by('deleted').length + by('partly').length;
    const limit = `the limit this run was ${cleanup.budget} key(s)` +
      (cleanup.budget < SWEEP_MAX_DELETES ? ` (usually ${SWEEP_MAX_DELETES}; the check itself used the rest)` : '');
    lines.push(touched
      ? `  (${cleanup.deleted} storage key(s) removed for ${touched === 1 ? 'this item' : `these ${touched} items`} - one saved copy can be several keys; ${limit})`
      : `  (no storage keys removed this run - ${limit})`);
    if (cleanup.stoppedBy) lines.push(red(`DELETING STOPPED EARLY: ${cleanup.stoppedBy} - the rest waits for the next run`));
  }
  if (inv.notes.length) lines.push('Kept / not judged:\n' + inv.notes.map(n => `  - ${n}`).join('\n'));
  if (inv.unchecked.length) lines.push(`NOT FULLY CHECKED (read budget of ${SWEEP_READ_BUDGET} reached): ${inv.unchecked.join(', ')}`);
  return lines.join('\n');
}

// Every kind of key that isn't a library / device-state / mailbox / pointer, each with whether its count is EXPECTED
// (Ron, 2026-10-18). Unexpected counts and unknown keys show in red. Channel ids never appear (they're credentials).
function otherKeyLines(self, k) {
  const alerts = self.sendsThresholdAlerts; // the storage-alert level + today's alert records live only on that relay
  const withProof = [...k.blocked].filter(ch => k.proofs.has(ch)).length;
  const reasons = { ...(k.blockReasons || {}) };          // unpaired blocks only, by the reason each one records
  const noProofRevoked = reasons['user-revoked'] || 0; delete reasons['user-revoked'];
  const autoBlocked = reasons['rate-limit-auto'] || 0;   delete reasons['rate-limit-auto'];
  const otherReasons = Object.entries(reasons).map(([r, n]) => `${n} "${r}"`).join(', ');
  const proofOnly = [...k.proofs].filter(ch => !k.blocked.has(ch)).length;
  const flag = (bad, line) => bad ? red(line) : line;
  const out = ['Other keys:',
    flag(autoBlocked > 0 || otherReasons !== '',
      `  Blocked channels: ${k.blocked.size} - revoked by their owner ${withProof + noProofRevoked}` +
      (noProofRevoked ? ` (${noProofRevoked} without a stored proof; their block records say owner-revoked)` : '') +
      `, auto-blocked for abuse ${autoBlocked}${otherReasons ? `, other: ${otherReasons}` : ''} - 0 auto-blocked is what is expected`),
    `  First-used records: ${k.firstUsed} - one per channel that has ever saved (they never expire)`,
    `  Test-alert counter: ${k.testAlert} - ${k.testAlert ? '1 is what is expected' : 'none sent from this relay yet (fine)'}`,
    flag(k.storageBand !== (alerts ? 1 : 0), `  Storage-alert level: ${k.storageBand} - ${alerts ? '1 is what is expected' : '0 is what is expected (only production sends storage alerts)'}`),
    flag(k.alertsToday > (alerts ? 2 : 0), `  Recent alert records: ${k.alertsToday} - ${alerts ? '0 to 2 is what is expected (they expire after 2 days)' : '0 is what is expected (only production sends alerts)'}`),
    `  Rate-limit counters: ${k.rateLimit} - they expire within 2 hours; a few after recent activity is expected`,
    flag(k.mistriggers > 1, `  Stray-schedule tally: ${k.mistriggers} - 0 or 1 is what is expected`)];
  if (proofOnly) out.push(red(`  Revocation proofs without a block: ${proofOnly} - 0 is what is expected`));
  if (k.unknown.length) {
    const shown = k.unknown.slice(0, 5).map(n => n.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '{channel}'));
    out.push(red(`  UNKNOWN keys: ${k.unknown.length} - none is what is expected: ${shown.join(', ')}${k.unknown.length > 5 ? ', …' : ''}`));
  }
  return out;
}

// --- Helpers ---

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function validateChannelId(id) {
  return UUID_REGEX.test(id);
}

function isAllowedOrigin(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim());
  return allowed.includes(origin);
}

function corsResponse(request, env, response) {
  const origin = request.headers.get('Origin');
  if (!origin) return response;

  const headers = new Headers(response.headers);
  if (isAllowedOrigin(origin, env)) {
    headers.set('Access-Control-Allow-Origin', origin);
  }
  headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  headers.set('Access-Control-Allow-Headers', 'Content-Type');
  headers.set('Access-Control-Max-Age', '86400');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' }
  });
}

function badRequest(message) {
  return jsonResponse({ error: message }, 400);
}
