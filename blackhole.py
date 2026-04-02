"""Black hole — gravity well that sucks in nearby objects."""
import math
import random

import pygame

from circleshape import CircleShape
from colors import BLACKHOLE_ACCRETION, BLACKHOLE_CENTER, BLACKHOLE_RING_COLORS
from constants import (
    BLACKHOLE_KILL_RADIUS,
    BLACKHOLE_LIFETIME,
    BLACKHOLE_PULL_FORCE,
    BLACKHOLE_PULL_RADIUS,
    BLACKHOLE_RADIUS,
    BLACKHOLE_SPAWN_RATE_MAX,
    BLACKHOLE_SPAWN_RATE_MIN,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class BlackHole(CircleShape):
    """Stationary gravity well that pulls nearby objects inward."""

    def __init__(self, x, y):
        super().__init__(x, y, BLACKHOLE_RADIUS)
        self.age = 0
        self.rotation = 0

    @property
    def alive_time_left(self):
        return max(0, BLACKHOLE_LIFETIME - self.age)

    @property
    def fade_alpha(self):
        """1.0 when fully alive, fades to 0 in the last 3 seconds."""
        remaining = self.alive_time_left
        if remaining > 3.0:
            return 1.0
        return remaining / 3.0

    def apply_gravity(self, entity, dt):
        """Pull an entity toward this black hole. Returns True if within kill radius."""
        diff = self.position - entity.position
        dist = diff.length()

        if dist < BLACKHOLE_KILL_RADIUS:
            return True  # kill zone

        if dist > BLACKHOLE_PULL_RADIUS:
            return False  # too far

        # Inverse-square pull, capped to avoid extreme forces at close range
        force_mag = min(BLACKHOLE_PULL_FORCE / max(dist * dist, 100), 800)
        force_mag *= self.fade_alpha  # weaken as it fades

        direction = diff / dist
        entity.velocity += direction * force_mag * dt
        return False

    def draw(self, screen):
        cx, cy = int(self.position.x), int(self.position.y)
        alpha = self.fade_alpha

        # Draw on a transparent surface for alpha support
        size = (BLACKHOLE_PULL_RADIUS * 2 + 20, BLACKHOLE_PULL_RADIUS * 2 + 20)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        center = (size[0] // 2, size[1] // 2)

        # Concentric rotating rings
        self.rotation += 1.5
        for i, color in enumerate(BLACKHOLE_RING_COLORS):
            ring_r = self.radius + (i + 1) * 12
            ring_alpha = int(alpha * (100 - i * 20))
            pygame.draw.circle(
                surf, (*color, ring_alpha), center, ring_r, 2,
            )

        # Accretion particles (small dots orbiting)
        num_dots = 12
        for i in range(num_dots):
            angle = math.radians(self.rotation * (2 + i * 0.3) + i * (360 / num_dots))
            orbit_r = self.radius + 8 + i * 4
            dx = int(math.cos(angle) * orbit_r)
            dy = int(math.sin(angle) * orbit_r)
            dot_alpha = int(alpha * (180 - i * 12))
            pygame.draw.circle(
                surf, (*BLACKHOLE_ACCRETION, max(0, dot_alpha)),
                (center[0] + dx, center[1] + dy), 2,
            )

        # Dark center
        center_alpha = int(alpha * 220)
        pygame.draw.circle(surf, (*BLACKHOLE_CENTER, center_alpha), center, self.radius)
        # Slightly lighter inner ring
        inner_alpha = int(alpha * 140)
        pygame.draw.circle(
            surf, (40, 15, 70, inner_alpha), center, self.radius, 2,
        )

        # Blit centered
        blit_x = cx - size[0] // 2
        blit_y = cy - size[1] // 2
        screen.blit(surf, (blit_x, blit_y))

    def update(self, dt):
        self.age += dt
        if self.age >= BLACKHOLE_LIFETIME:
            self.kill()


class BlackHoleSpawner(pygame.sprite.Sprite):
    """Timer-based spawner for black holes. One at a time."""

    def __init__(self, blackholes_group, player_ref):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self._blackholes = blackholes_group
        self._player = player_ref
        self._timer = random.uniform(
            BLACKHOLE_SPAWN_RATE_MIN, BLACKHOLE_SPAWN_RATE_MAX
        )

    def update(self, dt):
        self._timer -= dt
        if self._timer <= 0:
            self._timer = random.uniform(
                BLACKHOLE_SPAWN_RATE_MIN, BLACKHOLE_SPAWN_RATE_MAX
            )
            if len(self._blackholes) > 0:
                return
            # Random position, away from edges and player
            margin = 150
            for _ in range(20):  # try up to 20 times
                x = random.uniform(margin, SCREEN_WIDTH - margin)
                y = random.uniform(margin, SCREEN_HEIGHT - margin)
                if self._player and self._player.alive():
                    dist = pygame.Vector2(x, y).distance_to(
                        self._player.position
                    )
                    if dist < 200:
                        continue
                BlackHole(x, y)
                return
