"""Unit tests for the Shot class."""

import pytest

from colors import SHOT_COLOR_DEFAULT
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SHOT_LIFETIME, SHOT_RADIUS
from shot import Shot


class TestShotMovement:
    def test_update_moves_position(self, make_shot):
        s = make_shot(x=400, y=300, dx=0, dy=-500)
        orig_y = s.position.y
        s.update(1 / 60)
        # Position should have moved in the velocity direction
        assert s.position.y < orig_y

    def test_position_changes_proportional_to_dt(self, make_shot):
        s = make_shot(x=400, y=300, dx=100, dy=0)
        orig_x = s.position.x
        dt = 0.5
        s.update(dt)
        expected_x = orig_x + 100 * dt
        assert s.position.x == pytest.approx(expected_x)


class TestShotDespawn:
    def test_auto_despawn_by_lifetime(self, make_shot):
        """Shot should kill itself when age >= SHOT_LIFETIME."""
        s = make_shot(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2, dx=0, dy=0)
        # Simulate just past the lifetime
        s.age = SHOT_LIFETIME - 0.01
        s.update(0.02)  # age becomes >= SHOT_LIFETIME
        assert not s.alive()

    def test_not_despawned_before_lifetime(self, make_shot):
        """Shot should stay alive before reaching lifetime."""
        s = make_shot(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2, dx=0, dy=0)
        s.update(0.1)
        assert s.alive()

    def test_auto_despawn_off_screen(self, make_shot):
        """Shot should kill itself when off-screen by > 50 pixels."""
        s = make_shot(x=SCREEN_WIDTH + 60, y=300, dx=0, dy=0)
        s.update(0.01)
        assert not s.alive()

    def test_auto_despawn_off_screen_left(self, make_shot):
        s = make_shot(x=-60, y=300, dx=0, dy=0)
        s.update(0.01)
        assert not s.alive()

    def test_auto_despawn_off_screen_top(self, make_shot):
        s = make_shot(x=300, y=-60, dx=0, dy=0)
        s.update(0.01)
        assert not s.alive()

    def test_auto_despawn_off_screen_bottom(self, make_shot):
        s = make_shot(x=300, y=SCREEN_HEIGHT + 60, dx=0, dy=0)
        s.update(0.01)
        assert not s.alive()


class TestShotColor:
    def test_color_parameter(self):
        """Shot should use the provided color or default."""
        s = Shot(100, 100)
        assert s.color == SHOT_COLOR_DEFAULT

    def test_custom_color(self):
        custom = (255, 0, 0)
        s = Shot(100, 100, color=custom)
        assert s.color == custom

    def test_default_radius(self):
        s = Shot(100, 100)
        assert s.radius == SHOT_RADIUS
