#!/usr/bin/env python3
"""
version-guard.py — RW pre-commit chokepoint for version stamps. Called by git-hooks/pre-commit (run by git; saved in
the repo since 2026-10-15 — it used to live in the unsaved .claude/hooks/).

WHY: nothing enforced the "every runtime change gets a version bump" rule. The pre-build
gate (gate-check.py) is only an 11-point CHECKLIST — it never verifies the version actually
moved — so a bump could be silently forgotten (7.18.0-alpha.19 shipped without one; the
on-screen build marker lagged at alpha.18 until Ron caught it). This makes the bump STRUCTURAL:
a commit that touches shipped code but forgets its version stamp is refused.

RULE — for each STAGED code file, its version stamp must ALSO change in the same commit:

  readerwrangler.js   -> ORGANIZER_VERSION  (internal const, same file)
  mobile.js           -> MOBILE_VERSION      (internal const, same file)
  relay/relay-worker.js -> WORKER_VERSION    (internal const, same file — shown in the relay's emails)
  <module>.js         -> its  <module>.js?v=  cache-buster line in readerwrangler.html
  readerwrangler.css  -> its  readerwrangler.css?v=  cache-buster line in readerwrangler.html

<module>.js are the local scripts readerwrangler.html loads with a ?v= buster. readerwrangler.js
and mobile.js are the exceptions: their HTML buster is APP_VERSION (frozen during alpha testing),
so they carry an INTERNAL const that bumps every alpha instead.

Deliberate exception (Ron's call only, per CLAUDE.md): git commit --no-verify.
"""
import subprocess
import sys
import re

# Local module scripts loaded from readerwrangler.html with a ?v= cache-buster.
MODULES = ["uiHelpers", "bookFields", "bookMerge", "storage", "overlayRegistry",
           "integrity", "organizeEngine", "relay-crypto", "relay-compress", "relay-client"]
HTML = "readerwrangler.html"


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout or ""
    # git reports paths repo-relative with forward slashes; we match on basename anyway.
    return set(line.strip() for line in out.splitlines() if line.strip())


def added_lines(path):
    """The '+' side of the staged diff for `path` (new/changed lines only)."""
    out = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout or ""
    return [ln[1:] for ln in out.splitlines()
            if ln.startswith("+") and not ln.startswith("+++")]


def const_bumped(path, const_name):
    pat = re.compile(re.escape(const_name) + r"\s*=")
    return any(pat.search(ln) for ln in added_lines(path))


def html_buster_bumped(basename):
    """A '+' line in the staged HTML diff that sets  basename?v=..."""
    pat = re.compile(re.escape(basename) + r"\?v=")
    return any(pat.search(ln) for ln in added_lines(HTML))


def main():
    files = staged_files()
    # Match on basename so the guard is location-agnostic.
    names = set(f.split("/")[-1] for f in files)
    html_staged = HTML in names
    errors = []

    if "readerwrangler.js" in names and not const_bumped("readerwrangler.js", "ORGANIZER_VERSION"):
        errors.append("readerwrangler.js is staged but ORGANIZER_VERSION was not bumped.")

    if "mobile.js" in names and not const_bumped("mobile.js", "MOBILE_VERSION"):
        errors.append("mobile.js is staged but MOBILE_VERSION was not bumped.")

    # The relay worker carries its own stamp (7.22.0, Ron 2026-10-14) — printed in every summary email, so an email
    # shows which deploy sent it. Same X.Y.Z-alpha.N scheme as the app.
    if "relay-worker.js" in names and not const_bumped("relay/relay-worker.js", "WORKER_VERSION"):
        errors.append("relay/relay-worker.js is staged but WORKER_VERSION was not bumped.")

    for m in MODULES:
        fn = m + ".js"
        if fn in names and not (html_staged and html_buster_bumped(fn)):
            errors.append(f"{fn} is staged but its `{fn}?v=` cache-buster in {HTML} was not bumped.")

    if "readerwrangler.css" in names and not (html_staged and html_buster_bumped("readerwrangler.css")):
        errors.append(f"readerwrangler.css is staged but its `readerwrangler.css?v=` cache-buster in {HTML} was not bumped.")

    if errors:
        sys.stderr.write("\n[VERSION-GUARD] commit blocked - a runtime change needs its version stamp moved:\n")
        for e in errors:
            sys.stderr.write("  x " + e + "\n")
        sys.stderr.write("\nFix: bump the stamp in the SAME commit. Deliberate exception: git commit --no-verify.\n\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
