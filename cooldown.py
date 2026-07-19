"""
cooldown.py
-----------
Thin, dedicated cooldown/debounce manager for action execution. While
gesture_detector.py has its own internal cooldown for gesture *recognition*,
this module guards the *action execution* layer (ppt_controller) so the
same action can never be double-fired even if called from multiple places.
"""

from typing import Dict

from constants import Action
from utils import Cooldown


class ActionCooldownManager:
    """Tracks independent cooldown timers per Action type."""

    def __init__(self, default_seconds: float = 1.0) -> None:
        self.default_seconds = default_seconds
        self._cooldowns: Dict[Action, Cooldown] = {}

    def _get(self, action: Action) -> Cooldown:
        if action not in self._cooldowns:
            self._cooldowns[action] = Cooldown(self.default_seconds)
        return self._cooldowns[action]

    def can_fire(self, action: Action) -> bool:
        """Return True if this specific action is not currently on cooldown."""
        return self._get(action).ready()

    def mark_fired(self, action: Action) -> None:
        """Record that this action just executed, starting its cooldown."""
        self._get(action).fire()

    def remaining(self, action: Action) -> float:
        """Seconds remaining before this action can fire again."""
        return self._get(action).remaining()

    def reset_all(self) -> None:
        """Clear all cooldown timers (e.g., on app restart or mode switch)."""
        self._cooldowns.clear()
