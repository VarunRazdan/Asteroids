"""Power-up items that drop from destroyed asteroids."""
import math

import pygame

from circleshape import CircleShape
from colors import (
    POWERUP_BOMB_COLOR,
    POWERUP_LIFE_COLOR,
    POWERUP_SHIELD_COLOR,
    POWERUP_SPEED_COLOR,
    POWERUP_WEAPON_RAPID_COLOR,
    POWERUP_WEAPON_SPREAD_COLOR,
    WHITE,
)
from constants import (
    POWERUP_BOB_AMPLITUDE,
    POWERUP_BOB_SPEED,
    POWERUP_LIFETIME,
    POWERUP_RADIUS,
)

SHIELD = "shield"
SPEED = "speed"
WEAPON_SPREAD = "weapon_spread"
WEAPON_RAPID = "weapon_rapid"
BOMB = "bomb"
LIFE = "life"

POWERUP_COLORS = {
    SHIELD: POWERUP_SHIELD_COLOR,
    SPEED: POWERUP_SPEED_COLOR,
    WEAPON_SPREAD: POWERUP_WEAPON_SPREAD_COLOR,
    WEAPON_RAPID: POWERUP_WEAPON_RAPID_COLOR,
    BOMB: POWERUP_BOMB_COLOR,
    LIFE: POWERUP_LIFE_COLOR,
}

ALL_TYPES = [SHIELD, SPEED, WEAPON_SPREAD, WEAPON_RAPID, BOMB, LIFE]


class PowerUp(CircleShape):
    def __init__(self, x, y, powerup_type):
        super().__init__(x, y, POWERUP_RADIUS)
        self.powerup_type = powerup_type
        self.color = POWERUP_COLORS.get(powerup_type, WHITE)
        self.age = 0
        self.base_y = y
        self.pulse_timer = 0

    def draw(self, screen):
        # Pulsing outer ring
        self.pulse_timer += 0.05
        pulse = 1.0 + 0.2 * math.sin(self.pulse_timer * 4)
        outer_r = int(self.radius * pulse)

        # Semi-transparent glow
        glow_surf = pygame.Surface((outer_r * 4, outer_r * 4), pygame.SRCALPHA)
        center = (outer_r * 2, outer_r * 2)
        pygame.draw.circle(glow_surf, (*self.color, 40), center, outer_r)
        screen.blit(glow_surf, (self.position.x - outer_r * 2, self.position.y - outer_r * 2))

        # Solid inner circle
        pygame.draw.circle(screen, self.color, self.position, int(self.radius * 0.6))

        # Type icon
        self._draw_icon(screen)

        # Outer ring
        pygame.draw.circle(screen, self.color, self.position, outer_r, 2)

    def _draw_icon(self, screen):
        """Draw a simple icon indicating the power-up type."""
        cx, cy = int(self.position.x), int(self.position.y)
        r = int(self.radius * 0.3)

        if self.powerup_type == SHIELD:
            # Small ring
            pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r, 1)
        elif self.powerup_type == SPEED:
            # Arrow pointing right
            pygame.draw.polygon(screen, (0, 0, 0), [
                (cx - r, cy - r), (cx + r, cy), (cx - r, cy + r)
            ])
        elif self.powerup_type in (WEAPON_SPREAD, WEAPON_RAPID):
            # Star shape
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                ex = cx + int(math.cos(rad) * r)
                ey = cy + int(math.sin(rad) * r)
                pygame.draw.line(screen, (0, 0, 0), (cx, cy), (ex, ey), 1)
        elif self.powerup_type == BOMB:
            # X mark
            pygame.draw.line(screen, (0, 0, 0), (cx - r, cy - r), (cx + r, cy + r), 2)
            pygame.draw.line(screen, (0, 0, 0), (cx + r, cy - r), (cx - r, cy + r), 2)
        elif self.powerup_type == LIFE:
            # Plus sign
            pygame.draw.line(screen, (0, 0, 0), (cx - r, cy), (cx + r, cy), 2)
            pygame.draw.line(screen, (0, 0, 0), (cx, cy - r), (cx, cy + r), 2)

    def update(self, dt):
        self.age += dt
        # Gentle bobbing
        bob = math.sin(self.age * POWERUP_BOB_SPEED) * POWERUP_BOB_AMPLITUDE
        self.position.y = self.base_y + bob
        # Auto-despawn
        if self.age >= POWERUP_LIFETIME:
            self.kill()
