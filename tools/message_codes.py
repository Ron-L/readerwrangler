#!/usr/bin/env python3
"""
message_codes.py — ReaderWrangler's logging rules, checked from the code itself, and the support table generated from it
(docs/design/LOGGING.md §6; Ron + Claude, 2026-11-07).

    py tools/message_codes.py           check the rules and write docs/design/MESSAGE-CODES.md
    py tools/message_codes.py --check   check the rules and that the saved table is current (the commit hook) — exit 1
                                        with the reasons if not

7.28.0 (Ron, 2026-11-11): two layers. The general rules and the table are the logging kit's (logkit/check_messages.py —
it knows nothing of RW); this file is RW's layer on top. It knows what's ours — which scripts to scan (every shipped
script, as git lists it), the logger's name (rwLog), where our areas are listed (logkit-settings.js), where the table
lives and how it introduces itself — checks our own two rules, and calls the kit for the rest:
  the kit:  every rwLog.log(level, code, text…) call (and the kit's own calls) — level and code written as plain quoted
            words; one of the five levels; code AREA or AREA-NN with a known area; warning and above numbered; each
            numbered code at ONE call. The table: every numbered code — code, level, message, file — sorted by area.
  ours:     no direct showToast( — a toast goes through rwLog.log(…, { toast }) so it reaches the log with its area;
            every call of our five dialog routines names its area first (rwLog.dialog logs what the dialog showed).
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "git-hooks"))
import shipped_paths  # noqa: E402  (the one "is this shipped?" rule — the scripts scanned)
_spec = importlib.util.spec_from_file_location("check_messages", os.path.join(ROOT, "logkit", "check_messages.py"))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)

TABLE = "docs/design/MESSAGE-CODES.md"
SETTINGS = "logkit-settings.js"      # RW's settings for the logging kit — the areas live here
LOGGER = "rwLog"                     # what our code calls the logger (logkit-settings.js's globalName)
INTRO = ("_Written by `py tools/message_codes.py` from every `rwLog.log(…)` call in the code (docs/design/LOGGING.md §6). "
         "The commit check refuses a commit whose copy is out of date. Support: find the code a user reports; the level "
         "says how serious it is._")
# The dialog routines (readerwrangler.js) — each call names its area first (rwLog.dialog logs what the dialog showed).
DIALOG_CALL_RE = re.compile(r"\b(showInfoDialog|showConfirmDialog|showChoiceDialog|showInputDialog|showProgressDialog)\(")


def areas_from_logger(text):
    """The areas, read from LOG_AREAS in RW's settings for the logging kit (logkit-settings.js) — the one list (never
    a copy here)."""
    m = re.search(r"LOG_AREAS\s*=\s*Object\.freeze\(\{(.*?)\}\)", text, re.S)
    return set(re.findall(r"\b([A-Z]+)\s*:", m.group(1))) if m else set()


def find_calls(path, src):
    """[(path, line, level or None, code or None, text)] for every logging call in one file (the kit's reader)."""
    return kit.find_calls(path, src, logger=LOGGER)


def _toast_rule(files):
    """2026-11-09 (the toast pass): every toast goes through rwLog.log(…, { toast }) so it reaches the log with its area.
    Allowed: the one line that hands showToast to the logger (rwLog.setToaster), and comments."""
    problems = []
    for path, src in files:
        for m in re.finditer(r"\bshowToast\(", src):
            if kit.in_comment(src, m.start()):
                continue
            ls = src.rfind("\n", 0, m.start()) + 1
            le = src.find("\n", m.start())
            if "setToaster" in src[ls:le if le >= 0 else len(src)]:
                continue
            problems.append(f"{path}:{kit.line_of(src, m.start())}: a direct showToast( call — use "
                            "rwLog.log(level, code, text, null, { toast: true }) so the toast reaches the log with its area")
    return problems


def _dialog_rule(files, areas):
    """2026-11-09 (Ron, option 1): every dialog call names its area FIRST, as a plain quoted word — the dialog logs what
    it showed in that area (rwLog.dialog, which checks it again when the app runs). The routines' definitions aren't calls."""
    problems = []
    for path, src in files:
        for m in DIALOG_CALL_RE.finditer(src):
            if kit.in_comment(src, m.start()) or src[max(0, m.start() - 9):m.start()].endswith("function "):
                continue
            where = f"{path}:{kit.line_of(src, m.start())}"
            area, _ = kit.read_literal(src, kit.skip(src, m.end()))
            if area is None or not re.fullmatch(r"[A-Z]+", area):
                problems.append(f"{where}: {m.group(1)}'s first argument must be its area, as a plain quoted word "
                                f"(e.g. {m.group(1)}('BACKUP', title, …)) — the dialog logs what it showed there")
            elif area not in areas:
                problems.append(f"{where}: {m.group(1)} names an unknown area \"{area}\" — the areas are listed in {SETTINGS}")
    return problems


def check(files, areas):
    """files = [(path, source)] → (calls, problems): the kit's rules, then ours."""
    calls, problems = kit.check(files, areas, logger=LOGGER, areas_from=SETTINGS)
    return calls, problems + _toast_rule(files) + _dialog_rule(files, areas)


def table(calls):
    return kit.table(calls, intro=INTRO)


def _git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def app_scripts(staged):
    """Every SHIPPED script (git-hooks/shipped_paths.py — the root, logkit/, …; never the built dist/), as git lists it —
    as staged (the commit hook) or on disk. (7.28.0: was the root only; the logging module moved into logkit/.)"""
    listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.js"], cwd=ROOT,
                            capture_output=True, text=True).stdout.split()
    names = sorted(n for n in listed if shipped_paths.is_shipped_source(n) and os.path.exists(os.path.join(ROOT, n)))
    out = []
    for n in names:
        src = _git("show", ":" + n) if staged else None
        if src is None:
            with open(os.path.join(ROOT, n), encoding="utf-8", errors="replace") as f:
                src = f.read()
        out.append((n, src))
    return out


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    a = argparse.ArgumentParser(description="Check the logging rules and write the message-code table.")
    a.add_argument("--check", action="store_true", help="check only; fail if the saved table is out of date (commit hook)")
    args = a.parse_args(argv)
    files = app_scripts(staged=args.check)
    calls, problems = check(files, areas_from_logger(dict(files).get(SETTINGS, "")))
    wanted = table(calls)
    if problems:
        print("message codes: the logging rules are broken —")
        for p in problems:
            print("  " + p)
        return 1
    if args.check:
        saved = _git("show", ":" + TABLE)
        if saved is None and os.path.exists(os.path.join(ROOT, TABLE)):
            saved = open(os.path.join(ROOT, TABLE), encoding="utf-8").read()
        if (saved or "").replace("\r\n", "\n") != wanted:
            print(f"message codes: {TABLE} is out of date — run  py tools/message_codes.py  and stage it")
            return 1
        return 0
    with open(os.path.join(ROOT, TABLE), "w", encoding="utf-8", newline="\n") as f:
        f.write(wanted)
    rows = [ln for ln in wanted.splitlines() if ln.startswith("| ") and not ln.startswith("| Code")]
    print(f"wrote {TABLE}: {len(rows)} numbered codes")
    return 0


if __name__ == "__main__":
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    try:
        from pytools.keepopen import run
    except ImportError:
        sys.exit(main())
    run(main)
