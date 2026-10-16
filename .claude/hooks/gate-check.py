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

WHOLE-BATCH BOUNCE (Ron, 2026-10-16): when the first app edit arrives in a batch of several, bouncing only that one let
the REST land -- the bounced change then went missing (alpha.62 shipped half a fix; it tried again twice on 7.21.2).
So every other app-source edit in the SAME batch is refused too: the batch fails as a whole, loudly, and is re-sent
as a whole. "Same batch" = same assistant message, read from the session transcript (every call in one batch shares
its message id; a re-send has a new one) -- Ron's idea, 2026-10-16, after the first version's 5-second timer refused
a fast re-send on its first real use. The timer remains only as the fallback when the transcript can't answer
(window FIXED from the bounce, so a re-send is refused at most once more, never in a loop).

Fail-safe: ANY error or unexpected input -> allow (exit 0). A gate bug must never block real work.
"""
import sys, os, json, tempfile, time

BATCH_WINDOW_S = 5.0   # a batch's calls run back-to-back (well under a second); a re-send after reading the bounce
                       # takes a full reply, normally longer than this

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


def batch_of(transcript_path, tool_use_id):
    """The id of the assistant message that carries this tool call -- i.e. its batch -- or None if not (yet) written.
    Reads only the transcript's tail (it grows to many MB)."""
    if not (transcript_path and tool_use_id and os.path.exists(transcript_path)):
        return None
    with open(transcript_path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 4000000))
        tail = f.read().decode("utf-8", "replace")
    for line in reversed(tail.splitlines()):
        if tool_use_id not in line:
            continue
        try:
            msg = json.loads(line).get("message") or {}
        except Exception:
            continue
        if any(isinstance(c, dict) and c.get("id") == tool_use_id for c in msg.get("content") or []):
            return msg.get("id")
    return None


def same_batch_as_bounce(bounced_path, data):
    """Was this call sent in the same batch as the bounced one? By the batch's real identity when the transcript has
    both calls (a call isn't always written yet when ITS OWN hook runs -- probed 2026-10-16 -- but the bounced one is
    by the time a later call arrives); otherwise by the time window."""
    try:
        rec = json.load(open(bounced_path))
    except Exception:
        return False
    tp = data.get("transcript_path")
    a, b = batch_of(tp, rec.get("tool_use_id")), batch_of(tp, data.get("tool_use_id"))
    if a and b:
        return a == b
    return 0 <= time.time() - float(rec.get("t", 0)) <= BATCH_WINDOW_S


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

        # Flag lives in the system temp dir (NOT the repo). The runtime does not
        # reliably pass scratchpad_dir, so use a deterministic temp path keyed by
        # session id -- gate-reset.py computes the identical path.
        session = data.get("session_id") or "default"
        flag = os.path.join(tempfile.gettempdir(),
                            "rw-gate-pending-%s.flag" % session)

        bounced = os.path.join(tempfile.gettempdir(),
                               "rw-gate-bounced-%s.stamp" % session)

        if not os.path.exists(flag):
            # Not the first app-source edit of the turn -- but if it rode in the SAME batch as the bounced one,
            # refuse it too, so the batch never applies by halves.
            if same_batch_as_bounce(bounced, data):
                return deny(
                    "[PRE-BUILD GATE -- BATCH BOUNCED] This edit was sent in the same batch as an edit the pre-build\n"
                    "checklist just bounced, so it was refused too -- NOTHING in that batch's app-code edits applied\n"
                    "(non-app edits in the batch, e.g. docs, did). After the checklist, RE-SEND EVERY app-code edit\n"
                    "from that batch. (If a re-send is refused again, it came too fast -- send it once more.)")
            return allow()

        # First app-source edit of the turn: record the bounce (its call id + time) BEFORE consuming the flag (so a
        # parallel call that finds the flag gone already sees the record), then deny once.
        try:
            with open(bounced, "w") as f:
                json.dump({"t": time.time(), "tool_use_id": data.get("tool_use_id")}, f)
        except Exception:
            pass
        try:
            os.remove(flag)
        except Exception:
            pass

        return deny(checklist_text() + "\n\n[BATCH] Any other app-code edit sent together with this one is refused "
                    "too -- re-send ALL of them, not just this one.")
    except Exception:
        return allow()


if __name__ == "__main__":
    main()
