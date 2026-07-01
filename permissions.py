"""
permissions.py — consent + privacy guard for windows-computer-control

- Sensitive actions (right-click, delete/edit keys, typing, paste, drag,
  clipboard writes) pop up a native dialog: Allow Once / Always Allow /
  Cancel, before anything happens.
- Privacy-sensitive reads (clipboard read, screenshot) ALWAYS prompt —
  they can never be set to "Always Allow" — so Claude can never silently
  read what's on your screen or clipboard.
- Auto-deny (no prompt, no bypass) whenever the active window looks like
  a password manager, banking app, or similar — even if "Always Allow"
  was set previously for that action.
"""

import json
import os
import tkinter as tk

STORE_PATH = os.path.join(
    os.path.expanduser("~"), ".windows_computer_control_permissions.json"
)

# Windows whose title contains any of these are always off-limits,
# regardless of prior "Always Allow" choices. Edit this list as needed.
BLOCKED_WINDOW_KEYWORDS = [
    "password", "bank", "netbanking", "net banking", "wallet", "upi",
    "otp", "aadhaar", "pan card", "credit card", "debit card",
    "keychain", "1password", "bitwarden", "lastpass", "paypal",
]

# These tools touch personal data directly — never eligible for
# "Always Allow"; every single call re-prompts.
ALWAYS_ASK_TOOLS = {"get_clipboard", "screenshot"}


def _load_store() -> dict:
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_store(store: dict) -> None:
    with open(STORE_PATH, "w") as f:
        json.dump(store, f, indent=2)


def _active_window_title() -> str:
    try:
        import pygetwindow as gw
        w = gw.getActiveWindow()
        return w.title if w else ""
    except Exception:
        return ""


def _is_blocked_window() -> tuple[bool, str]:
    title = _active_window_title().lower()
    return any(k in title for k in BLOCKED_WINDOW_KEYWORDS), title


def _show_prompt(tool_name: str, detail: str) -> str:
    """Blocking native popup. Returns 'once', 'always', or 'cancel'."""
    result = {"choice": "cancel"}

    root = tk.Tk()
    root.title("Claude is requesting permission")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    tk.Label(
        root, text=f"Claude wants to use: {tool_name}",
        font=("Segoe UI", 11, "bold"), padx=20, pady=(15, 5),
    ).pack()
    tk.Label(root, text=detail, wraplength=380, justify="left", padx=20).pack(pady=(0, 15))

    def choose(c):
        result["choice"] = c
        root.destroy()

    frame = tk.Frame(root, pady=10)
    frame.pack()
    tk.Button(frame, text="Allow Once", width=13, command=lambda: choose("once")).grid(row=0, column=0, padx=5)
    tk.Button(frame, text="Always Allow", width=13, command=lambda: choose("always")).grid(row=0, column=1, padx=5)
    tk.Button(frame, text="Cancel", width=13, command=lambda: choose("cancel")).grid(row=0, column=2, padx=5)

    root.eval("tk::PlaceWindow . center")
    root.mainloop()
    return result["choice"]


def request_permission(tool_name: str, detail: str = "") -> bool:
    """Returns True if the action is allowed to proceed."""
    blocked, title = _is_blocked_window()
    if blocked:
        return False

    store = _load_store()
    if tool_name not in ALWAYS_ASK_TOOLS and store.get(tool_name) == "always":
        return True

    choice = _show_prompt(tool_name, detail or f"Allow this action now?")

    if choice == "always" and tool_name not in ALWAYS_ASK_TOOLS:
        store[tool_name] = "always"
        _save_store(store)
        return True

    return choice in ("once", "always")


def reset_permissions() -> None:
    """Clear all saved 'Always Allow' decisions."""
    if os.path.exists(STORE_PATH):
        os.remove(STORE_PATH)
