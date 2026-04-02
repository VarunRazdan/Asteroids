"""All game configuration constants. Never inline magic numbers — put them here."""

# Screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Player
PLAYER_RADIUS = 20
LINE_WIDTH = 2
PLAYER_TURN_SPEED = 300          # degrees/sec
PLAYER_THRUST = 500              # acceleration pixels/sec²
PLAYER_FRICTION = 0.98           # velocity multiplier per frame (1.0 = no friction)
PLAYER_MAX_SPEED = 350           # pixels/sec cap
PLAYER_REVERSE_THRUST_MULT = 0.4 # reverse is weaker than forward
PLAYER_LIVES = 3
PLAYER_INVULNERABILITY_TIME = 3.0  # seconds
PLAYER_FLASH_RATE = 8            # flashes per second during invulnerability

# Legacy (kept for compatibility with existing movement code)
PLAYER_SPEED = 200

# Shots
SHOT_RADIUS = 5
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3
SHOT_LIFETIME = 3.0              # seconds before auto-despawn

# Weapons
SPREAD_SHOT_COUNT = 5
SPREAD_SHOT_ANGLE = 40           # total fan angle in degrees
SPREAD_SHOT_COOLDOWN = 0.4
RAPID_FIRE_COOLDOWN = 0.1
RAPID_FIRE_SHOT_RADIUS = 3
RAPID_FIRE_SHOT_SPEED = 600

# Asteroids
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 0.8
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
ASTEROID_SPLIT_SPEED_MULT = 1.2
ASTEROID_SPLIT_ANGLE_MIN = 20
ASTEROID_SPLIT_ANGLE_MAX = 50
ASTEROID_VERTICES_LARGE = (8, 10)   # min, max vertex count
ASTEROID_VERTICES_MEDIUM = (6, 8)
ASTEROID_VERTICES_SMALL = (5, 6)
ASTEROID_RADIUS_VARIANCE = 0.3      # ±30% from base radius
ASTEROID_MAX_ANGULAR_VELOCITY = 60  # degrees/sec

# Scoring
SCORE_SMALL_ASTEROID = 100
SCORE_MEDIUM_ASTEROID = 50
SCORE_LARGE_ASTEROID = 20
COMBO_TIMEOUT = 2.0              # seconds before combo resets
COMBO_MAX_MULTIPLIER = 5

# Power-ups
POWERUP_SPAWN_CHANCE = 0.08      # 8% chance from medium/large asteroids
POWERUP_LIFETIME = 10.0          # seconds before auto-despawn
POWERUP_BOB_SPEED = 3.0          # sine wave speed
POWERUP_BOB_AMPLITUDE = 5.0      # pixels
POWERUP_RADIUS = 15
SHIELD_DURATION = 10.0           # seconds
SPEED_BOOST_DURATION = 8.0       # seconds
SPEED_BOOST_MULTIPLIER = 1.5
WEAPON_POWERUP_DURATION = 8.0    # seconds
BOMB_MAX = 3

# Particles
PARTICLE_POOL_SIZE = 1024
EXPLOSION_PARTICLE_COUNT_SMALL = 15
EXPLOSION_PARTICLE_COUNT_MEDIUM = 25
EXPLOSION_PARTICLE_COUNT_LARGE = 40
THRUST_PARTICLE_RATE = 5         # particles per frame while thrusting
MUZZLE_FLASH_PARTICLES = 6
DEATH_PARTICLE_COUNT = 60
BOMB_PARTICLE_COUNT = 100
POWERUP_SPARKLE_COUNT = 20
PARTICLE_GRAVITY = 0             # no gravity in space

# Screen effects
SHAKE_DECAY = 3.0                # trauma decay per second
SHAKE_MAX_OFFSET = 8             # max pixels offset
SHAKE_POWER = 2                  # trauma^power = magnitude (quadratic)
FLASH_DURATION = 0.1             # seconds
FLASH_ALPHA = 180                # starting alpha
SLOWMO_SCALE = 0.3               # dt multiplier during slow-mo
SLOWMO_DURATION = 0.5            # seconds
SLOWMO_RETURN_SPEED = 3.0        # speed of returning to normal

# Background
STAR_COUNT_FAR = 80
STAR_COUNT_MEDIUM = 50
STAR_COUNT_NEAR = 25

# HUD
HUD_MARGIN = 20
HUD_FONT_SIZE = 28
HUD_FONT_SIZE_LARGE = 48
SCORE_POPUP_SPEED = 80           # pixels/sec upward
SCORE_POPUP_LIFETIME = 1.0       # seconds

# Death transition
DEATH_DELAY = 1.5                # seconds before game-over screen after final death

# Scoreboard
SCOREBOARD_FILE = "high_scores.json"
SCOREBOARD_MAX_ENTRIES = 10
GAME_VERSION = "1.0"
DEADZONE = 0.15

# Alien craft
ALIEN_RADIUS = 22
ALIEN_SPEED = 120
ALIEN_SPAWN_RATE_MIN = 15.0
ALIEN_SPAWN_RATE_MAX = 20.0
ALIEN_SHOOT_COOLDOWN = 2.0
ALIEN_SHOT_SPEED = 300
ALIEN_SHOT_RADIUS = 4
ALIEN_HEALTH = 2
ALIEN_SCORE = 500
ALIEN_POWERUP_CHANCE = 0.5
ALIEN_BOB_SPEED = 3.0
ALIEN_BOB_AMPLITUDE = 8.0

# Black holes
BLACKHOLE_RADIUS = 35
BLACKHOLE_KILL_RADIUS = 15
BLACKHOLE_PULL_RADIUS = 250
BLACKHOLE_PULL_FORCE = 15000
BLACKHOLE_LIFETIME = 18.0
BLACKHOLE_SPAWN_RATE_MIN = 25.0
BLACKHOLE_SPAWN_RATE_MAX = 35.0
BLACKHOLE_SPIRAL_DURATION = 1.5
BLACKHOLE_PARTICLE_RATE = 2
