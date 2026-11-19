#!/usr/bin/env python3
"""
Commit checks on? (SessionStart, beside gate-reset.py; TODO "Working-process safety net", item 1 — sprint 9, 2026-11-18)

The commit checks (git-hooks/) run only when git's local setting core.hooksPath says "git-hooks" — a clone never brings
it. When the session's copy of the project isn't set up, this says so LOUDLY: a message Ron sees at once
(systemMessage), and a note telling Claude to say it to him, with the one command that fixes it. Set up → silent.

The rule and the wording are tools/setup_check.py's (serve.py prints the same warning at start-up). The copy checked is
the session's project ($CLAUDE_PROJECT_DIR; this file's own repo when that isn't set).

Fail loud: if tools/setup_check.py can't be loaded, that is said instead (the check must never silently stop). Never
fails the session (exit 0).
"""
import importlib.util
import json
import os
import sys

HERE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def emit(user_text, claude_text):
    print(json.dumps({"systemMessage": user_text,
                      "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": claude_text}}))


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass
    root = os.environ.get("CLAUDE_PROJECT_DIR") or HERE_ROOT
    try:
        spec = importlib.util.spec_from_file_location("rw_setup_check", os.path.join(HERE_ROOT, "tools", "setup_check.py"))
        check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(check)
    except Exception as e:   # noqa: BLE001 — fail loud, never silent
        emit(f"[setup-check] CHECK MISSING: tools/setup_check.py couldn't be loaded ({e}) - whether the commit checks are "
             "on in this copy is unknown.",
             "[setup-check] The session-start check of the commit checks couldn't run (tools/setup_check.py didn't "
             f"load: {e}). Tell Ron at the start of your reply.")
        return
    problem = check.hooks_path_problem(root)
    if problem is None:
        return
    text = "\n".join(check.warning_lines(problem))
    emit(text,
         f"[setup-check] THE COMMIT CHECKS ARE OFF in {root}: {problem}. Every commit there skips them (version guard, "
         f"name check, private values...). Tell Ron first thing in your reply, with the fix: `{check.FIX}` (run once "
         "in the project folder). Don't commit there until it's fixed.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
