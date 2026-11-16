"""
test_slots.py — the machine-wide limit on screen tests running at once (TODO "Faster sprints", item 1; 2026-11-16).

Screen tests run in parallel (tools/run_tests.py --jobs), and several working copies of the project may test at the same
time — but sprint 4's one-time failures came from machine load. So every screen-test file, from ANY run on this PC,
holds one of N slots for as long as it runs:

    slots = Slots()                                  # N = RW_TEST_SLOTS, else 4; the slot files live in %TEMP%
    slot = slots.acquire("test/ui/test_cells.py", on_wait=print)    # waits while all N are taken (says so, once)
    ...                                              # run the file
    slot.release()

A slot is a file (%TEMP%\\rw-test-slots\\slot-<n>.lock) held with an OS file lock — not a flag written in it — so a run
that crashes or is stopped frees its slot the moment its process ends: nothing to clean up, nothing stale. The file's
text says who holds it (process id, working copy, test file, since when), so a waiting run can name what it waits for.
Every run must use the same N — a run with fewer slots just uses the first ones.

Tested by test/test_run_tests.py (RUN-035…).
"""
import datetime
import os
import tempfile
import time

DEFAULT_SLOTS = 4
FOLDER = os.path.join(tempfile.gettempdir(), "rw-test-slots")
_LOCK_AT = 1 << 30      # Windows locks are mandatory: lock one byte far past the text, so others can still read who holds it

if os.name == "nt":
    import msvcrt

    def _try_lock(fd):
        os.lseek(fd, _LOCK_AT, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _unlock(fd):
        os.lseek(fd, _LOCK_AT, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:   # Ron's PC is Windows; this keeps the runner usable elsewhere
    import fcntl

    def _try_lock(fd):
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _unlock(fd):
        fcntl.flock(fd, fcntl.LOCK_UN)


def slot_count():
    """N: RW_TEST_SLOTS if it's a whole number of at least 1, else 4."""
    try:
        n = int(os.environ.get("RW_TEST_SLOTS", ""))
        return n if n >= 1 else DEFAULT_SLOTS
    except ValueError:
        return DEFAULT_SLOTS


class Slot:
    def __init__(self, number, fd, waited):
        self.number, self._fd, self.waited = number, fd, waited

    def release(self):
        if self._fd is None:
            return
        try:
            os.ftruncate(self._fd, 0)
        except OSError:
            pass
        _unlock(self._fd)
        os.close(self._fd)
        self._fd = None


class Slots:
    def __init__(self, count=None, folder=None):
        self.count = slot_count() if count is None else count
        self.folder = folder or FOLDER

    def _path(self, n):
        return os.path.join(self.folder, f"slot-{n}.lock")

    def try_acquire(self, label):
        """A free slot (holding it), or None if all are taken. label: what will run in it, and from which working copy
        (shown to waiting runs)."""
        os.makedirs(self.folder, exist_ok=True)
        for n in range(1, self.count + 1):
            fd = os.open(self._path(n), os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOINHERIT", 0))
            if _try_lock(fd):
                os.ftruncate(fd, 0)
                os.lseek(fd, 0, os.SEEK_SET)
                since = datetime.datetime.now().strftime("%H:%M:%S")
                os.write(fd, f"process {os.getpid()} · {label} · since {since}\n".encode("utf-8"))
                return Slot(n, fd, 0.0)
            os.close(fd)
        return None

    def holders(self):
        """Who holds each slot, in words (what a waiting run shows)."""
        out = []
        for n in range(1, self.count + 1):
            try:
                with open(self._path(n), encoding="utf-8", errors="replace") as f:
                    text = f.read().strip()
            except OSError:
                text = ""
            out.append(f"slot {n}: {text or '(starting)'}")
        return out

    def acquire(self, label, on_wait=None, poll_s=0.5):
        """Wait for a free slot and hold it. on_wait(message) is called once, if it has to wait, naming the holders."""
        start = time.monotonic()
        said = False
        while True:
            slot = self.try_acquire(label)
            if slot:
                slot.waited = time.monotonic() - start
                return slot
            if not said and on_wait:
                on_wait(f"· {label} waits for a test slot — all {self.count} on this PC are in use "
                        f"(RW_TEST_SLOTS; {self.folder}):\n    " + "\n    ".join(self.holders()))
                said = True
            time.sleep(poll_s)
