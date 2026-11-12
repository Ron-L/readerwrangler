# Tests for git-hooks/shipped_paths.py — the ONE answer to "is this file part of what we ship?"
# tags: commit-checks, build, tier 1
# covers: git-hooks/shipped_paths.py, tools/build.py, .claude/hooks/gate-check.py, git-hooks/version-guard.py
# Run: python test/test_shipped_paths.py
#
# 2026-11-11 ("Logging as its own module" — logger.js moves into logkit/): three tools each had their own rule — the
# pre-build gate (".js at the root + the relay worker"), the version guard (a list of folders that aren't shipped), the
# style build (root pages and scripts only) — so code in a new folder would silently skip the gate and lose its styles.
# Now one rule, in one file, that all three use: shipped = everything except the listed non-shipped folders.
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sp = load("shipped_paths", "git-hooks/shipped_paths.py")
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402


def the_rule():
    yes = ["readerwrangler.js", "storage.js", "reset.html", "logkit/logger.js", "logkit/diagnostics-window.js",
           "relay/relay-worker.js", "a-new-folder/module.js"]
    no = ["test/ui/rw.py", "test/logger.test.js", "tools/build.py", "tools/build/compile.js", "git-hooks/pre-commit",
          "docs/design/LOGGING.md", "v4/readerwrangler.js", ".claude/hooks/gate-check.py", ".private/x.js",
          "pytools/keepopen.py", "post-mortems/x.md", "dist/readerwrangler.js", "tools/build/node_modules/x/y.js"]
    wrong = [p for p in yes if not sp.is_shipped_source(p)] + [p for p in no if sp.is_shipped_source(p)]
    check(not wrong, f"misjudged: {wrong}")
test("SHIP-001", "shipped source = everything outside the non-shipped folders (a new folder is covered), never dist/",
     the_rule)


def the_gate_uses_it():
    gate = load("gate_check", ".claude/hooks/gate-check.py")
    rel = lambda p: os.path.join(ROOT, p)   # noqa: E731
    check(gate.is_app_source(rel("logkit/logger.js")), "the pre-build gate covers code in logkit/")
    check(gate.is_app_source(rel("readerwrangler.js")) and gate.is_app_source(rel("relay/relay-worker.js")),
          "…and still the root scripts and the relay worker")
    check(not gate.is_app_source(rel("test/ui/rw.py")) and not gate.is_app_source(rel("dist/readerwrangler.js")),
          "…and not tests or the built copies")
test("SHIP-002", "the pre-build gate asks the shared rule — code in a new folder can't skip it", the_gate_uses_it)


def the_style_build_uses_it():
    b = load("build", "tools/build.py")
    got = b.style_sources(["readerwrangler.html", "logkit/diagnostics-window.js", "logkit/README.md", "test/x.js",
                           "dist/readerwrangler.js", "tools/build/compile.js", "storage.js"])
    check(got == ["logkit/diagnostics-window.js", "readerwrangler.html", "storage.js"],
          f"the styles are read from every shipped page and script, folders included: {got}")
test("SHIP-003", "the style build reads every shipped page and script — a window in logkit/ keeps its styles",
     the_style_build_uses_it)

done()
