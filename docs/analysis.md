# Project analysis

## Technical choices

- **Graphics**: pygame, limited to the functions that have an MLX
  equivalent (window, image, pixel, PNG loading, putting an image, key
  events), as asked by the subject. Resizing, mirroring, shapes and text
  are done pixel by pixel. The first version used MiniLibX (`pymlx`).
- **Look**: Looney Tunes characters (Bugs Bunny and 4 enemies), carrots as
  super-pacgums, a darkened prairie as background, the `42` as a window
  on the bright prairie, edible enemies colored in green.
- **Mazes**: assigned `mazegenerator` 2.1.0, `perfect=False`, seed 42 for the
  first level then random. A pacgum in every reachable cell.
- **Movements**: cell by cell, speed in cells per second.
- **Ghosts**: at each cell they take the free direction (except turning back)
  that brings them the closest to their target, counted through the
  corridors (BFS). A Manhattan distance made them turn around the walls
  of our random mazes without ever catching Pac-Man.
  Blinky: Pac-Man. Pinky: 4 cells in front of Pac-Man. Inky: symmetric of
  Blinky around 2 cells in front of Pac-Man. Clyde: Pac-Man if further than
  8 cells, his corner otherwise. 7 s of scatter then 20 s of chase. When
  edible, they run away from Pac-Man.
- **Time limit**: the player loses a life and the timer restarts.
- **Highscores**: top 10 in a JSON file.
- **Packaging**: PyInstaller (`pac-man.spec`), one Linux file on itch.io.

## Problems found in the generator

- The middle of the maze can be inside the `42`: the player starts on the
  closest free cell.
- Its errors are caught and displayed, the game goes back to the menu.
