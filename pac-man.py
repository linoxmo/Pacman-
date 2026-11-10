from pacgame.parsing import create_conf
from pacgame.screens import App
import sys


def main() -> None:
    """Read the config file given as argument and launch the game.
    Args: none.
    Returns: none."""

    try:
        if len(sys.argv) != 2:
            print("Error: input should be 'python3 pac-man.py config.json'")
            return
        config = create_conf(sys.argv[1])
        App(config).run()
    except KeyboardInterrupt:
        print("\nGame stopped")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
