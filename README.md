# GesturePPT — AI-Powered Touchless PowerPoint Controller

Control Microsoft PowerPoint using only hand gestures, captured live through your
webcam. No keyboard, no mouse, no clicker — just your hand.

## Features

- **Next / Previous Slide** — swipe your hand right or left
- **Start Slideshow** — thumbs up
- **End Slideshow** — victory / peace sign
- **Black Screen** — closed fist
- **White Screen** — open palm
- Real-time hand tracking with MediaPipe (up to 2 hands)
- Stabilized gesture recognition (debouncing + cooldown, no repeated triggers)
- Automatic PowerPoint focus detection (keystrokes only sent when PPT is active)
- Automatic webcam detection & reconnection on failure
- Live on-screen HUD: gesture name, confidence, FPS, action, cooldown timer,
  camera/PPT connection status
- Structured logging of every gesture and action to `logs/gestureppt.log`
- Fully configurable via `config.py`

## Architecture

```
Webcam --> Camera --> HandDetector (MediaPipe) --> FingerCounter
                                                        |
                                                        v
                                              GestureDetector (stability,
                                              cooldown, swipe motion)
                                                        |
                                                        v
                                              PPTController (PyAutoGUI
                                              keystrokes + focus detection)
                                                        |
                                                        v
                                                   OverlayUI (HUD)
```

See [`docs/Architecture.md`](docs/Architecture.md) for full details.

## Requirements

- Windows 11
- Python 3.12+
- A working webcam
- Microsoft PowerPoint

## Installation

```bat
setup.bat
```

This creates a virtual environment and installs all dependencies from
`requirements.txt`. See [`docs/Installation.md`](docs/Installation.md) for
manual steps and troubleshooting.

## Running

```bat
run.bat
```

Or manually:

```bat
venv\Scripts\activate
python main.py
```

Open your PowerPoint presentation, start editing or presenting, then perform
gestures in front of your webcam. Press **`q`** in the preview window to quit.

## Controls

| Gesture         | Action           |
|-----------------|------------------|
| Swipe Right     | Next Slide       |
| Swipe Left      | Previous Slide   |
| Thumbs Up       | Start Slideshow  |
| Victory Sign    | End Slideshow    |
| Closed Fist     | Black Screen     |
| Open Palm       | White Screen     |

Full usage walkthrough in [`docs/UserGuide.md`](docs/UserGuide.md).

## Folder Structure

```
GesturePPT/
├── main.py                # Application entry point / orchestrator
├── config.py               # All tunable settings
├── camera.py                # Webcam handling
├── hand_detector.py          # MediaPipe hand tracking
├── finger_counter.py          # Per-finger up/down state
├── gesture_detector.py         # Gesture classification & stability
├── ppt_controller.py           # PowerPoint keystroke automation
├── cooldown.py                  # Action-level cooldown manager
├── ui.py                         # OpenCV HUD overlay
├── logger.py                      # Logging setup
├── utils.py                        # Shared helpers (FPS, cooldown, geometry)
├── constants.py                     # Enums & static mappings
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── setup.bat / run.bat
├── tests/                             # pytest unit tests
├── assets/                             # icons, screenshots, demo gif
└── docs/                                 # extended documentation
```

## Screenshots

_Add screenshots of the live HUD to `assets/screenshots/` and reference them here._

## Building a Windows Executable

```bat
pyinstaller --onefile --windowed --name GesturePPT ^
  --hidden-import=mediapipe ^
  --hidden-import=cv2 ^
  --hidden-import=pyautogui ^
  --hidden-import=pynput ^
  main.py
```

The resulting `.exe` will be in `dist/`. See
[`docs/Installation.md`](docs/Installation.md) for full packaging notes.

## Testing

```bat
pytest tests/
```

## Future Improvements

- Air mouse mode (cursor control via hand position)
- Laser pointer mode with annotation drawing
- Voice command fallback
- Custom/trainable gestures
- IP/wireless camera support
- Presentation timer overlay
- Cloud analytics dashboard

See [`docs/Architecture.md`](docs/Architecture.md#future-expansion) for how the
codebase is structured to support these without major rewrites.

## License

MIT — see [`LICENSE`](LICENSE).
