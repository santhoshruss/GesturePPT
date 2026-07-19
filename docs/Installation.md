# Installation Guide

## Prerequisites

- **Windows 11** (Windows 10 also works but is untested)
- **Python 3.12+** — download from https://www.python.org/downloads/
  during install, check **"Add python.exe to PATH"**
- **Microsoft PowerPoint** installed
- A functioning **webcam** (built-in laptop camera or USB)
- **VS Code** (recommended) — https://code.visualstudio.com/

## 1. Get the Project

Extract the `GesturePPT.zip` archive (or `git clone` the repository) to a
folder of your choice, e.g. `C:\Projects\GesturePPT`.

## 2. Automatic Setup (recommended)

Double-click **`setup.bat`**, or run it from a terminal in the project folder:

```bat
setup.bat
```

This will:
1. Create a virtual environment in `venv\`
2. Activate it
3. Upgrade `pip`
4. Install every dependency listed in `requirements.txt`

## 3. Manual Setup (alternative)

If you prefer to do it by hand, open a terminal (PowerShell or cmd) in the
project folder:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Verify the Installation

```bat
python -c "import cv2, mediapipe, pyautogui, numpy, pynput; print('All dependencies OK')"
```

If this prints `All dependencies OK` without errors, you're ready to go.

## 5. Run the Application

```bat
run.bat
```

or manually:

```bat
venv\Scripts\activate
python main.py
```

A window titled **"GesturePPT — Touchless Presentation Controller"** should
open showing your webcam feed with the HUD overlay.

## 6. Common Installation Issues

> **Important:** `requirements.txt` pins `mediapipe==0.10.14` deliberately.
> Newer MediaPipe releases removed the legacy `mp.solutions.hands` API that
> this project uses, in favor of a new Tasks API with separately-downloaded
> model files. Installing a newer/unpinned `mediapipe` version will cause
> `AttributeError: module 'mediapipe' has no attribute 'solutions'` at
> startup. Stick to the pinned version unless you migrate `hand_detector.py`
> to the Tasks API yourself.

| Problem | Solution |
|---|---|
| `python` not recognized | Reinstall Python and check "Add to PATH", or use `py` instead of `python` |
| `pip install mediapipe` fails | Ensure you're on Python 3.12 (not 3.13+ — MediaPipe wheels lag behind new Python releases); use a 3.12 interpreter |
| `pywin32` import errors | Run `python venv\Scripts\pywin32_postinstall.py -install` from an elevated terminal |
| Webcam permission denied | Windows Settings → Privacy & Security → Camera → allow desktop apps to access the camera |
| Antivirus flags PyAutoGUI/pynput | These libraries simulate keyboard input and are sometimes flagged by aggressive AV heuristics; add an exclusion for the project folder if needed |

See [`Troubleshooting.md`](Troubleshooting.md) for runtime issues.

## 7. Building a Standalone Executable

Once dependencies are installed:

```bat
pyinstaller --onefile --windowed --name GesturePPT ^
  --hidden-import=mediapipe ^
  --hidden-import=cv2 ^
  --hidden-import=pyautogui ^
  --hidden-import=pynput ^
  --hidden-import=win32gui ^
  --hidden-import=win32con ^
  main.py
```

The `.exe` will appear in `dist\GesturePPT.exe`. Note: MediaPipe ships model
files that PyInstaller sometimes fails to bundle automatically — if the
executable fails to find model assets at runtime, add:

```bat
--add-data "venv\Lib\site-packages\mediapipe\modules;mediapipe/modules"
```

to the command above (adjust the path to your actual `site-packages`
location).
