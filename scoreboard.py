"""Persistent top-10 high score storage backed by a JSON file."""
import json
import os

from constants import SCOREBOARD_FILE, SCOREBOARD_MAX_ENTRIES


class Scoreboard:
    def __init__(self):
        self._scores = self._load()

    def _load(self):
        """Read scores from disk. Returns empty list if file missing/corrupt."""
        if not os.path.exists(SCOREBOARD_FILE):
            return []
        try:
            with open(SCOREBOARD_FILE) as f:
                data = json.load(f)
            # Validate structure
            if not isinstance(data, list):
                return []
            return [
                {"name": str(e.get("name", "???"))[:3], "score": int(e.get("score", 0))}
                for e in data[:SCOREBOARD_MAX_ENTRIES]
            ]
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self):
        """Write current scores to disk."""
        try:
            with open(SCOREBOARD_FILE, "w") as f:
                json.dump(self._scores, f, indent=2)
        except OSError:
            pass

    def get_scores(self):
        """Return the top-10 list (sorted descending by score)."""
        return list(self._scores)

    def is_high_score(self, score):
        """True if the given score would make the top 10."""
        if score <= 0:
            return False
        if len(self._scores) < SCOREBOARD_MAX_ENTRIES:
            return True
        return score > self._scores[-1]["score"]

    def add_score(self, name, score):
        """Insert a score, re-sort, keep top 10, and save to disk."""
        self._scores.append({"name": name[:3].upper(), "score": score})
        self._scores.sort(key=lambda e: e["score"], reverse=True)
        self._scores = self._scores[:SCOREBOARD_MAX_ENTRIES]
        self._save()

    def high_score(self):
        """Return the highest score, or 0 if no scores."""
        if self._scores:
            return self._scores[0]["score"]
        return 0
