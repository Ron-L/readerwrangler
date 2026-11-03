#!/usr/bin/env python3
"""
Tool-survey reminder (UserPromptSubmit, RW only; Ron, 2026-11-03).

Tools for Claude (skills, plugins, tool servers) appear faster than Claude's training data can keep up with, so the
survey of what RW should use is re-run every 4 weeks — by a hook, not by remembering. The STATE IS THE REPORT ITSELF
(SURVEY below): its "Next due: YYYY-MM-DD" line. Once today reaches it, this asks Claude to raise the refresh with Ron
at a natural break and offer /tool-survey. "Not now" = Claude moves the Next due line (that edit is the snooze), so
the reminder doesn't repeat on every message after Ron has answered. A refresh rewrites both lines (Surveyed = the run
date, Next due = +INTERVAL_DAYS).

Fail loud: a missing report or an unreadable Next due line is reported, never silently skipped.
Any other error -> emit nothing (exit 0).
"""
import sys, os, re, json, datetime

SURVEY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "design", "TOOL-SURVEY.md")
INTERVAL_DAYS = 28


def emit(note):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": note}}))


def main():
    try:
        sys.stdin.read()
        path = os.path.normpath(SURVEY)
        try:
            with open(SURVEY, encoding="utf-8") as f:
                head = f.read(4000)
        except OSError:
            emit("[Tool survey] REPORT MISSING: " + path + " - tell Ron; the 4-weekly survey reminder can't work "
                 "without it (recreate it with /tool-survey).")
            return
        m = re.search(r"^Next due:\s*(\d{4}-\d{2}-\d{2})", head, re.MULTILINE)
        if not m:
            emit("[Tool survey] " + path + " has no readable 'Next due: YYYY-MM-DD' line near the top - tell Ron and "
                 "fix the line (it is this reminder's only state).")
            return
        due = datetime.date.fromisoformat(m.group(1))
        today = datetime.date.today()
        if today < due:
            return
        last = re.search(r"^Surveyed:\s*(\d{4}-\d{2}-\d{2})", head, re.MULTILINE)
        since = (" (last surveyed " + last.group(1) + ")") if last else ""
        emit("[Tool survey] The 4-weekly survey of tools for Claude is due (Next due " + due.isoformat() + since + "). "
             "At a natural break in this conversation — not in the middle of other work — tell Ron and offer to run "
             "/tool-survey. If he says not now, move the report's 'Next due' line to the date he picks (or +7 days); "
             "that edit is the snooze. Answer his message first as usual.")
    except Exception:
        pass


if __name__ == "__main__":
    main()
    sys.exit(0)
