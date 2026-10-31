/**
 * Signed-writes test (7.25.0 — docs/design/RELAY-SECURITY-PLAN.md, Phase 3).
 * Runs the REAL relay-client.js in Node (22+) against a relay and checks every rule of the design:
 * unregistered channels still accepted; registration; a good signature; a missing / wrong-key / stale / future
 * signature; a changed body, method or address; write-once parts; register twice; a PC clock 10 minutes off
 * (corrected by the retry); signed and unsigned revoke.
 *
 * Usage:  node relay/test-signed-writes.mjs                 (a LOCAL relay: cd relay && npx wrangler dev --env dev --local)
 *         RELAY_URL=https://readerwrangler-relay-dev.readerwrangler.workers.dev node relay/test-signed-writes.mjs
 * Refuses the production relay. Every channel is a fresh random one, revoked at the end.
 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const URL_ = process.env.RELAY_URL || 'http://127.0.0.1:8787';
if (/readerwrangler-relay\.readerwrangler/.test(URL_)) { console.error('Refusing the PRODUCTION relay.'); process.exit(2); }

const storage = new Map();
globalThis.localStorage = { getItem: k => storage.get(k) ?? null, setItem: (k, v) => storage.set(k, String(v)), removeItem: k => storage.delete(k) };
globalThis.window = globalThis;
window._RW_RELAY_WORKER_URL = URL_;
const uuid = () => crypto.randomUUID();
const pass32 = () => Array.from(crypto.getRandomValues(new Uint8Array(24))).map(b => 'ABCDEFGHJKMNPQRSTVWXYZabcdefghjkmnpqrstvwxyz0123456789'[b % 54]).join('').padEnd(32, 'x').slice(0, 32);
for (const f of ['relay-crypto.js', 'relay-compress.js', 'relay-client.js']) (0, eval)(readFileSync(join(root, f), 'utf8'));
const RW = window.RWRelay;
const use = (ch, pw) => { window._RW_RELAY_CHANNEL = ch; window._RW_RELAY_PASSPHRASE = pw; RW.initFromGlobals(); };

let pass = 0, fail = 0;
const ok = (desc, cond, extra = '') => { cond ? pass++ : fail++; console.log(`  ${cond ? 'PASS' : 'FAIL'} ${desc}${!cond && extra ? '  — ' + extra : ''}`); };
const raw = (path, opts) => fetch(`${URL_}${path}`, opts);

// An independent signer (NOT relay-client's code) — so the test checks the format, not the client against itself.
const enc = s => new TextEncoder().encode(s);
const hex = buf => Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
async function writeKey(pw, ch) {
  const base = await crypto.subtle.importKey('raw', enc(pw), 'PBKDF2', false, ['deriveBits']);
  return hex(await crypto.subtle.deriveBits({ name: 'PBKDF2', salt: enc('rw-write-key:' + ch), iterations: 100000, hash: 'SHA-256' }, base, 256));
}
async function sign(keyHex, method, path, t, contents) {
  const u = new URL(URL_ + path); const q = new URLSearchParams(u.search); q.delete('t'); q.delete('sig');
  const text = ['RW-SIG-1', method, u.pathname + (q.toString() ? '?' + q : ''), String(t), contents].join('\n');
  const key = await crypto.subtle.importKey('raw', new Uint8Array(keyHex.match(/../g).map(h => parseInt(h, 16))), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return hex(await crypto.subtle.sign('HMAC', key, enc(text)));
}
const sha = async s => hex(await crypto.subtle.digest('SHA-256', enc(s)));
async function signedRaw(keyHex, method, path, body, { t = Date.now(), contents, sendPath = path, sendMethod = method } = {}) {
  const c = contents ?? await sha(body ?? '');
  const sig = await sign(keyHex, method, path, t, c);
  const sep = sendPath.includes('?') ? '&' : '?';
  return raw(`${sendPath}${sep}t=${t}&sig=${sig}`, { method: sendMethod, body });
}
const payload = tag => JSON.stringify({ tag, books: { items: [{ asin: 'B' + tag, title: tag }] } });

async function main() {
  console.log('— Signed-writes test against', URL_, '\n');

  console.log('[1] An unregistered channel is accepted as before (old clients keep working)');
  const A = uuid(), pwA = pass32(), keyA = await writeKey(pwA, A);
  let r = await raw(`/gen/${A}/begin?device=test`, { method: 'POST' });
  ok('unsigned write on an unregistered channel → 200', r.status === 200, `HTTP ${r.status}`);

  console.log('\n[2] The app registers and signs; a good signature is accepted');
  use(A, pwA);
  const w = await RW.writeRun(payload('one'), 'wishlist-add');
  ok('writeRun (registers, then signs) succeeds', !!(w && w.runId));
  const reg = await raw(`/auth/${A}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key: keyA }) });
  ok('the relay holds THIS key (registering it again → "already")', reg.status === 200 && (await reg.json()).registered === 'already');
  const mb = await RW.readMailbox();
  ok('the signed run reads back intact', mb.runs.some(x => x.runId === w.runId && x.jsonString === payload('one')));

  console.log('\n[3] Refusals on a registered channel');
  r = await raw(`/gen/${A}/begin?device=test`, { method: 'POST' });
  ok('unsigned write → 401', r.status === 401, `HTTP ${r.status}`);
  const j = r.status === 401 ? await r.json() : {};
  ok('the refusal carries the relay\'s time', typeof j.serverTime === 'number');
  r = await signedRaw(await writeKey('wrong-passphrase', A), 'POST', `/gen/${A}/begin?device=test`);
  ok('signed with the wrong key → 401', r.status === 401, `HTTP ${r.status}`);
  r = await signedRaw(keyA, 'POST', `/gen/${A}/begin?device=test`, undefined, { t: Date.now() - 10 * 60000 });
  ok('a signature 10 minutes old → 401', r.status === 401, `HTTP ${r.status}`);
  r = await signedRaw(keyA, 'POST', `/gen/${A}/begin?device=test`, undefined, { t: Date.now() + 10 * 60000 });
  ok('a signature 10 minutes in the future → 401', r.status === 401, `HTTP ${r.status}`);
  r = await signedRaw(keyA, 'PUT', `/pointer/${A}`, JSON.stringify({ gen: 'x' }), { contents: await sha(JSON.stringify({ gen: 'y' })) });
  ok('a small message whose body was changed → 401', r.status === 401, `HTTP ${r.status}`);
  r = await signedRaw(keyA, 'DELETE', `/mail/${A}/aaaa`, undefined, { sendPath: `/mail/${A}/bbbb` });
  ok('a signature reused on another address → 401', r.status === 401, `HTTP ${r.status}`);
  r = await signedRaw(keyA, 'POST', `/gen/${A}/begin?device=test`, undefined, { sendMethod: 'DELETE', sendPath: `/gen/${A}/begin?device=test` });
  ok('a signature reused with another method → refused', r.status === 401 || r.status === 404, `HTTP ${r.status}`);
  r = await signedRaw(keyA, 'POST', `/gen/${A}/begin?device=test`);
  ok('a correct hand-made signature → 200 (the format matches the design)', r.status === 200, `HTTP ${r.status}`);

  console.log('\n[4] Write-once parts');
  const m = await RW.commitGeneration(payload('gen'), []);
  ok('commitGeneration (signed) succeeds', !!(m && m.gen));
  const part = new Uint8Array([1, 2, 3, 4]).buffer;
  r = await signedRaw(keyA, 'POST', `/gen/${A}/${m.gen}/chunk/0`, part, { contents: 'size:4' });
  ok('rewriting a part of a finished copy → 409', r.status === 409, `HTTP ${r.status}`);

  console.log('\n[5] Register twice');
  r = await raw(`/auth/${A}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key: await writeKey('other', A) }) });
  ok('a different key for a registered channel → 409', r.status === 409, `HTTP ${r.status}`);

  console.log('\n[6] A PC clock 10 minutes off is corrected by the retry');
  const realNow = Date.now;
  Date.now = () => realNow() - 10 * 60000;
  let clockOk = false;
  try { clockOk = !!(await RW.writeRun(payload('clock'), 'wishlist-add')).runId; } catch (e) { clockOk = false; }
  Date.now = realNow;
  ok('writeRun with the clock 10 minutes slow still succeeds', clockOk);

  console.log('\n[7a] A new copy without its checksum is never served — the reader falls back (7.25.0-alpha.2)');
  const B = uuid(), pwB = pass32(), keyB = await writeKey(pwB, B);
  use(B, pwB);
  const good = await RW.commitGeneration(payload('good'), []);
  // Clone the good copy's REAL encrypted part into a new copy, with or without the manifest's checksum, and point at it.
  async function cloneCopy(keepChecksum) {
    const gen = (await (await signedRaw(keyB, 'POST', `/gen/${B}/begin?device=test`)).json()).gen;
    const bytes = await (await raw(`/gen/${B}/${good.gen}/chunk/0`)).arrayBuffer();
    await signedRaw(keyB, 'POST', `/gen/${B}/${gen}/chunk/0`, bytes, { contents: `size:${bytes.byteLength}` });
    const man = await (await raw(`/gen/${B}/${good.gen}/manifest`)).json();
    man.gen = gen;
    if (!keepChecksum) delete man.checksum;
    await signedRaw(keyB, 'POST', `/gen/${B}/${gen}/manifest`, JSON.stringify(man));
    await signedRaw(keyB, 'PUT', `/pointer/${B}`, JSON.stringify({ gen }));
    return gen;
  }
  const control = await cloneCopy(true);
  let read = await RW.readCanonical();
  ok('control: a cloned copy WITH its checksum is served from the pointer', read.gen === control && read.source === 'pointer', `${read.source} ${read.gen}`);
  const stripped = await cloneCopy(false);
  read = await RW.readCanonical();
  ok('a cloned copy WITHOUT its checksum is refused; the reader falls back to a good copy',
     read.gen !== stripped && read.source === 'fallback', `${read.source} ${read.gen}`);
  await RW.revokeChannel();

  console.log('\n[7] Revoke');
  use(A, pwA);
  r = await raw(`/revoke/${A}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ proof: 'a'.repeat(64) }) });
  ok('an unsigned revoke of a registered channel → 401 (the lockout gap is closed)', r.status === 401, `HTTP ${r.status}`);
  await RW.revokeChannel();
  r = await raw(`/status/${A}`);
  ok('the app\'s signed revoke works (the channel now answers "revoked")', r.status === 403, `HTTP ${r.status}`);
  const D = uuid();
  r = await raw(`/revoke/${D}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ proof: 'b'.repeat(64) }) });
  ok('an unregistered channel can still be revoked the old way (the known weakness, until it registers)', r.status === 200, `HTTP ${r.status}`);

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
}
main().catch(e => { console.error('CRASHED:', e); process.exit(1); });
