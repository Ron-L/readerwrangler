#!/usr/bin/env python3
"""
check-joined.py — refuse a commit that stages a test file where a line of code has been joined onto the end of a
comment (2026-11-18, sprint 8; TODO "Turn more of our working rules into automatic checks", item 11.3).

WHY: an edit that swallows a line break joins the next line onto the comment above it. The file still parses, so
nothing notices: in app code the name check catches it when the lost line was a declaration (7.18.0-alpha.55 — alpha.52
joined `const shareBtnRef = useRef(null)` onto a `//` comment and the book details window crashed). In a TEST file
nothing did: a joined `check(...)`, `row(...)`, `test(...)`, `assert ...` or table row simply stops running, and the
file still passes — a test silently deleted.

WHAT: in every staged test file — Python (test/**/*.py) and JavaScript (test/**/*.js, *.mjs; relay/test-*.mjs), the
STAGED copy — each line comment (`#`, `//`) is read by the language's own reader (Python's tokenizer; Babel for
JavaScript, through git-hooks/joined-js.js), so a `#` or `//` inside a string is never taken for one. A comment is
refused when its words END in a complete line of code that starts at one of the places a lost line break leaves:
  1. after a run of two or more spaces (or a tab) that follows the comment's words — the joined line's own indent (the
     alpha.55 shape: "…for its <Popover>            const shareBtnRef = useRef(null);");
  2. after ONE space that follows a word, a sentence's end or a line of dashes (a separator: "# ------- check(…)",
     "# ── 4.1 Move ──── row(…)" — 2026-11-18, sprint 9) — an editor's "join lines" — unless the tail is a call with no
     arguments, which is how prose names a function ("its failure counted. done() prints the summary");
  3. right against the comment's last character, with no space — a line that had no indent: after its closing dot or
     bracket ("# the table." + "ROWS = []"; not after a dot that ends a real name of the file: "harness.done()"), or
     after an empty `#` / `//` ("#import os"), or INSIDE the last word ("# the rows" + "row(…)" = "# the rowsrow(…)")
     when it splits into a nonsense word plus a name of the file's code (a word that is itself a real name is a
     mention: "environment()"). Never inside an address ("https://…?b=c(d)").
"A complete line of code" is decided by parsing the tail, not by a pattern: a declaration or assignment, a call written
as code (its name right against its `(`, no space at its dots — prose writes "the Inbox (2 books)"), `assert`,
`return x`, `raise`/`throw`, `del`/`delete`, `await`, an import, a function or class, a one-line if/for/while/with
whose body is one of those, the first line of a block (`for r in ROWS:`, `with App() as app:`, `def f():`,
`for (const k of KINDS)`), a table row ending in its comma (a tuple / list / object / call holding a piece of text,
or a dictionary entry), or JavaScript's `'use strict';` with its semicolon (2026-11-18, sprint 9 — also glued after
anything but a space). A lone word, a bare value, a label ("Note: …") or anything that doesn't parse is prose.

Not caught, on purpose (each one would refuse ordinary prose): a no-argument call joined with one space or after a
sentence's dot ("…the end. done()" — but `done();` with its semicolon is caught); a comment that is code from its first
word after a space (commented-out code, a usage example — "#   const x = f();" — written as a comment on purpose, or
joined onto an empty `#` line with its indent: the two look the same); a line glued after a word that happens to be a
real name of the file ("…be refused.import os" when `refused` is a variable there); a table row whose line starts with
a bracket, glued with no space ("…phone)(\"PARSE-003\", …)"); 'use strict' without its semicolon (prose names it so);
a joined line that is only the start of a
statement spread over several lines (the rest is then stray code, and the parse check refuses the file); block
comments (/* … */ — a line joined into one is still a comment line, and one joined after its `*/` still runs).
Measured on the 2026-11-18 library (63 files, 1,712 line comments; no false refusal): every line comment joined with
the code line after it — 749 joins, 465 of which still parse — is caught in 459 of 465 keeping the indent, 454 with no
indent, 438 with one space.

ON PURPOSE: a comment that truly ends in code says so on its own line, or in the comment lines directly above it:
`# not-joined: <why>` / `// not-joined: <why>` (as `not-readSaved:` in check-saved-reads.py).

  python git-hooks/check-joined.py          the commit check (staged test files)
  python git-hooks/check-joined.py --all    every test file in the repo, as staged, with what was scanned and allowed

Tested by test/test_check_joined.py. Exit: 0 clean · 1 refused (each comment named: file, line, the code) · 2 setup
problem — fails LOUD.
"""
import ast
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tokenize
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
IN_SCOPE = re.compile(r"^(test/.+\.(py|js|mjs)|relay/test-[^/]+\.mjs)$")
MARKER = re.compile(r"not-joined:\s*(\S.{3,})")          # the marker, with at least a few words of why
GAP = re.compile(r"\S([ \t]{2,}|\t)(?=\S)")              # a run of spaces after the comment's words: a lost indent
HEAD = re.compile(r"^\s*([A-Za-z_$][\w$]*)")              # the name a line of code starts with
NAME = re.compile(r"[A-Za-z_$][\w$]*")
# An editor's "join lines" leaves ONE space: after a word or a sentence's end (not after `=`, `(` or `,` — inside code
# written in a comment), or after a line of dashes — a separator ("# ---------", "# ── 4.1 Move ─────"; 2026-11-18, sprint
# 9: missed until then); a call with no arguments is how prose names a function ("and done() prints the summary").
ONE_SPACE = re.compile(r"(?:[\w.:;!?)\]'\"`]|[-─━~*#]{3})( )(?=[^\s(])")
NO_ARGS = re.compile(r"[\w$.]+\(\)\s*$")          # (used with .match: from where it's asked, to the end)
# JavaScript's first line, joined onto the header comment above it (2026-11-18, sprint 9) — caught with its semicolon only:
# prose names it without one ("runs in 'use strict' mode").
USE_STRICT = re.compile(r"""['"]use strict['"]""")
# Every shape counted as code below holds one of these — a quick sieve, so only a few tails are parsed.
COULD_BE_CODE = re.compile(r"[(=]|\+\+|--|,\s*(#.*|//.*)?$|^['\"]use strict['\"]|^(import|from|return|throw|raise|"
                           r"assert|del|delete|await|def|class|function|async|const|let|var|export|for|while|if|with|"
                           r"global|nonlocal)\b")
WORD_CHAR = re.compile(r"[\w$]")
KEYWORDS = {"import", "from", "const", "let", "var", "def", "class", "for", "while", "if", "with", "return", "await",
            "assert", "del", "delete", "raise", "throw", "async", "function", "export"}


def in_scope(path):
    return bool(IN_SCOPE.match(path))


def staged_texts(paths):
    """[(path, text)] — each path as staged (the index), read in one `git cat-file --batch` (a `git show` each took
    seconds over the whole library)."""
    paths = list(paths)
    if not paths:
        return []
    listed = subprocess.run(["git", "ls-files", "-s", "-z", "--"] + paths, capture_output=True, text=True,
                            encoding="utf-8", errors="replace").stdout or ""
    blobs = {}
    for entry in filter(None, listed.split("\0")):
        meta, path = entry.split("\t", 1)
        blobs[path] = meta.split()[1]
    wanted = [p for p in paths if p in blobs]
    r = subprocess.run(["git", "cat-file", "--batch"], input="".join(blobs[p] + "\n" for p in wanted).encode(),
                       capture_output=True)
    out, data, at = [], r.stdout, 0
    for p in wanted:
        header_end = data.index(b"\n", at)
        size = int(data[at:header_end].split()[2])
        out.append((p, data[header_end + 1:header_end + 1 + size].decode("utf-8", "replace")))
        at = header_end + 1 + size + 1
    return out


# ── the comments of a file: [(line, column, own_line, text)] — text without its `#` / `//` ─────────────────────────


def python_read(src):
    """(comments, names) — names = every name the code uses (not words in its comments or strings). Raises
    tokenize.TokenError / SyntaxError when the file can't be read."""
    lines = src.splitlines()
    comments, names = [], set()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type == tokenize.COMMENT:
            ln, col = tok.start
            comments.append((ln, col, not lines[ln - 1][:col].strip(), tok.string[1:]))
        elif tok.type == tokenize.NAME:
            names.add(tok.string)
    return comments, names


def node_call(payload):
    node = shutil.which("node")
    if not node:
        print("check-joined: SETUP - node isn't on the PATH, so JavaScript can't be read.", file=sys.stderr)
        raise SystemExit(2)
    r = subprocess.run([node, os.path.join(HERE, "joined-js.js")], input=json.dumps(payload).encode("utf-8"),
                       capture_output=True)
    if r.returncode:
        sys.stderr.write(r.stderr.decode("utf-8", "replace"))
        raise SystemExit(2)
    return json.loads(r.stdout.decode("utf-8"))


# ── is this tail a complete line of Python code? (JavaScript's answer comes from joined-js.js) ──────────────────────


def _tight_call(call, src):
    """A call written as code: its name right against the `(`, no space at its dots — prose puts spaces there: "the
    Inbox (2 books)", "its failure counted. done()" (which parses as `counted.done()`)."""
    line = src.splitlines()[call.func.end_lineno - 1] if call.func.end_lineno else ""
    name = ast.get_source_segment(src, call.func) or " "
    return line[call.func.end_col_offset:call.func.end_col_offset + 1] == "(" and not re.search(r"\s\.|\.\s", name)


def _holds_text(node):
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in ast.walk(node))


def _py_expr(e, src):
    if isinstance(e, ast.Call):
        return _tight_call(e, src)
    if isinstance(e, ast.Await):
        return _py_expr(e.value, src)
    return False


def _py_stmt(s, src):
    if isinstance(s, (ast.Assign, ast.AugAssign, ast.Assert, ast.Raise, ast.Import, ast.ImportFrom, ast.Delete,
                      ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Global, ast.Nonlocal)):
        return True
    if isinstance(s, ast.AnnAssign):
        return s.value is not None
    if isinstance(s, ast.Return):
        return s.value is not None
    if isinstance(s, ast.Expr):
        return _py_expr(s.value, src)
    if isinstance(s, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith)):
        return all(_py_stmt(b, src) for b in s.body + getattr(s, "orelse", []))
    return False


def _parses(src, mode="exec"):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")   # prose read as code: "invalid escape sequence" and the like
        try:
            return ast.parse(src, mode=mode)
        except (SyntaxError, ValueError):
            return None


def python_is_code(tail):
    tree = _parses(tail)
    if tree and tree.body and all(_py_stmt(s, tail) for s in tree.body):
        return True
    # The first line of a block — `def f(x):`, `for row in ROWS:`, `with App() as app:` — its body follows below.
    if re.search(r":\s*(#.*)?$", tail):
        tree = _parses(tail + "\n    pass")
        s = tree.body[0] if tree and len(tree.body) == 1 else None
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.For, ast.AsyncFor)):
            return True
        if isinstance(s, (ast.If, ast.While, ast.With, ast.AsyncWith)):   # not "  with care:" — code tests code
            return any(isinstance(n, (ast.Call, ast.Attribute, ast.Compare, ast.Subscript)) for n in ast.walk(s))
    # A table row ending in its comma: `("ID-001", "what", True),`, `row("ID-001", ok),` — a tuple / list / dict / call
    # holding a piece of text — or a dictionary's entry, `"reset.html": {KEPT: 1},`.
    if not re.search(r",\s*(#.*)?$", tail):
        return False
    wrapped = "[" + tail + "\n]"
    tree = _parses(wrapped, "eval")
    if tree and tree.body.elts and all(_holds_text(r) and (isinstance(r, (ast.Tuple, ast.List, ast.Dict)) or (
            isinstance(r, ast.Call) and _tight_call(r, wrapped))) for r in tree.body.elts):
        return True
    tree = _parses("{" + tail + "\n}", "eval")
    return bool(tree and isinstance(tree.body, ast.Dict) and tree.body.keys and _holds_text(tree.body))


# ── where a joined line could start inside a comment ─────────────────────────────────────────────────────────────


def heads_of(src, lang):
    """The names this file's lines of code start with (`row`, `check`, `const`, `await`…) — where a line with no
    indent, joined right against a comment's last word, would begin."""
    marker = "#" if lang == "py" else "//"
    heads = set()
    for line in src.splitlines():
        s = line.lstrip()
        if s and not s.startswith((marker, "*", "/*")):
            m = HEAD.match(s)
            if m:
                heads.add(m.group(1))
    return heads


def tails(text, heads, names):
    """[(how, tail)] — every place in a comment's words where a joined line could start (the module's 1.-3.).
    heads: the names this file's lines start with; names: every name its code uses."""
    out = [("after a run of spaces", text[m.end():]) for m in GAP.finditer(text)]
    for m in ONE_SPACE.finditer(text):
        tail = text[m.end():]
        if not NO_ARGS.match(tail):
            out.append(("after one space", tail))
    known = heads | KEYWORDS | {n for n in names if len(n) >= 3}   # a 1-2 letter name hides inside any word
    # One pass for what each position needs to know of the text before it — where its run of non-spaces began, whether
    # that run holds "://", where its word began — so the scan below is linear (it searched text[:i] at every i: a long
    # comment cost its length squared; 2026-11-18, sprint 9).
    n = len(text)
    run_from, word_from, in_url = [0] * (n + 1), [0] * (n + 1), [False] * (n + 1)
    for i in range(1, n + 1):
        c = text[i - 1]
        run_from[i] = i if c.isspace() else run_from[i - 1]
        word_from[i] = word_from[i - 1] if WORD_CHAR.match(c) else i
        in_url[i] = not c.isspace() and (in_url[i - 1] or (i - 3 >= run_from[i] and text[i - 3:i] == "://"))
    for i in range(n):
        # A name glued to what's before it — to a comment's closing dot or bracket ("# …the rows." + "row(…)"), or to
        # the comment marker itself (an empty `#` / `//` line; commented-out code is written with a space after the
        # marker). Never after a space (prose: "and done() prints"), `_` or `$` (one longer name: "on_failure()").
        # After a word and a dot only when that word is no name of the file's code ("harness.done()" is a mention).
        # INSIDE a word — "# the rows" + "row(…)" = "rowsrow(…)" — only at a name or keyword of the file's code, and
        # only when the whole word is none: a word that names real code is a mention ("environment()").
        # And JavaScript's 'use strict'; glued after anything but a space ("// the header." + "'use strict';").
        before = text[i - 1] if i else ""
        if before.isspace() or before in ("_", "$"):
            continue
        if USE_STRICT.match(text, i):
            out.append(("right against the comment's last word", text[i:]))
            continue
        if not NAME.match(text, i):
            continue
        if in_url[i]:
            continue   # inside an address: "https://example.com/a?b=c(d)"
        name = NAME.match(text, i).group(0)
        if before.isalnum():
            if name not in known or text[word_from[i]:i] + name in names:
                continue
        elif before == ".":
            # "harness.done()" names real code; "page.reload()" — a dotted call with no arguments — is how prose names
            # one too, so a sentence's end glued to `done()` is let through (with its `;`, JavaScript's isn't).
            word = text[word_from[i - 1]:i - 1]
            if word and word in names or NO_ARGS.match(text, i):
                continue
        out.append(("right against the comment's last word", text[i:]))
    return out


# ── the check ────────────────────────────────────────────────────────────────────────────────────────────────────


def find_joined(files):
    """files: [(path, text)] → {"joined": [{path, line, how, code}], "allowed": [{path, line, why}],
    "unparsed": [{path, error}], "scanned": {"files": n, "comments": n}}."""
    found = {"joined": [], "allowed": [], "unparsed": [], "scanned": {"files": 0, "comments": 0}}
    comments = {}   # path → [(line, col, own_line, text)]
    names = {}      # path → every name its code uses
    js = [(p, s) for p, s in files if p.endswith((".js", ".mjs"))]
    for path, src in files:
        if path.endswith(".py"):
            try:
                comments[path], names[path] = python_read(src)
            except (tokenize.TokenError, SyntaxError) as e:
                found["unparsed"].append({"path": path, "error": f"{e.__class__.__name__}: {e}"})
    if js:
        res = node_call({"files": [{"path": p, "src": s} for p, s in js]})
        found["unparsed"] += res["unparsed"]
        names.update({p: set(n) for p, n in res["names"].items()})
        srcs = dict(js)
        for c in res["comments"]:
            if c["block"]:
                continue   # a block comment: nothing joined into or after one is lost (see the module's notes)
            lines = srcs[c["path"]].splitlines()
            own = not lines[c["line"] - 1][:c["column"]].strip()
            comments.setdefault(c["path"], []).append((c["line"], c["column"], own, c["text"]))
        unread = {u["path"] for u in res["unparsed"]}
        for p, _ in js:
            if p not in unread:
                comments.setdefault(p, [])   # read, and without a line comment

    # Every candidate tail, then one parse question per language.
    candidates = []   # (path, line, how, tail)
    for path, src in files:
        if path not in comments:
            continue
        found["scanned"]["files"] += 1
        found["scanned"]["comments"] += len(comments[path])
        heads = heads_of(src, "py" if path.endswith(".py") else "js")
        for line, _, _, text in comments[path]:
            for how, tail in tails(text.rstrip(), heads, names[path]):
                if COULD_BE_CODE.search(tail):
                    candidates.append((path, line, how, tail))
    js_tails = [c[3] for c in candidates if not c[0].endswith(".py")]
    js_answers = iter(node_call({"snippets": js_tails})["code"] if js_tails else [])
    hits = {}   # (path, line) → first (how, tail) that is code
    for path, line, how, tail in candidates:
        is_code = python_is_code(tail) if path.endswith(".py") else next(js_answers)
        if is_code and (path, line) not in hits:
            hits[(path, line)] = (how, tail)

    for (path, line), (how, tail) in sorted(hits.items()):
        why = marker_for(comments[path], line)
        if why:
            found["allowed"].append({"path": path, "line": line, "why": why})
        else:
            found["joined"].append({"path": path, "line": line, "how": how, "code": tail.strip()})
    return found


def marker_for(comments, line):
    """The `not-joined: <why>` on this comment, or on the comment lines directly above it — else None."""
    by_line = {ln: (own, text) for ln, _, own, text in comments}
    m = MARKER.search(by_line[line][1])
    if m:
        return m.group(1).strip()
    ln = line - 1
    while ln in by_line and by_line[ln][0]:
        m = MARKER.search(by_line[ln][1])
        if m:
            return m.group(1).strip()
        ln -= 1
    return None


def report(found):
    for u in found["unparsed"]:   # the parse check names these properly; don't pass a file this check couldn't read
        print(f"  x {u['path']}: couldn't be read ({u['error']})", file=sys.stderr)
    if found["joined"]:
        print("\n[CHECK-JOINED] commit refused - a line of code joined onto the end of a comment (it no longer runs):",
              file=sys.stderr)
        for j in found["joined"]:
            print(f"  x {j['path']}:{j['line']}  ({j['how']})  {j['code']}", file=sys.stderr)
        print("\nPut the code back on its own line (an edit that dropped a line break is the usual cause). If the comment"
              " truly ends in code, say so on its line or the line above: # not-joined: <why>  (// in JavaScript)\n",
              file=sys.stderr)
    return 1 if (found["joined"] or found["unparsed"]) else 0


def staged_test_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout or ""
    return staged_texts(p for p in (ln.strip() for ln in out.splitlines()) if in_scope(p))


def all_test_files():
    out = subprocess.run(["git", "ls-files", "test", "relay"], capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout or ""
    return staged_texts(p for p in (ln.strip() for ln in out.splitlines()) if in_scope(p))


def main(argv):
    for stream in (sys.stdout, sys.stderr):   # the code it quotes may hold any character (a Windows console is cp1252)
        stream.reconfigure(encoding="utf-8", errors="replace")
    if "--all" in argv:
        found = find_joined(all_test_files())
        s = found["scanned"]
        print(f"check-joined: {s['files']} test files, {s['comments']} line comments scanned.")
        print(f"Allowed ({len(found['allowed'])}), each with its why:")
        for a in found["allowed"]:
            print(f"  - {a['path']}:{a['line']}  {a['why']}")
        rc = report(found)
        if not rc:
            print("No joined lines.")
        return rc
    files = staged_test_files()
    return report(find_joined(files)) if files else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
