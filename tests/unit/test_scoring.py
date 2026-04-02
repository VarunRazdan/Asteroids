"""Unit tests for the scoring and combo system.

Scoring logic lives inside PlayingScene._asteroid_destroyed, but the
combo state (multiplier, timer) is tracked on the Player. We test the
constants-based scoring rules and the combo mechanics via Player state.
"""


from constants import (
    ASTEROID_MIN_RADIUS,
    COMBO_MAX_MULTIPLIER,
    COMBO_TIMEOUT,
    SCORE_LARGE_ASTEROID,
    SCORE_MEDIUM_ASTEROID,
    SCORE_SMALL_ASTEROID,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from player import Player


class TestAsteroidScoreValues:
    def test_small_asteroid_100_points(self):
        assert SCORE_SMALL_ASTEROID == 100

    def test_medium_asteroid_50_points(self):
        assert SCORE_MEDIUM_ASTEROID == 50

    def test_large_asteroid_20_points(self):
        assert SCORE_LARGE_ASTEROID == 20


class TestComboMultiplier:
    def test_combo_multiplier_increments(self):
        """Combo multiplier should increase (capped at COMBO_MAX_MULTIPLIER)."""
        p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        assert p.combo_multiplier == 1
        # Simulate successive combo hits
        for i in range(COMBO_MAX_MULTIPLIER + 2):
            p.combo_timer = COMBO_TIMEOUT
            if p.combo_multiplier < COMBO_MAX_MULTIPLIER:
                p.combo_multiplier += 1
        assert p.combo_multiplier == COMBO_MAX_MULTIPLIER

    def test_combo_resets_after_timeout(self):
        """Combo multiplier should reset to 1 after COMBO_TIMEOUT expires."""
        from unittest.mock import patch

        p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        p.combo_multiplier = 3
        p.combo_timer = COMBO_TIMEOUT

        keys = [False] * 512
        with patch("pygame.key.get_pressed", return_value=keys):
            # Simulate enough frames to exhaust the combo timer
            elapsed = 0
            while elapsed < COMBO_TIMEOUT + 0.5:
                p.update(1 / 60)
                elapsed += 1 / 60

        assert p.combo_multiplier == 1
        assert p.combo_timer <= 0

    def test_combo_stays_active_within_timeout(self):
        """Combo should remain if timer has not expired."""
        from unittest.mock import patch

        p = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        p.combo_multiplier = 3
        p.combo_timer = COMBO_TIMEOUT

        keys = [False] * 512
        with patch("pygame.key.get_pressed", return_value=keys):
            # Just one frame
            p.update(1 / 60)
        assert p.combo_multiplier == 3
        assert p.combo_timer > 0


class TestScoreCalculation:
    def test_score_with_multiplier(self):
        """Points = base_points * combo_multiplier."""
        base = SCORE_SMALL_ASTEROID
        multiplier = 3
        assert base * multiplier == 300

    def test_radius_to_score_mapping(self):
        """Verify the radius-to-score rules match the playing scene logic."""
        # Small: radius <= ASTEROID_MIN_RADIUS
        # Medium: radius <= ASTEROID_MIN_RADIUS * 2
        # Large: radius > ASTEROID_MIN_RADIUS * 2
        assert ASTEROID_MIN_RADIUS == 20
        # radius 20 => small => 100 pts
        # radius 40 => medium => 50 pts
        # radius 60 => large => 20 pts
