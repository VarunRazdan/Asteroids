"""VFX manager -- bridges game events to particles and screen effects."""

import random

from colors import (
    EXPLOSION_COLORS,
    THRUST_FLAME_COLOR,
    THRUST_FLAME_TIP,
    WHITE,
    YELLOW,
)
from constants import (
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    BOMB_PARTICLE_COUNT,
    DEATH_PARTICLE_COUNT,
    EXPLOSION_PARTICLE_COUNT_LARGE,
    EXPLOSION_PARTICLE_COUNT_MEDIUM,
    EXPLOSION_PARTICLE_COUNT_SMALL,
    MUZZLE_FLASH_PARTICLES,
    POWERUP_SPARKLE_COUNT,
    THRUST_PARTICLE_RATE,
)


class VFXManager:
    """Translates game events into particle emissions and screen effects.

    Args:
        particle_pool: A ParticlePool instance.
        screen_effects: An object (or dict-like) with attributes:
            shake   -- a ScreenShake instance
            flash   -- a ScreenFlash instance
            slowmo  -- a SlowMo instance
    """

    def __init__(self, particle_pool, screen_effects):
        self._particles = particle_pool
        if screen_effects is not None:
            _get = (screen_effects.get if isinstance(screen_effects, dict)
                    else lambda k, d=None: getattr(screen_effects, k, d))
            self._shake = _get("shake")
            self._flash = _get("flash")
            self._slowmo = _get("slowmo")
        else:
            self._shake = None
            self._flash = None
            self._slowmo = None

    # ------------------------------------------------------------------
    # Game event handlers
    # ------------------------------------------------------------------

    def on_asteroid_destroyed(self, pos, vel, radius):
        """Explosion when an asteroid is destroyed.

        Particle count scales with asteroid radius:
          small  -> EXPLOSION_PARTICLE_COUNT_SMALL  (15)
          medium -> EXPLOSION_PARTICLE_COUNT_MEDIUM (25)
          large  -> EXPLOSION_PARTICLE_COUNT_LARGE  (40)

        Particles inherit some of the asteroid's velocity and spread in
        all directions with an orange-to-dark-red color fade.
        """
        # Determine count based on radius thresholds
        mid = (ASTEROID_MIN_RADIUS + ASTEROID_MAX_RADIUS) / 2
        if radius <= ASTEROID_MIN_RADIUS * 1.5:
            count = EXPLOSION_PARTICLE_COUNT_SMALL
        elif radius <= mid:
            count = EXPLOSION_PARTICLE_COUNT_MEDIUM
        else:
            count = EXPLOSION_PARTICLE_COUNT_LARGE

        # Color: orange (EXPLOSION_COLORS[2]) -> dark red (EXPLOSION_COLORS[4])
        color_start = EXPLOSION_COLORS[2]   # orange
        color_end = EXPLOSION_COLORS[4]     # dark red

        # Inherit a fraction of asteroid velocity
        inherit = 0.3
        base_vx = vel[0] * inherit if vel else 0
        base_vy = vel[1] * inherit if vel else 0

        self._particles.emit(
            x=pos[0], y=pos[1],
            count=count,
            speed_range=(40, 180),
            lifetime_range=(0.3, 0.9),
            color_start=color_start,
            color_end=color_end,
            size=4,
            size_decay=0.93,
            angle_range=(0, 360),
            base_vx=base_vx,
            base_vy=base_vy,
        )

        # Shake proportional to asteroid radius (normalized to 0-1 range)
        trauma = 0.15 + 0.45 * (radius / ASTEROID_MAX_RADIUS)
        if self._shake:
            self._shake.add_trauma(trauma)

    def on_player_shoot(self, pos, rotation, weapon_type="default"):
        """Muzzle flash particles when the player fires.

        5-8 small white/yellow particles emitted in the shooting direction.
        """
        count = random.randint(5, MUZZLE_FLASH_PARTICLES + 2)

        # Shooting direction: rotation=0 is "up" in typical asteroid games
        # Convert to a narrow cone around the shoot direction
        shoot_angle = rotation  # degrees, 0 = up
        # Convert so 0 deg = right for math, adjust as needed
        # Our convention: rotation in degrees, 0 = up, clockwise positive
        # math angle: 0 = right, counter-clockwise positive
        # So math_angle = -(rotation - 90) = 90 - rotation
        center_angle = 90 - shoot_angle

        half_spread = 15  # narrow cone
        min_a = center_angle - half_spread
        max_a = center_angle + half_spread

        color_start = WHITE
        color_end = YELLOW

        self._particles.emit(
            x=pos[0], y=pos[1],
            count=count,
            speed_range=(80, 200),
            lifetime_range=(0.05, 0.15),
            color_start=color_start,
            color_end=color_end,
            size=2,
            size_decay=0.90,
            angle_range=(min_a, max_a),
        )

    def on_player_thrust(self, pos, rotation):
        """Flame particles behind the ship while thrusting.

        3-5 orange/yellow particles emitted opposite the facing direction.
        """
        count = random.randint(3, THRUST_PARTICLE_RATE)

        # Opposite of facing direction
        # facing angle in math coords: 90 - rotation
        # opposite: 90 - rotation + 180 = 270 - rotation
        center_angle = 270 - rotation
        half_spread = 25
        min_a = center_angle - half_spread
        max_a = center_angle + half_spread

        self._particles.emit(
            x=pos[0], y=pos[1],
            count=count,
            speed_range=(50, 120),
            lifetime_range=(0.1, 0.3),
            color_start=THRUST_FLAME_TIP,    # bright yellow core
            color_end=THRUST_FLAME_COLOR,     # orange edge
            size=3,
            size_decay=0.88,
            angle_range=(min_a, max_a),
        )

    def on_player_death(self, pos):
        """Dramatic explosion when the player dies.

        50+ white particles in all directions, large shake, screen flash.
        """
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=DEATH_PARTICLE_COUNT,
            speed_range=(60, 300),
            lifetime_range=(0.4, 1.2),
            color_start=EXPLOSION_COLORS[0],  # hot white
            color_end=EXPLOSION_COLORS[3],    # red-orange
            size=5,
            size_decay=0.92,
            angle_range=(0, 360),
        )

        if self._shake:
            self._shake.add_trauma(0.9)
        if self._flash:
            self._flash.trigger()

    def on_bomb_detonated(self, pos):
        """Massive explosion for bomb detonation.

        100 particles, massive shake, flash, slow-mo.
        """
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=BOMB_PARTICLE_COUNT,
            speed_range=(80, 400),
            lifetime_range=(0.5, 1.5),
            color_start=EXPLOSION_COLORS[0],  # hot white core
            color_end=EXPLOSION_COLORS[4],    # dark red
            size=6,
            size_decay=0.94,
            angle_range=(0, 360),
        )

        if self._shake:
            self._shake.add_trauma(1.0)
        if self._flash:
            self._flash.trigger()
        if self._slowmo:
            self._slowmo.trigger()

    def on_powerup_collected(self, pos, powerup_color):
        """Sparkle burst when a power-up is collected.

        20 particles in the power-up's color radiating outward.
        """
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=POWERUP_SPARKLE_COUNT,
            speed_range=(40, 160),
            lifetime_range=(0.3, 0.7),
            color_start=powerup_color,
            color_end=WHITE,
            size=3,
            size_decay=0.91,
            angle_range=(0, 360),
        )

    def on_alien_destroyed(self, pos):
        """Neon pink explosion for alien craft destruction."""
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=30,
            speed_range=(50, 200),
            lifetime_range=(0.3, 0.8),
            color_start=(255, 16, 240),   # neon pink
            color_end=(255, 100, 200),
            size=4,
            size_decay=0.92,
            angle_range=(0, 360),
        )
        if self._shake:
            self._shake.add_trauma(0.5)

    def on_alien_shoot(self, pos, direction):
        """Small red flash when alien fires."""
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=4,
            speed_range=(30, 80),
            lifetime_range=(0.1, 0.3),
            color_start=(255, 60, 80),
            size=2,
            size_decay=0.9,
            angle_range=(0, 360),
        )

    def on_blackhole_pull(self, pos):
        """Subtle purple particles spiraling near black hole (call each frame)."""
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=1,
            speed_range=(5, 20),
            lifetime_range=(0.5, 1.2),
            color_start=(140, 60, 200),
            color_end=(60, 20, 100),
            size=2,
            size_decay=0.97,
            angle_range=(0, 360),
        )

    def on_blackhole_kill(self, pos):
        """Implosion effect — particles rush inward then flash."""
        # Inward burst (negative speed simulated by small outward + short life)
        self._particles.emit(
            x=pos[0], y=pos[1],
            count=40,
            speed_range=(10, 60),
            lifetime_range=(0.2, 0.5),
            color_start=WHITE,
            color_end=(140, 60, 200),
            size=3,
            size_decay=0.85,
            angle_range=(0, 360),
        )
        if self._shake:
            self._shake.add_trauma(0.6)
        if self._flash:
            self._flash.trigger()

    # ------------------------------------------------------------------
    # Per-frame update and draw
    # ------------------------------------------------------------------

    def update(self, dt):
        """Update the particle pool (aging, movement, death)."""
        self._particles.update(dt)

    def draw(self, surface):
        """Draw all alive particles."""
        self._particles.draw(surface)
