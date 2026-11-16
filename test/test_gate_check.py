# Tests for the pre-build gate (.claude/hooks/gate-check.py) — which edits it stops, in the main folder AND in a working
# copy (tools/copies.py: a git worktree in another folder).
# tags: gate, tooling, copies, tier 1
# covers: .claude/hooks/gate-check.py, .claude/hooks/command_writes.py, .claude/hooks/gate-batch-end.py, .claude/settings.json, git-hooks/shipped_paths.py
# Run: python test/test_gate_check.py
#
# 2026-11-16 (TODO "Faster sprints", item 3): the gate judged every path against the session's own folder
# (CLAUDE_PROJECT_DIR), so an edit to readerwrangler.js in a working copy — outside that folder — counted as "outside
# this repo" and went through unchecked (seen live: an edit in a copy passed while the gate was armed). Now it finds the
# working copy that holds the file and asks THAT copy's shipped-code rule.
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, remove_tree, test   # noqa: E402

GATE = os.path.join(ROOT, ".claude", "hooks", "gate-check.py")
SESSION = "gate-test-session"
# git's own variables (GIT_DIR, GIT_INDEX_FILE…) point every git command at THIS repository while the commit hook runs
# (RUN-044) — the throwaway repositories get an environment without them.
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(cwd, *args):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, env=CLEAN_ENV,
                       capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stderr}")
    return r.stdout


def make_repo(tmp):
    """A main folder with the shipped-code rule committed, and a working copy of it (a real git worktree) beside it —
    laid out as tools/copies.py lays them out. Returns (main, copy)."""
    main = os.path.join(tmp, "RW")
    os.makedirs(os.path.join(main, "git-hooks"))
    shutil.copy(os.path.join(ROOT, "git-hooks", "shipped_paths.py"), os.path.join(main, "git-hooks"))
    for name in ("readerwrangler.js", "tools/x.js"):
        os.makedirs(os.path.dirname(os.path.join(main, name)), exist_ok=True)
        open(os.path.join(main, name), "w").write("// x\n")
    git(main, "init", "-q", "-b", "main")
    git(main, "add", "git-hooks/shipped_paths.py", "readerwrangler.js", "tools/x.js")
    git(main, "commit", "-q", "-m", "start")
    copy = os.path.join(tmp, "RW-copies", "one")
    git(main, "worktree", "add", "-q", "-b", "one", copy)
    return main, copy


def ask(path, project_dir, tmp):
    """Run the gate as Claude Code does (the edit as JSON on stdin), ARMED for a session; True = it refused."""
    # the gate's state files go in tmp — TMPDIR too: Python reads it first, and git's shell sets it (the commit hook
    # runs this test there; with only TEMP/TMP set it failed only under the hook)
    env = dict(CLEAN_ENV, CLAUDE_PROJECT_DIR=project_dir, TMPDIR=tmp, TEMP=tmp, TMP=tmp)
    for state in ("pending", "refusing"):
        f = os.path.join(tmp, f"rw-gate-{state}-{SESSION}.flag")
        if os.path.exists(f):
            os.remove(f)
    open(os.path.join(tmp, f"rw-gate-pending-{SESSION}.flag"), "w").close()     # ARMED
    data = {"session_id": SESSION, "tool_name": "Edit", "tool_input": {"file_path": path}}
    r = subprocess.run([sys.executable, GATE], input=json.dumps(data), capture_output=True, text=True, env=env)
    return '"deny"' in r.stdout


def gate_in_a_copy():
    tmp = tempfile.mkdtemp(prefix="rw-gate-test-")
    try:
        main, copy = make_repo(tmp)
        check(ask(os.path.join(main, "readerwrangler.js"), main, tmp), "the main folder's app script: stopped")
        check(ask(os.path.join(copy, "readerwrangler.js"), main, tmp),
              "the SAME script in a working copy (a session started in the main folder): stopped")
        check(ask(os.path.join(copy, "newmodule.js"), main, tmp), "a new script at the copy's root: stopped")
        check(ask(os.path.join(copy, "readerwrangler.js"), copy, tmp), "a session started in the copy itself: stopped")
        check(not ask(os.path.join(copy, "tools", "x.js"), main, tmp), "a tool script in the copy (tools/): not stopped")
        check(not ask(os.path.join(copy, "notes.md"), main, tmp), "a document in the copy: not stopped")
        outside = os.path.join(tmp, "elsewhere", "app.js")
        os.makedirs(os.path.dirname(outside))
        check(not ask(outside, main, tmp), "a script in no RW folder: not stopped")
    finally:
        remove_tree(tmp)
test("GATE-001", "the gate stops the first shipped-code edit in a working copy, judged by the copy's own rule",
     gate_in_a_copy)


# 2026-11-16 (TODO tooling task, open item 1 — decided Ron): the gate fired only for the Edit / Write tools, so a change
# made from a terminal command skipped it — twice this week an agent moved version stamps with `sed`, though its brief
# said not to. Now a terminal command (the Bash or PowerShell tool) that WRITES onto shipped code gets the same
# once-per-turn checklist, in the same state machine: one ARMED flag per turn, a refused batch refuses its other app
# edits too, whichever tool made them.
BATCH_END = os.path.join(ROOT, ".claude", "hooks", "gate-batch-end.py")


class Turn:
    """A turn of a session as Claude Code drives the gate: armed once (gate-reset.py's job), then each tool call is shown
    to the gate in turn, and end_batch() is PostToolBatch. Nothing is reset between calls — the state carries over."""

    def __init__(self, tmp, project_dir, cwd):
        self.tmp, self.cwd = tmp, cwd
        self.env = dict(CLEAN_ENV, CLAUDE_PROJECT_DIR=project_dir, TMPDIR=tmp, TEMP=tmp, TMP=tmp)
        for state in ("pending", "refusing"):
            f = os.path.join(tmp, f"rw-gate-{state}-{SESSION}.flag")
            if os.path.exists(f):
                os.remove(f)
        open(os.path.join(tmp, f"rw-gate-pending-{SESSION}.flag"), "w").close()     # ARMED

    def call(self, tool, tool_input):
        """The gate's answer to one tool call: 'checklist' (refused, showing the checklist), 'batch' (refused as part of a
        batch already refused) or 'allow'."""
        data = {"session_id": SESSION, "cwd": self.cwd, "tool_name": tool, "tool_input": tool_input}
        r = subprocess.run([sys.executable, GATE], input=json.dumps(data), capture_output=True, text=True,
                           env=self.env, encoding="utf-8")
        if '"deny"' not in r.stdout:
            return "allow"
        return "batch" if "BATCH REFUSED" in r.stdout else "checklist"

    def bash(self, command):
        return self.call("Bash", {"command": command, "description": "x"})

    def powershell(self, command):
        return self.call("PowerShell", {"command": command, "description": "x"})

    def edit(self, path):
        return self.call("Edit", {"file_path": path, "old_string": "a", "new_string": "b"})

    def end_batch(self):
        subprocess.run([sys.executable, BATCH_END], input=json.dumps({"session_id": SESSION}), capture_output=True,
                       text=True, env=self.env)


def with_copy(fn):
    """Runs fn(main, copy, tmp) on a throwaway main folder + working copy (make_repo), always cleaned up."""
    def run():
        tmp = tempfile.mkdtemp(prefix="rw-gate-test-")
        try:
            fn(*make_repo(tmp), tmp)
        finally:
            remove_tree(tmp)
    return run


def sed_in_place(main, copy, tmp):
    t = Turn(tmp, main, copy)
    check(t.bash("sed -i 's/a/b/' readerwrangler.js") == "checklist", "the first sed -i onto the app script: the checklist")
    t.end_batch()
    check(t.bash("sed -i 's/a/b/' readerwrangler.js") == "allow", "re-sent after the batch: allowed")
    check(t.bash("sed -i 's/b/c/' readerwrangler.js") == "allow", "a later one in the same turn: allowed (once per turn)")
test("GATE-002", "a sed -i onto shipped code gets the checklist once per turn, like an edit",
     with_copy(sed_in_place))


def redirect_onto_shipped(main, copy, tmp):
    check(Turn(tmp, main, copy).bash("echo x > storage.js") == "checklist", "echo x > storage.js: the checklist")
    check(Turn(tmp, main, copy).bash("echo x >> storage.js") == "checklist", "echo x >> storage.js: the checklist")
    check(Turn(tmp, main, copy).bash("echo x | tee -a storage.js") == "checklist", "tee -a storage.js: the checklist")
test("GATE-003", "a redirect or tee onto a shipped script gets the checklist", with_copy(redirect_onto_shipped))


def reads_and_other_writes_pass(main, copy, tmp):
    t = Turn(tmp, main, copy)
    for cmd in ("sed -n 1p readerwrangler.js", "grep -n x readerwrangler.js", "cat readerwrangler.js",
                "sed -i 's/a/b/' test/foo.py", "echo x > docs/notes.md", "cp x dist/readerwrangler.js",
                "git checkout -- readerwrangler.js", "git diff readerwrangler.js > /tmp/x.diff",
                "py tools/run_tests.py --tier 1", "node git-hooks/check-names.js readerwrangler.js"):
        check(t.bash(cmd) == "allow", f"{cmd!r}: passes")
    check(t.edit(os.path.join(copy, "readerwrangler.js")) == "checklist",
          "none of them used up the turn's checklist: the next app edit still gets it")
test("GATE-004", "reads, writes to tests / docs / dist/, and git commands pass without using up the checklist",
     with_copy(reads_and_other_writes_pass))


def copy_onto_worker(main, copy, tmp):
    check(Turn(tmp, main, copy).bash("cp x relay/relay-worker.js") == "checklist", "cp onto relay/relay-worker.js")
    check(Turn(tmp, main, copy).bash("mv new.js storage.js") == "checklist", "mv onto storage.js")
test("GATE-005", "cp / mv onto a shipped script gets the checklist", with_copy(copy_onto_worker))


def powershell_writes(main, copy, tmp):
    check(Turn(tmp, main, copy).powershell("Set-Content readerwrangler.js 'x'") == "checklist",
          "Set-Content readerwrangler.js: the checklist")
    check(Turn(tmp, main, copy).powershell(
        "(Get-Content readerwrangler.js) -replace 'a','b' | Set-Content -Path readerwrangler.js -Encoding utf8")
        == "checklist", "Get-Content … -replace … | Set-Content -Path: the checklist")
    check(Turn(tmp, main, copy).powershell("Get-Content readerwrangler.js | Select-Object -First 5") == "allow",
          "reading with Get-Content: passes")
test("GATE-006", "a PowerShell write onto shipped code gets the checklist", with_copy(powershell_writes))


def edit_and_command_one_batch(main, copy, tmp):
    t = Turn(tmp, main, copy)
    app = os.path.join(copy, "readerwrangler.js")
    check(t.edit(app) == "checklist", "the batch's first app edit (Edit tool): the checklist")
    check(t.bash("sed -i 's/a/b/' storage.js") == "batch", "the sed in the same batch: refused too, no second checklist")
    t.end_batch()
    check(t.edit(app) == "allow" and t.bash("sed -i 's/a/b/' storage.js") == "allow", "both re-sent: both pass")
    t2 = Turn(tmp, main, copy)
    check(t2.bash("sed -i 's/a/b/' storage.js") == "checklist", "a turn whose first app write is a command: the checklist")
    check(t2.edit(app) == "batch", "the Edit in that batch: refused too")
test("GATE-007", "an Edit and a terminal write in one batch see ONE checklist, and both are refused",
     with_copy(edit_and_command_one_batch))


def recognizer_table():
    """What the command reader (.claude/hooks/command_writes.py) says each command writes — every path, shipped or not
    (the gate then asks the shared rule). Paths relative to the command's folder; [] = writes nothing it can tell."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("command_writes", os.path.join(ROOT, ".claude", "hooks",
                                                                                 "command_writes.py"))
    cw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cw)
    tmp = tempfile.mkdtemp(prefix="rw-gate-test-")
    try:
        cwd = os.path.join(tmp, "RW")
        os.makedirs(os.path.join(cwd, "relay"))
        bash_cwd = "/" + cwd[0].lower() + cwd[2:].replace("\\", "/")          # C:\x\RW -> /c/x/RW (Git Bash's spelling)

        def got(cmd, shell="bash", where=None):
            out = cw.written_paths(cmd, where or os.path.join(tmp, "elsewhere"), shell)
            return sorted(os.path.relpath(p, cwd).replace("\\", "/") for p in out)
        rows = [
            # (command, shell, expected) — run from cwd unless the command moves there itself
            ("sed -i 's/a/b/' a.js b.js", "bash", ["a.js", "b.js"]),
            ("sed -i.bak -e 's/a/b/' -e 's/c/d/' a.js", "bash", ["a.js"]),
            ("sed -Ei 's/a/b/' a.js", "bash", ["a.js"]),
            ("sed --in-place=.orig 's/a/b/' a.js", "bash", ["a.js"]),
            ("sed -n '1,5p' a.js", "bash", []),
            ("sed 's/a/b/' a.js > b.js", "bash", ["b.js"]),
            ("perl -pi -e 's/a/b/' a.js", "bash", ["a.js"]),
            ("perl -i.bak -pe 's/a/b/' a.js", "bash", ["a.js"]),
            ("perl -ne 'print' a.js", "bash", []),
            ("awk -i inplace '{print}' a.js", "bash", ["a.js"]),
            ("cat a.js >> b.js", "bash", ["b.js"]),
            ("cmd 2> err.js", "bash", ["err.js"]),
            ("cmd 2>&1 | tail", "bash", []),
            ("cmd > /dev/null 2>&1", "bash", []),
            ("echo x | tee a.js b.js", "bash", ["a.js", "b.js"]),
            ("cp a.js b.js", "bash", ["b.js"]),
            ("cp -f x/a.js x/b.js relay/", "bash", ["relay/a.js", "relay/b.js"]),
            ("cp -t relay x/a.js", "bash", ["relay/a.js"]),
            ("mv a.js b.js", "bash", ["b.js"]),
            ("dd if=a.js of=b.js", "bash", ["b.js"]),
            (f"cd {bash_cwd} && sed -i 's/a/b/' a.js", "bash", ["a.js"]),
            (f"sed -i 's/a/b/' {bash_cwd}/relay/w.js", "bash", ["relay/w.js"]),
            (f"cd '{cwd}' ; echo x > a.js", "bash", ["a.js"]),
            (f"cd {bash_cwd} && cat > a.js <<'EOF'\nline > other.js\nEOF", "bash", ["a.js"]),
            (f"cd {bash_cwd} && git commit -m \"$(cat <<'EOF'\nsed -i x > a.js\nEOF\n)\"", "bash", []),
            (f"cd {bash_cwd} && git show HEAD:a.js > a.js", "bash", ["a.js"]),
            (f"cd {bash_cwd} && git checkout -- a.js && git mv a.js b.js", "bash", []),
            (f"cd {bash_cwd} && python -c \"open('a.js', 'w').write('x')\"", "bash", ["a.js"]),
            (f"cd {bash_cwd} && py -c \"import pathlib; pathlib.Path('a.js').write_text('x')\"", "bash", ["a.js"]),
            (f"cd {bash_cwd} && python -c \"print(open('a.js').read())\"", "bash", []),
            (f"cd {bash_cwd} && python - <<'EOF'\nwith open(r'a.js', 'a', encoding='utf-8') as f: f.write('x')\nEOF",
             "bash", ["a.js"]),
            (f"cd {bash_cwd} && node -e \"require('fs').writeFileSync('a.js', 'x')\"", "bash", ["a.js"]),
            (f"cd {bash_cwd} && powershell -Command \"Set-Content -Path a.js -Value x\"", "bash", ["a.js"]),
            (f"cd {bash_cwd} && bash -c 'sed -i s/a/b/ a.js'", "bash", ["a.js"]),
            (f"cd {bash_cwd} && for f in *.js; do sed -i s/a/b/ $f; done", "bash", []),   # can't tell: passes
            ("Set-Content a.js 'x'", "powershell", ["a.js"]),
            ("Set-Content -Value 'x' -Path a.js", "powershell", ["a.js"]),
            ("Add-Content -LiteralPath a.js -Value x", "powershell", ["a.js"]),
            ("'x' | Out-File -FilePath a.js -Encoding utf8", "powershell", ["a.js"]),
            ("'x' | Out-File a.js", "powershell", ["a.js"]),
            ("(Get-Content a.js) -replace 'a','b' | Set-Content a.js", "powershell", ["a.js"]),
            ("Copy-Item x.js -Destination relay\\w.js", "powershell", ["relay/w.js"]),
            ("Move-Item x.js a.js -Force", "powershell", ["a.js"]),
            ("[IO.File]::WriteAllText('a.js', 'x')", "powershell", ["a.js"]),
            ("'x' > a.js", "powershell", ["a.js"]),
            (f"Set-Location '{cwd}'; Set-Content relay\\w.js x", "powershell", ["relay/w.js"]),
            ("Get-Content a.js | Select-String x", "powershell", []),
            ("git log --oneline > log.txt", "powershell", ["log.txt"]),
        ]
        bad = []
        for cmd, shell, want in rows:
            where = cwd if not cmd.startswith(("cd ", "Set-Location")) else None
            try:
                have = got(cmd, shell, where)
            except Exception as e:                                     # noqa: BLE001 — a crash is a wrong answer here
                have = f"crashed: {e!r}"
            if have != sorted(want):
                bad.append(f"{shell}: {cmd!r}\n        wanted {sorted(want)}, got {have}")
        check(not bad, f"{len(bad)} of {len(rows)} commands read wrong:\n      " + "\n      ".join(bad))
    finally:
        remove_tree(tmp)
test("GATE-008", "the command reader finds the files a terminal command writes (and none it only reads)",
     recognizer_table)


def wired_for_commands():
    """All of the above is dead unless Claude Code hands terminal commands to the gate: .claude/settings.json's PreToolUse
    entry that runs gate-check.py must match Edit, Write, Bash and PowerShell (the tools' names as Claude Code gives them)."""
    import re
    settings = json.load(open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8"))
    matchers = [e.get("matcher", "") for e in settings["hooks"]["PreToolUse"]
                if any("gate-check.py" in h.get("command", "") for h in e.get("hooks", []))]
    check(matchers, "a PreToolUse entry runs gate-check.py")
    for tool in ("Edit", "Write", "Bash", "PowerShell"):
        check(any(re.fullmatch(m, tool) for m in matchers), f"the gate's matcher {matchers} covers the {tool} tool")
test("GATE-009", "the gate is wired for Edit, Write AND the terminal tools (Bash, PowerShell)", wired_for_commands)

done()
