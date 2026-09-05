
from enum import IntEnum

import pygame as pg

from pacman.models import (
    MazeConfig, GameplayConfig, ScoresConfig,
    Entity, Pacman, Ghost,
    Map, Directions, OPPOSITE_DIRECTION, Movements)


class Timers(IntEnum):
    LEVEL = pg.USEREVENT + 0
    SUPER = pg.USEREVENT + 1
    ANIMATIONS = pg.USEREVENT + 2


ANIM_TICK: int = 15


class LevelOutput:
    def __init__(self, victorious: bool, lives: int, cheats_used: bool,
                 level_timer: int, score: int, scores: dict[str, int]) -> None:
        self.victorious: bool = victorious
        self.lives: int = lives
        self.cheats_used: bool = cheats_used
        self.level_timer: int = level_timer
        self.score: int = score
        self.scores: dict[str, int] = scores


class Level:
    def __init__(
            self, level_id: int, max_lives: int, player_lives: int,
            cheats_allowed: bool, maze_config: MazeConfig,
            gameplay: GameplayConfig, scores_config: ScoresConfig) -> None:
        self.level_id: int = level_id
        self.max_lives: int = max_lives
        self.lives: int = player_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = False
        self.theme: str = gameplay.theme
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
                new_ghost.down_time *= 1000
                new_ghost.current_speed = new_ghost.speed
                self.ghosts.update({name: new_ghost})
                self.char_anim.update({name: new_ghost.current_speed})

    def move_pacman(self) -> None:
        self.pacman.move(self.map.get_cell(self.pacman.pos).walls)
        if self.pacman.direction.value == 15:
            self.char_anim["Pacman"] = self.pacman.current_speed
        else:
            self.char_anim["Pacman"] = 0

    def move_ghost(self, name: str) -> None:
        ghost: Ghost = self.ghosts[name]
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

    def gain_score(self, type: str, amount: int) -> None:
        self.score += amount
        self.scores[type] += amount

    def activate_super(self) -> None:
        self.super_anim = self.super_duration
        self.pacman.is_super = True
        self.pacman.current_speed = self.pacman.super_speed
        for ghost in self.ghosts.values():
            if ghost.is_alive is True:
                ghost.is_super = True
                ghost.current_speed = ghost.super_speed
        pg.time.set_timer(Timers.SUPER.value, self.super_duration, 1)

    def deactivate_super(self) -> None:
        self.super_anim = 0
        self.pacman.is_super = False
        self.pacman.current_speed = self.pacman.speed
        for ghost in self.ghosts.values():
            ghost.is_super = False
            ghost.current_speed = ghost.speed

    def update_pacman(self) -> None:
        if self.pacman.is_alive is True:
            self.move_pacman()
        else:
            self.lives -= 1
            self.pacman.is_alive = True
            self.pacman.current_speed = self.pacman.speed
            self.pacman.direction = Directions.NONE
            self.pacman.respawn()
            for ghost in self.ghosts.values():
                ghost.is_alive = True
                ghost.respawn()

    def update_animations(self) -> None:
        if self.pacman.is_super is True:
            self.super_anim -= ANIM_TICK
            if self.super_anim < 0:
                self.deactivate_super()
                self.super_anim = 0
        self.char_anim["Pacman"] += ANIM_TICK
        if self.char_anim["Pacman"] > self.pacman.current_speed:
            self.char_anim["Pacman"] = self.pacman.current_speed
        for name, ghost in self.ghosts.items():
            self.char_anim[name] += ANIM_TICK
            if self.char_anim[name] > ghost.current_speed:
                self.char_anim[name] = ghost.current_speed

    def theoric_position(self, name: str, entity: Entity) -> tuple[int, int]:
        theoric_pos: tuple[int, int] = entity.pos
        if (entity.direction.value != 15
                and self.char_anim[name] < entity.current_speed // 2.2):
            opposite_move: tuple[int, int] = (
                Movements[OPPOSITE_DIRECTION[entity.direction].name].value)
            theoric_pos = (theoric_pos[0] + opposite_move[0],
                           theoric_pos[1] + opposite_move[1])
        return theoric_pos

    def update_entities(self) -> None:
        if self.char_anim["Pacman"] == self.pacman.current_speed:
            self.update_pacman()
        pac_pos: tuple[int, int] = self.theoric_position("Pacman", self.pacman)
        output: str = self.map.update_gum(pac_pos)
        if output == "simple_gum":
            self.gain_score("gum", self.scores_ref.gum)
        elif output == "super_gum":
            self.gain_score("sup_gum", self.scores_ref.sup_gum)
            self.activate_super()
        for name, ghost in self.ghosts.items():
            if self.char_anim[name] == ghost.current_speed:
                if ghost.is_alive is True:
                    self.move_ghost(name)
                else:
                    ghost.is_alive = True
                    ghost.current_speed = ghost.speed
            ghost_pos: tuple[int, int] = self.theoric_position(name, ghost)
            if ghost_pos == pac_pos:
                if ghost.is_super is False:
                    self.pacman.is_alive = False
                    self.pacman.current_speed = 2000
                    self.pacman.direction = Directions.NONE
                    self.char_anim["Pacman"] = 0
                else:
                    self.gain_score("ghost", self.scores_ref.ghost)
                    self.char_anim[name] = 0
                    ghost.respawn()
                    ghost.current_speed = ghost.down_time
                    ghost.is_super = False
                    ghost.is_alive = False

    def create_level_output(self, victorious: bool) -> LevelOutput:
        return LevelOutput(victorious, self.lives, self.cheats_used,
                           self.level_timer, self.score, self.scores)

    def update(self) -> None | LevelOutput:
        self.update_entities()
        if self.level_timer == 0 or self.lives == 0:
            return self.create_level_output(False)
        if self.map.check_gum() is True:
            return self.create_level_output(True)
        return None
