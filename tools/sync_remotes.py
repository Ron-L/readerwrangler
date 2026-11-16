#!/usr/bin/env python3
"""
sync_remotes.py — keep both GitHub repositories (dev and prod) holding every branch and tag this folder has
(Ron, 2026-11-16: "it is simpler to understand if both dev and prod match (except during a dev test) and both match the
local repo which has all the feature and sprint branches").

    py tools/sync_remotes.py            push what's missing or behind, then show what still differs
    py tools/sync_remotes.py --dry-run  show what it would push, push nothing

For every local branch and each remote:
    missing there              → pushed (a new branch)
    behind (local is ahead)    → pushed (a fast-forward)
    the same                   → nothing
    ahead or diverged there    → LEFT ALONE and listed — never overwritten, never forced (dev's main ahead of yours =
                                 a dev test in progress)
Every tag goes to both (git refuses to move a tag that differs — listed, never forced). Branches only on a remote are
listed, never deleted.

Never pushed by this script:
    main to prod — that DEPLOYS readerwrangler.com, so it stays an explicit `git push prod main --tags`, which always asks
                   Ron (.claude/settings.json). This script runs pre-approved, so it must not be a way around that.
    merging/*    — tools/merge_branches.py's scratch branches (it deletes them itself).

One push command per remote (all its refs at once), so a run is one or two pushes. Tested by test/test_sync_remotes.py.
"""
import argparse
import os
import subprocess
import sys

REMOTES = ("dev", "prod")
NEVER = {("prod", "main")}                 # (remote, branch) this script never pushes — main to prod deploys
SKIP_PREFIXES = ("merging/",)


def git(folder, *args, check=False):
    r = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed:\n{(r.stderr or r.stdout).strip()}")
    return r


def out(folder, *args):
    return git(folder, *args, check=True).stdout.strip()


def refs(folder, pattern):
    """{short name: commit} for refs under `pattern` (e.g. refs/heads/, refs/remotes/dev/)."""
    lines = out(folder, "for-each-ref", "--format=%(objectname) %(refname)", pattern).splitlines()
    res = {}
    for ln in lines:
        sha, name = ln.split(" ", 1)
        short = name[len(pattern):]
        if short != "HEAD":
            res[short] = sha
    return res


def is_ancestor(folder, a, b):
    return git(folder, "merge-base", "--is-ancestor", a, b).returncode == 0


def plan(folder, remote, local, there):
    """What to do with each branch for one remote: (to_push, same, left_alone, only_there, never)."""
    to_push, same, left, never = [], [], [], []
    for name, sha in sorted(local.items()):
        if name.startswith(SKIP_PREFIXES):
            continue
        if (remote, name) in NEVER:
            if there.get(name) != sha:
                never.append(name)
            continue
        theirs = there.get(name)
        if theirs is None:
            to_push.append((name, "new"))
        elif theirs == sha:
            same.append(name)
        elif is_ancestor(folder, theirs, sha):
            to_push.append((name, "ahead"))
        elif is_ancestor(folder, sha, theirs):
            left.append((name, f"{remote} is ahead of your branch"
                               + (" — a dev test in progress?" if (remote, name) == ("dev", "main") else "")))
        else:
            left.append((name, "the two have diverged"))
    only_there = sorted(n for n in there if n not in local)
    return to_push, same, left, only_there, never


def main(argv=None, folder=None):
    ap = argparse.ArgumentParser(description="Keep dev and prod holding every branch and tag this folder has.")
    ap.add_argument("--dry-run", action="store_true", help="show what would be pushed; push nothing")
    a = ap.parse_args(argv)
    folder = folder or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    remotes = [r for r in REMOTES if r in out(folder, "remote").split()]
    if not remotes:
        raise SystemExit(f"no remote named {' or '.join(REMOTES)} in {folder}")
    local = refs(folder, "refs/heads/")
    problems = 0
    for remote in remotes:
        git(folder, "fetch", "-q", remote, check=True)        # never --prune: a branch only there is listed, not lost
        there = refs(folder, f"refs/remotes/{remote}/")
        to_push, same, left, only_there, never = plan(folder, remote, local, there)
        print(f"── {remote}: {len(to_push)} to push ({sum(1 for _, k in to_push if k == 'new')} new), "
              f"{len(same)} the same, {len(left)} left alone, {len(only_there)} only there")
        for name, why in left:
            print(f"   LEFT ALONE  {name} — {why} (never forced; look at it)")
        for name in never:
            print(f"   NOT PUSHED  {name} — main to {remote} deploys: `git push {remote} main --tags` (asks Ron)")
        for name in only_there:
            print(f"   only on {remote}: {name} (not deleted)")
        if a.dry_run:
            for name, kind in to_push:
                print(f"   would push  {name} ({kind})")
            continue
        args = [f"refs/heads/{n}:refs/heads/{n}" for n, _ in to_push]
        r = git(folder, "push", "--tags", remote, *args)
        msg = (r.stderr or r.stdout).strip()
        if r.returncode:
            problems += 1
            print(f"   PUSH FAILED — {msg.splitlines()[-1] if msg else 'no message'}")
            for ln in msg.splitlines():
                if "rejected" in ln:
                    print(f"     {ln.strip()}")
        else:
            print(f"   pushed {len(to_push)} branch(es) and every tag" if to_push else "   tags checked; nothing else to push")
    if not a.dry_run:
        # what still differs, checked fresh (not assumed from the plan)
        local = refs(folder, "refs/heads/")
        for remote in remotes:
            git(folder, "fetch", "-q", remote, check=True)
            there = refs(folder, f"refs/remotes/{remote}/")
            to_push, _, left, _, never = plan(folder, remote, local, there)
            if to_push:
                problems += 1
                print(f"!! {remote} still lacks: {', '.join(n for n, _ in to_push)}")
        print("IN SYNC — both remotes hold every branch and tag (except what's listed above)" if not problems
              else f"NOT IN SYNC — {problems} problem(s) above")
    return 1 if problems else 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    sys.exit(main())
