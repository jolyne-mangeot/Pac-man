
import pygame as pg
from functools import partial
from typing import Any

from pacman.controllers import (
    Control, State,
    Menu, Spacer, ActivateOption, SliderOption, InputOption, SelectionOption)
from pacman.models import (
    model_to_json,
    Dialogs, Settings, KeyConfig, Languages, Resolutions, ACTION_LIST)


class OptionsMenu(State):
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
        self.settings: dict[str, Any]
        self.options_menu: Menu

    def __init_menu__(self) -> None:
        """Instantiate the settings dict from the control's settings object and
        the options_menu attribute with set parameters, selecting
        elements from the dialogs dict of control.
        """
        self.settings = self.control.settings.model_dump()
        dialogs: Dialogs = self.control.dialogs
        self.options_menu = Menu(
            self.control.screen, loop_cursor=False, from_top=50,
            from_left=int(self.control.screen.get_width() / 4), options=[
                SelectionOption(
                    "lang", f"{dialogs.lang:<20}""{value}",
                    self.settings, [lang for lang in Languages]),
                SelectionOption(
                    "res", f"{dialogs.res:<20}""{value}",
                    self.settings, [res for res in Resolutions], cycle=False),
                SliderOption(
                    "sfx_vol", f"{dialogs.sfx_vol:<20}""{value}",
                    self.settings, range(0, 11), 0, 0, cycle=False),
                SliderOption(
                    "bgm_vol", f"{dialogs.bgm_vol:<20}""{value}",
                    self.settings, range(0, 11), 0, 0, cycle=False),
                Spacer(), Spacer(), *[
                    InputOption(
                        key, f"{str(getattr(dialogs, key)) + ":":<20}"
                        "{value}", self.settings["key_config"], 1,
                        False, True, False,
                        excluded_input=("return", "escape", "backspace")
                    ) for key in ACTION_LIST],
                Spacer(), Spacer(),
                ActivateOption("reset", dialogs.reset_settings,
                               partial(self.reset_settings)),
                ActivateOption("apply", dialogs.apply,
                               partial(self.apply_settings)),
                ActivateOption("back", dialogs.back,
                               partial(self.switch_state, "main_menu")),
                InputOption(
                    "haha", f"{"haha:":<10}""{value}",
                    self.settings, 15, input_require_return=False,
                    char_checker=lambda _: True)
                ])

    def reset_settings(self) -> None:
        """Updates the settings dict that's being modified by the user's inputs
        with one made from blank KeyConfig and Settings objects to reset all
        values, then rerender all options_menu visuals with the dedicated
        method.
        """
        self.settings["key_config"].update(KeyConfig().model_dump())
        self.settings.update(Settings().model_dump())
        self.options_menu.pre_render_all_options()

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

    def startup(self) -> None:
        """Called when the state is awaken, calls init_menu to keep the options
        up with the settings.
        """
        self.__init_menu__()

    def cleanup(self) -> None:
        """Called when the state is deactivated, deleting the options_menu and
        settings attributes to save on memory usage.
        """
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
        if event.type == pg.KEYDOWN and event.unicode == return_key:
            return self.switch_state("main_menu")
        self.options_menu.get_event(
            self.control.settings.key_config,
            event, "chart")

    def update(self) -> None:
        """Called after the events have been parsed, rerender all options in
        the options_menu object to keep up with the user's changes, then call
        the draw method.
        """
        self.options_menu.pre_render_option()
        self.draw()

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((255, 255, 255))
        self.options_menu.draw_chart_options()
