# Issues

- Ghosts never caught a stopped Pac-Man: they used a Manhattan distance
  and turned around the walls. Fixed by counting the distance through the
  corridors with the BFS of `level.py`.
