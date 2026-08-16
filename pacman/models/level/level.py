
from enum import IntEnum

import pygame as pg

from pacman.models import MazeConfig, GameplayConfig, ScoresConfig, Map


class Timers(IntEnum):
    LEVEL = pg.USEREVENT + 0
    SUPER = pg.USEREVENT + 1
    PACMAN = pg.USEREVENT + 2
    BLINKY = pg.USEREVENT + 3
    PINKY = pg.USEREVENT + 4
    INKY = pg.USEREVENT + 5
    CLYDE = pg.USEREVENT + 6


class Level:
    def __init__(self, maze_config: MazeConfig, gameplay: GameplayConfig,
                 scores_config: ScoresConfig) -> None:
        self.level_duration: int = gameplay.timer
        self.level_timer: int = gameplay.timer
        self.super_mode: bool = False
        self.super_duration: int = gameplay.super_duration
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        self.map: Map = Map(**maze_config.model_dump())
        self.pacman: dict[str, str] = {}
        pg.time.set_timer(Timers.LEVEL.value, 1000, 1)

    def move_pacman(self) -> None:
        self.pacman  # .move()
        output: str = "none"  # self.map.check_gums(self.pacman.position)
        if output == "gum":
            self.score += self.scores_ref.gum
            self.scores["gum"] += self.scores_ref.gum
        elif output == "sup_gum":
            self.score += self.scores_ref.sup_gum
            self.scores["sup_gum"] += self.scores_ref.sup_gum
            self.super_mode = True
            pg.time.set_timer(Timers.SUPER.value, self.super_duration, 1)

    def get_event(self, event: pg.event.Event, action_key: str) -> None:
        if event.type == pg.KEYDOWN:
            self.pacman  # .update_input(action_key)
            if self.pacman:  # .direction == Directions.NONE
                self.move_pacman()
        elif event.type == Timers.LEVEL.value:
            self.level_timer -= 1
        elif event.type == Timers.PACMAN.value:
            self.move_pacman()

    def update(self) -> None:
        if self.level_timer == 0:
            pass
