import pygame
from pacgame.parsing import Config
from pacgame.game import Game
from pacgame.level import LevelError
from pacgame.highscore import Highscores, MAX_NAME
from pacgame.new_representations import GameView, WIDTH, HEIGHT
from pacgame.cheat import KEY_CHEAT, CHEATS, toggle_cheat_mode, use_cheat


class App():
    """Open the window and go from one screen to another: main menu,
    game, pause menu, end of the game, highscores and instructions.
    Args: none.
    Returns: none."""

    FPS: int = 60
    KEYS: dict[int, str] = {
        pygame.K_UP: "N", pygame.K_DOWN: "S",
        pygame.K_LEFT: "W", pygame.K_RIGHT: "E",
        pygame.K_w: "N", pygame.K_z: "N", pygame.K_s: "S",
        pygame.K_a: "W", pygame.K_q: "W", pygame.K_d: "E"}
    KEY_ENTER: tuple[int, int] = (pygame.K_RETURN, pygame.K_KP_ENTER)
    TEXT: tuple[int, int, int] = (255, 255, 255)
    SELECTED: tuple[int, int, int] = (255, 255, 0)
    LOST: tuple[int, int, int] = (255, 0, 0)
    WON: tuple[int, int, int] = (0, 255, 0)
    CHEAT: tuple[int, int, int] = (255, 0, 0)
    MAIN_MENU: list[str] = ["START GAME", "HIGHSCORES", "INSTRUCTIONS",
                            "EXIT"]
    PAUSE_MENU: list[str] = ["RESUME", "MAIN MENU"]

    def __init__(self, config: Config) -> None:
        """Prepare the application.
        Args: config is the game configuration.
        Returns: none."""

        self.config: Config = config
        self.highscores: Highscores = Highscores(config.highscore_filename)
        self.screen: pygame.Surface
        self.fonts: dict[int, pygame.font.Font] = {}
        self.running: bool = True
        self.state: str = "menu"
        self.choice: int = 0
        self.message: str = ""
        self.name: str = ""
        self.score: int = 0
        self.won: bool = False
        self.game: Game | None = None
        self.view: GameView | None = None

    # ---------- text ----------

    def font(self, size: int) -> pygame.font.Font:
        """Return a (cached) monospace font.
        Args: size is the size of one letter pixel, as in the mlx version.
        Returns: the font."""

        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont(
                "dejavusansmono,couriernew,monospace", size * 8, bold=True)
        return self.fonts[size]

    def write_centered(self, text: str, y: int, size: int,
                       color: tuple[int, int, int]) -> None:
        """Write a text centered in the window.
        Args: text is the text, y is the top of the text, size is the
        size of one letter pixel, color is the color of the text.
        Returns: none."""

        surface: pygame.Surface = self.font(size).render(text, True, color)
        self.screen.blit(surface, ((WIDTH - surface.get_width()) // 2, y))

    # ---------- screens ----------

    def show_screen(self, state: str) -> None:
        """Go to another screen.
        Args: state is "menu", "pause", "highscores", "instructions",
        "name" or "game".
        Returns: none."""

        self.state = state
        self.choice = 0

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
        self.view = GameView(self.game)
        self.show_screen("game")

    def stop_game(self) -> None:
        """Forget the current game.
        Args: none.
        Returns: none."""

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

    # ---------- keys ----------

    def on_key(self, key: int, char: str) -> None:
        """React to a key, depending on the current screen.
        Args: key is the pygame key code, char the typed character.
        Returns: none."""

        if self.state == "name":
            self.name_key(key, char)
        elif key == pygame.K_ESCAPE and self.state == "menu":
            self.running = False
        elif key == pygame.K_ESCAPE:
            self.stop_game()
            self.show_screen("menu")
        elif self.state == "game":
            self.game_key(key)
        elif self.state in ("menu", "pause"):
            self.menu_key(key)

    def game_key(self, key: int) -> None:
        """During the game: move Pac-Man, open the pause menu or use the
        cheat mode.
        Args: key is the pygame key code.
        Returns: none."""

        if self.game is None:
            return
        if key in (pygame.K_SPACE, pygame.K_p):
            self.game.toggle_pause()
            self.show_screen("pause")
        elif key in self.KEYS:
            self.game.player.turn(self.KEYS[key])
        elif key == KEY_CHEAT:
            toggle_cheat_mode(self.game)
        elif key in CHEATS:
            use_cheat(self.game, key)

    def menu_key(self, key: int) -> None:
        """In a menu: move the selection up or down or validate it.
        Args: key is the pygame key code.
        Returns: none."""

        options: list[str] = self.MAIN_MENU if self.state == "menu" \
            else self.PAUSE_MENU
        if key in (pygame.K_UP, pygame.K_w, pygame.K_z):
            self.choice = (self.choice - 1) % len(options)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.choice = (self.choice + 1) % len(options)
        elif key in self.KEY_ENTER:
            self.select(options[self.choice])
        elif key in (pygame.K_SPACE, pygame.K_p) and self.state == "pause":
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
            self.running = False
        elif option == "RESUME" and self.game is not None:
            self.game.toggle_pause()
            self.show_screen("game")
        elif option == "MAIN MENU":
            self.stop_game()
            self.show_screen("menu")

    def name_key(self, key: int, char: str) -> None:
        """Type the name of the player, then save the score with Enter.
        Args: key is the pygame key code, char the typed character.
        Returns: none."""

        if key in self.KEY_ENTER:
            self.highscores.add(self.name, self.score)
            self.show_screen("menu")
        elif key == pygame.K_ESCAPE:
            self.show_screen("menu")
        elif key == pygame.K_BACKSPACE:
            self.name = self.name[:-1]
        elif len(char) == 1 and ord(char) < 128 \
                and len(self.name) < MAX_NAME:
            if char.isalnum() or char == " ":
                self.name += char.upper()

    # ---------- drawing ----------

    def draw_screen(self) -> None:
        """Draw the current menu-like screen on a black background.
        Args: none.
        Returns: none."""

        self.screen.fill((0, 0, 0))
        if self.state == "menu":
            self.write_centered("PAC-MAN", 150, 14, self.SELECTED)
            self.draw_options(self.MAIN_MENU)
            self.write_centered(self.message[:60], 830, 3, self.LOST)
        elif self.state == "pause":
            self.write_centered("PAUSE", 150, 12, self.SELECTED)
            self.draw_options(self.PAUSE_MENU)
        elif self.state == "highscores":
            self.draw_highscores()
        elif self.state == "instructions":
            self.draw_instructions()
        elif self.state == "name":
            self.draw_name()

    def draw_options(self, options: list[str]) -> None:
        """Write the options of a menu, the selected one appears yellow.
        Args: options are the options of the menu.
        Returns: none."""

        for i, option in enumerate(options):
            color = self.SELECTED if i == self.choice else self.TEXT
            self.write_centered(option, 420 + i * 90, 6, color)
        self.write_centered("ARROWS: CHOOSE    ENTER: VALIDATE    "
                            "ESC: QUIT", 920, 3, self.TEXT)

    def draw_highscores(self) -> None:
        """Write the top 10 (at max) with the names and the scores.
        Args: none.
        Returns: none."""

        self.write_centered("HIGHSCORES", 80, 9, self.SELECTED)
        if not self.highscores.scores:
            self.write_centered("NO SCORE YET", 450, 5, self.TEXT)
        for i, (name, score) in enumerate(self.highscores.scores):
            line: str = f"{i + 1:>2}. {name:<10} {score:>7}"
            self.write_centered(line, 230 + i * 62, 5, self.TEXT)
        self.write_centered("ESC: BACK TO MENU", 920, 3, self.TEXT)

    def draw_instructions(self) -> None:
        """Write the controls and the rules of the game.
        Args: none.
        Returns: none."""

        conf: Config = self.config
        lines: list[str] = [
            "ARROWS OR WASD: MOVE PAC-MAN",
            "SPACE OR P: PAUSE    ESC: MENU, AGAIN: QUIT",
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
        self.write_centered("INSTRUCTIONS", 60, 9, self.SELECTED)
        for i, line in enumerate(lines):
            self.write_centered(line, 190 + i * 52, 4, self.TEXT)
        for i, line in enumerate(cheats):
            self.write_centered(line, 770 + i * 36, 3, self.CHEAT)
        self.write_centered("ESC: BACK TO MENU", 940, 3, self.TEXT)

    def draw_name(self) -> None:
        """Write the end of the game: the result, the final score and the
        name of the player being typed.
        Args: none.
        Returns: none."""

        if self.won:
            self.write_centered("CONGRATULATIONS!", 120, 8, self.WON)
            self.write_centered("YOU FINISHED ALL THE LEVELS", 250, 4,
                                self.TEXT)
        else:
            self.write_centered("GAME OVER", 120, 10, self.LOST)
        self.write_centered(f"FINAL SCORE {self.score}", 360, 6, self.TEXT)
        self.write_centered("ENTER YOUR NAME", 520, 4, self.TEXT)
        self.write_centered(self.name + "_", 600, 7, self.SELECTED)
        self.write_centered("ENTER: SAVE    ESC: SKIP", 920, 3, self.TEXT)

    # ---------- main loop ----------

    def on_frame(self, dt: float) -> None:
        """Play and draw one frame.
        Args: dt is the time since the last frame, in seconds.
        Returns: none."""

        try:
            if self.state == "game" and self.game is not None \
                    and self.view is not None:
                self.game.update(dt)
                self.view.draw(self.screen)
                if self.game.state in ("won", "lost"):
                    self.end_game(self.game)
            else:
                self.draw_screen()
        except LevelError as e:
            self.stop_game()
            self.message = f"ERROR: {e}"
            self.show_screen("menu")

    def run(self) -> None:
        """Open the window and play until the player quits.
        Args: none.
        Returns: none."""

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        clock: pygame.time.Clock = pygame.time.Clock()
        while self.running:
            dt: float = min(clock.tick(self.FPS) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.on_key(event.key, event.unicode)
            self.on_frame(dt)
            pygame.display.flip()
        pygame.quit()