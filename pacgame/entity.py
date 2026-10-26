from pacgame.level import Maze, DIRECTIONS


OPPOSITE: dict[str, str] = {"N": "S", "S": "N", "E": "W", "W": "E"}


class Entity():
    """Parent class of Pac-Man and the ghosts: position, direction, speed.
    Args: none.
    Returns: none."""

    def __init__(self, maze: Maze, start: tuple[int, int],
                 speed: float) -> None:
        """Place the entity on its start cell.
        Args: maze is the current maze, start is the start cell and
        speed is in cells per second.
        Returns: none."""

        self.maze: Maze = maze
        self.start: tuple[int, int] = start
        self.speed: float = speed
        self.x, self.y = start
        self.direction: str | None = None
        self.progress: float = 0.0

    def reset(self) -> None:
        """Put the entity back on its start cell.
        Args: none.
        Returns: none."""

        self.x, self.y = self.start
        self.direction = None
        self.progress = 0.0

    def free_directions(self) -> list[str]:
        """List the directions without a wall from the current cell.
        Args: none.
        Returns: the free directions."""

        return [d for d in DIRECTIONS if self.maze.can_move(self.x, self.y, d)]

    def next_cell(self, direction: str) -> tuple[int, int]:
        """Give the neighbour cell in a direction (ex: E of (3, 2) is
        (4, 2)).
        Args: direction is N, E, S or W.
        Returns: the neighbour cell."""

        dx, dy, _ = DIRECTIONS[direction]
        return (self.x + dx, self.y + dy)

    def update(self, dt: float) -> None:
        """Move as many cells as the speed allows during dt seconds.
        Args: dt (= delta time) is the time since the last update in
        seconds.
        Returns: none."""

        self.progress += self.speed * dt
        while self.progress >= 1:
            self.progress -= 1
            self.move()

    def move(self) -> None:
        """Move according to the rule of Pac-Man or of the ghost.
        Args: none.
        Returns: none."""

        pass
