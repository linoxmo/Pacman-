from pacgame.entity import Entity
from pacgame.level import Maze


class Player(Entity):
    """Pac-Man, moved with the arrow keys or WASD.
    Args: none.
    Returns: none."""

    def __init__(self, maze: Maze, speed: float, lives: int) -> None:
        """Place Pac-Man in the middle of the maze.
        Args: maze is the current maze, speed is in cells per second and
        lives is the number of lives.
        Returns: none."""

        super().__init__(maze, maze.player_start, speed)
        self.lives: int = lives
        self.wanted: str | None = None

    def reset(self) -> None:
        """Put Pac-Man back in the middle of the maze.
        Args: none.
        Returns: none."""

        super().reset()
        self.wanted = None

    def turn(self, direction: str) -> None:
        """Remember the direction asked by the player.
        Args: direction is N, E, S or W.
        Returns: none."""

        self.wanted = direction

    def move(self) -> None:
        """Take the asked direction if possible and move one cell.
        Args: none.
        Returns: none."""

        if self.wanted and self.maze.can_move(self.x, self.y, self.wanted):
            self.direction = self.wanted
        if self.direction and \
                self.maze.can_move(self.x, self.y, self.direction):
            self.x, self.y = self.next_cell(self.direction)
