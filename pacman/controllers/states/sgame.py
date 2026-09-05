
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import Level, LevelOutput, ActivateOption, Spacer
from pacman.views import GameDisplay


class Player:
    def __init__(self, max_lives: int, cheats_allowed: bool) -> None:
        self.max_lives: int = max_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = False
        self.lives: int = max_lives
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}

    def regen_life(self, life_regen: int) -> None:
        self.lives += life_regen
        if self.lives > self.max_lives:
            self.lives = self.max_lives


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
        self.current_output: LevelOutput

    def __init_menues__(self) -> None:
        self.pause_menu = Menu(loop_cursor=False, options=[
            ActivateOption("resume", "{name}",
                           partial(self.change_game_state, "level")),
            ActivateOption("settings", "{name}",
                           partial(self.switch_state, "options_menu")),
            Spacer(),
            ActivateOption("back_to_main", "{name}",
                           partial(self.leave_game))
        ])
        self.level_end_menu = Menu()
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
            self.current_state = "level"
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
                self.pause_menu.get_event(event, action_key, "", "vertical")
            case "victory":
                pass
            case "defeat":
                pass
            case "end":
                pass

    def update(self) -> None:
        match self.current_state:
            case "level":
                level_output: LevelOutput | None = self.current_level.update()
                if level_output is not None:
                    self.current_output = level_output
                    self.current_state = (
                        "victory" if level_output.victorious is True
                        else "defeat")
            case "victory":
                pass
            case "defeat":
                pass
            case "end":
                pass
        self.display.draw(self.current_state)
