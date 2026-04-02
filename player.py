import math

import pygame

from circleshape import CircleShape
from colors import PLAYER_COLOR, SHIELD_COLOR, THRUST_FLAME_COLOR, THRUST_FLAME_TIP
from constants import (
    BOMB_MAX,
    LINE_WIDTH,
    PLAYER_FLASH_RATE,
    PLAYER_FRICTION,
    PLAYER_INVULNERABILITY_TIME,
    PLAYER_MAX_SPEED,
    PLAYER_RADIUS,
    PLAYER_REVERSE_THRUST_MULT,
    PLAYER_THRUST,
    PLAYER_TURN_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_DURATION,
    SPEED_BOOST_DURATION,
    SPEED_BOOST_MULTIPLIER,
    WEAPON_POWERUP_DURATION,
)
from weapons import SingleShot


class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.is_thrusting = False
        self.just_shot = False
        self.input_mgr = None  # set by PlayingScene

        # Weapon system
        self.active_weapon = SingleShot()
        self._default_weapon = SingleShot()
        self.weapon_timer = 0

        # Shield
        self.shield_active = False
        self.shield_timer = 0
        self.shield_rotation = 0

        # Speed boost
        self.speed_boost_active = False
        self.speed_boost_timer = 0

        # Bombs
        self.bombs = 0

        # Invulnerability
        self.invulnerable = False
        self.invulnerable_timer = 0
        self._flash_visible = True

        # Black hole spiral death
        self.being_sucked = False
        self._suck_target = None
        self._suck_timer = 0
        self._suck_scale = 1.0

        # Score tracking
        self.score = 0
        self.combo_multiplier = 1
        self.combo_timer = 0

    def start_spiral_death(self, target_pos):
        """Begin the black hole spiral-in animation."""
        from constants import BLACKHOLE_SPIRAL_DURATION
        self.being_sucked = True
        self._suck_target = target_pos.copy()
        self._suck_timer = BLACKHOLE_SPIRAL_DURATION
        self._suck_scale = 1.0
        self.velocity = pygame.Vector2(0, 0)

    def make_invulnerable(self):
        self.invulnerable = True
        self.invulnerable_timer = PLAYER_INVULNERABILITY_TIME

    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = SHIELD_DURATION

    def activate_speed_boost(self):
        self.speed_boost_active = True
        self.speed_boost_timer = SPEED_BOOST_DURATION

    def set_weapon(self, weapon_class):
        self.active_weapon = weapon_class()
        self.weapon_timer = WEAPON_POWERUP_DURATION

    def add_bomb(self):
        self.bombs = min(self.bombs + 1, BOMB_MAX)

    def triangle(self):
        scale = self._suck_scale if self.being_sucked else 1.0
        r = self.radius * scale
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * r / 1.5
        a = self.position + forward * r
        b = self.position - forward * r - right
        c = self.position - forward * r + right
        return [a, b, c]

    def get_triangle_points(self):
        """Return triangle vertices as pygame.Vector2 for SAT collision."""
        return self.triangle()

    def draw(self, screen):
        # Invulnerability flash
        if self.invulnerable:
            flash_cycle = self.invulnerable_timer * PLAYER_FLASH_RATE * 2
            if int(flash_cycle) % 2 == 0:
                return  # invisible this frame

        tri = self.triangle()

        # Thrust flame
        if self.is_thrusting:
            backward = pygame.Vector2(0, -1).rotate(self.rotation)
            right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 3
            rear = self.position - pygame.Vector2(0, 1).rotate(self.rotation) * self.radius
            flame_base_l = rear + right
            flame_base_r = rear - right
            # Flickering length
            flicker = 0.8 + 0.4 * math.sin(pygame.time.get_ticks() * 0.02)
            flame_tip = self.position + backward * self.radius * 1.2 * flicker
            pygame.draw.polygon(screen, THRUST_FLAME_COLOR, [flame_base_l, flame_tip, flame_base_r])
            # Inner bright flame
            inner_tip = self.position + backward * self.radius * 0.7 * flicker
            pygame.draw.polygon(screen, THRUST_FLAME_TIP, [flame_base_l, inner_tip, flame_base_r])

        # Shield ring
        if self.shield_active:
            self.shield_rotation += 2
            shield_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            center = (self.radius * 2, self.radius * 2)
            pygame.draw.circle(shield_surf, (*SHIELD_COLOR, 60), center, int(self.radius * 1.5), 2)
            # Small dots around the ring
            for i in range(6):
                angle = math.radians(self.shield_rotation + i * 60)
                dx = math.cos(angle) * self.radius * 1.5
                dy = math.sin(angle) * self.radius * 1.5
                pygame.draw.circle(shield_surf, (*SHIELD_COLOR, 150),
                                   (int(center[0] + dx), int(center[1] + dy)), 3)
            screen.blit(shield_surf,
                        (self.position.x - self.radius * 2, self.position.y - self.radius * 2))

        # Ship body
        pygame.draw.polygon(screen, PLAYER_COLOR, tri, LINE_WIDTH)

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def update(self, dt):
        # Black hole spiral death — skip all normal input
        if self.being_sucked:
            self._update_spiral(dt)
            return

        self.just_shot = False
        inp = self.input_mgr

        # Timers
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False

        if self.speed_boost_active:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False

        if self.weapon_timer > 0:
            self.weapon_timer -= dt
            if self.weapon_timer <= 0:
                self.active_weapon = self._default_weapon

        # Combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.combo_multiplier = 1

        # Input — use InputManager if available, fall back to raw keyboard
        if inp:
            rot = inp.get_rotation()
            if rot != 0:
                self.rotate(rot * dt)

            self.is_thrusting = False
            if inp.is_thrust():
                self.is_thrusting = True
                direction = pygame.Vector2(0, 1).rotate(self.rotation)
                self.velocity += direction * PLAYER_THRUST * dt
            if inp.is_reverse():
                direction = pygame.Vector2(0, 1).rotate(self.rotation)
                self.velocity -= (
                    direction * PLAYER_THRUST * PLAYER_REVERSE_THRUST_MULT * dt
                )

            if inp.is_shoot():
                self.shoot()
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.rotate(-dt)
            if keys[pygame.K_d]:
                self.rotate(dt)
            self.is_thrusting = False
            if keys[pygame.K_w]:
                self.is_thrusting = True
                direction = pygame.Vector2(0, 1).rotate(self.rotation)
                self.velocity += direction * PLAYER_THRUST * dt
            if keys[pygame.K_s]:
                direction = pygame.Vector2(0, 1).rotate(self.rotation)
                self.velocity -= (
                    direction * PLAYER_THRUST * PLAYER_REVERSE_THRUST_MULT * dt
                )
            if keys[pygame.K_SPACE]:
                self.shoot()

        # Friction
        self.velocity *= PLAYER_FRICTION

        # Speed cap
        max_speed = PLAYER_MAX_SPEED
        if self.speed_boost_active:
            max_speed *= SPEED_BOOST_MULTIPLIER
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)

        # Apply velocity
        self.position += self.velocity * dt

        # Screen wrapping
        self.wrap_position(SCREEN_WIDTH, SCREEN_HEIGHT)

    def shoot(self):
        if self.shoot_timer > 0:
            return []
        self.shoot_timer = self.active_weapon.cooldown
        self.just_shot = True
        return self.active_weapon.fire(self.position, self.rotation)

    def _update_spiral(self, dt):
        """Animate spiraling into a black hole."""
        from constants import BLACKHOLE_SPIRAL_DURATION
        self._suck_timer -= dt
        progress = 1.0 - max(0, self._suck_timer) / BLACKHOLE_SPIRAL_DURATION

        # Spiral toward target
        diff = self._suck_target - self.position
        dist = diff.length()
        if dist > 2:
            # Move closer
            self.position += diff * 2.0 * dt
            # Orbit perpendicular to the pull direction
            perp = pygame.Vector2(-diff.y, diff.x)
            if perp.length() > 0:
                perp.normalize_ip()
            orbit_speed = 300 + 600 * progress
            self.position += perp * orbit_speed * dt

        # Spin faster and shrink
        self.rotation += (400 + 1200 * progress) * dt
        self._suck_scale = max(0.05, 1.0 - progress)

        if self._suck_timer <= 0:
            self.being_sucked = False
            self._suck_scale = 1.0

    def reset_position(self):
        """Reset to center of screen for respawn."""
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.is_thrusting = False
        self.being_sucked = False
        self._suck_scale = 1.0
