from pathlib import Path
import math
import time
import pygame
from pacgame.game import Game
from pacgame.level import Maze, CLOSED, DIRECTIONS
from pacgame.ghost import Ghost, Blinky, Pinky, Inky, Clyde
from pacgame.player import Player
from pacgame.font import Color, draw_letter, draw_text, text_width
from pacgame.cheat import cheat_text


IMAGES: Path = Path(__file__).resolve().parent.parent / "images"
BACKGROUND_IMAGE: str = "background.png"
START_IMAGE = "start.png"
BRIGHT_IMAGE: str = "background_bright.png"
CARROT_IMAGE: str = "carrotes.png"
BUGS_IMAGES: str = "bugs_{:02d}.png"
ELMER_IMAGES: str = "elmer/elmer_{:02d}.png"
TAZ_IMAGES: str = "taz/taz_{:02d}.png"
MARVIN_IMAGES: str = "marvin/marvin_{:02d}.png"
COYOTE_IMAGES: str = "coyote/coyote_{:03d}.png"
WALK_ORDER_BUGS: list[int] = [1, 3, 4, 3, 2, 1, 0]
WALK_ORDER_ELMER: list[int] = [2, 3, 4, 5, 1, 2, 3]
WALK_ORDER_TAZ: list[int] = [3, 4, 5, 4, 3, 4, 5]
WALK_ORDER_MARVIN: list[int] = [1, 0, 2, 0, 1, 0, 2]
WALK_ORDER_COYOTE: list[int] = [18, 19, 20, 21, 22, 17, 18]
STEP_TIME: float = 0.12
WIDTH: int = 1500
HEIGHT: int = 1000
HEADER: int = 100
WALL: Color = (0, 255, 159)
PACGUMS: Color = (227, 119, 25)
RED: Color = (255, 0, 0)
EYES: Color = (255, 255, 255)
PUPILS: Color = (33, 33, 222)
EDIBLE_TINT: Color = WALL
BLINK_TINT: Color = (255, 255, 255)
BLINK_TIME: float = 3.0
TEXT_SIZE: int = 4
CHEAT_SIZE: int = 3


def load_image(name: str) -> pygame.Surface:
    """Load a PNG image of the images folder.
    Args: name is the file name inside the images folder.
    Returns: the image."""

    return pygame.image.load(str(IMAGES / name))


def fill_rectangle(surface: pygame.Surface, x: int, y: int, w: int, h: int,
                   color: Color) -> None:
    """Fill a rectangle pixel by pixel (ex: the walls).
    Args: surface is the image to draw on, x and y are the top left
    corner, w is the width and h the height in pixels, color is the color
    of the rectangle.
    Returns: none."""

    for py in range(y, y + h):
        for px in range(x, x + w):
            surface.set_at((px, py), color)


def fill_ellipse(surface: pygame.Surface, cx: int, cy: int, rx: int,
                 ry: int, color: Color) -> None:
    """Fill an ellipse pixel by pixel (ex: the pacgums).
    Args: surface is the image to draw on, cx and cy the center, rx and
    ry the radius in x and y, color the fill color.
    Returns: none."""

    rx = max(rx, 1)
    ry = max(ry, 1)
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if dx * dx * ry * ry + dy * dy * rx * rx <= rx * rx * ry * ry:
                surface.set_at((cx + dx, cy + dy), color)


def copy_area(source: pygame.Surface, target: pygame.Surface, x: int,
              y: int, w: int, h: int) -> None:
    """Copy a rectangle of an image into another one, pixel by pixel
    (ex: erase an eaten pacgum with the background).
    Args: source is the image to read, target is the image to draw on,
    x and y are the top left corner, w and h the size in pixels.
    Returns: none."""

    for py in range(y, y + h):
        for px in range(x, x + w):
            target.set_at((px, py), source.get_at((px, py)))


class Sprite():
    """An image with transparent pixels, kept as the list of its visible
    pixels: only them are drawn.
    Args: none.
    Returns: none."""

    def __init__(self, width: int, height: int,
                 pixels: list[tuple[int, int, Color]]) -> None:
        """Save the size and the visible pixels.
        Args: width and height are the size in pixels, pixels are the
        visible pixels (x, y, color).
        Returns: none."""

        self.width: int = width
        self.height: int = height
        self.pixels: list[tuple[int, int, Color]] = pixels

    def draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw the visible pixels.
        Args: surface is the image to draw on, x and y the top left corner.
        Returns: none."""

        for dx, dy, color in self.pixels:
            surface.set_at((x + dx, y + dy), color)


def scale_sprite(source: pygame.Surface, width: int, height: int) -> Sprite:
    """Resize an image: each pixel takes the color of the closest pixel
    of the source, so pixel art stays sharp. Transparent pixels are
    skipped.
    Args: source is the image, width and height the new size.
    Returns: the sprite."""

    source_w, source_h = source.get_size()
    pixels: list[tuple[int, int, Color]] = []
    for y in range(height):
        for x in range(width):
            c: pygame.Color = source.get_at((x * source_w // width,
                                             y * source_h // height))
            if c.a >= 128:
                pixels.append((x, y, (c.r, c.g, c.b)))
    return Sprite(width, height, pixels)


def mirror_sprite(sprite: Sprite) -> Sprite:
    """Flip a sprite left to right.
    Args: sprite is the sprite.
    Returns: the mirrored sprite."""

    pixels: list[tuple[int, int, Color]] = [
        (sprite.width - 1 - x, y, color) for x, y, color in sprite.pixels]
    return Sprite(sprite.width, sprite.height, pixels)


def filled_image(width: int, height: int, color: Color) -> pygame.Surface:
    """Make an image of one color (ex: a piece of wall).
    Args: width and height are the size, color the color.
    Returns: the image."""

    image: pygame.Surface = pygame.Surface((width, height))
    fill_rectangle(image, 0, 0, width, height, color)
    return image


def drawing_sprite(surface: pygame.Surface) -> Sprite:
    """Turn a drawing made on a black image into a sprite: the black
    pixels become transparent.
    Args: surface is the drawing.
    Returns: the sprite."""

    width, height = surface.get_size()
    pixels: list[tuple[int, int, Color]] = []
    for y in range(height):
        for x in range(width):
            c: pygame.Color = surface.get_at((x, y))
            if (c.r, c.g, c.b) != (0, 0, 0):
                pixels.append((x, y, (c.r, c.g, c.b)))
    return Sprite(width, height, pixels)


class CellArea():
    """Draw shapes inside one cell, with positions given from 0 to 1
    (0.5 is the middle of the cell).
    Args: none.
    Returns: none."""

    def __init__(self, surface: pygame.Surface, x: int, y: int,
                 size: int) -> None:
        """Save where the drawing area is on the image.
        Args: surface is the image, x and y the top left corner of the
        drawing area, size its width and height.
        Returns: none."""

        self.surface: pygame.Surface = surface
        self.x: int = x
        self.y: int = y
        self.size: int = size

    def to_pixels(self, value: float) -> int:
        """Convert a value from 0 to 1 into pixels.
        Args: value is the position or the size from 0 to 1.
        Returns: the value in pixels."""

        return int(value * self.size)

    def ellipse(self, cx: float, cy: float, rx: float, ry: float,
                color: Color) -> None:
        """Fill an ellipse in the cell.
        Args: cx and cy the center, rx and ry the radius (0 to 1),
        color the fill color.
        Returns: none."""

        fill_ellipse(self.surface, self.x + self.to_pixels(cx),
                     self.y + self.to_pixels(cy),
                     self.to_pixels(rx), self.to_pixels(ry), color)

    def rectangle(self, x: float, y: float, w: float, h: float,
                  color: Color) -> None:
        """Fill a rectangle in the cell.
        Args: x and y the top left corner, w and h the size (0 to 1),
        color the fill color.
        Returns: none."""

        fill_rectangle(self.surface, self.x + self.to_pixels(x),
                       self.y + self.to_pixels(y),
                       max(self.to_pixels(w), 1),
                       max(self.to_pixels(h), 1), color)


def draw_pacgum(area: CellArea) -> None:
    """Small pacgum.
    Args: area is the drawing area of the cell.
    Returns: none."""

    area.ellipse(0.5, 0.5, 0.08, 0.08, PACGUMS)


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
                     PUPILS)


def tint_sprite(sprite: Sprite, tint: Color) -> Sprite:
    """Color a sprite with one color, keeping its light and dark parts
    (ex: an edible ghost).
    Args: sprite is the sprite, tint the color.
    Returns: the colored sprite."""

    pixels: list[tuple[int, int, Color]] = []
    for x, y, (r, g, b) in sprite.pixels:
        light: float = 0.35 + 0.65 * (0.3 * r + 0.59 * g + 0.11 * b) / 255
        pixels.append((x, y, (min(int(tint[0] * light), 255),
                              min(int(tint[1] * light), 255),
                              min(int(tint[2] * light), 255))))
    return Sprite(sprite.width, sprite.height, pixels)


class SpriteSet():
    """The walking frames of one character, resized for the maze.
    Args: none.
    Returns: none."""

    def __init__(self, path: str, walk_order: list[int],
                 looks_to: str) -> None:
        """Load the frames used by the walk.
        Args: path is the file name model (ex: "taz/taz_{:02d}.png"),
        walk_order the frames in the order of the animation, looks_to
        the side the original images look at ("E" or "W").
        Returns: none."""

        self.walk_order: list[int] = walk_order
        self.looks_to: str = looks_to
        self.source: dict[int, pygame.Surface] = {
            i: load_image(path.format(i)) for i in set(walk_order)}
        self.east: dict[int, Sprite] = {}
        self.west: dict[int, Sprite] = {}
        self.tinted: dict[tuple[str, str], dict[int, Sprite]] = {}

    def resize(self, tile: int) -> None:
        """Fit the frames in a cell (same ratio for all the frames), make
        the mirrored frames and the colored frames (edible, blinking).
        Args: tile is the size of a cell in pixels.
        Returns: none."""

        limit: int = max(int(tile * 0.9), 1)
        height: int = max(s.get_height() for s in self.source.values())
        width: int = max(s.get_width() for s in self.source.values())
        ratio: float = min(limit / height, limit / width)
        for i, s in self.source.items():
            w: int = max(int(s.get_width() * ratio), 1)
            h: int = max(int(s.get_height() * ratio), 1)
            normal: Sprite = scale_sprite(s, w, h)
            mirrored: Sprite = mirror_sprite(normal)
            if self.looks_to == "E":
                self.east[i], self.west[i] = normal, mirrored
            else:
                self.east[i], self.west[i] = mirrored, normal
        for look, tint in (("edible", EDIBLE_TINT), ("blink", BLINK_TINT)):
            for side, frames in (("E", self.east), ("W", self.west)):
                self.tinted[(look, side)] = {
                    i: tint_sprite(s, tint) for i, s in frames.items()}

    def image(self, side: str, step: int, look: str = "normal") -> Sprite:
        """Give the frame to draw.
        Args: side is "E" or "W", step the number of the animation step,
        look is "normal", "edible" or "blink".
        Returns: the frame."""

        if look == "normal":
            frames: dict[int, Sprite] = \
                self.west if side == "W" else self.east
        else:
            frames = self.tinted[(look, "W" if side == "W" else "E")]
        return frames[self.walk_order[step % len(self.walk_order)]]


class Images():
    """All the images of the game, loaded once when the game starts.
    Args: none.
    Returns: none."""

    def __init__(self) -> None:
        """Load the images.
        Args: none.
        Returns: none."""

        self.prairie: pygame.Surface = load_image(BACKGROUND_IMAGE)
        self.start: pygame.Surface = load_image(START_IMAGE)
        self.start: pygame.Surface = pygame.transform.smoothscale(
    self.start, (WIDTH, HEIGHT))
        self.bright: pygame.Surface = load_image(BRIGHT_IMAGE)
        for name, image in ((BACKGROUND_IMAGE, self.prairie),
                            (BRIGHT_IMAGE, self.bright)):
            if image.get_size() != (WIDTH, HEIGHT):
                raise pygame.error(f"{name} must be {WIDTH} x {HEIGHT} "
                                   "pixels")
        self.carrot_source: pygame.Surface = load_image(CARROT_IMAGE)
        self.carrot: Sprite = Sprite(0, 0, [])
        self.shapes: dict[str, Sprite] = {}
        self.wall_h: pygame.Surface = pygame.Surface((1, 1))
        self.wall_v: pygame.Surface = pygame.Surface((1, 1))
        self.bugs: SpriteSet = SpriteSet(BUGS_IMAGES, WALK_ORDER_BUGS, "W")
        self.ghosts: dict[type, SpriteSet] = {
            Blinky: SpriteSet(ELMER_IMAGES, WALK_ORDER_ELMER, "E"),
            Pinky: SpriteSet(TAZ_IMAGES, WALK_ORDER_TAZ, "E"),
            Inky: SpriteSet(MARVIN_IMAGES, WALK_ORDER_MARVIN, "W"),
            Clyde: SpriteSet(COYOTE_IMAGES, WALK_ORDER_COYOTE, "E")}
        self.tile: int = 0

    def resize(self, tile: int) -> None:
        """Resize the characters and the carrot and draw the shapes
        (pacgum, eyes) to the size of a cell, only when this size changes.
        Args: tile is the size of a cell in pixels.
        Returns: none."""

        if tile == self.tile:
            return
        self.tile = tile
        self.bugs.resize(tile)
        for sprite_set in self.ghosts.values():
            sprite_set.resize(tile)
        size: int = max(int(tile * 0.8), 1)
        self.carrot = scale_sprite(self.carrot_source, size, size)
        self.wall_h = filled_image(tile + 2, 2, WALL)
        self.wall_v = filled_image(2, tile + 2, WALL)
        self.shapes = {"pacgum": cell_drawing(tile, "pacgum", None)}
        for direction in ("N", "E", "S", "W", None):
            self.shapes[f"eyes-{direction}"] = cell_drawing(tile, "eyes",
                                                            direction)


def cell_drawing(tile: int, draw: str, direction: str | None) -> Sprite:
    """Draw a shape in an empty cell and turn it into a sprite.
    Args: tile is the size of a cell, draw is "pacgum" or "eyes",
    direction is where the eyes look.
    Returns: the sprite."""

    surface: pygame.Surface = pygame.Surface((tile, tile))
    area: CellArea = CellArea(surface, 2, 2, tile - 4)
    if draw == "pacgum":
        draw_pacgum(area)
    else:
        draw_eyes(area, direction)
    return drawing_sprite(surface)


class GameView():
    """Draw a game in the window: the prairie, the walls, the pacgums,
    the carrots (super-pacgums), Bugs Bunny (the player) and the ghosts.
    Args: none.
    Returns: none."""

    def __init__(self, game: Game, images: Images) -> None:
        """Prepare the view of a game.
        Args: game is the game to draw, images are the loaded images.
        Returns: none."""

        self.game: Game = game
        self.images: Images = images
        self.maze: Maze | None = None
        self.background: pygame.Surface = pygame.Surface((WIDTH, HEIGHT))
        self.board: pygame.Surface = pygame.Surface((WIDTH, HEIGHT))
        self.tile: int = 0
        self.offset_x: int = 0
        self.offset_y: int = HEADER
        self.on_board: set[tuple[int, int]] = set()
        self.header: dict[int, tuple[str, int]] = {}
        self.sides: dict[object, str] = {}

    def new_level(self) -> None:
        """Draw the prairie and the walls of a new maze on the background,
        then the pacgums and the carrots on the board.
        Args: none.
        Returns: none."""

        maze: Maze = self.game.maze
        self.maze = maze
        self.tile = min((WIDTH - 40) // maze.width,
                        (HEIGHT - HEADER - 20) // maze.height)
        self.offset_x = (WIDTH - self.tile * maze.width) // 2
        self.offset_y = HEADER + (HEIGHT - HEADER
                                  - self.tile * maze.height) // 2
        self.images.resize(self.tile)
        self.background.blit(self.images.prairie, (0, 0))
        for y in range(maze.height):
            for x in range(maze.width):
                self.draw_walls(x, y)
        self.board.blit(self.background, (0, 0))
        for x, y in maze.pacgums:
            self.images.shapes["pacgum"].draw(self.board,
                                              *self.corner(x, y))
        for x, y in maze.super_pacgums:
            self.draw_centered(self.board, self.images.carrot, x, y)
        self.on_board = maze.pacgums | maze.super_pacgums
        self.header = {}

    def draw_walls(self, x: int, y: int) -> None:
        """Draw the walls around a cell, or fill it as part of the 42, by
        putting the pieces of wall prepared for this cell size.
        Args: x and y are the cell.
        Returns: none."""

        t: int = self.tile
        px: int = self.offset_x + x * t
        py: int = self.offset_y + y * t
        walls: int = self.game.maze.grid[y][x]
        bg: pygame.Surface = self.background
        images: Images = self.images
        if walls == CLOSED:
            copy_area(images.bright, bg, px, py, t, t)
        if walls & 1:
            bg.blit(images.wall_h, (px - 1, py - 1))
        if walls & 2:
            bg.blit(images.wall_v, (px + t - 1, py - 1))
        if walls & 4:
            bg.blit(images.wall_h, (px - 1, py + t - 1))
        if walls & 8:
            bg.blit(images.wall_v, (px - 1, py - 1))

    def corner(self, x: int, y: int) -> tuple[int, int]:
        """Give the top left pixel of a cell.
        Args: x and y are the cell.
        Returns: the pixel position."""

        return (self.offset_x + x * self.tile, self.offset_y + y * self.tile)

    def draw_centered(self, surface: pygame.Surface, sprite: Sprite, x: int,
                      y: int) -> None:
        """Draw a sprite in the middle of a cell.
        Args: surface is the image to draw on, sprite the sprite, x and y
        the cell.
        Returns: none."""

        px, py = self.corner(x, y)
        sprite.draw(surface, px + (self.tile - sprite.width) // 2,
                    py + (self.tile - sprite.height) // 2)

    def update_board(self) -> None:
        """Erase the pacgums and carrots eaten since the last frame.
        Args: none.
        Returns: none."""

        maze: Maze = self.game.maze
        eaten: set[tuple[int, int]] = \
            self.on_board - maze.pacgums - maze.super_pacgums
        for x, y in eaten:
            px, py = self.corner(x, y)
            copy_area(self.background, self.board, px + 1, py + 1,
                      self.tile - 2, self.tile - 2)
        self.on_board -= eaten

    def side(self, entity: object, direction: str | None) -> str:
        """Give the side (east or west) a character looks at: the last one
        where it went, so it does not turn back when it goes up or down.
        Args: entity is the character, direction where it goes.
        Returns: "E" or "W"."""

        if direction in ("E", "W"):
            self.sides[entity] = direction
        return self.sides.get(entity, "E")

    def draw_ghost(self, surface: pygame.Surface, ghost: Ghost,
                   step: int) -> None:
        """Draw a ghost according to its state.
        Args: surface is the window, ghost is the ghost, step the number
        of the animation step.
        Returns: none."""

        if ghost.state == "eaten":
            sprite: Sprite = self.images.shapes[f"eyes-{ghost.direction}"]
            sprite.draw(surface, *self.corner(ghost.x, ghost.y))
            return
        look: str = "normal"
        if ghost.state == "edible":
            blink: bool = (ghost.timer < BLINK_TIME
                           and int(ghost.timer * 4) % 2 == 0)
            look = "blink" if blink else "edible"
        sprite = self.images.ghosts[type(ghost)].image(
            self.side(ghost, ghost.direction), step, look)
        self.draw_centered(surface, sprite, ghost.x, ghost.y)

    def header_text(self) -> str:
        """Give the text of the header: the score, lives, level and time.
        Args: none.
        Returns: the text."""

        game: Game = self.game
        level: str = f"{game.level_index + 1}/{len(game.config.levels)}"
        texts: list[str] = [f"SCORE {game.score}",
                            f"LIVES {game.player.lives}",
                            f"LEVEL {level}",
                            f"TIME {max(0, math.ceil(game.time_left))}"]
        return "    ".join(texts)

    def draw_header(self) -> None:
        """Write the header: the score, lives, level and time in big
        letters, and the cheats that are on below in red.
        Args: none.
        Returns: none."""

        self.draw_line(self.header_text(), 12, TEXT_SIZE, EYES)
        self.draw_line(cheat_text(self.game), 12 + 8 * TEXT_SIZE + 10,
                       CHEAT_SIZE, RED)

    def draw_line(self, text: str, y: int, size: int, color: Color) -> None:
        """Write a line centered on the board. Only the letters that
        changed are drawn again (ex: the time).
        Args: text is the text, y is the top of the line, size is the size
        of one letter pixel, color is the color of the text.
        Returns: none."""

        old_text, old_x = self.header.get(y, ("", 0))
        if text == old_text:
            return
        x: int = (WIDTH - text_width(text, size)) // 2
        step: int = 6 * size
        if len(text) == len(old_text):
            for i, letter in enumerate(text):
                if letter != old_text[i]:
                    copy_area(self.background, self.board, x + i * step, y,
                              5 * size, 7 * size)
                    draw_letter(self.board, letter, x + i * step, y,
                                size, color)
        else:
            copy_area(self.background, self.board, old_x, y,
                      max(text_width(old_text, size), 0), 7 * size)
            draw_text(self.board, text, x, y, size, color)
        self.header[y] = (text, x)

    def draw(self, window: pygame.Surface) -> None:
        """Draw the whole frame in the window.
        Args: window is the image of the window.
        Returns: none."""

        if self.game.maze is not self.maze:
            self.new_level()
        self.update_board()
        self.draw_header()
        window.blit(self.board, (0, 0))
        step: int = int(time.monotonic() / STEP_TIME)
        player: Player = self.game.player
        bugs: Sprite = self.images.bugs.image(
            self.side(player, player.direction), step)
        self.draw_centered(window, bugs, player.x, player.y)
        for ghost in self.game.ghosts:
            self.draw_ghost(window, ghost, step)
