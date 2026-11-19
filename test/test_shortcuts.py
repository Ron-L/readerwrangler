# Tests for tools/shortcuts.py — the "open" shortcut (TODO "The 'open' shortcut: start serve.py if needed and open the
# app"; sprint 9). The shortcut runs `serve.py --open` (what that does: test/test_serve.py SERVE-003–007).
# tags: tooling, tier 1
# covers: tools/shortcuts.py
# Run: python test/test_shortcuts.py
#
# Never on Ron's real Start menu or Desktop, and nothing is ever launched: every shortcut here is written into a
# temporary folder and read back (Windows' own shortcut reader, through PowerShell — reading opens no window).
# Never a git command on any repository but the temporary ones made here (2026-11-18 — see below).
import json
import os
import subprocess
import sys
import tempfile

# NEVER inherit git's own variables (2026-11-18, sprint 9 — a real incident): while the commit hook runs this test,
# GIT_DIR / GIT_INDEX_FILE point at the REAL repository's git folder, and a git command here would act on it (a `git
# init` in another test wrote core.bare = true into the real shared config). Removed before anything else runs.
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import shortcuts   # noqa: E402


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


# A temporary project: a "main folder" repository and a working copy of it (a git worktree, as tools/copies.py makes).
_TMP = tempfile.TemporaryDirectory(prefix="rw-shortcut-project-")
MAIN = os.path.join(_TMP.name, "Main Folder")             # a space: the shortcut's paths must be quoted
COPY = os.path.join(_TMP.name, "copies", "a-copy")
git(_TMP.name, "init", "-q", "-b", "main", MAIN)
git(MAIN, "config", "user.name", "Test")
git(MAIN, "config", "user.email", "test@example.com")
with open(os.path.join(MAIN, "serve.py"), "w") as _f:
    _f.write("# stand-in\n")
git(MAIN, "add", "serve.py")
git(MAIN, "commit", "-q", "-m", "start")
git(MAIN, "worktree", "add", "-q", "-b", "a-copy", COPY)


def read_back(lnk):
    ps = ("$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:LNK); "
          "@{target=$s.TargetPath; args=$s.Arguments; dir=$s.WorkingDirectory; icon=$s.IconLocation; "
          "desc=$s.Description} | ConvertTo-Json -Compress")
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], env=dict(os.environ, LNK=lnk),
                       capture_output=True, text=True, timeout=60, check=True)
    return json.loads(r.stdout)


def same(a, b):
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def written_and_read_back():
    if os.name != "nt":
        return
    with tempfile.TemporaryDirectory(prefix="rw-shortcut-") as tmp:
        lnk = shortcuts.write(tmp, python=r"C:\Python\python.exe", root=MAIN)
        check(os.listdir(tmp) == [shortcuts.NAME + ".lnk"], f"one shortcut, named {shortcuts.NAME!r}: {os.listdir(tmp)}")
        check(same(lnk, os.path.join(tmp, shortcuts.NAME + ".lnk")), f"its path is returned: {lnk}")
        s = read_back(lnk)
        check(same(s["target"], r"C:\Python\python.exe"), f"it runs the Python given: {s}")
        serve = os.path.normpath(os.path.join(MAIN, "serve.py"))
        check(os.path.normcase(s["args"]) == os.path.normcase(f'"{serve}" --open'),
              f"serve.py --open, path quoted: {s['args']!r}")
        check(same(s["dir"], MAIN), f"in the project folder: {s['dir']}")
        check(s["icon"].lower().startswith(os.path.normpath(os.path.join(MAIN, "icons", "favicon.ico")).lower()),
              f"with the app's icon: {s['icon']}")
        check("starts" in s["desc"] and "isn't running" in s["desc"], f"its tip says what it does: {s['desc']!r}")
        shortcuts.write(tmp, python=r"C:\Python\python.exe", root=MAIN)
        check(os.listdir(tmp) == [shortcuts.NAME + ".lnk"], "written again: still one (rewriting is harmless)")
test("SHORTCUT-001", "the shortcut runs `serve.py --open` with the Python given, in the project folder, with the app's "
     "icon — written into the folder asked for; rewriting it is harmless", written_and_read_back)


def main_folder_from_a_copy():
    """Run in a working copy, the shortcut still points at the MAIN folder — a copy is removed when its task is done,
    and a shortcut into it would break. (A temporary main folder and copy.)"""
    if os.name != "nt":
        return
    check(same(shortcuts.project_folder(COPY), MAIN), f"project_folder(copy) is the main folder: "
                                                     f"{shortcuts.project_folder(COPY)}")
    with tempfile.TemporaryDirectory(prefix="rw-shortcut-") as tmp:
        s = read_back(shortcuts.write(tmp, python=r"C:\Python\python.exe", root=COPY))
    check(same(s["dir"], MAIN) and os.path.normcase(os.path.normpath(os.path.join(MAIN, "serve.py")))
          in os.path.normcase(s["args"]), f"the shortcut written from the copy points at the main folder: {s}")
test("SHORTCUT-002", "from a working copy, the shortcut still points at the main folder (copies.main_folder)",
     main_folder_from_a_copy)


def where_by_default():
    env = {"APPDATA": r"C:\Users\Someone\AppData\Roaming"}
    check(same(shortcuts.start_menu(env), r"C:\Users\Someone\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
          f"the Start menu's programs folder (Windows search finds it): {shortcuts.start_menu(env)}")
    seen = []
    real = shortcuts.make_shortcut
    shortcuts.make_shortcut = lambda lnk, target, args, workdir, icon, description: seen.append((lnk, target))
    try:
        rc = shortcuts.main([], environ=env, root=COPY)
    finally:
        shortcuts.make_shortcut = real
    check(rc == 0 and len(seen) == 1, f"main() with no arguments writes one shortcut: {seen}")
    check(same(os.path.dirname(seen[0][0]), shortcuts.start_menu(env)) and same(seen[0][1], shortcuts.default_python()),
          f"into the Start menu, running the default Python: {seen}")
    py = shortcuts.default_python(which=lambda name: r"C:\Launcher\py.exe" if name == "py" else None)
    check(py == r"C:\Launcher\py.exe", f"the py launcher when there is one (survives a Python upgrade): {py}")
    py = shortcuts.default_python(which=lambda name: None)
    check(py == sys.executable, f"else the Python running the tool: {py}")
test("SHORTCUT-003", "by default: the Start menu's programs folder (Windows search), and the py launcher (else the Python "
     "running the tool) — nothing written here, the shortcut maker is a stand-in", where_by_default)

try:
    git(MAIN, "worktree", "remove", "--force", COPY)      # the temporary copy only, then the temporary folder
except subprocess.CalledProcessError:
    pass
try:
    _TMP.cleanup()
except OSError:
    pass
done()
