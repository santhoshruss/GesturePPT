# Internal API Reference

This document describes the public classes/functions of each module for
developers extending GesturePPT.

## `constants.py`

- `Gesture` (Enum): `NONE, SWIPE_RIGHT, SWIPE_LEFT, OPEN_PALM, CLOSED_FIST, THUMBS_UP, VICTORY, PINCH, POINTING`
- `Action` (Enum): `NONE, NEXT_SLIDE, PREV_SLIDE, START_SLIDESHOW, END_SLIDESHOW, BLACK_SCREEN, WHITE_SCREEN`
- `GESTURE_ACTION_MAP: Dict[Gesture, Action]` — default gesture→action bindings

## `config.py`

- `CameraConfig`, `HandDetectorConfig`, `GestureConfig`, `UIConfig`, `LoggingConfig` — dataclasses
- `AppConfig` — bundles the above
- `CONFIG: AppConfig` — shared singleton instance used by `main.py`

## `camera.py`

### `class Camera(config: CameraConfig)`
- `open() -> None` — opens the configured camera index or auto-detects one; raises `CameraError` if none found
- `read() -> Tuple[bool, Optional[np.ndarray], float]` — returns `(success, frame, fps)`; attempts recovery on failure
- `release() -> None` — releases the device
- `is_connected: bool` — current connection state

## `hand_detector.py`

### `class HandResult`
- `landmarks: List[Tuple[float, float, float]]` — 21 normalized (x, y, z) points
- `pixel_landmarks: List[Tuple[int, int]]` — 21 pixel-space (x, y) points
- `handedness: str` — `"Left"` or `"Right"`
- `confidence: float`

### `class HandDetector(config: HandDetectorConfig)`
- `process(frame_bgr: np.ndarray) -> List[HandResult]`
- `draw_landmarks(frame_bgr, results) -> np.ndarray`
- `close() -> None`

## `finger_counter.py`

### `get_finger_state(hand: HandResult) -> FingerState`
- `FingerState.states: List[bool]` — `[thumb, index, middle, ring, pinky]`
- `FingerState.count: int`
- `FingerState.names_up: List[str]`

## `gesture_detector.py`

### `class GestureDetector(config: GestureConfig)`
- `update(hand: Optional[HandResult]) -> GestureResult` — call once per frame
- `reset() -> None` — clears temporal state
- `cooldown_remaining() -> float`

### `class GestureResult`
- `gesture: Gesture`
- `confidence: float`

## `ppt_controller.py`

### `class PPTController()`
- `is_powerpoint_active() -> bool`
- `execute(action: Action, require_ppt_focus: bool = True) -> bool`
- `ppt_detected: bool`

## `cooldown.py`

### `class ActionCooldownManager(default_seconds: float = 1.0)`
- `can_fire(action: Action) -> bool`
- `mark_fired(action: Action) -> None`
- `remaining(action: Action) -> float`
- `reset_all() -> None`

## `ui.py`

### `class OverlayUI(config: UIConfig)`
- `render(frame, gesture, confidence, action, fps, cooldown_remaining, camera_connected, ppt_connected, hands_detected) -> np.ndarray`
- `show(frame) -> int` — displays frame, returns pressed key code
- `close() -> None`

## `logger.py`

- `get_logger(name: str = "GesturePPT") -> logging.Logger`
- `log_gesture_event(logger, gesture: str, confidence: float, action: str) -> None`

## `utils.py`

- `euclidean_distance(p1, p2) -> float`
- `clamp(value, lo, hi) -> float`
- `class FPSCounter` — `.tick() -> float`
- `class Cooldown(seconds)` — `.ready()`, `.remaining()`, `.fire()`, `.reset()`

## Extending: Adding a New Gesture

1. Add a new member to `Gesture` in `constants.py`.
2. Add classification logic in `GestureDetector._classify_static()` (or a
   new motion-based method, following the `_detect_swipe()` pattern).
3. Map it to an `Action` in `GESTURE_ACTION_MAP` (or handle it separately
   if it's not a PPT action, e.g. a mode-switch gesture).
4. Add a keystroke mapping in `ppt_controller._ACTION_KEYS` if it maps to
   a new `Action`.
5. Add unit tests in `tests/test_gesture.py` following existing patterns.
