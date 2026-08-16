
from functools import partial
from typing import Any

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import (
    model_to_json, Option,
    Spacer, ActivateOption, SliderOption, InputOption, SelectionOption,
    Settings, KeyConfig, Languages, Resolutions, ACTION_LIST)
from pacman.views import OptionsMenuDisplay


class OptionsMenuState(State):
    """Class OptionsMenu, subclass of State

    Represents the settings menu of the game, initializing a Menu object to
    navigate different options: Language, Resolution, SFX and BGM volumes and
    keybindings. Can also reset and apply new settings.

    ### Attributes:
    - *State instance parameters and attributes*
    - settings: dict[str, Any] => Used to store the currently modified values
    and pass them down by reference to each option of the options_menu
    - options_menu: Menu => Menu object used to navigate options and display
    them

    ### Methods
    - *State instance methods*
    - init_menu => instantiate the Menu object into the options_menu attribute
    with set parameters
    - reset_settings => updates the settings dict with default values by
    initializing a new Settings and KeyConfig object, then rerender all options
    - apply_settings => updates the control's settings object with a new one
    created from the settings dict, discarding any invalid arguments, then
    calls cleanup, control's update_options and startup to apply this settings
    - startup (override) => calls init_menu to initialize navigation
    - cleanup (override) => deletes the options_menu and settings attributes
    to save memory
    - get_event (override) => check if the return_key has been pressed to
    return to the main menu, otherwise pass down the pygame event received
    to options_menu's input_event method
    - update (override) => calls the pre_render_option Menu method to
    update the currently picked option's visual and keep with the user's
    changes, then draw
    - draw (override) => displays all visual elements, namely the background
    and the options_menu with the dedicated method
    """
    def __init__(self, control: Control) -> None:
        """Initialize the menu with State's init, taking a Control object
        as argument, and a self attributed variable options_menu of type Menu
        to handle navigation and program flow, and a settings dict of any type
        to hold the setting values that can be modified by the user.
        """
        State.__init__(self, control)
        self.display: OptionsMenuDisplay = OptionsMenuDisplay(self.control)
        self.display.load_main_menues()
        self.settings: dict[str, Any]
        self.options_menu: Menu

    def __init_menu__(self) -> None:
        """Instantiate the settings dict from the control's settings object and
        the options_menu attribute with set parameters, selecting
        elements from the dialogs dict of control.
        """
        self.settings = self.control.settings.model_dump()
        options: list[Option] = [
            SelectionOption(
                "lang", "{name}:", self.settings,
                [str(lang) for lang in Languages]),
            SelectionOption(
                "res", "{name}:", self.settings, cycle=False,
                options=[res for res in Resolutions]),
            SliderOption(
                "sfx_vol", "{name}:",
                self.settings, range(0, 11), 0, 0, cycle=False),
            SliderOption(
                "bgm_vol", "{name}:",
                self.settings, range(0, 11), 0, 0, cycle=False),
            Spacer(), Spacer(), *[
                InputOption(
                    key, "{name}:",
                    self.settings["key_config"], 1, False, True, False,
                    excluded_input=["return", "escape", "backspace"]
                ) for key in ACTION_LIST],
            Spacer(), Spacer(),
            ActivateOption("reset_settings", "{name}",
                           partial(self.reset_settings), "option_update"),
            ActivateOption("apply", "{name}", partial(self.apply_settings)),
            ActivateOption("back", "{name}",
                           partial(self.switch_state, "main_menu"))]

        self.options_menu = Menu(loop_cursor=False, options=options)

    def reset_settings(self) -> None:
        """Updates the settings dict that's being modified by the user's inputs
        with one made from blank KeyConfig and Settings objects to reset all
        values, then rerender all options_menu visuals with the dedicated
        method.
        """
        self.settings["key_config"].update(KeyConfig().model_dump())
        self.settings.update(Settings().model_dump())
        self.display.menu_render.pre_render_all_options(self.control.dialogs)

    def apply_settings(self) -> None:
        """Updates the control's settings object with one made from the
        settings dict, checking all values and defaulting them to safe values
        if needed.

        Save these settings in the dedicated json file with the model_to_json
        function, then call cleanup, control's update and startup to
        effectively apply the new settings.
        """
        self.control.settings = Settings(**self.settings)
        model_to_json(self.control.settings)
        self.cleanup()
        self.control.update_options()
        self.startup()
        self.display.mixer("option_activate")

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings.
        """
        self.__init_menu__()
        self.display.startup(self.options_menu)

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting the options_menu and
        settings attributes to save on memory usage.
        """
        self.display.mixer("cursor_unpick")
        self.display.cleanup()
        del self.options_menu
        del self.settings

    def get_event(self, event: pg.event.Event) -> None:
        """Takes a pygame Event object as argument.

        Checks if the return_key was pressed by comparing the event with the
        key_config from State attributes to switch state to the main menu, and
        otherwise pass the event object down to the options_menu by calling its
        input_event method.
        """
        return_key: str = self.control.settings.key_config.return_key
        if (self.options_menu.picked_index == -1 and event.type == pg.KEYDOWN
                and pg.key.name(event.key) == return_key):
            self.switch_state("main_menu")
            return
        self.options_menu.get_event(
            *self.read_input_events(event), "chart")

    def update(self) -> None:
        """Called after the events have been parsed, rerender all options in
        the options_menu object to keep up with the user's changes, then call
        the draw and mixer Display methods.
        """
        self.display.menu_render.pre_render_option(self.control.dialogs)
        self.display.mixer(self.options_menu.action_done)
        self.display.draw()
        self.options_menu.action_done = ""
