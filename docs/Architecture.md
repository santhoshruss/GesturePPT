# Architecture

## Overview

GesturePPT follows a modular, single-responsibility pipeline. Each stage
consumes the previous stage's output and knows nothing about the stages
beyond its immediate neighbor, which keeps the system testable and easy to
extend.

```
Camera --> HandDetector --> FingerCounter --> GestureDetector --> PPTController --> OverlayUI
             (MediaPipe)                        (stability,
                                                  cooldown,
                                                  swipe motion)
```

## Module Responsibilities

| Module              | Responsibility                                                        |
|---------------------|------------------------------------------------------------------------|
| `camera.py`          | Open/read/reconnect the webcam; report FPS                            |
| `hand_detector.py`    | Run MediaPipe Hands; return landmarks + handedness + confidence       |
| `finger_counter.py`    | Convert landmarks into per-finger extended/curled booleans            |
| `gesture_detector.py`   | Classify static poses + detect swipe motion; debounce & cooldown-gate |
| `ppt_controller.py`      | Map an Action to a keystroke; verify PowerPoint has focus             |
| `cooldown.py`             | Per-action cooldown bookkeeping (independent of gesture-level cooldown)|
| `ui.py`                    | Render the HUD overlay (gesture, confidence, FPS, status)            |
| `logger.py`                 | Rotating file + console logging                                     |
| `config.py`                   | All tunable parameters in one place (dataclasses)                  |
| `constants.py`                  | Enums for Gesture/Action, landmark indices, gesture→action map    |

## Data Flow Per Frame

1. `Camera.read()` returns a BGR frame + current FPS.
2. `HandDetector.process()` returns a list of `HandResult` (landmarks,
   pixel coordinates, handedness, confidence) — empty if no hand visible.
3. If a hand is present, `GestureDetector.update()`:
   - Appends the wrist position to a rolling history buffer and checks for
     a horizontal **swipe** first (motion-based gestures take priority).
   - Otherwise calls `finger_counter.get_finger_state()` and classifies the
     pose into one of the static gestures (open palm, fist, thumbs up,
     victory, pinch, pointing).
   - Requires `stability_frames` consecutive identical classifications
     before accepting (debouncing / smoothing).
   - Gates the final result behind a confidence threshold and a cooldown
     timer so a held pose cannot repeatedly fire.
4. If a `Gesture` maps to an `Action` (see `GESTURE_ACTION_MAP` in
   `constants.py`), `PPTController.execute()`:
   - Checks whether PowerPoint is the active window.
   - Checks its own independent action-level cooldown.
   - Sends the mapped keystroke via PyAutoGUI.
5. `OverlayUI.render()` draws the HUD (gesture, confidence, action, FPS,
   cooldown, camera/PPT/hand status) onto the frame, which is then shown
   in an OpenCV window.
6. Every recognized gesture + executed action is logged via `logger.py`.

## Design Principles Applied

- **Single Responsibility** — each module does exactly one job.
- **Dependency Injection** — `Config` dataclasses are passed into
  constructors rather than imported as globals inside logic modules,
  making unit testing straightforward (see `tests/test_gesture.py`).
- **Open/Closed** — new gestures are added by extending
  `GestureDetector._classify_static` and `GESTURE_ACTION_MAP` without
  touching `main.py`, `camera.py`, or `ui.py`.
- **Fail-safe defaults** — camera reconnection, PPT-focus checks, and
  cooldown gates all default to the safe/conservative behavior (skip the
  action) rather than risk sending stray keystrokes.

## Future Expansion

The pipeline is intentionally structured so the following can be added as
new modules/branches without restructuring existing code:

- **Air mouse mode** — a new `air_mouse.py` consuming `HandResult` directly,
  toggled by a dedicated gesture, running in parallel to `GestureDetector`.
- **Laser pointer / annotation** — an `annotation.py` module that draws on
  an overlay canvas using fingertip position, activated by a mode-switch
  gesture (e.g., pinch-and-hold).
- **Voice commands** — a `voice_controller.py` module feeding the same
  `Action` enum consumed by `PPTController.execute()`.
- **Custom/trainable gestures** — replace the rule-based
  `_classify_static()` with a small classifier (e.g., scikit-learn/TF) that
  still returns `(Gesture, confidence)`, keeping the rest of the pipeline
  unchanged.
- **IP/wireless camera** — extend `Camera` with an RTSP/HTTP stream backend
  behind the same `read()` interface.
- **Cloud analytics** — tap into `logger.log_gesture_event()` to also emit
  events to a remote endpoint.
