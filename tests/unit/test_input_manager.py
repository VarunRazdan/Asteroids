"""Tests for InputManager — keyboard and gamepad abstraction."""
from unittest.mock import patch

import pygame
import pytest

from input_manager import InputManager, _apply_deadzone


class TestDeadzone:
    def test_small_value_zeroed(self):
        assert _apply_deadzone(0.05) == 0.0
        assert _apply_deadzone(-0.1) == 0.0

    def test_large_value_passes(self):
        result = _apply_deadzone(0.5)
        assert result > 0.0

    def test_negative_large_value(self):
        result = _apply_deadzone(-0.8)
        assert result < 0.0

    def test_exact_threshold_zeroed(self):
        assert _apply_deadzone(0.15) == 0.0

    def test_max_value(self):
        assert abs(_apply_deadzone(1.0) - 1.0) < 0.01


class TestInputManagerKeyboard:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mgr = InputManager()

    def _make_keys(self, **pressed):
        keys = [False] * 512
        for key_name, val in pressed.items():
            keys[getattr(pygame, key_name)] = val
        return keys

    def test_thrust_with_w(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_w=True)):
            self.mgr.update()
            assert self.mgr.is_thrust() is True

    def test_no_thrust_without_input(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys()):
            self.mgr.update()
            assert self.mgr.is_thrust() is False

    def test_reverse_with_s(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_s=True)):
            self.mgr.update()
            assert self.mgr.is_reverse() is True

    def test_rotation_a_returns_negative(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_a=True)):
            self.mgr.update()
            assert self.mgr.get_rotation() == -1.0

    def test_rotation_d_returns_positive(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_d=True)):
            self.mgr.update()
            assert self.mgr.get_rotation() == 1.0

    def test_rotation_none_returns_zero(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys()):
            self.mgr.update()
            assert self.mgr.get_rotation() == 0.0

    def test_shoot_with_space(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_SPACE=True)):
            self.mgr.update()
            assert self.mgr.is_shoot() is True

    def test_no_joystick_graceful(self):
        """All methods return defaults when no controller is connected."""
        with patch("pygame.key.get_pressed", return_value=self._make_keys()):
            self.mgr.update()
            assert self.mgr.is_thrust() is False
            assert self.mgr.is_reverse() is False
            assert self.mgr.get_rotation() == 0.0
            assert self.mgr.is_shoot() is False
            assert self.mgr.has_joystick is False


class TestInputManagerOneShot:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mgr = InputManager()

    def _make_keys(self, **pressed):
        keys = [False] * 512
        for key_name, val in pressed.items():
            keys[getattr(pygame, key_name)] = val
        return keys

    def test_bomb_one_shot(self):
        """is_bomb returns True only on the first frame of a press."""
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_b=True)):
            self.mgr.update()
            assert self.mgr.is_bomb() is True
            # Second call in same frame state should be False
            assert self.mgr.is_bomb() is False

    def test_bomb_re_triggers_after_release(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_b=True)):
            self.mgr.update()
            self.mgr.is_bomb()  # consume

        with patch("pygame.key.get_pressed", return_value=self._make_keys()):
            self.mgr.update()
            self.mgr.is_bomb()  # release frame

        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_b=True)):
            self.mgr.update()
            assert self.mgr.is_bomb() is True

    def test_pause_one_shot(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_ESCAPE=True)):
            self.mgr.update()
            assert self.mgr.is_pause() is True
            assert self.mgr.is_pause() is False

    def test_confirm_one_shot(self):
        with patch("pygame.key.get_pressed", return_value=self._make_keys(K_RETURN=True)):
            self.mgr.update()
            assert self.mgr.is_confirm() is True
            assert self.mgr.is_confirm() is False
