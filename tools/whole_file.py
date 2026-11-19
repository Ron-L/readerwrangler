"""
whole_file.py — the one way a tool writes a file whole (Law 22; TODO "Working-process safety net", sprint 9 item 4).

write(path, text) writes a scratch copy beside the file, then swaps it in — a reader never sees half a file. The scratch
copy is named for this process and thread, so two servers (or two threads) writing the same file never share one.

Windows refuses the swap while another program is reading the old copy (another server sending it — 2026-11-16), and now
and then right after the file was rewritten (six runs saving test costs at once — 2026-11-18). So a refused swap
(PermissionError) is retried, SWAP_TRIES times SWAP_PAUSE_S apart (~2 s in all). Still refused: the scratch copy is
removed, the old file is left whole, and the PermissionError is raised. Any other failure stops at once, the same way.

Used by tools/build.py (dist/, LF line endings) and tools/browser_level.py (save — also how tools/test_costs.py writes).
Before 2026-11-18 each had its own copy of this loop. Tested by test/test_whole_file.py (WHOLE-001–006).
"""
import os
import threading
import time

SWAP_TRIES, SWAP_PAUSE_S = 20, 0.1      # ~2 s in all


def write(path, text, newline=None):
    """Write `text` (UTF-8) to `path` whole. newline: as open()'s — None writes the system's ending, "\\n" keeps LF."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8", newline=newline) as f:
            f.write(text)
        for attempt in range(SWAP_TRIES):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if attempt == SWAP_TRIES - 1:
                    raise
                time.sleep(SWAP_PAUSE_S)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
