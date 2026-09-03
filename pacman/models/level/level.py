
from enum import IntEnum

import pygame as pg

from pacman.models import (
    MazeConfig, GameplayConfig, ScoresConfig,
    Entity, Pacman, Ghost,
    Map, Directions, OPPOSITE_DIRECTION, Movements)


class Timers(IntEnum):
    LEVEL = pg.USEREVENT + 0
    SUPER = pg.USEREVENT + 1
    PACMAN = pg.USEREVENT + 2
    BLINKY = pg.USEREVENT + 3
    PINKY = pg.USEREVENT + 4
    INKY = pg.USEREVENT + 5
    CLYDE = pg.USEREVENT + 6
    ANIMATIONS = pg.USEREVENT + 7


ANIM_TICK: int = 15


class Level:
    def __init__(
            self, level_id: int,  player_lives: int, cheats_allowed: bool,
            maze_config: MazeConfig, gameplay: GameplayConfig,
            scores_config: ScoresConfig) -> None:
        self.level_id: int = level_id
        self.lives: int = player_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = False
        self.theme: str = gameplay.theme
        self.level_duration: int = gameplay.timer
        self.level_timer: int = gameplay.timer
        self.super_duration: int = gameplay.super_duration
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        self.map: Map = Map(**maze_config.model_dump())
        self.map.super_gum_placement()
        self.map.simple_gum_placement()
        self.map.generate_cell_graph()
        self.pacman: Pacman
        self.ghosts: dict[str, Ghost] = {}
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
        self.pacman.is_super = False
        self.pacman.speed = self.calc_speed(self.pacman.speed)
        self.pacman.super_speed = self.calc_speed(self.pacman.super_speed)
        self.pacman.current_speed = self.pacman.speed
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
                new_ghost.is_super = False
                new_ghost.speed = self.calc_speed(new_ghost.speed)
                new_ghost.super_speed = self.calc_speed(new_ghost.super_speed)
                new_ghost.current_speed = new_ghost.speed
                self.ghosts.update({name: new_ghost})
                self.char_anim.update({name: new_ghost.current_speed})
                pg.time.set_timer(Timers[name.upper()].value, 100, 1)

    def set_entity_moving_timer(self, name: str, entity: Entity) -> None:
        pg.time.set_timer(Timers[name.upper()].value, entity.current_speed, 1)

    def update_entity_timer_instant(self, name: str, entity: Entity) -> None:
        time: int = entity.current_speed - self.char_anim[name]
        pg.time.set_timer(Timers[name.upper()].value,
                          time if time > 0 else 1, 1)

    def move_pacman(self) -> None:
        self.pacman.move(self.map.get_cell(self.pacman.pos).walls)
        if self.pacman.direction.value == 15:
            pg.time.set_timer(Timers.PACMAN.value, 0)
        else:
            self.char_anim["Pacman"] = 0
            self.set_entity_moving_timer("pacman", self.pacman)

    def move_ghost(self, name: str) -> None:
        ghost: Ghost = self.ghosts[name]
        if ghost.is_super is True:
            ghost.escape(self.pacman.pos)
        else:
            ghost.chase(self.pacman.pos)
        self.char_anim[name] = 0
        self.set_entity_moving_timer(name, ghost)

    def get_event(self, event: pg.event.Event, action_key: str) -> None:
        if event.type == pg.KEYDOWN:
            self.pacman.update_user_input(action_key)
            if self.pacman.direction.value == 15:
                self.move_pacman()
        elif event.type == Timers.LEVEL.value:
            self.level_timer -= 1
        elif event.type == Timers.SUPER.value:
            self.deactivate_super()
        elif event.type == Timers.PACMAN.value:
            self.update_pacman()
        elif event.type == Timers.ANIMATIONS.value:
            self.update_animations()
        for name in self.ghosts.keys():
            if event.type == Timers[name.upper()].value:
                if self.ghosts[name].is_alive is True:
                    self.move_ghost(name)
                else:
                    self.ghosts[name].is_alive = True
                    self.set_entity_moving_timer(name, self.ghosts[name])

    def gain_score(self, type: str, amount: int) -> None:
        self.score += amount
        self.scores[type] += amount

    def activate_super(self) -> None:
        self.pacman.is_super = True
        self.pacman.current_speed = self.pacman.super_speed
        self.update_entity_timer_instant("Pacman", self.pacman)
        for name, ghost in self.ghosts.items():
            if ghost.is_alive is True:
                ghost.is_super = True
                ghost.current_speed = ghost.super_speed
                self.update_entity_timer_instant(name, ghost)
        pg.time.set_timer(Timers.SUPER.value, self.super_duration * 1000, 1)

    def deactivate_super(self) -> None:
        self.pacman.is_super = False
        self.pacman.current_speed = self.pacman.speed
        self.update_entity_timer_instant("Pacman", self.pacman)
        for name, ghost in self.ghosts.items():
            ghost.is_super = False
            ghost.current_speed = ghost.speed
            self.update_entity_timer_instant(name, ghost)

    def update_pacman(self) -> None:
        if self.pacman.is_alive is True:
            self.move_pacman()
        else:
            self.pacman.is_alive = True
            self.pacman.direction = Directions.NONE
            self.pacman.respawn()
            for ghost in self.ghosts.values():
                ghost.is_alive = True
                ghost.respawn()

    def update_animations(self) -> None:
        if self.pacman.is_alive and self.pacman.direction.value != 15:
            self.char_anim["Pacman"] += ANIM_TICK
            if self.char_anim["Pacman"] > self.pacman.current_speed:
                self.char_anim["Pacman"] = self.pacman.current_speed
        else:
            self.char_anim["Pacman"] = self.pacman.current_speed
        for name, ghost in self.ghosts.items():
            if ghost.is_alive is False or ghost.direction.value == 15:
                self.char_anim[name] = ghost.current_speed
            self.char_anim[name] += ANIM_TICK
            if self.char_anim[name] > ghost.current_speed:
                self.char_anim[name] = ghost.current_speed

    def theoric_position(self, name: str, entity: Entity) -> tuple[int, int]:
        theoric_pos: tuple[int, int] = entity.pos
        if self.char_anim[name] < entity.current_speed // 2:
            opposite_move: tuple[int, int] = (
                Movements[OPPOSITE_DIRECTION[entity.direction].name].value)
            theoric_pos = (theoric_pos[0] + opposite_move[0],
                           theoric_pos[1] + opposite_move[1])
        return theoric_pos

    def update_entities(self) -> None:
        pac_pos: tuple[int, int] = self.theoric_position("Pacman", self.pacman)
        output: str = self.map.update_gum(pac_pos)
        if output == "simple_gum":
            self.gain_score("gum", self.scores_ref.gum)
        elif output == "super_gum":
            self.gain_score("sup_gum", self.scores_ref.sup_gum)
            self.activate_super()
        for name, ghost in self.ghosts.items():
            if ghost.is_alive is False:
                continue
            ghost_pos: tuple[int, int] = self.theoric_position(name, ghost)
            if ghost_pos == pac_pos:
                if ghost.is_super is False:
                    self.pacman.is_alive = False
                    self.lives -= 1
                    pg.time.set_timer(Timers.PACMAN.value, 2000, 1)
                else:
                    self.gain_score("ghost", self.scores_ref.ghost)
                    ghost.respawn()
                    ghost.is_super = False
                    ghost.is_alive = False
                    pg.time.set_timer(
                        Timers[name.upper()].value, ghost.down_time * 1000, 1)

    def update(self) -> None:
        if self.pacman.is_alive is True:
            self.update_entities()
        if self.level_timer == 0 or self.lives == 0:
            pass
        if self.map.check_gum() is True:
            pass
