
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import TextHolder, ActivateOption
from pacman.views import InstructionsMenuDisplay


class InstructionsMenuState(State):
    """Class InstructionsMenuState, subclass of State

    #### Description:
    Organizes and renders the saved highscores to be browsed or reset by the
    player.

    ### Attributes:
    - *State instance parameters and attributes*
    - display: InstructionsMenuDisplay => Display class to handle the state's
    rendering
    - highscore_title: Menu => Menu containing a TextHolder to display the
    menu's name
    - highscore_index: Menu => Menu containing a TextValueHolder to show the
    placement of the currently viewed highscore
    - highscore_list: Menu => Menu containing all highscores to be displayed
    with their corresponding values
    - reset_menu: Menu => Menu enabling the user to leave the highscores menu
    or reset them
    - index: int => index to show the placement of the currently viewed
    highscore

    ### Methods
    - *State instance methods*
    - init_menu => instantiates all Menu attributes with set values and options
    - startup => initializes the menues and pass them down to the Display
    - cleanup => deletes all menues and calls the display's cleanup method
    - reset_highscores => reset Control's highscore attributes to an empty
    one, and calls its score saving method to reset all highscores
    - get_event => recovers pygame events and send them down to the highscore
    list and reset menues
    - update => updates the index attribute, and calls the display's draw
    method
    """
    def __init__(self, control: Control) -> None:
        """Initialize the menu with State's init, taking a Control object
        as argument, and multiple self-attributed menues and an index to browse
        the saved highscores.
        """
        State.__init__(self, control)
        self.display: InstructionsMenuDisplay = InstructionsMenuDisplay(
            self.control)
        self.instructions_menu: Menu

        self.index: int = 1

    def __init_menu__(self) -> None:
        """Gives values to all Menu attributes with set values and options for
        the state to function correctly. Takes into account the possibility
        of there being no highscore to display.
        """
        self.instructions_menu = Menu([
            TextHolder("instructions_menu", static_style="picked"),
            ActivateOption("back", partial(self.back_a_state))])

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings, then pass them down to the display.
        """
        self.__init_menu__()
        self.display.startup(self.instructions_menu)

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting all Menu objects and
        calling the display's cleanup method
        """
        self.display.mixer("option_activate")
        del self.instructions_menu
        self.display.cleanup()

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Parse the event to recover the user's input if any, and pass them down
        to the highscore list and reset menues.
        """
        inputs: tuple[str, str, str] = self.read_input_events(event)
        if inputs[1] == "return_key":
            self.back_a_state()
        self.instructions_menu.get_event(*inputs, "vertical")

    def update(self) -> None:
        """Called after the events have been parsed, calls the draw and mixer
        Display methods. Updates the index attribute with the select_index
        of the highscore_list.
        """
        self.display.menu_mixer([self.instructions_menu])
        self.display.draw()
