from pymlx import Mlx
from typing import Any
from pacgame.parsing import Config
from pacgame.game import Game
from pacgame.level import LevelError
from pacgame.representation import GameView, WIDTH, HEIGHT
import time


KEY_ESC: int = 65307
KEY_P: int = 112
KEYS: dict[int, str] = {
    65362: "N", 65364: "S", 65361: "W", 65363: "E",
    119: "N", 122: "N", 115: "S", 97: "W", 113: "W", 100: "E"}
FRAME_TIME: float = 1 / 60


class App():
    """Open the window and run the game loop.
    Args: none.
    Returns: none."""

    def __init__(self, config: Config) -> None:
        """Prepare the application.
        Args: config is the game configuration.
        Returns: none."""

        self.config: Config = config
        self.mlx: Any = None
        self.win: Any = None
        self.game: Game
        self.view: GameView
        self.last: float = 0.0

    def run(self) -> None:
        """Open the window and play until it is closed.
        Args: none.
        Returns: none."""

        with Mlx() as mlx:
            self.mlx = mlx
            self.win = mlx.new_window(WIDTH, HEIGHT, "Pac-Man")
            try:
                self.game = Game(self.config)
            except LevelError as e:
                print(f"Error: {e}")
                self.win.destroy()
                return
            self.view = GameView(mlx, self.game)
            self.last = time.monotonic()
            self.win.on_key(self.on_key)
            self.win.on_close(mlx.loop_end)
            mlx.on_loop(self.on_frame)
            mlx.loop()
            self.win.destroy()

    def on_key(self, keycode: int) -> None:
        """React to a key: move, pause or quit.
        Args: keycode is the key.
        Returns: none."""

        if keycode == KEY_ESC:
            self.mlx.loop_end()
        elif keycode == KEY_P:
            self.game.toggle_pause()
        elif keycode in KEYS:
            self.game.player.turn(KEYS[keycode])

    def on_frame(self) -> None:
        """Play and draw one frame, about 60 times per second.
        Args: none.
        Returns: none."""

        try:
            now: float = time.monotonic()
            dt: float = min(now - self.last, 0.1)
            self.last = now
            self.game.update(dt)
            self.win.put_image(self.view.draw(), 0, 0)
            self.view.draw_header(self.win)
            if self.game.state in ("won", "lost"):
                print(f"Game {self.game.state}, score {self.game.score}")
                self.mlx.loop_end()
            spent: float = time.monotonic() - now
            if spent < FRAME_TIME:
                time.sleep(FRAME_TIME - spent)
        except LevelError as e:
            print(f"Error: {e}")
            self.mlx.loop_end()
