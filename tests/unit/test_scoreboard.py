"""Tests for the Scoreboard persistence and logic."""
import os

import pytest

from constants import SCOREBOARD_FILE, SCOREBOARD_MAX_ENTRIES
from scoreboard import Scoreboard


@pytest.fixture(autouse=True)
def clean_scoreboard():
    """Remove any leftover scoreboard file before/after each test."""
    if os.path.exists(SCOREBOARD_FILE):
        os.remove(SCOREBOARD_FILE)
    yield
    if os.path.exists(SCOREBOARD_FILE):
        os.remove(SCOREBOARD_FILE)


class TestScoreboardBasic:
    def test_empty_board(self):
        sb = Scoreboard()
        assert sb.get_scores() == []
        assert sb.high_score() == 0

    def test_add_and_retrieve(self):
        sb = Scoreboard()
        sb.add_score("AAA", 1000)
        scores = sb.get_scores()
        assert len(scores) == 1
        assert scores[0]["name"] == "AAA"
        assert scores[0]["score"] == 1000

    def test_sorted_descending(self):
        sb = Scoreboard()
        sb.add_score("LOW", 100)
        sb.add_score("HI", 5000)
        sb.add_score("MID", 2000)
        scores = sb.get_scores()
        assert scores[0]["score"] == 5000
        assert scores[1]["score"] == 2000
        assert scores[2]["score"] == 100

    def test_high_score(self):
        sb = Scoreboard()
        sb.add_score("AAA", 500)
        sb.add_score("BBB", 3000)
        assert sb.high_score() == 3000


class TestScoreboardLimits:
    def test_top_10_limit(self):
        sb = Scoreboard()
        for i in range(15):
            sb.add_score("TST", (i + 1) * 100)
        assert len(sb.get_scores()) == SCOREBOARD_MAX_ENTRIES

    def test_is_high_score_empty_board(self):
        sb = Scoreboard()
        assert sb.is_high_score(1) is True

    def test_is_high_score_full_board(self):
        sb = Scoreboard()
        for i in range(SCOREBOARD_MAX_ENTRIES):
            sb.add_score("TST", (i + 1) * 1000)
        # Lowest is 1000
        assert sb.is_high_score(999) is False
        assert sb.is_high_score(1001) is True

    def test_zero_score_not_high(self):
        sb = Scoreboard()
        assert sb.is_high_score(0) is False


class TestScoreboardPersistence:
    def test_persistence_to_file(self):
        sb1 = Scoreboard()
        sb1.add_score("ABC", 4200)

        # New instance should load from file
        sb2 = Scoreboard()
        assert len(sb2.get_scores()) == 1
        assert sb2.get_scores()[0]["score"] == 4200

    def test_corrupt_file_handled(self):
        with open(SCOREBOARD_FILE, "w") as f:
            f.write("not valid json {{{")

        sb = Scoreboard()
        assert sb.get_scores() == []

    def test_name_truncated_to_3(self):
        sb = Scoreboard()
        sb.add_score("ABCDEF", 100)
        assert sb.get_scores()[0]["name"] == "ABC"
