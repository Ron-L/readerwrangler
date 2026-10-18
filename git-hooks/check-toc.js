#!/usr/bin/env node
// git-hooks/check-toc.js — refuse a TODO.md whose table of contents doesn't match its headers.
//
// WHY (2026-10-14): TODO.md opens with a table of contents built by the VS Code extension "Auto Markdown TOC" — but the
// extension rebuilds it only when the file is SAVED IN VS CODE. Edits made any other way (Claude writes straight to
// disk) leave it stale, and a promise to keep it in sync by hand would drift. This check runs from the pre-commit hook,
// so a stale table can't be committed: re-save the file in VS Code (or fix the listed lines) and commit again.
//
// HOW: the table sits between the extension's hidden markers <!-- TOC --> and <!-- /TOC -->. Each entry's TEXT and
// nesting depth must equal the document's headers, in order. Link targets are NOT compared — the extension builds
// them, and copying its exact link rules (emoji, dashes, apostrophes) here would be a second implementation to drift.
// Lines inside ``` code fences are not headers.
//
// Usage:  node git-hooks/check-toc.js [file]          (default: TODO.md)
//         git show :TODO.md | node git-hooks/check-toc.js - TODO.md   (check the STAGED copy; the name is for messages)
// Exit:   0 in sync · 1 out of sync or no table · 2 setup problem (fails LOUD, never silently passes).
'use strict';
const fs = require('fs');

const [arg = 'TODO.md', label = arg] = process.argv.slice(2);
let text;
try {
    text = arg === '-' ? fs.readFileSync(0, 'utf8') : fs.readFileSync(arg, 'utf8');
} catch (e) {
    console.error(`check-toc: SETUP — cannot read ${label}: ${e.message}`);
    process.exit(2);
}
const lines = text.split(/\r?\n/);

const start = lines.findIndex(l => l.trim() === '<!-- TOC -->');
const end = lines.findIndex(l => l.trim() === '<!-- /TOC -->');
if (start < 0 || end < start) {
    console.error(`check-toc: ${label} has no table of contents (<!-- TOC --> … <!-- /TOC -->).\n` +
        '  Fix: open it in VS Code and run the extension\'s "Insert TOC" (Auto Markdown TOC), then commit again.');
    process.exit(1);
}

// Table entries: "  - [text](#link)" — depth from the indent (2 spaces per level).
const toc = [];
for (const l of lines.slice(start + 1, end)) {
    const m = l.match(/^(\s*)- \[(.*)\]\(#[^)]*\)\s*$/);
    if (m) toc.push({ depth: m[1].length / 2, text: m[2] });
}

// Headers outside the table and outside code fences — depth relative to the shallowest header.
const headers = [];
let inFence = false;
lines.forEach((l, i) => {
    if (i >= start && i <= end) return;
    if (/^\s*```/.test(l)) { inFence = !inFence; return; }
    const m = !inFence && l.match(/^(#{1,6})\s+(.*?)\s*#*\s*$/);
    if (m) headers.push({ level: m[1].length, text: m[2], line: i + 1 });
});
const minLevel = Math.min(...headers.map(h => h.level));
headers.forEach(h => { h.depth = h.level - minLevel; });

const problems = [];
const n = Math.max(toc.length, headers.length);
for (let i = 0; i < n && problems.length < 10; i++) {
    const t = toc[i], h = headers[i];
    if (!t) problems.push(`  header not in the table:  line ${h.line}: ${'#'.repeat(h.level)} ${h.text}`);
    else if (!h) problems.push(`  table entry with no header:  ${t.text}`);
    else if (t.text !== h.text || t.depth !== h.depth) {
        problems.push(`  entry ${i + 1}: table says "${t.text}" (level ${t.depth + 1}), ` +
            `header at line ${h.line} is "${h.text}" (level ${h.depth + 1})`);
    }
}
if (problems.length) {
    console.error(`check-toc: ${label}'s table of contents is OUT OF SYNC with its headers ` +
        `(table ${toc.length} entries, ${headers.length} headers):\n${problems.join('\n')}\n` +
        '  Fix: open the file in VS Code and SAVE it (the extension rebuilds the table), then commit again.');
    process.exit(1);
}
console.log(`check-toc: ${label} — table of contents matches all ${headers.length} headers.`);
