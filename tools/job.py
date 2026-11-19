"""
job.py — run a process in a Windows job: everything it starts is measured, and ended with it.

    code, out, err, measures = job.run(cmd, timeout=600, cwd=…, env=…)    # one test unit (tools/run_tests.py)

    j = job.new()                         # a job of our own (or, where none can be made, a stand-in — below)
    p, why = j.launch(cmd, **popen_kw)    # started inside the job before it runs a single instruction
    j.running()                           # the ids of the processes in it right now
    left = j.end()                        # every process in it stopped, by the job's handle; [] once all are gone
    measures = j.finish()                 # what it cost (below) — and the job closed

KILL-ON-CLOSE: Windows ends every process in the job when the job's last handle closes — when we close it, and when the
process holding it ends for any reason (the runner crashes, its window is closed, it is stopped). A process can't leave
its job (breakaway is never allowed; Chrome's own jobs sit inside ours), so nothing a test starts outlives it. Used for
each test unit (run(), below), the relay tests' local relay (tools/local_relay.py) and the screen tests' web server
(test/ui/rw.py).

WHAT IT COST — for the whole process tree, exited processes included; kept in each run's record:
    committed_peak_bytes     the most private memory (commit charge: RAM or page file) the tree held at once — NOT RAM
    ram_peak_sampled_bytes   the highest sum of the processes' PRIVATE working sets, sampled about once a second (what
                             the test adds to the PC's RAM; ram_kind "private"). A Windows without that figure: whole
                             working sets, shared pages counted in each (ram_kind "shared included", ram_note why).
                             The shared-included sum is kept beside it (ram_with_shared_peak_sampled_bytes)
    cpu_seconds              user + kernel time of every process in the tree
    io_read_bytes, io_written_bytes   all I/O — files, pipes and network, not only the disk
    processes                how many processes the tree started in all
    left_running             how many were still running when the unit's own process ended (run(): ended with its job)
Not on Windows, or anything about the job fails: every measure is None, `missing` says why, and the process runs exactly
as it would have without a job (a stand-in that stops what it started by its own handle — a process group elsewhere).

Tested by test/test_job.py.
"""
import os
import subprocess
import threading
import time

FIRST_SAMPLE_S, SAMPLE_S = 0.25, 1.0        # the RAM sample: a quarter second after the start, then once a second
END_WAIT_S = 10.0                           # end() waits this long at most for every process to be gone
_POLL_S = 0.5                               # run(): how often it looks whether the unit's own process has ended


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


# --- a Windows job ------------------------------------------------------------------------------------------------------
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
    _k32.SetInformationJobObject.restype = w.BOOL
    _k32.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
    _k32.CreateToolhelp32Snapshot.restype, _k32.CreateToolhelp32Snapshot.argtypes = w.HANDLE, [w.DWORD, w.DWORD]
    _k32.ResumeThread.restype, _k32.ResumeThread.argtypes = w.DWORD, [w.HANDLE]
    _k32.K32GetProcessMemoryInfo.restype = w.BOOL
    _k32.K32GetProcessMemoryInfo.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD]
    _k32.TerminateJobObject.restype, _k32.TerminateJobObject.argtypes = w.BOOL, [w.HANDLE, w.UINT]

    CREATE_SUSPENDED = 0x00000004
    PROCESS_TERMINATE, PROCESS_SET_QUOTA, PROCESS_QUERY_LIMITED = 0x0001, 0x0100, 0x1000
    THREAD_SUSPEND_RESUME = 0x0002
    TH32CS_SNAPTHREAD = 0x00000004
    INVALID_HANDLE = w.HANDLE(-1).value
    BASIC_PROCESS_ID_LIST, BASIC_AND_IO_ACCOUNTING, EXTENDED_LIMIT = 3, 8, 9    # JOBOBJECTINFOCLASS
    KILL_ON_JOB_CLOSE = 0x00002000          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

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

    class _Limits(ctypes.Structure):         # JOBOBJECT_BASIC_LIMIT_INFORMATION
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
        (it just ended). A Windows without PROCESS_MEMORY_COUNTERS_EX2 leaves the private field as it was, so it is preset
        to a value Windows never writes."""
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

    def _query(handle, cls, struct):
        if not _k32.QueryInformationJobObject(handle, cls, ctypes.byref(struct), ctypes.sizeof(struct), None):
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
        """A Windows job with kill-on-close set: made empty, processes started in it, sampled, read, closed. Its handle is
        never inherited, so only this process holds it — when this process ends, so does everything in the job."""

        def __init__(self):
            self.handle = _k32.CreateJobObjectW(None, None)
            if not self.handle:
                raise OSError(_err("making a job object"))
            info = _Extended()
            info.BasicLimitInformation.LimitFlags = KILL_ON_JOB_CLOSE
            if not _k32.SetInformationJobObject(self.handle, EXTENDED_LIMIT, ctypes.byref(info), ctypes.sizeof(info)):
                why = _err("setting the job to end its processes when it closes")
                _k32.CloseHandle(self.handle)
                raise OSError(why)
            self.ram_peak, self.shared_peak, self.ram_kind = None, None, None
            self._stop, self._thread = threading.Event(), None
            self.missing = None         # why a process couldn't be put in it (it then runs outside — launch())

        def launch(self, cmd, **popen_kw):
            """subprocess.Popen(cmd, **popen_kw) — in this job before it runs a single instruction: started suspended,
            put in the job, let go. (the process, None) — or (the process, why) when it couldn't be put in the job: it
            then runs outside it (one that couldn't be let go is stopped by its own handle and started again, outside)."""
            flags = popen_kw.pop("creationflags", 0)
            p = subprocess.Popen(cmd, creationflags=flags | CREATE_SUSPENDED, **popen_kw)
            why = self._adopt(p.pid)
            if not _resume(p.pid):
                why = _err("letting the process go") + " — started again, outside the job"
                p.kill()
                p.communicate()
                p = subprocess.Popen(cmd, creationflags=flags, **popen_kw)
            if why:
                self.missing = why
            elif self._thread is None:
                self._start_sampling()
            return p, why

        def _adopt(self, pid):
            h = _k32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid)
            if not h:
                return _err("opening the process")
            try:
                return None if _k32.AssignProcessToJobObject(self.handle, h) else _err("putting it in the job")
            finally:
                _k32.CloseHandle(h)

        def running(self):
            """The ids of the processes in the job right now (each one ours: a process can't leave its job)."""
            if not self.handle:
                return []
            ids = _query(self.handle, BASIC_PROCESS_ID_LIST, _PidList())
            return [int(p) for p in ids.ProcessIdList[:min(ids.NumberOfProcessIdsInList, 1024)]]

        def _ram_now(self):
            """(the working sets in the job right now, added up — shared pages counted in each; their PRIVATE working
            sets added up, or None if any process's couldn't be given)."""
            total, private = 0, 0
            for pid in self.running():
                got = _process_memory(pid)
                if got is None:
                    continue        # it just ended
                total += got[0]
                private = None if private is None or got[1] is None else private + got[1]
            return total, private

        def _start_sampling(self):
            def loop():
                wait = FIRST_SAMPLE_S
                while not self._stop.wait(wait):
                    try:
                        total, private = self._ram_now()
                    except OSError:
                        return
                    # One kind per job, never mixed: once a sample lacks the private figure, it is the whole sum.
                    if private is None and self.ram_kind != "shared included":
                        self.ram_kind, self.ram_peak = "shared included", self.shared_peak
                    elif self.ram_kind is None:
                        self.ram_kind = "private"
                    now = private if self.ram_kind == "private" else total
                    self.ram_peak = now if self.ram_peak is None else max(self.ram_peak, now)
                    self.shared_peak = total if self.shared_peak is None else max(self.shared_peak, total)
                    wait = SAMPLE_S
            self._thread = threading.Thread(target=loop, name="rw-job-sampler", daemon=True)
            self._thread.start()

        def end(self, wait_s=END_WAIT_S):
            """Stop every process in the job, by the job's own handle, and wait until they're gone: the ids still there
            after wait_s ([] = all gone)."""
            if not self.handle:
                return []
            _k32.TerminateJobObject(self.handle, 1)
            deadline = time.monotonic() + wait_s
            while (left := self.running()) and time.monotonic() < deadline:
                time.sleep(0.05)
            return left

        def finish(self):
            """What it cost (the measures) — then the job closed, ending whatever still runs in it."""
            self._stop.set()
            if self._thread:
                self._thread.join(5)
            try:
                if self.missing:
                    return nothing(self.missing)
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
else:
    def _Job():
        raise OSError("not Windows — the measures come from Windows job objects")


class _NoJob:
    """The stand-in where no job can be made: the same calls; what it started is stopped by its own handle (elsewhere
    than Windows: its whole process group — it is started in a session of its own)."""

    def __init__(self, why):
        self.missing, self.procs = why, []

    def launch(self, cmd, **popen_kw):
        if os.name != "nt":
            popen_kw.setdefault("start_new_session", True)
        p = subprocess.Popen(cmd, **popen_kw)
        self.procs.append(p)
        return p, self.missing

    def running(self):
        return [p.pid for p in self.procs if p.poll() is None]

    def end(self, wait_s=END_WAIT_S):
        for p in self.procs:
            try:
                if os.name != "nt":
                    import signal
                    os.killpg(p.pid, signal.SIGKILL)
                else:
                    p.kill()
            except OSError:
                pass
        deadline = time.monotonic() + wait_s
        while (left := self.running()) and time.monotonic() < deadline:
            time.sleep(0.05)
        return left

    def finish(self):
        self.end()
        return nothing(self.missing)

    def close(self):
        self.end()


def new():
    """A job of our own — or, when none can be made (not Windows, or Windows refused), the stand-in, saying why."""
    try:
        return _Job()
    except Exception as e:      # noqa: BLE001 — a job never stops a process from running
        return _NoJob(str(e))


def run(cmd, timeout=None, **popen_kw):
    """subprocess.run(cmd, capture_output=True, timeout=timeout, **popen_kw) in a job of its own: (exit code — None when
    it ran past `timeout` and was stopped, with everything it started —, stdout bytes, stderr bytes, measures). Once its
    own process ends, whatever it left running is counted (left_running) and ended — at once, since a leftover may hold
    its output pipes open (the wait would otherwise last until the time limit)."""
    j = new()
    p, _ = j.launch(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **popen_kw)
    left = None
    deadline = None if timeout is None else time.monotonic() + timeout
    with p:
        try:
            while True:
                step = _POLL_S if deadline is None else max(0.0, min(_POLL_S, deadline - time.monotonic()))
                try:
                    out, err = p.communicate(timeout=step)
                    break
                except subprocess.TimeoutExpired:
                    if deadline is not None and time.monotonic() >= deadline:
                        raise
                    if p.poll() is not None and left is None:     # it ended; something it started holds its pipes
                        left = len(j.running())
                        j.end()
            code = p.returncode
            if left is None:
                left = len(j.running())
        except subprocess.TimeoutExpired:
            j.end()
            p.kill()            # (by its own handle — when it runs outside a job)
            out, err = p.communicate()
            code = None
        except BaseException:
            p.kill()
            raise
        finally:
            measures = j.finish()
    if measures.get("missing") is None:
        measures["left_running"] = left
    return code, out, err, measures


def combine(parts):
    """A sharded file's measures from its shards' (they ran side by side): CPU, I/O, processes and what was left running
    added up; each peak the largest shard's (their sum would claim they all peaked at once). A measure any shard lacks is
    None."""
    parts = [p or nothing("not measured") for p in parts]
    out = {}
    for k in ("cpu_seconds", "io_read_bytes", "io_written_bytes", "processes", "left_running", "committed_peak_bytes",
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
