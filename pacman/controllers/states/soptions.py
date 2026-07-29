
import pygame as pg
from functools import partial
from typing import Any

from pacman.controllers import (
    Control, State,
    Menu, ActivateOption, SliderOption, InputOption, SelectionOption)
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
                    self.settings, [res for res in Resolutions]),
                SliderOption(
                    "sfx_vol", f"{dialogs.sfx_vol:<20}""{value}",
                    self.settings, range(0, 11), 0, 0),
                SliderOption(
                    "bgm_vol", f"{dialogs.bgm_vol:<20}""{value}",
                    self.settings, range(0, 11), 0, 0),
                None, None,
                *[
                    InputOption(
                        key, f"{str(getattr(dialogs, key)) + ":":<20}"
                        "{value}", self.settings["key_config"], 1, True, False)
                    for key in ACTION_LIST],
                None, None,
                ActivateOption("reset", dialogs.reset_settings,
                               partial(self.reset_settings)),
                ActivateOption("apply", dialogs.apply,
                               partial(self.apply_settings)),
                ActivateOption("back", dialogs.back,
                               partial(self.switch_state, "main_menu"))])

    def reset_settings(self) -> None:
        self.control.settings = Settings()
        self.settings["key_config"].update(KeyConfig().model_dump())
        self.settings.update(self.control.settings.model_dump())
        self.options_menu.pre_render_all_options()
        self.apply_settings()

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
        if event.type == pg.KEYDOWN:
            if event.unicode == self.control.settings.key_config.return_key:
                return self.switch_state("main_menu")
            self.options_menu.get_event(
                self.control.settings.key_config,
                pg.key.name(event.key), "chart")

    def update(self) -> None:
        self.draw()

    def draw(self) -> None:
        self.control.screen.fill((255, 255, 255))
        self.options_menu.draw_chart_options()
