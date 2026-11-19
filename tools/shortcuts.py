#!/usr/bin/env python3
"""
shortcuts.py — (re)write ReaderWrangler's "open" shortcut (TODO "The 'open' shortcut: start serve.py if needed and open
the app"; decided Ron + Claude 2026-10-31, built sprint 9, 2026-11-18 — adapted from the utilities project's
tools/shortcuts.py):

    Start Menu\\Programs\\ReaderWrangler (local).lnk   serve.py --open   (Windows search: type "ReaderWrangler")

One click opens ReaderWrangler's page (http://localhost:8000/readerwrangler.html) in the default browser — a browser
TAB, not an app window: the bookmarklets live on the bookmarks bar. If serve.py isn't running, it's started first, in
its own window (that window is the server, as when Startup starts it); if it is, the page just opens. The open half
only: no restart or shutdown (serve.py's top says why). Named "(local)" so Windows search tells it apart from the site.

It points at the MAIN project folder (tools/copies.py's main_folder) even when run from a working copy — a copy is
removed when its task is done. It runs the py launcher (as Ron's own serve.py shortcuts do — it survives a Python
upgrade), or the Python running this tool when there's no launcher. Rewriting the shortcut is harmless. Ron's
"ReaderWrangler Server" shortcuts (Start menu + Startup, made by hand — they start the server without opening the page)
are left as they are.

    py tools\\shortcuts.py                     write it into the Start menu (double-clicking works too)
    py tools\\shortcuts.py --folder <folder>   write it there instead (the tests use a temporary folder)

Tested by test/test_shortcuts.py (SHORTCUT-001–003); what --open does: test/test_serve.py (SERVE-003–007).
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import copies  # noqa: E402  (main_folder: the one way to find the main folder from a working copy)

NAME = "ReaderWrangler (local)"
DESCRIPTION = "Opens ReaderWrangler on this PC (starts its local server first if it isn't running)"


def project_folder():
    """The main project folder — never a working copy."""
    return copies.main_folder(ROOT)


def start_menu(environ=None):
    """The Start menu's programs folder — where Windows search finds a shortcut."""
    env = os.environ if environ is None else environ
    return os.path.join(env["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")


def make_shortcut(lnk, target, args, workdir, icon, description):
    # Windows' own shortcut maker (WScript.Shell) through PowerShell — no extra packages, no window. Values go in through
    # environment variables, so paths with spaces or quotes need no escaping.
    ps = ("$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:LNK); $s.TargetPath = $env:TARGET; "
          "$s.Arguments = $env:ARGS; $s.WorkingDirectory = $env:WORKDIR; $s.IconLocation = $env:ICON; "
          "$s.Description = $env:DESC; $s.Save()")
    env = dict(os.environ, LNK=lnk, TARGET=target, ARGS=args, WORKDIR=workdir, ICON=icon, DESC=description)
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], env=env, check=True,
                   capture_output=True, text=True)


def default_python(which=shutil.which):
    """The py launcher when there is one — as Ron's own serve.py shortcuts (Start menu + Startup, "ReaderWrangler
    Server", made by hand 2026-10-16) — it survives a Python upgrade; else the Python running this."""
    return which("py") or sys.executable


def write(folder, python=None):
    """Write the shortcut into `folder` (an existing folder); its path."""
    main = project_folder()
    lnk = os.path.join(folder, NAME + ".lnk")
    make_shortcut(lnk, python or default_python(), f'"{os.path.join(main, "serve.py")}" --open', main,
                  os.path.join(main, "icons", "favicon.ico") + ",0", DESCRIPTION)
    return lnk


def main(argv=None, environ=None):
    ap = argparse.ArgumentParser(description="Write ReaderWrangler's \"open\" shortcut (Start menu by default).")
    ap.add_argument("--folder", help="write it here instead of the Start menu")
    a = ap.parse_args(argv)
    if os.name != "nt":
        sys.exit("shortcuts.py makes Windows shortcuts; elsewhere run:  python serve.py --open")
    folder = a.folder or start_menu(environ)
    python = default_python()
    lnk = write(folder, python)
    print(f"{lnk}\n    runs {python} \"{os.path.join(project_folder(), 'serve.py')}\" --open\n"
          f"    (opens the page; starts serve.py first if it isn't running)")
    return 0


if __name__ == "__main__":
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)   # the pytools submodule is at the project root
    try:
        from pytools.keepopen import run
    except ImportError:
        print("shortcuts.py needs the pytools submodule. In the project folder run:\n"
              "    git submodule update --init\n"
              "then start it again.", file=sys.stderr)
        try:
            input("\nPress Enter to close this window.")
        except (EOFError, KeyboardInterrupt):   # no keyboard (run by another tool) — just exit
            pass
        sys.exit(1)
    run(main, pause="always")
