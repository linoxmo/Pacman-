from pacgame.entity import Entity, OPPOSITE
from pacgame.level import Maze, DIRECTIONS, distance
from pacgame.player import Player


class Ghost(Entity):
    """A ghost that chases Pac-Man or runs away when it is edible.
    Args: none.
    Returns: none."""

    color: int = 0xFFFFFF

    def __init__(self, maze: Maze, corner: tuple[int, int], speed: float,
                 player: Player, edible_time: float,
                 respawn_time: float) -> None:
        """Place the ghost in its corner.
        Args: maze is the current maze, corner is the start cell, speed is
        in cells per second, player is Pac-Man, edible_time and
        respawn_time are in seconds.
        Returns: none."""

        super().__init__(maze, corner, speed)
        self.player: Player = player
        self.edible_time: float = edible_time
        self.respawn_time: float = respawn_time
        self.state: str = "chase"
        self.timer: float = 0.0

    def reset(self) -> None:
        """Put the ghost back in its corner, chasing.
        Args: none.
        Returns: none."""

        super().reset()
        self.state = "chase"
        self.timer = 0.0

    def make_edible(self) -> None:
        """Make the ghost edible for a while (ie: super-pacgum eaten).
        Args: none.
        Returns: none."""

        if self.state != "eaten":
            self.state = "edible"
            self.timer = self.edible_time

    def get_eaten(self) -> None:
        """Send the ghost back to its corner and make it wait.
        Args: none.
        Returns: none."""

        super().reset()
        self.state = "eaten"
        self.timer = self.respawn_time

    def get_target(self) -> tuple[int, int]:
        """Give the cell the ghost goes to. Blinky, Pinky, Inky and Clyde
        each write their own version.
        Args: none.
        Returns: the target cell."""

        return (self.player.x, self.player.y)

    def choose_direction(self) -> str | None:
        """Choose the free direction (except turning back) that brings the
        ghost the closest to its target through the corridors or the
        furthest from Pac-Man when it is edible.
        Args: none.
        Returns: the chosen direction."""

        options: list[str] = [d for d in self.free_directions()
                              if self.direction is None
                              or d != OPPOSITE[self.direction]]
        if not options:
            return OPPOSITE[self.direction] if self.direction else None
        if self.state == "edible":
            far: dict[tuple[int, int], int] = self.maze.bfs(self.player.x,
                                                            self.player.y)
            return max(options, key=lambda d: far.get(self.next_cell(d), 0))
        target_x, target_y = self.maze.closest_cell(self.get_target())
        near: dict[tuple[int, int], int] = self.maze.bfs(target_x, target_y)
        return min(options,
                   key=lambda d: near.get(self.next_cell(d), len(near)))

    def move(self) -> None:
        """If the ghost was eaten, stay still in the corner. Otherwise,
        choose a direction and go one cell further.
        Args: none.
        Returns: none."""

        if self.state == "eaten":
            return
        self.direction = self.choose_direction()
        if self.direction:
            self.x, self.y = self.next_cell(self.direction)

    def update(self, dt: float) -> None:
        """Count down the edible or waiting time and then move again.
        Args: dt is the time since the last update in seconds.
        Returns: none."""

        if self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.state = "chase"
        super().update(dt)


class Blinky(Ghost):
    """Red ghost: targets Pac-Man.
    Args: none.
    Returns: none."""

    color: int = 0xFF0000

    def get_target(self) -> tuple[int, int]:
        """Target Pac-Man.
        Args: none.
        Returns: the target cell."""

        return (self.player.x, self.player.y)


class Pinky(Ghost):
    """Pink ghost: targets 4 cells in front of Pac-Man.
    Args: none.
    Returns: none."""

    color: int = 0xFFB8FF

    def get_target(self) -> tuple[int, int]:
        """Target 4 cells in front of Pac-Man.
        Args: none.
        Returns: the target cell."""

        dx, dy = 0, 0
        if self.player.direction:
            dx, dy, _ = DIRECTIONS[self.player.direction]
        return (self.player.x + 4 * dx, self.player.y + 4 * dy)


class Inky(Ghost):
    """Blue ghost: catches Pac-Man between Blinky and himself.
    Args: none.
    Returns: none."""

    color: int = 0x00FFFF

    def __init__(self, maze: Maze, corner: tuple[int, int], speed: float,
                 player: Player, edible_time: float, respawn_time: float,
                 blinky: Blinky) -> None:
        """Place Inky in his corner and keep Blinky, because the target
        of Inky depends on the position of Blinky.
        Args: the same as Ghost and blinky is the red ghost.
        Returns: none."""

        super().__init__(maze, corner, speed, player, edible_time,
                         respawn_time)
        self.blinky: Blinky = blinky

    def get_target(self) -> tuple[int, int]:
        """Take the cell 2 cells in front of Pac-Man, then go as far on
        the other side of it as Blinky is: Inky and Blinky surround
        Pac-Man.
        Args: none.
        Returns: the target cell."""

        dx, dy = 0, 0
        if self.player.direction:
            dx, dy, _ = DIRECTIONS[self.player.direction]
        px: int = self.player.x + 2 * dx
        py: int = self.player.y + 2 * dy
        return (2 * px - self.blinky.x, 2 * py - self.blinky.y)


class Clyde(Ghost):
    """Orange ghost: chases Pac-Man from far, runs to his corner when
    close.
    Args: none.
    Returns: none."""

    color: int = 0xFFB852

    def get_target(self) -> tuple[int, int]:
        """Target Pac-Man if further than 8 cells and his corner otherwise.
        Args: none.
        Returns: the target cell."""

        pacman: tuple[int, int] = (self.player.x, self.player.y)
        if distance((self.x, self.y), pacman) > 8:
            return pacman
        return self.start
