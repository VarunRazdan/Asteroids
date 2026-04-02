"""System tests — memory / leak checks for sprite lifecycle."""


import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_MIN_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from shot import Shot


class TestShotsDespawn:
    def test_shots_despawn_offscreen(self, reset_sprite_groups):
        """Shots that leave the screen boundary should be removed from groups."""
        # Fire shots heading off every edge
        directions = [
            pygame.Vector2(0, -1000),   # up
            pygame.Vector2(0, 1000),    # down
            pygame.Vector2(-1000, 0),   # left
            pygame.Vector2(1000, 0),    # right
        ]
        for d in directions:
            s = Shot(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            s.velocity = d

        initial_count = len(reset_sprite_groups["shots"])
        assert initial_count == 4

        # Simulate enough frames for the shots to leave the screen
        dt = 1 / 60
        for _ in range(120):  # 2 seconds
            reset_sprite_groups["updatable"].update(dt)

        # All shots should have been killed (off-screen or lifetime)
        remaining = len(reset_sprite_groups["shots"])
        assert remaining == 0, f"Expected 0 shots remaining, got {remaining}"


class TestKilledSpritesRemoved:
    def test_killed_sprites_removed(self, reset_sprite_groups):
        """Calling .kill() on a sprite should remove it from ALL groups."""
        a = Asteroid(400, 300, ASTEROID_MIN_RADIUS)
        a.velocity = pygame.Vector2(0, 0)

        assert a in reset_sprite_groups["asteroids"]
        assert a in reset_sprite_groups["updatable"]
        assert a in reset_sprite_groups["drawable"]

        a.kill()

        assert a not in reset_sprite_groups["asteroids"]
        assert a not in reset_sprite_groups["updatable"]
        assert a not in reset_sprite_groups["drawable"]

    def test_shot_kill_removes_from_groups(self, reset_sprite_groups):
        s = Shot(100, 100)
        s.velocity = pygame.Vector2(0, 0)
        assert s in reset_sprite_groups["shots"]

        s.kill()
        assert s not in reset_sprite_groups["shots"]
        assert s not in reset_sprite_groups["updatable"]

    def test_split_asteroid_removed(self, reset_sprite_groups):
        """After split(), the parent asteroid should be gone from all groups."""
        a = Asteroid(400, 300, ASTEROID_MIN_RADIUS * 2)
        a.velocity = pygame.Vector2(50, 50)
        a.split()

        assert a not in reset_sprite_groups["asteroids"]
        assert a not in reset_sprite_groups["updatable"]
        assert a not in reset_sprite_groups["drawable"]
