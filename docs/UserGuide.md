# User Guide

## Getting Started

1. Open your presentation in Microsoft PowerPoint.
2. Launch GesturePPT (`run.bat` or `python main.py`).
3. Position yourself so your hand is clearly visible to the webcam,
   roughly arm's length away, with reasonable lighting on your hand.
4. Click into the PowerPoint window (or start the slideshow with `F5`) so
   it has focus — GesturePPT only sends keystrokes when PowerPoint is the
   active window, as a safety measure.
5. Perform gestures. The HUD in the top-left shows the recognized gesture
   and confidence; the top-right shows FPS and connection status.

## Gesture Reference

| Gesture | How to perform it | Result |
|---|---|---|
| **Swipe Right** | Move your open hand steadily to the right | Next Slide |
| **Swipe Left** | Move your open hand steadily to the left | Previous Slide |
| **Thumbs Up** | Make a fist, extend only your thumb upward | Start Slideshow |
| **Victory Sign** | Extend index + middle finger only (peace sign) | End Slideshow |
| **Closed Fist** | Curl all fingers into a fist | Black Screen |
| **Open Palm** | Show all five fingers extended, palm facing camera | White Screen |

## Tips for Reliable Recognition

- **Lighting**: avoid strong backlighting (e.g., sitting in front of a
  window); front-lit or evenly lit rooms work best.
- **Distance**: keep your hand roughly 40–80 cm from the camera.
- **Hold static poses briefly**: static gestures (fist, palm, thumbs up,
  victory) need a few consecutive stable frames to register — a quick
  flash won't trigger, which is intentional (prevents false positives).
- **Swipes should be deliberate**: a clear, continuous horizontal motion
  works better than a short flick.
- **One hand at a time**: while two hands can be detected, only the first
  detected hand drives gesture recognition in this version.
- **Cooldown**: after any action fires, there's a short cooldown (default
  ~1.2s) before another action can trigger — this is shown in the HUD.

## On-Screen HUD

- **Top-left**: current gesture name, confidence %, last executed action,
  and remaining cooldown time.
- **Top-right**: live FPS, camera connection status, PowerPoint detection
  status, and number of hands currently detected.
- Press **`q`** at any time to close the application.

## Adjusting Sensitivity

If gestures trigger too easily or too rarely, edit `config.py`:

- `GestureConfig.confidence_threshold` — raise to require cleaner poses.
- `GestureConfig.stability_frames` — raise to require a longer hold.
- `GestureConfig.cooldown_seconds` — raise to slow down repeat triggers.
- `GestureConfig.swipe_min_distance` — raise if swipes fire too easily,
  lower if swipes are hard to trigger.

## Troubleshooting

See [`Troubleshooting.md`](Troubleshooting.md) for solutions to common
runtime problems (camera not found, PowerPoint not responding, poor
detection in low light, etc.).
