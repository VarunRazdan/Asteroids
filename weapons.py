"""Weapon strategy classes. Player.active_weapon delegates shooting to these."""
import pygame

from colors import SHOT_COLOR_DEFAULT, SHOT_COLOR_RAPID, SHOT_COLOR_SPREAD
from constants import (
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    RAPID_FIRE_COOLDOWN,
    RAPID_FIRE_SHOT_RADIUS,
    RAPID_FIRE_SHOT_SPEED,
    SHOT_RADIUS,
    SPREAD_SHOT_ANGLE,
    SPREAD_SHOT_COOLDOWN,
    SPREAD_SHOT_COUNT,
)
from shot import Shot


class Weapon:
    """Base weapon class."""

    def __init__(self, name, cooldown, shot_color):
        self.name = name
        self.cooldown = cooldown
        self.shot_color = shot_color

    def fire(self, position, rotation):
        """Return a list of Shot objects. Override in subclasses."""
        return []


class SingleShot(Weapon):
    def __init__(self):
        super().__init__("SINGLE", PLAYER_SHOOT_COOLDOWN_SECONDS, SHOT_COLOR_DEFAULT)

    def fire(self, position, rotation):
        shot = Shot(position.x, position.y, SHOT_RADIUS, self.shot_color)
        direction = pygame.Vector2(0, 1).rotate(rotation)
        shot.velocity = direction * PLAYER_SHOOT_SPEED
        return [shot]


class SpreadShot(Weapon):
    def __init__(self):
        super().__init__("SPREAD", SPREAD_SHOT_COOLDOWN, SHOT_COLOR_SPREAD)

    def fire(self, position, rotation):
        shots = []
        half_angle = SPREAD_SHOT_ANGLE / 2
        step = SPREAD_SHOT_ANGLE / (SPREAD_SHOT_COUNT - 1) if SPREAD_SHOT_COUNT > 1 else 0
        for i in range(SPREAD_SHOT_COUNT):
            angle_offset = -half_angle + step * i
            shot = Shot(position.x, position.y, SHOT_RADIUS, self.shot_color)
            direction = pygame.Vector2(0, 1).rotate(rotation + angle_offset)
            shot.velocity = direction * PLAYER_SHOOT_SPEED
            shots.append(shot)
        return shots


class RapidFire(Weapon):
    def __init__(self):
        super().__init__("RAPID", RAPID_FIRE_COOLDOWN, SHOT_COLOR_RAPID)

    def fire(self, position, rotation):
        shot = Shot(position.x, position.y, RAPID_FIRE_SHOT_RADIUS, self.shot_color)
        direction = pygame.Vector2(0, 1).rotate(rotation)
        shot.velocity = direction * RAPID_FIRE_SHOT_SPEED
        return [shot]
