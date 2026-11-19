# Tests for tools/shortcuts.py — the "open" shortcut (TODO "The 'open' shortcut: start serve.py if needed and open the
# app"; sprint 9). The shortcut runs `serve.py --open` (what that does: test/test_serve.py SERVE-003–007).
# tags: tooling, tier 1
# covers: tools/shortcuts.py
# Run: python test/test_shortcuts.py
#
# Never on Ron's real Start menu or Desktop, and nothing is ever launched: every shortcut here is written into a
# temporary folder and read back (Windows' own shortcut reader, through PowerShell — reading opens no window).
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import shortcuts   # noqa: E402
import copies   # noqa: E402

# git's own variables (GIT_DIR…) point git at THIS repository while the commit hook runs the test (as test_copies.py)
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]


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
    main = copies.main_folder(ROOT)
    with tempfile.TemporaryDirectory(prefix="rw-shortcut-") as tmp:
        lnk = shortcuts.write(tmp, python=r"C:\Python\python.exe")
        check(os.listdir(tmp) == [shortcuts.NAME + ".lnk"], f"one shortcut, named {shortcuts.NAME!r}: {os.listdir(tmp)}")
        check(same(lnk, os.path.join(tmp, shortcuts.NAME + ".lnk")), f"its path is returned: {lnk}")
        s = read_back(lnk)
        check(same(s["target"], r"C:\Python\python.exe"), f"it runs the Python given: {s}")
        check(s["args"] == f'"{os.path.join(main, "serve.py")}" --open', f"serve.py --open, path quoted: {s['args']!r}")
        check(same(s["dir"], main), f"in the project folder: {s['dir']}")
        check(s["icon"].lower().startswith(os.path.join(main, "icons", "favicon.ico").lower()),
              f"with the app's icon: {s['icon']}")
        check("starts" in s["desc"] and "isn't running" in s["desc"], f"its tip says what it does: {s['desc']!r}")
        shortcuts.write(tmp, python=r"C:\Python\python.exe")
        check(os.listdir(tmp) == [shortcuts.NAME + ".lnk"], "written again: still one (rewriting is harmless)")
test("SHORTCUT-001", "the shortcut runs `serve.py --open` with the Python given, in the project folder, with the app's "
     "icon — written into the folder asked for; rewriting it is harmless", written_and_read_back)


def main_folder_from_a_copy():
    """Run in a working copy (as this test may be), the shortcut still points at the MAIN folder — a copy is removed
    when its task is done, and a shortcut into it would break."""
    if os.name != "nt":
        return
    main = copies.main_folder(ROOT)
    with tempfile.TemporaryDirectory(prefix="rw-shortcut-") as tmp:
        s = read_back(shortcuts.write(tmp, python=r"C:\Python\python.exe"))
    check(same(s["dir"], main) and os.path.join(main, "serve.py") in s["args"], f"the main folder: {s}")
    check(shortcuts.project_folder() == main, f"project_folder() is copies.main_folder: {shortcuts.project_folder()}")
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
        rc = shortcuts.main([], environ=env)
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

done()
