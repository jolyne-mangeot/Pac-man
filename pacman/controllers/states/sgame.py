
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import (
    Level, LevelOutput, Highscores, Score,
    ActivateOption, Spacer, TextHolder, TextValueHolder, InputOption)
from pacman.views import GameDisplay


class Player:
    def __init__(self, player_name: str, max_lives: int, cheats_allowed: bool
                 ) -> None:
        self.player_name: str = player_name
        self.max_lives: int = max_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = True
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
        self.menues: dict[str, tuple[Menu, str]]

        self.level_reached: int = -1
        self.player_name: str = "Player"
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
        pause_menu = Menu(loop_cursor=False, options=[
            ActivateOption("resume", partial(self.change_game_state, "level")),
            ActivateOption("settings",
                           partial(self.switch_state, "options_menu")),
            Spacer(), ActivateOption("give_up", partial(self.leave_game))])
        level_end_menu = Menu(loop_cursor=False, options=[
            TextValueHolder("time_taken", self.current_output),
            *[TextValueHolder(name, self.current_output["scores"])
              for name in self.current_output["scores"].keys()], Spacer(),
            TextValueHolder("score", self.current_output),
            TextValueHolder("current_score", self.player), Spacer(),
            ActivateOption("continue_next", partial(self.access_next_level))])
        end_screen = Menu(loop_cursor=False, options=[
            TextHolder("run_end"), TextValueHolder("level_reached", self),
            TextValueHolder("playtime", self.player),
            *[TextValueHolder(name, self.player.scores)
                for name in self.player.scores.keys()], Spacer(),
            TextValueHolder("current_score", self.player),
            InputOption("player_name", self.player, 10,
                        char_checker=lambda s: s.isalnum()),
            ActivateOption("save_score", partial(self.save_score)),
            ActivateOption("end_run", partial(self.leave_game))])
        self.menues = {
            "pause": (pause_menu, "vertical"),
            "victory": (level_end_menu, "vertical"),
            "defeat": (level_end_menu, "vertical"),
            "end": (end_screen, "vertical")}

    def startup(self) -> None:
        if self.level_reached == -1:
            self.level_reached = 0
            self.player = Player(
                self.player_name, self.control.config.player.lives_count,
                self.control.config.player.cheats_allowed)
            self.__init_menues__()
            self.display.startup(self.menues)
            self.instantiate_level()
        else:
            self.__init_menues__()
            self.display.startup(self.menues)
            self.display.update_level(self.current_level)

    def change_game_state(self, state: str) -> None:
        self.current_state = state

    def save_score(self) -> None:
        self.control.highscores = Highscores(
            scores=self.control.highscores.scores + [Score(
                player=self.player.player_name,
                score=self.player.current_score,
                level_reached=self.level_reached,
                time_taken=self.player.playtime,
                remaining_lives=self.player.lives)])
        if self.control.update_highscores() is True:
            self.menues["end"][0].options[10] = TextHolder("score_saved")
            self.menues["end"][0].select_index = 11
            self.display.menu_renders["end"][0].pre_render_option(
                self.control.dialogs, 10)

    def leave_game(self) -> None:
        self.level_reached = -1
        del self.menues

        del self.player
        del self.current_level
        self.switch_state("main_menu")

    def cleanup(self) -> None:
        self.display.cleanup()

    def instantiate_level(self) -> None:
        self.player.regen_life(
            self.control.config.levels[self.level_reached].gameplay.life_regen)
        self.current_level = Level(
            self.level_reached + 1, self.player.max_lives,
            self.player.lives, self.player.cheats_allowed,
            self.control.config.levels[self.level_reached].maze,
            self.control.config.levels[self.level_reached].gameplay,
            self.control.config.levels[self.level_reached].scores)
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
        self.level_reached += 1
        if (self.current_state == "victory"
                and self.level_reached < len(self.control.config.levels)):
            self.instantiate_level()
        else:
            self.access_run_end()

    def access_run_end(self) -> None:
        self.current_state = "end"
        if self.player.cheats_used is True:
            self.menues["end"][0].options[10] = TextHolder("cheats_used")
            self.display.menu_renders["end"][0].pre_render_option(
                self.control.dialogs, 10)

    def get_event(self, event: pg.event.Event) -> None:
        inputs: tuple[str, str, str] = self.read_input_events(event)
        if self.current_state == "level":
            if inputs[1] == "return_key":
                self.change_game_state("pause")
                return
            self.current_level.get_event(event, inputs[1])
        elif self.current_state == "pause":
            if inputs[1] == "return_key":
                self.change_game_state("level")
        if self.current_state in self.menues.keys():
            menu: tuple[Menu, str] = self.menues[self.current_state]
            menu[0].get_event(*self.read_input_events(event), menu[1])

    def update(self) -> None:
        if self.current_state == "level":
            level_output: LevelOutput | None = self.current_level.update()
            if level_output is not None:
                self.update_output(level_output)
                self.player.update_with_output(self.current_output)
                self.display.update_level_output(self.current_output)
                self.current_state = (
                    "victory" if level_output["victorious"] is True
                    else "defeat")
        self.display.draw(self.current_state)
