"""Unit tests for weapon strategy classes."""

import pygame

from colors import SHOT_COLOR_DEFAULT, SHOT_COLOR_RAPID, SHOT_COLOR_SPREAD
from constants import (
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    RAPID_FIRE_COOLDOWN,
    RAPID_FIRE_SHOT_RADIUS,
    SHOT_RADIUS,
    SPREAD_SHOT_COOLDOWN,
    SPREAD_SHOT_COUNT,
)
from weapons import RapidFire, SingleShot, SpreadShot


class TestSingleShot:
    def test_single_shot_fires_one(self):
        weapon = SingleShot()
        pos = pygame.Vector2(400, 300)
        shots = weapon.fire(pos, 0)
        assert len(shots) == 1

    def test_single_shot_cooldown(self):
        weapon = SingleShot()
        assert weapon.cooldown == PLAYER_SHOOT_COOLDOWN_SECONDS

    def test_single_shot_color(self):
        weapon = SingleShot()
        assert weapon.shot_color == SHOT_COLOR_DEFAULT

    def test_single_shot_has_velocity(self):
        weapon = SingleShot()
        pos = pygame.Vector2(400, 300)
        shots = weapon.fire(pos, 0)
        assert shots[0].velocity.length() > 0


class TestSpreadShot:
    def test_spread_shot_fires_five(self):
        weapon = SpreadShot()
        pos = pygame.Vector2(400, 300)
        shots = weapon.fire(pos, 0)
        assert len(shots) == SPREAD_SHOT_COUNT

    def test_spread_shot_cooldown(self):
        weapon = SpreadShot()
        assert weapon.cooldown == SPREAD_SHOT_COOLDOWN

    def test_spread_shot_color(self):
        weapon = SpreadShot()
        assert weapon.shot_color == SHOT_COLOR_SPREAD

    def test_spread_shots_different_directions(self):
        weapon = SpreadShot()
        pos = pygame.Vector2(400, 300)
        shots = weapon.fire(pos, 0)
        # At least some shots should have different velocity directions
        angles = set()
        for s in shots:
            # Normalise angle to detect distinct directions
            angle = round(s.velocity.angle_to(pygame.Vector2(1, 0)), 1)
            angles.add(angle)
        assert len(angles) > 1


class TestRapidFire:
    def test_rapid_fire_fires_one(self):
        weapon = RapidFire()
        pos = pygame.Vector2(400, 300)
        shots = weapon.fire(pos, 0)
        assert len(shots) == 1

    def test_rapid_fire_cooldown_is_short(self):
        weapon = RapidFire()
        assert weapon.cooldown == RAPID_FIRE_COOLDOWN
        assert weapon.cooldown < PLAYER_SHOOT_COOLDOWN_SECONDS

    def test_rapid_fire_color(self):
        weapon = RapidFire()
        assert weapon.shot_color == SHOT_COLOR_RAPID

    def test_rapid_fire_uses_smaller_radius(self):
        weapon = RapidFire()
        pos = pygame.Vector2(400, 300)
        shots = weapon.fire(pos, 0)
        assert shots[0].radius == RAPID_FIRE_SHOT_RADIUS
        assert RAPID_FIRE_SHOT_RADIUS < SHOT_RADIUS


class TestShotColorsCorrect:
    """Cross-check that each weapon produces shots with the right color."""

    def test_shot_colors_correct(self):
        pos = pygame.Vector2(0, 0)
        single_shots = SingleShot().fire(pos, 0)
        spread_shots = SpreadShot().fire(pos, 0)
        rapid_shots = RapidFire().fire(pos, 0)

        assert single_shots[0].color == SHOT_COLOR_DEFAULT
        assert spread_shots[0].color == SHOT_COLOR_SPREAD
        assert rapid_shots[0].color == SHOT_COLOR_RAPID
