
from enum import IntEnum
from typing import TypedDict, cast

import pygame as pg

from pacman.models import (
    MazeConfig, GameplayConfig, ScoresConfig,
    Entity, Pacman, Ghost,
    Map, Directions, OPPOSITE_DIRECTION, Movements)


ANIM_TICK: int = 15


class Cheats(TypedDict):
    invincibility: bool
    infinite_super: bool
    super_speed: bool
    skip_level: bool
    life_gains: int


class Timers(IntEnum):
    LEVEL = pg.USEREVENT + 0
    SUPER = pg.USEREVENT + 1
    ANIMATIONS = pg.USEREVENT + 2


class LevelOutput(TypedDict):
    victorious: bool
    lives: int
    time_taken: int
    score: int
    scores: dict[str, int]


class Level:
    def __init__(
            self, level_id: int, max_lives: int, player_lives: int,
            maze_config: MazeConfig, gameplay: GameplayConfig,
            scores_config: ScoresConfig, cheats: Cheats) -> None:
        self.level_id: int = level_id
        self.max_lives: int = max_lives
        self.lives: int = player_lives
        self.theme: str = gameplay.theme
        self.cheats: Cheats = cheats
        self.level_duration: int = gameplay.timer
        self.level_timer: int = gameplay.timer
        self.super_duration: int = gameplay.super_duration * 1000
        self.super_anim: int = 0
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        self.map: Map = Map(**maze_config.model_dump())
        self.map.super_gum_placement()
        self.map.simple_gum_placement()
        self.map.generate_cell_graph()
        self.pacman: Pacman
        self.ghosts: list[str] = []
        self.chars: dict[str, Entity] = {}
        self.char_anim: dict[str, int] = {}
        self.instantiate_pacman(maze_config, gameplay)
        self.instantiate_ghosts(maze_config, gameplay)
        pg.time.set_timer(Timers.LEVEL.value, 1000)
        pg.time.set_timer(Timers.ANIMATIONS.value, ANIM_TICK)

    @staticmethod
    def calc_speed(speed: int) -> int:
        if speed > 0:
            return 1500 - (speed - 1) * 100
        return speed

    def instantiate_pacman(self, maze: MazeConfig,
                           config: GameplayConfig) -> None:
        self.pacman = Pacman(
            config.pac_man_speed, config.super_pac_man_speed,
            ((maze.width - 1) // 2, (maze.height - 1) // 2))
        self.pacman.speed = self.calc_speed(self.pacman.speed)
        self.pacman.super_speed = self.calc_speed(self.pacman.super_speed)
        self.pacman.current_speed = self.pacman.speed
        self.chars.update({"Pacman": self.pacman})
        self.char_anim.update({"Pacman": self.pacman.current_speed})

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
                new_ghost.speed = self.calc_speed(new_ghost.speed)
                new_ghost.super_speed = self.calc_speed(new_ghost.super_speed)
                new_ghost.down_time *= 1000
                new_ghost.current_speed = new_ghost.speed
                self.ghosts.append(name)
                self.chars.update({name: new_ghost})
                self.char_anim.update({name: new_ghost.current_speed})

    def move_pacman(self) -> None:
        self.pacman.move(self.map.get_cell(self.pacman.pos).walls)
        if self.pacman.direction.value == 15:
            self.char_anim["Pacman"] = self.pacman.current_speed
        else:
            self.char_anim["Pacman"] = 0

    def move_ghost(self, name: str) -> None:
        ghost: Ghost = cast(Ghost, self.chars[name])
        if ghost.is_super is True:
            ghost.escape(self.pacman.pos)
        else:
            ghost.chase(self.pacman.pos)
        self.char_anim[name] = 0

    def get_event(self, event: pg.event.Event, action_key: str) -> None:
        if event.type == pg.KEYDOWN:
            self.pacman.update_user_input(action_key)
            if self.pacman.direction.value == 15:
                self.move_pacman()
        elif event.type == Timers.LEVEL.value:
            self.level_timer -= 1
        elif event.type == Timers.ANIMATIONS.value:
            self.update_animations()

    def gain_score(self, type: str) -> None:
        amount: int = getattr(self.scores_ref, type)
        self.score += amount
        self.scores[type] += amount

    def activate_super(self) -> None:
        self.super_anim = self.super_duration
        for char in self.chars.values():
            if char.is_alive is True:
                char.is_super = True
                char.current_speed = char.super_speed
        pg.time.set_timer(Timers.SUPER.value, self.super_duration, 1)

    def deactivate_super(self) -> None:
        self.super_anim = 0
        for char in self.chars.values():
            char.is_super = False
            char.current_speed = char.speed

    def entity_die(self, name: str) -> None:
        self.char_anim[name] = 0
        self.chars[name].is_alive = False

    def entity_respawn(self, name: str) -> None:
        self.char_anim[name] = 0
        char: Entity = self.chars[name]
        char.is_alive = True
        if self.cheats["infinite_super"] is False:
            char.is_super = False
        char.current_speed = char.speed
        char.respawn()

    def entity_theoric_pos(self, name: str) -> tuple[int, int]:
        entity: Entity = self.chars[name]
        theoric_pos: tuple[int, int] = entity.pos
        if (entity.direction.value != 15
                and self.char_anim[name] < entity.current_speed // 2.2):
            opposite_move: tuple[int, int] = (
                Movements[OPPOSITE_DIRECTION[entity.direction].name].value)
            theoric_pos = (theoric_pos[0] + opposite_move[0],
                           theoric_pos[1] + opposite_move[1])
        return theoric_pos

    def update_pacman(self) -> None:
        if self.pacman.is_alive is True:
            speed_ref: int = (self.pacman.current_speed
                              if self.cheats["super_speed"] is False else 300)
            if self.char_anim["Pacman"] >= speed_ref:
                self.move_pacman()
        elif self.char_anim["Pacman"] >= 2000:
            self.lives -= 1
            self.pacman.direction = Directions.NONE
            self.pacman.next_direction = Directions.NONE
            if self.cheats["infinite_super"] is False:
                self.deactivate_super()
            for name in self.chars.keys():
                self.entity_respawn(name)

    def update_entities(self) -> None:
        self.update_pacman()
        pac_pos: tuple[int, int] = self.entity_theoric_pos("Pacman")

        if self.pacman.is_alive is True:
            output: str = self.map.update_gum(pac_pos)
            if output == "simple_gum":
                self.gain_score("gum")
            elif output == "super_gum":
                self.gain_score("sup_gum")
                self.activate_super()

        for name in self.ghosts:
            ghost: Ghost = cast(Ghost, self.chars[name])
            if ghost.is_alive is True:
                if self.char_anim[name] >= ghost.current_speed:
                    self.move_ghost(name)
            elif self.char_anim[name] >= ghost.down_time:
                self.entity_respawn(name)
            if self.pacman.is_alive is True and ghost.is_alive is True:
                ghost_pos: tuple[int, int] = self.entity_theoric_pos(name)
                if ghost_pos == pac_pos:
                    if ghost.is_super is True:
                        self.gain_score("ghost")
                        self.entity_die(name)
                    elif self.cheats["invincibility"] is False:
                        self.entity_die("Pacman")

    def update_animations(self) -> None:
        if self.pacman.is_super is True:
            if self.cheats["infinite_super"] is False:
                self.super_anim -= ANIM_TICK
            if self.super_anim < 0:
                self.deactivate_super()
                self.super_anim = 0
        for name in self.chars.keys():
            self.char_anim[name] += ANIM_TICK

    def create_level_output(self, victorious: bool) -> LevelOutput:
        return {"victorious": victorious, "lives": self.lives,
                "time_taken": self.level_duration - self.level_timer,
                "score": self.score, "scores": self.scores}

    def skip_level(self) -> LevelOutput:
        self.gain_score("level")
        return self.create_level_output(True)

    def update(self) -> None | LevelOutput:
        self.update_entities()
        if self.level_timer == 0 or self.lives == 0:
            return self.create_level_output(False)
        if self.map.check_gum() is True:
            self.gain_score("level")
            return self.create_level_output(True)
        return None
