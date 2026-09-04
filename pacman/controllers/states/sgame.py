
import pygame as pg

from pacman.controllers import Control, State
from pacman.models import Level
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
        self.level_index: int
        self.player: Player
        self.current_level: Level

    def startup(self) -> None:
        self.level_index = 0
        self.player = Player(self.control.config.player.lives_count,
                             self.control.config.player.cheats_allowed)
        self.display.startup()
        self.instantiate_level()

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
        action_input: str = ""
        if event.type == pg.KEYDOWN:
            action_input = self.key_unicode_to_action(pg.key.name(event.key))
        self.current_level.get_event(event, action_input)

    def update(self) -> None:
        self.current_level.update()
        self.display.draw()
