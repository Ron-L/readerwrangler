#!/usr/bin/env python3
"""
PreToolUse gate (trial). Fires on Edit/Write to APP SOURCE only.
On the FIRST app-source edit of a turn, denies once with the pre-build checklist,
then clears the per-turn flag so the immediate re-issue of the same edit proceeds.

The checklist is NOT stored here. It is the SINGLE SOURCE in docs/PRINCIPLES.md, between the
<!-- GATE-CHECKLIST-START --> / <!-- GATE-CHECKLIST-END --> markers; this hook is just a printer that
pulls that block. If it cannot be read, the hook prints a LOUD failure (never a silent degrade) so a
broken reference announces itself. (Ron, 2026-09-30: no duplication to drift; and make the failure active.)

Design: the flag is created by gate-reset.py on Stop/SessionStart; this hook consumes it, so the
checklist lands exactly once, at the planning->build boundary.

Fail-safe: ANY error or unexpected input -> allow (exit 0). A gate bug must never block real work.
"""
import sys, os, json, tempfile

# App source = SHIPPED code: every .js directly in the repo root (the app, its modules, the bookmarklet
# fetchers, reset.js) plus the deployed relay worker. A RULE, not a list, so a new module is covered the day
# it's created. (2026-10-08, 7.18.0 PM: the old list {"readerwrangler.js","mobile.js"} let an unapproved
# post-compaction edit to overlayRegistry.js skip the gate.) Docs/TODO/memory/CHANGELOG/HTML/config/tests/
# scripts deliberately do NOT trip the gate.
EXTRA_APP_SOURCE = {"relay/relay-worker.js"}


def is_app_source(file_path):
    rel = os.path.relpath(os.path.abspath(file_path), repo_root()).replace("\\", "/")
    if rel.startswith("../"):
        return False                                  # outside this repo
    return (rel.endswith(".js") and "/" not in rel) or rel in EXTRA_APP_SOURCE

# Match the FULL comment markers (not the bare tokens) so a prose mention of the marker names
# elsewhere in PRINCIPLES.md can't be mistaken for the real delimiters.
START = "<!-- GATE-CHECKLIST-START -->"
END = "<!-- GATE-CHECKLIST-END -->"


def repo_root():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and os.path.isdir(env):
        return env
    # <root>/.claude/hooks/gate-check.py -> up three
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_checklist():
    """Pull the checklist block from docs/PRINCIPLES.md (single source). Raises on any problem."""
    path = os.path.join(repo_root(), "docs", "PRINCIPLES.md")
    text = open(path, encoding="utf-8", errors="replace").read()
    s = text.find(START)
    e = text.find(END)
    if s == -1 or e == -1 or e <= s:
        raise ValueError("GATE-CHECKLIST markers not found in " + path)
    body = text[text.find("\n", s) + 1: text.rfind("\n", s, e)].strip()
    if not body:
        raise ValueError("GATE-CHECKLIST block is empty")
    return body


def checklist_text():
    try:
        return load_checklist()
    except Exception as ex:
        # LOUD, active failure -- the reference broke; do NOT pretend the gate is healthy.
        return (
            "[PRE-BUILD GATE -- ⚠ CHECKLIST SOURCE MISSING]\n"
            "Could not load the checklist from docs/PRINCIPLES.md: %s\n"
            "THE GATE'S SINGLE SOURCE IS BROKEN -- surface this to Ron and repair the file / markers / path\n"
            "before trusting the gate. Minimal core meanwhile: (1) verified in the SOURCE, not memory?  "
            "(2) did Ron approve THIS change?  (3) 3rd+ patch on one symptom -> question the abstraction, go\n"
            "to the true source.  (4) bump the version stamp in this same edit." % ex
        )


def allow():
    sys.exit(0)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        return allow()

    try:
        tool_input = data.get("tool_input") or {}
        file_path = tool_input.get("file_path") or tool_input.get("path") or ""
        if not file_path or not is_app_source(file_path):
            return allow()

        # Flag lives in the system temp dir (NOT the repo). The runtime does not
        # reliably pass scratchpad_dir, so use a deterministic temp path keyed by
        # session id -- gate-reset.py computes the identical path.
        session = data.get("session_id") or "default"
        flag = os.path.join(tempfile.gettempdir(),
                            "rw-gate-pending-%s.flag" % session)

        if not os.path.exists(flag):
            return allow()  # not the first app-source edit of the turn

        # First app-source edit of the turn: consume the flag and deny once.
        try:
            os.remove(flag)
        except Exception:
            pass

        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": checklist_text(),
            }
        }
        print(json.dumps(out))
        sys.exit(0)
    except Exception:
        return allow()


if __name__ == "__main__":
    main()
