import pygame
from pacgame.parsing import Config
from pacgame.game import Game
from pacgame.level import LevelError
from pacgame.new_representations import GameView, WIDTH, HEIGHT


KEYS: dict[int, str] = {
    pygame.K_UP: "N", pygame.K_DOWN: "S",
    pygame.K_LEFT: "W", pygame.K_RIGHT: "E",
    pygame.K_w: "N", pygame.K_z: "N", pygame.K_s: "S",
    pygame.K_a: "W", pygame.K_q: "W", pygame.K_d: "E"}
FPS: int = 60


class App():
    """Open the window and run the game loop.
    Args: none.
    Returns: none."""

    def __init__(self, config: Config) -> None:
        """Prepare the application.
        Args: config is the game configuration.
        Returns: none."""

        self.config: Config = config
        self.screen: pygame.Surface
        self.game: Game
        self.view: GameView

    def on_key(self, key: int) -> bool:
        """React to a key: move, pause or quit.
        Args: key is the pygame key code.
        Returns: false if the game must stop, true otherwise."""

        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_p:
            self.game.toggle_pause()
        elif key in KEYS:
            self.game.player.turn(KEYS[key])
        return True

    def run(self) -> None:
        """Open the window and play until it is closed.
        Args: none.
        Returns: none."""

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        try:
            self.game = Game(self.config)
        except LevelError as e:
            print(f"Error: {e}")
            pygame.quit()
            return
        self.view = GameView(self.game)
        clock = pygame.time.Clock()
        running: bool = True
        while running:
            dt: float = min(clock.tick(FPS) / 1000, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self.on_key(event.key) and running
            try:
                self.game.update(dt)
            except LevelError as e:
                print(f"Error: {e}")
                break
            self.view.draw(self.screen)
            pygame.display.flip()
            if self.game.state in ("won", "lost"):
                print(f"Game {self.game.state}, score {self.game.score}")
                running = False
        pygame.quit()