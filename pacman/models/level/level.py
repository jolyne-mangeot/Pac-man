
from typing import Any
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
    def __init__(
            self, player_lives: int, maze_config: MazeConfig,
            gameplay: GameplayConfig, scores_config: ScoresConfig) -> None:
        self.lives: int = player_lives
        self.level_duration: int = gameplay.timer
        self.level_timer: int = gameplay.timer
        self.super_mode: bool = False
        self.super_duration: int = gameplay.super_duration
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        self.map: Map = Map(**maze_config.model_dump())
        self.pacman: dict[str, Any] = {}
        self.ghosts: dict[str, dict[str, Any]]
        self.instantiate_ghosts(maze_config, gameplay)
        pg.time.set_timer(Timers.LEVEL.value, 1000, 1)

    def instantiate_ghosts(self, maze: MazeConfig,
                           config: GameplayConfig) -> None:
        positions: dict[str, tuple[int, int]] = {
            "Blinky": (0, 0),
            "Pinky": (maze.width - 1, 0),
            "Inky": (0, maze.height - 1),
            "Clyde": (maze.width - 1, maze.height - 1)}
        for name, pos in positions.items():
            if config.ghosts.get(name, None) is not None:
                new_ghost: dict[str, Any] = {
                    **config.ghosts[name].model_dump(), "initial_position": pos
                }
                if new_ghost["speed"] > 0:
                    new_ghost["speed"] = 2000 - (new_ghost["speed"] - 1) * 100
                if new_ghost["sup_speed"] > 0:
                    new_ghost["sup_speed"] = (
                        2000 - (new_ghost["sup_speed"] - 1) * 100)
                self.ghosts.update({name: new_ghost})
                pg.time.set_timer(Timers[name.upper()].value, 100, 1)

    def update_timer(self, name: str, entity: dict[str, Any]) -> None:
        speed: str = "sup_speed" if self.super_mode else "speed"
        pg.time.set_timer(
            Timers[name.upper()].value, getattr(entity, speed), 1)

    def move_pacman(self) -> None:
        self.pacman  # .move()
        if self.pacman["direction"].value == 0:
            pg.time.set_timer(Timers.PACMAN.value, 0)
        else:
            self.update_timer("pacman", self.pacman)

    def move_ghost(self, name: str) -> None:
        ghost: dict[str, Any] = self.ghosts[name]
        ghost  # .move()
        self.update_timer(name, ghost)

    def get_event(self, event: pg.event.Event, action_key: str) -> None:
        if event.type == pg.KEYDOWN:
            self.pacman  # .update_input(action_key)
            if self.pacman["direction"].value == 0:
                self.move_pacman()
        elif event.type == Timers.LEVEL.value:
            self.level_timer -= 1
        elif event.type == Timers.SUPER.value:
            self.super_mode = False
        elif event.type == Timers.PACMAN.value:
            if self.pacman["is_alive"] is True:
                self.move_pacman()
            else:
                self.pacman["is_alive"] = True
                self.pacman  # .respawn()
                for ghost in self.ghosts:
                    ghost  # .respawn()
        for name in self.ghosts.keys():
            if event.type == Timers[name.upper()].value:
                if self.ghosts[name]["is_alive"] is True:
                    self.move_ghost(name)
                else:
                    self.ghosts[name]["is_alive"] = True
                    self.update_timer(name, self.ghosts[name])

    def gain_score(self, type: str, amount: int) -> None:
        self.score += amount
        self.scores[type] += amount

    def activate_super(self) -> None:
        self.gain_score("sup_gum", self.scores_ref.sup_gum)
        self.super_mode = True
        pg.time.set_timer(Timers.SUPER.value, self.super_duration, 1)

    def update_entities(self) -> None:
        output: str = "none"  # self.map.update_gums(self.pacman.position)
        if output == "gum":
            self.gain_score("gum", self.scores_ref.gum)
        elif output == "sup_gum":
            self.activate_super()
        for name, ghost in self.ghosts.items():
            if ghost["position"] == self.pacman["position"]:
                if self.super_mode is False:
                    self.pacman["is_alive"] = False
                    self.lives -= 1
                    pg.time.set_timer(Timers.PACMAN.value, 2000, 1)
                else:
                    self.gain_score("ghost", self.scores_ref.ghost)
                    ghost["is_alive"] = False
                    pg.time.set_timer(
                        Timers[name.upper()].value, ghost["down_time"], 1)

    def update(self) -> None:
        if self.pacman["is_alive"] is True:
            self.update_entities()
        if self.level_timer == 0 or self.lives == 0:
            pass
        if self.map:  # .check_gum() is True:
            pass
