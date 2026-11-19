# Tests for git-hooks/check-joined.py — the commit check that refuses a test file where a line of code was joined onto
# the end of a comment (an edit that swallowed a line break: the line stops running and the file still passes).
# tags: commit-checks, tier 1
# covers: git-hooks/check-joined.py, git-hooks/joined-js.js
# Run: python test/test_check_joined.py
#
# 2026-11-18 (sprint 8; TODO "Turn more of our working rules into automatic checks", item 11.3). One table, a row per
# shape the check must refuse or let through, in both languages; then the marker, the staged copy, the real case
# (7.18.0-alpha.55's joined line), a real test file with a row joined on purpose, and the whole library as it stands.
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("check_joined", os.path.join(ROOT, "git-hooks", "check-joined.py"))
cj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cj)
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402

PY_TOP = 'from harness import check\nROWS = []\nharness = None\nrow = print\nrow("A-001", True, "one")\n'
JS_TOP = "const assert = require('assert');\nconst { test, done } = require('./harness');\n"

# (id, what, extension, source, refused?)
ROWS = [
    # ── refused: Python ──
    ("JOIN-001", "a check joined with its indent (the alpha.55 shape)", ".py",
     PY_TOP + "def t(ok):\n    x = 1   # the count    check(x == 1, \"one\")\n", True),
    ("JOIN-002", "an own-line comment with the next line's indent", ".py",
     PY_TOP + "def t(ok):\n    # the row must hold    check(ok, \"holds\")\n    return ok\n", True),
    ("JOIN-003", "a line with no indent, glued to the comment's last word", ".py",
     PY_TOP + "# the rowsrow(\"A-002\", True, \"two\")\n", True),
    ("JOIN-004", "glued to the comment's closing dot", ".py", PY_TOP + "# the table.ROWS = [1]\n", True),
    ("JOIN-005", "an empty comment line with code glued to it", ".py", PY_TOP + "#\n#import os\n", True),
    ("JOIN-006", "an assert joined after a run of spaces", ".py", PY_TOP + "x = 1   # first    assert x == 1\n", True),
    ("JOIN-007", "a table row joined onto the row above's note", ".py",
     PY_TOP + "CASES = [\n    (\"A-001\", \"x\", True),   # note    (\"A-002\", \"y\", False),\n]\n", True),
    ("JOIN-008", "a line joined with ONE space (an editor's join lines)", ".py",
     PY_TOP + "# then check it check(1 == 1, \"one\")\n", True),
    ("JOIN-009", "the first line of a block (its body continues the block above)", ".py",
     PY_TOP + "def a(R):\n    for r in R:\n        pass\n    # again    for r in R:\n        check(r, \"x\")\n", True),
    ("JOIN-010", "an await joined", ".py",
     PY_TOP + "async def a(page):\n    # wait    await page.click(\"#x\")\n", True),
    ("JOIN-011", "a dictionary entry joined", ".py",
     PY_TOP + "W = {\n    \"a.html\": {\"K\": 2},   # its count    \"b.html\": {\"K\": 1},\n}\n", True),
    # ── refused: JavaScript ──
    ("JOIN-012", "the real alpha.55 line's shape", ".js",
     "const a = useRef(null); // anchor for its <Popover>            const b = useRef(null); // anchor\n", True),
    ("JOIN-013", "a one-line test joined", ".js",
     JS_TOP + "// the merge  test('MERGE-001', 'x', () => assert.ok(true));\ndone();\n", True),
    ("JOIN-014", "glued to the comment's closing dot", ".js", JS_TOP + "// the end.assert.strictEqual(1, 1);\n", True),
    ("JOIN-015", "an array row joined", ".js",
     "const R = [\n    ['A-001', 'x', true],   // note    ['A-002', 'y', false],\n];\n", True),
    ("JOIN-016", "an object entry joined", ".js",
     "const P = {\n    'folder': 'f-x',   // one    'inbox': '__inbox__',\n};\n", True),
    ("JOIN-017", "an expect(...) chain joined", ".js", "// see    expect(x).toBe(1);\n", True),
    ("JOIN-018", "a for header joined (its body then runs once, alone)", ".js",
     JS_TOP + "const KINDS = [1];\n// each kind    for (const k of KINDS)\n    test('K-001', 'k', () => {});\n", True),
    ("JOIN-019", "a delete joined", ".js", "const o = {};\no.a = 1;      // a fetch never carries it    delete o.a;\n", True),
    # ── let through: prose that mentions code ──
    ("JOIN-020", "a call named mid-sentence", ".py", PY_TOP + "# see check(ok, msg) for how a row reads, and why\n", False),
    ("JOIN-021", "a call with no arguments, after one space (how prose names a function)", ".py",
     PY_TOP + "# its failure counted. done() and on_failure()\n", False),
    ("JOIN-022", "a dotted name that is real code", ".py", PY_TOP + "# then harness.done()\n", False),
    ("JOIN-023", "a word that is a real name of the file, before its call", ".py",
     PY_TOP + "def environment():\n    pass\n# test/ui/harness.py: environment()\n", False),
    ("JOIN-024", "an address", ".py", PY_TOP + "# https://example.com/a?b=c(d)\n", False),
    ("JOIN-025", "a TODO line", ".py", PY_TOP + "# TODO 20261116-0900 - rerun it with page.reload()\n", False),
    ("JOIN-026", "commented-out code (the whole comment is code, written with a space after the marker)", ".py",
     PY_TOP + "# check(1 == 1, \"one\")\n#   x = f(1)\n", False),
    ("JOIN-027", "aligned columns of prose", ".py",
     PY_TOP + "#   Inbox: 22 New Arrival One        Fantasy (pinned): 5 Good Omens; The Test Saga: 1 2\n", False),
    ("JOIN-028", "two spaces after a sentence's dot", ".py", PY_TOP + "# One sentence.  Then check(x) runs here.\n", False),
    ("JOIN-029", "an aside in brackets after a word", ".py", PY_TOP + "# the Inbox (2 books)\n# the Inbox  (2 books)\n", False),
    ("JOIN-030", "a # inside a text is no comment", ".py", PY_TOP + "s = \"a  # b    check(1, 'x')\"\n", False),
    ("JOIN-031", "a usage example in a comment (JavaScript)", ".js",
     "// Usage in a test file:\n//   const { test, done } = require('./harness');\n//   done();\n", False),
    ("JOIN-032", "a // inside a text or a template is no comment", ".js",
     "const s = 'a // b    check(1);';\nconst t = `x // y    check(2);`;\n", False),
    ("JOIN-033", "a block comment (nothing joined into or after one is lost)", ".js",
     "/* note    check(1); */\nconst a = 1;\n", False),
    ("JOIN-034", "a label is prose (Note: …)", ".js", "//  Note: see the rows\n", False),
    # ── the marker ──
    ("JOIN-035", "allowed with its why on the line above", ".py",
     PY_TOP + "# not-joined: quotes the call a reader should copy\n# like this    check(x, \"y\")\n", False),
    ("JOIN-036", "allowed with its why on the same line", ".js",
     "// (not-joined: an example to copy) like    check(x, 'y');\n", False),
    ("JOIN-037", "a marker with no why is no marker", ".py", PY_TOP + "# not-joined:\n# x    check(1, \"a\")\n", True),
    ("JOIN-038", "a marker above a line of code doesn't reach past it", ".py",
     PY_TOP + "# not-joined: the one below\ny = 2\n# x    check(1, \"a\")\n", True),
]

found = cj.find_joined([(f"{tid}{ext}", src) for tid, _, ext, src, _ in ROWS])


def row_test(tid, what, ext, refused):
    def run():
        path = f"{tid}{ext}"
        hits = [j for j in found["joined"] if j["path"] == path]
        unread = [u for u in found["unparsed"] if u["path"] == path]
        check(not unread, f"the row's source must be readable: {unread}")
        if refused:
            check(hits, "PASSED — should be refused")
        else:
            check(not hits, f"REFUSED — should pass: {hits}")
    test(tid, what + (" — refused" if refused else " — passes"), run)


for tid, what, ext, _, refused in ROWS:
    row_test(tid, what, ext, refused)


def refusal_names_line():
    hit = [j for j in found["joined"] if j["path"] == "JOIN-002.py"]
    check(len(hit) == 1 and hit[0]["line"] == PY_TOP.count("\n") + 2 and hit[0]["code"] == 'check(ok, "holds")',
          f"one refusal, at the comment's line, quoting the joined code: {hit}")
test("JOIN-039", "a refusal names the file, the line and the joined code", refusal_names_line)


def unreadable_refused():
    f = cj.find_joined([("bad.py", "def f(:\n  # x    check(1)\n"), ("bad.js", "const = ;\n")])
    check({u["path"] for u in f["unparsed"]} == {"bad.py", "bad.js"}, f"both named as unreadable: {f['unparsed']}")
    check(cj.report(f) == 1, "a file the check couldn't read is refused, never passed")
test("JOIN-040", "a file the check can't read is refused (not passed unread)", unreadable_refused)


def real_alpha55_line():
    # The line as 7.18.0-alpha.52 left it in readerwrangler.js (fixed in alpha.55, caf705e) — the joined line kept here
    # as text, as an app line is no test file; the check reads JavaScript the same way.
    line = ("            const saveResultsBtnRef = useRef(null); // v7.18.0-alpha.49 - anchor (\"💾 N results · Save ▾\") "
            "for its <Popover>            const shareBtnRef = useRef(null); // v7.18.0-alpha.49 - anchor (book dialog 📤) "
            "for the Share <Popover>\n")
    f = cj.find_joined([("test/alpha55.test.js", line)])
    check([j["code"].startswith("const shareBtnRef = useRef(null);") for j in f["joined"]] == [True],
          f"the joined declaration is named: {f['joined']}")
test("JOIN-041", "the real case: alpha.55's joined declaration is refused", real_alpha55_line)


def planted_in_real_file():
    # A row of test/test_check_parse.py's table joined onto the row above's note — that row would silently stop running.
    with open(os.path.join(ROOT, "test", "test_check_parse.py"), encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    at = next(i for i, ln in enumerate(lines) if ln.startswith('    ("PARSE-003"'))
    check("#" in lines[at] and lines[at + 1].startswith('    ("PARSE-004"'), "the planted spot: PARSE-003's note, then 004")
    planted = lines[:at] + [lines[at] + lines[at + 1]] + lines[at + 2:]
    f = cj.find_joined([("test/test_check_parse.py", "\n".join(planted))])
    check([(j["line"], j["code"][:12]) for j in f["joined"]] == [(at + 1, '("PARSE-004"')],
          f"refused at line {at + 1}, naming PARSE-004's row: {f['joined']}")
test("JOIN-042", "a row of a real test file's table, joined onto the note above, is refused at its line",
     planted_in_real_file)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def staged_copy_checked():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}   # a hook's GIT_DIR must not leak in
    script = os.path.join(ROOT, "git-hooks", "check-joined.py")
    with tempfile.TemporaryDirectory() as repo:
        def run():
            return subprocess.run([sys.executable, script], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", env=env)
        subprocess.run(["git", "init", "-q"], cwd=repo, env=env)
        os.makedirs(os.path.join(repo, "test"))
        os.makedirs(os.path.join(repo, "tools"))
        joined = "x = 1   # the count    assert x == 1\n"
        clean = "x = 1   # the count\nassert x == 1\n"
        path = os.path.join(repo, "test", "test_t.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(joined)
        subprocess.run(["git", "add", "test/test_t.py"], cwd=repo, env=env)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(clean)                                            # fixed on disk, NOT staged
        r = run()
        check(r.returncode == 1 and "test/test_t.py:1" in r.stderr, f"the staged copy is refused: {r.returncode} {r.stderr}")
        subprocess.run(["git", "add", "test/test_t.py"], cwd=repo, env=env)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(joined)                                           # broken on disk, the clean copy staged
        r = run()
        check(r.returncode == 0, f"the staged (clean) copy passes: {r.returncode} {r.stderr}")
        with open(os.path.join(repo, "tools", "t.py"), "w", encoding="utf-8") as fh:
            fh.write(joined)
        subprocess.run(["git", "add", "tools/t.py"], cwd=repo, env=env)
        r = run()
        check(r.returncode == 0, f"a file outside the tests isn't this check's: {r.returncode} {r.stderr}")
test("JOIN-043", "checks the STAGED copy of staged test files only", staged_copy_checked)


def scope():
    yes = ["test/test_x.py", "test/ui/test_x.py", "test/harness.js", "test/x.test.js", "test/fixtures/make.js",
           "test/x.mjs", "relay/test-phase1.mjs"]
    no = ["tools/run_tests.py", "relay/relay-worker.js", "readerwrangler.js", "test/fixtures/small.json", "git-hooks/x.py"]
    check(all(cj.in_scope(p) for p in yes) and not any(cj.in_scope(p) for p in no),
          f"in: {[p for p in yes if not cj.in_scope(p)]} wrongly out; {[p for p in no if cj.in_scope(p)]} wrongly in")
test("JOIN-044", "the test files are its scope: test/**/*.py, *.js, *.mjs and relay/test-*.mjs", scope)


def library_today():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "git-hooks", "check-joined.py"), "--all"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    check(r.returncode == 0 and "No joined lines." in r.stdout, f"--all passes today's library:\n{r.stdout}{r.stderr}")
    counts = [int(w) for w in r.stdout.split("check-joined:", 1)[1].split()[:6] if w.isdigit()]
    check(counts and counts[0] >= 60, f"it scanned the whole library (60+ files): {r.stdout.splitlines()[:1]}")
test("JOIN-045", "--all: every test file in the repo, as staged, passes today", library_today)

done()
