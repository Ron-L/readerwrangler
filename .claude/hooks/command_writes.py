"""command_writes.py — which files does a terminal command WRITE? Read from the command's text (2026-11-16).

The pre-build gate (gate-check.py) fired only for the Edit / Write tools, so a change made from a terminal command
skipped it — twice in one week an agent moved version stamps with `sed`, though its brief said not to (TODO tooling
task, open item 1; decided Ron 2026-11-16). The gate now asks this module for the files a Bash or PowerShell command
writes, then asks the SAME shipped-code rule it asks for an edit (is_app_source → git-hooks/shipped_paths.py).

Best effort, and it never guesses: a target it can't tell (a variable, a script that writes who-knows-where, a list fed
through xargs or a loop) is left out, so the command passes. What it reads:
  - redirects:  > >> >| &> &>> N>  (not N>&M, not /dev/null)            — any command, git's output included
  - sed -i / --in-place, perl -i, awk -i inplace                         — the files they edit
  - tee, cp, mv (incl. -t DIR and a folder as the destination), dd of=   — the files written
  - PowerShell: Set-Content, Add-Content, Out-File, Tee-Object, New-Item, Copy-Item, Move-Item (+ their aliases),
    > redirects, [IO.File]::WriteAll…/AppendAll…
  - python / py / node one-liners (-c / -e, or a heredoc fed to them): open(…, 'w'/'a'/'x'/'+'), Path(…).write_text /
    write_bytes, shutil.copy*/move, os.replace/rename, fs.writeFileSync/appendFileSync/copyFileSync/createWriteStream
  - bash -c / sh -c / powershell -Command: the inner command, read the same way
  - cd / pushd / Set-Location earlier in the command: later paths are taken from there; Git Bash's /c/… is C:/…
Not read (they pass): rm / del / Remove-Item (a deletion, not an edit), patch / git apply, scripts run from a file,
targets in variables or loops, xargs / find -exec.

Used by .claude/hooks/gate-check.py. Tested by test/test_gate_check.py (GATE-002–009).
"""
import glob
import os
import re

# ── Reading the text into words and operators ────────────────────────────────────────────────────────────────────────
# Longest first: the tokenizer takes the longest operator that matches.
OPERATORS = ("&>>", "<<<", "<<-", "&&", "||", ";;", "|&", "&>", ">>", ">&", ">|", "<<", "<&", "<>",
             ";", "&", "|", "<", ">", "(", ")", "\n")
OP_START = set("&|;<>()\n")
HEREDOC = re.compile(r"(?<!<)<<-?[ \t]*(['\"]?)([A-Za-z_][\w.-]*)\1")
PS_HERESTRING = re.compile(r"@(['\"])\r?\n.*?\r?\n\1@", re.S)
PLACEHOLDER = "__RW_TEXT_%d__"
PLACEHOLDER_RE = re.compile(r"__RW_TEXT_(\d+)__")


def take_heredocs(command):
    """Bash heredoc bodies cut out of the command (their text is data, not commands: a `>` in a commit message must not
    read as a redirect). Each marker becomes `<< __RW_TEXT_n__`; returns (command, [bodies])."""
    bodies, out, pos = [], [], 0
    while True:
        m = HEREDOC.search(command, pos)
        if not m:
            out.append(command[pos:])
            break
        word = m.group(2)
        line_end = command.find("\n", m.end())
        out.append(command[pos:m.start()] + "<< " + PLACEHOLDER % len(bodies))
        if line_end < 0:                                   # no body follows: nothing to cut
            bodies.append("")
            pos = m.end()
            continue
        end = re.compile(r"^\t*" + re.escape(word) + r"[ \t]*$", re.M).search(command, line_end + 1)
        bodies.append(command[line_end + 1:end.start() if end else len(command)])
        out.append(command[m.end():line_end + 1])          # the rest of the marker's line stays a command
        pos = end.end() if end else len(command)
    return "".join(out), bodies


def take_herestrings(command):
    """PowerShell here-strings (@' … '@ / @" … "@) cut out the same way; each becomes one word."""
    bodies = []

    def cut(m):
        bodies.append(m.group(0))
        return " " + PLACEHOLDER % (len(bodies) - 1) + " "
    return PS_HERESTRING.sub(cut, command), bodies


def tokenize(s, ps):
    """[(kind, text)]: kind 'w' = a word (quotes removed), 'op' = an operator. Bash: backslash escapes, '…' literal,
    "…" with \\ escapes. PowerShell: backtick escapes, '' inside '…'. A # at a word's start runs to the line's end."""
    esc = "`" if ps else "\\"
    toks, cur, i, n = [], None, 0, len(s)

    def flush():
        nonlocal cur
        if cur is not None:
            toks.append(("w", "".join(cur)))
            cur = None
    while i < n:
        c = s[i]
        if c in " \t\r":
            flush()
            i += 1
        elif c == "'":
            j = i + 1
            buf = []
            while j < n:
                if s[j] == "'":
                    if ps and j + 1 < n and s[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(s[j])
                j += 1
            cur = (cur or []) + buf
            i = j + 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n and s[j] != '"':
                if s[j] == esc and j + 1 < n and (ps or s[j + 1] in '"\\$`\n'):
                    buf.append(s[j + 1])
                    j += 2
                    continue
                buf.append(s[j])
                j += 1
            cur = (cur or []) + buf
            i = j + 1
        elif c == esc and i + 1 < n:
            if s[i + 1] != "\n":
                cur = (cur or []) + [s[i + 1]]
            i += 2
        elif c == "#" and cur is None:
            j = s.find("\n", i)
            i = n if j < 0 else j
        elif c in OP_START:
            flush()
            op = next(o for o in OPERATORS if s.startswith(o, i))
            toks.append(("op", op))
            i += len(op)
        else:
            cur = (cur or []) + [c]
            i += 1
    flush()
    return toks


def segments(toks):
    """Simple commands: [(words, redirect_targets, text_ids)] — split at ; && || | & ( ) and line ends.
    text_ids: the cut-out heredoc / here-string bodies this command reads."""
    out, words, reds, texts = [], [], [], []
    i = 0
    while i < len(toks):
        kind, t = toks[i]
        nxt = toks[i + 1][1] if i + 1 < len(toks) and toks[i + 1][0] == "w" else None
        if kind == "w":
            m = PLACEHOLDER_RE.fullmatch(t)
            if m:
                texts.append(int(m.group(1)))
            else:
                words.append(t)
        elif ">" in t:                                     # a write redirect … unless it copies a stream (2>&1, >&-)
            if nxt is not None:
                if not (t == ">&" and re.fullmatch(r"\d+|-", nxt)):
                    reds.append(nxt)
                i += 1
        elif "<" in t:                                     # an input redirect: its word is read, not a command word
            if nxt is not None:
                m = PLACEHOLDER_RE.fullmatch(nxt)
                if m:
                    texts.append(int(m.group(1)))
                i += 1
        else:                                              # a separator
            out.append((words, reds, texts))
            words, reds, texts = [], [], []
        i += 1
    out.append((words, reds, texts))
    return [s for s in out if s[0] or s[1] or s[2]]


# ── Paths ────────────────────────────────────────────────────────────────────────────────────────────────────────────
NOWHERE = {"/dev/null", "/dev/stdout", "/dev/stderr", "nul", "$null", "-"}
GLOB_CHARS = set("*?[")


def expand(word, ps):
    """A word's variables filled in where the environment has them; None when one is left unknown (can't tell)."""
    if ps:
        word = re.sub(r"\$env:(\w+)", lambda m: os.environ.get(m.group(1), m.group(0)), word, flags=re.I)
    else:
        word = os.path.expandvars(word)
    return None if "$" in word else word


def resolve(word, cwd, ps):
    """A written word as an absolute path, or None (nowhere, or can't tell)."""
    if not word or word.lower() in NOWHERE:
        return None
    word = expand(word, ps)
    if not word or word.startswith("/dev/"):
        return None
    word = os.path.expanduser(word)
    m = re.match(r"^/([A-Za-z])(/|$)", word)              # Git Bash: /c/Users/… is C:/Users/…
    if m and os.name == "nt":
        word = m.group(1).upper() + ":/" + word[3:]
    return os.path.normpath(os.path.join(cwd, word))


def resolve_all(word, cwd, ps):
    """resolve(), with a wildcard expanded against the files that exist (no match: the word as written)."""
    p = resolve(word, cwd, ps)
    if p is None:
        return []
    if GLOB_CHARS & set(os.path.basename(p)):
        return sorted(glob.glob(p)) or [p]
    return [p]


def into(dest, sources, cwd, ps, folder=False):
    """cp/mv-style destination: a folder (named as one, existing, or several sources) gets each source's own name."""
    d = resolve(dest, cwd, ps)
    if d is None:
        return []
    if folder or len(sources) > 1 or dest.endswith(("/", "\\")) or os.path.isdir(d):
        out = []
        for s in sources:
            names = [os.path.basename(p) for p in resolve_all(s, cwd, ps)] or [os.path.basename(s)]
            out += [os.path.join(d, nm) for nm in names if nm]
        return out
    return [d]


# ── What each command writes ─────────────────────────────────────────────────────────────────────────────────────────
def sed_writes(args):
    inplace, script_given, pos, i = False, False, [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            pos += args[i + 1:]
            break
        if a.startswith("--"):
            name, eq, _ = a[2:].partition("=")
            if name == "in-place":
                inplace = True
            elif name in ("expression", "file"):
                script_given = True
                i += 0 if eq else 1
            elif name == "line-length" and not eq:
                i += 1
        elif a.startswith("-") and len(a) > 1:
            for j, c in enumerate(a[1:], 1):
                if c == "i":                               # -i[SUFFIX]: the rest of the cluster is the suffix
                    inplace = True
                    break
                if c in "efl":                             # takes a value: the rest, or the next word
                    script_given = script_given or c != "l"
                    if j == len(a) - 1:
                        i += 1
                    break
        else:
            pos.append(a)
        i += 1
    if not inplace:
        return []
    return pos if script_given else pos[1:]


def perl_writes(args):
    inplace, code_given, pos, i = False, False, [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            pos += args[i + 1:]
            break
        if a.startswith("-") and len(a) > 1 and not pos:
            j = 1
            while j < len(a):
                c = a[j]
                if c == "i":
                    inplace = True
                    break
                if c in "eE":
                    code_given = True
                    if j == len(a) - 1:
                        i += 1
                    break
                if c in "MmIdDxCF":
                    if j == len(a) - 1 and c in "MmI":
                        i += 1
                    break
                j += 1
        else:
            pos.append(a)
        i += 1
    if not inplace:
        return []
    return pos if code_given else pos[1:]


def awk_writes(args):
    inplace, prog_given, pos, i = False, False, [], 0
    while i < len(args):
        a = args[i]
        if a in ("-i", "--include") and i + 1 < len(args):
            inplace = inplace or args[i + 1] in ("inplace", "inplace.awk")
            i += 2
            continue
        if a.startswith("--include="):
            inplace = inplace or a.split("=", 1)[1] in ("inplace", "inplace.awk")
        elif a in ("-f", "--file", "-e", "--source"):
            prog_given = True
            i += 1
        elif a in ("-v", "-F", "--assign", "--field-separator"):
            i += 1
        elif a.startswith("-") and len(a) > 1 and not pos:
            pass
        elif not re.match(r"^[A-Za-z_]\w*=", a):           # var=value is an assignment, not a file
            pos.append(a)
        i += 1
    if not inplace:
        return []
    return pos if prog_given else pos[1:]


def plain_args(args, value_opts=()):
    """The non-option words (tee's files)."""
    pos, i = [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            return pos + args[i + 1:]
        if a in value_opts:
            i += 1
        elif not (a.startswith("-") and len(a) > 1):
            pos.append(a)
        i += 1
    return pos


def cp_writes(args, cwd):
    target_dir, pos, i = None, [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            pos += args[i + 1:]
            break
        if a in ("-t", "--target-directory") and i + 1 < len(args):
            target_dir = args[i + 1]
            i += 1
        elif a.startswith("--target-directory="):
            target_dir = a.split("=", 1)[1]
        elif a in ("-S", "--suffix"):
            i += 1
        elif not (a.startswith("-") and len(a) > 1):
            pos.append(a)
        i += 1
    if target_dir is not None:
        return into(target_dir, pos, cwd, False, folder=True)
    if len(pos) < 2:
        return []
    return into(pos[-1], pos[:-1], cwd, False)


PS_SWITCHES = ("force", "nonewline", "append", "noclobber", "passthru", "whatif", "confirm", "recurse", "container",
               "asbytestream", "verbose", "debug")


def ps_params(args):
    """PowerShell parameters: ({name as typed, lowercase: value}, [positional words]). -Name:value, abbreviated names."""
    named, pos, i = {}, [], 0
    while i < len(args):
        a = args[i]
        if re.match(r"^-[A-Za-z]", a):
            name, colon, val = a[1:].partition(":")
            name = name.lower()
            if colon:
                named[name] = val
            elif any(sw.startswith(name) for sw in PS_SWITCHES):
                named[name] = True
            else:
                named[name] = args[i + 1] if i + 1 < len(args) else ""
                i += 1
        else:
            pos.append(a)
        i += 1
    return named, pos


def ps_get(named, *names):
    for typed, v in named.items():
        if isinstance(v, str) and any(full.startswith(typed) for full in names):
            return v
    return None


def ps_list(value):
    return [p for p in (value or "").split(",") if p]


PS_CONTENT = {"set-content", "sc", "add-content", "ac", "out-file", "tee-object"}
PS_COPY = {"copy-item", "cpi", "copy", "cp", "move-item", "mi", "move", "mv"}     # cp / mv: PowerShell's aliases
CD = {"cd", "pushd", "chdir", "set-location", "sl", "push-location"}
PYTHON = re.compile(r"^(python[\d.]*w?|py|pyw|node)$")
SHELLS = {"bash": "bash", "sh": "bash", "powershell": "powershell", "pwsh": "powershell"}
PREFIXES = {"sudo", "env", "command", "time", "nohup", "exec", "!", "{", "}", "then", "do", "else", "elif", "if",
            "while", "until", "builtin"}

Q = r"[rRbBuUfF]{0,2}(['\"])([^'\"\n]+?)\1"            # a quoted path in a script; group n+1 is the path
SCRIPT_WRITES = [
    (re.compile(r"\bopen\(\s*" + Q + r"\s*,\s*(?:mode\s*=\s*)?[rRbBuUfF]{0,2}(['\"])([^'\"\n]*)\3"), 2, 4),
    (re.compile(r"\bPath\(\s*" + Q + r"\s*\)\s*\.\s*write_(?:text|bytes)\("), 2, None),
    (re.compile(r"\b(?:shutil\.(?:copy\w*|move)|os\.(?:replace|rename))\(\s*[^,()]+,\s*" + Q), 2, None),
    (re.compile(r"\b(?:writeFileSync|appendFileSync|writeFile|appendFile|createWriteStream)\(\s*([`'\"])([^`'\"\n]+?)\1"),
     2, None),
    (re.compile(r"\b(?:copyFileSync|renameSync|copyFile|rename)\(\s*[^,()]+,\s*([`'\"])([^`'\"\n]+?)\1"), 2, None),
]
PS_SCRIPT_WRITES = [
    (re.compile(r"\[(?:System\.)?IO\.File\]::(?:WriteAll\w+|AppendAll\w+|Create\w*|Open\w*Write\w*)\(\s*(['\"])([^'\"\n]+?)\1",
                re.I), 2, None),
]


def script_writes(text, patterns):
    out = []
    for rx, path_group, mode_group in patterns:
        for m in rx.finditer(text):
            if mode_group is None or set(m.group(mode_group)) & set("wax+"):
                out.append(m.group(path_group))
    return out


def command_writes(words, texts, bodies, cwd, ps, depth):
    """(paths written, new cwd) for one simple command."""
    while words and (words[0] in PREFIXES or re.match(r"^[A-Za-z_]\w*=", words[0])):
        words = words[1:]
    if not words:
        return [], cwd
    name = re.sub(r"\.exe$", "", os.path.basename(words[0].replace("\\", "/")), flags=re.I).lower()
    args = words[1:]
    paths = []
    if name in CD:
        if ps:
            named, pos = ps_params(args)
            where = ps_get(named, "path", "literalpath") or (pos[0] if pos else None)
        else:
            pos = plain_args(args)
            where = pos[0] if pos else "~"
        new = resolve(where, cwd, ps) if where else None
        return [], new or cwd
    if name == "git":                                      # git's own work (checkout, mv, rm…) is not a terminal edit
        return [], cwd
    if ps and name in PS_CONTENT | {"tee", "new-item", "ni"} | PS_COPY:
        named, pos = ps_params(args)
        if name in PS_COPY:
            dest = ps_get(named, "destination") or (pos[1] if len(pos) > 1 else None)
            src = ps_list(ps_get(named, "path", "literalpath")) or pos[:1]
            return (into(dest, src, cwd, ps) if dest else []), cwd
        if name in ("new-item", "ni"):
            base = ps_get(named, "path") or (pos[0] if pos else None)
            leaf = ps_get(named, "name")
            targets = [os.path.join(base or ".", leaf)] if leaf else ps_list(base)
        else:
            targets = ps_list(ps_get(named, "path", "literalpath", "filepath")) or pos[:1]
        return [p for t in targets for p in resolve_all(t, cwd, ps)], cwd
    if name in ("sed", "gsed"):
        targets = sed_writes(args)
    elif name == "perl":
        targets = perl_writes(args)
    elif name in ("awk", "gawk"):
        targets = awk_writes(args)
    elif name == "tee":
        targets = plain_args(args)
    elif name in ("cp", "mv"):
        return cp_writes(args, cwd), cwd
    elif name == "dd":
        targets = [a[3:] for a in args if a.startswith("of=")]
    elif name in SHELLS and depth < 3:
        inner_ps = SHELLS[name] == "powershell"
        flag = ("-command", "-c", "-com", "-comm", "-comma", "-comman") if inner_ps else ("-c",)
        for k, a in enumerate(args):
            if a.lower() in flag and k + 1 < len(args):
                inner = " ".join(args[k + 1:]) if inner_ps else args[k + 1]
                paths += read_command(inner, cwd, inner_ps, depth + 1)
                break
        targets = []
    elif PYTHON.match(name):
        targets = script_writes("\n".join(args + [bodies[t] for t in texts if t < len(bodies)]), SCRIPT_WRITES)
    else:
        targets = []
    for t in targets:
        paths += resolve_all(t, cwd, ps)
    return paths, cwd


def read_command(command, cwd, ps, depth=0):
    if ps:
        command, bodies = take_herestrings(command)
    else:
        command, bodies = take_heredocs(command)
    paths = []
    for words, reds, texts in segments(tokenize(command, ps)):
        for r in reds:
            p = resolve(r, cwd, ps)
            if p:
                paths.append(p)
        written, cwd = command_writes(words, texts, bodies, cwd, ps, depth)
        paths += written
    if ps:
        paths += [p for t in script_writes(command, PS_SCRIPT_WRITES) for p in resolve_all(t, cwd, ps)]
    return paths


def written_paths(command, cwd, shell="bash"):
    """Every file the command writes that can be told from its text, as absolute paths (shell: 'bash' | 'powershell')."""
    seen, out = set(), []
    for p in read_command(command or "", cwd or os.getcwd(), shell == "powershell"):
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out
