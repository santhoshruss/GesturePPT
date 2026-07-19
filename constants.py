"""
constants.py
------------
Static constants used across the GesturePPT application.
Nothing here should change at runtime — for user-tunable values see config.py.
"""

from enum import Enum, auto


class Gesture(str, Enum):
    """Enumeration of all gestures the system can recognize."""
    NONE = "None"
    SWIPE_RIGHT = "Swipe Right"
    SWIPE_LEFT = "Swipe Left"
    OPEN_PALM = "Open Palm"
    CLOSED_FIST = "Closed Fist"
    THUMBS_UP = "Thumbs Up"
    VICTORY = "Victory Sign"
    PINCH = "Pinch"
    POINTING = "Index Only"
    FINGER_GUN = "Finger Gun"


class Action(str, Enum):
    """Enumeration of PowerPoint actions the controller can execute."""
    NONE = "None"
    NEXT_SLIDE = "Next Slide"
    PREV_SLIDE = "Previous Slide"
    START_SLIDESHOW = "Start Slideshow"
    END_SLIDESHOW = "End Slideshow"
    BLACK_SCREEN = "Black Screen"
    WHITE_SCREEN = "White Screen"


# Maps a recognized gesture to the PowerPoint action it triggers.
GESTURE_ACTION_MAP = {
    Gesture.OPEN_PALM: Action.NEXT_SLIDE,
    Gesture.POINTING: Action.PREV_SLIDE,
    Gesture.THUMBS_UP: Action.START_SLIDESHOW,
    Gesture.VICTORY: Action.END_SLIDESHOW,
    Gesture.CLOSED_FIST: Action.BLACK_SCREEN,
    Gesture.FINGER_GUN: Action.WHITE_SCREEN,
}

# MediaPipe hand landmark indices (21 points per hand)
WRIST = 0
THUMB_TIP = 4
THUMB_IP = 3
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18

FINGER_TIPS = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
FINGER_PIPS = [THUMB_IP, INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP]
FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

APP_NAME = "GesturePPT"
APP_VERSION = "1.0.0"
