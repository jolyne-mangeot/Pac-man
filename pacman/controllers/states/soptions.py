
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
    def __init__(self, control: Control) -> None:
        State.__init__(self, control)
        self.settings: dict[str, Any]
        self.options_menu: Menu

    def __init_menu__(self) -> None:
        """
        """
        self.settings = self.control.settings.model_dump()
        dialogs: Dialogs = self.control.dialogs
        self.options_menu = Menu(
            self.control.screen, from_top=50,
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
        self.control.settings = Settings()
        self.settings["key_config"].update(KeyConfig().model_dump())
        self.settings.update(self.control.settings.model_dump())
        self.options_menu.pre_render_all_options()

    def apply_settings(self) -> None:
        self.control.settings = Settings(**self.settings)
        model_to_json(self.control.settings)
        self.cleanup()
        self.control.update_options()
        self.startup()

    def startup(self) -> None:
        self.__init_menu__()

    def cleanup(self) -> None:
        del self.options_menu
        del self.settings

    def get_event(self, event: pg.event.Event) -> None:
        return_key: str = self.control.settings.key_config.return_key
        if event.type == pg.KEYDOWN and event.unicode == return_key:
            return self.switch_state("main_menu")
        self.options_menu.get_event(
            self.control.settings.key_config,
            event, "chart")

    def update(self) -> None:
        self.options_menu.pre_render_option()
        self.draw()

    def draw(self) -> None:
        self.control.screen.fill((255, 255, 255))
        self.options_menu.draw_chart_options()
