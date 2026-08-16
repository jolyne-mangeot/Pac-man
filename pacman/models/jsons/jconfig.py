
from typing import ClassVar
from random import randint

from pydantic import Field

from .utils import JSONModel


class PlayerConfig(JSONModel):
    lives_count: int = Field(gt=0, default=3)
    cheats_allowed: bool = Field(default=False)


class MazeConfig(JSONModel):
    width: int = Field(ge=15, le=100, default=10)
    height: int = Field(ge=15, le=100, default=10)
    seed: int = Field(ge=0, default_factory=lambda: randint(0, 10000000))


class GhostConfig(JSONModel):
    move_strat: str = Field(default="chase")  # REPLACE TYPE HINT BY LITERAL
    sup_move_strat: str = Field(default="run")  # LIST FROM ALGORITHMS FILE
    speed: int = Field(ge=0, default=3)
    sup_speed: int = Field(ge=0, default=3)
    down_time: int = Field(ge=0, default=3)


class GameplayConfig(JSONModel):
    timer: int = Field(gt=0, default=90)
    life_regen: int = Field(ge=0, default=0)
    super_duration: int = Field(ge=0, default=8)
    pac_man_speed: int = Field(ge=0, default=3)
    sup_pac_man_speed: int = Field(ge=0, default=4)
    ghosts: dict[str, GhostConfig] = Field(
        min_length=0, max_length=4,
        default={"Blinky": GhostConfig(), "Pinky": GhostConfig(),
                 "Inky": GhostConfig(), "Clyde": GhostConfig()})


class ScoresConfig(JSONModel):
    gum: int = Field(default=50)
    sup_gum: int = Field(default=10)
    ghost: int = Field(default=50)
    level: int = Field(default=250)


class LevelConfig(JSONModel):
    maze: MazeConfig = Field(default_factory=MazeConfig)
    gameplay: GameplayConfig = Field(default=GameplayConfig())
    scores: ScoresConfig = Field(default=ScoresConfig())


class Config(JSONModel):
    """Class Config, subclass of JSONModel

    Configuration object containing all base levels informations to run a
    functioning set of levels.
    """
    file_name: ClassVar[str] = "config"

    player: PlayerConfig = Field(default=PlayerConfig())
    levels: list[LevelConfig] = Field(
        min_length=1,
        default=list([LevelConfig(maze=MazeConfig(seed=68771))]
                     + [LevelConfig() for _ in range(9)]))
