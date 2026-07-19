"""
Unit tests for gesture_detector.py — static gesture classification,
stability/debouncing, and cooldown gating.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import GestureConfig
from constants import Gesture
from gesture_detector import GestureDetector
from tests.test_hand_detector import make_hand


def fresh_detector(**overrides) -> GestureDetector:
    cfg = GestureConfig(
        confidence_threshold=0.5,
        stability_frames=3,
        cooldown_seconds=0.0,
        swipe_min_distance=0.18,
        swipe_window_frames=10,
        pinch_distance_threshold=0.045,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return GestureDetector(cfg)


def test_open_palm_recognized_after_stability_window():
    detector = fresh_detector()
    hand = make_hand([True, True, True, True, True])

    fired = [detector.update(hand).gesture for _ in range(5)]

    assert Gesture.OPEN_PALM in fired


def test_no_hand_returns_none_and_resets():
    detector = fresh_detector()
    result = detector.update(None)
    assert result.gesture == Gesture.NONE
    assert result.confidence == 0.0


def test_closed_fist_recognized():
    detector = fresh_detector()
    hand = make_hand([False, False, False, False, False])

    fired = [detector.update(hand).gesture for _ in range(5)]

    assert Gesture.CLOSED_FIST in fired


def test_cooldown_blocks_immediate_refire():
    detector = fresh_detector(cooldown_seconds=5.0)
    hand = make_hand([True, True, True, True, True])

    first_batch = [detector.update(hand).gesture for _ in range(5)]
    assert Gesture.OPEN_PALM in first_batch

    # Feed the identical pose again immediately — cooldown should suppress it.
    second_batch = [detector.update(hand).gesture for _ in range(5)]
    assert Gesture.OPEN_PALM not in second_batch


def test_victory_gesture_recognized():
    detector = fresh_detector()
    hand = make_hand([False, True, True, False, False])

    fired = [detector.update(hand).gesture for _ in range(5)]

    assert Gesture.VICTORY in fired


def test_finger_gun_gesture_recognized():
    detector = fresh_detector()
    hand = make_hand([True, True, False, False, False])

    fired = [detector.update(hand).gesture for _ in range(5)]

    assert Gesture.FINGER_GUN in fired
    assert Gesture.THUMBS_UP not in fired


def test_index_only_pointing_gesture_recognized():
    detector = fresh_detector()
    hand = make_hand([False, True, False, False, False])

    fired = [detector.update(hand).gesture for _ in range(5)]

    assert Gesture.POINTING in fired
    assert Gesture.FINGER_GUN not in fired
