# Windows Computer Control — MCP Connector for Claude Desktop

Local MCP server giving Claude Desktop (Windows app) direct mouse, keyboard,
and clipboard control — cursor movement, left/right/double/triple click,
scroll up/down, drag-select, type text, hotkeys, copy/paste, clipboard
read/write, open URL in default browser, and screenshot.

**Windows desktop app only.** MCP servers run locally, so this will not
work on claude.ai (web) or the mobile apps — only the Claude Desktop app
installed on the same Windows PC.

## 1. Install Python (Windows)

Install Python 3.10+ from https://python.org (check "Add Python to PATH"
during setup). Verify:

```powershell
python --version
```

## 2. Get the files onto your PC

Copy this whole `windows-computer-control` folder to your Windows machine,
e.g. `C:\Users\YOUR_USERNAME\windows-computer-control\`.

## 3. Install dependencies

Open PowerShell in that folder:

```powershell
cd C:\Users\YOUR_USERNAME\windows-computer-control
pip install -r requirements.txt
```

## 4. Register the connector in Claude Desktop

Open (create if missing):
`%APPDATA%\Claude\claude_desktop_config.json`

Add the `windows-computer-control` entry from
`claude_desktop_config.sample.json` into your `mcpServers` object — merge
it with any servers you already have, don't overwrite the file. Update the
path to match where you copied the folder and your Python path if `python`
isn't on PATH (use the full path from `where python`).

## 5. Restart Claude Desktop

Fully quit and reopen the app. Look for a tools/plug icon in the chat box —
"windows-computer-control" should be listed with its tools available.

## 6. Use it

Ask Claude things like:
- "Open google.com and search for X"
- "Take a screenshot so you can see the page"
- "Right-click that link and copy it"
- "Select all the text on this page and copy it"
- "Scroll down and click the second result"

Claude will call `screenshot()` to see the screen, then use
`move_cursor` / `click` / `type_text` / `scroll` etc. to act — same
pattern as any computer-use agent.

## Tools included

| Tool | Does |
|---|---|
| `get_screen_size` | Screen resolution |
| `get_cursor_position` | Current mouse (x, y) |
| `move_cursor(x, y)` | Move mouse |
| `click(x, y, button, clicks)` | Left/right/middle click |
| `right_click(x, y)` | Right-click / context menu |
| `double_click(x, y)` | Double-click (select word) |
| `triple_click(x, y)` | Triple-click (select line) |
| `scroll(amount, x, y)` | Scroll up (+) / down (-) |
| `drag_select(x1,y1,x2,y2)` | Drag-select text/elements |
| `type_text(text)` | Type at focused field |
| `press_key(key)` | Single key or `ctrl+c` style combo |
| `select_all` | Ctrl+A |
| `copy` / `paste` | Ctrl+C / Ctrl+V |
| `get_clipboard` / `set_clipboard(text)` | Read/write clipboard directly |
| `open_url(url)` | Open URL in default browser |
| `screenshot` | Base64 PNG of the screen |

## Security & privacy features

**Permission prompts.** Right-click, delete/enter/edit keys, typing,
paste, drag-select, select-all, and clipboard writes all pop up a native
Windows dialog first: **Allow Once / Always Allow / Cancel**. Nothing
happens until you click one.
- *Allow Once* — runs this one time only, asks again next time.
- *Always Allow* — remembers your choice for that action (saved to
  `%USERPROFILE%\.windows_computer_control_permissions.json`).
- *Cancel* — blocks the action; Claude gets told it was denied.

**No silent personal-data access.** Reading the clipboard and taking
screenshots can never be set to "Always Allow" — every single call
prompts you fresh, since these can expose personal information.

**Auto-deny near sensitive apps.** If the currently focused window's
title contains a banking/password-manager keyword (bank, wallet, OTP,
1Password, Bitwarden, etc.), every guarded action is silently blocked —
no prompt, no bypass, even if you'd previously chosen "Always Allow".
Edit `BLOCKED_WINDOW_KEYWORDS` in `permissions.py` to add your own.

**Reset anytime.** Ask Claude to call `reset_permissions`, or delete
`%USERPROFILE%\.windows_computer_control_permissions.json` yourself, to
clear all saved "Always Allow" grants.

**Safe/unguarded actions** (no prompt, since they can't change or leak
anything): `get_screen_size`, `get_cursor_position`, `move_cursor`,
`click` (left click), `double_click`, `triple_click`, `scroll`, `copy`,
`open_url`.

## Safety notes — read before use

- This gives an AI model **real control of your mouse and keyboard**.
  Only enable it while you're watching the screen and actively supervising.
- PyAutoGUI's fail-safe is on: slam your mouse into any screen corner to
  immediately abort whatever action is in progress.
- Remove the entry from `claude_desktop_config.json` (and restart the app)
  whenever you're not actively using it.

