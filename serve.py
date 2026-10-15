#!/usr/bin/env python3
"""
serve.py — ReaderWrangler's local development server (2026-10-15).

Python's standard web server, with the one difference that matters: it serves only what the real site serves.
Production (GitHub Pages) publishes exactly the files in git and never lists folders, so this server refuses:

  1. any path with a part starting with a dot   (.private/ — secrets; .git/; .claude/; .vscode/ …)
  2. anything git ignores                       (readerwrangler-backup-*.json — they hold relay credentials; scratch files)
  3. folder listings                            (a folder with an index.html still shows that page)

Refused paths get a plain 404, as if they didn't exist.

It listens on the whole home network ON PURPOSE (a phone tests your local copy over Wi-Fi) — which is exactly why it
must not hand out private files to every device on that network. Same address and port as before
(http://localhost:8000), so everything the browser stores for ReaderWrangler stays put.

Usage:  py serve.py [port]        (default 8000; Windows: double-click start-server.bat)
        python serve.py [port]    (elsewhere)
Needs git on the PATH (it asks git what's ignored); exits with a clear message if git isn't there.
"""
import functools
import http.server
import os
import posixpath
import subprocess
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


def git_available():
    try:
        r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0 and r.stdout.strip() == "true"
    except (OSError, subprocess.TimeoutExpired):
        return False


@functools.lru_cache(maxsize=4096)
def git_ignores(rel_path):
    """True if git ignores this repo-relative path. Cached: a page load asks about the same ~30 files repeatedly."""
    r = subprocess.run(["git", "check-ignore", "-q", "--", rel_path], cwd=ROOT,
                       capture_output=True, timeout=10)
    return r.returncode == 0  # 0 = ignored, 1 = not ignored


def refusal_reason(url_path):
    """Why this request must be refused, or None if it may be served."""
    path = urllib.parse.unquote(urllib.parse.urlsplit(url_path).path)
    norm = posixpath.normpath("/" + path.lstrip("/"))       # collapses ./ and ../ before we judge it
    parts = [p for p in norm.split("/") if p]
    if any(p.startswith(".") for p in parts):
        return "private (dot) folder or file"
    rel = "/".join(parts)
    if rel and git_ignores(rel):
        return "kept out of git (not part of the site)"
    return None


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_head(self):
        reason = refusal_reason(self.path)
        if reason:
            self.log_message("REFUSED %s - %s", self.path, reason)  # plain hyphen: a Windows console garbles "—"
            self.send_error(404, "File not found")
            return None
        return super().send_head()

    def list_directory(self, path):
        # Production never lists folders; a folder with an index.html never gets here (send_head serves the page).
        self.send_error(404, "File not found")
        return None


def main():
    if not git_available():
        sys.exit("serve.py: git isn't available here, so it can't tell which files are private.\n"
                 "Install git (or run this from inside the cloned repo) and start it again.")
    server = http.server.ThreadingHTTPServer(("", PORT), Handler)
    print(f"ReaderWrangler local server: http://localhost:{PORT}/readerwrangler.html")
    print("Serving only what the real site serves (no dot-folders, nothing git ignores, no folder listings).")
    print("Close this window (or press Ctrl+C) to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
