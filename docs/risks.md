# Risks and how we handle them

- **The maze generator fails or returns a bad maze**: `LevelError`, message
  in the menu, no crash.
- **Wrong config file**: defaults, clamped values, warnings, no traceback.
- **Missing or broken highscore file**: empty top 10 or bad entries
  ignored, warning.
- **Missing image or no display**: clear error message, clean exit.
- **pygame function without MLX equivalent**: only window, image, pixel,
  PNG, blit and events.
- **Pixel by pixel drawing too slow**: sprites made once per cell size,
  background baked, only changed letters and eaten pacgums redrawn.
- **Too hard for the player**: ghosts slower than the player, scatter mode,
  cheat mode.
- **Two people working on the same files**: one branch per person, merge
  by pull request.
