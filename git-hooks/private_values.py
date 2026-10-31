#!/usr/bin/env python3
"""
private_values.py - the one check behind RW's private-value hooks (pre-commit, commit-msg) and the one-time history
scan. It refuses two kinds of thing, naming WHERE without ever printing a value:

  1. The values in the private secrets note (Resend key, test-alert key, Cloudflare token, …). They are read from the
     note at run time and never written anywhere. A value = a run of 16+ letters/digits/_/- holding both a letter and a
     digit; a line marked "(not really a secret)" is skipped (the Cloudflare account id is public in wrangler.toml by
     design - docs/design/CLOUD-SYNC-NAMING.md and the utilities project's review, 2026-10-31).
  2. Cloud Sync credentials by their SHAPE - no list can know them, every backup carries them:
     - a .json whose "relay" holds a channelId and a passphrase (a backup, or a demo file made from one);
     - a bookmarklet pasted as text: _RW_RELAY_PASSPHRASE='<a value>';
     - the app's Copy text: "Passphrase: <32 letters/digits>".
     Earned 2026-10-31: readerwrangler-demo-library-ORGANIZED.json carried a credential pair publicly from 692ee9e
     (2026-07-03) until 214e14e; the channel was revoked on both relays the same day.

Standard library only. Without the private notes (a contributor's clone) only the shape checks run.
  python git-hooks/private_values.py --list           what the values check will refuse (line + length, masked)
  python git-hooks/private_values.py --scan-history   the one-time scan of every commit (reports commit + path only)
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTE = os.environ.get("RW_SECRETS_NOTE") or os.path.join(ROOT, ".private", "Secrets.txt")   # override: tests only
VALUE = re.compile(r"[A-Za-z0-9_\-]{16,}")
# A real passphrase is what the app generates: exactly 32 letters/digits (Relay Setup). Placeholders pass - the docs'
# '<passphrase>', the relay test harness's 'phase1-harness-passphrase' (the scan's first run, 2026-10-31). When the
# Cloud Sync Key ships (docs/design/CLOUD-SYNC-NAMING.md: RW1- + Crockford base32), add its shape here too.
BOOKMARKLET = re.compile(r"_RW_RELAY_PASSPHRASE\s*=\s*['\"][A-Za-z0-9]{32}['\"]")
COPY_TEXT = re.compile(r"Passphrase:\s*[A-Za-z0-9]{32}\b")


def note_values():
    """[(note line, value)] - the private values; [] when the note isn't here."""
    try:
        lines = open(NOTE, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return []
    found = []
    for n, ln in enumerate(lines, 1):
        if "not really a secret" in ln.lower():
            continue
        for v in VALUE.findall(ln):
            if re.search(r"[A-Za-z]", v) and re.search(r"\d", v):
                found.append((n, v))
    return found


def holds_credentials(obj) -> bool:
    """A parsed .json with a non-empty channelId + passphrase in any "relay" object, at any depth."""
    if isinstance(obj, dict):
        r = obj.get("relay")
        if isinstance(r, dict) and r.get("channelId") and r.get("passphrase"):
            return True
        return any(holds_credentials(v) for v in obj.values())
    if isinstance(obj, list):
        return any(holds_credentials(v) for v in obj)
    return False


def line_problems(text, values):
    """What's wrong with one line of text: [] or a list of reasons (never the value)."""
    why = []
    if any(v in text for v in values):
        why.append("a value from the private secrets note")
    if BOOKMARKLET.search(text):
        why.append("a bookmarklet with its Cloud Sync credentials")
    if COPY_TEXT.search(text):
        why.append("a Cloud Sync passphrase (the Copy text)")
    return why


def json_problem(path, data: bytes):
    """A reason, or None, for one .json file's contents."""
    if not path.lower().endswith(".json"):
        return None
    try:
        obj = json.loads(data.decode("utf-8", "replace"))
    except ValueError:
        return None
    return "a backup-shaped .json holding Cloud Sync credentials (relay.channelId + relay.passphrase)" \
        if holds_credentials(obj) else None


def report(hook, what, hits):
    """Print the refusal (places + reasons, never values). Returns the exit code."""
    if not hits:
        return 0
    print(f"{hook}: COMMIT REFUSED - {what} hold private values:", file=sys.stderr)
    for place, why in hits:
        print(f"  {place}: {why}", file=sys.stderr)
    print("Take them out (credentials live only in your browser and your backups; keys only in the private notes) "
          "and commit again. A backup file belongs outside the repo - git ignores readerwrangler-backup-*.json.",
          file=sys.stderr)
    return 1


def check_lines(hook, what, lines):
    """lines = (place, text) pairs. Exit code 1 if any line holds a private value."""
    values = [v for _, v in note_values()]
    hits = [(place, "; ".join(w)) for place, text in lines for w in [line_problems(text, values)] if w]
    return report(hook, what, hits)


def git(*args, binary=False):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def list_values():
    vals = note_values()
    if not vals:
        print("No private secrets note found (or no values in it) - only the shape checks will run.")
        return 0
    print(f"The values check will refuse {len(vals)} value(s) from the private secrets note:")
    for n, v in vals:
        print(f"  note line {n}: a value of {len(v)} characters")
    return 0


def scan_history():
    """Every commit on every branch: added lines holding a note value / a credential shape, and every .json version
    holding credentials. Reports commit + path (+ line), never a value."""
    values = [v for _, v in note_values()]
    hits = set()
    log = git("log", "--all", "-p", "--no-color", "--text", "-U0", "--format=@@COMMIT %h")
    commit = path = None
    for ln in log.splitlines():
        if ln.startswith("@@COMMIT "):
            commit = ln.split()[1]
        elif ln.startswith("+++ "):
            path = ln[6:] if ln.startswith("+++ b/") else ln[4:]
        elif ln.startswith("+") and not ln.startswith("+++"):
            for why in line_problems(ln[1:], values):
                hits.add((commit, path, why))
    for line in git("rev-list", "--all", "--objects").splitlines():
        sha, _, p = line.partition(" ")
        if p.lower().endswith(".json"):
            why = json_problem(p, git("cat-file", "-p", sha, binary=True))
            if why:
                first = git("log", "--all", "--format=%h %ad", "--date=short", "--find-object=" + sha).split("\n")[-2:]
                hits.add((first[-1].strip() or first[0].strip() or "?", p, why))
    if not hits:
        print("History scan: nothing found.")
        return 0
    print(f"History scan: {len(hits)} finding(s) (commit, path, what - values never printed):")
    for c, p, w in sorted(hits, key=lambda h: (h[1] or "", h[0] or "")):
        print(f"  {c}  {p}: {w}")
    return 1


if __name__ == "__main__":
    if "--list" in sys.argv:
        sys.exit(list_values())
    if "--scan-history" in sys.argv:
        sys.exit(scan_history())
    print(__doc__)
