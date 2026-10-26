from mazegenerator import MazeGenerator
from pacgame.parsing import Level
from collections import deque as dq


DIRECTIONS: dict[str, tuple[int, int, int]] = {
    "N": (0, -1, 1), "E": (1, 0, 2), "S": (0, 1, 4), "W": (-1, 0, 8)}
CLOSED: int = 15


class LevelError(Exception):
    """Error raised when a level can't be created."""


def distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Manhattan distance between two cells: walls are not counted.
    Args: a and b are the two cells.
    Returns: the distance in cells."""

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def generate_grid(level: Level, seed: int) -> list[list[int]]:
    """Generate the maze walls with the assigned A-Maze-ing package.
    Args: level gives the maze size, seed is 0 for a random maze.
    Returns: the grid of the walls of each cell."""

    try:
        generator = MazeGenerator(size=(level.width, level.height),
                                  perfect=False, seed=seed)
        grid: list[list[int]] = generator.maze
    except Exception as e:
        raise LevelError(f"the maze generator failed ({e})") from e
    if len(grid) != level.height or \
            any(len(row) != level.width for row in grid):
        raise LevelError("the maze generator returned a wrong maze size")
    return grid


class Maze():
    """Playable maze of one level: walls, pacgums and start positions.
    Args: none.
    Returns: none."""

    def __init__(self, level: Level, seed: int) -> None:
        """Create the maze and place the pacgums.
        Args: level gives the maze size, seed is 0 for a random maze.
        Returns: none."""

        self.width: int = level.width
        self.height: int = level.height
        self.grid: list[list[int]] = generate_grid(level, seed)
        self.corners: list[tuple[int, int]] = [
            (0, 0), (self.width - 1, 0),
            (0, self.height - 1), (self.width - 1, self.height - 1)]
        self.player_start: tuple[int, int] = self.find_start()
        start_x, start_y = self.player_start
        reachable: set[tuple[int, int]] = set(self.bfs(start_x, start_y))
        self.cells: list[tuple[int, int]] = sorted(reachable)
        self.super_pacgums: set[tuple[int, int]] = {
            c for c in self.corners if c in reachable}
        self.pacgums: set[tuple[int, int]] = \
            reachable - self.super_pacgums - {self.player_start}

    def can_move(self, x: int, y: int, direction: str) -> bool:
        """Check if there is no wall in a direction from a cell.
        Args: x and y are the cell, direction is N, E, S or W.
        Returns: true if the move is possible, otherwise false."""

        dx, dy, wall = DIRECTIONS[direction]
        if not (0 <= x + dx < self.width and 0 <= y + dy < self.height):
            return False
        return not self.grid[y][x] & wall

    def find_start(self) -> tuple[int, int]:
        """Find the free cell the closest to the middle of the maze.
        Args: none.
        Returns: the start cell of the player."""

        middle: tuple[int, int] = (self.width // 2, self.height // 2)
        free: list[tuple[int, int]] = [
            (x, y) for y in range(self.height) for x in range(self.width)
            if self.grid[y][x] != CLOSED and (x, y) not in self.corners]
        if not free:
            raise LevelError("no free cell for the player")
        return min(free, key=lambda c: distance(c, middle))

    def closest_cell(self, target: tuple[int, int]) -> tuple[int, int]:
        """Find the reachable cell the closest to a target, which can be
        a wall or outside the maze.
        Args: target is the cell to reach.
        Returns: the closest reachable cell."""

        return min(self.cells, key=lambda c: distance(c, target))

    def bfs(self, start_x: int, start_y: int) -> dict[tuple[int, int], int]:
        """Find all the cells reachable from the given starting
        coordinates using BFS, with their distance through the corridors.
        Args: start_x and start_y are the starting coordinates in
        the maze grid.
        Returns: the distance of each reachable cell."""

        queue: dq[tuple[int, int]] = dq()
        visited = {(start_x, start_y): 0}

        queue.append((start_x, start_y))
        while queue:
            x, y = queue.popleft()
            for direction, (dx, dy, _) in DIRECTIONS.items():
                nx = x + dx
                ny = y + dy
                if (nx, ny) not in visited and \
                        self.can_move(x, y, direction):
                    visited[(nx, ny)] = visited[(x, y)] + 1
                    queue.append((nx, ny))
        return visited
