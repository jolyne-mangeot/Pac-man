
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import ActivateOption, TextHolder
from pacman.views import MainMenuDisplay


class MainMenuState(State):
    """Class MainMenuState, subclass of State

    #### Description:
    Represents the main menu of the game, initializing a Menu object to
    navigate different options: Play, Highscores, Settings and Quit.
    Relies on this Menu to handles events and display other than the
    background.

    ### Attributes:
    - *State instance parameters and attributes*
    - display: MainMenuDisplay => display the main_menu using its own methods
    - main_menu: Menu => Menu object used to navigate options and display them
    - error_list: Menu => object containing all current error messages

    ### Methods
    - *State instance methods*
    - init_menu => instantiate the Menu object into the main_menu attribute
    with set parameters
    - startup (override) => calls init_menu to initialize navigation
    - cleanup (override) => deletes the main_menu attribute to save memory
    - leave_game => switches the current state to "quit", informing Control to
    stop the program
    - get_event (override) => check if the return_key has been pressed to
    quit the game, otherwise pass down the pygame event received to main_menu's
    input_event method
    - update (override) => calls draw
    """
    def __init__(self, control: Control) -> None:
        """Initialize the menu with State's init, taking a Control object
        as argument, and a self attributed variable main_menu of type Menu
        to handle navigation and program flow.
        """
        State.__init__(self, control)
        self.display: MainMenuDisplay = MainMenuDisplay(self.control)
        self.main_menu: Menu
        self.error_list: Menu

    def __init_menu__(self) -> None:
        """Instantiate the main_menu attribute with set parameters, and the
        error_list menu with an empty list filled with all current errors.
        """
        self.main_menu = Menu(loop_cursor=False, options=[
            ActivateOption("play", partial(self.switch_state, "game_menu")),
            ActivateOption(
                "highscores", partial(self.switch_state, "highscores_menu")),
            ActivateOption(
                "settings", partial(self.switch_state, "options_menu")),
            ActivateOption("quit", partial(self.leave_game))])

        self.error_list = Menu(options=[])
        if self.control.config_path == "":
            self.error_list.options.append(TextHolder("arg_error"))
        if self.control.config.status is False:
            self.error_list.options.append(TextHolder("config_error"))
        if self.control.settings.status is False:
            self.error_list.options.append(TextHolder("settings_error"))
        if self.control.highscores.status is False:
            self.error_list.options.append(TextHolder("highscores_error"))
        if self.control.dialogs.get("status", False) == "False":
            self.error_list.options.append(TextHolder("dialogs_error"))
        if self.error_list.options != []:
            self.error_list.options.append(TextHolder("defaulted_values"))

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings.
        """
        self.__init_menu__()
        self.display.startup(self.main_menu, self.error_list)

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting the main_menu
        attribute to save on memory usage.
        """
        self.display.mixer("option_activate")
        del self.main_menu
        self.display.cleanup()

    def leave_game(self) -> None:
        """Plays a sound and switches the Control's state to quit, efficiently
        quitting the program.
        """
        self.display.mixer("program_quit")
        pg.time.delay(240)
        self.switch_state("quit")

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Pass the event object down to the main_menu by calling its input_event
        method. If it returns "program_quit" or the return key is pressed,
        switches the current state to "quit", effectively leaving the program.
        """
        return_key: str = self.control.settings.key_config.return_key
        self.main_menu.get_event(*self.read_input_events(event), "vertical")
        if (event.type == pg.KEYDOWN and pg.key.name(event.key) == return_key):
            self.leave_game()

    def update(self) -> None:
        """Called after the events have been parsed, calls the draw and mixer
        Display methods.
        """
        self.display.menu_mixer([self.main_menu])
        self.display.draw()
