"""
main.py
-------
Entry point for GesturePPT — the AI-powered touchless PowerPoint controller.

Wires together: Camera -> HandDetector -> GestureDetector -> PPTController,
with a live OpenCV overlay UI, structured logging, and graceful error
handling for webcam disconnects and missing hands.

Run with:
    python main.py
"""

import sys

import cv2

from camera import Camera, CameraError
from config import CONFIG
from constants import Action, Gesture, GESTURE_ACTION_MAP
from gesture_detector import GestureDetector
from hand_detector import HandDetector
from logger import get_logger, log_gesture_event
from ppt_controller import PPTController
from ui import OverlayUI

logger = get_logger(__name__)


class GesturePPTApp:
    """Top-level application orchestrator."""

    def __init__(self) -> None:
        self.camera = Camera(CONFIG.camera)
        self.hand_detector = HandDetector(CONFIG.hand_detector)
        self.gesture_detector = GestureDetector(CONFIG.gesture)
        self.ppt_controller = PPTController()
        self.ui = OverlayUI(CONFIG.ui)
        self._running = False

    def run(self) -> None:
        """Main application loop: capture -> detect -> recognize -> act -> render."""
        try:
            self.camera.open()
        except CameraError as exc:
            logger.error("Fatal: could not open any webcam. %s", exc)
            print(f"ERROR: {exc}\nPlease check that your webcam is connected and not in use "
                  f"by another application.")
            sys.exit(1)

        self._running = True
        logger.info("GesturePPT started. Press 'q' in the preview window to quit.")

        last_action = Action.NONE

        try:
            while self._running:
                ok, frame, fps = self.camera.read()
                if not ok or frame is None:
                    logger.error("Camera unavailable. Exiting main loop.")
                    break

                frame = cv2.flip(frame, 1)  # mirror for natural interaction
                hands = self.hand_detector.process(frame)

                gesture = Gesture.NONE
                confidence = 0.0
                action = Action.NONE

                if hands:
                    primary_hand = hands[0]
                    result = self.gesture_detector.update(primary_hand)
                    gesture, confidence = result.gesture, result.confidence

                    if CONFIG.ui.show_landmarks:
                        frame = self.hand_detector.draw_landmarks(frame, hands)

                    mapped_action = GESTURE_ACTION_MAP.get(gesture)
                    if mapped_action is not None:
                        executed = self.ppt_controller.execute(mapped_action)
                        if executed:
                            action = mapped_action
                            last_action = action
                            log_gesture_event(logger, gesture.value, confidence, action.value)
                else:
                    self.gesture_detector.update(None)

                frame = self.ui.render(
                    frame=frame,
                    gesture=gesture,
                    confidence=confidence,
                    action=action if action != Action.NONE else last_action,
                    fps=fps,
                    cooldown_remaining=self.gesture_detector.cooldown_remaining(),
                    camera_connected=self.camera.is_connected,
                    ppt_connected=self.ppt_controller.ppt_detected,
                    hands_detected=len(hands),
                )

                key = self.ui.show(frame)
                if key == ord("q"):
                    logger.info("Quit key pressed. Shutting down.")
                    break

        except KeyboardInterrupt:
            logger.info("Interrupted by user (Ctrl+C).")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Release all resources cleanly."""
        self._running = False
        self.camera.release()
        self.hand_detector.close()
        self.ui.close()
        logger.info("GesturePPT shut down cleanly.")


def main() -> None:
    app = GesturePPTApp()
    app.run()


if __name__ == "__main__":
    main()
