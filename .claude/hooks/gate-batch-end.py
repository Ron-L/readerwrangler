#!/usr/bin/env python3
"""
PostToolBatch: REFUSING → CLEAR for the pre-build gate (see gate-check.py's state machine).

Claude Code fires PostToolBatch once a whole batch of tool calls has finished, before the next model call — so the
batch whose app edits the gate refused is over, and the re-send (the next batch) may go through. If the gate wasn't
refusing, there's nothing to do (ARMED stays armed; CLEAR stays clear).

Fail-safe: any error is swallowed (exit 0). This hook never blocks anything.
"""
import sys, os, json, tempfile


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        session = data.get("session_id") or "default"
        refusing = os.path.join(tempfile.gettempdir(), "rw-gate-refusing-%s.flag" % session)
        if os.path.exists(refusing):
            os.remove(refusing)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
