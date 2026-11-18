# Acceptance test plan

All the tests below pass.
Bugs found and fixed (ie: `issues.md`).

- **Launch**: 0 or 2 arguments, missing image, no display: clear message,
  no crash.
- **Config**: missing file, bad JSON, value out of limits, unknown key:
  warning, then defaults.
- **Menus**: main menu, instructions, highscores, pause (Resume, Main
  menu), Esc to go back or quit.
- **Maze**: same first level with seed 42, random next levels.
- **Player**: arrows, WASD and ZQSD, no move through walls.
- **Score**: pacgum +10, carrot +50, edible ghost +200.
- **Lives**: ghost or end of the time: -1 life, respawn in the middle.
- **Levels**: all pacgums eaten: next level, score and lives kept.
- **End of the game**: name of 10 characters max (letters, digits,
  spaces), Enter saves, Esc skips.
- **Highscores**: top 10 sorted, kept after a restart, broken file ignored.
- **Cheat mode**: F1 to F7 only after C, C again turns them all off.
- **Lint and package**: `make lint`, `make package` then
  `./pac-man config.json` from another folder.
