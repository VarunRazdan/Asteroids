"""Neon retro color palette and color utility functions."""

# Core colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 16, 240)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)
PURPLE = (180, 50, 255)
BLUE = (50, 100, 255)

# Game-specific colors
PLAYER_COLOR = WHITE
SHOT_COLOR_DEFAULT = WHITE
SHOT_COLOR_SPREAD = YELLOW
SHOT_COLOR_RAPID = (255, 100, 80)
ASTEROID_COLORS = [
    (180, 180, 180),
    (160, 165, 170),
    (170, 160, 155),
    (155, 170, 165),
    (175, 170, 160),
]
THRUST_FLAME_COLOR = (255, 140, 0)
THRUST_FLAME_TIP = (255, 220, 80)
SHIELD_COLOR = CYAN
EXPLOSION_COLORS = [
    (255, 255, 200),  # hot white core
    (255, 220, 80),   # bright yellow
    (255, 165, 0),    # orange
    (255, 80, 20),    # red-orange
    (200, 50, 10),    # dark red
]

# Power-up colors
POWERUP_SHIELD_COLOR = CYAN
POWERUP_SPEED_COLOR = NEON_GREEN
POWERUP_WEAPON_SPREAD_COLOR = YELLOW
POWERUP_WEAPON_RAPID_COLOR = RED
POWERUP_BOMB_COLOR = PURPLE
POWERUP_LIFE_COLOR = WHITE

# HUD colors
HUD_TEXT_COLOR = NEON_GREEN
HUD_SCORE_COLOR = WHITE
HUD_COMBO_COLOR = YELLOW
HUD_LIVES_COLOR = WHITE

# Background
STAR_COLORS = [
    (100, 100, 120),  # dim far stars
    (160, 170, 200),  # medium stars
    (220, 230, 255),  # bright near stars
]
# Alien craft
ALIEN_COLOR = (255, 16, 240)       # neon pink/magenta
ALIEN_SHOT_COLOR = (255, 60, 80)   # red-pink

# Black hole
BLACKHOLE_CENTER = (10, 0, 20)
BLACKHOLE_RING_COLORS = [
    (60, 20, 100),
    (90, 30, 150),
    (120, 50, 180),
    (80, 40, 160),
]
BLACKHOLE_ACCRETION = (140, 60, 200)

NEBULA_COLORS = [
    (40, 10, 60, 25),   # deep purple
    (10, 20, 50, 20),   # dark blue
    (50, 10, 30, 15),   # dark magenta
]


def fade_color(color, alpha):
    """Return an RGBA tuple from an RGB color and alpha (0-255)."""
    return (color[0], color[1], color[2], int(alpha))


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colors. t in [0, 1]."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )
