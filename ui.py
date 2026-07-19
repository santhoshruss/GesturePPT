"""
ui.py
-----
Renders the live camera feed with OpenCV overlays: hand landmarks,
gesture name, confidence, FPS, current action, cooldown timer, and
system status (camera/PowerPoint connectivity).
"""

from typing import Optional

import cv2
import numpy as np

from config import UIConfig
from constants import Action, Gesture

_COLOR_GREEN = (80, 220, 100)
_COLOR_RED = (60, 60, 230)
_COLOR_YELLOW = (0, 210, 255)
_COLOR_WHITE = (255, 255, 255)
_COLOR_BG = (30, 30, 30)


class OverlayUI:
    """Draws the heads-up-display overlay onto camera frames."""

    def __init__(self, config: UIConfig) -> None:
        self.config = config

    def render(
        self,
        frame: np.ndarray,
        gesture: Gesture,
        confidence: float,
        action: Action,
        fps: float,
        cooldown_remaining: float,
        camera_connected: bool,
        ppt_connected: bool,
        hands_detected: int,
    ) -> np.ndarray:
        """
        Draw the full overlay panel onto the given frame and return it.

        Args:
            frame: BGR frame (already containing landmark drawings, if any).
            gesture: Currently recognized gesture.
            confidence: Confidence score of that gesture (0-1).
            action: Most recent action executed.
            fps: Current rolling FPS.
            cooldown_remaining: Seconds left before next action can fire.
            camera_connected: Whether the webcam is currently connected.
            ppt_connected: Whether PowerPoint appears to be active.
            hands_detected: Number of hands currently detected.

        Returns:
            The frame with overlay drawn on it.
        """
        h, w = frame.shape[:2]
        panel_h = 170
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, panel_h), _COLOR_BG, -1)
        cv2.addWeighted(overlay, self.config.overlay_alpha, frame, 1 - self.config.overlay_alpha, 0, frame)

        y = 28
        line_gap = 26

        self._put(frame, f"Gesture: {gesture.value}", 15, y, _COLOR_YELLOW)
        y += line_gap
        self._put(frame, f"Confidence: {int(confidence * 100)}%", 15, y, _COLOR_WHITE)
        y += line_gap
        self._put(frame, f"Action: {action.value}", 15, y, _COLOR_GREEN if action != Action.NONE else _COLOR_WHITE)
        y += line_gap
        self._put(frame, f"Cooldown: {cooldown_remaining:.1f}s", 15, y, _COLOR_WHITE)

        # Right column: system status
        right_x = w - 260
        y2 = 28
        if self.config.show_fps:
            self._put(frame, f"FPS: {fps:.1f}", right_x, y2, _COLOR_WHITE)
            y2 += line_gap

        cam_color = _COLOR_GREEN if camera_connected else _COLOR_RED
        self._put(frame, f"Camera: {'Connected' if camera_connected else 'Disconnected'}", right_x, y2, cam_color)
        y2 += line_gap

        ppt_color = _COLOR_GREEN if ppt_connected else _COLOR_RED
        self._put(frame, f"PPT: {'Connected' if ppt_connected else 'Not Detected'}", right_x, y2, ppt_color)
        y2 += line_gap

        hand_color = _COLOR_GREEN if hands_detected > 0 else _COLOR_RED
        self._put(frame, f"Hands: {hands_detected}", right_x, y2, hand_color)

        cv2.putText(
            frame, "Press 'q' to quit", (15, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, _COLOR_WHITE, 1, cv2.LINE_AA,
        )
        return frame

    @staticmethod
    def _put(frame: np.ndarray, text: str, x: int, y: int, color) -> None:
        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.62, color, 2, cv2.LINE_AA)

    def show(self, frame: np.ndarray) -> int:
        """Display the frame in the app window and return the pressed key code."""
        cv2.imshow(self.config.window_name, frame)
        return cv2.waitKey(1) & 0xFF

    def close(self) -> None:
        """Destroy all OpenCV windows."""
        cv2.destroyAllWindows()
