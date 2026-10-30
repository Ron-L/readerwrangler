#!/usr/bin/env python3
"""
Relay-summary reminder (UserPromptSubmit, RW only; Ron, 2026-10-30).

The relay mails its daily summaries at 23:55 UTC, dated by the UTC day. On any prompt where the newest available
nightly summary (yesterday, UTC) isn't yet in the trend file, this tells Claude to read the missing nights and add
them. The STATE IS THE TREND FILE (TREND below — the last "nightly" date in it), not a separate flag: the
reminder repeats on every prompt until the rows are actually added, so it can't be marked done by being shown once.
Missed days (Ron away from RW) are caught up whenever he's next here — up to MAX_CATCH_UP nights; beyond that, the
note says so. On-demand rows (run=on-demand) don't count toward "covered".

The reading is Claude's, through the one Gmail filter Ron allowed (memory: feedback_gmail_relay_only).
Fail loud: a missing trend file is reported, never silently skipped. Any other error -> emit nothing (exit 0).
"""
import sys, os, csv, json, datetime

TREND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".private", "relay-trend.csv")
GMAIL_FILTER = 'from:alerts@readerwrangler.com subject:"Daily usage summary"'
MAX_CATCH_UP = 31


def last_nightly():
    """The newest date with a nightly row, or None if there are none. Raises OSError if the file is missing."""
    covered = None
    with open(TREND, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                if row.get("run") == "nightly":
                    d = datetime.date.fromisoformat(row["date"])
                    covered = d if covered is None or d > covered else covered
            except (KeyError, ValueError, TypeError):
                continue
    return covered


def emit(note):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}}))


def main():
    try:
        sys.stdin.read()
        latest = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=1)
        try:
            covered = last_nightly()
        except OSError:
            emit("[Relay check] TREND FILE MISSING: " + os.path.normpath(TREND) + " - tell Ron, and recreate it "
                 "(header: date,relay,run,storage_mb,keys_now,keys_cf_max,requests,reads,writes,deletes,lists,"
                 "library_parts,devicestate_parts,mailbox,pointers,deleted,kept,notes).")
            return
        if covered is not None and covered >= latest:
            return
        first = latest if covered is None else covered + datetime.timedelta(days=1)
        gap = ""
        if (latest - first).days + 1 > MAX_CATCH_UP:
            first = latest - datetime.timedelta(days=MAX_CATCH_UP - 1)
            gap = " (more nights were missed than " + str(MAX_CATCH_UP) + "; tell Ron the earlier ones were skipped)"
        dates = [(first + datetime.timedelta(days=i)).isoformat() for i in range((latest - first).days + 1)]
        emit("[Relay check] The relay's nightly summaries for " + ", ".join(dates) + " (UTC) are in" + gap + ". In "
             "this reply: read them from Ron's Gmail with ONLY this filter: " + GMAIL_FILTER + " (plus those dates); "
             "add one row per relay per night to " + os.path.normpath(TREND) + " (run=nightly; the header names the columns; "
             "short channel codes only); and report - one line if both relays are healthy and nothing changed, details "
             "and the trend if anything did. Then answer Ron's message as usual.")
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
