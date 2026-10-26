_This activity has been created as part of the 42 curriculum by lagerard, tmagoudi._


((A compléter à la fin du projeeeeeet, bien vérifier qu'on oublie rien mais l'essentiel est là))


# DESCRIPTION
--> Goal and overview of the game

# INSTRUCTIONS
--> Installation, execution and controls

# CONFIGURATION
--> Config file structure and default values

A value out of its limits is set to the closest limit (ex: `"lives": 0`
becomes 1). A wrong or missing value takes its default value.

Maze size: from 11 x 11 to 50 x 50. Under 11, the ghosts (in the corners)
reach Pac-Man (in the middle) in less than 2 seconds, so the player has no
time to react. The `42` is only drawn from 15 x 11.

# HIGHSCORE
--> How it works and why

# MAZE GENERATION
--> How the assigned A-Maze-ing package is used

# IMPLEMENTATION
--> Technical summary

Ghosts: the 4 ghosts of the original game, with their original behaviour.
They all move the same way, only their target changes:
    - Blinky (red): Pac-Man
    - Pinky (pink): 4 cells in front of Pac-Man
    - Inky (blue): symmetric of Blinky around 2 cells in front of Pac-Man
    - Clyde (orange): Pac-Man if further than 8 cells, his corner otherwise

# GENERAL SOFTWARE ARCHITECTURE
--> Modules, classes and their relationships... Chiant

# PROJECT MANAGEMENT
--> Overview

# RESOURCES
--> References and help
