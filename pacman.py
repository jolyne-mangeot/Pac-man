
import pygame as pg

from pacman import (
    Control, State,
    MainMenu, OptionsMenu, GameMenu)


def main() -> int:
    """Pac-Man program's main script, initiating a Control object and
    calling its game_loop method, effectively launching the game.

    Returns an exit code:
    - 0, success
    - 1, keyboard interrupt
    """
    pg.init()
    pg.font.init()

    game = Control("pacman/config.json")

    state_dict: dict[str, State] = {
        "main_menu": MainMenu(game),
        "options_menu": OptionsMenu(game),
        "game_menu": GameMenu(game)}

    game.set_up_states(state_dict)

    game.game_loop()
    pg.quit()
    return 0


if __name__ == "__main__":
    try:
        output: int = main()
    except KeyboardInterrupt:
        output = 1
        print("\r  ")
    exits: tuple[str, ...] = (
        "Success", "Keyboard interrupt")
    print(f"\nLeaving program\n\nExit {output} ({exits[output]})\n")
