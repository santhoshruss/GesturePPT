"""
camera.py
---------
Webcam initialization, automatic detection, resolution handling, FPS
calculation, and camera failure recovery.
"""

import time
from typing import Optional, Tuple

import cv2
import numpy as np

from config import CameraConfig
from logger import get_logger
from utils import FPSCounter

logger = get_logger(__name__)


class CameraError(Exception):
    """Raised when the camera cannot be opened or read from after retries."""


class Camera:
    """
    Wraps cv2.VideoCapture with auto-detection, resolution configuration,
    FPS tracking, and automatic reconnection on failure.
    """

    def __init__(self, config: CameraConfig) -> None:
        self.config = config
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps_counter = FPSCounter()
        self.is_connected: bool = False

    def open(self) -> None:
        """Open the configured camera index, falling back to auto-detection."""
        index = self.config.index
        if not self._try_open(index):
            logger.warning("Camera index %d failed, scanning for any available camera.", index)
            found = self._auto_detect()
            if found is None:
                raise CameraError("No available webcam could be found.")
            index = found

        self._configure_resolution()
        self.is_connected = True
        logger.info("Camera opened successfully at index %d.", index)

    def _try_open(self, index: int) -> bool:
        """Attempt to open a specific camera index. Returns True on success."""
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if cv2.CAP_DSHOW else cv2.VideoCapture(index)
        if not cap.isOpened():
            cap.release()
            return False
        self._cap = cap
        return True

    def _auto_detect(self, max_scan: int = 5) -> Optional[int]:
        """Scan camera indices 0..max_scan-1 for the first working device."""
        for idx in range(max_scan):
            if self._try_open(idx):
                return idx
        return None

    def _configure_resolution(self) -> None:
        """Apply the configured width/height/fps to the open capture device."""
        if self._cap is None:
            return
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self._cap.set(cv2.CAP_PROP_FPS, self.config.target_fps)

    def read(self) -> Tuple[bool, Optional[np.ndarray], float]:
        """
        Read a single frame, attempting reconnection on failure.

        Returns:
            (success, frame_or_None, current_fps)
        """
        if self._cap is None:
            raise CameraError("Camera has not been opened yet.")

        ok, frame = self._cap.read()
        if not ok or frame is None:
            logger.warning("Frame read failed. Attempting camera recovery.")
            if self._recover():
                ok, frame = self._cap.read()
            if not ok or frame is None:
                self.is_connected = False
                return False, None, 0.0

        self.is_connected = True
        fps = self._fps_counter.tick()
        return True, frame, fps

    def _recover(self) -> bool:
        """Attempt to close and reopen the camera after a read failure."""
        for attempt in range(1, self.config.max_reconnect_attempts + 1):
            logger.info("Reconnect attempt %d/%d...", attempt, self.config.max_reconnect_attempts)
            self.release()
            time.sleep(self.config.reconnect_delay_sec)
            try:
                self.open()
                return True
            except CameraError:
                continue
        logger.error("Camera recovery failed after %d attempts.", self.config.max_reconnect_attempts)
        return False

    def release(self) -> None:
        """Release the underlying capture device, if open."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self.is_connected = False
