
from sys import argv

import pygame as pg
from pydantic import ValidationError

from game import (
    Control, State,
    MainMenuState, InstructionsMenuState, HighscoresMenuState,
    OptionsMenuState, GameState)


def main(config_path: str) -> int:
    """Pac-Man program's main script, initiating a Control object and
    calling its game_loop method, effectively launching the game.

    Returns an exit code:
    - 0, success
    - 1, keyboard interrupt
    """
    pg.init()
    pg.font.init()

    game = Control(config_path)

    state_dict: dict[str, State] = {
        "main_menu": MainMenuState(game),
        "instructions_menu": InstructionsMenuState(game),
        "highscores_menu": HighscoresMenuState(game),
        "options_menu": OptionsMenuState(game),
        "game_menu": GameState(game)}

    game.set_up_states(state_dict)

    game.game_loop()
    pg.quit()
    return 0


if __name__ == "__main__":
    config_path: str = argv[1] if len(argv) > 1 else ""
    print()
    try:
        output: int = main(config_path)
    except KeyboardInterrupt:
        output = 1
        print("\r  ")
    except ValidationError:
        output = 2
        print("Unexpected error during Parsing of configuration files.")
    # except Exception:
    #     output = 3
    exits: tuple[str, ...] = (
        "Success", "Keyboard interrupt",
        "Configuration error", "Unknown error")
    print(f"\nLeaving program\n\nExit {output} ({exits[output]})\n")
