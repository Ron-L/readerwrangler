#!/usr/bin/env python3
"""
Arms the per-turn pre-build gate (→ ARMED; see gate-check.py's state machine). Runs on Stop (end of each assistant
turn) and SessionStart (so the first turn is covered too). Creates the ARMED flag that gate-check.py consumes on the
first app-source edit of the next turn, and clears any leftover REFUSING flag (normally PostToolBatch clears it; this
makes sure a turn can never start stuck refusing).

Fail-safe: any error is swallowed (exit 0). Arming must never break a turn.
"""
import sys, os, json, tempfile


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        # Deterministic temp path keyed by session id (NOT the repo, NOT cwd) --
        # gate-check.py computes the identical path.
        session = data.get("session_id") or "default"
        flag = os.path.join(tempfile.gettempdir(),
                            "rw-gate-pending-%s.flag" % session)
        with open(flag, "w") as f:
            f.write("armed")
        refusing = os.path.join(tempfile.gettempdir(), "rw-gate-refusing-%s.flag" % session)
        if os.path.exists(refusing):
            os.remove(refusing)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
