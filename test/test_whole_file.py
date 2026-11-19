# Tests for tools/whole_file.py — the one way a tool writes a file whole (Law 22; TODO "Working-process safety net",
# sprint 9 item 4).
# tags: build, tooling, tier 1
# covers: tools/whole_file.py, tools/build.py, tools/browser_level.py
# Run: python test/test_whole_file.py
#
# tools/build.py (_write) and tools/browser_level.py (save) each wrote a scratch copy and swapped it in, retrying while
# Windows refused the swap — two copies of the same routine. Now both use whole_file.write.
import importlib.util
import json
import os
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test", "ui"))
from harness import check, done, test   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import whole_file   # noqa: E402
import browser_level   # noqa: E402

_spec = importlib.util.spec_from_file_location("rw_build_for_whole", os.path.join(ROOT, "tools", "build.py"))
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)


def written_whole():
    with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
        target = os.path.join(tmp, "sub", "a.txt")          # a folder that isn't there yet is made
        whole_file.write(target, "one\ntwo\n", newline="\n")
        check(open(target, "rb").read() == b"one\ntwo\n", "the text is written, with the line ending asked for")
        whole_file.write(target, "three\n", newline="\n")
        check(open(target, "rb").read() == b"three\n", "a second write replaces the file whole")
        check(os.listdir(os.path.dirname(target)) == ["a.txt"], "no scratch copy is left beside it")
test("WHOLE-001", "a file is written to a scratch copy and swapped in whole; no scratch copy is left",
     written_whole)


def waits_for_a_reader():
    with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
        target = os.path.join(tmp, "app.js")
        open(target, "w").write("old")
        reader = open(target)                               # another program reading the old copy
        threading.Timer(0.3, reader.close).start()          # … finishes after 0.3 s
        whole_file.write(target, "new")
        check(open(target).read() == "new", "the swap waited for the reader, then the new copy went in")
        if os.name != "nt":                                 # only Windows refuses a swap over an open file
            return
        reader = open(target)
        tries = whole_file.SWAP_TRIES
        try:
            whole_file.SWAP_TRIES = 3
            whole_file.write(target, "newer")
            raise AssertionError("a reader holding the file the whole time: PermissionError expected")
        except PermissionError:
            pass
        finally:
            whole_file.SWAP_TRIES = tries
            reader.close()
        check(open(target).read() == "new", "still refused: the old copy is left whole")
        check(os.listdir(tmp) == ["app.js"], f"and no scratch copy is left behind: {os.listdir(tmp)}")
test("WHOLE-002", "a refused swap is retried (~2 s); still refused, the old copy stays whole, no scratch copy, and "
     "PermissionError says so", waits_for_a_reader)


def refused_n_times():
    """The retry counted exactly: refused twice, then allowed — three tries, two pauses."""
    real_replace, real_sleep = whole_file.os.replace, whole_file.time.sleep
    calls, pauses = [], []

    def flaky(src, dst):
        calls.append(dst)
        if len(calls) <= 2:
            raise PermissionError(13, "Access is denied")
        return real_replace(src, dst)
    with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
        target = os.path.join(tmp, "level.json")
        whole_file.os.replace, whole_file.time.sleep = flaky, pauses.append
        try:
            whole_file.write(target, "{}")
        finally:
            whole_file.os.replace, whole_file.time.sleep = real_replace, real_sleep
        check(len(calls) == 3 and pauses == [whole_file.SWAP_PAUSE_S] * 2,
              f"three tries, two pauses of {whole_file.SWAP_PAUSE_S} s: {len(calls)} tries, pauses {pauses}")
        check(open(target).read() == "{}", "the third try put it in place")
test("WHOLE-003", "refused twice then allowed: three tries, two pauses — and the file is in place", refused_n_times)


def other_failures_not_retried():
    """Only Windows' "in use" refusal is retried; any other failure stops at once, leaving no scratch copy."""
    with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
        target = os.path.join(tmp, "x.txt")
        try:
            whole_file.write(target, object())      # not text: the write itself fails
            raise AssertionError("writing something that isn't text must fail")
        except TypeError:
            pass
        check(os.listdir(tmp) == [], f"no scratch copy left after a failed write: {os.listdir(tmp)}")
test("WHOLE-004", "a write that fails before the swap leaves no scratch copy and raises", other_failures_not_retried)


def both_tools_use_it():
    """Law 22 — one routine: build.py and browser_level.py both write through whole_file (no swap loop of their own)."""
    for rel in ("tools/build.py", "tools/browser_level.py"):
        src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        check("whole_file.write(" in src, f"{rel} writes through whole_file.write")
        check("os.replace(" not in src and "SWAP_TRIES" not in src, f"{rel} has no swap-and-retry of its own")
    seen = []
    real = whole_file.write
    whole_file.write = lambda *a, **k: (seen.append((a, k)), real(*a, **k))[1]
    try:
        with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
            build._write(os.path.join(tmp, "dist", "a.js"), "x\ny\n")
            check(open(os.path.join(tmp, "dist", "a.js"), "rb").read() == b"x\ny\n", "build.py's copy keeps LF endings")
            err = browser_level.save(os.path.join(tmp, "level.json"), {"level": 4})
            check(err is None and json.load(open(os.path.join(tmp, "level.json"))) == {"level": 4},
                  f"browser_level.save writes the state (err={err})")
    finally:
        whole_file.write = real
    check(len(seen) == 2, f"both went through whole_file.write: {len(seen)} calls")
test("WHOLE-005", "tools/build.py and tools/browser_level.py both write through whole_file.write (Law 22)",
     both_tools_use_it)


def save_failure_in_words():
    """browser_level.save still answers in words, never raises (the runner prints it)."""
    with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
        blocker = os.path.join(tmp, "file")
        open(blocker, "w").write("x")
        err = browser_level.save(os.path.join(blocker, "level.json"), {"level": 4})   # a folder that is a file
        check(isinstance(err, str) and "couldn't save" in err, f"why it couldn't, in words: {err!r}")
test("WHOLE-006", "browser_level.save that can't write says why in words (never raises)", save_failure_in_words)


def bytes_as_they_are():
    """A copied file (tools/backup_claude.py) is written byte for byte — no line endings changed."""
    with tempfile.TemporaryDirectory(prefix="rw-whole-") as tmp:
        target = os.path.join(tmp, "m.md")
        data = "a\r\nb\nü\n".encode("utf-8")
        whole_file.write(target, data)
        check(open(target, "rb").read() == data, "bytes are written exactly as given")
        check(os.listdir(tmp) == ["m.md"], "no scratch copy left")
test("WHOLE-007", "bytes are written whole, exactly as given (a copy of a file)", bytes_as_they_are)

done()
