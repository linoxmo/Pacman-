from pymlx import Mlx
from typing import Any
from pacgame.parsing import Config
from pacgame.game import Game
from pacgame.level import LevelError
from pacgame.highscore import Highscores, MAX_NAME
from pacgame.representation import GameView, WIDTH, HEIGHT
from pacgame.font import draw_text, text_width
from pacgame.cheat import KEY_CHEAT, CHEATS, toggle_cheat_mode, use_cheat
import time


KEY_ESC: int = 65307
KEY_SPACE: int = 32
KEY_ENTER: tuple[int, int] = (65293, 65421)
KEY_BACKSPACE: int = 65288
KEY_QUIT: tuple[int, int] = (113, 65307)
KEY_UP: tuple[int, int] = (119, 65362)
KEY_DOWN: tuple[int, int] = (115, 65364)
KEYS: dict[int, str] = {
    65362: "N", 65364: "S", 65361: "W", 65363: "E",
    119: "N", 115: "S", 97: "W", 100: "E"}
FRAME_TIME: float = 1 / 60
TEXT: int = 0xFFFFFF
SELECTED: int = 0xFFFF00
LOST: int = 0xFF0000
WON: int = 0x00FF00
CHEAT: int = 0xFF0000
MAIN_MENU: list[str] = ["START GAME", "HIGHSCORES", "INSTRUCTIONS", "EXIT"]
PAUSE_MENU: list[str] = ["RESUME", "MAIN MENU"]


def write_centered(img: Any, text: str, y: int, size: int,
                   color: int) -> None:
    """Write a text centered in the window.
    Args: img is the image to draw on, text is the text to be written,
    y is the top of the text, size is the size of one letter pixel,
    color is the color of the text.
    Returns: none."""

    x: int = (WIDTH - text_width(text, size)) // 2
    draw_text(img, text, x, y, size, color)


class Application():
    """Open the window and go from one screen to another: main menu,
    game, pause menu, end of the game, highscores and instructions.
    Args: none.
    Returns: none."""

    def __init__(self, config: Config) -> None:
        """Prepare the application.
        Args: config is the game configuration.
        Returns: none."""

        self.config: Config = config
        self.highscores: Highscores = Highscores(config.highscore_filename)
        self.mlx: Any = None
        self.win: Any = None
        self.img: Any = None
        self.screen: str = "menu"
        self.choice: int = 0
        self.redraw: bool = True
        self.message: str = ""
        self.name: str = ""
        self.score: int = 0
        self.won: bool = False
        self.game: Game | None = None
        self.view: GameView | None = None
        self.last_image_time: float = 0.0

    def run(self) -> None:
        """Open the window and play until the player quits.
        Args: none.
        Returns: none."""

        with Mlx() as mlx:
            self.mlx = mlx
            self.win = mlx.new_window(WIDTH, HEIGHT, "Pac-Man")
            self.last_image_time = time.monotonic()
            self.win.on_key(self.on_key)
            self.win.on_close(mlx.loop_end)
            mlx.on_loop(self.on_frame)
            mlx.loop()
            self.stop_game()
            if self.img is not None:
                mlx.destroy_image(self.img)
            self.win.destroy()

    def show_screen(self, screen: str) -> None:
        """Go to another screen.
        Args: screen is "menu", "pause", "highscores", "instructions",
        "name" or "game".
        Returns: none."""

        self.screen = screen
        self.choice = 0
        self.redraw = True

    def start_game(self) -> None:
        """Start a new game on the first level.
        Args: none.
        Returns: none."""

        try:
            self.game = Game(self.config)
        except LevelError as e:
            self.message = f"ERROR: {e}"
            self.show_screen("menu")
            return
        self.message = ""
        self.view = GameView(self.mlx, self.game)
        self.show_screen("game")

    def stop_game(self) -> None:
        """Forget the current game and free its image.
        Args: none.
        Returns: none."""

        if self.view is not None:
            self.view.close()
        self.view = None
        self.game = None

    def end_game(self, game: Game) -> None:
        """Keep the final score and ask the name of the player.
        Args: game is the game that just ended.
        Returns: none."""

        self.score = game.score
        self.won = game.state == "won"
        self.name = ""
        self.stop_game()
        self.show_screen("name")

    def on_key(self, keycode: int) -> None:
        """React to a key, depending on the current screen.
        Args: keycode is the key.
        Returns: none."""

        if self.screen == "name":
            self.name_key(keycode)
        elif keycode in KEY_QUIT and self.screen == "menu":
            self.mlx.loop_end()
        elif keycode in KEY_QUIT:
            self.stop_game()
            self.show_screen("menu")
        elif self.screen == "game":
            self.game_key(keycode)
        elif self.screen in ("menu", "pause"):
            self.menu_key(keycode)

    def game_key(self, keycode: int) -> None:
        """During the game: move Pac-Man, open the pause menu or use the
        cheat mode.
        Args: keycode is the key.
        Returns: none."""

        if self.game is None:
            return
        if keycode == KEY_SPACE:
            self.game.toggle_pause()
            self.show_screen("pause")
        elif keycode in KEYS:
            self.game.player.turn(KEYS[keycode])
        elif keycode == KEY_CHEAT:
            toggle_cheat_mode(self.game)
        elif keycode in CHEATS:
            use_cheat(self.game, keycode)

    def menu_key(self, keycode: int) -> None:
        """In a menu: move the selection up or down or validate it.
        Args: keycode is the key.
        Returns: none."""

        options: list[str] = MAIN_MENU if self.screen == "menu" \
            else PAUSE_MENU
        if keycode in KEY_UP:
            self.choice = (self.choice - 1) % len(options)
            self.redraw = True
        elif keycode in KEY_DOWN:
            self.choice = (self.choice + 1) % len(options)
            self.redraw = True
        elif keycode in KEY_ENTER:
            self.select(options[self.choice])
        elif keycode == KEY_SPACE and self.screen == "pause":
            self.select("RESUME")

    def select(self, option: str) -> None:
        """Do what the chosen option of a menu says.
        Args: option is the chosen option.
        Returns: none."""

        if option == "START GAME":
            self.start_game()
        elif option in ("HIGHSCORES", "INSTRUCTIONS"):
            self.show_screen(option.lower())
        elif option == "EXIT":
            self.mlx.loop_end()
        elif option == "RESUME" and self.game is not None:
            self.game.toggle_pause()
            self.show_screen("game")
        elif option == "MAIN MENU":
            self.stop_game()
            self.show_screen("menu")

    def name_key(self, keycode: int) -> None:
        """Type the name of the player, then save the score with Enter.
        Args: keycode is the key.
        Returns: none."""

        if keycode in KEY_ENTER:
            self.highscores.add(self.name, self.score)
            self.show_screen("menu")
        elif keycode == KEY_ESC:
            self.show_screen("menu")
        elif keycode == KEY_BACKSPACE:
            self.name = self.name[:-1]
            self.redraw = True
        elif keycode < 128 and len(self.name) < MAX_NAME:
            letter: str = chr(keycode)
            if letter.isalnum() or letter == " ":
                self.name += letter.upper()
                self.redraw = True

    def on_frame(self) -> None:
        """Play and draw one frame, about 60 times per second.
        Args: none.
        Returns: none."""

        now: float = time.monotonic()
        dt: float = min(now - self.last_image_time, 0.1)
        self.last_image_time = now
        try:
            if self.screen == "game" and self.game is not None \
                    and self.view is not None:
                self.game.update(dt)
                self.win.put_image(self.view.draw(), 0, 0)
                if self.game.state in ("won", "lost"):
                    self.end_game(self.game)
            else:
                if self.redraw:
                    self.draw_screen()
                self.win.put_image(self.img, 0, 0)
        except LevelError as e:
            self.stop_game()
            self.message = f"ERROR: {e}"
            self.show_screen("menu")
        spent: float = time.monotonic() - now
        if spent < FRAME_TIME:
            time.sleep(FRAME_TIME - spent)

    def draw_screen(self) -> None:
        """Draw the current screen on a new black image.
        Args: none.
        Returns: none."""

        if self.img is not None:
            self.mlx.destroy_image(self.img)
        self.img = self.mlx.new_image(WIDTH, HEIGHT)
        if self.screen == "menu":
            write_centered(self.img, "PAC-MAN", 150, 14, SELECTED)
            self.draw_options(MAIN_MENU)
            write_centered(self.img, self.message[:60], 830, 3, LOST)
        elif self.screen == "pause":
            write_centered(self.img, "PAUSE", 150, 12, SELECTED)
            self.draw_options(PAUSE_MENU)
        elif self.screen == "highscores":
            self.draw_highscores()
        elif self.screen == "instructions":
            self.draw_instructions()
        elif self.screen == "name":
            self.draw_name()
        self.redraw = False

    def draw_options(self, options: list[str]) -> None:
        """Write the options of a menu, the selected one appears yellow.
        Args: options are the options / categories of the menu.
        Returns: none."""

        for i, option in enumerate(options):
            color: int = SELECTED if i == self.choice else TEXT
            write_centered(self.img, option, 420 + i * 90, 6, color)
        write_centered(self.img, "ARROWS: CHOOSE    ENTER: VALIDATE    "
                       "Q OR ESC: QUIT", 920, 3, TEXT)

    def draw_highscores(self) -> None:
        """Write the top 10 (at max) with the names and the scores.
        Args: none.
        Returns: none."""

        write_centered(self.img, "HIGHSCORES", 80, 9, SELECTED)
        if not self.highscores.scores:
            write_centered(self.img, "NO SCORE YET", 450, 5, TEXT)
        for i, (name, score) in enumerate(self.highscores.scores):
            line: str = f"{i + 1:>2}. {name:<10} {score:>7}"
            write_centered(self.img, line, 230 + i * 62, 5, TEXT)
        write_centered(self.img, "Q OR ESC: BACK TO MENU", 920, 3, TEXT)

    def draw_instructions(self) -> None:
        """Write the controls and the rules of the game.
        Args: none.
        Returns: none."""

        conf: Config = self.config
        lines: list[str] = [
            "ARROWS OR WASD: MOVE PAC-MAN",
            "SPACE: PAUSE    Q OR ESC: MENU, AGAIN: QUIT",
            "",
            "EAT ALL THE PACGUMS TO FINISH A LEVEL",
            "BIG PACGUMS MAKE THE GHOSTS BLUE",
            "EAT THE BLUE GHOSTS FOR BONUS POINTS",
            "A GHOST OR THE END OF THE TIME: -1 LIFE",
            f"FINISH THE {len(conf.levels)} LEVELS TO WIN",
            "",
            f"PACGUM {conf.points_per_pacgum}    "
            f"BIG PACGUM {conf.points_per_super_pacgum}    "
            f"GHOST {conf.points_per_ghost}"]
        cheats: list[str] = [
            "CHEAT MODE: PRESS C IN GAME, THEN",
            "F1 INVINCIBLE    F2 NEXT LEVEL    F3 FREEZE GHOSTS",
            "F4 EXTRA LIFE    F5 SPEED    F6 BLUE GHOSTS    F7 TIME 10S"]
        write_centered(self.img, "INSTRUCTIONS", 60, 9, SELECTED)
        for i, line in enumerate(lines):
            write_centered(self.img, line, 190 + i * 52, 4, TEXT)
        for i, line in enumerate(cheats):
            write_centered(self.img, line, 770 + i * 36, 3, CHEAT)
        write_centered(self.img, "Q OR ESC: BACK TO MENU", 940, 3, TEXT)

    def draw_name(self) -> None:
        """Write the end of the game: the result, the final score and the
        name of the player being typed.
        Args: none.
        Returns: none."""

        if self.won:
            write_centered(self.img, "CONGRATULATIONS!", 120, 8, WON)
            write_centered(self.img, "YOU FINISHED ALL THE LEVELS", 250, 4,
                           TEXT)
        else:
            write_centered(self.img, "GAME OVER", 120, 10, LOST)
        write_centered(self.img, f"FINAL SCORE {self.score}", 360, 6, TEXT)
        write_centered(self.img, "ENTER YOUR NAME", 520, 4, TEXT)
        write_centered(self.img, self.name + "_", 600, 7, SELECTED)
        write_centered(self.img, "ENTER: SAVE    ESC: SKIP", 920, 3, TEXT)
