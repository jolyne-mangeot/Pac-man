
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import (
    TextHolder, TextValueHolder, ActivateOption, Highscores)
from pacman.views import HighscoresMenuDisplay


class HighscoresMenuState(State):
    """Class HighscoresMenuState, subclass of State

    #### Description:
    Organizes and renders the saved highscores to be browsed or reset by the
    player.

    ### Attributes:
    - *State instance parameters and attributes*
    - display: HighscoresMenuDisplay => Display class to handle the state's
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
        self.display: HighscoresMenuDisplay = HighscoresMenuDisplay(
            self.control)
        self.highscore_title: Menu
        self.highscore_index: Menu
        self.highscore_list: Menu
        self.reset_menu: Menu

        self.index: int = 1

    def __init_menu__(self) -> None:
        """Gives values to all Menu attributes with set values and options for
        the state to function correctly. Takes into account the possibility
        of there being no highscore to display.
        """
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

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings, then pass them down to the display.
        """
        self.__init_menu__()
        self.display.startup(
            self.highscore_title, self.highscore_index,
            self.highscore_list, self.reset_menu)

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting all Menu objects and
        calling the display's cleanup method
        """
        self.display.mixer("option_activate")
        del self.highscore_title
        del self.highscore_index
        del self.highscore_list
        del self.reset_menu
        self.display.cleanup()

    def reset_highscores(self) -> None:
        """Reinitialize Control's highscore attribute to one made with no
        argument, creating an empty list of scores. When done, calls Control's
        highscore saving method, and startup this state again to update the
        menues accordingly.
        """
        if self.control.highscores.scores == []:
            return
        self.control.highscores = Highscores()
        self.cleanup()
        self.control.update_highscores()
        self.startup()

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Parse the event to recover the user's input if any, and pass them down
        to the highscore list and reset menues.
        """
        inputs: tuple[str, str, str] = self.read_input_events(event)
        if inputs[1] == "return_key":
            self.switch_state("main_menu")
        self.highscore_list.get_event(*inputs, "vertical")
        self.reset_menu.get_event(*inputs, "horizontal")

    def update(self) -> None:
        """Called after the events have been parsed, calls the draw and mixer
        Display methods. Updates the index attribute with the select_index
        of the highscore_list.
        """
        self.index = self.highscore_list.select_index // 5 + 1
        self.display.menu_mixer([self.highscore_list, self.reset_menu])
        self.display.draw()
