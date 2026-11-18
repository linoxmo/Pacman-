# Issues encountered during development

- Ghosts never caught a stopped Pac-Man: they used a Manhattan distance
  and turned around the walls. Fixed by counting the distance through the
  corridors with the BFS of `level.py`.
- The game was too hard: ghosts slowed down (3 cells/s) and scatter mode
  added.
- Cheat keys 1 to 7 did not work on AZERTY keyboards (the MLX ignores
  Shift): moved to F1 to F7.
- After the merge, cheats worked without pressing C: the check was put
  back.
- The merge used about 68 random pacgums: back to a pacgum in every
  corridor ("most corridors" in the subject, first level reproducible).
- The first pygame version used functions without MLX equivalent
  (scale, flip, transparency, fonts): rewritten pixel by pixel.
- Pixel by pixel, loading took 6 s and a new level 1.5 s: background baked
  in `images/background.png`, sprites made once per cell size, walls put as
  ready pieces. Now about 2 s at start and less than 1 s per level.
