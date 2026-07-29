
import pygame as pg
from abc import ABC, abstractmethod
from typing import cast

from pacman.models import Settings, KeyConfig, Config, Dialogs, json_to_model


pg.init()


class Control:
    """Control class

    ### Argument:
    - config_path, leading to a config json file containing the game's preset
    data to use.

    Loads multiple json files (settings.json and a dialog file) and initiates
    every attribute necessary to Pygame such as the screen, the clock, the
    fps and delta_time values, as well as a dictionary of State objects for
    menu manipulating.

    ### Attributes:
    - config: Config => Config object containing values to pass down to game
    related states
    - settings: Settings => Settings object reference to be accessed by states
    - dialogs: Dialogs => Dialog object reference to be accessed by states
    - screen: pg.Surface => screen Surface reference to be blit by states
    - screen_rect: pg.Rect => contains dimension informations about the screen
    - clock: pg.time.Clock => time reference to calcultate delta_time and
    adapt all timed events to accustom to latency issues
    - delta_time: float => time passed between two run of the game loop for
    animation delays
    - fps: int => amount of frames per seconds used as reference by the clock
    to generate a delta_time
    - done: bool => boolean used by the game loop to run until this attribute
    is set to False
    - state_dict: dict[str, State] => dict containing all the game States like
    the main menu, the options menu, etc.
    - state_name: str => name of the current state in the state_dict to find
    it more easily
    - current_state: State => current State of the game from the state_dict to
    access it as an attribute

    ### Methods:
    - update_options => reloads the dialog and updates the screen to fit new
    settings from the Setting object
    - set_up_states => Updates the state_dict with the one given as argument
    - flip_state => Calls cleaning of the current state and setup of the
    new state
    - update => called every run of the game_loop, calling the current state's
    update method
    - event_loop => check every event in the pg.event.get() queue and send them
    to the current state
    - game_loop => runs a while loop on the done attribute and calls
    event_loop, update, updates the screen and the delta_time
    """
    def __init__(self, config_path: str) -> None:
        """Loads a Config object using the config_path argument and a Settings
        and Dialogs objects consequently. Initiate all instance attributes
        either using Pygame modules or with default values.
        """
        self.config: Config = cast(Config, json_to_model(Config, config_path))
        self.settings: Settings = cast(Settings, json_to_model(
            Settings, extra_args={"key_config": json_to_model(
                KeyConfig, sub_dict="key_config")}))
        self.dialogs: Dialogs = cast(Dialogs, json_to_model(
            Dialogs,
            "pacman/assets/dialogs/" + self.settings.lang.value + ".json"))

        self.screen: pg.Surface = self.update_display()
        self.screen_rect: pg.Rect = self.screen.get_rect()
        self.clock: pg.time.Clock = pg.time.Clock()
        self.delta_time: float
        self.fps: int = 30
        self.done: bool = False

        self.state_dict: dict[str, State]
        self.state_name: str
        self.current_state: State

    def update_display(self) -> pg.Surface:
        """Returns the call of pygame.display.set_mode with the resolution
        from the settings attribute. It this attribute contains "fullscreen"
        as a value, insert the pygame.FULLSCREEN flag to set_mode.
        """
        if self.settings.res.value == "fullscreen":
            return pg.display.set_mode(pg.display.get_desktop_sizes()[0],
                                       pg.FULLSCREEN)
        else:
            return pg.display.set_mode(self.settings.res.value)

    def update_options(self) -> None:
        """Updates Dialogs and screen attributes with updated settings.

        Calls json_to_model function again on Dialogs to reload them from
        file, update_display method to accord to new resolution settings.
        """
        self.dialogs = cast(Dialogs, json_to_model(
            Dialogs,
            "pacman/assets/dialogs/" + self.settings.lang.value + ".json"))
        self.update_display()
        self.screen_rect = self.screen.get_rect()

    def set_up_states(self, state_dict: dict[str, State]) -> None:
        """Takes a dict of State objects given by the main function of the
        program. Updates all states related attributes and calls startup on
        the current state (set to main_menu).
        """
        self.state_dict = state_dict
        self.state_name = "main_menu"
        self.current_state = self.state_dict[self.state_name]
        self.current_state.startup()

    def flip_state(self) -> None:
        """Make all necessary changes to attributes to cleanup a state
        and startup another.

        Reset to False the done attribute of the state that is done running
        and saves its name in a previous string, while the state_name control
        attribute is set to the next value of the current state.
        Calls its cleanup and switch current_state to the value in state_dict
        based on the new name. Calls its startup, and gives it as attribute
        the previous string, if ever needed.
        """
        self.current_state.done = False
        previous: str
        previous, self.state_name = self.state_name, self.current_state.next
        self.current_state.cleanup()
        self.current_state = self.state_dict[self.state_name]
        self.current_state.startup()
        self.current_state.previous = previous

    def update(self) -> None:
        """Check for state done bool attribute to calls its own update method
        or initialize a new state with flip_state.
        """
        if self.current_state.done:
            self.flip_state()
        self.current_state.update()

    def event_loop(self) -> None:
        """For loop running on each event in the pygame event queue. Checks for
        pygame.QUIT to switch the done attribute to True, then calls the
        current state's get_event method, passing down the current event.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            if event.type == pg.KEYDOWN:
                print(pg.key.name(event.key), end="", flush=True)
            self.current_state.get_event(event)

    def game_loop(self) -> None:
        """Runs while the done attribute is False.

        Calculates delta_time to estimate time since last loop iteration, then
        the event_loop control method, update, and finally flips the display,
        updating visual changes in the surface.
        """
        while not self.done:
            self.delta_time = self.clock.tick(self.fps) / 1000
            self.event_loop()
            self.update()
            pg.display.flip()


class State(ABC):
    """Abstract class State

    Parent of all state classes used to setp-up game menues, which instances
    are held by control to smoothly switch between them, update them and give
    them all pertinent information.

    ### Attributes:
    - control: Control (argument) => Control object containing all game related
    data such as settings and dialogs
    - done: bool => Boolean stating if the state is done running, reset to
    False by Control
    - next: str => String containing the name of the state to activate when
    the current one is done
    - previous: str => String containing the name of the last running state for
    general purposes (ex: back button)

    ### Methods:
    - switch_state => updates next attribute with string given as argument and
    set done to True. "quit" turns the control's done to True instead.
    - startup (abstract) => method called by control when a state is activated
    - cleanup (abstract) => method called by control when a state is
    deactivated
    <u>Runtime methods:</u>
    - get_event (abstract) => called to pass down events from control, to
    handle the player's input
    - update (abstract) => called to update any state data or calculation after
    the pygame events have been parsed
    - draw (abstract) => called to display everything the states needs to
    """
    def __init__(self, control: Control) -> None:
        """Takes control as attribute and initialize done, next and previous"""
        self.control: Control = control
        self.done: bool = False
        self.next: str
        self.previous: str

    def switch_state(self, new_state: str) -> None:
        """Takes a new_state string to update next attribute with, and toggles
        the done attribute value to True. If new_state is "quit", toggles the
        control's done attribute to True instead.
        """
        if new_state == "quit":
            self.control.done = True
            return
        self.next = new_state
        self.done = True

    @abstractmethod
    def startup(self) -> None:
        """Called by control when the state is waken to initialize all needed
        attributes or variables.
        """

    @abstractmethod
    def cleanup(self) -> None:
        """Called by control when the state is done to clean up attributes
        and call necessary methods for state shut down
        """
        pass

    @abstractmethod
    def get_event(self, event: pg.event.Event) -> None:
        """Called by control to pass down pygame events one by one to be
        handled by the state directly depending on its behavior.
        """

    @abstractmethod
    def update(self) -> None:
        """Called by control after each event from the pygame event queue has
        been handled to update the state's data based on the new information,
        or at least each frame.
        """

    @abstractmethod
    def draw(self) -> None:
        """Called by control after the events and updates have been handled for
        the state to call its own display methods.
        """
