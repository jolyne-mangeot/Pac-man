
from enum import IntEnum

import pygame as pg

from pacman.models import MazeConfig, GameplayConfig, ScoresConfig


class Timers(IntEnum):
    LEVEL = 0
    SUPER = 1
    PACMAN = 2
    BLINKY = 3
    PINKY = 4
    INKY = 5
    CLYDE = 6


class Level:
    def __init__(self, maze_config: MazeConfig, gameplay: GameplayConfig,
                 scores_config: ScoresConfig) -> None:
        self.super_duration: int = gameplay.super_duration
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        pg.time.set_timer(0, gameplay.timer)
