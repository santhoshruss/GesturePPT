# Troubleshooting

## Camera Issues

**"No available webcam could be found"**
- Ensure no other application (Zoom, Teams, another instance of GesturePPT)
  is currently using the camera.
- Check Windows Settings → Privacy & Security → Camera → allow desktop apps.
- Try a different `CameraConfig.index` value in `config.py` (0, 1, 2...) if
  you have multiple cameras.

**Camera feed freezes or disconnects mid-session**
- GesturePPT automatically attempts up to `max_reconnect_attempts` (default
  5) reconnects with a short delay between each. If it still fails, check
  the USB connection (for external webcams) and restart the app.

**Low FPS / laggy video**
- Lower `CameraConfig.width` / `height` in `config.py` (e.g. 960x540).
- Close other CPU/GPU-intensive applications.
- Set `HandDetectorConfig.model_complexity = 0` for a faster, lighter model.

## Hand Detection Issues

**Hand not detected at all**
- Improve lighting — avoid strong backlight; face a window or lamp instead
  of having it behind you.
- Make sure your whole hand (wrist to fingertips) is in frame.
- Lower `HandDetectorConfig.min_detection_confidence` slightly (e.g. 0.6).

**Multiple hands confuse gesture recognition**
- The app currently only listens to the first detected hand. If a second
  hand is being picked up as "first," step it out of frame or set
  `HandDetectorConfig.max_num_hands = 1` in `config.py`.

**Gestures trigger inconsistently**
- Increase `GestureConfig.stability_frames` for steadier requirements.
- Increase `GestureConfig.confidence_threshold`.
- Make sure your pose closely matches the reference in
  [`UserGuide.md`](UserGuide.md) — e.g., victory sign requires ring and
  pinky fully curled.

## PowerPoint Issues

**"PowerPoint not active/focused; action skipped" appears constantly**
- Click on the PowerPoint window (or start Slide Show with F5) so it has
  OS focus. GesturePPT deliberately refuses to send keystrokes to a
  background window to avoid disrupting other applications.
- If detection still fails, check that your PowerPoint window title
  contains "PowerPoint" (some third-party PowerPoint viewers may use a
  different title); you can relax the check in `ppt_controller.py`'s
  `is_powerpoint_active()` if needed.

**Actions execute but slides don't change**
- Confirm PowerPoint is in a state that accepts the corresponding shortcut
  (e.g., Next/Previous work in both Normal and Slide Show view; Black/White
  screen only apply during Slide Show).

## Installation Issues

See [`Installation.md`](Installation.md#6-common-installation-issues) for
setup-time problems (Python PATH, MediaPipe/Python version mismatches,
pywin32 post-install, antivirus flags).

**`AttributeError: module 'mediapipe' has no attribute 'solutions'`** — you
have a MediaPipe version newer than the pinned `0.10.14`. Run
`pip install "mediapipe==0.10.14"` inside your virtual environment to fix it.

## Still Stuck?

Check `logs/gestureppt.log` for detailed timestamps, recognized gestures,
confidence scores, and error messages — this is usually the fastest way to
pinpoint what's going wrong.
