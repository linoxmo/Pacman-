import pygame
from pacgame.game import Game
from pacgame.level import Maze, CLOSED, DIRECTIONS
from pacgame.ghost import Ghost, Blinky, Pinky, Inky, Clyde


WIDTH: int = 1500
HEIGHT: int = 1000
HEADER: int = 60
GROUND: str = "#000000"
WALL: str = "#2121DE"
PATTERN: str = "#101050"
PACGUMS: str = "#FFB8AE"
PACMAN: str = "#FFFF00"
RED: str = "#FF0000"
EYES: str = "#FFFFFF"
SCARED_GHOST: str = "#2121DE"
BLINK_TIME: float = 3.0
MOUTHS: dict[str, list[tuple[float, float]]] = {
    "E": [(0.5, 0.5), (1.0, 0.15), (1.0, 0.85)],
    "W": [(0.5, 0.5), (0.0, 0.15), (0.0, 0.85)],
    "N": [(0.5, 0.5), (0.15, 0.0), (0.85, 0.0)],
    "S": [(0.5, 0.5), (0.15, 1.0), (0.85, 1.0)]}
GHOST_COLORS: dict[type, str] = {
    Blinky: "#FF0000", Pinky: "#FFB8FF", Inky: "#00FFFF", Clyde: "#FFB852"}


class CellArea():
    """Draw shapes inside one cell, with positions from 0 to 1.
    Args: none.
    Returns: none."""

    def __init__(self, surface: pygame.Surface, x: int, y: int,
                 size: int) -> None:
        """Save where the cell is on the surface.
        Args: surface to draw on, x and y the top left corner, size the
        width and height of the area.
        Returns: none."""

        self.surface: pygame.Surface = surface
        self.x: int = x
        self.y: int = y
        self.size: int = size

    def px(self, value: float) -> int:
        """Convert a value from 0 to 1 into pixels.
        Args: value is the position or size from 0 to 1.
        Returns: the value in pixels."""

        return int(value * self.size)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float,
                color: str) -> None:
        """Fill an ellipse in the cell.
        Args: cx and cy the center, rx and ry the radius, color.
        Returns: none."""

        rect = pygame.Rect(self.x + self.px(cx - rx),
                           self.y + self.px(cy - ry),
                           max(self.px(2 * rx), 1), max(self.px(2 * ry), 1))
        pygame.draw.ellipse(self.surface, color, rect)

    def rectangle(self, x: float, y: float, w: float, h: float,
                  color: str) -> None:
        """Fill a rectangle in the cell.
        Args: x and y the top left corner, w and h the size, color.
        Returns: none."""

        rect = pygame.Rect(self.x + self.px(x), self.y + self.px(y),
                           max(self.px(w), 1), max(self.px(h), 1))
        pygame.draw.rect(self.surface, color, rect)

    def triangle(self, points: list[tuple[float, float]],
                 color: str) -> None:
        """Fill a triangle in the cell.
        Args: points the 3 corners, color.
        Returns: none."""

        corners = [(self.x + self.px(x), self.y + self.px(y))
                   for x, y in points]
        pygame.draw.polygon(self.surface, color, corners)


def draw_pacgum(area: CellArea) -> None:
    """Small pacgum.
    Args: area is the drawing area of the cell.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.08, 0.08, PACGUMS)


def draw_super_pacgum(area: CellArea) -> None:
    """Big pacgum.
    Args: area is the drawing area of the cell.
    Returns: none."""
    
    pacman.blit()
    area.ellipse(0.5, 0.5, 0.25, 0.25, PACGUMS)


def draw_pacman(area: CellArea, direction: str, mouth_open: bool) -> None:
    """Yellow circle with its mouth open in its direction.
    Args: area, direction where Pac-Man looks, mouth_open to draw the mouth.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.45, 0.45, PACMAN)
    if mouth_open:
        area.triangle(MOUTHS[direction], GROUND)


def draw_ghost_body(area: CellArea, color: str) -> None:
    """Round head, straight sides and 3 bumps at the bottom.
    Args: area, color the body color.
    Returns: none."""

    area.ellipse(0.5, 0.42, 0.42, 0.38, color)
    area.rectangle(0.08, 0.42, 0.84, 0.4, color)
    for x in (0.22, 0.5, 0.78):
        area.ellipse(x, 0.84, 0.13, 0.12, color)


def draw_eyes(area: CellArea, direction: str | None) -> None:
    """White eyes with blue pupils looking in the ghost's direction.
    Args: area, direction where it looks.
    Returns: none."""

    dx, dy = 0, 0
    if direction:
        dx, dy, _ = DIRECTIONS[direction]
    for x in (0.34, 0.66):
        area.ellipse(x, 0.4, 0.12, 0.14, EYES)
        area.ellipse(x + dx * 0.06, 0.42 + dy * 0.06, 0.06, 0.06,
                     SCARED_GHOST)


def draw_scared(area: CellArea, color: str) -> None:
    """Edible ghost: blue (or white when it blinks) with a wavy mouth.
    Args: area, color the body color.
    Returns: none."""

    draw_ghost_body(area, color)
    face: str = PACGUMS if color == SCARED_GHOST else RED
    for x in (0.36, 0.64):
        area.ellipse(x, 0.4, 0.06, 0.06, face)
    for i in range(4):
        area.rectangle(0.24 + i * 0.13, 0.62 + (i % 2) * 0.05, 0.12, 0.04,
                       face)


class GameView():
    """Draw a game on a pygame surface: walls, pacgums, Pac-Man, ghosts.
    Args: none.
    Returns: none."""

    def __init__(self, game: Game) -> None:
        """Prepare the view of a game.
        Args: game is the game to draw.
        Returns: none."""

        self.game: Game = game
        self.font: pygame.font.Font = pygame.font.Font(None, 48)
        self.maze: Maze | None = None
        self.background: pygame.Surface | None = None
        self.tile: int = 0
        self.offset_x: int = 0
        self.offset_y: int = HEADER

    def new_level(self) -> None:
        """Compute the layout and draw the walls once on a background.
        Args: none.
        Returns: none."""

        maze: Maze = self.game.maze
        self.maze = maze
        self.tile = min((WIDTH - 40) // maze.width,
                        (HEIGHT - HEADER - 20) // maze.height)
        self.offset_x = (WIDTH - self.tile * maze.width) // 2
        self.offset_y = HEADER + (HEIGHT - HEADER
                                  - self.tile * maze.height) // 2
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.fill(GROUND)
        for y in range(maze.height):
            for x in range(maze.width):
                self.draw_walls(x, y)

    def draw_walls(self, x: int, y: int) -> None:
        """Draw the walls around a cell on the background.
        Args: x and y are the cell.
        Returns: none."""

        t: int = self.tile
        px: int = self.offset_x + x * t
        py: int = self.offset_y + y * t
        walls: int = self.game.maze.grid[y][x]
        bg: pygame.Surface = self.background
        if walls == CLOSED:
            pygame.draw.rect(bg, PATTERN, (px, py, t, t))
        if walls & 1:
            pygame.draw.rect(bg, WALL, (px - 1, py - 1, t + 2, 2))
        if walls & 2:
            pygame.draw.rect(bg, WALL, (px + t - 1, py - 1, 2, t + 2))
        if walls & 4:
            pygame.draw.rect(bg, WALL, (px - 1, py + t - 1, t + 2, 2))
        if walls & 8:
            pygame.draw.rect(bg, WALL, (px - 1, py - 1, 2, t + 2))

    def cell_area(self, surface: pygame.Surface, x: int, y: int) -> CellArea:
        """Give the drawing area inside a cell, without its walls.
        Args: surface to draw on, x and y the cell.
        Returns: the drawing area."""

        return CellArea(surface, self.offset_x + x * self.tile + 2,
                        self.offset_y + y * self.tile + 2, self.tile - 4)

    def pacman_look(self) -> tuple[str, bool]:
        """Give Pac-Man's direction and whether its mouth is open
        (open on one cell out of two).
        Args: none.
        Returns: the direction and the mouth state."""

        player = self.game.player
        return (player.direction or "E", (player.x + player.y) % 2 == 0)

    def draw_ghost(self, surface: pygame.Surface, ghost: Ghost) -> None:
        """Draw a ghost according to its state.
        Args: surface to draw on, ghost is the ghost.
        Returns: none."""

        area: CellArea = self.cell_area(surface, ghost.x, ghost.y)
        if ghost.state == "eaten":
            draw_eyes(area, ghost.direction)
        elif ghost.state == "edible":
            blink: bool = (ghost.timer < BLINK_TIME
                           and int(ghost.timer * 4) % 2 == 0)
            draw_scared(area, EYES if blink else SCARED_GHOST)
        else:
            draw_ghost_body(area, GHOST_COLORS[type(ghost)])
            draw_eyes(area, ghost.direction)

    def draw_header(self, surface: pygame.Surface) -> None:
        """Write the score, lives, level and time (or the pause message),
        centered at the top.
        Args: surface to draw on.
        Returns: none."""

        game: Game = self.game
        if game.state == "paused":
            text, color = "PAUSE - PRESS P TO RESUME", PACMAN
        else:
            level: str = f"{game.level_index + 1}/{len(game.config.levels)}"
            text = "    ".join([f"SCORE {game.score}",
                                f"LIVES {game.player.lives}",
                                f"LEVEL {level}",
                                f"TIME {max(0, int(game.time_left))}"])
            color = EYES
        label: pygame.Surface = self.font.render(text, True, color)
        surface.blit(label, label.get_rect(center=(WIDTH // 2, HEADER // 2)))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the whole frame.
        Args: surface is the window surface.
        Returns: none."""

        if self.game.maze is not self.maze:
            self.new_level()
        surface.blit(self.background, (0, 0))
        maze: Maze = self.game.maze
        for x, y in maze.pacgums:
            draw_pacgum(self.cell_area(surface, x, y))
        for x, y in maze.super_pacgums:
            draw_super_pacgum(self.cell_area(surface, x, y))
        player = self.game.player
        direction, mouth = self.pacman_look()
        draw_pacman(self.cell_area(surface, player.x, player.y),
                    direction, mouth)
        for ghost in self.game.ghosts:
            self.draw_ghost(surface, ghost)
        self.draw_header(surface)