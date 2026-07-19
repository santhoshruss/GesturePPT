"""
ppt_controller.py
------------------
Translates recognized Actions into real PowerPoint keyboard commands via
PyAutoGUI/pynput, and detects whether PowerPoint is the active/running
application (Windows-focused, with safe fallbacks on other platforms).
"""

import sys
from typing import Optional

import pyautogui

from constants import Action
from cooldown import ActionCooldownManager
from logger import get_logger

logger = get_logger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

# Keyboard mapping for each supported PowerPoint action.
# These match standard PowerPoint Slide Show shortcuts.
_ACTION_KEYS = {
    Action.NEXT_SLIDE: "right",
    Action.PREV_SLIDE: "left",
    Action.START_SLIDESHOW: "f5",
    Action.END_SLIDESHOW: "esc",
    Action.BLACK_SCREEN: "b",
    Action.WHITE_SCREEN: "w",
}


def _get_active_window_title() -> Optional[str]:
    """
    Best-effort retrieval of the currently focused window's title.
    Returns None if it cannot be determined (e.g., unsupported platform).
    """
    if sys.platform.startswith("win"):
        try:
            import win32gui  # type: ignore
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except Exception:
            pass
    try:
        import pygetwindow as gw  # type: ignore
        active = gw.getActiveWindow()
        return active.title if active else None
    except Exception:
        return None


class PPTController:
    """
    Executes PowerPoint control actions and tracks whether PowerPoint
    currently appears to be the focused/running application.
    """

    def __init__(self) -> None:
        self.cooldowns = ActionCooldownManager(default_seconds=0.8)
        self.ppt_detected: bool = False

    def is_powerpoint_active(self) -> bool:
        """
        Heuristically determine whether PowerPoint is the active window.

        Returns:
            True if the foreground window title suggests PowerPoint
            (in Normal edit view or Slide Show view), False otherwise.
        """
        title = _get_active_window_title()
        if not title:
            self.ppt_detected = False
            return False

        title_lower = title.lower()
        active = "powerpoint" in title_lower or "slide show" in title_lower
        self.ppt_detected = active
        return active

    def execute(self, action: Action, require_ppt_focus: bool = True) -> bool:
        """
        Execute a PowerPoint action by sending the corresponding keystroke.

        Args:
            action: The Action to perform.
            require_ppt_focus: If True, skip execution unless PowerPoint
                appears to be the active window (prevents sending keystrokes
                to the wrong application).

        Returns:
            True if the action was executed, False if it was skipped/blocked.
        """
        if action == Action.NONE:
            return False

        if not self.cooldowns.can_fire(action):
            logger.debug("Action %s suppressed by cooldown.", action.value)
            return False

        if require_ppt_focus and not self.is_powerpoint_active():
            logger.warning("PowerPoint not active/focused; action '%s' skipped.", action.value)
            return False

        key = _ACTION_KEYS.get(action)
        if key is None:
            logger.error("No key mapping found for action: %s", action.value)
            return False

        try:
            pyautogui.press(key)
            self.cooldowns.mark_fired(action)
            logger.info("Executed PowerPoint action: %s (key='%s')", action.value, key)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to execute action %s: %s", action.value, exc)
            return False
