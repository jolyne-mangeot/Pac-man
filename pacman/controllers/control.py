
import pygame as pg
from typing import cast

from pacman.models import (
    State, Settings, Config, Dialogs, json_to_model,
    MainMenu, OptionsMenu, GameMenu)


class Control:
    def __init__(self, config_path: str) -> None:
        """Load game settings and init essential data related to Pygame."""
        self.config: Config = cast(Config, json_to_model(Config, config_path))
        self.settings: Settings = cast(Settings, json_to_model(Settings))
        self.dialogs: Dialogs = cast(Dialogs, json_to_model(
            Dialogs, "pacman/assets/dialogs" + self.settings.lang.value))

        self.screen: pg.Surface = pg.display.set_mode(self.settings.res.value)
        self.screen_rect: pg.Rect = self.screen.get_rect()
        self.clock: pg.time.Clock = pg.time.Clock()
        self.delta_time: float
        self.fps: int = 30
        self.done: bool = False

        self.state_dict: dict[str, State] = {
            "main_menu": MainMenu(self),
            "options_menu": OptionsMenu(self),
            "game_menu": GameMenu(self)}
        self.state_name: str = "main_menu"
        self.current_state: State = self.state_dict[self.state_name]

    def flip_state(self) -> None:
        """Make all necessary changes to attributes to cleanup a state
        and startup another based on next segment set in events such
        as select_option whenever state attribute done is True
        - also save in previous attribute the ended state.
        """
        self.current_state.done = False
        previous: str
        previous, self.state_name = self.state_name, self.current_state.next
        self.current_state.cleanup()
        self.current_state = self.state_dict[self.state_name]
        self.current_state.startup()
        self.current_state.previous = previous

    def update(self) -> None:
        """Check for state done status to either quit the script loop
        or initialize a new state with flip_state.
        """
        if self.current_state.done:
            self.flip_state()
        self.current_state.update()

    def event_loop(self) -> None:
        """Main loop for pygame events which initializes the current state's
        event loop as well.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.current_state.get_event(event)

    def main_game_loop(self) -> None:
        """Access all essential methods to run game loop based on clock ticks
        with event_loop, which launches on the control class scope before
        the current state one, update for each class level as well before
        updating the pygame display.
        """
        while not self.done:
            self.delta_time = self.clock.tick(self.fps) / 1000
            self.event_loop()
            self.update()
            pg.display.update()
