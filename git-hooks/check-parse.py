#!/usr/bin/env python3
"""
check-parse.py — refuse a commit that stages a script which doesn't parse (2026-11-04; ported from the utilities
project's pre-commit `syntax_errors`, Hsv-Utilities-App Law 9).

WHY: the name check (check-names.js) parses only the scripts readerwrangler.html loads, plus mobile.js, and reads them
from disk, not as staged. So the fetchers and the bookmarklet menu (shipped code that runs on Amazon's pages), the
relay worker, reset.js, the .mjs tests and every Python file were never checked — a mangled edit (an escape gone wrong,
a stray null byte) could be committed in any of them.

WHAT: every STAGED .js, .mjs and .py file — the staged copy, not the working one — must parse. JavaScript goes through
git-hooks/parse-js.js (Babel: plain scripts, JSX and modules alike); Python through compile(). Nothing is run.
Tested by test/test_check_parse.py (one row per kind of file).

Exit: 0 all parse · 1 refused (each bad file named, with the error and where) · 2 setup problem — fails LOUD.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXTENSIONS = (".js", ".mjs", ".py")
SKIP_DIRS = ("v4/", "node_modules/")   # v4/: the archived old app (its own task removes it)


def staged_scripts():
    """[(path, bytes)] for every staged (added / copied / modified) script, as staged."""
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout or ""
    files = []
    for path in (ln.strip() for ln in out.splitlines()):
        if path.endswith(EXTENSIONS) and not path.startswith(SKIP_DIRS):
            src = subprocess.run(["git", "show", ":" + path], capture_output=True).stdout
            files.append((path, src))
    return files


def syntax_errors(files):
    """'path: the error (where)' for each (path, bytes) that doesn't parse. Raises SystemExit(2) on a setup problem."""
    bad = []
    js = [(p, s) for p, s in files if p.endswith((".js", ".mjs"))]
    for path, src in files:
        if path.endswith(".py"):
            try:
                compile(src, path, "exec")
            except (SyntaxError, ValueError) as e:   # ValueError: a null byte
                where = f" (line {e.lineno})" if getattr(e, "lineno", None) else ""
                bad.append(f"{path}: {e.__class__.__name__}: {getattr(e, 'msg', None) or e}{where}")
    if js:
        node = shutil.which("node")
        if not node:
            print("check-parse: SETUP - node isn't on the PATH, so JavaScript can't be checked.", file=sys.stderr)
            raise SystemExit(2)
        payload = json.dumps([{"path": p, "src": s.decode("utf-8", "replace")} for p, s in js])
        r = subprocess.run([node, os.path.join(HERE, "parse-js.js")], input=payload.encode("utf-8"),
                           capture_output=True)
        if r.returncode:
            sys.stderr.write(r.stderr.decode("utf-8", "replace"))
            raise SystemExit(2)
        bad += [f"{e['path']}: {e['error']}" for e in json.loads(r.stdout.decode("utf-8"))]
        bad += [f"{p}: contains a null byte" for p, s in js if b"\x00" in s and not any(b.startswith(p + ":") for b in bad)]
    return bad


def main():
    broken = syntax_errors(staged_scripts())
    if broken:
        print("\n[CHECK-PARSE] commit refused - staged code that doesn't parse:", file=sys.stderr)
        for b in broken:
            print("  x " + b, file=sys.stderr)
        print("\nFix it (an edit script's escapes are the usual cause) and commit again.\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
