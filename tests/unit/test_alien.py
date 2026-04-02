"""Tests for alien craft entities."""
import pygame

from alien import AlienCraft, AlienShot, AlienSpawner
from constants import ALIEN_HEALTH, ALIEN_RADIUS


class TestAlienCraftInit:
    def test_init_position_and_radius(self, player):
        alien = AlienCraft(100, 200, player)
        assert alien.position.x == 100
        assert alien.position.y == 200
        assert alien.radius == ALIEN_RADIUS

    def test_init_health(self, player):
        alien = AlienCraft(0, 0, player)
        assert alien.health == ALIEN_HEALTH


class TestAlienDamage:
    def test_takes_damage(self, player):
        alien = AlienCraft(0, 0, player)
        assert alien.take_damage() is False  # 2 -> 1
        assert alien.health == ALIEN_HEALTH - 1

    def test_dies_at_zero(self, player):
        alien = AlienCraft(0, 0, player)
        alien.take_damage()
        assert alien.take_damage() is True  # 1 -> 0


class TestAlienShot:
    def test_moves_toward_target(self, reset_sprite_groups):
        target = pygame.Vector2(200, 0)
        shot = AlienShot(0, 0, target)
        assert shot.velocity.x > 0  # aimed right

    def test_despawns_after_lifetime(self, reset_sprite_groups):
        shot = AlienShot(0, 0, pygame.Vector2(100, 0))
        for _ in range(300):  # 5 seconds at 60fps
            shot.update(1 / 60)
        assert not shot.alive()


class TestAlienSpawner:
    def test_timer_based_spawning(self, player, reset_sprite_groups):
        # Create a temporary group and set containers
        aliens_group = pygame.sprite.Group()
        AlienSpawner.containers = (reset_sprite_groups["updatable"],)
        AlienCraft.containers = (
            aliens_group,
            reset_sprite_groups["updatable"],
            reset_sprite_groups["drawable"],
        )
        spawner = AlienSpawner(aliens_group, player)
        # Fast-forward timer
        spawner._timer = 0.01
        spawner.update(0.02)
        assert len(aliens_group) == 1

    def test_max_one_active(self, player, reset_sprite_groups):
        aliens_group = pygame.sprite.Group()
        AlienSpawner.containers = (reset_sprite_groups["updatable"],)
        AlienCraft.containers = (
            aliens_group,
            reset_sprite_groups["updatable"],
            reset_sprite_groups["drawable"],
        )
        spawner = AlienSpawner(aliens_group, player)
        spawner._timer = 0.01
        spawner.update(0.02)
        assert len(aliens_group) == 1
        # Try again — should not spawn a second
        spawner._timer = 0.01
        spawner.update(0.02)
        assert len(aliens_group) == 1
