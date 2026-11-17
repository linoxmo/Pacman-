from pacgame.game import Game


KEY_CHEAT: int = 99
CHEATS: dict[int, str] = {
    65470: "INVINCIBLE", 65471: "NEXT LEVEL", 65472: "FREEZE",
    65473: "EXTRA LIFE", 65474: "SPEED", 65475: "BLUE GHOSTS",
    65476: "TIME 10S"}
FAST: float = 2.0
SHORT_TIME: float = 10.0
MESSAGE_TIME: float = 3.0


def show_message(game: Game, message: str) -> None:
    """Show a message after "CHEAT MODE:" for 3 seconds.
    Args: game is the current game, message is the text to show.
    Returns: none."""

    game.message = message
    game.message_time = MESSAGE_TIME


def toggle_cheat_mode(game: Game) -> None:
    """Turn the cheat mode on or off. When it is off, every cheat stops.
    Args: game is the current game.
    Returns: none."""

    game.cheat_mode = not game.cheat_mode
    if not game.cheat_mode:
        game.invincible = False
        game.frozen = False
        game.always_edible = False
        set_speed(game, 1.0)


def set_speed(game: Game, factor: float) -> None:
    """Change the speed of Pac-Man (it is kept for the next levels).
    Args: game is the current game, factor multiplies the normal speed.
    Returns: none."""

    game.speed_factor = factor
    game.player.speed = game.config.player_speed * factor


def use_cheat(game: Game, keycode: int) -> None:
    """Use the cheat of a function key (F1 to F7), only in cheat mode.
    Args: game is the current game, keycode is the key.
    Returns: none."""

    if not game.cheat_mode or keycode not in CHEATS:
        return
    cheat: str = CHEATS[keycode]
    if cheat == "INVINCIBLE":
        game.invincible = not game.invincible
    elif cheat == "NEXT LEVEL":
        game.next_level()
        show_message(game, f"LEVEL {game.level_index + 1}")
    elif cheat == "FREEZE":
        game.frozen = not game.frozen
    elif cheat == "EXTRA LIFE":
        game.player.lives += 1
        show_message(game, "+1 LIFE")
    elif cheat == "SPEED":
        set_speed(game, 1.0 if game.speed_factor > 1.0 else FAST)
    elif cheat == "BLUE GHOSTS":
        game.always_edible = not game.always_edible
    elif cheat == "TIME 10S":
        game.time_left = min(game.time_left, SHORT_TIME)


def cheat_text(game: Game) -> str:
    """Give the cheats that are on, to show them on the screen.
    Args: game is the current game.
    Returns: ex: "CHEAT MODE: INVINCIBLE / FREEZE" or "" if the mode is
    off."""

    if not game.cheat_mode:
        return ""
    names: list[str] = []
    if game.invincible:
        names.append("INVINCIBLE")
    if game.frozen:
        names.append("FREEZE")
    if game.speed_factor > 1.0:
        names.append("SPEED")
    if game.always_edible:
        names.append("BLUE GHOSTS")
    if game.message_time > 0:
        names.append(game.message)
    if not names:
        return "CHEAT MODE: ON"
    return "CHEAT MODE: " + " / ".join(names)
