"""Unit tests for CircleShape — the base class for all circular game objects."""

import pygame

from circleshape import CircleShape
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class TestCircleShapeInit:
    def test_init_position_velocity_radius(self):
        cs = CircleShape(100, 200, 15)
        assert cs.position == pygame.Vector2(100, 200)
        assert cs.velocity == pygame.Vector2(0, 0)
        assert cs.radius == 15


class TestCollidesWidth:
    def test_collides_with_overlapping(self):
        a = CircleShape(100, 100, 20)
        b = CircleShape(110, 100, 20)
        # distance=10, sum of radii=40 => 10 < 40 => True
        assert a.collides_with(b) is True

    def test_collides_with_not_touching(self):
        a = CircleShape(0, 0, 10)
        b = CircleShape(100, 0, 10)
        # distance=100, sum of radii=20 => 100 < 20 => False
        assert a.collides_with(b) is False

    def test_collides_with_exactly_touching(self):
        """The implementation uses strict < so exactly-touching circles do NOT collide."""
        a = CircleShape(0, 0, 10)
        b = CircleShape(20, 0, 10)
        # distance=20, sum of radii=20 => 20 < 20 => False
        assert a.collides_with(b) is False


class TestWrapPosition:
    def test_wrap_position_left(self):
        cs = CircleShape(-100, 300, 10)
        # x = -100 < -10 (=-radius), so should wrap to right
        cs.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        assert cs.position.x == SCREEN_WIDTH + cs.radius

    def test_wrap_position_right(self):
        cs = CircleShape(SCREEN_WIDTH + 100, 300, 10)
        # x > SCREEN_WIDTH + radius, so should wrap to left
        cs.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        assert cs.position.x == -cs.radius

    def test_wrap_position_top(self):
        cs = CircleShape(300, -100, 10)
        # y = -100 < -10 (=-radius), so should wrap to bottom
        cs.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        assert cs.position.y == SCREEN_HEIGHT + cs.radius

    def test_wrap_position_bottom(self):
        cs = CircleShape(300, SCREEN_HEIGHT + 100, 10)
        # y > SCREEN_HEIGHT + radius, so should wrap to top
        cs.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        assert cs.position.y == -cs.radius

    def test_no_wrap_when_inside(self):
        cs = CircleShape(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 10)
        orig_x, orig_y = cs.position.x, cs.position.y
        cs.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)
        assert cs.position.x == orig_x
        assert cs.position.y == orig_y
