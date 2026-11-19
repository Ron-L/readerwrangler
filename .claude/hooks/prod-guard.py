#!/usr/bin/env python3
"""
PreToolUse (Bash, PowerShell): while the autonomy switch is on, a push of main to prod — it deploys — needs Ron's newest
message to say "push to prod" (TODO "Remove the test-runner parts that didn't pay for themselves…", Decided item 7;
sprint 10, 2026-11-19). Settings alone can't say "only while the switch is on"; and the switch is usually on even while
Ron releases, so his own word lets it through.

Acts ONLY on a command that pushes to prod's main: `git push prod main`, `… HEAD:main`, `… x:refs/heads/main`, `--all`,
`--mirror`, `git push prod` with no branch named, a bare `git push` (main's own remote is prod), `git -C <path> push …`,
anywhere in a longer command line (and inside `bash -c "…"`). Pushes to dev and prod pushes of other branches (what
tools/sync_remotes.py does) are left alone. Then: the switch (the MAIN folder's .private/AUTONOMY.md — found from a
working copy too) off or missing → no say (the normal "ask" prompt still applies). On or trial → Ron's newest typed
message in the conversation record (the transcript; as compaction_carry.py finds it) must contain "push to prod".
When unsure — a switch file that can't be read, no readable record, no message of Ron's — DENY: this guards a deploy.
Anything going wrong on a command that isn't a prod push → no say: it never blocks other work.
Tests: test/test_prod_guard.py (PROD-001–008); RW_PROD_GUARD_SWITCH points it at a test's switch file.
"""
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REASON = ("A push of main to prod while the autonomy switch is on needs Ron's newest message to say 'push to prod' — "
          "ask him.")
LOOKS_LIKE = re.compile(r"\bgit(\.exe)?\b.*\bpush\b", re.S | re.I)     # the fallback when a command can't be read
SHELLS = {"bash", "sh", "powershell", "pwsh", "cmd"}


def pushes_prod_main(words):
    """One simple command's words → True if it pushes (or may push) prod's main."""
    while words and (re.fullmatch(r"\w+=.*", words[0]) or words[0] in ("env", "command", "time", "exec")):
        words = words[1:]
    head = re.split(r"[\\/]", words[0])[-1].lower() if words else ""
    if head.removesuffix(".exe") in SHELLS:                              # bash -c "…", powershell -Command "…"
        return any(is_prod_main_push(w) for w in words[1:] if not w.startswith(("-", "/")))
    if head not in ("git", "git.exe"):
        return False
    i = 1
    while i < len(words) and words[i].startswith("-"):                 # git's own options: -C <path>, -c <k=v>…
        i += 2 if words[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    if i >= len(words) or words[i] != "push":
        return False
    remote, refs, every, args = None, [], False, iter(words[i + 1:])
    for a in args:
        if a in ("--all", "--mirror", "--branches"):
            every = True
        elif a in ("-o", "--push-option"):
            next(args, None)
        elif a.startswith("-"):
            continue
        elif remote is None:
            remote = a
        else:
            refs.append(a)
    if remote is None:
        return True                                     # bare `git push`: main's own remote is prod
    dests = [r.lstrip("+").split(":")[-1] for r in refs]
    return remote == "prod" and (every or not refs or any(d in ("main", "refs/heads/main", "HEAD", "@") for d in dests))


def is_prod_main_push(command):
    if "push" not in command.lower():
        return False
    try:
        sys.path.insert(0, HERE)
        from command_writes import PS_HERESTRING, take_heredocs         # heredoc / here-string bodies are text, not commands
        lex = shlex.shlex(PS_HERESTRING.sub(" ", take_heredocs(command)[0]), posix=True, punctuation_chars=";&|(){}\n")
        lex.whitespace, lex.whitespace_split = " \t\r", True
        segment = []
        for w in list(lex) + [";"]:
            if w and all(c in ";&|(){}\n" for c in w):
                if segment and pushes_prod_main(segment):
                    return True
                segment = []
            else:
                segment.append(w)
        return False
    except Exception:                                                  # can't read it: a git push of any kind counts
        return bool(LOOKS_LIKE.search(command))


def main_folder():
    """The main folder: the session's folder, or — when that is a working copy (a git worktree, whose .git is a FILE) —
    the folder that holds the shared .git."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(HERE))
    dot_git = os.path.join(root, ".git")
    if not os.path.isfile(dot_git):
        return root
    gitdir = open(dot_git, encoding="utf-8").read().split("gitdir:", 1)[1].strip()
    common = open(os.path.join(gitdir, "commondir"), encoding="utf-8").read().strip()
    return os.path.dirname(os.path.normpath(os.path.join(gitdir, common)))


def switch_on():
    path = os.environ.get("RW_PROD_GUARD_SWITCH") or os.path.join(main_folder(), ".private", "AUTONOMY.md")
    if not os.path.exists(path):
        return False
    m = re.search(r"^\s*mode:\s*`?(\w+)", open(path, encoding="utf-8", errors="replace").read(), re.M | re.I)
    return not (m and m.group(1).lower() == "off")                     # anything but a clear "off" is guarded


def newest_ron_message(path):
    """Ron's newest typed message (a user record or a queued message whose origin is "human"), or None."""
    def text(c):
        return c if isinstance(c, str) else "\n".join(
            x.get("text", "") for x in c or [] if isinstance(x, dict) and x.get("type") == "text")
    newest = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            a = r.get("attachment") or {}
            if r.get("isSidechain") or r.get("isMeta") or r.get("isCompactSummary"):
                continue
            if r.get("type") == "user" and (r.get("origin") or {}).get("kind") == "human":
                newest = text((r.get("message") or {}).get("content"))
            elif r.get("type") == "attachment" and a.get("type") == "queued_command" and \
                    (a.get("origin") or {}).get("kind") == "human":
                newest = text(a.get("prompt"))
    if newest is None:
        return None
    return re.sub(r"<(ide_opened_file|ide_selection|system-reminder)\b[^>]*>.*?</\1>", "", newest, flags=re.S)


def decide(data):
    """None = no say; otherwise the reason to deny."""
    if not is_prod_main_push((data.get("tool_input") or {}).get("command") or ""):
        return None
    try:
        if not switch_on():
            return None
        if not data.get("transcript_path"):
            return REASON + " (No conversation record was given to read.)"
        said = newest_ron_message(data["transcript_path"])
    except Exception as e:                                              # noqa: BLE001 — unsure → deny
        return REASON + f" (Couldn't check: {e})"
    if said is None:
        return REASON + " (No message of Ron's was found in the conversation record.)"
    return None if "push to prod" in " ".join(said.lower().split()) else REASON


if __name__ == "__main__":
    try:
        reason = decide(json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}"))
    except Exception:                                                   # can't even read the call: never block
        reason = None
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    sys.exit(0)
