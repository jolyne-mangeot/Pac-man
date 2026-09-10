
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import (
    TextHolder, TextValueHolder, ActivateOption, Highscores)
from pacman.views import HighscoresMenuDisplay


class HighscoresMenuState(State):
    def __init__(self, control: Control) -> None:
        """Initialize the menu with State's init, taking a Control object
        as argument, and a self attributed variable main_menu of type Menu
        to handle navigation and program flow.
        """
        State.__init__(self, control)
        self.display: HighscoresMenuDisplay = HighscoresMenuDisplay(
            self.control)
        self.highscore_title: Menu
        self.highscore_index: Menu
        self.highscore_list: Menu
        self.reset_menu: Menu

        self.index: int = 1

    def __init_menu__(self) -> None:
        self.highscore_title = Menu([TextHolder(
            "highscores_menu", static_style="picked")])
        if self.control.highscores.scores == []:
            self.highscore_index = Menu([])
            self.highscore_list = Menu([TextHolder("no_highscores")])
        else:
            self.highscore_index = Menu([TextValueHolder(
                "index", self, False, text="")])
            self.highscore_list = Menu(loop_cursor=False, options=[])
            for score in self.control.highscores.scores:
                self.highscore_list.options.extend([
                    TextValueHolder("player", score, selectable=True),
                    TextValueHolder("score", score),
                    TextValueHolder("level_reached", score),
                    TextValueHolder("time_taken", score),
                    TextValueHolder("remaining_lives", score)])
            self.highscore_list.select_index = 0
        self.reset_menu = Menu(loop_cursor=False, options=[
            ActivateOption("back", partial(self.switch_state, "main_menu")),
            ActivateOption("reset_highscores", partial(self.reset_highscores))]
        )

    def reset_highscores(self) -> None:
        if self.control.highscores.scores == []:
            return
        self.control.highscores = Highscores()
        self.cleanup()
        self.control.update_highscores()
        self.startup()

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings.
        """
        self.__init_menu__()
        self.display.startup(
            self.highscore_title, self.highscore_index,
            self.highscore_list, self.reset_menu)

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting the main_menu
        attribute to save on memory usage.
        """
        self.display.mixer("option_activate")
        del self.highscore_title
        del self.highscore_index
        del self.highscore_list
        del self.reset_menu
        self.display.cleanup()

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Pass the event object down to the main_menu by calling its input_event
        method. If it returns "program_quit" or the return key is pressed,
        switches the current state to "quit", effectively leaving the program.
        """
        inputs: tuple[str, str, str] = self.read_input_events(event)
        if inputs[1] == "return_key":
            self.switch_state("main_menu")
        self.highscore_list.get_event(*inputs, "vertical")
        self.reset_menu.get_event(*inputs, "horizontal")
        self.index = (self.highscore_list.select_index // 5) + 1

    def update(self) -> None:
        """Called after the events have been parsed, calls the draw and mixer
        Display methods. Updates the menu's current action to an empty string
        to avoid sound repetitions.
        """
        self.display.draw()
