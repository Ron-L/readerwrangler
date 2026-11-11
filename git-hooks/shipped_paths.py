"""shipped_paths.py — the ONE answer to "is this file part of what we ship?" (2026-11-11).

Three tools used to answer it three ways — the pre-build gate (".js at the root + the relay worker"), the version guard
(its own list of non-shipped folders), the style build (root pages and scripts only) — so code in a new folder (logkit/,
"Logging as its own module") would silently skip the gate and lose its styles. Now: shipped = everything OUTSIDE the
folders listed here, so a new folder is covered the day it's created. A RULE with one short list, in one place.

Used by git-hooks/version-guard.py, .claude/hooks/gate-check.py and tools/build.py. Tested by test/test_shipped_paths.py.
"""

# Folders that hold no shipped code (tools, tests, docs, history, the old v4 app). Anything else is shipped.
NOT_SHIPPED_DIRS = ("git-hooks/", "test/", "docs/", "v4/", "tools/", "pytools/", "post-mortems/")
BUILT_DIR = "dist/"            # shipped, but BUILT from the sources — never a source itself, never edited


def is_shipped(path):
    """Served to people (built copies included). path: repo-relative, forward slashes."""
    p = path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    if p.startswith(".") or "/." in p:                  # .claude/, .private/, .git/ … never shipped
        return False
    return not p.startswith(NOT_SHIPPED_DIRS)


def is_shipped_source(path):
    """A shipped page or script someone edits (not a built copy)."""
    p = path.replace("\\", "/")
    return is_shipped(p) and not p.startswith(BUILT_DIR)
