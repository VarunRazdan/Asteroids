"""Unit tests for collision detection functions."""

import pygame
import pytest

from collision import circles_collide, sat_triangle_circle


class TestSATTriangleCircle:
    def _make_triangle(self, cx, cy, size=50):
        """Helper: equilateral-ish triangle centered at (cx, cy)."""
        return [
            pygame.Vector2(cx, cy - size),
            pygame.Vector2(cx - size, cy + size),
            pygame.Vector2(cx + size, cy + size),
        ]

    def test_sat_triangle_circle_overlap(self):
        """Circle inside / overlapping triangle should collide."""
        tri = self._make_triangle(100, 100)
        circle_pos = pygame.Vector2(100, 100)
        assert sat_triangle_circle(tri, circle_pos, 10) is True

    def test_sat_triangle_circle_no_overlap(self):
        """Circle far from triangle should not collide."""
        tri = self._make_triangle(100, 100)
        circle_pos = pygame.Vector2(500, 500)
        assert sat_triangle_circle(tri, circle_pos, 10) is False

    def test_sat_triangle_circle_edge_case(self):
        """Circle just barely touching a triangle edge."""
        # Place triangle at origin area, circle just outside one edge
        tri = [
            pygame.Vector2(0, -50),
            pygame.Vector2(-50, 50),
            pygame.Vector2(50, 50),
        ]
        # Circle placed well outside the triangle
        circle_pos = pygame.Vector2(200, 200)
        assert sat_triangle_circle(tri, circle_pos, 5) is False

    def test_sat_circle_on_vertex(self):
        """Circle centered exactly on a triangle vertex should collide."""
        tri = self._make_triangle(100, 100, size=50)
        # Place circle at the top vertex
        circle_pos = pygame.Vector2(100, 50)
        assert sat_triangle_circle(tri, circle_pos, 10) is True

    @pytest.mark.parametrize("radius,expected", [
        (1, False),   # too small to reach the triangle
        (300, True),  # large enough to overlap (nearest vertex ~226 px away)
    ])
    def test_sat_parametrized_radius(self, radius, expected):
        tri = self._make_triangle(100, 100, size=30)
        circle_pos = pygame.Vector2(300, 300)
        result = sat_triangle_circle(tri, circle_pos, radius)
        assert result is expected


class TestCirclesCollide:
    def test_circles_collide_overlap(self):
        p1 = pygame.Vector2(100, 100)
        p2 = pygame.Vector2(110, 100)
        # distance=10, radii_sum=40 => 100 < 1600 => True
        assert circles_collide(p1, 20, p2, 20) is True

    def test_circles_collide_no_overlap(self):
        p1 = pygame.Vector2(0, 0)
        p2 = pygame.Vector2(100, 0)
        # distance=100, radii_sum=20 => 10000 < 400 => False
        assert circles_collide(p1, 10, p2, 10) is False

    def test_circles_collide_exactly_touching(self):
        """Strict < means exactly touching circles do NOT collide."""
        p1 = pygame.Vector2(0, 0)
        p2 = pygame.Vector2(20, 0)
        # distance=20, radii_sum=20 => 400 < 400 => False
        assert circles_collide(p1, 10, p2, 10) is False

    @pytest.mark.parametrize("x2,r1,r2,expected", [
        (5, 10, 10, True),    # heavily overlapping
        (19, 10, 10, True),   # just overlapping
        (21, 10, 10, False),  # just apart
        (0, 10, 10, True),    # concentric
    ])
    def test_circles_collide_parametrized(self, x2, r1, r2, expected):
        p1 = pygame.Vector2(0, 0)
        p2 = pygame.Vector2(x2, 0)
        assert circles_collide(p1, r1, p2, r2) is expected
