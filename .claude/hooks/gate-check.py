#!/usr/bin/env python3
"""
PreToolUse gate. Fires on Edit/Write to APP SOURCE only.
On the FIRST app-source edit of a turn it shows the pre-build checklist by refusing the edit; the edit is then re-sent.

The checklist is NOT stored here. It is the SINGLE SOURCE in docs/PRINCIPLES.md, between the
<!-- GATE-CHECKLIST-START --> / <!-- GATE-CHECKLIST-END --> markers; this hook is just a printer that
pulls that block. If it cannot be read, the hook prints a LOUD failure (never a silent degrade) so a
broken reference announces itself. (Ron, 2026-09-30: no duplication to drift; and make the failure active.)

THE STATE MACHINE (2026-10-19, Ron + Claude) — three states, moved only by real signals, no guessing:

    ARMED ──first app edit──▶ REFUSING ──PostToolBatch──▶ CLEAR
      ▲                     (every app edit in              │
      └──── Stop / SessionStart (gate-reset.py) ────────────┘
              this batch is refused)

  - ARMED     (file rw-gate-pending-<session>.flag)   set by gate-reset.py at each turn's end and at session start.
  - REFUSING  (file rw-gate-refusing-<session>.flag)  set here by the first app edit; EVERY app edit while it exists
                                                      is refused, however the batch is streamed or timed.
  - CLEAR     (neither file)                          set by gate-batch-end.py on PostToolBatch, which Claude Code fires
                                                      once a whole batch of tool calls has finished, before the next
                                                      model call (probed 2026-10-19: once per batch, after its slowest
                                                      call, listing every call). The re-send is the next batch → allowed.

Why: when the first app edit arrives in a batch of several, refusing only that one let the REST land, and the change
applied by halves (alpha.62; twice more on 7.21.2). Two earlier fixes GUESSED where a batch ends — a 5-second timer,
then the session transcript's message ids — and both failed (edits stream in and are written with unpredictable
timing; 7.23.0-alpha.2 and 7.22.1-alpha.3 half-applied). PostToolBatch is the signal those guesses stood in for.

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


def state_file(session, state):
    """The temp-dir file that marks a state ('pending' = ARMED, 'refusing' = REFUSING) for this session. gate-reset.py
    and gate-batch-end.py compute the identical paths."""
    return os.path.join(tempfile.gettempdir(), "rw-gate-%s-%s.flag" % (state, session))


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


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
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

        session = data.get("session_id") or "default"
        armed, refusing = state_file(session, "pending"), state_file(session, "refusing")

        if os.path.exists(refusing):                      # REFUSING: another app edit of the bounced batch
            return deny(
                "[PRE-BUILD GATE -- BATCH REFUSED] This app-code edit came in the same batch as the one the checklist\n"
                "just refused, so it was refused too -- NONE of this batch's app-code edits applied (non-app edits,\n"
                "e.g. docs, did). After the checklist, RE-SEND EVERY app-code edit from the batch.")

        if os.path.exists(armed):                         # ARMED → REFUSING: the first app edit of the turn
            try:
                open(refusing, "w").close()               # REFUSING before ARMED is consumed: no edit can slip between
            except Exception:
                pass
            try:
                os.remove(armed)
            except Exception:
                pass
            return deny(checklist_text() + "\n\n[BATCH] Every other app-code edit in this batch is refused too -- "
                        "re-send ALL of them, not just this one.")

        return allow()                                    # CLEAR
    except Exception:
        return allow()


if __name__ == "__main__":
    main()
