"""
Windows Computer/Browser Control — MCP Server
-----------------------------------------------
Gives Claude Desktop (Windows app) direct control of your mouse, keyboard,
and clipboard so it can drive your default browser (or any app) like a
human would: move cursor, click, right-click, scroll, select text,
copy/paste, type, and press hotkeys.

Runs ONLY on Windows, launched locally by Claude Desktop as a stdio MCP
server. It does NOT work with claude.ai (web) — Windows desktop app only.

SECURITY WARNING
-----------------
This gives an AI model full control of your mouse and keyboard. Only run
this on a machine you trust, only enable it when you actually need it, and
watch the screen while Claude is using it. Move your mouse to any screen
corner at any time to trigger PyAutoGUI's built-in fail-safe abort.
"""

import base64
import io
import time

import pyautogui
import pyperclip
import webbrowser

from mcp.server.fastmcp import FastMCP
from permissions import request_permission

# Fail-safe: slamming the mouse into a screen corner raises an exception
# and stops whatever PyAutoGUI is doing.
pyautogui.FAILSAFE = True
# Small pause between every PyAutoGUI call so actions are visible/reliable.
pyautogui.PAUSE = 0.05

mcp = FastMCP("windows-computer-control")


# ---------------------------------------------------------------------------
# Screen / cursor
# ---------------------------------------------------------------------------

@mcp.tool()
def get_screen_size() -> dict:
    """Get the screen resolution (width, height) in pixels."""
    w, h = pyautogui.size()
    return {"width": w, "height": h}


@mcp.tool()
def get_cursor_position() -> dict:
    """Get the current mouse cursor position."""
    x, y = pyautogui.position()
    return {"x": x, "y": y}


@mcp.tool()
def move_cursor(x: int, y: int, duration: float = 0.3) -> str:
    """Move the mouse cursor to absolute screen coordinates (x, y)."""
    pyautogui.moveTo(x, y, duration=duration)
    return f"Cursor moved to ({x}, {y})"


# ---------------------------------------------------------------------------
# Mouse buttons
# ---------------------------------------------------------------------------

@mcp.tool()
def click(x: int = None, y: int = None, button: str = "left", clicks: int = 1) -> str:
    """Click the mouse. button: 'left', 'right', or 'middle'.
    If x/y are omitted, clicks at the current cursor position."""
    if x is not None and y is not None:
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
    else:
        pyautogui.click(button=button, clicks=clicks)
    return f"{button} click x{clicks} at ({x}, {y})"


@mcp.tool()
def right_click(x: int = None, y: int = None) -> str:
    """Right-click at coordinates (or current position if omitted).
    Use this to open context menus (e.g. browser right-click menu).
    Asks for permission (Allow Once / Always Allow / Cancel) first."""
    if not request_permission("right_click", f"Right-click at ({x}, {y})?"):
        return "Denied: user did not grant permission for right_click"
    if x is not None and y is not None:
        pyautogui.rightClick(x=x, y=y)
    else:
        pyautogui.rightClick()
    return f"Right-clicked at ({x}, {y})"


@mcp.tool()
def double_click(x: int = None, y: int = None) -> str:
    """Double-click at coordinates (or current position if omitted).
    Useful for selecting a single word."""
    if x is not None and y is not None:
        pyautogui.doubleClick(x=x, y=y)
    else:
        pyautogui.doubleClick()
    return f"Double-clicked at ({x}, {y})"


@mcp.tool()
def triple_click(x: int = None, y: int = None) -> str:
    """Triple-click at coordinates (or current position if omitted).
    Useful for selecting a full line/paragraph."""
    if x is not None and y is not None:
        pyautogui.tripleClick(x=x, y=y)
    else:
        pyautogui.tripleClick()
    return f"Triple-clicked at ({x}, {y})"


@mcp.tool()
def scroll(amount: int, x: int = None, y: int = None) -> str:
    """Scroll the mouse wheel. Positive amount scrolls up, negative scrolls
    down (e.g. 500 = scroll up, -500 = scroll down). Optionally moves the
    cursor to (x, y) first so you scroll inside the right panel/element."""
    if x is not None and y is not None:
        pyautogui.moveTo(x, y)
    pyautogui.scroll(amount)
    direction = "up" if amount >= 0 else "down"
    return f"Scrolled {direction} by {abs(amount)}"


@mcp.tool()
def drag_select(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> str:
    """Click-drag from (x1, y1) to (x2, y2) — e.g. to select a range of text
    or a block of content on a page, or to drag-and-drop an element.
    Asks for permission (Allow Once / Always Allow / Cancel) first."""
    if not request_permission("drag_select", f"Drag-select from ({x1},{y1}) to ({x2},{y2})?"):
        return "Denied: user did not grant permission for drag_select"
    pyautogui.moveTo(x1, y1)
    pyautogui.mouseDown()
    pyautogui.moveTo(x2, y2, duration=duration)
    pyautogui.mouseUp()
    return f"Dragged from ({x1}, {y1}) to ({x2}, {y2})"


# ---------------------------------------------------------------------------
# Keyboard
# ---------------------------------------------------------------------------

@mcp.tool()
def type_text(text: str, interval: float = 0.02) -> str:
    """Type text at the current cursor/focus position, as if typed on a
    physical keyboard. Asks for permission (Allow Once / Always Allow /
    Cancel) first, since this can edit or submit content."""
    preview = text if len(text) <= 60 else text[:57] + "..."
    if not request_permission("type_text", f'Type: "{preview}"?'):
        return "Denied: user did not grant permission for type_text"
    pyautogui.write(text, interval=interval)
    return f"Typed {len(text)} characters"


@mcp.tool()
def press_key(key: str) -> str:
    """Press a single key, or a hotkey combo joined with '+'.
    Examples: 'enter', 'esc', 'tab', 'backspace', 'delete', 'f5',
    'ctrl+c', 'ctrl+v', 'ctrl+shift+t', 'alt+tab', 'win', 'ctrl+l'.
    Asks for permission (Allow Once / Always Allow / Cancel) first for any
    key that can delete, edit, or submit content."""
    GUARDED = {
        "delete", "backspace", "enter", "return", "ctrl+x", "ctrl+z",
        "ctrl+shift+z", "ctrl+a", "ctrl+w", "alt+f4",
    }
    if key.lower() in GUARDED and not request_permission("press_key", f"Press key: {key}?"):
        return "Denied: user did not grant permission for press_key"
    keys = [k.strip() for k in key.lower().split("+")]
    if len(keys) == 1:
        pyautogui.press(keys[0])
    else:
        pyautogui.hotkey(*keys)
    return f"Pressed {key}"


@mcp.tool()
def select_all() -> str:
    """Select all content in the currently focused window/field (Ctrl+A).
    Asks for permission (Allow Once / Always Allow / Cancel) first."""
    if not request_permission("select_all", "Select all content in the focused window?"):
        return "Denied: user did not grant permission for select_all"
    pyautogui.hotkey("ctrl", "a")
    return "Selected all"


# ---------------------------------------------------------------------------
# Clipboard (copy / paste)
# ---------------------------------------------------------------------------

@mcp.tool()
def copy() -> str:
    """Copy the current selection to the clipboard (Ctrl+C)."""
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.1)
    return "Copied selection to clipboard"


@mcp.tool()
def paste() -> str:
    """Paste clipboard content at the current cursor position (Ctrl+V).
    Asks for permission (Allow Once / Always Allow / Cancel) first."""
    if not request_permission("paste", "Paste clipboard content here?"):
        return "Denied: user did not grant permission for paste"
    pyautogui.hotkey("ctrl", "v")
    return "Pasted clipboard content"


@mcp.tool()
def get_clipboard() -> str:
    """Read the current clipboard text content. Privacy-sensitive: this
    ALWAYS prompts for permission, even if you've allowed it before,
    since the clipboard may contain personal information."""
    if not request_permission("get_clipboard", "Allow Claude to read your clipboard content?"):
        return "Denied: user did not grant permission to read clipboard"
    return pyperclip.paste()


@mcp.tool()
def set_clipboard(text: str) -> str:
    """Write text directly to the clipboard (without simulating Ctrl+C).
    Asks for permission (Allow Once / Always Allow / Cancel) first."""
    if not request_permission("set_clipboard", "Overwrite clipboard content?"):
        return "Denied: user did not grant permission for set_clipboard"
    pyperclip.copy(text)
    return "Clipboard set"


# ---------------------------------------------------------------------------
# Browser / apps
# ---------------------------------------------------------------------------

@mcp.tool()
def open_url(url: str) -> str:
    """Open a URL in the system's default web browser."""
    webbrowser.open(url)
    return f"Opened {url} in default browser"


@mcp.tool()
def screenshot() -> str:
    """Take a screenshot of the full screen and return it as a
    base64-encoded PNG image, so the model can see the current screen
    before deciding where to click/scroll/type next. Privacy-sensitive:
    this ALWAYS prompts for permission, even if allowed before, since the
    screen may show personal information."""
    if not request_permission("screenshot", "Allow Claude to see a screenshot of your screen?"):
        return "Denied: user did not grant permission for screenshot"
    img = pyautogui.screenshot()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@mcp.tool()
def reset_permissions() -> str:
    """Clear all previously saved 'Always Allow' permission grants, so
    every sensitive action will prompt again from scratch."""
    from permissions import reset_permissions as _reset
    _reset()
    return "All saved permissions cleared. Every sensitive action will ask again."


if __name__ == "__main__":
    mcp.run(transport="stdio")
