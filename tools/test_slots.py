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

    group = slots.acquire_all("… (rerun alone)")     # EVERY slot: no other screen test on this PC runs meanwhile
    group.release()

Low memory (2026-11-17, TODO tooling item 9): free_memory() reads what the PC has available; memory_slots() says how many
browsers this run should run at once — fewer when memory is low — and why, in words.

Tested by test/test_run_tests.py (RUN-035…, 074, 079).
"""
import datetime
import os
import tempfile
import time

DEFAULT_SLOTS = 4
# Below LOW_MEMORY_GB free: 2 browsers at once; below half of it: 1 (RW_TEST_LOW_MEMORY_GB overrides it; 0 = no check).
# Measured 2026-11-17 on Ron's PC (a full tier 2, sampled every 3 s; RAM in use — working set — the same column as the
# "available" this reads): one screen-test file's Chrome, all its processes, 0.15 GB typically, 0.48 GB at the 90th
# percentile, 0.57 GB at most; our web servers and local relays together up to 0.27 GB. So 4 at their peak ≈ 2.5 GB: with
# under 4 GB free that leaves Windows and everything else under ~1.5 GB, and it pages; 2 (≈ 1.4 GB) leave room. Under
# 2 GB, even 2 would leave under ~0.6 GB: 1. (That day the PC had 3.8 GB of 31.4 free before the run, 1.4 GB at its low.)
LOW_MEMORY_GB = 4.0
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


def memory_slots(free, count, environ=None):
    """(browsers to run at once, why — or None when it's all of them): `count` normally; 2 with less than LOW_MEMORY_GB
    free, 1 with less than half of it (never more than count). RW_TEST_LOW_MEMORY_GB sets the threshold; 0 turns the
    check off. free: bytes, or None (unknown — no limit)."""
    env = os.environ if environ is None else environ
    try:
        low = float(env.get("RW_TEST_LOW_MEMORY_GB", "") or LOW_MEMORY_GB)
    except ValueError:
        low = LOW_MEMORY_GB
    if free is None or low <= 0:
        return count, None
    gb = free / 2 ** 30
    n = count if gb >= low else 2 if gb >= low / 2 else 1
    n = min(n, count)
    if n >= count:
        return count, None
    return n, (f"only {gb:.1f} GB of memory free — running {n} browser{'s' if n > 1 else ''} at once, not {count} "
               f"(under {low:g} GB: 2, under {low / 2:g} GB: 1 — RW_TEST_LOW_MEMORY_GB; 0 turns it off)")


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

    def try_acquire(self, label):
        """A free slot (holding it), or None if all are taken. label: what will run in it, and from which working copy
        (shown to waiting runs)."""
        for n in range(1, self.count + 1):
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
