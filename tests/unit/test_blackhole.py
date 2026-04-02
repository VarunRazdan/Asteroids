"""Tests for black hole entities."""
import pygame

from blackhole import BlackHole, BlackHoleSpawner
from constants import (
    BLACKHOLE_KILL_RADIUS,
    BLACKHOLE_LIFETIME,
    BLACKHOLE_PULL_RADIUS,
    BLACKHOLE_RADIUS,
)


class TestBlackHoleInit:
    def test_init_position_and_radius(self, reset_sprite_groups):
        bh = BlackHole(300, 400)
        assert bh.position.x == 300
        assert bh.position.y == 400
        assert bh.radius == BLACKHOLE_RADIUS

    def test_init_age_zero(self, reset_sprite_groups):
        bh = BlackHole(0, 0)
        assert bh.age == 0


class TestBlackHoleGravity:
    def test_pull_moves_nearby_entity(self, reset_sprite_groups, make_asteroid):
        bh = BlackHole(400, 400)
        ast = make_asteroid(x=400, y=300)  # 100px above
        ast.velocity = pygame.Vector2(0, 0)
        killed = bh.apply_gravity(ast, 1 / 60)
        assert not killed
        assert ast.velocity.length() > 0

    def test_no_pull_beyond_range(self, reset_sprite_groups, make_asteroid):
        bh = BlackHole(400, 400)
        far = make_asteroid(x=400, y=400 - BLACKHOLE_PULL_RADIUS - 50)
        far.velocity = pygame.Vector2(0, 0)
        killed = bh.apply_gravity(far, 1 / 60)
        assert not killed
        assert far.velocity.length() == 0

    def test_kill_inside_radius(self, reset_sprite_groups, make_asteroid):
        bh = BlackHole(400, 400)
        close = make_asteroid(x=400, y=400 + BLACKHOLE_KILL_RADIUS - 1)
        killed = bh.apply_gravity(close, 1 / 60)
        assert killed


class TestBlackHoleLifetime:
    def test_expires_after_lifetime(self, reset_sprite_groups):
        bh = BlackHole(400, 400)
        for _ in range(int(BLACKHOLE_LIFETIME * 60) + 10):
            bh.update(1 / 60)
        assert not bh.alive()

    def test_alive_before_lifetime(self, reset_sprite_groups):
        bh = BlackHole(400, 400)
        bh.update(1.0)
        assert bh.alive()

    def test_fade_alpha(self, reset_sprite_groups):
        bh = BlackHole(400, 400)
        assert bh.fade_alpha == 1.0
        bh.age = BLACKHOLE_LIFETIME - 1.0  # 1 second left, within 3s fade
        assert bh.fade_alpha < 1.0
        assert bh.fade_alpha > 0.0


class TestBlackHoleSpawner:
    def test_max_one_active(self, player, reset_sprite_groups):
        bh_group = pygame.sprite.Group()
        BlackHoleSpawner.containers = (reset_sprite_groups["updatable"],)
        BlackHole.containers = (
            bh_group,
            reset_sprite_groups["updatable"],
            reset_sprite_groups["drawable"],
        )
        spawner = BlackHoleSpawner(bh_group, player)
        spawner._timer = 0.01
        spawner.update(0.02)
        assert len(bh_group) == 1
        spawner._timer = 0.01
        spawner.update(0.02)
        assert len(bh_group) == 1  # still only one
