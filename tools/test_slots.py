"""
test_slots.py — the machine-wide limit on screen tests running at once (TODO "Faster sprints", item 1; 2026-11-16).

Screen tests run in parallel (tools/run_tests.py --jobs), and several working copies of the project may test at the same
time — but sprint 4's one-time failures came from machine load. So every screen-test file, from ANY run on this PC,
holds one of N slots for as long as it runs:

    slots = Slots()                                  # N = RW_TEST_SLOTS, else 6; the slot files live in %TEMP%
    slot = slots.acquire("test/ui/test_cells.py", on_wait=print)    # waits while all N are taken (says so, once)
    slot = slots.acquire("…", upto=lambda: 3)        # only among the first 3 (the run's level — browser_level.py)
    ...                                              # run the file
    slot.release()

A slot is a file (%TEMP%\\rw-test-slots\\slot-<n>.lock) held with an OS file lock — not a flag written in it — so a run
that crashes or is stopped frees its slot the moment its process ends: nothing to clean up, nothing stale. The file's
text says who holds it (process id, working copy, test file, since when), so a waiting run can name what it waits for.
Every run must use the same N — a run with fewer slots just uses the first ones.

    group = slots.acquire_all("… (rerun alone)")     # EVERY slot: no other screen test on this PC runs meanwhile
    group.release()

How many browsers a run uses at once — its LEVEL, 1 to 6 — is chosen by the runner itself and saved beside these slot
files (tools/browser_level.py, 2026-11-17: it replaced the fixed low-memory rule of the same morning). A run at level L
takes only the first L slots, so every run on this PC together stays within the PC's level too. free_memory() reads
what the PC has available — noted in each run's record, as evidence.

Tested by test/test_run_tests.py (RUN-035…, 074, 079, 083).
"""
import datetime
import os
import tempfile
import time

DEFAULT_SLOTS = 6       # = browser_level.TOP, the most browsers at once a run may choose (4 until 2026-11-17)
# Measured 2026-11-17 on Ron's PC (a full tier 2, sampled every 3 s; RAM in use — working set — the same column as the
# "available" free_memory reads): one screen-test file's Chrome, all its processes, 0.15 GB typically, 0.48 GB at the
# 90th percentile, 0.57 GB at most; our web servers and local relays together up to 0.27 GB. (That day the PC had 3.8 GB
# of 31.4 free before the run, 1.4 GB at its low.) A fixed threshold drawn from that was replaced the same day by the
# level the runner finds for itself (browser_level.py); free memory is still recorded with every run.
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
        self.folder = folder or FOLDER

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
        """How many of the slots to look in: all, or the first `upto` (a number, or a function giving one — a run's
        level, which can drop while it waits)."""
        n = upto() if callable(upto) else upto
        return self.count if n is None else max(1, min(self.count, n))

    def try_acquire(self, label, upto=None):
        """A free slot (holding it), or None if all are taken. label: what will run in it, and from which working copy
        (shown to waiting runs). upto: look only in the first that-many slots (_upto)."""
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
                n = self._upto(upto)
                on_wait(f"· {label} waits for a test slot — "
                        + (f"all {self.count} on this PC are in use" if n >= self.count else
                           f"the first {n} of the {self.count} on this PC (browsers at once: {n}) are in use")
                        + f" (RW_TEST_SLOTS; {self.folder}):\n    " + "\n    ".join(self.holders()))
                said = True
            time.sleep(poll_s)
