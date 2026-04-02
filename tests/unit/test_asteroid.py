"""Unit tests for the Asteroid class."""

import random

import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_VERTICES_LARGE,
    ASTEROID_VERTICES_MEDIUM,
    ASTEROID_VERTICES_SMALL,
    SCREEN_WIDTH,
)


class TestAsteroidInit:
    def test_lumpy_vertices_generated(self, make_asteroid):
        """Asteroids should have a list of base_vertices (lumpy polygon)."""
        random.seed(42)
        a = make_asteroid(radius=ASTEROID_MIN_RADIUS * 2)
        assert hasattr(a, "base_vertices")
        assert len(a.base_vertices) >= ASTEROID_VERTICES_MEDIUM[0]
        # Each vertex should be a Vector2
        for v in a.base_vertices:
            assert isinstance(v, pygame.Vector2)

    def test_large_asteroid_vertex_count(self):
        random.seed(42)
        a = Asteroid(100, 100, ASTEROID_MIN_RADIUS * 3)
        vmin, vmax = ASTEROID_VERTICES_LARGE
        assert vmin <= len(a.base_vertices) <= vmax

    def test_small_asteroid_vertex_count(self):
        random.seed(42)
        a = Asteroid(100, 100, ASTEROID_MIN_RADIUS)
        vmin, vmax = ASTEROID_VERTICES_SMALL
        assert vmin <= len(a.base_vertices) <= vmax


class TestAsteroidRotation:
    def test_rotation_changes_over_time(self, make_asteroid):
        a = make_asteroid()
        original = a.rotation_angle
        a.velocity = pygame.Vector2(0, 0)
        a.update(1 / 60)
        # If angular_velocity != 0, rotation should change.
        # Use a seed that gives non-zero angular velocity.
        if a.angular_velocity != 0:
            assert a.rotation_angle != original
        else:
            # Extremely unlikely with random.uniform but handle gracefully
            assert a.rotation_angle == original


class TestAsteroidSplit:
    def test_split_kills_self(self, make_asteroid, reset_sprite_groups):
        a = make_asteroid(radius=ASTEROID_MIN_RADIUS * 2)
        a.velocity = pygame.Vector2(50, 50)
        a.split()
        assert not a.alive()

    def test_split_small_no_children(self, reset_sprite_groups):
        """The smallest asteroid should not spawn children on split."""
        a = Asteroid(100, 100, ASTEROID_MIN_RADIUS)
        a.velocity = pygame.Vector2(50, 50)
        a.split()
        assert not a.alive()
        # Only the original was in the group; after kill, the group should
        # contain 0 of the original. But split() of a small asteroid produces
        # no new children.
        # Count asteroids that are NOT the original
        remaining = [s for s in reset_sprite_groups["asteroids"] if s is not a]
        assert len(remaining) == 0

    def test_split_large_creates_two(self, reset_sprite_groups):
        """A large asteroid should produce exactly two children on split."""
        random.seed(42)
        a = Asteroid(400, 300, ASTEROID_MIN_RADIUS * 3)
        a.velocity = pygame.Vector2(50, 50)
        a.split()
        # The original is killed, two new ones are created
        remaining = [s for s in reset_sprite_groups["asteroids"] if s is not a]
        assert len(remaining) == 2

    def test_split_children_correct_radius(self, reset_sprite_groups):
        """Children should have radius = parent radius - ASTEROID_MIN_RADIUS."""
        random.seed(42)
        parent_radius = ASTEROID_MIN_RADIUS * 3
        a = Asteroid(400, 300, parent_radius)
        a.velocity = pygame.Vector2(50, 50)
        a.split()
        children = [s for s in reset_sprite_groups["asteroids"] if s is not a]
        expected_radius = parent_radius - ASTEROID_MIN_RADIUS
        for child in children:
            assert child.radius == expected_radius


class TestAsteroidWrapPosition:
    def test_wrap_position(self):
        a = Asteroid(SCREEN_WIDTH + 100, 300, ASTEROID_MIN_RADIUS)
        a.velocity = pygame.Vector2(0, 0)
        a.update(1 / 60)
        # Should have wrapped to the left side
        assert a.position.x == -a.radius
