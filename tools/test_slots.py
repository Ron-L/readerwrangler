"""
test_slots.py — the PC-wide limit on screen tests running at once, and the folder where this PC's test state lives.

Several runs may test at once (tools/run_tests.py runs files in parallel, and each working copy may run its own). Every
screen-test file — and every tier-1 file whose header says `heavy: yes` — holds one of the PC's slots while it runs:

    slots = Slots()                                  # N = RW_TEST_SLOTS, else 6 (the most any run may use)
    slot = slots.try_acquire("test/ui/test_x.py", upto=4)   # a free slot among the first 4, or None
    slot = slots.acquire("…", on_wait=print, upto=4)        # the same, waiting while they're taken (said once)
    ...                                              # run the file
    slot.release()
    group = slots.acquire_all("… (rerun alone)")     # EVERY slot: no other screen test on this PC runs meanwhile
    group.release()

A run uses the first 4 slots (its --jobs N: the first N), so every run on the PC together stays at 4 browsers at once.
A slot is a file (slot-<n>.lock) held with an OS file lock — not a flag written in it — so a run that crashes frees its
slot the moment its process ends: nothing stale. The file's text names who holds it, so a waiting run can say so.

    with locked(path) as held:                       # the same OS file lock, on any file — waits (30 s at most)
        ...                                          # tools/held_tests.py reads, changes and saves its file here

The folder (FOLDER, slots_folder()): %LOCALAPPDATA%\\ReaderWrangler-tests — not the temp folder, which Windows may clear
(a held file's record would vanish with it). RW_TEST_SLOTS_DIR chooses another folder. free_memory() reads what the PC
has available (noted in each run's record).

Tested by test/test_run_tests.py and test/test_job.py.
"""
import contextlib
import datetime
import os
import time

DEFAULT_SLOTS = 6       # the most browsers at once any run may use (--jobs 6); a run uses the first 4 by default
FOLDER = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".cache"),
                      "ReaderWrangler-tests")


def slots_folder():
    """Where this PC's test state lives — the slot files, the held files: RW_TEST_SLOTS_DIR when set, else FOLDER. Read at
    each call, not at import."""
    own = os.environ.get("RW_TEST_SLOTS_DIR")
    return os.path.abspath(own) if own else FOLDER


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


@contextlib.contextmanager
def locked(path, limit_s=30.0, poll_s=0.05):
    """Hold the OS file lock on `path` (made if missing) for the with-block — the slots' own lock (_try_lock), the one
    way a file is locked on this PC (Law 22). Waits while another process (or another handle here) holds it, `limit_s`
    at most; yields True when held, False when it gave up waiting. Freed by the OS if the process ends."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOINHERIT", 0))
    try:
        deadline, got = time.monotonic() + limit_s, False
        while not (got := _try_lock(fd)) and time.monotonic() < deadline:
            time.sleep(poll_s)
        try:
            yield got
        finally:
            if got:
                _unlock(fd)
    finally:
        os.close(fd)


def slot_count():
    """N: RW_TEST_SLOTS if it's a whole number of at least 1, else 6."""
    try:
        n = int(os.environ.get("RW_TEST_SLOTS", ""))
        return n if n >= 1 else DEFAULT_SLOTS
    except ValueError:
        return DEFAULT_SLOTS


def free_memory():
    """Bytes of memory the PC can give right now without swapping to disk — Windows: GlobalMemoryStatusEx's available
    physical memory; elsewhere /proc/meminfo's MemAvailable, else the free pages. None if it can't be read."""
    if os.name == "nt":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        return status.ullAvailPhys if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)) else None
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    try:
        return os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    except (ValueError, OSError, AttributeError):
        return None


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


class SlotGroup:
    """Every slot, held together (Slots.acquire_all)."""

    def __init__(self, slots, waited):
        self.slots, self.waited = slots, waited

    def release(self):
        for s in self.slots:
            s.release()


class Slots:
    def __init__(self, count=None, folder=None):
        self.count = slot_count() if count is None else count
        self.folder = folder or slots_folder()

    def _path(self, n):
        return os.path.join(self.folder, f"slot-{n}.lock")

    def _try_one(self, n, label):
        """Slot n (holding it), or None if it's taken."""
        os.makedirs(self.folder, exist_ok=True)
        fd = os.open(self._path(n), os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOINHERIT", 0))
        if _try_lock(fd):
            os.ftruncate(fd, 0)
            os.lseek(fd, 0, os.SEEK_SET)
            since = datetime.datetime.now().strftime("%H:%M:%S")
            os.write(fd, f"process {os.getpid()} · {label} · since {since}\n".encode("utf-8"))
            return Slot(n, fd, 0.0)
        os.close(fd)
        return None

    def _upto(self, upto):
        """How many of the slots to look in: all, or the first `upto`."""
        return self.count if upto is None else max(1, min(self.count, upto))

    def try_acquire(self, label, upto=None):
        """A free slot (holding it), or None if all are taken. label: what will run in it, and from which working copy
        (shown to waiting runs). upto: look only in the first that-many slots (the run's browsers at once)."""
        for n in range(1, self._upto(upto) + 1):
            slot = self._try_one(n, label)
            if slot:
                return slot
        return None

    def acquire_all(self, label, on_wait=None, poll_s=0.5):
        """Hold EVERY slot — no other screen test on this PC runs meanwhile (a file rerun alone after the machine's
        trouble, tools/run_tests.py). Taken in order, 1 to N, each waited for: two runs doing this at once can't each
        hold half and wait forever. on_wait(message) once, if it has to wait. Returns a group: .release(), .waited."""
        start, held, said = time.monotonic(), [], False
        for n in range(1, self.count + 1):
            while True:
                slot = self._try_one(n, label)
                if slot:
                    held.append(slot)
                    break
                if not said and on_wait:
                    on_wait(f"· {label} waits for every test slot on this PC to be free (RW_TEST_SLOTS; {self.folder}):"
                            "\n    " + "\n    ".join(self.holders()))
                    said = True
                time.sleep(poll_s)
        return SlotGroup(held, time.monotonic() - start)

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

    def acquire(self, label, on_wait=None, poll_s=0.5, upto=None):
        """Wait for a free slot and hold it. on_wait(message) is called once, if it has to wait, naming the holders.
        upto: only among the first that-many slots (_upto)."""
        start = time.monotonic()
        said = False
        while True:
            slot = self.try_acquire(label, upto)
            if slot:
                slot.waited = time.monotonic() - start
                return slot
            if not said and on_wait:
                on_wait(self.wait_message(label, upto))
                said = True
            time.sleep(poll_s)

    def wait_message(self, label, upto=None):
        """What a run waiting for a slot says (once): what waits, which slots it may use, who holds each."""
        n = self._upto(upto)
        return (f"· {label} waits for a test slot — "
                + (f"all {self.count} on this PC are in use" if n >= self.count else
                   f"the first {n} of the {self.count} on this PC (its browsers at once: {n}) are in use")
                + f" (RW_TEST_SLOTS; {self.folder}):\n    " + "\n    ".join(self.holders()))
