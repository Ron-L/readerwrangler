#!/usr/bin/env node
// git-hooks/parse-js.js — the JavaScript half of check-parse.py: does each given source parse?
//
// Reads JSON from stdin: [{ "path": "...", "src": "..." }, …]; prints JSON: [{ "path": "...", "error": "..." }, …] for
// the ones that DON'T parse (an empty list when all do). Uses the same Babel the name check uses, because RW's files
// are three kinds `node --check` can't all read: plain scripts (the fetchers), JSX (readerwrangler.js, mobile.js —
// compiled in the browser) and modules (the relay worker, the .mjs tests). `sourceType: 'unambiguous'` picks script or
// module per file.
// Exit: 0 ran (errors, if any, are in the output) · 2 setup problem — fails LOUD, never silently passes.
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
let babel, presetReact;
try {
    babel = require(require.resolve('@babel/core', { paths: [ROOT] }));
    presetReact = require.resolve('@babel/preset-react', { paths: [ROOT] });
} catch (e) {
    console.error('parse-js: SETUP — @babel/core + @babel/preset-react are not installed in this repo.\n' +
        '  Fix:  npm i --no-save @babel/core @babel/preset-react   (then commit again)');
    process.exit(2);
}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { input += d; });
process.stdin.on('end', () => {
    const files = JSON.parse(input);
    const bad = [];
    for (const { path: p, src } of files) {
        try {
            babel.parseSync(src, {
                filename: p, presets: [presetReact], sourceType: 'unambiguous', babelrc: false, configFile: false,
            });
        } catch (e) {
            const where = e.loc ? ` (line ${e.loc.line}, column ${e.loc.column + 1})` : '';
            const first = String(e.message || e).split('\n')[0].replace(/^.*?: /, '').replace(/\s*\(\d+:\d+\)\s*$/, '');
            bad.push({ path: p, error: first + where });
        }
    }
    process.stdout.write(JSON.stringify(bad));
});
