"""Integration tests — simulate multi-object game-loop interactions."""

import random
from unittest.mock import patch

import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_MIN_RADIUS,
    PLAYER_SHOOT_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from player import Player
from shot import Shot


class TestAsteroidShotCollision:
    def test_asteroid_shot_collision_chain(self, reset_sprite_groups):
        """A shot that collides with an asteroid should trigger split logic."""
        random.seed(42)
        a = Asteroid(400, 300, ASTEROID_MIN_RADIUS * 2)
        a.velocity = pygame.Vector2(0, 0)

        s = Shot(400, 300)
        s.velocity = pygame.Vector2(0, -PLAYER_SHOOT_SPEED)

        # They share the same position so they collide immediately
        assert a.collides_with(s)

        # Simulate what the game loop does: detect collision, split, kill shot
        a.split()
        s.kill()

        assert not a.alive()
        assert not s.alive()
        # Medium asteroid split should create two children
        children = [sp for sp in reset_sprite_groups["asteroids"] if sp is not a]
        assert len(children) == 2

    def test_asteroid_split_cascade(self, reset_sprite_groups):
        """Splitting a large asteroid produces children that can themselves split."""
        random.seed(42)
        # Create a large asteroid (radius = 3 * MIN)
        large = Asteroid(400, 300, ASTEROID_MIN_RADIUS * 3)
        large.velocity = pygame.Vector2(50, 0)
        large.split()

        # Two medium children
        mediums = [s for s in reset_sprite_groups["asteroids"]]
        assert len(mediums) == 2

        # Now split each medium child
        for m in mediums:
            m.velocity = pygame.Vector2(30, 30)
            m.split()

        # Each medium produces 2 small children = 4 smalls total
        smalls = [s for s in reset_sprite_groups["asteroids"] if s.alive()]
        assert len(smalls) == 4

        # Small asteroids should NOT produce children
        for sm in smalls:
            sm.velocity = pygame.Vector2(10, 10)
            sm.split()
        remaining = [s for s in reset_sprite_groups["asteroids"] if s.alive()]
        assert len(remaining) == 0


class TestFullSimulation:
    def test_full_60_frame_simulation(self, reset_sprite_groups):
        """Run 60 frames of updates with a player and asteroids; nothing should crash."""
        random.seed(42)
        p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # Spawn a few asteroids
        asteroids_list = []
        for i in range(5):
            a = Asteroid(100 + i * 100, 100, ASTEROID_MIN_RADIUS * 2)
            a.velocity = pygame.Vector2(random.uniform(-50, 50),
                                        random.uniform(-50, 50))
            asteroids_list.append(a)

        keys = [False] * 512
        with patch("pygame.key.get_pressed", return_value=keys):
            for frame in range(60):
                dt = 1 / 60
                # Update all sprites through the group
                reset_sprite_groups["updatable"].update(dt)

        # Player and asteroids should still be alive
        assert p.alive()
        for a in asteroids_list:
            assert a.alive()
