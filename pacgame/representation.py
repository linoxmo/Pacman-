from typing import Any
from pacgame.game import Game
from pacgame.level import Maze, CLOSED, DIRECTIONS
from pacgame.ghost import Ghost, Blinky, Pinky, Inky, Clyde
from pacgame.font import draw_letter, draw_text, text_width


WIDTH: int = 1500
HEIGHT: int = 1000
HEADER: int = 60
GROUND: int = 0x000000
WALL: int = 0x2121DE
PATTERN: int = 0x101050
PACGUMS: int = 0xFFB8AE
PACMAN: int = 0xFFFF00
MOUTHS: dict[str, list[tuple[float, float]]] = {
    "E": [(0.5, 0.5), (1.0, 0.15), (1.0, 0.85)],
    "W": [(0.5, 0.5), (0.0, 0.15), (0.0, 0.85)],
    "N": [(0.5, 0.5), (0.15, 0.0), (0.85, 0.0)],
    "S": [(0.5, 0.5), (0.15, 1.0), (0.85, 1.0)]}
GHOST_COLORS: dict[type, int] = {
    Blinky: 0xFF0000, Pinky: 0xFFB8FF, Inky: 0x00FFFF, Clyde: 0xFFB852}
EYES: int = 0xFFFFFF
SCARED_GHOST: int = 0x2121DE
BLINK_TIME: float = 3.0
TEXT_SIZE: int = 4


def fill_rectangle(img: Any, x: int, y: int, w: int, h: int,
                   color: int) -> None:
    """Fill a rectangle on the image (ex: walls and when something disappear).
    Args: img is the image to draw on, x and y are the pixel position
    of the top left corner, w is the width and h the height in pixels,
    color is the color of the rectangle.
    Returns: none."""

    for py in range(y, y + h):
        for px in range(x, x + w):
            img.pixel_put(px, py, color)


def fill_ellipse(img: Any, cx: int, cy: int, rx: int, ry: int,
                 color: int) -> None:
    """Fill an ellipse on the image (ex: Pac-Man and pacgums).
    Args: img is the image to draw on, cx and cy the center, rx and ry
    the radius in x and y, color the fill color.
    Returns: none."""

    rx = max(rx, 1)
    ry = max(ry, 1)
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if dx * dx * ry * ry + dy * dy * rx * rx <= rx * rx * ry * ry:
                img.pixel_put(cx + dx, cy + dy, color)


def fill_triangle(img: Any, points: list[tuple[int, int]],
                  color: int) -> None:
    """Fill a triangle on the image (ie: PacMan's mouth). A pixel is inside
    when it is on the same side of the 3 edges.
    Args: img is the image, points the 3 corners, color the fill color.
    Returns: none."""

    (ax, ay), (bx, by), (cx, cy) = points

    def side(x0: int, y0: int, x1: int, y1: int, x: int, y: int) -> int:
        """Tell on which side of the edge (x0, y0) -> (x1, y1) a pixel is.
        Args: x0, y0, x1 and y1 the edge, x and y the pixel.
        Returns: positive on one side, negative on the other, 0 on it."""

        return (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)

    for y in range(min(ay, by, cy), max(ay, by, cy) + 1):
        for x in range(min(ax, bx, cx), max(ax, bx, cx) + 1):
            s1: int = side(ax, ay, bx, by, x, y)
            s2: int = side(bx, by, cx, cy, x, y)
            s3: int = side(cx, cy, ax, ay, x, y)
            if (s1 >= 0 and s2 >= 0 and s3 >= 0) or \
                    (s1 <= 0 and s2 <= 0 and s3 <= 0):
                img.pixel_put(x, y, color)


class CellArea():
    """Draw shapes inside one cell, with positions given from 0 to 1
    (0.5 is the middle of the cell).
    Args: none.
    Returns: none."""

    def __init__(self, img: Any, x: int, y: int, size: int) -> None:
        """Save where the cell is on the image.
        Args: img is the image, x and y the top left corner of the
        drawing area, size its width and height.
        Returns: none."""

        self.img: Any = img
        self.x: int = x
        self.y: int = y
        self.size: int = size

    def to_pixels(self, value: float) -> int:
        """Convert a value from 0 to 1 into pixels.
        Args: value is the position or the size from 0 to 1.
        Returns: the value in pixels."""

        return int(value * self.size)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float,
                color: int) -> None:
        """Fill an ellipse in the cell.
        Args: cx and cy the center, rx and ry the radius (0 to 1),
        color the fill color.
        Returns: none."""

        fill_ellipse(self.img, self.x + self.to_pixels(cx),
                     self.y + self.to_pixels(cy),
                     self.to_pixels(rx), self.to_pixels(ry), color)

    def rectangle(self, x: float, y: float, w: float, h: float,
                  color: int) -> None:
        """Fill a rectangle in the cell.
        Args: x and y the top left corner, w and h the size (0 to 1),
        color the fill color.
        Returns: none."""

        fill_rectangle(self.img, self.x + self.to_pixels(x),
                       self.y + self.to_pixels(y),
                       max(self.to_pixels(w), 1),
                       max(self.to_pixels(h), 1), color)

    def triangle(self, points: list[tuple[float, float]],
                 color: int) -> None:
        """Fill a triangle in the cell.
        Args: points are the 3 corners (0 to 1), color the fill color.
        Returns: none."""

        corners: list[tuple[int, int]] = [
            (self.x + self.to_pixels(x), self.y + self.to_pixels(y))
            for x, y in points]
        fill_triangle(self.img, corners, color)


def draw_pacgum(area: CellArea) -> None:
    """Small pacgum.
    Args: area is the drawing area of the cell.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.08, 0.08, PACGUMS)


def draw_super_pacgum(area: CellArea) -> None:
    """Big pacgum (super-pacgum).
    Args: area is the drawing area of the cell.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.25, 0.25, PACGUMS)


def draw_pacman(area: CellArea, direction: str, mouth_open: bool) -> None:
    """Yellow circle with its mouth open in the direction it goes.
    Args: area is the drawing area of the cell, direction where Pac-Man
    looks, mouth_open true to draw the mouth.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.45, 0.45, PACMAN)
    if mouth_open:
        area.triangle(MOUTHS[direction], GROUND)


def draw_ghost_body(area: CellArea, color: int) -> None:
    """Round head, straight sides and 3 bumps at the bottom.
    Args: area is the drawing area of the cell, color the body color.
    Returns: none."""

    area.ellipse(0.5, 0.42, 0.42, 0.38, color)
    area.rectangle(0.08, 0.42, 0.84, 0.4, color)
    for x in (0.22, 0.5, 0.78):
        area.ellipse(x, 0.84, 0.13, 0.12, color)


def draw_eyes(area: CellArea, direction: str | None) -> None:
    """White eyes with blue pupils looking in the direction of the ghost.
    Args: area is the drawing area of the cell, direction where it looks.
    Returns: none."""

    dx, dy = 0, 0
    if direction:
        dx, dy, _ = DIRECTIONS[direction]
    for x in (0.34, 0.66):
        area.ellipse(x, 0.4, 0.12, 0.14, EYES)
        area.ellipse(x + dx * 0.06, 0.42 + dy * 0.06, 0.06, 0.06,
                     SCARED_GHOST)


def draw_scared(area: CellArea, color: int) -> None:
    """Edible ghost: blue (or white when it blinks) with a wavy mouth.
    Args: area is the drawing area of the cell, color the body color.
    Returns: none."""

    draw_ghost_body(area, color)
    face: int = PACGUMS if color == SCARED_GHOST else 0xFF0000
    for x in (0.36, 0.64):
        area.ellipse(x, 0.4, 0.06, 0.06, face)
    for i in range(4):
        area.rectangle(0.24 + i * 0.13, 0.62 + (i % 2) * 0.05, 0.12, 0.04,
                       face)


class GameView():
    """Draw a game on an image: walls, pacgums, Pac-Man and the ghosts.
    Only the cells that changed are drawn again at each frame.
    Args: none.
    Returns: none."""

    def __init__(self, mlx: Any, game: Game) -> None:
        """Prepare the view of a game.
        Args: mlx is the MiniLibX object, game is the game to draw.
        Returns: none."""

        self.mlx: Any = mlx
        self.game: Game = game
        self.img: Any = None
        self.maze: Maze | None = None
        self.tile: int = 0
        self.offset_x: int = 0
        self.offset_y: int = HEADER
        self.drawn: dict[int, tuple[int, int, str]] = {}
        self.header: tuple[str, int] = ("", 0)
        self.header_x: int = 0

    def new_level(self) -> None:
        """Draw a new maze on a new black image.
        Args: none.
        Returns: none."""

        maze: Maze = self.game.maze
        if self.img is not None:
            self.mlx.destroy_image(self.img)
        self.img = self.mlx.new_image(WIDTH, HEIGHT)
        self.maze = maze
        self.tile = min((WIDTH - 40) // maze.width,
                        (HEIGHT - HEADER - 20) // maze.height)
        self.offset_x = (WIDTH - self.tile * maze.width) // 2
        self.offset_y = HEADER + (HEIGHT - HEADER
                                  - self.tile * maze.height) // 2
        for y in range(maze.height):
            for x in range(maze.width):
                self.draw_walls(x, y)
                self.draw_cell(x, y)
        self.drawn = {}
        self.header = ("", 0)
        self.update_cells()

    def draw(self) -> Any:
        """Draw what changed since the last frame.
        Args: none.
        Returns: the image to put in the window."""

        if self.game.maze is not self.maze:
            self.new_level()
        else:
            self.update_cells()
        self.draw_header()
        return self.img

    def draw_walls(self, x: int, y: int) -> None:
        """Draw the walls around a cell or fill it as part of the 42 pattern.
        Args: x and y are the cell.
        Returns: none."""

        t: int = self.tile
        px: int = self.offset_x + x * t
        py: int = self.offset_y + y * t
        walls: int = self.game.maze.grid[y][x]
        if walls == CLOSED:
            fill_rectangle(self.img, px, py, t, t, PATTERN)
        if walls & 1:
            fill_rectangle(self.img, px - 1, py - 1, t + 2, 2, WALL)
        if walls & 2:
            fill_rectangle(self.img, px + t - 1, py - 1, 2, t + 2, WALL)
        if walls & 4:
            fill_rectangle(self.img, px - 1, py + t - 1, t + 2, 2, WALL)
        if walls & 8:
            fill_rectangle(self.img, px - 1, py - 1, 2, t + 2, WALL)

    def cell_area(self, x: int, y: int) -> CellArea:
        """Give the drawing area inside a cell, without its walls.
        Args: x and y are the cell.
        Returns: the drawing area."""

        return CellArea(self.img, self.offset_x + x * self.tile + 2,
                        self.offset_y + y * self.tile + 2, self.tile - 4)

    def draw_cell(self, x: int, y: int) -> None:
        """Clear the inside of a cell and draw its pacgum if there is one.
        Args: x and y are the cell.
        Returns: none."""

        maze: Maze = self.game.maze
        if maze.grid[y][x] == CLOSED:
            return
        t: int = self.tile
        fill_rectangle(self.img, self.offset_x + x * t + 1,
                       self.offset_y + y * t + 1, t - 2, t - 2, GROUND)
        if (x, y) in maze.pacgums:
            draw_pacgum(self.cell_area(x, y))
        elif (x, y) in maze.super_pacgums:
            draw_super_pacgum(self.cell_area(x, y))

    def pacman_look(self) -> str:
        """Give how Pac-Man must be drawn: its direction and its mouth,
        open on one cell out of two.
        Args: none.
        Returns: Pac-Man's look (ex: "E-open" for if it's looking E with
        its mouth opened)."""

        player = self.game.player
        direction: str = player.direction or "E"
        mouth: str = "open" if (player.x + player.y) % 2 == 0 else "closed"
        return f"{direction}-{mouth}"

    def ghost_look(self, ghost: Ghost) -> str:
        """Give how a ghost must be drawn.
        Args: ghost is the ghost.
        Returns: "normal-<direction>", "scared", "blink" or
        "eyes-<direction>"."""

        if ghost.state == "eaten":
            return f"eyes-{ghost.direction}"
        if ghost.state == "edible":
            if ghost.timer < BLINK_TIME and int(ghost.timer * 4) % 2 == 0:
                return "blink"
            return "scared"
        return f"normal-{ghost.direction}"

    def update_cells(self) -> None:
        """Draw again the cells where something moved or changed.
        Args: none.
        Returns: none."""

        player = self.game.player
        now: dict[int, tuple[int, int, str]] = {
            0: (player.x, player.y, self.pacman_look())}
        for i, ghost in enumerate(self.game.ghosts, start=1):
            now[i] = (ghost.x, ghost.y, self.ghost_look(ghost))

        to_redraw: set[tuple[int, int]] = set()
        for key, (x, y, look) in now.items():
            if self.drawn.get(key) != (x, y, look):
                to_redraw.add((x, y))
                if key in self.drawn:
                    to_redraw.add(self.drawn[key][:2])

        for x, y in to_redraw:
            self.draw_cell(x, y)

        if (player.x, player.y) in to_redraw:
            direction, mouth = now[0][2].split("-")
            draw_pacman(self.cell_area(player.x, player.y), direction,
                        mouth == "open")

        for i, ghost in enumerate(self.game.ghosts, start=1):
            if (ghost.x, ghost.y) in to_redraw:
                self.draw_ghost(ghost, now[i][2])
        self.drawn = now

    def draw_ghost(self, ghost: Ghost, look: str) -> None:
        """Draw a ghost with its look.
        Args: ghost is the ghost, look is how to draw it.
        Returns: none."""

        area: CellArea = self.cell_area(ghost.x, ghost.y)
        if look.startswith("eyes"):
            draw_eyes(area, ghost.direction)
        elif look == "scared":
            draw_scared(area, SCARED_GHOST)
        elif look == "blink":
            draw_scared(area, EYES)
        else:
            draw_ghost_body(area, GHOST_COLORS[type(ghost)])
            draw_eyes(area, ghost.direction)

    def header_text(self) -> tuple[str, int]:
        """Give the text of the header and its color: the score, lives,
        level and time, or the pause message.
        Args: none.
        Returns: the text and its color."""

        game: Game = self.game
        if game.state == "paused":
            return ("PAUSE - PRESS P TO RESUME", PACMAN)
        level: str = f"{game.level_index + 1}/{len(game.config.levels)}"
        texts: list[str] = [f"SCORE {game.score}",
                            f"LIVES {game.player.lives}",
                            f"LEVEL {level}",
                            f"TIME {max(0, int(game.time_left))}"]
        return ("    ".join(texts), EYES)

    def draw_header(self) -> None:
        """Write the header in big letters, centered in the window. Only
        the letters that changed are drawn again (ex: the time).
        Args: none.
        Returns: none."""

        text, color = self.header_text()
        old_text, old_color = self.header
        if (text, color) == self.header:
            return
        x: int = (WIDTH - text_width(text, TEXT_SIZE)) // 2
        y: int = (HEADER - 7 * TEXT_SIZE) // 2
        step: int = 6 * TEXT_SIZE
        if len(text) == len(old_text) and color == old_color:
            for i, letter in enumerate(text):
                if letter != old_text[i]:
                    fill_rectangle(self.img, x + i * step, y,
                                   5 * TEXT_SIZE, 7 * TEXT_SIZE, GROUND)
                    draw_letter(self.img, letter, x + i * step, y,
                                TEXT_SIZE, color)
        else:
            fill_rectangle(self.img, self.header_x, y,
                           text_width(old_text, TEXT_SIZE), 7 * TEXT_SIZE,
                           GROUND)
            draw_text(self.img, text, x, y, TEXT_SIZE, color)
        self.header = (text, color)
        self.header_x = x
