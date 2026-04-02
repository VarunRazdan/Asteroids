"""Layered starfield background with nebula patches, cached to a single surface."""

import random

import pygame

from colors import BLACK, NEBULA_COLORS, STAR_COLORS
from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STAR_COUNT_FAR,
    STAR_COUNT_MEDIUM,
    STAR_COUNT_NEAR,
)


class StarfieldBackground:
    """Three-layer parallax starfield with nebula patches.

    Everything is pre-rendered to a single cached surface on init,
    so drawing is a single blit per frame.
    """

    def __init__(self):
        self._surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self._surface.fill(BLACK)
        self._render()

    def _render(self):
        """Generate all stars and nebulae onto the cached surface."""
        # Draw nebula patches first (behind stars)
        self._draw_nebulae()

        # Draw star layers from far (dim, small) to near (bright, large)
        star_layers = [
            (STAR_COUNT_FAR, 1, STAR_COLORS[0]),
            (STAR_COUNT_MEDIUM, 2, STAR_COLORS[1]),
            (STAR_COUNT_NEAR, 3, STAR_COLORS[2]),
        ]

        for count, size, color in star_layers:
            for _ in range(count):
                x = random.randint(0, SCREEN_WIDTH - 1)
                y = random.randint(0, SCREEN_HEIGHT - 1)

                if size == 1:
                    self._surface.set_at((x, y), color)
                else:
                    pygame.draw.circle(self._surface, color, (x, y), size)

    def _draw_nebulae(self):
        """Draw 2-3 large semi-transparent nebula patches."""
        nebula_count = random.randint(2, 3)

        # Create a temporary SRCALPHA surface for blending
        nebula_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        nebula_surface.fill((0, 0, 0, 0))

        for _ in range(nebula_count):
            color = random.choice(NEBULA_COLORS)
            cx = random.randint(100, SCREEN_WIDTH - 100)
            cy = random.randint(100, SCREEN_HEIGHT - 100)
            radius = random.randint(120, 250)

            # Draw multiple concentric circles with decreasing alpha
            # to create a soft glow effect
            steps = 8
            for i in range(steps, 0, -1):
                t = i / steps
                r = int(radius * t)
                # Alpha falls off toward the edge
                a = max(1, int(color[3] * (1.0 - (1.0 - t) ** 0.5)))
                nebula_color = (color[0], color[1], color[2], a)
                pygame.draw.circle(nebula_surface, nebula_color, (cx, cy), r)

        self._surface.blit(nebula_surface, (0, 0))

    def draw(self, screen):
        """Single blit of the cached background surface."""
        screen.blit(self._surface, (0, 0))
