"""
Unit tests for ppt_controller.py and cooldown.py.
PyAutoGUI key presses are monkeypatched so tests never send real keystrokes.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from constants import Action
from cooldown import ActionCooldownManager
import ppt_controller as ppt_controller_module
from ppt_controller import PPTController


def test_cooldown_manager_blocks_until_elapsed():
    mgr = ActionCooldownManager(default_seconds=10.0)
    assert mgr.can_fire(Action.NEXT_SLIDE) is True
    mgr.mark_fired(Action.NEXT_SLIDE)
    assert mgr.can_fire(Action.NEXT_SLIDE) is False
    # A different action should be unaffected.
    assert mgr.can_fire(Action.PREV_SLIDE) is True


def test_execute_skips_when_ppt_not_focused(monkeypatch):
    controller = PPTController()
    monkeypatch.setattr(controller, "is_powerpoint_active", lambda: False)

    pressed = []
    monkeypatch.setattr(ppt_controller_module.pyautogui, "press", lambda key: pressed.append(key))

    result = controller.execute(Action.NEXT_SLIDE, require_ppt_focus=True)
    assert result is False
    assert pressed == []


def test_execute_sends_key_when_ppt_focused(monkeypatch):
    controller = PPTController()
    monkeypatch.setattr(controller, "is_powerpoint_active", lambda: True)

    pressed = []
    monkeypatch.setattr(ppt_controller_module.pyautogui, "press", lambda key: pressed.append(key))

    result = controller.execute(Action.NEXT_SLIDE, require_ppt_focus=True)
    assert result is True
    assert pressed == ["right"]


def test_execute_none_action_is_noop(monkeypatch):
    controller = PPTController()
    pressed = []
    monkeypatch.setattr(ppt_controller_module.pyautogui, "press", lambda key: pressed.append(key))
    result = controller.execute(Action.NONE)
    assert result is False
    assert pressed == []
