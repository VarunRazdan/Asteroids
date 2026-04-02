"""Alien craft — rare enemy UFO that shoots at the player."""
import math
import random

import pygame

from circleshape import CircleShape
from colors import ALIEN_COLOR, ALIEN_SHOT_COLOR
from constants import (
    ALIEN_BOB_AMPLITUDE,
    ALIEN_BOB_SPEED,
    ALIEN_HEALTH,
    ALIEN_RADIUS,
    ALIEN_SHOOT_COOLDOWN,
    ALIEN_SHOT_RADIUS,
    ALIEN_SHOT_SPEED,
    ALIEN_SPAWN_RATE_MAX,
    ALIEN_SPAWN_RATE_MIN,
    ALIEN_SPEED,
    ASTEROID_MAX_RADIUS,
    LINE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class AlienShot(CircleShape):
    """Projectile fired by an alien craft, aimed at the player."""

    def __init__(self, x, y, target_pos):
        super().__init__(x, y, ALIEN_SHOT_RADIUS)
        direction = target_pos - pygame.Vector2(x, y)
        if direction.length() > 0:
            direction.normalize_ip()
        self.velocity = direction * ALIEN_SHOT_SPEED
        self.color = ALIEN_SHOT_COLOR
        self.age = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt
        self.age += dt
        if self.age > 4.0:
            self.kill()
        elif (self.position.x < -50 or self.position.x > SCREEN_WIDTH + 50
              or self.position.y < -50 or self.position.y > SCREEN_HEIGHT + 50):
            self.kill()


class AlienCraft(CircleShape):
    """Flying saucer enemy that shoots at the player."""

    def __init__(self, x, y, player_ref):
        super().__init__(x, y, ALIEN_RADIUS)
        self.player_ref = player_ref
        self.health = ALIEN_HEALTH
        self.shoot_timer = ALIEN_SHOOT_COOLDOWN
        self.age = 0
        self.base_y = y

    def take_damage(self):
        """Reduce health by 1. Returns True if destroyed."""
        self.health -= 1
        return self.health <= 0

    def draw(self, screen):
        cx, cy = int(self.position.x), int(self.position.y)
        r = int(self.radius)

        # UFO body — ellipse
        body_rect = pygame.Rect(cx - r, cy - r // 3, r * 2, r * 2 // 3)
        pygame.draw.ellipse(screen, ALIEN_COLOR, body_rect, LINE_WIDTH)

        # Dome on top
        dome_rect = pygame.Rect(cx - r // 2, cy - r, r, r * 2 // 3)
        pygame.draw.arc(screen, ALIEN_COLOR, dome_rect, 0, math.pi, LINE_WIDTH)

        # Horizontal line across middle
        pygame.draw.line(
            screen, ALIEN_COLOR,
            (cx - r - 4, cy), (cx + r + 4, cy), LINE_WIDTH,
        )

        # Small lights blinking
        blink = int(self.age * 6) % 2 == 0
        if blink:
            for angle in (-40, 0, 40):
                lx = cx + int(r * 0.7 * math.cos(math.radians(angle)))
                ly = cy + int(r * 0.3 * math.sin(math.radians(angle))) + 2
                pygame.draw.circle(screen, (255, 255, 100), (lx, ly), 2)

    def update(self, dt):
        self.age += dt

        # Move forward
        self.position += self.velocity * dt

        # Bobbing
        self.position.y = self.base_y + math.sin(
            self.age * ALIEN_BOB_SPEED
        ) * ALIEN_BOB_AMPLITUDE
        self.base_y += self.velocity.y * dt

        # Shoot at player
        self.shoot_timer -= dt
        if self.shoot_timer <= 0 and self.player_ref:
            self.shoot_timer = ALIEN_SHOOT_COOLDOWN
            self._fire()

        # Despawn when fully off-screen
        margin = 100
        if (self.position.x < -margin or self.position.x > SCREEN_WIDTH + margin
                or self.position.y < -margin
                or self.position.y > SCREEN_HEIGHT + margin):
            self.kill()

    def _fire(self):
        """Create an AlienShot aimed at the player."""
        if self.player_ref and self.player_ref.alive():
            AlienShot(
                self.position.x, self.position.y,
                self.player_ref.position.copy(),
            )


class AlienSpawner(pygame.sprite.Sprite):
    """Timer-based spawner for alien craft. Only one alien at a time."""

    edges = [
        (pygame.Vector2(1, 0),
         lambda t: pygame.Vector2(-ASTEROID_MAX_RADIUS, t * SCREEN_HEIGHT)),
        (pygame.Vector2(-1, 0),
         lambda t: pygame.Vector2(
             SCREEN_WIDTH + ASTEROID_MAX_RADIUS, t * SCREEN_HEIGHT)),
    ]

    def __init__(self, aliens_group, player_ref):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self._aliens = aliens_group
        self._player = player_ref
        self._timer = random.uniform(ALIEN_SPAWN_RATE_MIN, ALIEN_SPAWN_RATE_MAX)

    def update(self, dt):
        self._timer -= dt
        if self._timer <= 0:
            self._timer = random.uniform(
                ALIEN_SPAWN_RATE_MIN, ALIEN_SPAWN_RATE_MAX
            )
            # Only one alien at a time
            if len(self._aliens) > 0:
                return
            edge = random.choice(self.edges)
            pos = edge[1](random.uniform(0.2, 0.8))
            alien = AlienCraft(pos.x, pos.y, self._player)
            alien.velocity = edge[0] * ALIEN_SPEED
