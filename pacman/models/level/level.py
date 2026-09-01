
from enum import IntEnum

import pygame as pg

from pacman.models import (
    Entity, Pacman, Ghost, MazeConfig, GameplayConfig, ScoresConfig, Map)


class Timers(IntEnum):
    LEVEL = pg.USEREVENT + 0
    SUPER = pg.USEREVENT + 1
    PACMAN = pg.USEREVENT + 2
    BLINKY = pg.USEREVENT + 3
    PINKY = pg.USEREVENT + 4
    INKY = pg.USEREVENT + 5
    CLYDE = pg.USEREVENT + 6
    ANIMATIONS = pg.USEREVENT + 7


class Level:
    def __init__(
            self, player_lives: int, cheats_allowed: bool,
            maze_config: MazeConfig, gameplay: GameplayConfig,
            scores_config: ScoresConfig) -> None:
        self.lives: int = player_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = False
        self.theme: str = gameplay.theme
        self.level_duration: int = gameplay.timer
        self.level_timer: int = gameplay.timer
        self.super_mode: bool = False
        self.super_duration: int = gameplay.super_duration
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        self.map: Map = Map(**maze_config.model_dump())
        self.map.super_gum_placement()
        self.map.simple_gum_placement()
        self.pacman: Pacman = Pacman(
            gameplay.pac_man_speed, gameplay.super_pac_man_speed,
            ((maze_config.width - 1) // 2, (maze_config.height - 1) // 2))
        self.ghosts: dict[str, Ghost] = {}
        self.anim_tick: int = 0
        self.instantiate_ghosts(maze_config, gameplay)
        pg.time.set_timer(Timers.LEVEL.value, 1000, 1)
        pg.time.set_timer(Timers.ANIMATIONS.value, 333)

    def instantiate_ghosts(self, maze: MazeConfig,
                           config: GameplayConfig) -> None:
        positions: dict[str, tuple[int, int]] = {
            "Blinky": (0, 0),
            "Pinky": (maze.width - 1, 0),
            "Inky": (0, maze.height - 1),
            "Clyde": (maze.width - 1, maze.height - 1)}
        for name, pos in positions.items():
            if config.ghosts.get(name, None) is not None:
                new_ghost: Ghost = Ghost(
                    **config.ghosts[name].model_dump(),
                    initial_pos=pos, maze=self.map)
                if new_ghost.speed > 0:
                    new_ghost.speed = 2000 - (new_ghost.speed - 1) * 100
                if new_ghost.super_speed > 0:
                    new_ghost.super_speed = (
                        2000 - (new_ghost.super_speed - 1) * 100)
                self.ghosts.update({name: new_ghost})
                pg.time.set_timer(Timers[name.upper()].value, 100, 1)

    def update_timer(self, name: str, entity: Entity) -> None:
        speed: str = "sup_speed" if self.super_mode else "speed"
        pg.time.set_timer(
            Timers[name.upper()].value, getattr(entity, speed), 1)

    def move_pacman(self) -> None:
        self.pacman.move(self.map.get_cell(self.pacman.pos).walls)
        if self.pacman.direction.value == 0:
            pg.time.set_timer(Timers.PACMAN.value, 0)
        else:
            self.update_timer("pacman", self.pacman)

    def move_ghost(self, name: str) -> None:
        ghost: Ghost = self.ghosts[name]
        if self.super_mode is True:
            ghost.chase(self.pacman.pos)
        else:
            ghost.escape(self.pacman.pos)
        self.update_timer(name, ghost)

    def get_event(self, event: pg.event.Event, action_key: str) -> None:
        if event.type == pg.KEYDOWN:
            self.pacman.update_user_input(action_key)
            if self.pacman.direction.value == 0:
                self.move_pacman()
        elif event.type == Timers.LEVEL.value:
            self.level_timer -= 1
        elif event.type == Timers.SUPER.value:
            self.super_mode = False
        elif event.type == Timers.PACMAN.value:
            if self.pacman.is_alive is True:
                self.move_pacman()
            else:
                self.pacman.is_alive = True
                self.pacman.respawn()
                for ghost in self.ghosts.values():
                    ghost.respawn()
        elif event.type == Timers.ANIMATIONS.value:
            self.anim_tick = (self.anim_tick + 1) % 3
        for name in self.ghosts.keys():
            if event.type == Timers[name.upper()].value:
                if self.ghosts[name].is_alive is True:
                    self.move_ghost(name)
                else:
                    self.ghosts[name].is_alive = True
                    self.update_timer(name, self.ghosts[name])

    def gain_score(self, type: str, amount: int) -> None:
        self.score += amount
        self.scores[type] += amount

    def activate_super(self) -> None:
        self.gain_score("sup_gum", self.scores_ref.sup_gum)
        self.super_mode = True
        pg.time.set_timer(Timers.SUPER.value, self.super_duration, 1)

    def update_entities(self) -> None:
        output: str = self.map.update_gum(self.pacman.pos)
        if output == "gum":
            self.gain_score("gum", self.scores_ref.gum)
        elif output == "sup_gum":
            self.activate_super()
        for name, ghost in self.ghosts.items():
            if ghost.pos == self.pacman.pos:
                if self.super_mode is False:
                    self.pacman.is_alive = False
                    self.lives -= 1
                    pg.time.set_timer(Timers.PACMAN.value, 2000, 1)
                else:
                    self.gain_score("ghost", self.scores_ref.ghost)
                    ghost.is_alive = False
                    pg.time.set_timer(
                        Timers[name.upper()].value, ghost.down_time, 1)

    def update(self) -> None:
        if self.pacman.is_alive is True:
            self.update_entities()
        if self.level_timer == 0 or self.lives == 0:
            pass
        if self.map.check_gum() is True:
            pass
