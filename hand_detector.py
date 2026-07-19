"""
hand_detector.py
----------------
Wraps MediaPipe Hands to detect one or two hands, draw landmarks, and
expose normalized/pixel landmark coordinates plus a confidence score.
"""

from dataclasses import dataclass
from typing import List, Optional

import cv2
import mediapipe as mp
import numpy as np

from config import HandDetectorConfig
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class HandResult:
    """Result of hand detection for a single detected hand."""
    landmarks: List[tuple]        # [(x_norm, y_norm, z_norm), ...] 21 points
    pixel_landmarks: List[tuple]  # [(x_px, y_px), ...] 21 points
    handedness: str                # "Left" or "Right"
    confidence: float


class HandDetector:
    """Detects hands in a BGR frame using MediaPipe Hands."""

    def __init__(self, config: HandDetectorConfig) -> None:
        self.config = config
        self._mp_hands = mp.solutions.hands
        self._mp_drawing = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles

        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.max_num_hands,
            model_complexity=config.model_complexity,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence,
        )

    def process(self, frame_bgr: np.ndarray) -> List[HandResult]:
        """
        Run hand detection on a frame.

        Args:
            frame_bgr: The camera frame in BGR color order.

        Returns:
            A list of HandResult, one per detected hand (empty if none found).
        """
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self._hands.process(frame_rgb)

        hands_out: List[HandResult] = []
        if not results.multi_hand_landmarks:
            return hands_out

        handedness_list = results.multi_handedness or []
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
            pixel_landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]

            label = "Unknown"
            score = 0.0
            if i < len(handedness_list):
                classification = handedness_list[i].classification[0]
                label = classification.label
                score = classification.score

            hands_out.append(
                HandResult(
                    landmarks=landmarks,
                    pixel_landmarks=pixel_landmarks,
                    handedness=label,
                    confidence=score,
                )
            )

        return hands_out

    def draw_landmarks(self, frame_bgr: np.ndarray, results: List[HandResult]) -> np.ndarray:
        """Draw hand landmarks and connections directly onto the frame (in-place-ish)."""
        # MediaPipe's drawing utils expect the raw NormalizedLandmarkList proto,
        # so we re-run drawing using stored pixel coordinates for simplicity/perf.
        for hand in results:
            for (x, y) in hand.pixel_landmarks:
                cv2.circle(frame_bgr, (x, y), 4, (0, 255, 0), -1)
            connections = self._mp_hands.HAND_CONNECTIONS
            for start_idx, end_idx in connections:
                x1, y1 = hand.pixel_landmarks[start_idx]
                x2, y2 = hand.pixel_landmarks[end_idx]
                cv2.line(frame_bgr, (x1, y1), (x2, y2), (255, 255, 255), 1)
        return frame_bgr

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()
