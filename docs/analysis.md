# Project analysis

## Technical choices

- **Graphics**: MiniLibX (`pymlx`), already used in our A-Maze-ing.
- **Config**: `#` lines removed, then validated with Pydantic. Out of range
  values are clamped, invalid or missing ones take their default value.
- **Mazes**: assigned `mazegenerator` 2.1.0, `perfect=False`, seed 42 for the
  first level then random.
- **Movements**: cell by cell, speed in cells per second.
- **Ghosts**: at each cell they take the free direction (except turning back)
  that brings them the closest to their target, counted through the
  corridors (BFS). A Manhattan distance made them turn around the walls
  of our random mazes without ever catching Pac-Man.
  Blinky: Pac-Man. Pinky: 4 cells in front of Pac-Man. Inky: symmetric of
  Blinky around 2 cells in front of Pac-Man. Clyde: Pac-Man if further than
  8 cells, his corner otherwise. When edible, they run away from Pac-Man.
- **Time limit**: the player loses a life and the timer restarts.
- **Highscores**: top 10 in a JSON file.
- **Packaging**: PyInstaller, Linux build on itch.io.


## Problems found in the generator

- The middle of the maze can be inside the `42`: the player starts on the
  closest free cell.
- Its errors are caught and displayed, the game goes back to the menu.
