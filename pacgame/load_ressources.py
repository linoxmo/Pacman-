import sys
from pathlib import Path

class Resources():
    """Find the files of the game, from the sources or from the build.
    Args: none.
    Returns: none."""

    @staticmethod
    def root() -> Path:
        """Give the folder that contains the images.
        Args: none.
        Returns: the folder."""

        if getattr(sys, "frozen", False):
            return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def user_data() -> Path:
        """Give a folder where the game can write (highscores).
        Args: none.
        Returns: the folder, created if needed."""

        folder: Path = Path.home() / ".pacgame"
        folder.mkdir(exist_ok=True)
        return folder