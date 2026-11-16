# Tests for tools/sync_remotes.py — dev and prod kept holding every branch and tag this folder has.
# tags: remotes, tooling, tier 1
# covers: tools/sync_remotes.py
# Run: python test/test_sync_remotes.py
#
# Ron, 2026-11-16. Each test builds, in %TEMP%, a throwaway repository with two bare "remotes" named dev and prod, and
# drives sync_remotes.main() on it — real git, nothing pushed anywhere real.
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, remove_tree, test   # noqa: E402

# git's own variables point every git command at THIS repository while the commit hook runs (RUN-044)
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]

spec = importlib.util.spec_from_file_location("sync_remotes", os.path.join(ROOT, "tools", "sync_remotes.py"))
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)


def git(folder, *args):
    r = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise AssertionError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


class Repo:
    """A local repository on main with remotes dev and prod (bare, in the same temp folder), both holding main."""
    def __enter__(self):
        self.top = tempfile.mkdtemp(prefix="rw-sync-")
        self.dir = os.path.join(self.top, "local")
        os.makedirs(self.dir)
        git(self.dir, "init", "-q", "-b", "main")
        git(self.dir, "config", "user.email", "t@example.com")
        git(self.dir, "config", "user.name", "t")
        self.commit("first")
        for r in ("dev", "prod"):
            bare = os.path.join(self.top, r + ".git")
            subprocess.run(["git", "init", "-q", "--bare", bare], check=True)
            git(self.dir, "remote", "add", r, bare)
            git(self.dir, "push", "-q", r, "main")
        return self

    def __exit__(self, *exc):
        remove_tree(self.top)

    def commit(self, msg, branch=None):
        if branch:
            git(self.dir, "switch", "-q", branch)
        with open(os.path.join(self.dir, "f.txt"), "a") as f:
            f.write(msg + "\n")
        git(self.dir, "add", "f.txt")
        git(self.dir, "commit", "-q", "-m", msg)
        return git(self.dir, "rev-parse", "HEAD")

    def remote_head(self, remote, branch):
        r = subprocess.run(["git", "--git-dir", os.path.join(self.top, remote + ".git"), "rev-parse", "--verify", "-q",
                            f"refs/heads/{branch}"], capture_output=True, text=True)
        return r.stdout.strip() or None

    def remote_tags(self, remote):
        return subprocess.run(["git", "--git-dir", os.path.join(self.top, remote + ".git"), "tag"],
                              capture_output=True, text=True).stdout.split()

    def sync(self, *argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = sr.main(list(argv), folder=self.dir)
        return code, buf.getvalue()


def new_branches_go_to_both_but_main_never_to_prod():
    with Repo() as r:
        git(r.dir, "switch", "-q", "-c", "feature/a")
        a = r.commit("a")
        git(r.dir, "switch", "-q", "main")
        m = r.commit("main moves")
        git(r.dir, "tag", "v1.0.0")
        code, out = r.sync()
        check(code == 0 and "IN SYNC" in out, f"exit {code}:\n{out}")
        check(r.remote_head("dev", "feature/a") == a and r.remote_head("prod", "feature/a") == a,
              "a new branch reaches both remotes")
        check(r.remote_head("dev", "main") == m, "main goes to dev (the dev site — allowed)")
        check(r.remote_head("prod", "main") != m and "NOT PUSHED  main" in out,
              f"main NEVER goes to prod from this script (it deploys) — and it says so:\n{out}")
        check("v1.0.0" in r.remote_tags("dev") and "v1.0.0" in r.remote_tags("prod"), "tags reach both")


def ahead_or_diverged_remotes_are_left_alone():
    with Repo() as r:
        git(r.dir, "switch", "-q", "-c", "feature/b")
        r.commit("b1")
        git(r.dir, "push", "-q", "dev", "feature/b")
        git(r.dir, "push", "-q", "prod", "feature/b")
        # dev's main moves ahead (a dev test); prod's feature/b diverges (someone else's commit there)
        other = os.path.join(r.top, "other")
        subprocess.run(["git", "clone", "-q", os.path.join(r.top, "dev.git"), other], check=True)
        git(other, "config", "user.email", "t@example.com")
        git(other, "config", "user.name", "t")
        with open(os.path.join(other, "g.txt"), "w") as f:
            f.write("dev test\n")
        git(other, "add", "g.txt")
        git(other, "commit", "-q", "-m", "dev test")
        git(other, "push", "-q", "origin", "main")
        dev_main = git(other, "rev-parse", "HEAD")
        git(other, "remote", "add", "prod", os.path.join(r.top, "prod.git"))
        git(other, "fetch", "-q", "prod")
        git(other, "switch", "-q", "-c", "feature/b", "prod/feature/b")
        with open(os.path.join(other, "h.txt"), "w") as f:
            f.write("theirs\n")
        git(other, "add", "h.txt")
        git(other, "commit", "-q", "-m", "theirs")
        git(other, "push", "-q", "prod", "feature/b")
        prod_b = git(other, "rev-parse", "HEAD")
        r.commit("b2 (mine)", branch="feature/b")     # local feature/b now diverges from prod's
        code, out = r.sync()
        check(r.remote_head("dev", "main") == dev_main and "a dev test in progress?" in out,
              f"dev's main ahead of yours is left alone and named a dev test:\n{out}")
        check(r.remote_head("prod", "feature/b") == prod_b and "diverged" in out,
              f"a diverged branch is never overwritten:\n{out}")
        check(r.remote_head("dev", "feature/b") == git(r.dir, "rev-parse", "feature/b"),
              "where the remote is simply behind, it's fast-forwarded")


def scratch_skipped_remote_only_kept_dry_run_pushes_nothing():
    with Repo() as r:
        git(r.dir, "switch", "-q", "-c", "merging/sprint-9")
        r.commit("scratch")
        git(r.dir, "switch", "-q", "main")
        git(r.dir, "switch", "-q", "-c", "fix/c")
        c = r.commit("c")
        git(r.dir, "push", "-q", "dev", "fix/c:refs/heads/only-on-dev")
        git(r.dir, "switch", "-q", "main")
        code, out = r.sync("--dry-run")
        check(r.remote_head("dev", "fix/c") is None and r.remote_head("prod", "fix/c") is None
              and "would push  fix/c (new)" in out, f"--dry-run pushes nothing and says what it would:\n{out}")
        code, out = r.sync()
        check(r.remote_head("dev", "fix/c") == c and r.remote_head("prod", "fix/c") == c, "then it pushes")
        check(r.remote_head("dev", "merging/sprint-9") is None and r.remote_head("prod", "merging/sprint-9") is None,
              "the merge script's scratch branches are never pushed")
        check(r.remote_head("dev", "only-on-dev") == c and "only on dev: only-on-dev (not deleted)" in out,
              f"a branch only on a remote is listed, never deleted:\n{out}")


test("SYNC-001", "a new branch and every tag go to both remotes; main goes to dev but never to prod (it deploys)",
     new_branches_go_to_both_but_main_never_to_prod)
test("SYNC-002", "a remote that is ahead (dev's main: a dev test) or has diverged is left alone and named; a remote "
     "that is behind is fast-forwarded", ahead_or_diverged_remotes_are_left_alone)
test("SYNC-003", "--dry-run pushes nothing; scratch branches (merging/*) are never pushed; a branch only on a remote "
     "is listed, never deleted", scratch_skipped_remote_only_kept_dry_run_pushes_nothing)

done()
