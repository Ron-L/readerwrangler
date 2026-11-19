# Tests for tools/backup_claude.py — Claude's memory and settings back themselves up at every release (TODO
# "Working-process safety net", items 2 and 3; sprint 9).
# tags: tooling, tier 1
# covers: tools/backup_claude.py, tools/whole_file.py
# Run: python test/test_backup_claude.py
#
# Never the real repositories, never a real push: every repository here is a throwaway in a temporary folder, cloned
# from a local bare repository that stands in for GitHub.
import os
import subprocess
import sys
import tempfile

# NEVER inherit git's own variables (2026-11-18, sprint 9 — a real incident): while the commit hook runs this test,
# GIT_DIR / GIT_INDEX_FILE point at the REAL repository's git folder, and a git command here would act on it (a `git
# init` in another test wrote core.bare = true into the real shared config). Removed before anything else runs; the
# tool itself removes them too (backup_claude.git).
for _k in [k for k in os.environ if k.startswith("GIT_")]:
    del os.environ[_k]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import backup_claude as bc   # noqa: E402


def git(repo, *args, check_=True):
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8")
    if check_ and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} in {repo}: {r.stderr}")
    return r.stdout.strip()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def repo_with_remote(tmp, name, files):
    """A clone of a bare 'remote' (origin), with `files` committed and pushed. Its path."""
    bare = os.path.join(tmp, name + ".git")
    git(tmp, "init", "-q", "--bare", "-b", "main", bare)
    repo = os.path.join(tmp, name)
    git(tmp, "clone", "-q", bare, repo)
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "checkout", "-q", "-b", "main")
    for rel, text in files.items():
        write(os.path.join(repo, rel), text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "start")
    git(repo, "push", "-q", "-u", "origin", "main")
    return repo


def setup(tmp):
    """Ron's layout, in miniature: memory, settings.local.json, the global settings, the private notes repository
    (with an older backup) and the Projects repository (allow-list .gitignore without the copy)."""
    memory = os.path.join(tmp, "home", ".claude", "projects", "c--x-ReaderWrangler", "memory")
    write(os.path.join(memory, "MEMORY.md"), "# index v2\n")
    write(os.path.join(memory, "kept.md"), "kept, changed\n")
    write(os.path.join(memory, "new.md"), "a new memory\n")
    write(os.path.join(memory, "notes.txt"), "not a memory file\n")
    local = os.path.join(tmp, "main", ".claude", "settings.local.json")
    write(local, '{"permissions": {"allow": ["x"]}}\n')
    glob = os.path.join(tmp, "home", ".claude", "settings.json")
    write(glob, '{"hooks": {}}\n')
    private = repo_with_remote(tmp, "private", {
        "claude-backup/README.md": "readme\n",
        "claude-backup/memory/MEMORY.md": "# index v1\n",
        "claude-backup/memory/kept.md": "kept\n",
        "claude-backup/memory/gone.md": "a memory since deleted\n",
        "claude-backup/memory/other.txt": "not ours to touch\n",
        "claude-backup/settings.local.json": "{}\n",
        "TODO_NOTES.md": "notes\n"})
    projects = repo_with_remote(tmp, "projects", {".gitignore": "/*\n!/.gitignore\n!/stamp.py\n!/HOMELAB.md\n",
                                                  "stamp.py": "x\n"})
    return dict(memory=memory, local_settings=local, global_settings=glob, private_repo=private,
                projects_repo=projects)


def remote_head(repo):
    return git(repo, "rev-parse", "origin/main"), git(repo + ".git", "rev-parse", "main")


def first_run():
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        p = setup(tmp)
        write(os.path.join(p["private_repo"], "proposals", "draft.md"), "untracked — not the backup's\n")
        write(os.path.join(p["projects_repo"], "HOMELAB.md"), "staged by Ron, not the backup's\n")
        git(p["projects_repo"], "add", "HOMELAB.md")
        lines, ok = bc.backup(**p)
        text = "\n".join(lines)
        check(ok, f"it worked:\n{text}")
        mem = os.path.join(p["private_repo"], "claude-backup", "memory")
        check(sorted(os.listdir(mem)) == ["MEMORY.md", "kept.md", "new.md", "other.txt"],
              f"memory mirrored: new.md added, gone.md REMOVED (deleted in memory), only .md files: {os.listdir(mem)}")
        check(read(os.path.join(mem, "MEMORY.md")) == "# index v2\n" and read(os.path.join(mem, "kept.md")) ==
              "kept, changed\n", "changed files updated")
        check(read(os.path.join(p["private_repo"], "claude-backup", "settings.local.json")) ==
              '{"permissions": {"allow": ["x"]}}\n', "settings.local.json copied")
        check("removed" in text and "gone.md" in text, f"the report names what was removed:\n{text}")
        # committed and pushed — only the backup's files
        priv = p["private_repo"]
        check(git(priv, "status", "--porcelain", "--", "claude-backup") == "", "the backup is committed in the private repo")
        changed = git(priv, "show", "--name-status", "--format=", "HEAD").splitlines()
        check(sorted(changed) == sorted(["M\tclaude-backup/memory/MEMORY.md", "M\tclaude-backup/memory/kept.md",
                                         "A\tclaude-backup/memory/new.md", "D\tclaude-backup/memory/gone.md",
                                         "M\tclaude-backup/settings.local.json"]),
              f"one commit holding exactly the backup's changes: {changed}")
        subject = git(priv, "log", "-1", "--format=%s")
        check(subject.endswith("memory - 1 added, 2 updated, 1 removed; settings.local.json updated"),
              f"the commit says what changed: {subject!r}")
        check("proposals/" in git(priv, "status", "--porcelain"), "an untracked file of Ron's is left alone")
        local_head, bare_head = remote_head(priv)
        check(git(priv, "rev-parse", "HEAD") == local_head == bare_head, "and pushed to origin")
        # the Projects repository: the global settings, allowed back in by .gitignore
        proj = p["projects_repo"]
        check(read(os.path.join(proj, bc.GLOBAL_COPY)) == '{"hooks": {}}\n', f"the global settings copied to "
              f"{bc.GLOBAL_COPY}")
        check("!/" + bc.GLOBAL_COPY in read(os.path.join(proj, ".gitignore")), "the allow-list lets the copy in")
        changed = git(proj, "show", "--name-status", "--format=", "HEAD").splitlines()
        check(sorted(changed) == sorted(["M\t.gitignore", "A\t" + bc.GLOBAL_COPY]),
              f"committed: the copy and .gitignore only: {changed}")
        check(git(proj, "diff", "--cached", "--name-only") == "HOMELAB.md", "what Ron had staged stays staged, "
              "uncommitted")
        local_head, bare_head = remote_head(proj)
        check(git(proj, "rev-parse", "HEAD") == local_head == bare_head, "and pushed to origin")
test("CBAK-001", "memory mirrored into the private repo (added, updated, a deleted memory deleted, .md only), "
     "settings.local.json and the global settings copied (.gitignore allows it), each repo committed — only the "
     "backup's files — and pushed", first_run)


def nothing_changed():
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        p = setup(tmp)
        bc.backup(**p)
        heads = [git(p[r], "rev-parse", "HEAD") for r in ("private_repo", "projects_repo")]
        lines, ok = bc.backup(**p)
        text = "\n".join(lines)
        check(ok, f"fine:\n{text}")
        check([git(p[r], "rev-parse", "HEAD") for r in ("private_repo", "projects_repo")] == heads,
              "nothing changed: no commit in either repo")
        check(text.count("nothing changed") == 2, f"and it says so for each:\n{text}")
test("CBAK-002", "run again with nothing changed: no commit, and it says so", nothing_changed)


def empty_memory_refused():
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        p = setup(tmp)
        for n in os.listdir(p["memory"]):
            os.remove(os.path.join(p["memory"], n))
        head = git(p["private_repo"], "rev-parse", "HEAD")
        lines, ok = bc.backup(**p)
        mem = os.path.join(p["private_repo"], "claude-backup", "memory")
        check(not ok and any("no memory files" in ln for ln in lines), f"refused, saying why: {lines}")
        check("gone.md" in os.listdir(mem) and git(p["private_repo"], "rev-parse", "HEAD") == head,
              "the backup is untouched — an empty (or missing) memory folder never empties it")
        p["memory"] = os.path.join(tmp, "nowhere")
        lines, ok = bc.backup(**p)
        check(not ok and any("no memory files" in ln or "isn't there" in ln for ln in lines),
              f"a missing folder too: {lines}")
test("CBAK-003", "a memory folder that's empty or missing is refused — the backup is never emptied",
     empty_memory_refused)


def push_refused():
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        p = setup(tmp)
        other = os.path.join(tmp, "elsewhere")                   # someone pushed from another PC
        git(tmp, "clone", "-q", p["private_repo"] + ".git", other)
        git(other, "config", "user.name", "Other")
        git(other, "config", "user.email", "o@example.com")
        write(os.path.join(other, "TODO_NOTES.md"), "changed elsewhere\n")
        git(other, "commit", "-q", "-am", "elsewhere")
        git(other, "push", "-q", "origin", "main")
        lines, ok = bc.backup(**p)
        text = "\n".join(lines)
        check(not ok and "PUSH FAILED" in text, f"the refused push is said loudly:\n{text}")
        check(git(p["private_repo"], "status", "--porcelain", "--", "claude-backup") == "",
              "the backup is still committed locally")
        check(git(p["private_repo"] + ".git", "log", "-1", "--format=%s", "main") == "elsewhere",
              "and the remote is untouched — never forced")
        local_head, bare_head = remote_head(p["projects_repo"])
        check(git(p["projects_repo"], "rev-parse", "HEAD") == bare_head, "the other repo still went through")
test("CBAK-004", "a push the remote refuses: said loudly, the commit kept, nothing forced; the other repo still goes",
     push_refused)


def where_memory_is():
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        home = os.path.join(tmp, "home")
        os.makedirs(os.path.join(home, ".claude", "projects", "c--Users-Ron-Projects-ReaderWrangler", "memory"))
        got = bc.memory_folder(r"C:\Users\Ron\Projects\ReaderWrangler", home)
        check(got == os.path.join(home, ".claude", "projects", "c--Users-Ron-Projects-ReaderWrangler", "memory"),
              f"Claude Code's folder for the project, its name from the project's path (any case): {got}")
        got = bc.memory_folder(r"C:\Elsewhere\Project", home)
        check(got is None, f"no folder for the project: None ({got})")
        paths = bc.default_paths(r"C:\Users\Ron\Projects\ReaderWrangler", home)
        check(paths["private_repo"] == r"C:\Users\Ron\Projects\ReaderWrangler\.private"
              and paths["projects_repo"] == r"C:\Users\Ron\Projects"
              and paths["local_settings"] == r"C:\Users\Ron\Projects\ReaderWrangler\.claude\settings.local.json"
              and paths["global_settings"] == os.path.join(home, ".claude", "settings.json"),
              f"everything from the MAIN folder: {paths}")
test("CBAK-005", "where things are: the memory folder from the project's path (any case), the rest from the main folder",
     where_memory_is)


def line_endings_only():
    """Ron's git turns LF into CRLF on checkout (core.autocrlf true): the backup's files on disk end lines in CRLF while
    memory's end in LF. Copied over, the bytes differ but git sees no change — so no commit, and none claimed."""
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        p = setup(tmp)
        bc.backup(**p)
        priv = p["private_repo"]
        git(priv, "config", "core.autocrlf", "true")
        for n in os.listdir(os.path.join(priv, "claude-backup", "memory")):     # as a fresh checkout would leave them
            f = os.path.join(priv, "claude-backup", "memory", n)
            data = open(f, "rb").read()
            open(f, "wb").write(data.replace(b"\n", b"\r\n"))
        head = git(priv, "rev-parse", "HEAD")
        lines, ok = bc.backup(**p)
        check(ok and git(priv, "rev-parse", "HEAD") == head, f"no commit: git sees no change ({lines})")
        check(any("nothing changed" in ln for ln in lines), f"and it says nothing changed: {lines}")
test("CBAK-007", "only line endings differ (git's CRLF on checkout): git sees no change — no commit", line_endings_only)


def from_a_copy():
    """Run from a working copy, the main folder is found — never the copy. A temporary main folder and copy (a git
    worktree, as tools/copies.py makes) — never the real repository."""
    with tempfile.TemporaryDirectory(prefix="rw-cbak-") as tmp:
        main = repo_with_remote(tmp, "Main", {"x.txt": "x\n"})
        copy = os.path.join(tmp, "copies", "a-copy")
        git(main, "worktree", "add", "-q", "-b", "a-copy", copy)
        got = bc.project_folder(copy)
        check(os.path.normcase(os.path.normpath(got)) == os.path.normcase(os.path.normpath(main)),
              f"from the copy: the main folder ({got})")
        git(main, "worktree", "remove", "--force", copy)
test("CBAK-006", "the main folder is found even from a working copy (copies.main_folder)", from_a_copy)

done()
