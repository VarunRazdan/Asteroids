import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class for all circular game objects."""

    def __init__(self, x, y, radius):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        pass

    def update(self, dt):
        pass

    def collides_with(self, other):
        distance = self.position.distance_to(other.position)
        return distance < self.radius + other.radius

    def wrap_position(self, screen_w, screen_h):
        """Wrap position around screen edges."""
        if self.position.x < -self.radius:
            self.position.x = screen_w + self.radius
        elif self.position.x > screen_w + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = screen_h + self.radius
        elif self.position.y > screen_h + self.radius:
            self.position.y = -self.radius
