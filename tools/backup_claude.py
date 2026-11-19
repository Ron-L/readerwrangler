#!/usr/bin/env python3
"""
backup_claude.py — Claude's memory and settings back themselves up (TODO "Working-process safety net", items 2 and 3;
decided Ron + UX 2026-10-22, built sprint 9, 2026-11-18). A release-checklist step, so the backup is never more than one
release behind (the by-hand backup slipped a week: Oct 15 → 22, 56 files backed up of 68, 18 differing). Not a
per-turn hook: a commit per turn is noise.

What it copies — the pieces of the working process that live OUTSIDE the ReaderWrangler repository:
  1. Claude's memory for this project  ~\\.claude\\projects\\<the project's folder name>\\memory\\*.md
     → .private\\claude-backup\\memory\\  — a MIRROR: a memory file deleted is deleted in the backup too (git's history
     still holds it). Only .md files; anything else in either folder is left alone. An empty or missing memory folder
     is refused, so the backup is never emptied by mistake.
  2. ReaderWrangler\\.claude\\settings.local.json → .private\\claude-backup\\settings.local.json
  3. Claude Code's global settings  ~\\.claude\\settings.json (it wires the timestamp hook; no secrets, but personal
     paths) → the Projects repository (C:\\Users\\Ron\\Projects — private, Ron-L/projects-root) as claude-settings.json,
     beside stamp.py and CLAUDE-TOOLING.md ("claude-" so it sorts with CLAUDE.md and says whose settings it is — a bare
     settings.json at the Projects root would read as the folder's own). That repository's .gitignore is an allow-list:
     the first run adds "!/claude-settings.json", or git would never see the copy.
Then each repository (.private and Projects) is committed — ONLY the backup's files (anything else Ron has staged or
left untracked there stays as it is) — and pushed to origin. Nothing changed → no commit. A push the remote refuses
(it has commits this PC doesn't) is said loudly, the commit kept; never forced.

It finds the MAIN project folder even when run from a working copy (tools/copies.py's main_folder); the memory folder's
name comes from that path, as Claude Code names it (every character but a letter or digit → "-", any case).

    py tools\\backup_claude.py      (double-clicking works too; exit 1 if anything failed)

Tested by test/test_backup_claude.py (CBAK-001–007) — throwaway repositories with local stand-ins for GitHub.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import copies  # noqa: E402  (main_folder: the one way to find the main folder from a working copy)
import whole_file  # noqa: E402  (the one way to write a file whole — Law 22)

BACKUP_DIR = "claude-backup"
GLOBAL_COPY = "claude-settings.json"
REMOTE = "origin"


class BackupError(Exception):
    pass


def project_folder(root=ROOT):
    """The main project folder of the copy `root` — never a working copy. (`root`: the tests use a temporary one.)"""
    return copies.main_folder(root)


def memory_folder(main, home):
    """Claude Code's memory folder for the project at `main`, or None. Claude Code names the folder after the project's
    path, every character but a letter or digit made "-" ("c--Users-Ron-Projects-ReaderWrangler"); the drive letter's
    case follows how the path was given, so it's matched in any case."""
    want = re.sub(r"[^A-Za-z0-9]", "-", os.path.normpath(main)).lower()
    projects = os.path.join(home, ".claude", "projects")
    try:
        names = os.listdir(projects)
    except OSError:
        return None
    for name in names:
        if name.lower() == want:
            return os.path.join(projects, name, "memory")
    return None


def default_paths(main, home):
    memory = memory_folder(main, home) or os.path.join(home, ".claude", "projects",
                                                       re.sub(r"[^A-Za-z0-9]", "-", os.path.normpath(main)), "memory")
    return dict(memory=memory,
                local_settings=os.path.join(main, ".claude", "settings.local.json"),
                global_settings=os.path.join(home, ".claude", "settings.json"),
                private_repo=os.path.join(main, ".private"),
                projects_repo=os.path.dirname(os.path.normpath(main)))


def git(repo, *args):
    # git's own variables (GIT_DIR…, set while a git hook runs) would point every command at THAT repository
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env)


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def copy_file(src, dst):
    """Copy src over dst when they differ: "added", "updated" or None (the same already)."""
    data = read_bytes(src)
    if not os.path.exists(dst):
        whole_file.write(dst, data)
        return "added"
    if read_bytes(dst) == data:
        return None
    whole_file.write(dst, data)
    return "updated"


def mirror(src, dst):
    """dst's .md files made exactly src's: {"added": [...], "updated": [...], "removed": [...]}."""
    if not os.path.isdir(src):
        raise BackupError(f"the memory folder isn't there: {src} - nothing backed up (the backup is never emptied)")
    names = sorted(n for n in os.listdir(src) if n.endswith(".md") and os.path.isfile(os.path.join(src, n)))
    if not names:
        raise BackupError(f"{src} has no memory files - refused, so the backup is never emptied by mistake")
    out = {"added": [], "updated": [], "removed": []}
    for n in names:
        what = copy_file(os.path.join(src, n), os.path.join(dst, n))
        if what:
            out[what].append(n)
    for n in sorted(os.listdir(dst)):
        if n.endswith(".md") and n not in names and os.path.isfile(os.path.join(dst, n)):
            os.remove(os.path.join(dst, n))
            out["removed"].append(n)
    return out


def allow(repo, rel):
    """Make sure the repository's .gitignore lets `rel` in (an allow-list ignores everything else). True if added."""
    if git(repo, "check-ignore", "-q", "--", rel).returncode != 0:
        return False
    path = os.path.join(repo, ".gitignore")
    text = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    text += ("" if not text or text.endswith("\n") else "\n") + \
        "# Claude Code's global settings (~/.claude/settings.json), copied by ReaderWrangler's tools/backup_claude.py\n" \
        f"!/{rel}\n"
    whole_file.write(path, text, newline="\n")
    if git(repo, "check-ignore", "-q", "--", rel).returncode == 0:
        raise BackupError(f"{repo}: added \"!/{rel}\" to .gitignore, but git still ignores {rel} - look at .gitignore")
    return True


def commit_and_push(repo, paths, message):
    """Commit `paths` only (anything else staged or untracked is left as it is), then push to origin when ahead. Lines
    to report; raises BackupError when something failed. `message` may be a function of what git staged — [(status
    letter, path)] — so the commit says what git saw: with core.autocrlf a copy can differ in line endings from the
    checked-out file while git sees no change."""
    lines = []
    r = git(repo, "add", "-A", "--", *paths)
    if r.returncode != 0:
        raise BackupError(f"{repo}: git add failed - {r.stderr.strip()}")
    staged = [ln.split("\t", 1) for ln in git(repo, "diff", "--cached", "--name-status", "--", *paths).stdout.splitlines()
              if "\t" in ln]
    if staged:
        message = message(staged) if callable(message) else message
        r = git(repo, "commit", "-q", "-m", message, "--", *paths)
        if r.returncode != 0:
            raise BackupError(f"{repo}: the commit failed - {(r.stderr or r.stdout).strip()}")
        lines.append(f"  committed {git(repo, 'rev-parse', '--short', 'HEAD').stdout.strip()}: {message}")
    else:
        lines.append("  nothing changed - no commit")
    branch = git(repo, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip()
    if not branch:
        raise BackupError(f"{repo}: not on a branch - not pushed")
    ahead = git(repo, "rev-list", "--count", f"{REMOTE}/{branch}..HEAD")
    if ahead.returncode == 0 and ahead.stdout.strip() == "0":
        return lines
    r = git(repo, "push", REMOTE, branch)
    if r.returncode != 0:
        raise BackupError(f"{repo}: PUSH FAILED (the commit is kept here; nothing was forced) - "
                          f"{r.stderr.strip()[-400:]}")
    lines.append(f"  pushed to {REMOTE}/{branch}")
    return lines


def is_repo_top(path):
    r = git(path, "rev-parse", "--show-toplevel") if os.path.isdir(path) else None
    return bool(r and r.returncode == 0 and
                os.path.normcase(os.path.normpath(r.stdout.strip())) == os.path.normcase(os.path.normpath(path)))


def backup_private(memory, local_settings, private_repo):
    lines = [f"Private notes ({private_repo}):"]
    if not is_repo_top(private_repo):
        raise BackupError(f"{private_repo} isn't a git repository - nothing backed up there")
    dst = os.path.join(private_repo, BACKUP_DIR)
    m = mirror(memory, os.path.join(dst, "memory"))
    parts = [f"{len(m[k])} {k}" for k in ("added", "updated", "removed") if m[k]]
    lines.append(f"  memory from {memory}: copied " + (", ".join(parts) if parts else "nothing (the same)"))
    if m["removed"]:
        lines.append("  removed (deleted from memory; git's history keeps them): " + ", ".join(m["removed"]))
    paths = [f"{BACKUP_DIR}/memory"]
    if os.path.isfile(local_settings):
        what = copy_file(local_settings, os.path.join(dst, "settings.local.json"))
        lines.append(f"  settings.local.json: {what or 'the same'}")
        paths.append(f"{BACKUP_DIR}/settings.local.json")
    else:
        lines.append(f"  NOTE: {local_settings} isn't there - not backed up")
    lines += commit_and_push(private_repo, paths, private_message)
    return lines


def private_message(staged):
    """The private repo's commit message, from what git staged."""
    words = {"A": "added", "M": "updated", "D": "removed"}
    memory = [s[0] for s, p in staged if p.startswith(f"{BACKUP_DIR}/memory/")]
    parts = [f"{memory.count(k)} {w}" for k, w in words.items() if memory.count(k)]
    other = [p.rsplit("/", 1)[-1] for _s, p in staged if not p.startswith(f"{BACKUP_DIR}/memory/")]
    return ("Claude backup (ReaderWrangler tools/backup_claude.py): memory - " + (", ".join(parts) or "no change")
            + "".join(f"; {name} updated" for name in other))


def backup_global(global_settings, projects_repo):
    lines = [f"Projects ({projects_repo}):"]
    if not is_repo_top(projects_repo):
        raise BackupError(f"{projects_repo} isn't a git repository - the global settings aren't backed up")
    if not os.path.isfile(global_settings):
        lines.append(f"  NOTE: {global_settings} isn't there - not backed up")
        return lines
    what = copy_file(global_settings, os.path.join(projects_repo, GLOBAL_COPY))
    lines.append(f"  {GLOBAL_COPY} (from {global_settings}): {what or 'the same'}")
    paths = [GLOBAL_COPY]
    if allow(projects_repo, GLOBAL_COPY):
        lines.append(f"  .gitignore: added \"!/{GLOBAL_COPY}\" (the allow-list lets it in)")
        paths.append(".gitignore")
    lines += commit_and_push(projects_repo, paths,
                             f"Back up Claude Code's global settings ({GLOBAL_COPY}; ReaderWrangler "
                             "tools/backup_claude.py)")
    return lines


def backup(memory, local_settings, global_settings, private_repo, projects_repo):
    """Both repositories, each on its own (one failing doesn't stop the other). (lines, ok)."""
    lines, ok = [], True
    for step in (lambda: backup_private(memory, local_settings, private_repo),
                 lambda: backup_global(global_settings, projects_repo)):
        try:
            lines += step()
        except BackupError as e:
            lines.append(f"  FAILED: {e}")
            ok = False
    return lines, ok


def main():
    paths = default_paths(project_folder(), os.path.expanduser("~"))
    lines, ok = backup(**paths)
    print("\n".join(lines))
    print("Backed up." if ok else "\nSOMETHING FAILED - see FAILED above.")
    return 0 if ok else 1


if __name__ == "__main__":
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)   # the pytools submodule is at the project root
    try:
        from pytools.keepopen import run
    except ImportError:
        print("backup_claude.py needs the pytools submodule. In the project folder run:\n"
              "    git submodule update --init\n"
              "then start it again.", file=sys.stderr)
        try:
            input("\nPress Enter to close this window.")
        except (EOFError, KeyboardInterrupt):   # no keyboard (run by another tool) — just exit
            pass
        sys.exit(1)
    run(main, pause="always")
