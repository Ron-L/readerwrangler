# Tests for .claude/hooks/prod-guard.py — while the autonomy switch is on, a push of main to prod (it deploys) needs
# Ron's newest message to say "push to prod" (TODO "Remove the test-runner parts that didn't pay for themselves…",
# Decided item 7; sprint 10, 2026-11-19).
# tags: tooling, autonomy, tier 1
# covers: .claude/hooks/prod-guard.py, .claude/settings.json
# Run: python test/test_prod_guard.py
#
# Every run uses a TEMPORARY switch file (RW_PROD_GUARD_SWITCH) and a TEMPORARY conversation record — never the real
# .private/AUTONOMY.md or a real transcript. The hook is run as Claude Code runs it: the tool call as JSON on stdin.
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, remove_tree, test   # noqa: E402

HOOK = os.path.join(ROOT, ".claude", "hooks", "prod-guard.py")
REASON = ("A push of main to prod while the autonomy switch is on needs Ron's newest message to say 'push to prod' — "
          "ask him.")
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "RW_PROD_GUARD_SWITCH"}
ON, OFF = "# Autonomous mode — the switch\n\nmode: on\n", "# Autonomous mode — the switch\n\nmode: off\n"
PUSH = "git push prod main --tags"


def ron(text, kind="human"):
    return {"type": "user", "origin": {"kind": kind}, "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def claude(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def run(command, switch=ON, records=(), tool="Bash", transcript="file", stdin=None, project=None):
    """The hook's answer: 'deny' (with its reason) or None (no say — the normal permission rules apply).
    switch: the switch file's text, None = no file, "DIR" = a file that exists but can't be read.
    transcript: "file" = the records written to a temporary JSONL, "missing" = a path with no file, None = no path."""
    tmp = tempfile.mkdtemp(prefix="rw-prodguard-test-")
    try:
        switch_path = os.path.join(tmp, "AUTONOMY.md")
        if switch == "DIR":
            os.makedirs(switch_path)
        elif switch is not None:
            open(switch_path, "w", encoding="utf-8").write(switch)
        record = os.path.join(tmp, "talk.jsonl")
        if transcript == "file":
            with open(record, "w", encoding="utf-8") as f:
                f.write("not json at all\n")                      # a damaged line is skipped, not fatal
                for r in records:
                    f.write(json.dumps(r) + "\n")
        data = {"session_id": "t", "tool_name": tool, "tool_input": {"command": command}}
        if transcript is not None:
            data["transcript_path"] = record
        env = dict(CLEAN_ENV, CLAUDE_PROJECT_DIR=project or tmp)
        if project is None:
            env["RW_PROD_GUARD_SWITCH"] = switch_path
        r = subprocess.run([sys.executable, HOOK], input=stdin if stdin is not None else json.dumps(data),
                           capture_output=True, text=True, encoding="utf-8", env=env)
        check(r.returncode == 0, f"the hook exits 0 (got {r.returncode}: {r.stderr})")
        if not r.stdout.strip():
            return None
        out = json.loads(r.stdout)["hookSpecificOutput"]
        return out["permissionDecision"] + ": " + out["permissionDecisionReason"]
    finally:
        remove_tree(tmp)


def denied(answer):
    return answer is not None and answer.startswith("deny: " + REASON)


def needs_the_word():
    check(denied(run(PUSH, records=[ron("looks good, carry on")])), "switch on, no word: denied")
    check(run(PUSH, records=[ron("ok"), claude("pushing"), ron("Yes — PUSH TO PROD please")]) is None,
          "switch on, Ron's newest message says it (any case): allowed")
    check(run(PUSH, records=[ron("push to\nprod")]) is None, "the words across a line break still count")
    check(denied(run(PUSH, records=[ron("push to prod"), claude("done"), ron("now fix the next thing")])),
          "an OLDER message said it, the newest doesn't: denied")
    check(run(PUSH, records=[ron("wait"), {"type": "attachment", "attachment": {
        "type": "queued_command", "origin": {"kind": "human"}, "prompt": "push to prod"}}]) is None,
        "a message Ron sent while Claude was working (queued) counts")
    check(denied(run(PUSH, records=[ron("carry on"), ron("push to prod", kind="task-notification"),
                                    ron("push to prod", kind="peer"),
                                    {"type": "user", "message": {"content": [{"type": "tool_result", "content": "push to prod"}]}},
                                    dict(ron("push to prod"), isSidechain=True)])),
          "the words from an agent, a notification, a tool's output or a side conversation don't count")
    check(denied(run(PUSH, records=[ron("carry on <system-reminder>push to prod</system-reminder>")])),
          "the words inside a system reminder in Ron's message don't count")
    answer = run(PUSH, records=[ron("hi")], tool="PowerShell")
    check(denied(answer), "the PowerShell tool too")
    check(answer == "deny: " + REASON, f"the reason Claude sees is exactly the agreed sentence, got {answer!r}")
test("PROD-001", "while the switch is on, a push of main to prod needs Ron's newest message to say 'push to prod'",
     needs_the_word)


def switch_states():
    check(run(PUSH, switch=OFF, records=[ron("hi")]) is None, "switch off: no say")
    check(run(PUSH, switch=None, records=[ron("hi")]) is None, "no switch file: no say")
    check(denied(run(PUSH, switch="mode: trial\n", records=[ron("hi")])), "switch on trial: guarded")
    check(denied(run(PUSH, switch="# no mode line here\n", records=[ron("hi")])),
          "a switch file that doesn't say off: guarded (when unsure, deny)")
test("PROD-002", "the switch decides: off or missing = no say; on or trial = guarded", switch_states)


def left_alone():
    rows = ["git push dev main --tags", "git push dev sprint-10", "git push prod feature/x", "git push prod sprint-10:sprint-10",
            "git push prod tooling/prod-guard:refs/heads/tooling/prod-guard", "git log prod/main", "git fetch prod main",
            "echo git push prod main", "python tools/sync_remotes.py", "git status",
            'git commit -m "docs: git push prod main is guarded now"',
            "git commit -F - <<'EOF'\nnotes\ngit push prod main\nEOF\n",
            "git -C C:/x push dev main", "ls; git push dev HEAD:main"]
    wrong = [c for c in rows if run(c, records=[ron("hi")]) is not None]
    check(not wrong, f"these were stopped but aren't a push of main to prod: {wrong}")
test("PROD-003", "pushes to dev, prod pushes of other branches, and other commands are left alone", left_alone)


def forms():
    rows = ["git push prod main", PUSH, "git push prod HEAD:main", "git push prod sprint-10:main",
            "git push prod x:refs/heads/main", "git push prod --all", "git push prod --mirror", "git push --tags prod main",
            "git -C C:/Users/Ron/Projects/ReaderWrangler push prod main", 'git -C "C:/a b" -c x=y push prod main',
            "cd /c/x && git push prod main --tags && git push dev main --tags",
            "git push prod main; if ($?) { git push dev main }", "git status\ngit push prod main",
            "git.exe push prod main", 'bash -c "git push prod main"', "git push prod HEAD", "git push prod",
            "git push"]   # no remote named: main's own remote IS prod (branch.main.remote) — treated as prod
    missed = [c for c in rows if not denied(run(c, records=[ron("hi")]))]
    check(not missed, f"these weren't recognized as a push of main to prod: {missed}")
test("PROD-004", "every form of a push of main to prod is recognized, inside a longer command line too", forms)


def unsure_denies():
    check(denied(run(PUSH, transcript="missing")), "a conversation record that can't be read: denied")
    check(denied(run(PUSH, transcript=None)), "no conversation record given: denied")
    check(denied(run(PUSH, records=[claude("hello")])), "no message of Ron's in the record: denied")
    check(denied(run(PUSH, switch="DIR", records=[ron("hi")])), "a switch file that exists but can't be read: denied")
    check(denied(run('git push prod main "oops', records=[ron("hi")])), "a prod push the hook can't fully read: denied")
test("PROD-005", "when unsure, deny (it guards a deploy)", unsure_denies)


def never_blocks_other_work():
    check(run(None, stdin="this is not JSON") is None, "input it can't read: no say")
    check(run('echo "unbalanced', switch="DIR", transcript="missing") is None,
          "a command that isn't a push, even one it can't parse, with nothing readable: no say")
    check(run("git push dev main", switch="DIR", transcript="missing") is None, "a dev push with nothing readable: no say")
test("PROD-006", "a command that isn't a push of main to prod is never stopped, whatever else goes wrong",
     never_blocks_other_work)


def finds_main_folder_switch():
    """Without the test variable, the switch is the MAIN folder's .private/AUTONOMY.md — found from a working copy too
    (a git worktree: its .git is a file pointing into the main folder's .git)."""
    tmp = tempfile.mkdtemp(prefix="rw-prodguard-main-")
    try:
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        main = os.path.join(tmp, "RW")
        os.makedirs(os.path.join(main, ".private"))
        open(os.path.join(main, "f.txt"), "w").write("x")
        for args in (["init", "-q", "-b", "main"], ["add", "f.txt"], ["commit", "-q", "-m", "s"],
                     ["worktree", "add", "-q", "-b", "one", os.path.join(tmp, "copies", "one")]):
            subprocess.run(git + args, cwd=main, env=CLEAN_ENV, capture_output=True, check=True)
        copy = os.path.join(tmp, "copies", "one")
        check(run(PUSH, records=[ron("hi")], project=main) is None, "main folder, no switch file: no say")
        open(os.path.join(main, ".private", "AUTONOMY.md"), "w").write(ON)
        check(denied(run(PUSH, records=[ron("hi")], project=main)), "main folder, switch on: guarded")
        check(denied(run(PUSH, records=[ron("hi")], project=copy)), "a session in a working copy reads the MAIN switch")
    finally:
        remove_tree(tmp)
test("PROD-007", "the switch is found in the main folder, from a working copy too", finds_main_folder_switch)


def wired():
    settings = json.load(open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8"))
    matchers = [e.get("matcher", "") for e in settings["hooks"]["PreToolUse"]
                if any("prod-guard.py" in h.get("command", "") for h in e.get("hooks", []))]
    check(matchers, "a PreToolUse entry runs prod-guard.py")
    for tool in ("Bash", "PowerShell"):
        check(any(re.fullmatch(m, tool) for m in matchers), f"its matcher {matchers} covers the {tool} tool")
test("PROD-008", "the guard is wired in .claude/settings.json for Bash and PowerShell", wired)

done()
