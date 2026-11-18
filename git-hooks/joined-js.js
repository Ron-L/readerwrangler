#!/usr/bin/env node
// git-hooks/joined-js.js — the JavaScript half of check-joined.py. Two services, both through Babel's parser (the one
// inside the @babel/core the name and parse checks use, with JSX on as their preset-react turns it on — called straight:
// thousands of comment tails, each paying core's set-up, took seconds):
//   1. every comment in each given file — read by the parser, never by a pattern: a `//` inside a string, a template or
//      a regular expression is not a comment, and only a parser knows which is which;
//   2. for each given piece of text (a comment's tail), is it a complete line of CODE? — the shapes a test line takes:
//      a declaration (`const a = f(x);`), a call (`check(ok, 'msg');`, `await page.click(s);` — the name right against
//      its `(`), an assignment (`a.b = 1;`, `n++`), `return x`, `throw e`, an import, a one-line `if`/`for`/`while`
//      whose body is one of these, or a table row (`['ID-001', 'what', true],` — a list or object element holding a
//      piece of text, ending in its comma). A lone word, a label, a bare value or anything that doesn't parse is not.
//
// Reads JSON from stdin: { "files": [{ "path", "src" }, …], "snippets": ["…", …] }; prints JSON:
//   { "comments": [{ path, line, column, block, text }], "names": { path: [name, …] }, "unparsed": [{ path, error }],
//     "code": [true|false, …] }
// `line` 1-based, `column` 0-based (where the `//` or `/*` starts), `block` true for /* … */, `text` without the markers;
// `names` every name the file's code uses (keywords and identifiers — not words in its comments or strings);
// `code[i]` answers snippets[i].
// Exit: 0 ran · 2 setup problem — fails LOUD, never silently passes. Tested by test/test_check_joined.py.
'use strict';
const path = require('path');
const ROOT = path.resolve(__dirname, '..');
let babelParser;
try {
    const core = require.resolve('@babel/core', { paths: [ROOT] });
    require.resolve('@babel/preset-react', { paths: [ROOT] });
    babelParser = require(require.resolve('@babel/parser', { paths: [path.dirname(core)] }));
} catch (e) {
    console.error('joined-js: SETUP — @babel/core + @babel/preset-react are not installed in this repo.\n' +
        '  Fix:  npm i --no-save @babel/core @babel/preset-react   (then commit again)');
    process.exit(2);
}

// A file: script or module, as the parse check reads it (sourceType 'unambiguous').
const parseFile = (src) => babelParser.parse(src, { sourceType: 'unambiguous', plugins: ['jsx'], tokens: true });
// A comment's tail is a line lifted out of a function body: `await` and `return` must be allowed where it stands.
const parseLine = (src) => babelParser.parse(src, {
    sourceType: 'module', plugins: ['jsx'], allowReturnOutsideFunction: true, allowAwaitOutsideFunction: true,
});

// A call written as code writes its name right against the `(`, no space at its dots — prose puts spaces there: "the
// Inbox (2 books)", "its failure counted. done()" (which parses as `counted.done()`).
function tightCall(node, src) {
    return node.type === 'CallExpression' && src[node.callee.end] === '('
        && !/\s\.|\.\s/.test(src.slice(node.callee.start, node.callee.end));
}

function codeExpression(e, src) {
    switch (e.type) {
        case 'CallExpression': return tightCall(e, src);
        case 'AwaitExpression': return codeExpression(e.argument, src);
        case 'AssignmentExpression': case 'UpdateExpression': return true;
        case 'UnaryExpression': return e.operator === 'delete';
        case 'NewExpression': return tightCall({ type: 'CallExpression', callee: e.callee }, src);
        default: return false;
    }
}

function codeStatement(s, src) {
    switch (s.type) {
        case 'VariableDeclaration': case 'ImportDeclaration': case 'ExportNamedDeclaration':
        case 'ExportDefaultDeclaration': case 'FunctionDeclaration': case 'ClassDeclaration':
        case 'ThrowStatement':
            return true;
        case 'ReturnStatement': return !!s.argument;
        case 'ExpressionStatement': return codeExpression(s.expression, src);
        case 'IfStatement': return codeStatement(s.consequent, src) && (!s.alternate || codeStatement(s.alternate, src));
        case 'ForStatement': case 'ForOfStatement': case 'ForInStatement': case 'WhileStatement':
            return codeStatement(s.body, src);
        case 'BlockStatement': return s.body.length > 0 && s.body.every(b => codeStatement(b, src));
        default: return false;   // a label ("Note: …"), an empty statement, a bare value or name
    }
}

function holdsText(node) {   // a table row names its case in text: somewhere inside is a string or a template
    let found = false;
    (function walk(n) {
        if (found || !n || typeof n.type !== 'string') return;
        if (n.type === 'StringLiteral' || n.type === 'TemplateLiteral') { found = true; return; }
        for (const k of Object.keys(n)) {
            if (k === 'loc' || k === 'start' || k === 'end' || k === 'extra') continue;
            const v = n[k];
            if (Array.isArray(v)) v.forEach(walk); else if (v && typeof v === 'object') walk(v);
        }
    })(node);
    return found;
}

function program(src) {
    try { return parseLine(src).program.body; } catch (e) { return null; }
}

function isCode(snippet) {
    let body = program(snippet);
    if (body && body.length && body.every(s => codeStatement(s, snippet))) return true;
    // The first line of a block whose body follows below: `for (const k of KINDS)`, `while (more())`.
    body = !body && program(snippet + '\n{}');
    if (body && body.length === 1 && /^(For|ForOf|ForIn|While)Statement$/.test(body[0].type)) return true;
    // A table row ending in its comma: `['ID-001', 'what', true],`, `{ id: 'ID-001' },`, `row('ID-001', ok),` — a list,
    // object or call holding a piece of text — or an object's entry, `'folder': 'f-scifi', 'inbox': '__inbox__',`.
    if (!/,\s*$/.test(snippet.replace(/\/\/.*$/, ''))) return false;
    const wrapped = '[' + snippet + '\n]';
    body = program(wrapped);
    const arr = body && body.length === 1 && body[0].type === 'ExpressionStatement' && body[0].expression;
    if (arr && arr.type === 'ArrayExpression' && arr.elements.length > 0 && arr.elements.every(el => el && holdsText(el)
        && (el.type === 'ArrayExpression' || el.type === 'ObjectExpression' || tightCall(el, wrapped)))) return true;
    body = program('({' + snippet + '\n})');
    const obj = body && body.length === 1 && body[0].type === 'ExpressionStatement' && body[0].expression;
    return !!obj && obj.type === 'ObjectExpression' && obj.properties.length > 0 && holdsText(obj);
}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', d => { input += d; });
process.stdin.on('end', () => {
    const { files = [], snippets = [] } = JSON.parse(input);
    const out = { comments: [], names: {}, unparsed: [], code: snippets.map(isCode) };
    for (const { path: p, src } of files) {
        let ast;
        try {
            ast = parseFile(src);
        } catch (e) {
            out.unparsed.push({ path: p, error: String(e.message || e).split('\n')[0] });
            continue;
        }
        for (const c of ast.comments || []) {
            out.comments.push({
                path: p, line: c.loc.start.line, column: c.loc.start.column,
                block: c.type === 'CommentBlock', text: c.value,
            });
        }
        const names = new Set();
        for (const t of ast.tokens || []) {
            if (t.type && (t.type.label === 'name' || t.type.keyword) && typeof t.value === 'string') names.add(t.value);
        }
        out.names[p] = [...names];
    }
    process.stdout.write(JSON.stringify(out));
});
