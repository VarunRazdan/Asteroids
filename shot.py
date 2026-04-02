import pygame

from circleshape import CircleShape
from colors import SHOT_COLOR_DEFAULT
from constants import LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SHOT_LIFETIME, SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, x, y, radius=SHOT_RADIUS, color=SHOT_COLOR_DEFAULT):
        super().__init__(x, y, radius)
        self.color = color
        self.age = 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt
        self.age += dt
        # Despawn if lifetime exceeded or off-screen
        if self.age >= SHOT_LIFETIME:
            self.kill()
        elif (self.position.x < -50 or self.position.x > SCREEN_WIDTH + 50
              or self.position.y < -50 or self.position.y > SCREEN_HEIGHT + 50):
            self.kill()
