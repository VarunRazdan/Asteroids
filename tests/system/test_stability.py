"""System tests — long-running stability checks."""

import random
from unittest.mock import patch

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import ASTEROID_MIN_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player


class TestStability:
    def test_600_frames_no_crash(self, reset_sprite_groups):
        """Simulate 600 frames (10 seconds at 60 FPS) with active gameplay.

        This verifies that no exception is thrown during an extended run
        with asteroids spawning, shots firing, and collisions occurring.
        """
        random.seed(42)

        Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        AsteroidField()

        # Pre-spawn some asteroids
        for _ in range(10):
            a = Asteroid(
                random.uniform(0, SCREEN_WIDTH),
                random.uniform(0, SCREEN_HEIGHT),
                random.choice([ASTEROID_MIN_RADIUS, ASTEROID_MIN_RADIUS * 2,
                               ASTEROID_MIN_RADIUS * 3]),
            )
            a.velocity = pygame.Vector2(
                random.uniform(-80, 80), random.uniform(-80, 80)
            )

        keys = [False] * 512
        keys[pygame.K_w] = True      # constant thrust
        keys[pygame.K_d] = True      # constant rotation
        keys[pygame.K_SPACE] = True  # constant shooting

        dt = 1 / 60
        with patch("pygame.key.get_pressed", return_value=keys):
            for frame in range(600):
                reset_sprite_groups["updatable"].update(dt)

                # Periodic collision handling (simplified)
                for asteroid in list(reset_sprite_groups["asteroids"]):
                    for shot in list(reset_sprite_groups["shots"]):
                        if asteroid.collides_with(shot):
                            asteroid.split()
                            shot.kill()
                            break

        # If we get here without an exception, the test passes
        assert len(reset_sprite_groups["updatable"]) > 0
