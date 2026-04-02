"""Unit tests for the Player class."""

from unittest.mock import patch

import pygame
import pytest

from constants import (
    PLAYER_INVULNERABILITY_TIME,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    PLAYER_TURN_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_DURATION,
)


class TestPlayerInitialState:
    def test_initial_state(self, player):
        assert player.rotation == 0
        assert player.shoot_timer == 0
        assert player.is_thrusting is False
        assert player.shield_active is False
        assert player.invulnerable is False
        assert player.bombs == 0
        assert player.score == 0
        assert player.combo_multiplier == 1

    def test_initial_position(self, player):
        assert player.position.x == SCREEN_WIDTH / 2
        assert player.position.y == SCREEN_HEIGHT / 2

    def test_initial_radius(self, player):
        assert player.radius == PLAYER_RADIUS


class TestPlayerTriangle:
    def test_triangle_returns_three_points(self, player):
        tri = player.triangle()
        assert len(tri) == 3
        for point in tri:
            assert isinstance(point, pygame.Vector2)

    def test_get_triangle_points_matches_triangle(self, player):
        assert player.get_triangle_points() == player.triangle()


class TestPlayerRotation:
    def test_rotate_changes_rotation(self, player):
        original = player.rotation
        player.rotate(0.1)  # positive dt
        assert player.rotation != original
        assert player.rotation == pytest.approx(original + PLAYER_TURN_SPEED * 0.1)

    def test_rotate_negative_dt(self, player):
        original = player.rotation
        player.rotate(-0.1)
        assert player.rotation == pytest.approx(original - PLAYER_TURN_SPEED * 0.1)


class TestPlayerMovement:
    def _no_keys(self):
        """Return a key state with nothing pressed."""
        keys = [False] * 512
        return keys

    def _keys_with(self, *keycodes):
        """Return a key state with the given keys pressed."""
        keys = [False] * 512
        for k in keycodes:
            keys[k] = True
        return keys

    def test_acceleration_physics(self, player):
        """Pressing W (thrust) should increase velocity magnitude."""
        keys = self._keys_with(pygame.K_w)
        with patch("pygame.key.get_pressed", return_value=keys):
            player.update(1 / 60)
        assert player.velocity.length() > 0
        assert player.is_thrusting is True

    def test_friction_slows_down(self, player):
        """Without any keys held, friction should reduce velocity each frame."""
        player.velocity = pygame.Vector2(200, 0)
        keys = self._no_keys()
        with patch("pygame.key.get_pressed", return_value=keys):
            player.update(1 / 60)
        # After friction, speed should be less than 200
        assert player.velocity.length() < 200

    def test_max_speed_cap(self, player):
        """Velocity should never exceed PLAYER_MAX_SPEED."""
        player.velocity = pygame.Vector2(1000, 1000)
        keys = self._no_keys()
        with patch("pygame.key.get_pressed", return_value=keys):
            player.update(1 / 60)
        assert player.velocity.length() <= PLAYER_MAX_SPEED + 0.01

    def test_rotation_via_keys(self, player):
        """Pressing D should increase rotation, pressing A should decrease."""
        original = player.rotation
        keys = self._keys_with(pygame.K_d)
        with patch("pygame.key.get_pressed", return_value=keys):
            player.update(1 / 60)
        assert player.rotation > original


class TestPlayerShooting:
    def test_shoot_creates_shots(self, player, reset_sprite_groups):
        """Player.shoot() should return a list of Shot objects."""
        shots = player.shoot()
        assert len(shots) >= 1
        # The shots should be in the shots sprite group
        assert len(reset_sprite_groups["shots"]) >= 1

    def test_shoot_cooldown(self, player):
        """Shooting immediately after should return empty (cooldown active)."""
        player.shoot()
        # shoot_timer is now > 0
        assert player.shoot_timer > 0
        result = player.shoot()
        assert result == []

    def test_shoot_after_cooldown_expires(self, player):
        """After cooldown expires, shooting should work again."""
        player.shoot()
        player.shoot_timer = 0  # manually expire cooldown
        result = player.shoot()
        assert len(result) >= 1


class TestPlayerShield:
    def test_shield_activation(self, player):
        player.activate_shield()
        assert player.shield_active is True
        assert player.shield_timer == SHIELD_DURATION

    def test_shield_expires(self, player):
        player.activate_shield()
        keys = [False] * 512
        with patch("pygame.key.get_pressed", return_value=keys):
            # Simulate enough time for shield to expire
            for _ in range(int(SHIELD_DURATION * 60) + 60):
                player.update(1 / 60)
        assert player.shield_active is False


class TestPlayerInvulnerability:
    def test_invulnerability(self, player):
        player.make_invulnerable()
        assert player.invulnerable is True
        assert player.invulnerable_timer == PLAYER_INVULNERABILITY_TIME

    def test_invulnerability_expires(self, player):
        player.make_invulnerable()
        keys = [False] * 512
        with patch("pygame.key.get_pressed", return_value=keys):
            # Simulate enough time for invulnerability to expire
            for _ in range(int(PLAYER_INVULNERABILITY_TIME * 60) + 60):
                player.update(1 / 60)
        assert player.invulnerable is False


class TestPlayerWrapPosition:
    def test_wrap_position(self, player):
        """Player should wrap around screen edges."""
        player.position.x = SCREEN_WIDTH + PLAYER_RADIUS + 10
        keys = [False] * 512
        with patch("pygame.key.get_pressed", return_value=keys):
            player.update(1 / 60)
        # After wrapping, x should be on the left side
        assert player.position.x == pytest.approx(-PLAYER_RADIUS, abs=1)
