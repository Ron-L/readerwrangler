@echo off
rem ReaderWrangler local server — double-click to start; close the window to stop.
rem Auto-start at logon: put a shortcut to this file in your Startup folder (Win+R -> shell:startup).
rem The server itself is serve.py (it refuses private files, anything git ignores, and folder listings).
title ReaderWrangler local server (close this window to stop)
cd /d "%~dp0"
py serve.py
rem If the server stops with an error, keep the window open so the message can be read.
pause
