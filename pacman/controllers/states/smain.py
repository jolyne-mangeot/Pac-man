
from functools import partial
from typing import Any

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import ActivateOption
from pacman.views import MainMenuDisplay


class MainMenuState(State):
    """Class MainMenu, subclass of State

    Represents the main menu of the game, initializing a Menu object to
    navigate different options: Play, Highscores, Settings and Quit.
    Relies on this Menu to handles events and display other than the
    background.

    ### Attributes:
    - *State instance parameters and attributes*
    - main_menu: Menu => Menu object used to navigate options and display them

    ### Methods
    - *State instance methods*
    - init_menu => instantiate the Menu object into the main_menu attribute
    with set parameters
    - startup (override) => calls init_menu to initialize navigation
    - cleanup (override) => deletes the main_menu attribute to save memory
    - get_event (override) => check if the return_key has been pressed to
    quit the game, otherwise pass down the pygame event received to main_menu's
    input_event method
    - update (override) => calls draw
    - draw (override) => displays all visual elements, namely the background
    and the main_menu with the dedicated method
    """
    def __init__(self, control: Control) -> None:
        """Initialize the menu with State's init, taking a Control object
        as argument, and a self attributed variable main_menu of type Menu
        to handle navigation and program flow.
        """
        State.__init__(self, control)
        self.display: MainMenuDisplay = MainMenuDisplay(self.control)
        self.display.load_main_menues()
        self.main_menu: Menu

    def __init_menu__(self) -> None:
        """Instantiate the main_menu attribute with set parameters, selecting
        elements from the dialogs dict of control.
        """
        self.main_menu = Menu(loop_cursor=False, options=[
            ActivateOption(
                "play", "{name}", partial(self.switch_state, "game_menu")),
            ActivateOption(
                "highscores", "{name}",
                partial(self.switch_state, "highscores_menu")),
            ActivateOption(
                "settings", "{name}",
                partial(self.switch_state, "options_menu")),
            ActivateOption("quit", "{name}", partial(lambda: "program_quit"))])

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings.
        """
        self.__init_menu__()
        self.display.startup(self.main_menu)

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting the main_menu
        attribute to save on memory usage.
        """
        self.display.mixer("option_activate")
        del self.main_menu
        self.display.cleanup()

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Pass the event object down to the main_menu by calling its input_event
        method. If it returns "program_quit" or the return key is pressed,
        switches the current state to "quit", effectively leaving the program.
        """
        return_key: str = self.control.settings.key_config.return_key
        output: Any = self.main_menu.get_event(
            *self.read_input_events(event), "vertical")
        if (event.type == pg.KEYDOWN and pg.key.name(event.key) == return_key
                or output == "program_quit"):
            self.display.mixer("program_quit")
            pg.time.delay(240)
            self.switch_state("quit")
            return

    def update(self) -> None:
        """Called after the events have been parsed, calls the draw and mixer
        Display methods. Updates the menu's current action to an empty string
        to avoid sound repetitions.
        """
        self.display.mixer(self.main_menu.action_done)
        self.display.draw()
        self.main_menu.action_done = ""
