
import pygame as pg
from functools import partial

from pacman.controllers import Control, State, Menu, ActivateOption
from pacman.models import Dialogs


class MainMenu(State):
    def __init__(self, control: Control) -> None:
        State.__init__(self, control)
        self.main_menu: Menu

    def __init_menu__(self) -> None:
        dialogs: Dialogs = self.control.dialogs
        self.main_menu = Menu(
            self.control.screen, options=[
                ActivateOption("play", dialogs.play,
                               partial(self.switch_state, "game_menu")),
                ActivateOption(
                    "highscores", dialogs.highscores,
                    partial(self.switch_state, "highscores_menu")),
                ActivateOption(
                    "settings", dialogs.settings,
                    partial(self.switch_state, "options_menu")),
                ActivateOption("quit", dialogs.quit,
                               partial(self.switch_state, "quit"))])

    def startup(self) -> None:
        self.__init_menu__()

    def cleanup(self) -> None:
        del self.main_menu

    def get_event(self, event: pg.event.Event) -> None:
        return_key: str = self.control.settings.key_config.return_key
        if event.type == pg.KEYDOWN and event.unicode == return_key:
            return self.switch_state("quit")
        self.main_menu.get_event(
            self.control.settings.key_config, event, "vertical")

    def update(self) -> None:
        self.draw()

    def draw(self) -> None:
        self.control.screen.fill((255, 0, 0))
        self.main_menu.draw_vertical_options()
