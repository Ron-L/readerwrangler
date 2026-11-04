# Tests for tools/run_tests.py — the one test runner (docs/design/TESTING.md §4).
# tags: test-runner, tier 1
# covers: tools/run_tests.py, test/harness.js
# Run: python test/test_run_tests.py
#
# Sample test files are written to a temporary folder; each row checks one thing the runner must do.
import importlib.util
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("run_tests", os.path.join(ROOT, "tools", "run_tests.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

HARNESS = os.path.join(ROOT, "test", "harness.js").replace("\\", "/")
results = []


def row(tid, name, ok, detail=""):
    results.append((tid, name, ok, detail))
    print(f"  {'✓' if ok else '✗'} {tid} {name}" + ("" if ok else f" — {detail}"))


with tempfile.TemporaryDirectory() as d:
    def write(name, text):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    js_ok = write("a.test.js", f"""// sample
// tags: merge, import, tier 1
// covers: bookMerge.js, storage.js
const {{ test, done }} = require('{HARNESS}');
test('SAMPLE-001', 'passes', () => {{}});
done();
""")
    js_bad = write("b.test.js", f"""// sample
// tags: dates, tier 1
// covers: uiHelpers.js
const {{ test, done }} = require('{HARNESS}');
test('SAMPLE-002', 'fails', () => {{ throw new Error('boom'); }});
test('SAMPLE-003', 'still runs after a failure', () => {{}});
done();
""")
    py_ok = write("test_c.py", """# sample
# tags: commit-checks, tier 1
# covers: git-hooks/check-parse.py
print("1 passed, 0 failed")
""")
    no_header = write("d.test.js", "// no header at all\nconsole.log('hi');\n")
    ui = write("test_e.py", "# sample\n# tags: delete-key, tier 2\n# covers: readerwrangler.js\n")

    h = rt.read_header(js_ok)
    row("RUN-001", "reads tags, tier and covers from a // header",
        h["tags"] == ["merge", "import"] and h["tier"] == 1 and h["covers"] == ["bookMerge.js", "storage.js"], str(h))
    h = rt.read_header(py_ok)
    row("RUN-002", "reads a # header (Python files)",
        h["tags"] == ["commit-checks"] and h["tier"] == 1 and h["covers"] == ["git-hooks/check-parse.py"], str(h))
    h = rt.read_header(no_header)
    row("RUN-003", "a file with no header is reported as missing one (headers are required)",
        h["problem"] is not None, str(h))

    files = [rt.TestFile(p) for p in (js_ok, js_bad, py_ok, ui)]
    def pick(**kw):
        return sorted(os.path.basename(f.path) for f in rt.select(files, **kw))
    row("RUN-004", "--changed picks the tests that cover a changed file",
        pick(changed=["bookMerge.js"]) == ["a.test.js"], str(pick(changed=["bookMerge.js"])))
    row("RUN-005", "--changed picks nothing for a file no test covers",
        pick(changed=["readme.txt"]) == [], str(pick(changed=["readme.txt"])))
    own = [os.path.relpath(js_bad, d)]
    row("RUN-006", "--changed picks a test file that itself changed",
        pick(changed=own, base=d) == ["b.test.js"], str(pick(changed=own, base=d)))
    row("RUN-007", "--tag picks by area", pick(tags=["dates"]) == ["b.test.js"], str(pick(tags=["dates"])))
    row("RUN-008", "--tier 1 leaves out tier 2", pick(tier=1) == ["a.test.js", "b.test.js", "test_c.py"], str(pick(tier=1)))
    row("RUN-009", "--tier all keeps every tier", pick(tier="all") == ["a.test.js", "b.test.js", "test_c.py", "test_e.py"],
        str(pick(tier="all")))

    ok, out = rt.run_file(rt.TestFile(js_ok))
    row("RUN-010", "a passing JS file reports success", ok and "1 passed, 0 failed" in out, out[-200:])
    ok, out = rt.run_file(rt.TestFile(js_bad))
    row("RUN-011", "a failing JS file reports failure", not ok and "SAMPLE-002" in out, out[-200:])
    row("RUN-012", "a failure doesn't stop the file — the next test still ran", "SAMPLE-003" in out, out[-200:])
    ok, out = rt.run_file(rt.TestFile(py_ok))
    row("RUN-013", "a passing Python file reports success", ok, out[-200:])

    ui_py = write("test_f.py", "# sample\n# tags: screen, tier 2\n# covers: readerwrangler.js\n"
                               "import sys\nprint('ran with', sys.executable)\n")
    ok, out = rt.run_file(rt.TestFile(ui_py))
    row("RUN-014", "a screen test (tier 2) runs with the project's venv Python",
        ok and ".venv" in out.replace("\\", "/"), out[-200:])
    saved, rt.VENV_PY = rt.VENV_PY, os.path.join(d, "no-such-venv", "python.exe")
    ok, out = rt.run_file(rt.TestFile(ui_py))
    rt.VENV_PY = saved
    row("RUN-015", "no venv → the screen test fails loud with the setup command (never skipped quietly)",
        not ok and "py -m venv .venv" in out, out[-200:])

failed = [r for r in results if not r[2]]
print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
