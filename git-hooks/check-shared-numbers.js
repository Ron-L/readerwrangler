#!/usr/bin/env node
// check-shared-numbers.js — the app and the relay must agree on a few numbers and rules, but each program types its own
// copy (relay-client.js runs in the browser; relay/relay-worker.js on Cloudflare). If one changes and the other doesn't,
// things go quietly wrong — e.g. the worker's nightly cleanup would treat the app's normal copies as leftovers and
// delete them. This refuses a commit where any pair differs. (Decided Ron 2026-10-14, option (c); built 7.23.0.)
//
// Compares VALUES, not text (the units differ: the worker's TTL is seconds, the app's ms). Reads the STAGED copies.
// Run by git-hooks/pre-commit when either file is staged.  Usage: node git-hooks/check-shared-numbers.js [--worktree]
const { execSync } = require('child_process');
const fs = require('fs');

const CLIENT = 'relay-client.js', WORKER = 'relay/relay-worker.js';
const useWorktree = process.argv.includes('--worktree');
const read = f => useWorktree ? fs.readFileSync(f, 'utf8') : execSync(`git show :${f}`, { encoding: 'utf8' });

// The value of `const NAME = <expression>;` — only digits, spaces and * + - ( ) are allowed in the expression, or the
// name of another constant in the same file (e.g. SWEEP_ABSORBED_GRACE_MS = SWEEP_ORPHAN_GRACE_MS).
function constValue(text, name, file) {
  const m = text.match(new RegExp(`const\\s+${name}\\s*=\\s*([^;\\n]+);`));
  if (!m) throw new Error(`${file}: \`const ${name} = …;\` not found`);
  const expr = m[1].trim();
  if (/^[A-Z_][A-Z0-9_]*$/.test(expr)) return constValue(text, expr, file);
  if (!/^[\d\s*+\-()]+$/.test(expr)) throw new Error(`${file}: ${name} = ${expr} — not a plain number expression`);
  return Function(`"use strict"; return (${expr});`)();
}
const fnBody = (text, name, file) => {
  const m = text.match(new RegExp(`function\\s+${name}\\s*\\(([^)]*)\\)\\s*\\{([^}]*)\\}`));
  if (!m) throw new Error(`${file}: function ${name}(…) not found`);
  return (m[1] + '|' + m[2]).replace(/\/\/[^\n]*/g, '').replace(/\s+/g, '');
};

const errors = [];
try {
  const c = read(CLIENT), w = read(WORKER);
  const pairs = [
    ['how long an upload waits on the relay (90 days)', constValue(w, 'LETTER_TTL', WORKER) * 1000, constValue(c, 'LETTER_TTL_MS', CLIENT),
     `${WORKER} LETTER_TTL (seconds) × 1000 ↔ ${CLIENT} LETTER_TTL_MS`],
    ['how many finished copies to keep', constValue(w, 'SWEEP_KEEP_GENS', WORKER), constValue(c, 'KEEP_GENS', CLIENT),
     `${WORKER} SWEEP_KEEP_GENS ↔ ${CLIENT} KEEP_GENS`],
    ['the grace for an unfinished copy', constValue(w, 'SWEEP_ORPHAN_GRACE_MS', WORKER), constValue(c, 'ORPHAN_GRACE_MS', CLIENT),
     `${WORKER} SWEEP_ORPHAN_GRACE_MS ↔ ${CLIENT} ORPHAN_GRACE_MS`],
  ];
  for (const [what, a, b, where] of pairs) {
    if (a !== b) errors.push(`${what}: ${a} ≠ ${b}  (${where})`);
  }
  if (fnBody(w, 'idTimestamp', WORKER) !== fnBody(c, 'idTimestamp', CLIENT)) {
    errors.push(`reading the time out of an id: idTimestamp() differs between ${WORKER} and ${CLIENT}`);
  }
  // The ids the worker mints must START with the 13-digit time that idTimestamp reads.
  const re = (w.match(/const\s+MINTED_ID_REGEX\s*=\s*\/(.+)\/;/) || [])[1];
  if (!re) errors.push(`${WORKER}: MINTED_ID_REGEX not found`);
  else if (!re.startsWith('^\\d{13}-')) errors.push(`${WORKER}: MINTED_ID_REGEX (/${re}/) no longer starts with the 13-digit time idTimestamp reads`);
} catch (err) {
  errors.push(err.message);
}

if (errors.length) {
  console.error('\n[SHARED NUMBERS] commit blocked — the app and the relay disagree:');
  for (const e of errors) console.error('  x ' + e);
  console.error('\nFix: change BOTH files in this commit. Deliberate exception: git commit --no-verify.\n');
  process.exit(1);
}
console.log('check-shared-numbers: OK — relay-client.js and relay/relay-worker.js agree (90-day uploads, keep 2, unfinished-copy grace, id time).');
