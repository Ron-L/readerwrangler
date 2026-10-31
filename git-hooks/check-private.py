#!/usr/bin/env python3
"""check-private.py - pre-commit: refuse staged changes that add a private value or a Cloud Sync credential (the
check itself: private_values.py). Looks at every added line, and at the whole staged copy of every .json."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from private_values import check_lines, git, json_problem, report  # noqa: E402


def added_lines():
    """("file:line", text) for every line the staged changes add."""
    path, n = None, 0
    for ln in git("diff", "--cached", "--no-color", "--text", "-U0").splitlines():
        if ln.startswith("+++ "):
            path = ln[6:] if ln.startswith("+++ b/") else ln[4:]
        elif ln.startswith("@@"):
            n = int(re.search(r"\+(\d+)", ln).group(1))
        elif ln.startswith("+"):
            yield f"{path}:{n}", ln[1:]
            n += 1


def staged_json():
    names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0")
    for p in filter(None, names):
        if p.lower().endswith(".json"):
            why = json_problem(p, git("show", f":{p}", binary=True))
            if why:
                yield p, why


if __name__ == "__main__":
    code = check_lines("pre-commit (private values)", "these added lines", added_lines())
    code |= report("pre-commit (private values)", "these staged files", list(staged_json()))
    sys.exit(code)
