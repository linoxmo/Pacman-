from pacgame.parsing import Config
from pacgame.level import Maze
from pacgame.player import Player
from pacgame.ghost import Ghost, Blinky, Pinky, Inky, Clyde


class Game():
    """Rules of one game: score, lives, time and levels.
    Args: none.
    Returns: none."""

    def __init__(self, config: Config) -> None:
        """Start a new game on the first level.
        Args: config is the game configuration.
        Returns: none."""

        self.config: Config = config
        self.score: int = 0
        self.level_index: int = 0
        self.state: str = "playing"
        self.maze: Maze
        self.player: Player
        self.ghosts: list[Ghost]
        self.time_left: float
        self.load_level(config.lives)

    def load_level(self, lives: int) -> None:
        """Create the maze, Pac-Man and the ghosts of the current level.
        Args: lives is the number of lives Pac-Man still have.
        Returns: none."""

        conf: Config = self.config
        seed: int = conf.seed if self.level_index == 0 else 0
        self.maze = Maze(conf.levels[self.level_index], seed)
        self.player = Player(self.maze, conf.player_speed, lives)
        top_left, top_right, bottom_left, bottom_right = self.maze.corners
        times: tuple[float, float] = (conf.edible_time,
                                      conf.ghost_respawn_time)
        blinky: Blinky = Blinky(self.maze, top_left, conf.ghost_speed,
                                self.player, *times)
        self.ghosts = [
            blinky,
            Pinky(self.maze, top_right, conf.ghost_speed, self.player, *times),
            Inky(self.maze, bottom_left, conf.ghost_speed, self.player,
                 *times, blinky),
            Clyde(self.maze, bottom_right, conf.ghost_speed, self.player,
                  *times)]
        self.time_left = float(conf.level_max_time)

    def toggle_pause(self) -> None:
        """Pause the game or resume it if it is already paused.
        Args: none.
        Returns: none."""

        if self.state == "playing":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "playing"

    def update(self, dt: float) -> None:
        """Play dt (= delta time since last image) seconds of the game.
        Args: dt is the time since the last image update in seconds.
        Returns: none."""

        if self.state != "playing":
            return
        self.time_left -= dt
        if self.time_left <= 0:
            self.lose_life()
            return
        self.player.update(dt)
        self.eat()
        self.check_ghosts()
        for ghost in self.ghosts:
            ghost.update(dt)
        self.check_ghosts()
        if not self.maze.pacgums and not self.maze.super_pacgums:
            self.next_level()

    def eat(self) -> None:
        """Eat the pacgum or the super-pacgum under Pac-Man.
        Args: none.
        Returns: none."""

        cell: tuple[int, int] = (self.player.x, self.player.y)
        if cell in self.maze.pacgums:
            self.maze.pacgums.remove(cell)
            self.score += self.config.points_per_pacgum
        elif cell in self.maze.super_pacgums:
            self.maze.super_pacgums.remove(cell)
            self.score += self.config.points_per_super_pacgum
            for ghost in self.ghosts:
                ghost.make_edible()

    def check_ghosts(self) -> None:
        """Check if Pac-Man and a ghost are on the same cell: Pac-Man eats
        an edible ghost, a chasing ghost takes a life of Pac-Man.
        Args: none.
        Returns: none."""

        for ghost in self.ghosts:
            if (ghost.x, ghost.y) != (self.player.x, self.player.y):
                continue
            if ghost.state == "edible":
                ghost.get_eaten()
                self.score += self.config.points_per_ghost
            elif ghost.state == "chase":
                self.lose_life()
                return

    def lose_life(self) -> None:
        """Remove a life. Game over if there is no life left, otherwise
        everybody goes back to its start cell and the time restarts.
        Args: none.
        Returns: none."""

        self.player.lives -= 1
        if self.player.lives <= 0:
            self.state = "lost"
            return
        self.player.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.time_left = float(self.config.level_max_time)

    def next_level(self) -> None:
        """Go to the next level, keeping your score and lives, or win the
        game after the last level.
        Args: none.
        Returns: none."""

        self.level_index += 1
        if self.level_index >= len(self.config.levels):
            self.state = "won"
            return
        self.load_level(self.player.lives)
