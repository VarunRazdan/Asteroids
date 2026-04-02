import math
import random

import pygame

from circleshape import CircleShape
from colors import ASTEROID_COLORS
from constants import (
    ASTEROID_MAX_ANGULAR_VELOCITY,
    ASTEROID_MIN_RADIUS,
    ASTEROID_RADIUS_VARIANCE,
    ASTEROID_SPLIT_ANGLE_MAX,
    ASTEROID_SPLIT_ANGLE_MIN,
    ASTEROID_SPLIT_SPEED_MULT,
    ASTEROID_VERTICES_LARGE,
    ASTEROID_VERTICES_MEDIUM,
    ASTEROID_VERTICES_SMALL,
    LINE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


def _generate_lumpy_vertices(radius, num_vertices):
    """Generate irregular polygon vertices for a lumpy asteroid."""
    vertices = []
    angle_step = 360 / num_vertices
    prev_r = radius

    for i in range(num_vertices):
        angle = math.radians(i * angle_step)
        # Random radius offset, smoothed with previous vertex
        variance = random.uniform(-ASTEROID_RADIUS_VARIANCE, ASTEROID_RADIUS_VARIANCE)
        r = radius * (1 + variance)
        # Smooth with previous to avoid sharp spikes
        r = prev_r * 0.3 + r * 0.7
        r = max(radius * 0.6, min(radius * 1.4, r))  # clamp
        prev_r = r
        vertices.append(pygame.Vector2(math.cos(angle) * r, math.sin(angle) * r))

    return vertices


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

        # Determine vertex count by size tier
        if radius >= ASTEROID_MIN_RADIUS * 2.5:
            vmin, vmax = ASTEROID_VERTICES_LARGE
        elif radius >= ASTEROID_MIN_RADIUS * 1.5:
            vmin, vmax = ASTEROID_VERTICES_MEDIUM
        else:
            vmin, vmax = ASTEROID_VERTICES_SMALL

        num_verts = random.randint(vmin, vmax)
        self.base_vertices = _generate_lumpy_vertices(radius, num_verts)
        self.rotation_angle = random.uniform(0, 360)
        self.angular_velocity = random.uniform(
            -ASTEROID_MAX_ANGULAR_VELOCITY, ASTEROID_MAX_ANGULAR_VELOCITY
        )
        self.color = random.choice(ASTEROID_COLORS)

    def _get_rotated_vertices(self):
        """Return vertices rotated and translated to world position."""
        cos_a = math.cos(math.radians(self.rotation_angle))
        sin_a = math.sin(math.radians(self.rotation_angle))
        result = []
        for v in self.base_vertices:
            rx = v.x * cos_a - v.y * sin_a + self.position.x
            ry = v.x * sin_a + v.y * cos_a + self.position.y
            result.append((rx, ry))
        return result

    def draw(self, screen):
        points = self._get_rotated_vertices()
        pygame.draw.polygon(screen, self.color, points, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        self.rotation_angle += self.angular_velocity * dt
        self.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)

    def split(self):
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        random_angle = random.uniform(ASTEROID_SPLIT_ANGLE_MIN, ASTEROID_SPLIT_ANGLE_MAX)
        new_velocity1 = self.velocity.rotate(random_angle) * ASTEROID_SPLIT_SPEED_MULT
        new_velocity2 = self.velocity.rotate(-random_angle) * ASTEROID_SPLIT_SPEED_MULT
        new_radius = self.radius - ASTEROID_MIN_RADIUS

        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = new_velocity1

        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a2.velocity = new_velocity2
