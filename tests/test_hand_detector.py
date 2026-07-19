"""
Unit tests for hand_detector.py and finger_counter.py.
Uses synthetic HandResult objects to avoid requiring a real webcam or
MediaPipe model inference during CI.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hand_detector import HandResult
from finger_counter import get_finger_state


def make_hand(finger_up_flags, handedness="Right"):
    """
    Build a synthetic HandResult with 21 landmarks positioned so that
    get_finger_state() reads back the desired up/down pattern.

    finger_up_flags: [thumb, index, middle, ring, pinky] booleans
    """
    landmarks = [(0.5, 0.5, 0.0)] * 21  # default: wrist-ish center

    # Non-thumb fingers: tip.y < pip.y means "up"
    # Give each finger a distinct base x-offset so "curled" tips never
    # accidentally collide with each other (e.g., thumb and index tips
    # landing on the exact same point, which would falsely read as a pinch).
    tip_pip_pairs = {1: (8, 6, 0.60), 2: (12, 10, 0.70), 3: (16, 14, 0.80), 4: (20, 18, 0.90)}
    for finger_idx, (tip, pip, x_offset) in tip_pip_pairs.items():
        if finger_up_flags[finger_idx]:
            landmarks[tip] = (x_offset, 0.2, 0.0)
            landmarks[pip] = (x_offset, 0.4, 0.0)
        else:
            landmarks[tip] = (x_offset, 0.5, 0.0)
            landmarks[pip] = (x_offset, 0.3, 0.0)

    # Thumb: for "Right" hand, tip.x < ip.x means "up"
    thumb_tip, thumb_ip = 4, 3
    if finger_up_flags[0]:
        landmarks[thumb_tip] = (0.2, 0.5, 0.0)
        landmarks[thumb_ip] = (0.4, 0.5, 0.0)
    else:
        landmarks[thumb_tip] = (0.5, 0.5, 0.0)
        landmarks[thumb_ip] = (0.3, 0.5, 0.0)

    return HandResult(
        landmarks=landmarks,
        pixel_landmarks=[(int(x * 100), int(y * 100)) for x, y, _ in landmarks],
        handedness=handedness,
        confidence=0.95,
    )


def test_open_palm_all_fingers_up():
    hand = make_hand([True, True, True, True, True])
    state = get_finger_state(hand)
    assert state.count == 5
    assert all(state.states)


def test_closed_fist_all_fingers_down():
    hand = make_hand([False, False, False, False, False])
    state = get_finger_state(hand)
    assert state.count == 0
    assert not any(state.states)


def test_thumbs_up_only_thumb():
    hand = make_hand([True, False, False, False, False])
    state = get_finger_state(hand)
    assert state.states[0] is True
    assert state.count == 1


def test_victory_index_and_middle():
    hand = make_hand([False, True, True, False, False])
    state = get_finger_state(hand)
    assert state.states[1] and state.states[2]
    assert state.count == 2
