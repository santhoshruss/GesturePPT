"""
finger_counter.py
-----------------
Determines which fingers are extended ("up") vs. curled ("down") from
a single hand's landmark set, and returns a finger-state vector plus count.
"""

from dataclasses import dataclass
from typing import List, Tuple

from constants import FINGER_NAMES, FINGER_PIPS, FINGER_TIPS
from hand_detector import HandResult


@dataclass
class FingerState:
    """Extended/curled state for all five fingers of one hand."""
    states: List[bool]     # [thumb, index, middle, ring, pinky] True = extended
    count: int
    names_up: List[str]


def get_finger_state(hand: HandResult) -> FingerState:
    """
    Determine which fingers are extended for a given detected hand.

    Uses a simple, robust heuristic:
      - For the four non-thumb fingers: tip is "up" if it is above (smaller y)
        than its PIP joint (works regardless of hand rotation reasonably well
        for an upright, camera-facing hand).
      - For the thumb: compares horizontal (x) position of tip vs. IP joint,
        flipped based on detected handedness, since the thumb extends
        sideways rather than vertically.

    Args:
        hand: A HandResult produced by HandDetector.

    Returns:
        A FingerState with per-finger booleans, total count, and names.
    """
    landmarks = hand.landmarks  # normalized (x, y, z)
    states: List[bool] = [False] * 5

    # Thumb (index 0): horizontal comparison, direction depends on handedness.
    thumb_tip_x = landmarks[FINGER_TIPS[0]][0]
    thumb_ip_x = landmarks[FINGER_PIPS[0]][0]
    if hand.handedness == "Right":
        states[0] = thumb_tip_x < thumb_ip_x
    else:
        states[0] = thumb_tip_x > thumb_ip_x

    # Other four fingers: vertical comparison (smaller y = higher on screen = extended).
    for i in range(1, 5):
        tip_y = landmarks[FINGER_TIPS[i]][1]
        pip_y = landmarks[FINGER_PIPS[i]][1]
        states[i] = tip_y < pip_y

    count = sum(states)
    names_up = [FINGER_NAMES[i] for i, up in enumerate(states) if up]

    return FingerState(states=states, count=count, names_up=names_up)
