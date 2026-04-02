"""Shared fixtures for the Asteroids test suite.

SDL video and audio drivers are set to 'dummy' BEFORE pygame is imported
so that every test can run in headless CI without a display server.
"""

import os
import sys

# Must be set before any pygame import
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
import pytest

# Ensure the project root is on sys.path so bare imports like
# ``from player import Player`` resolve correctly.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from asteroid import Asteroid  # noqa: E402
from asteroidfield import AsteroidField  # noqa: E402
from constants import ASTEROID_MIN_RADIUS, SCREEN_HEIGHT, SCREEN_WIDTH  # noqa: E402
from player import Player  # noqa: E402
from powerup import PowerUp  # noqa: E402
from shot import Shot  # noqa: E402

# ---------------------------------------------------------------------------
# Session-scoped pygame initialisation
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialise pygame once for the entire test session."""
    pygame.init()
    # Create a tiny display surface so draw calls don't explode
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


# ---------------------------------------------------------------------------
# Fresh sprite groups for every test (autouse)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_sprite_groups():
    """Create fresh sprite groups and wire them to class containers.

    This runs before *every* test so no sprites leak between tests.
    """
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)

    yield {
        "updatable": updatable,
        "drawable": drawable,
        "asteroids": asteroids,
        "shots": shots,
        "powerups": powerups,
    }

    # Kill every sprite so nothing persists
    updatable.empty()
    drawable.empty()
    asteroids.empty()
    shots.empty()
    powerups.empty()


# ---------------------------------------------------------------------------
# Convenience fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def player():
    """Return a Player placed at the centre of the screen."""
    return Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)


@pytest.fixture
def make_asteroid():
    """Factory fixture: ``make_asteroid(x, y, radius)``."""
    def _factory(x=400, y=300, radius=ASTEROID_MIN_RADIUS * 2):
        return Asteroid(x, y, radius)
    return _factory


@pytest.fixture
def make_shot():
    """Factory fixture: ``make_shot(x, y, dx, dy)``."""
    def _factory(x=400, y=300, dx=0, dy=-500):
        s = Shot(x, y)
        s.velocity = pygame.Vector2(dx, dy)
        return s
    return _factory
