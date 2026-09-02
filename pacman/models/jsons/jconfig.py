
from typing import ClassVar, Any, Iterable
from random import randint

from pydantic import Field, field_validator, ValidationInfo

from .utils import JSONModel, themes


STRATS: tuple[str, ...] = (
    "ChaseOnSpot", "AlternateAngleStrat", "PatrollingAngleStrat",
    "ChaseStumbling")


class PlayerConfig(JSONModel):
    lives_count: int = Field(gt=0, default=3)
    cheats_allowed: bool = Field(default=False)


class MazeConfig(JSONModel):
    width: int = Field(ge=11, le=100, default=11)
    height: int = Field(ge=11, le=100, default=11)
    gum_percent: int = Field(ge=0, le=100, default=80)
    seed: int = Field(ge=0, default_factory=lambda: randint(0, 10000000))


class GhostConfig(JSONModel):
    idle_strat: str = Field(default="AlternateAngleStrat")
    chase_strat: str = Field(default="ChaseOnSpot")
    escape_strat: str = Field(default="PatrollingAngleStrat")
    speed: int = Field(ge=0, le=20, default=3)
    super_speed: int = Field(ge=0, le=20, default=3)
    escape_radius: int = Field(ge=0, default=5)
    chase_radius: int = Field(ge=0, default=5)
    chasing_stamina: int = Field(ge=0, default=10)
    down_time: int = Field(ge=0, le=20, default=3)

    @field_validator("idle_strat", "chase_strat", "escape_strat",
                     mode="before")
    @classmethod
    def strats_validator(cls, value: Any, info: ValidationInfo) -> Any:
        field_info: Any = (
            cls.model_fields[str(info.field_name)].asdict())
        if value not in STRATS:
            return field_info["attributes"]["default"]
        else:
            return value


class GameplayConfig(JSONModel):
    timer: int = Field(gt=0, default=90)
    theme: themes = Field(default="grassy")
    life_regen: int = Field(ge=0, default=0)
    super_duration: int = Field(ge=0, default=8)
    pac_man_speed: int = Field(ge=0, default=3)
    super_pac_man_speed: int = Field(ge=0, default=4)
    ghosts: dict[str, GhostConfig] = Field(
        min_length=0, max_length=4,
        default={"Blinky": GhostConfig(), "Pinky": GhostConfig(),
                 "Inky": GhostConfig(), "Clyde": GhostConfig()})

    @field_validator("ghosts", mode="before")
    def ghosts_validator(value: Any) -> Any:
        names: tuple[str, ...] = ("Blinky", "Pinky", "Inky", "Clyde")
        if isinstance(value, dict) is False:
            return None
        for entry in [key for key in value.keys() if key not in names]:
            value.pop(entry)
        for ghost, info in value.items():
            if isinstance(info, GhostConfig):
                value.update({ghost: info})
            elif isinstance(info, dict) is False:
                value.update({ghost: GhostConfig()})
            else:
                value.update({ghost: GhostConfig(**info)})
        return value


class ScoresConfig(JSONModel):
    gum: int = Field(default=50)
    sup_gum: int = Field(default=10)
    ghost: int = Field(default=50)
    level: int = Field(default=250)


class LevelConfig(JSONModel):
    maze: MazeConfig = Field(default_factory=MazeConfig)
    gameplay: GameplayConfig = Field(default_factory=GameplayConfig)
    scores: ScoresConfig = Field(default_factory=ScoresConfig)

    @field_validator("maze", "gameplay", "scores", mode="before")
    @classmethod
    def config_validator(cls, value: Any, info: ValidationInfo) -> Any:
        field_info: Any = (
            cls.model_fields[str(info.field_name)].asdict())
        if isinstance(value, field_info["attributes"]["default_factory"]):
            return value
        if isinstance(value, dict) is False:
            return None
        return field_info["attributes"]["default_factory"](**value)


class Config(JSONModel):
    """Class Config, subclass of JSONModel

    Configuration object containing all base levels informations to run a
    functioning set of levels.
    """
    file_name: ClassVar[str] = "config"

    player: PlayerConfig = Field(default_factory=PlayerConfig)
    levels: list[LevelConfig] = Field(
        min_length=1,
        default=list([LevelConfig(maze=MazeConfig(seed=68771))]
                     + [LevelConfig() for _ in range(9)]))

    @field_validator("player", mode="before")
    def player_validator(value: Any) -> Any:
        if isinstance(value, PlayerConfig):
            return value
        if isinstance(value, dict) and len(value) > 0:
            return PlayerConfig(**value)
        return None

    @field_validator("levels", mode="before")
    def levels_validator(value: Any) -> Any:
        if isinstance(value, Iterable):
            level_list: list[LevelConfig] = []
            for config in value:
                if isinstance(config, LevelConfig):
                    level_list.append(config)
                elif isinstance(config, dict) and len(config) > 0:
                    level_list.append(LevelConfig(**config))
            return level_list
        return None
