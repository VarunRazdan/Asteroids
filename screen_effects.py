"""Screen-level visual effects: shake, flash, scanlines, slow-mo."""

import random

import pygame

from colors import WHITE
from constants import (
    FLASH_ALPHA,
    FLASH_DURATION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHAKE_DECAY,
    SHAKE_MAX_OFFSET,
    SHAKE_POWER,
    SLOWMO_DURATION,
    SLOWMO_RETURN_SPEED,
    SLOWMO_SCALE,
)


class ScreenShake:
    """Trauma-based camera shake.

    Shake magnitude = trauma^SHAKE_POWER * SHAKE_MAX_OFFSET.
    Trauma decays over time and is clamped to [0, 1].
    """

    def __init__(self):
        self._trauma = 0.0

    def add_trauma(self, amount):
        """Add trauma (clamped to [0, 1])."""
        self._trauma = min(1.0, self._trauma + amount)

    def update(self, dt):
        """Decay trauma over time."""
        self._trauma = max(0.0, self._trauma - SHAKE_DECAY * dt)

    def get_offset(self):
        """Return (x, y) pixel offset for the current frame."""
        if self._trauma <= 0:
            return (0, 0)

        magnitude = (self._trauma ** SHAKE_POWER) * SHAKE_MAX_OFFSET
        ox = random.uniform(-1, 1) * magnitude
        oy = random.uniform(-1, 1) * magnitude
        return (int(ox), int(oy))

    @property
    def trauma(self):
        return self._trauma


class ScreenFlash:
    """Brief white flash overlay that fades out."""

    def __init__(self):
        self._alpha = 0
        self._timer = 0.0
        self._duration = FLASH_DURATION
        self._surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def trigger(self, alpha=FLASH_ALPHA):
        """Start a flash at the given alpha intensity."""
        self._alpha = alpha
        self._timer = self._duration

    def update(self, dt):
        """Fade the flash to zero."""
        if self._timer <= 0:
            self._alpha = 0
            return

        self._timer -= dt
        # Linear fade from starting alpha to 0 over duration
        t = max(0.0, self._timer / self._duration)
        self._alpha = int(FLASH_ALPHA * t)

    def draw(self, screen):
        """Draw the semi-transparent white overlay if active."""
        if self._alpha <= 0:
            return

        self._surface.fill((WHITE[0], WHITE[1], WHITE[2], self._alpha))
        screen.blit(self._surface, (0, 0))

    @property
    def active(self):
        return self._alpha > 0


class CRTScanlines:
    """Pre-rendered horizontal scanline overlay for a retro CRT look."""

    def __init__(self):
        self._surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._surface.fill((0, 0, 0, 0))

        # Draw semi-transparent black lines every 3 pixels
        line_color = (0, 0, 0, 40)
        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(
                self._surface, line_color, (0, y), (SCREEN_WIDTH, y)
            )

    def draw(self, screen):
        """Blit the pre-rendered scanline overlay."""
        screen.blit(self._surface, (0, 0))


class SlowMo:
    """Slow-motion time scale effect.

    When triggered, dt is multiplied by SLOWMO_SCALE for SLOWMO_DURATION seconds,
    then smoothly returns to 1.0 at SLOWMO_RETURN_SPEED.
    """

    def __init__(self):
        self._scale = 1.0
        self._timer = 0.0
        self._active = False

    def trigger(self):
        """Start the slow-motion effect."""
        self._scale = SLOWMO_SCALE
        self._timer = SLOWMO_DURATION
        self._active = True

    def update(self, dt):
        """Manage the slow-mo timer and smooth return to normal speed.

        Note: this update should be called with the REAL (unscaled) dt so
        the slow-mo timer counts down in real time.
        """
        if not self._active:
            return

        self._timer -= dt

        if self._timer <= 0:
            # Return phase: smoothly lerp back to 1.0
            self._scale = min(1.0, self._scale + SLOWMO_RETURN_SPEED * dt)
            if self._scale >= 1.0:
                self._scale = 1.0
                self._active = False

    def get_scale(self):
        """Return the current dt multiplier (1.0 = normal speed)."""
        return self._scale

    @property
    def active(self):
        return self._active
