"""
test_costs.py — what each test costs this PC: measured for every test unit, and a running average kept per PC (TODO
"Turn more of our working rules into automatic checks", item 12, step 1 — Ron, 2026-11-18: "Measure 1st. If you don't
measure you won't know if you've improved things"). Measuring only: nothing here changes how tests are scheduled.

A UNIT is one process the runner starts: a whole test file, or one shard of a file split with `shards: N`.

1. MEASURED, per unit, per run (run(), below) — for the unit's WHOLE process tree, including processes that already
   exited (git, node, Chrome's helpers): the unit is started suspended, put in a Windows job object of its own, then
   let go; a job counts every process started inside it (a process can't leave it — we never allow breakaway; Chrome's
   own nested jobs still count in ours). What each number is — and is NOT:
     - wall seconds (the runner's own clock, as before);
     - COMMITTED peak — the job's PeakJobMemoryUsed: the most private memory (commit charge: memory the processes asked
       Windows to guarantee them, backed by RAM or the page file) the tree held at once. NOT RAM in use — PRINCIPLES
       Law 2: 7.31.0 quoted committed memory as RAM;
     - RAM, private (sampled peak) — what the test adds to the PC's RAM: each process's PRIVATE working set (RAM only it
       uses; the pages it shares — Chrome's and Python's DLLs — left out), added up about once a second; the highest sum
       seen (ram_peak_sampled_bytes, ram_kind "private"). A peak between two samples is missed, so it can read low; a
       unit shorter than the first sample (¼ s) has none. A Windows without the private figure (before 10 1709): the
       whole working sets instead, shared pages counted in each — ram_kind "shared included", ram_note why. (2026-11-18:
       the first version summed whole working sets — the same shared base added to every test squeezed the ratio
       between tests toward 1, the number the next step decides on.) The shared-included sum is kept beside it in the
       record (ram_with_shared_peak_sampled_bytes — the same call gives it, so it costs nothing), but never averaged or
       shown: nothing is decided on it;
     - CPU seconds — user + kernel time of every process in the tree, exited ones included;
     - I/O bytes read and written — Windows counts ALL of a process's I/O here: files, pipes AND network, not only the
       disk;
     - processes — how many the tree started in all (the proof that Chrome stayed in the job: a screen test shows many).
   Not on Windows, or anything about measuring fails: every measure is None, the run goes on exactly as before, and
   `missing` says why — measuring must never fail or slow a test run.

2. KEPT, per PC (teach(), below): for each unit, a running average and spread of each measure — TCP's own method for
   round-trip times (RFC 6298: spread += (|sample − average| − spread)/4, then average += (sample − average)/8; the first
   sample: average = sample, spread = sample/2), with its count and last value and the date. Saved beside the test
   slots and the browsers-at-once level (%TEMP%\\rw-test-slots\\test-costs.json, or RW_TEST_SLOTS_DIR's folder):
     - only a unit that ran IN FULL and PASSED teaches it (Karn's rule, as the browsers-at-once level does): never one in
       a run narrowed by --id, --tag, --changed or RW_CELLS, never a failed one, never a rerun alone after the machine's
       trouble — those stay in the run's record, marked, but out of the average (left_out());
     - a test file whose contents changed starts its history over (each file's hash is kept with it);
     - several runs on this PC (other working copies) may finish at once: each change is read, merged and written under
       an OS file lock (tools/test_slots.py locked — the slots' own lock), and written whole by browser_level.save (a
       temporary file put in place) — the one way each is done here (Law 22).
   To start again: delete the file.

3. SHOWN: `py tools/run_tests.py --costs` — table(): each unit, how many runs taught it, average ± spread of each
   measure, sorted by average time; the totals; and how much the screen tests differ in RAM (the biggest average RAM
   peak over the smallest — the later budget step asks "is the biggest at least twice the smallest?").

Tested by test/test_test_costs.py (COST-001–…).
"""
import contextlib
import datetime
import hashlib
import json
import os
import subprocess
import threading

import browser_level    # tools/: its save() writes a file whole (a temporary file, then put in place)
import test_slots       # tools/: the slots' OS file lock (locked()) and their folder (slots_folder())

FILE_NAME = "test-costs.json"
MEASURES = ("seconds", "committed_peak_bytes", "ram_peak_sampled_bytes", "cpu_seconds", "io_read_bytes",
            "io_written_bytes")             # what is averaged; "processes" is kept in the run's record only
FIRST_SAMPLE_S, SAMPLE_S = 0.25, 1.0        # the RAM sample: a quarter second after the start, then once a second
LOCK_LIMIT_S = 30.0                         # saving waits this long at most for another run's save, then gives up


def costs_path(folder=None):
    """This PC's file: beside the test slots (RW_TEST_SLOTS_DIR, else %TEMP%\\rw-test-slots)."""
    return os.path.join(folder or test_slots.slots_folder(), FILE_NAME)


def nothing(why):
    """Measures that couldn't be taken: every one None, and why."""
    return {"committed_peak_bytes": None, "ram_peak_sampled_bytes": None, "ram_kind": None,
            "ram_with_shared_peak_sampled_bytes": None, "cpu_seconds": None, "io_read_bytes": None,
            "io_written_bytes": None, "processes": None, "missing": why}


SHARED_NOTE = "this Windows gives no private working set (PROCESS_MEMORY_COUNTERS_EX2) — whole working sets instead"


def ram_fields(peak, shared_peak, kind):
    """The record's RAM fields: the measure, its kind, why when it isn't the private one, and the shared-included sum."""
    return {"ram_peak_sampled_bytes": peak, "ram_kind": kind,
            **({"ram_note": SHARED_NOTE} if kind == "shared included" else {}),
            "ram_with_shared_peak_sampled_bytes": shared_peak}


# --- 1. measuring one unit's process tree (Windows job objects) ---------------------------------------------------------
if os.name == "nt":
    import ctypes
    from ctypes import wintypes as w

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)     # our own handle: the shared ctypes.windll is left alone
    _k32.CreateJobObjectW.restype, _k32.CreateJobObjectW.argtypes = w.HANDLE, [ctypes.c_void_p, w.LPCWSTR]
    _k32.OpenProcess.restype, _k32.OpenProcess.argtypes = w.HANDLE, [w.DWORD, w.BOOL, w.DWORD]
    _k32.OpenThread.restype, _k32.OpenThread.argtypes = w.HANDLE, [w.DWORD, w.BOOL, w.DWORD]
    _k32.CloseHandle.argtypes = [w.HANDLE]
    _k32.AssignProcessToJobObject.restype, _k32.AssignProcessToJobObject.argtypes = w.BOOL, [w.HANDLE, w.HANDLE]
    _k32.QueryInformationJobObject.restype = w.BOOL
    _k32.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD)]
    _k32.CreateToolhelp32Snapshot.restype, _k32.CreateToolhelp32Snapshot.argtypes = w.HANDLE, [w.DWORD, w.DWORD]
    _k32.ResumeThread.restype, _k32.ResumeThread.argtypes = w.DWORD, [w.HANDLE]
    _k32.K32GetProcessMemoryInfo.restype = w.BOOL
    _k32.K32GetProcessMemoryInfo.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD]

    CREATE_SUSPENDED = 0x00000004
    PROCESS_TERMINATE, PROCESS_SET_QUOTA, PROCESS_QUERY_LIMITED = 0x0001, 0x0100, 0x1000
    THREAD_SUSPEND_RESUME = 0x0002
    TH32CS_SNAPTHREAD = 0x00000004
    INVALID_HANDLE = w.HANDLE(-1).value
    BASIC_PROCESS_ID_LIST, BASIC_AND_IO_ACCOUNTING, EXTENDED_LIMIT = 3, 8, 9    # JOBOBJECTINFOCLASS

    class _Basic(ctypes.Structure):          # JOBOBJECT_BASIC_ACCOUNTING_INFORMATION (times in 100-ns ticks)
        _fields_ = [("TotalUserTime", ctypes.c_int64), ("TotalKernelTime", ctypes.c_int64),
                    ("ThisPeriodTotalUserTime", ctypes.c_int64), ("ThisPeriodTotalKernelTime", ctypes.c_int64),
                    ("TotalPageFaultCount", w.DWORD), ("TotalProcesses", w.DWORD), ("ActiveProcesses", w.DWORD),
                    ("TotalTerminatedProcesses", w.DWORD)]

    class _Io(ctypes.Structure):             # IO_COUNTERS — every kind of I/O: files, pipes, network
        _fields_ = [(n, ctypes.c_uint64) for n in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                                                   "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class _BasicAndIo(ctypes.Structure):     # JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION
        _fields_ = [("BasicInfo", _Basic), ("IoInfo", _Io)]

    class _Limits(ctypes.Structure):         # JOBOBJECT_BASIC_LIMIT_INFORMATION (we set none — read only)
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", w.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", w.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", w.DWORD), ("SchedulingClass", w.DWORD)]

    class _Extended(ctypes.Structure):       # JOBOBJECT_EXTENDED_LIMIT_INFORMATION — its peaks are COMMITTED memory
        _fields_ = [("BasicLimitInformation", _Limits), ("IoInfo", _Io), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    class _PidList(ctypes.Structure):        # JOBOBJECT_BASIC_PROCESS_ID_LIST, room for 1024 processes
        _fields_ = [("NumberOfAssignedProcesses", w.DWORD), ("NumberOfProcessIdsInList", w.DWORD),
                    ("ProcessIdList", ctypes.c_size_t * 1024)]

    class _Memory(ctypes.Structure):         # PROCESS_MEMORY_COUNTERS_EX2 (Windows 10 1709+; 96 bytes on x64)
        _fields_ = [("cb", w.DWORD), ("PageFaultCount", w.DWORD)] + [(n, ctypes.c_size_t) for n in (
            "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage",
            "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage",
            "PrivateUsage", "PrivateWorkingSetSize")] + [("SharedCommitUsage", ctypes.c_uint64)]

    _UNFILLED = 0xFFFFFFFFFFFF          # a value Windows never writes there: still there after the call → not given

    def _process_memory(pid):
        """(working set, private working set or None) of one process, in bytes — None for the whole if it can't be read
        (it just ended). The private working set — RAM only this process uses, the pages it shares (DLLs: Chrome's,
        Python's) left out — is PROCESS_MEMORY_COUNTERS_EX2's; a Windows without it leaves the field as it was, so it
        is preset to a value Windows never writes (checked 2026-11-18 on Windows 11 26200: a process holding 200 MB →
        203.9 MB, the same as WMI's WorkingSetPrivate for that process id)."""
        h = _k32.OpenProcess(PROCESS_QUERY_LIMITED, False, pid)
        if not h:
            return None
        try:
            m = _Memory()
            m.cb = ctypes.sizeof(_Memory)
            m.PrivateWorkingSetSize = _UNFILLED
            if not _k32.K32GetProcessMemoryInfo(h, ctypes.byref(m), m.cb):
                return None
            return m.WorkingSetSize, (None if m.PrivateWorkingSetSize == _UNFILLED else m.PrivateWorkingSetSize)
        finally:
            _k32.CloseHandle(h)

    class _Thread(ctypes.Structure):         # THREADENTRY32
        _fields_ = [("dwSize", w.DWORD), ("cntUsage", w.DWORD), ("th32ThreadID", w.DWORD),
                    ("th32OwnerProcessID", w.DWORD), ("tpBasePri", w.LONG), ("tpDeltaPri", w.LONG), ("dwFlags", w.DWORD)]

    _k32.Thread32First.restype = _k32.Thread32Next.restype = w.BOOL
    _k32.Thread32First.argtypes = _k32.Thread32Next.argtypes = [w.HANDLE, ctypes.POINTER(_Thread)]

    def _err(what):
        return f"{what} failed (Windows error {ctypes.get_last_error()})"

    def _query(job, cls, struct):
        if not _k32.QueryInformationJobObject(job, cls, ctypes.byref(struct), ctypes.sizeof(struct), None):
            raise OSError(_err("reading the job"))
        return struct

    def _resume(pid):
        """Let a process started suspended go: resume its one thread (found by a thread snapshot). True if resumed."""
        snap = _k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
        if not snap or snap == INVALID_HANDLE:
            return False
        resumed = False
        try:
            t = _Thread()
            t.dwSize = ctypes.sizeof(_Thread)
            more = _k32.Thread32First(snap, ctypes.byref(t))
            while more:
                if t.th32OwnerProcessID == pid:
                    h = _k32.OpenThread(THREAD_SUSPEND_RESUME, False, t.th32ThreadID)
                    if h:
                        resumed = _k32.ResumeThread(h) != 0xFFFFFFFF or resumed
                        _k32.CloseHandle(h)
                more = _k32.Thread32Next(snap, ctypes.byref(t))
        finally:
            _k32.CloseHandle(snap)
        return resumed

    class _Job:
        """One unit's job: made empty, the unit's process put in, sampled, read at the end, closed. No limits are set —
        no kill-on-close, no breakaway allowed: it only counts."""

        def __init__(self):
            self.handle = _k32.CreateJobObjectW(None, None)
            if not self.handle:
                raise OSError(_err("making a job object"))
            self.ram_peak, self.shared_peak, self.ram_kind = None, None, None
            self._stop, self._thread = threading.Event(), None

        def adopt(self, pid):
            """Put the suspended process in the job; None, or why it couldn't be (it is NOT resumed here)."""
            h = _k32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid)
            if not h:
                return _err("opening the test's process")
            try:
                return None if _k32.AssignProcessToJobObject(self.handle, h) else _err("putting it in the job")
            finally:
                _k32.CloseHandle(h)

        def ram_now(self):
            """(the working sets of the processes in the job right now, added up — shared pages counted in each; their
            PRIVATE working sets added up, or None if any process's couldn't be given)."""
            ids = _query(self.handle, BASIC_PROCESS_ID_LIST, _PidList())
            total, private = 0, 0
            for pid in ids.ProcessIdList[:min(ids.NumberOfProcessIdsInList, 1024)]:
                got = _process_memory(pid)
                if got is None:
                    continue        # it just ended
                total += got[0]
                private = None if private is None or got[1] is None else private + got[1]
            return total, private

        def start_sampling(self):
            def loop():
                wait = FIRST_SAMPLE_S
                while not self._stop.wait(wait):
                    try:
                        total, private = self.ram_now()
                    except OSError:
                        return
                    # The RAM measure is the private sum; where this Windows can't give it, the whole sum — and once a
                    # sample lacks it, the whole unit is the whole sum (one kind per unit, never mixed).
                    if private is None and self.ram_kind != "shared included":
                        self.ram_kind, self.ram_peak = "shared included", self.shared_peak
                    elif self.ram_kind is None:
                        self.ram_kind = "private"
                    now = private if self.ram_kind == "private" else total
                    self.ram_peak = now if self.ram_peak is None else max(self.ram_peak, now)
                    self.shared_peak = total if self.shared_peak is None else max(self.shared_peak, total)
                    wait = SAMPLE_S
            self._thread = threading.Thread(target=loop, name="rw-test-costs-sampler", daemon=True)
            self._thread.start()

        def finish(self):
            """The measures (the process has ended) — and the job closed. Processes still running stay running."""
            self._stop.set()
            if self._thread:
                self._thread.join(5)
            try:
                acc = _query(self.handle, BASIC_AND_IO_ACCOUNTING, _BasicAndIo())
                ext = _query(self.handle, EXTENDED_LIMIT, _Extended())
                return {"committed_peak_bytes": int(ext.PeakJobMemoryUsed),
                        **ram_fields(self.ram_peak, self.shared_peak, self.ram_kind),
                        "cpu_seconds": round((acc.BasicInfo.TotalUserTime + acc.BasicInfo.TotalKernelTime) / 1e7, 2),
                        "io_read_bytes": int(acc.IoInfo.ReadTransferCount),
                        "io_written_bytes": int(acc.IoInfo.WriteTransferCount),
                        "processes": int(acc.BasicInfo.TotalProcesses)}
            except OSError as e:
                return nothing(str(e))
            finally:
                self.close()

        def close(self):
            if self.handle:
                _k32.CloseHandle(self.handle)
                self.handle = None


def available():
    """(True, None) if this PC can measure — else (False, why, in words)."""
    if os.name != "nt":
        return False, "not Windows — the measures come from Windows job objects"
    return True, None


def run(cmd, timeout=None, measure=True, **popen_kw):
    """subprocess.run(cmd, capture_output=True, timeout=timeout, **popen_kw), measured: (exit code — None when it ran past
    `timeout` and was stopped —, stdout bytes, stderr bytes, measures). measure False: run as before, measures all None.
    Anything about measuring that fails leaves the run itself as it would have been: measures None, and why."""
    ok, why = available() if measure else (False, "not asked")
    job = None
    if ok:
        try:
            job = _Job()
        except Exception as e:      # noqa: BLE001 — measuring never fails a run
            why = f"{e}"
    flags = popen_kw.pop("creationflags", 0) | (CREATE_SUSPENDED if job else 0)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=flags, **popen_kw)
    with p:
        if job:
            why = job.adopt(p.pid)          # in the job BEFORE it runs a single instruction: nothing it starts escapes
            if not _resume(p.pid):          # never left suspended: stopped by its own handle (exact) and run unmeasured
                p.kill()
                p.communicate()
                job.close()
                code, out, err, _ = run(cmd, timeout=timeout, measure=False, **popen_kw)
                return code, out, err, nothing(_err("letting the test's process go") + " — run again unmeasured")
            if why:
                job.close()
                job = None
            else:
                job.start_sampling()
        try:
            out, err = p.communicate(timeout=timeout)
            code = p.returncode
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            code = None
        except BaseException:
            p.kill()
            raise
        finally:
            measures = job.finish() if job else None
    return code, out, err, measures if measures is not None else nothing(why)


def combine(parts):
    """A sharded file's measures from its shards' (they ran side by side): CPU, I/O and processes added up; each peak the
    largest shard's (their sum would claim they all peaked at once). A measure any shard lacks is None."""
    parts = [p or nothing("not measured") for p in parts]
    out = {}
    for k in ("cpu_seconds", "io_read_bytes", "io_written_bytes", "processes", "committed_peak_bytes",
              "ram_peak_sampled_bytes", "ram_with_shared_peak_sampled_bytes"):
        vals = [p.get(k) for p in parts]
        if not vals or any(v is None for v in vals):
            out[k] = None
        elif "peak" in k:
            out[k] = max(vals)
        else:
            out[k] = round(sum(vals), 2) if k == "cpu_seconds" else sum(vals)
    kinds = {p.get("ram_kind") for p in parts}
    kind = kinds.pop() if len(kinds) == 1 else None          # shards of different kinds: no one RAM figure
    if kind is None:
        out["ram_peak_sampled_bytes"] = None
    out.update(ram_fields(out["ram_peak_sampled_bytes"], out["ram_with_shared_peak_sampled_bytes"], kind))
    why = "; ".join(sorted({p["missing"] for p in parts if p.get("missing")}))
    return dict(out, **({"missing": why} if why else {}), shards=len(parts))


# --- 2. the running averages, per PC ------------------------------------------------------------------------------------
def smooth(stat, sample):
    """One measure's running average after one more sample — RFC 6298 (TCP's round-trip time): the spread moves a quarter
    of the way to |sample − average| (the OLD average), then the average an eighth of the way to the sample; the first
    sample sets average = sample, spread = sample/2. stat: {avg, spread, count, last} or None. Pure: a new dict."""
    if not stat or not stat.get("count"):
        return {"avg": sample, "spread": sample / 2, "count": 1, "last": sample}
    avg, spread = stat["avg"], stat["spread"]
    spread += (abs(sample - avg) - spread) / 4
    avg += (sample - avg) / 8
    return {"avg": avg, "spread": spread, "count": stat["count"] + 1, "last": sample}


def unit_key(shard, of):
    """A unit's name within its file: "whole", or "shard 2 of 4"."""
    return "whole" if shard is None else f"shard {shard} of {of}"


def file_hash(path):
    """The test file's contents, hashed — a changed file starts its history over. None if it can't be read."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def left_out(narrowed, passed, rerun):
    """Why this unit's sample may NOT teach the average (Karn's rule — an ambiguous sample is dropped, not risked), or
    None when it may: it ran in full (narrowed: what narrowed the run, in words — [] for none) and passed, the first time."""
    if narrowed:
        return "a narrowed run (" + "; ".join(narrowed) + ")"
    if not passed:
        return "it failed"
    if rerun:
        return "a rerun alone after the machine's trouble"
    return None


def fresh():
    return {"version": 1, "files": {}}


def load(path):
    """(state, note) — note None when read; a missing or damaged file → a fresh state, and the note says so."""
    try:
        with open(path, encoding="utf-8") as f:
            s = json.load(f)
    except FileNotFoundError:
        return fresh(), "no costs measured on this PC yet"
    except (OSError, ValueError) as e:
        return fresh(), f"the costs file couldn't be read ({type(e).__name__}: {path}) — starting again"
    if not isinstance(s, dict) or not isinstance(s.get("files"), dict):
        return fresh(), f"the costs file couldn't be read (damaged: {path}) — starting again"
    return s, None


def learn(state, samples, when):
    """The state after these samples — [{file, tier, hash, unit, seconds, measures}], each one that may teach (left_out
    None). A file whose hash differs from the one kept starts over. The RAM average holds one kind (ram_kind: private,
    or shared included): a sample of another kind starts that measure over. Pure: a new state."""
    files = json.loads(json.dumps(state.get("files") or {}))
    for s in samples:
        entry = files.get(s["file"])
        if not entry or entry.get("hash") != s.get("hash"):
            entry = files[s["file"]] = {"hash": s.get("hash"), "tier": s.get("tier"), "units": {}}
        entry["tier"] = s.get("tier")
        unit = entry["units"].setdefault(s["unit"], {"count": 0, "measures": {}})
        values = dict(s.get("measures") or {}, seconds=s.get("seconds"))
        if isinstance(values.get("ram_peak_sampled_bytes"), (int, float)):
            if unit.get("ram_kind") != values.get("ram_kind"):
                unit["measures"].pop("ram_peak_sampled_bytes", None)
            unit["ram_kind"] = values.get("ram_kind")
        for m in MEASURES:
            v = values.get(m)
            if isinstance(v, (int, float)):
                unit["measures"][m] = smooth(unit["measures"].get(m), v)
        unit["count"] += 1
        unit["when"] = when
    return {"version": 1, "files": files}


@contextlib.contextmanager
def _held(path):
    with test_slots.locked(path + ".lock", limit_s=LOCK_LIMIT_S) as got:
        yield got


def teach(path, samples, when=None):
    """Add the samples to this PC's averages — read, merged and written under the lock, so runs finishing together each
    add theirs. None, or why they couldn't be saved, in words (a run never fails on it)."""
    if not samples:
        return None
    when = when or datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        with _held(path) as got:
            if not got:
                return f"another run held {path}'s lock for {LOCK_LIMIT_S:g} s — this run's costs weren't saved"
            state, _ = load(path)
            return browser_level.save(path, learn(state, samples, when))
    except OSError as e:
        return f"the costs couldn't be saved to {path}: {e}"


def read(path):
    """(state, note) — load(), under the lock (a save may be putting the file in place right now)."""
    try:
        with _held(path):
            return load(path)
    except OSError as e:
        return fresh(), f"the costs file couldn't be read ({e})"


# --- 3. the report ------------------------------------------------------------------------------------------------------
def _mb(b, spread=None):
    """'600 MB' / '1.25 GB' — with a spread, both in the average's unit: '600 ± 50 MB'. '—' for None."""
    if b is None:
        return "—"
    div, unit, fmt = (2 ** 30, "GB", "{:.2f}") if b >= 2 ** 30 else (2 ** 20, "MB", "{:.0f}")
    return fmt.format(b / div) + ("" if spread is None else " ± " + fmt.format(spread / div)) + f" {unit}"


def _sec(s, spread=None):
    """'60.0 s' — with a spread: '60.0 ± 5.0 s'. '—' for None."""
    return "—" if s is None else f"{s:.1f}" + ("" if spread is None else f" ± {spread:.1f}") + " s"


def _pm(stat, fmt):
    """'average ± spread' in the measure's own unit — or '—' (never measured)."""
    return "—" if not stat else fmt(stat["avg"], stat["spread"])


def table(state, note=None, where=""):
    """The --costs report, as lines."""
    rows = []
    for name, entry in (state.get("files") or {}).items():
        for key, unit in (entry.get("units") or {}).items():
            rows.append((name + ("" if key == "whole" else f" ({key})"), entry.get("tier"), unit))
    out = [f"What each test costs this PC — average ± spread over the runs that taught it (only full runs that passed) "
           f"— {where}" + (f" ({note})" if note else "")]
    if not rows:
        out.append("  Nothing measured yet: a full run (py tools/run_tests.py --tier 1, --tier 2 or --tier all) teaches it.")
        return out
    rows.sort(key=lambda r: -((r[2]["measures"].get("seconds") or {}).get("avg") or 0))
    cols = [("Test", None), ("Runs", None), ("Time", _sec), ("Memory committed (peak)", _mb),
            ("RAM, private (sampled peak)", _mb), ("CPU", _sec), ("I/O read", _mb), ("I/O written", _mb)]
    keys = [None, None, "seconds", "committed_peak_bytes", "ram_peak_sampled_bytes", "cpu_seconds", "io_read_bytes",
            "io_written_bytes"]

    def cell(u, k, fmt):
        text = _pm(u["measures"].get(k), fmt)
        return text + " *" if k == "ram_peak_sampled_bytes" and u.get("ram_kind") == "shared included" else text
    body = [[name, str(u.get("count", 0))] + [cell(u, k, fmt) for k, (_, fmt) in zip(keys[2:], cols[2:])]
            for name, _, u in rows]

    def total(k):
        vals = [v for v in ((u["measures"].get(k) or {}).get("avg") for _, _, u in rows) if v is not None]
        return sum(vals) if vals else None
    totals = ["Total (one run of each, one after another)", ""] + [
        fmt(total(k)) if k in ("seconds", "cpu_seconds", "io_read_bytes", "io_written_bytes") else "—"
        for k, (_, fmt) in zip(keys[2:], cols[2:])]
    widths = [max(len(c[0]), *(len(r[i]) for r in body + [totals])) for i, c in enumerate(cols)]

    def line(cells):
        return "  " + "  ".join(c.ljust(widths[0]) if i == 0 else c.rjust(widths[i]) for i, c in enumerate(cells))
    out.append(line([c[0] for c in cols]))
    out += [line(r) for r in body] + [line(totals)]
    out.append("  Memory committed = what the processes asked Windows to guarantee them (RAM or page file) — not RAM in "
               "use. RAM, private = what the test adds to the PC's RAM: each process's own pages, added up about once a "
               "second (pages shared between processes left out). I/O = files, pipes and network, not only the disk.")
    if any(u.get("ram_kind") == "shared included" for _, _, u in rows):
        out.append("  * shared pages included — " + SHARED_NOTE)
    screen = [(name, (u["measures"].get("ram_peak_sampled_bytes") or {}).get("avg")) for name, tier, u in rows
              if tier == 2 and u.get("ram_kind") != "shared included"]      # one kind compared with itself only
    screen = [(n, v) for n, v in screen if v]
    if len(screen) >= 2:
        big, small = max(screen, key=lambda x: x[1]), min(screen, key=lambda x: x[1])
        ratio = big[1] / small[1]
        out.append(f"  Screen tests differ in RAM by {ratio:.1f}× — the biggest average private RAM peak (sampled) is "
                   f"{big[0]} ({_mb(big[1])}), the smallest {small[0]} ({_mb(small[1])}) — "
                   + ("at least twice: worth a budget by memory" if ratio >= 2 else "less than twice"))
    else:
        out.append("  Screen tests differ in RAM by: not known yet — fewer than two screen-test units have a private RAM "
                   "peak.")
    return out
