# Tests for tools/merge_branches.py — task branches merged into main-prime by a script.
# tags: merge-branches, tooling, tier 1
# covers: tools/merge_branches.py, git-hooks/check-toc.js
# Run: python test/test_merge_branches.py
#
# TODO "Faster sprints", item 4 (2026-11-16). Each test builds a throwaway repository with real git: the real
# tools/merge_branches.py, and stand-ins for the tools it calls — build.py (dist/ = the source with a header),
# message_codes.py (the table from log("CODE") calls), run_tests.py (records each tier's run on the commit; --stamp is
# PROVEN only when tiers 1 and 2 both ran on HEAD with nothing uncommitted).
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, remove_tree, test   # noqa: E402

MERGE = os.path.join(ROOT, "tools", "merge_branches.py")
# git's own variables (GIT_DIR, GIT_INDEX_FILE…) point every git command at THIS repository while the commit hook runs
# (RUN-044) — everything here runs without them.
CLEAN_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

BUILD = '''import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for name in ("readerwrangler.js", "mobile.js"):
    text = open(os.path.join(ROOT, name), encoding="utf-8").read()
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    open(os.path.join(ROOT, "dist", name), "w", encoding="utf-8", newline="\\n").write("// built\\n" + text)
'''
CODES = '''import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for name in sorted(os.listdir(ROOT)):
    if name.endswith(".js"):
        for code in re.findall(r'log\\("([A-Z]+-\\d+)"', open(os.path.join(ROOT, name), encoding="utf-8").read()):
            rows.append(f"| {code} | {name} |")
os.makedirs(os.path.join(ROOT, "docs", "design"), exist_ok=True)
open(os.path.join(ROOT, "docs", "design", "MESSAGE-CODES.md"), "w", encoding="utf-8", newline="\\n").write(
    "# Codes\\n\\n| Code | File |\\n|---|---|\\n" + "".join(r + "\\n" for r in sorted(rows)))
'''
RUNNER = '''import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
log = os.path.join(ROOT, git("rev-parse", "--git-path", "stub-runs"))
head, clean = git("rev-parse", "HEAD"), git("status", "--porcelain") == ""
if "--stamp" in sys.argv:
    runs = open(log).read().split() if os.path.exists(log) else []
    ok = all(f"{t}:{head}:clean" in runs for t in ("1", "2"))
    print(("PROVEN" if ok else "NOT PROVEN") + f" — stand-in stamp for {head[:12]}")
    sys.exit(0 if ok else 1)
tier = sys.argv[sys.argv.index("--tier") + 1]
failing = os.environ.get("RW_STUB_FAIL") == "1"
open(log, "a").write(f"{tier}:{head}:{'clean' if clean and not failing else 'no'}\\n")
print(f"stand-in tier {tier} on {head[:12]}: " + ("Tests: 0 file(s) passed, 1 failed" if failing else
      "Tests: 1 file(s) passed, 0 failed"))
sys.exit(1 if failing else 0)
'''
FILLER = "".join(f"// line {i}\n" for i in range(12))
APP = ('// app\nconst ORGANIZER_VERSION = "7.31.0-alpha.1";  // Build version for this file\nfunction alpha() {\n'
       '    return 1;\n}\n' + FILLER + 'function omega() {\n    return 2;\n}\n')
MOBILE = "// phone\nconst MOBILE_VERSION = '1.12.2';\n" + FILLER + "function phone() {}\n"
PAGE = ('<html>\n<link rel="stylesheet" href="readerwrangler.css?v=7.30.0">\n<script src="storage.js?v=7.30.0"></script>\n'
        '<script src="uiHelpers.js?v=7.30.0"></script>\n</html>\n')


def task(title, tid):
    return f"### {title}\n<!-- id {tid} -->\n\n_Why it matters:_ {title.lower()}.\n\nDetails.\n\n"


def todo(tasks):
    def link(t):
        return re.sub(r"[^a-z0-9 -]", "", t.lower()).strip().replace(" ", "-")
    toc = ["- [TODO](#todo)", "  - [High](#high)"] + [f"    - [{t}](#{link(t)})" for t, _ in tasks]
    return ("<!-- TOC -->\n\n" + "\n".join(toc) + "\n\n<!-- /TOC -->\n\n# TODO\n\n## High\n\n"
            + "".join(task(t, i) for t, i in tasks))


def git(cwd, *args, ok=True):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, env=CLEAN_ENV,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if ok and r.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {r.stdout}{r.stderr}")
    return r.stdout.strip()


class Repo:
    """A throwaway repository on main-prime, its dist/ and codes table generated; removed at the end."""

    def __enter__(self):
        self.tmp = tempfile.mkdtemp(prefix="rw-merge-test-")
        self.dir = d = os.path.join(self.tmp, "RW")
        files = {"tools/merge_branches.py": open(MERGE, encoding="utf-8").read(), "tools/build.py": BUILD,
                 "tools/message_codes.py": CODES, "tools/run_tests.py": RUNNER, "readerwrangler.js": APP,
                 "mobile.js": MOBILE, "readerwrangler.html": PAGE, "storage.js": "// storage\n",
                 "readerwrangler.css": "/* css */\n", ".gitignore": "__pycache__/\n",
                 "TODO.md": todo([("Task X", "20261116-0001"), ("Task W", "20261116-0002")])}
        for rel, text in files.items():
            self.write(rel, text)
        git(d, "init", "-q", "-b", "main-prime")
        self.tools()
        git(d, "add", *files, "dist/readerwrangler.js", "dist/mobile.js", "docs/design/MESSAGE-CODES.md")
        git(d, "commit", "-q", "-m", "start")
        return self

    def write(self, rel, text):
        p = os.path.join(self.dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.dir, rel), encoding="utf-8") as f:
            return f.read()

    def tools(self):
        for t in ("build.py", "message_codes.py"):
            subprocess.run([sys.executable, os.path.join(self.dir, "tools", t)], cwd=self.dir, env=CLEAN_ENV, check=True)

    def branch(self, name, edits):
        """A task branch off main-prime: each edit is (file, old, new); the build and codes table regenerated, as the
        commit checks would demand."""
        git(self.dir, "switch", "-q", "-c", name, "main-prime")
        for rel, old, new in edits:
            text = self.read(rel)
            if old not in text:
                raise AssertionError(f"{rel}: {old!r} not found")
            self.write(rel, text.replace(old, new, 1))
        self.tools()
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", f"7.31.0-alpha.9: {name}'s work")
        git(self.dir, "switch", "-q", "main-prime")

    def merge(self, *args, fail_tests=False):
        env = dict(CLEAN_ENV, RW_STUB_FAIL="1" if fail_tests else "0")
        r = subprocess.run([sys.executable, os.path.join(self.dir, "tools", "merge_branches.py"), *args], cwd=self.dir,
                           env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.returncode, r.stdout + r.stderr

    def head(self, ref="HEAD"):
        return git(self.dir, "rev-parse", ref)

    def __exit__(self, *exc):
        remove_tree(self.tmp)


def stamp_of(text, key):
    m = re.search(re.escape(key) + r'\s*=\s*["\']([^"\']+)', text) or re.search(re.escape(key) + r'\?v=([^"]+)', text)
    return m.group(1) if m else None


def two_branches_no_person():
    with Repo() as r:
        r.branch("task-a", [("readerwrangler.js", '"7.31.0-alpha.1"', '"7.31.0-alpha.2"'),
                            ("readerwrangler.js", "    return 1;", '    log("ALPHA-01");\n    return 1;'),
                            ("storage.js", "// storage", "// storage, changed by A"),
                            ("readerwrangler.html", "storage.js?v=7.30.0", "storage.js?v=7.31.0-alpha.2")])
        r.branch("task-b", [("readerwrangler.js", '"7.31.0-alpha.1"', '"7.31.0-alpha.3"'),
                            ("readerwrangler.js", "    return 2;", '    log("OMEGA-01");\n    return 2;'),
                            ("readerwrangler.css", "/* css */", "/* css, changed by B */"),
                            ("readerwrangler.html", "readerwrangler.css?v=7.30.0", "readerwrangler.css?v=7.31.0-alpha.3"),
                            ("mobile.js", "'1.12.2'", "'1.12.3-alpha.3'"),
                            ("mobile.js", "function phone() {}", "function phone() { return 'B'; }")])
        start = r.head("main-prime")
        code, out = r.merge("task-a", "task-b")
        check(code == 0 and "LANDED" in out, f"merged with no person needed (exit {code}):\n{out}")
        app, page, phone = r.read("readerwrangler.js"), r.read("readerwrangler.html"), r.read("mobile.js")
        check('log("ALPHA-01")' in app and 'log("OMEGA-01")' in app, "both branches' code is in")
        check(stamp_of(app, "ORGANIZER_VERSION") == "7.31.0-alpha.5", "ONE fresh version above every branch's (alpha.3 "
              f"→ .4 for A's commit, .5 for B's): {stamp_of(app, 'ORGANIZER_VERSION')}")
        check(stamp_of(page, "storage.js") == "7.31.0-alpha.4" and stamp_of(page, "readerwrangler.css") == "7.31.0-alpha.5"
              and stamp_of(page, "uiHelpers.js") == "7.30.0",
              f"each moved ?v= stamp is a fresh alpha; one nobody moved stays:\n{page}")
        check(stamp_of(phone, "MOBILE_VERSION") == "1.12.3-alpha.5", f"MOBILE_VERSION: its own X.Y.Z, the fresh suffix: {phone}")
        check(r.read("dist/readerwrangler.js") == "// built\n" + app and r.read("dist/mobile.js") == "// built\n" + phone,
              "dist/ is the build of the merged sources")
        codes = r.read("docs/design/MESSAGE-CODES.md")
        check("ALPHA-01" in codes and "OMEGA-01" in codes, f"the codes table regenerated with both: {codes}")
        everything = "".join(r.read(p) for p in git(r.dir, "ls-files").splitlines() if not p.startswith("tools/"))
        check("<<<<<<<" not in everything and "@@RW-STAMP@@" not in everything, "no conflict marker anywhere")
        subjects = git(r.dir, "log", "--format=%s", f"{start}..main-prime").splitlines()
        check(len(subjects) == 2 and subjects[1].startswith("7.31.0-alpha.4: task-a's work (squashed from task-a")
              and subjects[0].startswith("7.31.0-alpha.5: task-b's work (squashed from task-b"),
              f"one squash commit per branch, each with its version: {subjects}")
        check(git(r.dir, "rev-parse", "--abbrev-ref", "HEAD") == "main-prime" and git(r.dir, "status", "--porcelain") == ""
              and not git(r.dir, "branch", "--list", "merging/*"), "back on main-prime, clean, the scratch branch gone")
        check("stand-in tier 1" in out and "stand-in tier 2" in out and "PROVEN" in out,
              f"tier 1 and tier 2 ran on the merged result and its stamp was reported:\n{out}")
test("MERGE-001", "two branches that both bump the version and change dist/ and the codes table, in different code: "
     "merged with no person, one fresh version", two_branches_no_person)


def same_lines_stop():
    with Repo() as r:
        r.branch("task-c", [("readerwrangler.js", '"7.31.0-alpha.1"', '"7.31.0-alpha.2"'),
                            ("readerwrangler.js", "    return 1;", "    return 10;")])
        r.branch("task-d", [("readerwrangler.js", '"7.31.0-alpha.1"', '"7.31.0-alpha.2"'),
                            ("readerwrangler.js", "    return 1;", "    return 20;")])
        start = r.head("main-prime")
        code, out = r.merge("task-c", "task-d")
        check(code == 2 and "STOPPED" in out and "readerwrangler.js" in out.split("STOPPED", 1)[1],
              f"stops, naming the file:\n{out}")
        check("dist/" not in out.split("STOPPED", 1)[1].split("The merge")[0],
              f"…and only the real conflict — not the generated files:\n{out}")
        check(r.head("main-prime") == start, "main-prime hasn't moved")
        check(git(r.dir, "rev-parse", "--abbrev-ref", "HEAD") == "merging/main-prime", "the folder is on the scratch branch")
        app = r.read("readerwrangler.js")
        check("<<<<<<<" in app and "return 10;" in app and "return 20;" in app, "the merge is left in place, both sides")
        code, out = r.merge("--continue")
        check(code != 0 and "still unresolved" in out, f"--continue before resolving: refused:\n{out}")
        # a person's resolution: the first side (the hunk holds the version line too), with the line decided
        r.write("readerwrangler.js", re.sub(r"<<<<<<<[^\n]*\n(.*?)=======\n(.*?)>>>>>>>[^\n]*\n",
                                            lambda m: m.group(1).replace("return 10;", "return 30;"), app, flags=re.S))
        git(r.dir, "add", "readerwrangler.js")
        code, out = r.merge("--continue")
        app = r.read("readerwrangler.js")
        check(code == 0 and "LANDED" in out and "return 30;" in app, f"resolved by a person, --continue lands it:\n{out}")
        check(stamp_of(app, "ORGANIZER_VERSION") == "7.31.0-alpha.4" and r.read("dist/readerwrangler.js") == "// built\n" + app,
              f"with its fresh version and its build: {stamp_of(app, 'ORGANIZER_VERSION')}")

        r.branch("task-e", [("readerwrangler.js", "    return 2;", "    return 40;")])
        r.branch("task-f", [("readerwrangler.js", "    return 2;", "    return 50;")])
        start = r.head("main-prime")
        code, out = r.merge("task-e", "task-f")
        check(code == 2, f"a second conflict stops too:\n{out}")
        code, out = r.merge("--abort")
        check(code == 0 and "ABORTED" in out and r.head() == start and r.head("main-prime") == start,
              f"--abort: back on main-prime, exactly as it was:\n{out}")
        check(git(r.dir, "status", "--porcelain") == "" and not git(r.dir, "branch", "--list", "merging/*")
              and not os.path.exists(os.path.join(r.dir, ".git", "SQUASH_MSG")), "clean, the scratch branch gone")
test("MERGE-002", "two branches editing the same lines: stops, names the file, leaves the merge for a person; "
     "--continue lands it, --abort undoes it", same_lines_stop)


def todo_tasks_kept():
    with Repo() as r:
        r.branch("task-done", [("TODO.md", "### Task X\n", "### ✅ Task X\n"),
                               ("TODO.md", "    - [Task X](#task-x)", "    - [✅ Task X](#-task-x)")])
        r.branch("task-new", [("TODO.md", "### Task W\n", task("Task Y", "20261116-0003") + "### Task W\n"),
                              ("TODO.md", "    - [Task X](#task-x)\n", "    - [Task X](#task-x)\n    - [Task Y](#task-y)\n")])
        code, out = r.merge("task-done", "task-new")
        check(code == 0 and "LANDED" in out, f"merged with no person (only the table of contents collided):\n{out}")
        text = r.read("TODO.md")
        check("### ✅ Task X" in text and "### Task Y" in text and "### Task W" in text, "both branches' tasks are kept")
        toc = text.split("<!-- /TOC -->")[0]
        check(toc.index("[✅ Task X](#task-x)") < toc.index("[Task Y](#task-y)") < toc.index("[Task W](#task-w)"),
              f"the table of contents is rebuilt from the merged headers, in order:\n{toc}")
        r2 = subprocess.run(["node", os.path.join(ROOT, "git-hooks", "check-toc.js"), os.path.join(r.dir, "TODO.md")],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        check(r2.returncode == 0, f"and the real TOC check passes it: {r2.stdout}{r2.stderr}")
test("MERGE-003", "a TODO task from each branch (one marked done, one new right after it): the table of contents "
     "regenerated, both kept", todo_tasks_kept)


def failing_tests_dont_land():
    with Repo() as r:
        r.branch("task-g", [("storage.js", "// storage", "// storage, changed by G")])
        start = r.head("main-prime")
        code, out = r.merge("task-g", fail_tests=True)
        check(code != 0 and "NOT LANDED" in out and r.head("main-prime") == start,
              f"tier 1 fails on the merged result: main-prime untouched:\n{out}")
        check("tier 2 not run" in out, f"tier 2 isn't run after tier 1 failed:\n{out}")
        code, out = r.merge("--abort")
        check(code == 0 and r.head() == start, f"--abort after a failed run: back as it was:\n{out}")
        code, out = r.merge("task-g", "--no-test")
        check(code == 0 and "NOTHING WAS PROVEN" in out and r.head("main-prime") != start,
              f"--no-test lands, and says loudly that nothing was proven:\n{out}")
        code, out = r.merge("task-g")
        check(code == 0 and "nothing to merge" in out, f"a branch already in: nothing to merge:\n{out}")
        git(r.dir, "switch", "-q", "task-g")
        code, out = r.merge("main-prime")
        check(code != 0 and "not main-prime" in out, f"a folder not on the target is refused:\n{out}")
test("MERGE-004", "the merged result must pass tier 1 and tier 2 to land; --no-test lands and says nothing was proven",
     failing_tests_dont_land)

done()
