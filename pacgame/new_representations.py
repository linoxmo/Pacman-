import pygame
from pacgame.game import Game
from pacgame.level import Maze, CLOSED, DIRECTIONS
from pacgame.ghost import Ghost, Blinky, Pinky, Inky, Clyde

FRONT_IMAGE: str = "images/prairie.png"
CHERRY_IMAGE: str = "images/fruit.png"
BUGS_IMAGES: str = "images/bugs_{:02d}.png"
BUGS_COUNT: int = 5
WALK_ORDER: list[int] = [1, 3, 4, 3, 2, 1, 0]
WIDTH: int = 1500
HEIGHT: int = 1000
HEADER: int = 60
GROUND: str = "#000000"
WALL: str = "#2121DE"
PATTERN: str = "#101050"
PACMAN: str = "#FFFF00"
PACGUMS: str = "#FFB8AE"
RED: str = "#FF0000"
EYES: str = "#FFFFFF"
SCARED_GHOST: str = "#2121DE"
BLINK_TIME: float = 3.0
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


def draw_pacgum(area: CellArea) -> None:
    """Small pacgum.
    Args: area is the drawing area of the cell.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.08, 0.08, PACGUMS)


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
    """Draw a game on a pygame surface: walls, pacgums, cherries
    (super-pacgums), Bugs Bunny (the player) and the ghosts.
    Args: none.
    Returns: none."""

    def __init__(self, game: Game) -> None:
        """Prepare the view of a game.
        Args: game is the game to draw.
        Returns: none."""

        self.game: Game = game
        self.font: pygame.font.Font = pygame.font.Font(None, 48)
        self.maze: Maze | None = None
        self.prairie_source: pygame.Surface = pygame.image.load(
            FRONT_IMAGE).convert()
        self.background: pygame.Surface | None = None
        self.tile: int = 0
        self.offset_x: int = 0
        self.offset_y: int = HEADER
        self.cherry_source: pygame.Surface = pygame.image.load(
            CHERRY_IMAGE).convert_alpha()
        self.cherry_image: pygame.Surface = self.cherry_source
        self.bugs_source: list[pygame.Surface] = [
            pygame.image.load(BUGS_IMAGES.format(i)).convert_alpha()
            for i in range(BUGS_COUNT)]
        self.bugs_right: list[pygame.Surface] = self.bugs_source
        self.bugs_left: list[pygame.Surface] = self.bugs_source

    def new_level(self) -> None:
        """Compute the layout, draw the walls once on a background and
        resize the cherry and Bugs Bunny images to the size of a cell.
        Args: none.
        Returns: none."""

        maze: Maze = self.game.maze
        self.maze = maze
        self.tile = min((WIDTH - 40) // maze.width,
                        (HEIGHT - HEADER - 20) // maze.height)
        self.offset_x = (WIDTH - self.tile * maze.width) // 2
        self.offset_y = HEADER + (HEIGHT - HEADER
                                  - self.tile * maze.height) // 2
        self.background = pygame.transform.smoothscale(
        self.prairie_source, (WIDTH, HEIGHT))
        for y in range(maze.height):
            for x in range(maze.width):
                self.draw_walls(x, y)
        size: int = max(int(self.tile * 0.8), 1)
        self.cherry_image = pygame.transform.smoothscale(
            self.cherry_source, (size, size))
        self.resize_bugs()
        shade: pygame.Surface = pygame.Surface((WIDTH, HEIGHT))
        shade.set_alpha(120)          # 0 = transparent, 255 = noir complet
        self.background.blit(shade, (0, 0))

    def resize_bugs(self) -> None:
        """Resize the Bugs Bunny frames to fit a cell (same ratio for all
        frames, pixel art kept sharp) and make the mirrored frames used
        to walk to the west.
        Args: none.
        Returns: none."""

        height: int = max(int(self.tile * 0.9), 1)
        ratio: float = height / max(s.get_height() for s in self.bugs_source)
        self.bugs_right = [
            pygame.transform.scale(
                s, (max(int(s.get_width() * ratio), 1),
                    max(int(s.get_height() * ratio), 1)))
            for s in self.bugs_source]
        self.bugs_left = [pygame.transform.flip(s, True, False)
                          for s in self.bugs_right]

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

    def draw_bugs(self, surface: pygame.Surface) -> None:
        """Draw Bugs Bunny in the cell of the player. The frame changes at
        each cell (0,1,2,3,4,3,2,1,0) so he seems to walk, and the image
        is mirrored when he goes west.
        Args: surface to draw on.
        Returns: none."""

        player = self.game.player
        index: int = WALK_ORDER[(player.x + player.y) % len(WALK_ORDER)]
        frames: list[pygame.Surface] = (
            self.bugs_right if player.direction == "W" else self.bugs_left)
        image: pygame.Surface = frames[index]
        w, h = image.get_size()
        px: int = self.offset_x + player.x * self.tile + (self.tile - w) // 2
        py: int = self.offset_y + player.y * self.tile + (self.tile - h) // 2
        surface.blit(image, (px, py))

    def draw_pacgums(self, surface: pygame.Surface) -> None:
        """Draw the small pacgums as circles and the super-pacgums as
        cherries (image centered in their cell).
        Args: surface to draw on.
        Returns: none."""

        maze: Maze = self.game.maze
        for x, y in maze.pacgums:
            draw_pacgum(self.cell_area(surface, x, y))
        w, h = self.cherry_image.get_size()
        for x, y in maze.super_pacgums:
            px: int = self.offset_x + x * self.tile + (self.tile - w) // 2
            py: int = self.offset_y + y * self.tile + (self.tile - h) // 2
            surface.blit(self.cherry_image, (px, py))

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
        self.draw_pacgums(surface)
        self.draw_bugs(surface)
        for ghost in self.game.ghosts:
            self.draw_ghost(surface, ghost)
        self.draw_header(surface)