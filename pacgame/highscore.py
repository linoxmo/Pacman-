from typing import Any
import json


MAX_SCORES: int = 10
MAX_NAME: int = 10


def clean_name(name: str) -> str:
    """Keep alphanumeric and spaces only, MAX_NAME characters max.
    Args: name is the name typed by the player.
    Returns: the clean name, or "PLAYER" if nothing is left."""

    name = "".join(c for c in name if c.isalnum() or c == " ")
    name = name[:MAX_NAME].strip()
    return name if name else "PLAYER"


class Highscores():
    """Top MAX_SCORES of the best scores, saved in a json file.
    Args: none.
    Returns: none."""

    def __init__(self, path: str) -> None:
        """Load the scores of the file.
        Args: path is the highscore file.
        Returns: none."""

        self.path: str = path
        self.scores: list[tuple[str, int]] = self.load()

    def load(self) -> list[tuple[str, int]]:
        """Read the file and keep only the valid scores.
        Args: none.
        Returns: the best scores, from the best to the worst."""

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data: Any = json.load(file)
        except FileNotFoundError:
            return []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            print(f"Warning: '{self.path}' can't be read, "
                  "highscores start empty")
            return []
        if not isinstance(data, list):
            print(f"Warning: '{self.path}' is not a list, "
                  "highscores start empty")
            return []
        scores: list[tuple[str, int]] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            name: Any = entry.get("name")
            score: Any = entry.get("score")
            if isinstance(name, str) and isinstance(score, int) \
                    and not isinstance(score, bool) and score >= 0:
                scores.append((clean_name(name), score))
        return self.sort(scores)

    def sort(self, scores: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """Sort the scores from the best and keep the MAX_SCORES best ones.
        Args: scores is a list of (name, score).
        Returns: the top MAX_SCORES."""

        return sorted(scores, key=lambda entry: entry[1],
                      reverse=True)[:MAX_SCORES]

    def save(self) -> None:
        """Write the scores in the file.
        Args: none.
        Returns: none."""

        data: list[dict[str, Any]] = [{"name": name, "score": score}
                                      for name, score in self.scores]
        try:
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except OSError as e:
            print(f"Warning: can't save highscores ({e.strerror})")

    def add(self, name: str, score: int) -> None:
        """Add a score, keep the top MAX_SCORES and save it.
        Args: name is the player name, score is the final score.
        Returns: none."""

        self.scores = self.sort(self.scores + [(clean_name(name),
                                                max(score, 0))])
        self.save()
