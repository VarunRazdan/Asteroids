"""System tests — performance benchmarks."""

import random
import time
from unittest.mock import patch

import pygame

from asteroid import Asteroid
from constants import ASTEROID_MIN_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player
from shot import Shot


class TestPerformance:
    def test_60_updates_under_one_second(self, reset_sprite_groups):
        """60 update ticks (1 second of gameplay) should complete in < 1 wall-second.

        This ensures the update logic (without rendering) runs fast enough
        to sustain 60 FPS on typical hardware.
        """
        random.seed(42)
        Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # Spawn many objects to stress the update loop
        for _ in range(30):
            a = Asteroid(
                random.uniform(0, SCREEN_WIDTH),
                random.uniform(0, SCREEN_HEIGHT),
                random.choice([ASTEROID_MIN_RADIUS, ASTEROID_MIN_RADIUS * 2,
                               ASTEROID_MIN_RADIUS * 3]),
            )
            a.velocity = pygame.Vector2(
                random.uniform(-80, 80), random.uniform(-80, 80)
            )

        # Fire a bunch of shots
        for i in range(20):
            s = Shot(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            s.velocity = pygame.Vector2(
                random.uniform(-500, 500), random.uniform(-500, 500)
            )

        keys = [False] * 512
        keys[pygame.K_w] = True
        dt = 1 / 60

        start = time.perf_counter()
        with patch("pygame.key.get_pressed", return_value=keys):
            for _ in range(60):
                reset_sprite_groups["updatable"].update(dt)
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"60 updates took {elapsed:.3f}s (budget: 1.0s)"
