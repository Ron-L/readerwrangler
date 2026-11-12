#!/usr/bin/env python3
"""
check_messages.py — the logging kit's commit check: the logging rules, read from the code itself, and the table of
numbered message codes generated from it (designed 2026-11-07; moved into the kit in 7.28.0 — its first host's own
checker sits on top of it, adds its own rules, and calls it).

It knows nothing of the host — no files, no git, no logger name of its own. The host calls it with what to check:

    calls, problems = check(files, areas, logger="appLog", areas_from="settings.js")
        files: [(path, source text)]; areas: the host's areas; logger: the name its code calls the logger by
    text = table(calls, intro="…")        the table, as Markdown (intro: a line saying where it comes from)

For every  <logger>.log(level, code, text…)  call (and in the kit's own files, the kit's log(…) / log.log(…) calls):
  - the level and the code are written as plain quoted words (so they can be checked at all);
  - the level is one of the five; the code is AREA or AREA-NN, with AREA one of the host's areas;
  - warning and above use a numbered code (AREA-NN) — those are what support asks about;
  - each numbered code is used at exactly ONE call (so its level has one home, and a code always means one message).
The table lists every numbered code — code, level, message, file — sorted by area. Nobody edits it. (No line numbers:
they shift with every unrelated edit and would make the table stale on almost every commit.)

A host's own rules can use the readers here: read_literal, read_expression, skip, in_comment, line_of.
Standard library only.
"""
import os
import re

LEVELS = ["debug", "info", "warning", "error", "critical"]
CODE_RE = re.compile(r"^([A-Z]+)(?:-(\d{2}))?$")
# The kit's own files (the folder this file is in): the module's own log('error', 'UI-02', …) calls, and the Diagnostics
# window's log.log('warning', 'UI-06', …) — the logger is handed to it
KIT_DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__))) + "/"
CALL_IN_KIT = re.compile(r"(?<![\w.])(?:log\.)?log\(\s*(?=['\"`])")


def read_literal(src, i):
    """A quoted literal starting at src[i] ('…', "…" or `…`) → (its text, index after it), or (None, i)."""
    if i >= len(src) or src[i] not in "'\"`":
        return None, i
    q, j, out = src[i], i + 1, []
    while j < len(src) and src[j] != q:
        if src[j] == "\\" and j + 1 < len(src):
            out.append(src[j + 1])
            j += 2
            continue
        if q == "`" and src.startswith("${", j):          # a template's ${ … } may hold quotes, even another template
            depth, k = 1, j + 2
            while k < len(src) and depth:
                if src[k] in "'\"`":
                    _, k = read_literal(src, k)
                    continue
                depth += {"{": 1, "}": -1}.get(src[k], 0)
                k += 1
            out.append(src[j:k])
            j = k
            continue
        out.append(src[j])
        j += 1
    return "".join(out), j + 1


def read_expression(src, i):
    """An argument that isn't a literal: up to the comma or closing parenthesis at its own depth."""
    depth, j = 0, i
    while j < len(src):
        c = src[j]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                break
            depth -= 1
        elif c == "," and depth == 0:
            break
        elif c in "'\"`":
            _, j = read_literal(src, j)
            continue
        j += 1
    return src[i:j].strip(), j


def skip(src, i):
    """Past the spaces and line breaks at src[i]."""
    while i < len(src) and src[i] in " \t\r\n":
        i += 1
    return i


def in_comment(src, pos):
    """Is src[pos] inside a // line comment or a /* … */ block? (Good enough for ordinary code: a '//' inside a string on
    the same line before the call would hide it — the check would then miss a call, never invent one.)"""
    line_start = src.rfind("\n", 0, pos) + 1
    if "//" in src[line_start:pos]:
        return True
    return src.rfind("/*", 0, pos) > src.rfind("*/", 0, pos)


def line_of(src, pos):
    """The line number (from 1) of src[pos]."""
    return src.count("\n", 0, pos) + 1


def _call_pattern(logger):
    return re.compile(r"\b" + re.escape(logger) + r"\.log\(")


def find_calls(path, src, logger="log", kit_dir=KIT_DIR):
    """[(path, line, level or None, code or None, text)] for every logging call in one file."""
    pattern = CALL_IN_KIT if path.replace("\\", "/").startswith(kit_dir) else _call_pattern(logger)
    calls = []
    for m in pattern.finditer(src):
        if in_comment(src, m.start()):      # a comment that mentions a logging call isn't one
            continue
        i = skip(src, m.end())
        level, i = read_literal(src, i)
        i = skip(src, i)
        if i < len(src) and src[i] == ",":
            i = skip(src, i + 1)
        code, i = read_literal(src, i)
        i = skip(src, i)
        if i < len(src) and src[i] == ",":
            i = skip(src, i + 1)
        text, _ = read_literal(src, i)
        if text is None:
            text, _ = read_expression(src, i)
        calls.append((path, line_of(src, m.start()), level, code, text))
    return calls


def check(files, areas, logger="log", areas_from="the host's list of areas", kit_dir=KIT_DIR):
    """files = [(path, source)] → (calls, problems). areas_from names where the areas are listed, for the refusals."""
    calls, problems, seen = [], [], {}
    for path, src in files:
        calls.extend(find_calls(path, src, logger, kit_dir))
    for path, line, level, code, text in calls:
        where = f"{path}:{line}"
        if level is None or code is None:
            problems.append(f"{where}: write the level and the code as plain quoted words, so they can be checked")
            continue
        if level not in LEVELS:
            problems.append(f"{where}: unknown level \"{level}\" (one of {', '.join(LEVELS)})")
        m = CODE_RE.match(code)
        if not m:
            problems.append(f"{where}: badly shaped code \"{code}\" — use AREA or AREA-NN")
            continue
        if m.group(1) not in areas:
            problems.append(f"{where}: unknown area \"{m.group(1)}\" — the areas are listed in {areas_from}")
        if level in LEVELS and LEVELS.index(level) >= LEVELS.index("warning") and not m.group(2):
            problems.append(f"{where}: a {level} needs a numbered code ({m.group(1)}-NN)")
        if m.group(2):
            if code in seen:
                problems.append(f"{where}: {code} is already used at {seen[code]} — each numbered code at ONE call")
            else:
                seen[code] = where
    return calls, problems


def _placeholders(text):
    """A template's ${ … } parts are one occurrence's details (counts, names) — shown as "…": support needs the
    message's meaning. Nested braces and quotes inside a ${ … } are skipped as a whole."""
    out, i = [], 0
    while i < len(text):
        if text.startswith("${", i):
            depth, k = 1, i + 2
            while k < len(text) and depth:
                if text[k] in "'\"`":
                    _, k = read_literal(text, k)
                    continue
                depth += {"{": 1, "}": -1}.get(text[k], 0)
                k += 1
            if not out or out[-1] != "…":           # details side by side read as one "…"
                out.append("…")
            i = k
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def table(calls, intro="_Generated from every logging call in the code. Support: find the code a user reports; the level "
                       "says how serious it is._"):
    """The table of numbered codes (Markdown), sorted by area then code; general lines counted, not listed."""
    numbered = sorted({(c[3], c[2], c[4], c[0]) for c in calls if c[3] and CODE_RE.match(c[3]) and CODE_RE.match(c[3]).group(2)},
                      key=lambda r: (r[0].split("-")[0], r[0]))
    general = sum(1 for c in calls if c[3] and CODE_RE.match(c[3]) and not CODE_RE.match(c[3]).group(2))

    def cell(s):
        return _placeholders(str(s)).replace("|", "\\|").replace("\n", " ")
    lines = [
        "# Message codes — generated, do not edit",
        "",
        intro,
        "",
        f"{len(numbered)} numbered code{'s' if len(numbered) != 1 else ''}. ({general} general line{'s' if general != 1 else ''}"
        " — info and debug, coded by their area alone — not listed.)",
        "",
        "| Code | Level | Message | File |",
        "|---|---|---|---|",
    ]
    lines += [f"| {cell(code)} | {cell(level)} | {cell(text)} | {cell(path)} |" for code, level, text, path in numbered]
    return "\n".join(lines) + "\n"
