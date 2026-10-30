#!/usr/bin/env python3
"""
Relay-summary reminder (UserPromptSubmit, RW only; Ron, 2026-10-30).

The relay mails its daily summaries at 23:55 UTC, dated by the UTC day. On the first prompt after 00:00 UTC this
adds a note to Claude's turn: "the summaries for <date(s)> are in — read them and report", then records the latest
date as covered. A skipped day is caught up on the next prompt (up to a week). The reading itself is Claude's, through
the one Gmail filter Ron allowed (memory: feedback_gmail_relay_only) — this hook only reminds.

Mechanism, not memory: "remember to check each evening" fails after a compaction; this can't.
State: a temp-dir file holding the last covered date (YYYY-MM-DD). Lost (temp cleared) = one extra reminder, harmless.
Fail-safe: any error -> emit nothing (exit 0). A reminder must never block a turn.
"""
import sys, os, json, tempfile, datetime

STATE = os.path.join(tempfile.gettempdir(), "rw-relay-summary-covered.txt")
GMAIL_FILTER = 'from:alerts@readerwrangler.com subject:"Daily usage summary"'
MAX_CATCH_UP = 7


def main():
    try:
        sys.stdin.read()                                   # payload unused; read it so the pipe closes cleanly
        latest = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)
        covered = None
        try:
            with open(STATE) as f:
                covered = datetime.date.fromisoformat(f.read().strip())
        except (OSError, ValueError):
            covered = None      # missing or damaged = start over (one reminder) — never go silent for good
        if covered is not None and covered >= latest:
            return
        first = latest if covered is None else max(covered + datetime.timedelta(days=1),
                                                   latest - datetime.timedelta(days=MAX_CATCH_UP - 1))
        dates = [(first + datetime.timedelta(days=i)).isoformat() for i in range((latest - first).days + 1)]
        note = ("[Relay check] The relay's daily summaries for " + ", ".join(dates) + " (UTC) are in. In this reply, "
                "read them from Ron's Gmail with ONLY this filter: " + GMAIL_FILTER + " (plus those dates), and report "
                "- one line if both relays are healthy and nothing changed, details if anything did. Then answer Ron's "
                "message as usual.")
        with open(STATE, "w") as f:
            f.write(latest.isoformat())
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}}))
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
