"""
utils.py
--------
Small, reusable helper functions shared across modules (math, timing, geometry).
"""

import math
import time
from collections import deque
from typing import Deque, Optional, Tuple


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Compute the Euclidean distance between two 2D points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value to the inclusive range [lo, hi]."""
    return max(lo, min(hi, value))


class FPSCounter:
    """Rolling-average FPS counter based on a sliding window of frame timestamps."""

    def __init__(self, window_size: int = 30) -> None:
        self._timestamps: Deque[float] = deque(maxlen=window_size)

    def tick(self) -> float:
        """
        Register a new frame and return the current rolling FPS.

        Returns:
            Estimated frames-per-second based on recent frame timing.
        """
        now = time.perf_counter()
        self._timestamps.append(now)
        if len(self._timestamps) < 2:
            return 0.0
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed <= 0:
            return 0.0
        return (len(self._timestamps) - 1) / elapsed


class Cooldown:
    """Simple time-based cooldown/debounce gate."""

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        self._last_fire: Optional[float] = None

    def ready(self) -> bool:
        """Return True if the cooldown period has elapsed (or never fired)."""
        if self._last_fire is None:
            return True
        return (time.perf_counter() - self._last_fire) >= self.seconds

    def remaining(self) -> float:
        """Return seconds remaining before the cooldown clears (0 if ready)."""
        if self._last_fire is None:
            return 0.0
        elapsed = time.perf_counter() - self._last_fire
        return max(0.0, self.seconds - elapsed)

    def fire(self) -> None:
        """Mark the cooldown as triggered now."""
        self._last_fire = time.perf_counter()

    def reset(self) -> None:
        """Clear the cooldown so the next check is always ready."""
        self._last_fire = None
