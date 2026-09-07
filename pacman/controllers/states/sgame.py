
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import (
    Level, LevelOutput, ActivateOption, Spacer, TextValueHolder)
from pacman.views import GameDisplay


class Player:
    def __init__(self, max_lives: int, cheats_allowed: bool) -> None:
        self.max_lives: int = max_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = False
        self.lives: int = max_lives
        self.playtime: int = 0
        self.current_score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}

    def regen_life(self, life_regen: int) -> None:
        self.lives += life_regen
        if self.lives > self.max_lives:
            self.lives = self.max_lives

    def update_with_output(self, output: LevelOutput) -> None:
        self.lives = output["lives"]
        if self.cheats_used is False:
            self.cheats_used = output["cheats_used"]
        self.playtime += output["time_taken"]
        self.current_score += output["score"]
        for key, value in output["scores"].items():
            self.scores[key] += value


class GameState(State):
    def __init__(self, control: Control) -> None:
        State.__init__(self, control)
        self.next = "main_menu"
        self.display: GameDisplay = GameDisplay(control)
        self.current_state: str = "level"
        self.pause_menu: Menu
        self.level_end_menu: Menu
        self.end_screen: Menu

        self.level_index: int = -1
        self.player: Player
        self.current_level: Level
        self.current_output: LevelOutput = {
            "victorious": True,
            "lives": 3,
            "cheats_used": False,
            "time_taken": 0,
            "score": 2000,
            "scores": {"gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}}

    def __init_menues__(self) -> None:
        self.pause_menu = Menu(loop_cursor=False, options=[
            ActivateOption("resume",
                           partial(self.change_game_state, "level")),
            ActivateOption("settings",
                           partial(self.switch_state, "options_menu")),
            Spacer(),
            ActivateOption("give_up",
                           partial(self.leave_game))])
        self.level_end_menu = Menu(loop_cursor=False, options=[
            TextValueHolder("time_taken", self.current_output),
            *[TextValueHolder(name, self.current_output["scores"])
              for name in self.current_output["scores"].keys()],
            Spacer(),
            TextValueHolder("score", self.current_output),
            TextValueHolder("current_score", self.player),
            Spacer(),
            ActivateOption("continue_next", partial(self.access_next_level))])
        self.end_screen = Menu()

    def change_game_state(self, state: str) -> None:
        self.current_state = state

    def leave_game(self) -> None:
        self.level_index = -1
        del self.pause_menu
        del self.level_end_menu
        del self.end_screen

        del self.player
        del self.current_level
        self.switch_state("main_menu")

    def startup(self) -> None:
        if self.level_index == -1:
            self.level_index = 0
            self.player = Player(self.control.config.player.lives_count,
                                 self.control.config.player.cheats_allowed)
            self.__init_menues__()
            self.display.startup(
                self.pause_menu, self.level_end_menu, self.end_screen)
            self.instantiate_level()
        else:
            self.__init_menues__()
            self.display.startup(
                self.pause_menu, self.level_end_menu, self.end_screen)
            self.display.update_level(self.current_level)

    def instantiate_level(self) -> None:
        self.player.regen_life(
            self.control.config.levels[self.level_index].gameplay.life_regen)
        self.current_level = Level(
            self.level_index + 1, self.player.max_lives,
            self.player.lives, self.player.cheats_allowed,
            self.control.config.levels[self.level_index].maze,
            self.control.config.levels[self.level_index].gameplay,
            self.control.config.levels[self.level_index].scores)
        self.display.update_level(self.current_level)
        self.current_state = "level"

    def update_output(self, level_output: LevelOutput) -> None:
        self.current_output["victorious"] = level_output["victorious"]
        self.current_output["lives"] = level_output["lives"]
        self.current_output["cheats_used"] = level_output["cheats_used"]
        self.current_output["time_taken"] = level_output["time_taken"]
        self.current_output["score"] = level_output["score"]
        self.current_output["scores"].update(level_output["scores"])

    def access_next_level(self) -> None:
        self.level_index += 1
        if (self.current_state == "victory"
                and self.level_index < len(self.control.config.levels)):
            self.instantiate_level()
        else:
            self.current_state = "end"

    def cleanup(self) -> None:
        self.display.cleanup()

    def get_event(self, event: pg.event.Event) -> None:
        action_key: str = ""
        if event.type == pg.KEYDOWN:
            action_key = self.key_unicode_to_action(pg.key.name(event.key))
        match self.current_state:
            case "level":
                if action_key == "return_key":
                    self.current_state = "pause"
                    action_key = ""
                self.current_level.get_event(event, action_key)
            case "pause":
                if action_key == "return_key":
                    self.change_game_state("level")
                elif event.type == pg.KEYDOWN:
                    self.pause_menu.get_event(
                        event.key, action_key, "", "vertical")
            case "victory" | "defeat":
                if event.type == pg.KEYDOWN:
                    self.level_end_menu.get_event(
                        event.key, action_key, "", "vertical")
            case "end":
                pass

    def update(self) -> None:
        if self.current_state == "level":
            level_output: LevelOutput | None = self.current_level.update()
            if level_output is not None:
                self.update_output(level_output)
                self.player.update_with_output(self.current_output)
                self.display.level_end_menu.pre_render_all_options(
                    self.control.dialogs)
                self.current_state = (
                    "victory" if level_output["victorious"] is True
                    else "defeat")
        self.display.draw(self.current_state)
