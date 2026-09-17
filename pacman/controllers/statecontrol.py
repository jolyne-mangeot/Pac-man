
from abc import ABC, abstractmethod
from typing import cast, Any

import pygame as pg

from pacman.models import (
    JSONModel, Config, Settings, Highscores, Dialogs, generate_level_one,
    json_to_model, model_to_json, json_to_config_base, config_base_to_json)


pg.init()
pg.mixer.init(channels=4)


class Control:
    """Control class

    #### Description:
    Loads multiple json files (settings.json and a dialog file) and initiates
    every attribute necessary to Pygame such as the screen, the clock, the
    fps and delta_time values, as well as a dictionary of State objects for
    menu manipulating.

    ### Parameter:
    - config_path, leading to a config json file containing the game's preset
    data to use.

    ### Attributes:
    - config_base: dict[str, Any] => dict representing the configuration file
    parsed at the program's load-up
    - config: Config => Config object containing values to pass down to game
    related states
    - settings: Settings => Settings object reference to be accessed by states
    - dialogs: Dialogs => Dialog object reference to be accessed by states
    - screen: pg.Surface => screen Surface reference to be blit by states
    - interface: pg.Surface => interface onto which the program is displayed,
    useful to keep the right resolution in fullscreen mode
    - interface_rect: pg.Rect => contains set coordinates to display the
    interface
    - bgm_channel: pg.mixer.Channel => sound channels used by pygame to play
    background music
    - sfx_channel: pg.mixer.Channel => sound channels used by pygame to play
    sound effects
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
    - update_display => calls pygame functions related to the display based
    on the current settings
    - update_options => reloads the dialog and updates the screen to fit new
    settings from the Setting object
    - save_model => saves a JSONModel passed as argument in attributes and
    files
    - load_dialogs => loads up the dialog file with the json_to_model
    function and transforms it into a dict[str, str]
    - generate_config_from_base => from the config_base, instantiate the config
    attribute
    - reload_config => reload JSONModels objects and the config_base using the
    config_path
    - reset_config => reinitializes the config_base to default values, and
    saves it using the dedicated function.
    - set_up_states => updates the state_dict with the one given as argument
    - flip_state => Calls cleaning of the current state and setup of the
    new state
    - event_loop => check every event in the pg.event.get() queue and send them
    to the current state
    - update => called every run of the game_loop, calling the current state's
    update method
    - game_loop => runs a while loop on the done attribute and calls
    event_loop, update, updates the screen and the delta_time
    """
    def __init__(self, config_path: str) -> None:
        """Loads a Config object using the config_path argument and a Settings,
        Dialogs and Highscores objects consequently. Initiate all instance
        attributes either using Pygame modules or with default values.
        """
        self.config_path: str = config_path
        self.config: Config
        self.config_base: dict[str, Any]
        self.settings: Settings
        self.highscores: Highscores
        self.dialogs: dict[str, str]
        self.reload_config()

        self.screen: pg.Surface
        self.interface: pg.Surface = pg.Surface((1, 1))
        self.interface_rect: pg.Rect
        pg.display.set_icon(pg.image.load("pacman/assets/icon.png"))
        pg.display.set_caption(self.dialogs["title"])
        self.update_display()

        self.bgm_channel: pg.mixer.Channel = pg.mixer.Channel(0)
        self.bgm_channel.set_volume(self.settings.bgm_vol / 10)
        self.sfx_channel: pg.mixer.Channel = pg.mixer.Channel(1)
        self.sfx_channel.set_volume(self.settings.sfx_vol / 10)

        self.clock: pg.time.Clock = pg.time.Clock()
        self.delta_time: float
        self.fps: int = 60
        self.done: bool = False

        self.state_dict: dict[str, State]
        self.state_name: str
        self.current_state: State

    def update_display(self) -> None:
        """Updates the display with the newest settings.

        In windowed mode, the screen is scaled to the chosen resolution as
        well as the interface, which rect object is placed at coordinates 0,0.

        In fullscreen, the screen is scaled to cover the entire display, while
        the interface is scaled on the screen's height by a 4:3 factor. Its
        rect is centered by its middle-top point, placed at the center of the
        screen's width.
        """
        if self.settings.res.value == "fullscreen":
            self.screen = pg.display.set_mode(
                pg.display.get_desktop_sizes()[0], pg.FULLSCREEN)
            screen_height: int = self.screen.get_height()
            self.interface = pg.transform.scale(self.interface, (
                screen_height * 4 / 3, screen_height))
            self.interface_rect = self.interface.get_rect()
            self.interface_rect.midtop = (int(self.screen.get_width() / 2), 0)
        else:
            self.screen = pg.display.set_mode(self.settings.res.value)
            self.interface = pg.transform.scale(
                self.interface, self.settings.res.value)
            self.interface_rect = self.interface.get_rect()
            self.interface_rect.topleft = (0, 0)

    def update_options(self, new_settings: Settings) -> bool:
        """Updates Dialogs and screen attributes with updated settings.

        Calls json_to_model function again on Dialogs to reload them from
        file, update_display method to accord to new resolution settings and
        set new volumes for the sfx and bgm sound channels.
        """
        self.settings = new_settings
        save_output: bool = model_to_json(self.settings)
        self.load_dialogs()
        self.update_display()
        self.bgm_channel.set_volume(self.settings.bgm_vol / 10)
        self.sfx_channel.set_volume(self.settings.sfx_vol / 10)
        return save_output

    def save_model(self, config: JSONModel) -> bool:
        """Simply returns the model_to_json function with the given JSONModel
        object, keeping Control as the only class accessing external files.
        """
        setattr(self, config.__class__.__name__.lower(), config)
        return model_to_json(config)

    def load_dialogs(self) -> None:
        """For better access, the Dialog JSONModel is casted to dict[str, str]
        after being loaded if the language chosen isn't en-en.

        But to show file opening-related errors, the status attribute is
        added to the dict as a string, from a boolean.
        """
        if self.settings.lang.value == "en-en":
            self.dialogs = Dialogs(status=True).model_dump()
            self.dialogs["status"] = "True"
        else:
            dialogs: Dialogs = cast(Dialogs, json_to_model(
                Dialogs,
                "pacman/assets/dialogs/" + self.settings.lang.value + ".json"))
            self.dialogs = cast(dict[str, str], dialogs.model_dump())
            self.dialogs["status"] = str(dialogs.status)

    def generate_config_from_base(self) -> None:
        """Punctual method generating a new Config object as Control's
        attribute using the config_base loaded from the configuration file at
        the start of the program.
        """
        self.config = Config(**self.config_base)

    def reload_config(self) -> None:
        """Reloads all configuration files from the path passed as argument
        when the program started.
        """
        self.config_base = json_to_config_base(self.config_path)
        self.settings = cast(Settings, json_to_model(Settings))
        self.highscores = cast(Highscores, json_to_model(Highscores))
        self.load_dialogs()

    def reset_config(self) -> None:
        """Method dedicated to creating a base for randomized levels apart
        from the first one generated using the generate_level_one function.
        Saves this new config_base in the file at the config_path.
        """
        self.config_base = Config(
            status=True, levels=[generate_level_one()]).model_dump()
        self.config_base["levels"].extend([{}] * 9)
        self.config_base["status"] = config_base_to_json(
            self.config_base, self.config_path)

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

    def event_loop(self) -> None:
        """For loop running on each event in the pygame event queue. Checks for
        pygame.QUIT to switch the done attribute to True, then calls the
        current state's get_event method, passing down the current event.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.current_state.get_event(event)

    def update(self) -> None:
        """Check for state done bool attribute to calls its own update method
        or initialize a new state with flip_state.
        """
        if self.current_state.done:
            self.flip_state()
        self.current_state.update()

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

    #### Description:
    Parent of all state classes used to set-up game menues, which instances
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

    def back_a_state(self) -> None:
        """Acts the same as switch_state method, but instead of taking a state
        name in argument, uses the previous attribute of the calling state.
        """
        self.next = self.previous
        self.done = True

    def read_input_events(self, event: pg.event.Event) -> tuple[str, str, str]:
        """Based on a pygame event, parse three strings to return in a tuple
        for States to take actions upon.

        - named_key => if the event is pygame.KEYDOWN, recovers the literal
        name of the pressed key
        - text_input => if the event is pygame.TEXTINPUT, recovers the text
        attribute of the event
        - action_key => uses the named key to point out which action it calls
        based on the KeyConfig (up_key, confirm_key, etc.)
        """
        named_key: str = ""
        text_input: str = ""
        if event.type == pg.TEXTINPUT:
            text_input = event.text
        elif event.type == pg.KEYDOWN:
            named_key = pg.key.name(event.key)
        action_key: str = self.key_unicode_to_action(named_key)
        return (named_key, action_key, text_input)

    def key_unicode_to_action(self, input: str) -> str:
        """Takes a KeyConfig object and an input as string in arguments.

        Checks in the KeyConfig, which contains duos of pygame keys with their
        action, to find what action corresponds to the input key. Does so by
        looping on items in the dict version of the KeyConfig object by the
        model_dump BaseModel method.
        """
        for action, key in (
                self.control.settings.key_config.model_dump().items()):
            if key == input:
                return action
        return ""

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
