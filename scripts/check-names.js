#!/usr/bin/env node
// scripts/check-names.js — refuse app code that references a NAME NOTHING DEFINES.
//
// WHY (7.18.0-alpha.55): an edit swallowed a line break and joined `const shareBtnRef = useRef(null)` onto the end
// of a `//` comment. The file still PARSED (the Babel syntax check passed), but opening the book details window
// threw "shareBtnRef is not defined". A syntax check can't see a missing name; a SCOPE check can. This is that check,
// run from the pre-commit hook so the class is blocked mechanically instead of by care.
//
// HOW: the app files (readerwrangler.js, mobile.js) run in a page whose globals come from (a) the browser, (b) the
// CDN libraries (React, ReactDOM, Babel), and (c) everything readerwrangler.html defines — its inline <script>
// blocks plus every LOCAL <script src="….js"> it loads. (c) is DERIVED by reading readerwrangler.html, so adding a
// new shared module needs no upkeep here. Any other unbound name in an app file is reported, with its line(s).
// Ignored on purpose: lowercase JSX tags (<div>), and `typeof X` (feature detection may name an absent global).
//
// Usage:  node scripts/check-names.js [file …]     (default: readerwrangler.js mobile.js)
// Exit:   0 clean · 1 unbound names found · 2 setup problem (fails LOUD, never silently passes).
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');

let babel, presetReact;
try {
    babel = require(require.resolve('@babel/core', { paths: [ROOT] }));
    presetReact = require.resolve('@babel/preset-react', { paths: [ROOT] });
} catch (e) {
    console.error('check-names: SETUP — @babel/core + @babel/preset-react are not installed in this repo.\n' +
        '  Fix:  npm i --no-save @babel/core @babel/preset-react   (then commit again)');
    process.exit(2);
}

// (a) browser + language globals, (b) CDN libraries the HTML loads before the app.
const BROWSER = new Set([
    'window', 'document', 'navigator', 'location', 'history', 'console', 'localStorage', 'sessionStorage', 'indexedDB',
    'fetch', 'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'requestAnimationFrame', 'cancelAnimationFrame',
    'alert', 'confirm', 'prompt', 'JSON', 'Math', 'Date', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Promise', 'Set',
    'Map', 'WeakMap', 'WeakSet', 'WeakRef', 'Symbol', 'Error', 'TypeError', 'RangeError', 'SyntaxError', 'RegExp', 'Intl',
    'URL', 'URLSearchParams', 'Blob', 'File', 'FileReader', 'FormData', 'TextEncoder', 'TextDecoder', 'crypto', 'btoa',
    'atob', 'encodeURIComponent', 'decodeURIComponent', 'encodeURI', 'decodeURI', 'parseInt', 'parseFloat', 'isNaN',
    'isFinite', 'Infinity', 'NaN', 'undefined', 'globalThis', 'performance', 'Node', 'Element', 'HTMLElement', 'Event',
    'KeyboardEvent', 'MouseEvent', 'CustomEvent', 'MutationObserver', 'ResizeObserver', 'IntersectionObserver',
    'getComputedStyle', 'matchMedia', 'Image', 'Audio', 'structuredClone', 'queueMicrotask', 'AbortController', 'Response',
    'Request', 'Headers', 'caches', 'screen', 'open', 'close', 'print', 'Uint8Array', 'Uint16Array', 'Int32Array',
    'ArrayBuffer', 'DataView', 'Proxy', 'Reflect', 'BigInt', 'arguments', 'self', 'CompressionStream',
    'DecompressionStream', 'DOMParser', 'XMLHttpRequest', 'WebSocket', 'BroadcastChannel', 'Notification', 'scrollTo',
    'innerWidth', 'innerHeight', 'devicePixelRatio', 'postMessage', 'addEventListener', 'removeEventListener',
    'getSelection', 'IDBKeyRange', 'ClipboardItem', 'module', 'require', 'exports',
    'React', 'ReactDOM', 'Babel',
]);

// A file/inline script that doesn't even PARSE is itself a finding (the browser rejects it too) — report it plainly
// instead of crashing with a stack trace. (First real catch, 2026-10-06: an inline script in readerwrangler.html had
// held a raw line break inside a string since 7.4.0, so the browser had silently never run it.)
const parse = (code, filename) => {
    try {
        return babel.parseSync(code, { filename, presets: [presetReact], sourceType: 'script', configFile: false, babelrc: false });
    } catch (e) {
        const where = e.loc ? ` (line ${e.loc.line}, column ${e.loc.column} of that script)` : '';
        console.error(`check-names: REFUSED — ${filename} does not parse${where}: ${String(e.message).split('\n')[0]}`);
        process.exit(1);
    }
};

// (c) names the page defines: top-level declarations + any `window.X = …` assignment.
function definedNames(code, filename, into) {
    const ast = parse(code, filename);
    for (const st of ast.program.body) {
        if (st.type === 'VariableDeclaration') {
            for (const d of st.declarations) Object.keys(babel.types.getBindingIdentifiers(d.id)).forEach(n => into.add(n));
        } else if ((st.type === 'FunctionDeclaration' || st.type === 'ClassDeclaration') && st.id) {
            into.add(st.id.name);
        }
    }
    babel.traverse(ast, {
        AssignmentExpression(p) {
            const l = p.node.left;
            if (l.type === 'MemberExpression' && l.object.type === 'Identifier' && l.object.name === 'window' && !l.computed && l.property.type === 'Identifier') into.add(l.property.name);
        },
    });
}

const htmlPath = path.join(ROOT, 'readerwrangler.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const pageNames = new Set();
const localSrcs = [...html.matchAll(/<script\b[^>]*\bsrc="([^"?#:]+\.js)/g)].map(m => m[1])
    .filter(s => !s.startsWith('//')); // protocol-relative = external (e.g. GoatCounter's //gc.zgo.at/count.js)
if (localSrcs.length === 0) { console.error('check-names: SETUP — found no local <script src> in readerwrangler.html (parser out of date?)'); process.exit(2); }
for (const src of localSrcs) {
    const p = path.join(ROOT, src);
    if (!fs.existsSync(p)) { console.error(`check-names: SETUP — readerwrangler.html loads ${src}, which does not exist`); process.exit(2); }
    definedNames(fs.readFileSync(p, 'utf8'), src, pageNames);
}
for (const m of html.matchAll(/<script\b(?![^>]*\bsrc=)([^>]*)>([\s\S]*?)<\/script>/g)) {
    const type = (m[1].match(/\btype="([^"]+)"/) || [])[1];
    if (type && !/javascript|module/.test(type)) continue; // e.g. application/ld+json
    definedNames(m[2], 'readerwrangler.html <inline script>', pageNames);
}

const targets = process.argv.slice(2).length ? process.argv.slice(2) : ['readerwrangler.js', 'mobile.js'];
let problems = 0;
for (const t of targets) {
    const file = path.join(ROOT, t);
    if (!fs.existsSync(file)) continue;
    const ast = parse(fs.readFileSync(file, 'utf8'), t);
    const hits = new Map();
    babel.traverse(ast, {
        ReferencedIdentifier(p) {
            const n = p.node.name;
            if (p.node.type === 'JSXIdentifier' && /^[a-z]/.test(n)) return;               // intrinsic tag (<div>)
            if (p.parentPath.isUnaryExpression({ operator: 'typeof' })) return;              // typeof X (feature detection)
            if (BROWSER.has(n) || pageNames.has(n) || p.scope.hasBinding(n, true)) return;
            if (!hits.has(n)) hits.set(n, []);
            hits.get(n).push(p.node.loc ? p.node.loc.start.line : '?');
        },
    });
    for (const [n, lines] of [...hits].sort()) {
        problems++;
        console.error(`check-names: ${t}: "${n}" is used but never defined — line(s) ${lines.slice(0, 8).join(', ')}${lines.length > 8 ? ' …' : ''}`);
    }
}
if (problems) {
    console.error(`\ncheck-names: REFUSED — ${problems} undefined name(s). A missing declaration, a typo, or code swallowed into a comment.\n` +
        '  (If a name is a genuine browser global missing from the list, add it to BROWSER in scripts/check-names.js.)');
    process.exit(1);
}
console.log(`check-names: OK — ${targets.join(', ')} reference no undefined names (${pageNames.size} page-level names from readerwrangler.html).`);
