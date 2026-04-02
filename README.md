# ASTEROIDS

```
    _    ____ _____ _____ ____   ___  ___ ____  ____
   / \  / ___|_   _| ____|  _ \ / _ \|_ _|  _ \/ ___|
  / _ \ \___ \ | | |  _| | |_) | | | || || | | \___ \
 / ___ \ ___) || | | |___|  _ <| |_| || || |_| |___) |
/_/   \_\____/ |_| |_____|_| \_\\___/|___|____/|____/
```

A classic Asteroids arcade game reimagined with retro neon aesthetics, acceleration-based physics, power-ups, procedural visuals, and chiptune audio — all built from scratch in Python with pygame.

**Created by Varun Razdan**

---

## Screenshots

<!-- Add your own screenshots to the screenshots/ directory -->
![Title Screen](screenshots/title.png)
![Gameplay](screenshots/gameplay.png)
![Game Over & Scoreboard](screenshots/gameover.png)

---

## Features & Enhancements

This game started as a basic Boot.dev Asteroids tutorial (simple circles, no score, no lives, `sys.exit()` on death) and was rebuilt into a full arcade experience. Here's everything that was added:

### Core Gameplay
- **Acceleration-based physics** with momentum, thrust, friction, and speed cap (the original had direct velocity movement)
- **Screen wrapping** for player, asteroids, and shots (originally objects flew off-screen forever)
- **Procedurally generated lumpy asteroids** — irregular polygons with 5-10 vertices and slow rotation (originally perfect circles)
- **Triangular ship hitbox** using SAT (Separating Axis Theorem) collision detection (originally a circular hitbox)
- **3 weapon types**: Single Shot, Spread Shot (5-bullet fan), and Rapid Fire

### Power-Up System (all new)
- **Shield** — absorbs one hit, rotating cyan ring visual (10s duration)
- **Speed boost** — 1.5x max speed for 8 seconds
- **Weapon upgrades** — spread shot and rapid fire pickups
- **Bombs** — press B to destroy all on-screen asteroids with a shockwave
- **Extra lives** — collect to gain an additional life (max 5)
- Power-ups drop from destroyed medium/large asteroids with 8% chance

### Scoring & Progression (all new)
- **Point system**: 100 pts (small), 50 pts (medium), 20 pts (large asteroids)
- **Combo multiplier** — consecutive kills within 2 seconds build up to 5x multiplier
- **Persistent top-10 high score board** saved to disk
- **Classic arcade 3-character name entry** — type A-Z or use arrows
- **On-screen score popups** that float up and fade

### Visual Effects (all new)
- **Particle explosions** on asteroid destruction (15-40 particles per explosion)
- **Thrust flame animation** with flickering inner/outer flame
- **Screen shake** on impacts (magnitude proportional to asteroid size)
- **Screen flash** on player death
- **CRT scanline overlay** for authentic retro feel
- **Slow-motion effect** on bomb detonation
- **Parallax starfield background** — 3 depth layers with nebula patches
- **Neon retro color palette** — cyan, green, yellow, orange, purple accents

### Audio (all new)
- **15 programmatically generated retro sound effects** — lasers, explosions (3 sizes), power-up chimes, shield sounds, bomb blast, death wail, menu blips, game-over jingle
- **Chiptune background music** — procedurally generated 4-bar loop at 140 BPM
- **8-channel audio system** with priority-based mixing

### Input (all new)
- **Keyboard controls** (WASD + Space + B)
- **Xbox/gamepad controller support** — left stick, A/X/RB/Start buttons
- **Dual input** — keyboard and controller work simultaneously

### Game States (all new)
- **Title screen** with ASCII art logo, author credit, and high score
- **Pause screen** (ESC / Start)
- **Game over screen** with death delay (explosion visible before transition)
- **Respawning** with 3-second invulnerability and flashing

### HUD (all new)
- Score display with pop animation
- Lives as small ship icons
- Combo multiplier indicator
- Active power-up timer bars
- Bomb count
- Weapon type label

---

## Controls

| Action | Keyboard | Controller |
|--------|----------|------------|
| Thrust | W | Left Stick Up / RT |
| Reverse | S | Left Stick Down |
| Rotate Left | A | Left Stick Left |
| Rotate Right | D | Left Stick Right |
| Shoot | Space | A / RB |
| Bomb | B | X |
| Pause | ESC | Start |
| Confirm / Start | Enter | A |

---

## Installation

Requires **Python 3.13+** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/VarunRazdan/Asteroids.git
cd Asteroids
uv sync
```

## Running from Source

```bash
uv run main.py
```

## Building a Standalone App (macOS)

No Python installation required for players:

```bash
# Install dev dependencies (includes PyInstaller)
uv sync --group dev

# Build the .app bundle
uv run pyinstaller --onedir --windowed --name Asteroids \
  --hidden-import=pygame._view --hidden-import=pygame.freetype \
  --hidden-import=numpy main.py

# The app is at dist/Asteroids.app — double-click to play!
```

High scores are saved to `~/.victor_asteroids/high_scores.json` so they persist across launches.

## Testing

```bash
# Install dev dependencies
uv sync --group dev

# Run all tests (headless)
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run pytest -v

# Lint
uv run ruff check .
```

---

## Tech Stack

- **Python 3.13** + **pygame 2.6.1** + **numpy**
- **uv** for dependency management
- **PyInstaller** for standalone app bundling
- **pytest** for testing (150+ tests)
- **ruff** for linting
- **GitHub Actions** for CI/CD

---

## License

MIT
