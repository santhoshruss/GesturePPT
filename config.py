"""
config.py
---------
Centralized, user-tunable configuration for GesturePPT.

Edit the values below (or override via environment variables / a future
settings UI) to tune camera behavior, gesture sensitivity, and cooldowns
without touching application logic.
"""

import os
from dataclasses import dataclass, field


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class CameraConfig:
    """Configuration for webcam capture."""
    index: int = _env_int("GESTUREPPT_CAM_INDEX", 0)
    width: int = _env_int("GESTUREPPT_CAM_WIDTH", 1280)
    height: int = _env_int("GESTUREPPT_CAM_HEIGHT", 720)
    target_fps: int = _env_int("GESTUREPPT_TARGET_FPS", 30)
    max_reconnect_attempts: int = 5
    reconnect_delay_sec: float = 1.5


@dataclass
class HandDetectorConfig:
    """Configuration for MediaPipe Hands."""
    max_num_hands: int = 2
    min_detection_confidence: float = _env_float("GESTUREPPT_DETECTION_CONF", 0.7)
    min_tracking_confidence: float = _env_float("GESTUREPPT_TRACKING_CONF", 0.6)
    model_complexity: int = 1  # 0 = fast/light, 1 = full


@dataclass
class GestureConfig:
    """Configuration for gesture recognition & stability."""
    # Minimum confidence (0-1) a gesture must have before it's considered valid
    confidence_threshold: float = _env_float("GESTUREPPT_GESTURE_THRESHOLD", 0.75)

    # Number of consecutive identical frames required before a gesture is
    # accepted (debouncing / smoothing).
    stability_frames: int = _env_int("GESTUREPPT_STABILITY_FRAMES", 5)

    # Seconds to wait after an action fires before another can fire.
    cooldown_seconds: float = _env_float("GESTUREPPT_COOLDOWN", 1.2)

    # Pixel-normalized distance the wrist must travel horizontally,
    # within the swipe_window_frames, to register as a swipe.
    swipe_min_distance: float = 0.18
    swipe_window_frames: int = 10

    # Normalized distance below which thumb+index tips count as a "pinch"
    pinch_distance_threshold: float = 0.045


@dataclass
class UIConfig:
    """Configuration for the on-screen overlay UI."""
    window_name: str = "GesturePPT — Touchless Presentation Controller"
    window_width: int = 1280
    window_height: int = 720
    show_landmarks: bool = True
    show_fps: bool = True
    overlay_alpha: float = 0.55


@dataclass
class LoggingConfig:
    """Configuration for application logging."""
    log_dir: str = "logs"
    log_file: str = "gestureppt.log"
    level: str = "INFO"
    max_bytes: int = 2_000_000
    backup_count: int = 3


@dataclass
class AppConfig:
    """Top-level configuration bundle passed around the application."""
    camera: CameraConfig = field(default_factory=CameraConfig)
    hand_detector: HandDetectorConfig = field(default_factory=HandDetectorConfig)
    gesture: GestureConfig = field(default_factory=GestureConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


# A single shared instance used throughout the app.
CONFIG = AppConfig()
