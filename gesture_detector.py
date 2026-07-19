"""
gesture_detector.py
-------------------
Recognizes discrete gestures (open palm, fist, thumbs up, victory, pinch,
pointing) plus motion-based gestures (swipe left/right) from hand landmark
history. Applies confidence thresholding, debouncing, cooldown, and
temporal smoothing so gestures fire once, cleanly, per intentional action.
"""

from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Tuple

from config import GestureConfig
from constants import INDEX_TIP, THUMB_TIP, Gesture
from finger_counter import FingerState, get_finger_state
from hand_detector import HandResult
from utils import Cooldown, euclidean_distance


@dataclass
class GestureResult:
    """A single recognized gesture with its confidence score."""
    gesture: Gesture
    confidence: float


class GestureDetector:
    """
    Stateful gesture recognizer. Feed it one hand's detection result per
    frame via `update()`; it returns a stabilized, cooldown-gated gesture
    (or Gesture.NONE) each call.
    """

    def __init__(self, config: GestureConfig) -> None:
        self.config = config
        self._wrist_history: Deque[Tuple[float, float]] = deque(maxlen=config.swipe_window_frames)
        self._recent_static_gestures: Deque[Gesture] = deque(maxlen=config.stability_frames)
        self._cooldown = Cooldown(config.cooldown_seconds)
        self.last_gesture: Gesture = Gesture.NONE
        self.last_confidence: float = 0.0

    def reset(self) -> None:
        """Clear all temporal state (e.g., when hand is lost)."""
        self._wrist_history.clear()
        self._recent_static_gestures.clear()

    def update(self, hand: Optional[HandResult]) -> GestureResult:
        """
        Process one frame's hand detection and return the currently
        recognized, stabilized gesture (Gesture.NONE if nothing qualifies
        or the cooldown has not yet elapsed).

        Args:
            hand: The primary detected hand this frame, or None if no hand
                  is currently visible.

        Returns:
            GestureResult with the gesture and its confidence score.
        """
        if hand is None:
            self.reset()
            return GestureResult(Gesture.NONE, 0.0)

        wrist = hand.landmarks[0][:2]
        self._wrist_history.append(wrist)

        # 1. Check motion-based gesture first (swipe) — takes priority since
        #    it requires a full window of motion history.
        swipe = self._detect_swipe()
        if swipe is not None:
            return self._maybe_fire(swipe, confidence=1.0)

        # 2. Static, pose-based gestures.
        finger_state = get_finger_state(hand)
        static_gesture, confidence = self._classify_static(hand, finger_state)

        self._recent_static_gestures.append(static_gesture)
        stabilized = self._stabilize()
        if stabilized is None:
            return GestureResult(Gesture.NONE, confidence)

        return self._maybe_fire(stabilized, confidence)

    def _stabilize(self) -> Optional[Gesture]:
        """Require N consecutive identical, non-NONE gestures before accepting."""
        if len(self._recent_static_gestures) < self.config.stability_frames:
            return None
        if len(set(self._recent_static_gestures)) == 1:
            g = self._recent_static_gestures[0]
            return g if g != Gesture.NONE else None
        return None

    def _maybe_fire(self, gesture: Gesture, confidence: float) -> GestureResult:
        """Apply confidence threshold + cooldown gating before accepting a gesture."""
        if confidence < self.config.confidence_threshold:
            return GestureResult(Gesture.NONE, confidence)

        if not self._cooldown.ready():
            return GestureResult(Gesture.NONE, confidence)

        self._cooldown.fire()
        self.last_gesture = gesture
        self.last_confidence = confidence
        # Clear history so the same held pose doesn't immediately refire.
        self._recent_static_gestures.clear()
        self._wrist_history.clear()
        return GestureResult(gesture, confidence)

    def _detect_swipe(self) -> Optional[Gesture]:
        """Detect a horizontal swipe using wrist x-position across the frame window."""
        if len(self._wrist_history) < self.config.swipe_window_frames:
            return None

        start_x = self._wrist_history[0][0]
        end_x = self._wrist_history[-1][0]
        delta = end_x - start_x

        if abs(delta) < self.config.swipe_min_distance:
            return None

        return Gesture.SWIPE_RIGHT if delta > 0 else Gesture.SWIPE_LEFT

    def _classify_static(
        self, hand: HandResult, finger_state: FingerState
    ) -> Tuple[Gesture, float]:
        """
        Classify the current hand pose into a static gesture.

        Returns:
            (gesture, confidence) — confidence derived from hand detection
            confidence and how cleanly the pose matches the pattern.
        """
        base_conf = max(hand.confidence, 0.5)
        states = finger_state.states  # [thumb, index, middle, ring, pinky]

        # Pinch: thumb tip close to index tip, other fingers curled.
        thumb_pt = hand.landmarks[THUMB_TIP][:2]
        index_pt = hand.landmarks[INDEX_TIP][:2]
        pinch_dist = euclidean_distance(thumb_pt, index_pt)
        if pinch_dist < self.config.pinch_distance_threshold and not any(states[2:]):
            return Gesture.PINCH, base_conf

        # Open palm: all 5 fingers extended.
        if all(states):
            return Gesture.OPEN_PALM, base_conf

        # Closed fist: no fingers extended.
        if not any(states):
            return Gesture.CLOSED_FIST, base_conf

        # Finger gun: thumb + index extended, middle/ring/pinky curled
        # (checked before "Thumbs up" and "Index only" since it shares
        # fingers with both but is a distinct two-finger combination).
        if states[0] and states[1] and not states[2] and not states[3] and not states[4]:
            return Gesture.FINGER_GUN, base_conf

        # Thumbs up: only thumb extended.
        if states[0] and not any(states[1:]):
            return Gesture.THUMBS_UP, base_conf

        # Victory / peace sign: index + middle extended, ring + pinky curled.
        if states[1] and states[2] and not states[3] and not states[4]:
            return Gesture.VICTORY, base_conf

        # Index only (pointing): only index extended.
        if states[1] and not states[0] and not states[2] and not states[3] and not states[4]:
            return Gesture.POINTING, base_conf

        return Gesture.NONE, 0.0

    def cooldown_remaining(self) -> float:
        """Seconds left before another gesture can fire."""
        return self._cooldown.remaining()
