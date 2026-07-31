
import pygame as pg
from functools import partial

from pacman.controllers import Control, State, Menu, ActivateOption
from pacman.models import Dialogs


class MainMenu(State):
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
        self.main_menu: Menu

    def __init_menu__(self) -> None:
        """Instantiate the main_menu attribute with set parameters, selecting
        elements from the dialogs dict of control.
        """
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
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings.
        """
        self.__init_menu__()

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting the main_menu
        attribute to save on memory usage.
        """
        del self.main_menu

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Checks if the return_key was pressed by comparing the event with the
        key_config from State attributes to leave the game, and otherwise
        pass the event object down to the main_menu by calling its input_event
        method.
        """
        return_key: str = self.control.settings.key_config.return_key
        if event.type == pg.KEYDOWN and event.unicode == return_key:
            return self.switch_state("quit")
        self.main_menu.get_event(
            self.control.settings.key_config, event, "vertical")

    def update(self) -> None:
        """Called after the events have been parsed, calls the draw method."""
        self.draw()

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((255, 120, 0))
        self.main_menu.draw_vertical_options()
