
from typing import ClassVar, Any, Iterable
from random import randint, choice

from pydantic import Field, field_validator, ValidationInfo

from .utils import JSONModel


STRATS: tuple[str, ...] = (
    "AlternateAngleStrat", "PatrollingAngleStrat", "ChaseOnSpot",
    "ChaseFumbling", "ChaseDynamic", "EscapeMaxDistance", "EscapeToCorner",
    "EscapeDynamic")

THEMES: tuple[str, ...] = ("grassy", "dungeon")


class PlayerConfig(JSONModel):
    """Class PlayerConfig, subclass of JSONModel

    Contains attributes related to the player.

    ### Attributes:
    - lives_count: int => int superior to 0
    - cheats_allowed: bool => boolean defaulted to False
    """
    lives_count: int = Field(gt=0, default=3)
    cheats_allowed: bool = Field(default=False)


class MazeConfig(JSONModel):
    """Class MazeConfig, subclass of JSONModel

    Contains attributes used to generate a level's maze.

    ### Attributes:
    - width: int => greater than 3 and less than 100, defaulted to 11
    - height: int => same as width
    - gum_percent: int => between 0 and 100, defaulted to 80.
    - seed: int => positive int randomized if unset
    """
    width: int = Field(ge=3, le=100, default=11)
    height: int = Field(ge=3, le=100, default=11)
    gum_percent: int = Field(ge=0, le=100, default=80)
    seed: int = Field(ge=0, default_factory=lambda: randint(0, 10000000))


class GhostConfig(JSONModel):
    """Class GhostConfig, subclass of JSONModel

    Contains attributes related to a single ghost.

    ### Attributes:
    - idle_strat: str => literal string corresponding to a Strategy the ghost
    will use when idling
    - chase_strat: str => literal string for the chasing Strategy
    - escape_strat: str => literal string for the escaping Strategy
    - speed: int => between 0 and 20 both included
    - super_speed: int => same as speed
    - chase_radius: int =>positive number corresponding to the manhattan
    distance between the ghost and pacman for it to start chasing it
    - escape_radius: int => positive number corresponding to the manhattan
    distance between the ghost and pacman for it to start escaping in super
    mode
    - chasing_stamina: int => number of cells traversed by the ghost while
    chasing pacman before it gives up
    - down_time: int => time in seconds during which the ghost is inactive

    ### Method:
    - strats_validator (classmethod) => checks if the idle, chase and escape
    strategies are effectively part of the literal list, otherwise returns the
    default value using a class attribute
    """
    idle_strat: str = Field(default="AlternateAngleStrat")
    chase_strat: str = Field(default="ChaseOnSpot")
    escape_strat: str = Field(default="EscapeToCorner")
    speed: int = Field(ge=0, le=20, default=10)
    super_speed: int = Field(ge=0, le=20, default=10)
    chase_radius: int = Field(ge=0, default=5)
    escape_radius: int = Field(ge=0, default=5)
    chasing_stamina: int = Field(ge=0, default=10)
    down_time: int = Field(ge=0, le=20, default=3)

    @field_validator("idle_strat", "chase_strat", "escape_strat",
                     mode="before")
    @classmethod
    def strats_validator(cls, value: Any, info: ValidationInfo) -> Any:
        """Effectively checks if the idle, chase and escape strategies passed
        as argument are part of the STRAT literal list. If not, uses the
        field's info to return its default value.
        """
        field_info: Any = (cls.model_fields[str(info.field_name)].asdict())
        if value not in STRATS:
            return field_info["attributes"]["default"]
        else:
            return value


class GameplayConfig(JSONModel):
    """Class GameplayConfig, subclass of JSONModel

    Contains attributes related to the running of a single level.

    ### Attributes:
    - timer: int => time in second in which the player must complete the level
    - theme: themes => theme used for the level between "grassy" and "dungeon"
    - life_regen: int => life given to the player upon entering the level
    - super_duration: int => time in second during which the super mode will
    last
    - pac_man_speed: int => speed of pacman during the level
    - super_pac_man_speed: int => speed of pacman in the super mode
    - ghosts: dict[str, GhostConfig] => dict of ghosts made of either
    GhostConfig objects or dicts containing all necessary information to
    generate one, also means not all 4 ghosts must be active at the same time

    ### Method:
    - theme_validator (classmethod) => checks if the theme attribute is part
    of the literal list, otherwise return the default value using a class
    attribute
    - ghosts_validator (staticmethod) => parse the value given for each ghost
    to return a dict of GhostConfig
    """
    timer: int = Field(gt=0, default=90)
    theme: str = Field(default_factory=lambda: choice(THEMES))
    life_regen: int = Field(ge=0, default=0)
    super_duration: int = Field(ge=0, default=8)
    pac_man_speed: int = Field(ge=0, default=10)
    super_pac_man_speed: int = Field(ge=0, default=11)
    ghosts: dict[str, GhostConfig] = Field(
        min_length=0, max_length=4,
        default={"Blinky": GhostConfig(), "Pinky": GhostConfig(),
                 "Inky": GhostConfig(), "Clyde": GhostConfig()})

    @field_validator("theme", mode="before")
    @classmethod
    def theme_validator(cls, value: Any, info: ValidationInfo) -> Any:
        """Effectively checks if the idle, chase and escape strategies passed
        as argument are part of the THEMES literal list. If not, uses the
        field's info to return its default value.
        """
        field_info: Any = (cls.model_fields[str(info.field_name)].asdict())
        if value not in THEMES:
            return field_info["attributes"]["default"]
        else:
            return value

    @field_validator("ghosts", mode="before")
    @staticmethod
    def ghosts_validator(value: Any) -> Any:
        """If the value's type isn't a dict, return None to use the default
        value. Otherwise, remove any entry in the dict which name doesn't
        correspond to one of the ghosts, and update the remaining ones either
        with the GhostConfig they already contain, or one made with their
        original values.

        Returns the dict of GhostConfig made then.
        """
        names: tuple[str, ...] = ("Blinky", "Pinky", "Inky", "Clyde")
        if isinstance(value, dict) is False:
            return None
        for entry in [key for key in value.keys() if key not in names]:
            value.pop(entry)
        for ghost, info in value.items():
            if isinstance(info, GhostConfig):
                value.update({ghost: info})
            elif isinstance(info, dict) and len(info) > 0:
                value.update({ghost: GhostConfig(**info)})
            else:
                value.update({ghost: GhostConfig()})
        return value


class ScoresConfig(JSONModel):
    """Class GameplayConfig, subclass of JSONModel

    Contains attributes related to the scores of a single level. All scores
    must be positive integers.

    ### Attributes:
    - gum: int => defaulted to 10
    - sup_gum: int => defaulted to 50
    - ghost: int => defaulted to 100, obtained when eating a ghost
    - level: int => defaulted to 250, obtained when completing the level
    """
    gum: int = Field(ge=0, default=10)
    sup_gum: int = Field(ge=0, default=50)
    ghost: int = Field(ge=0, default=100)
    level: int = Field(ge=0, default=250)


class LevelConfig(JSONModel):
    """Class GameplayConfig, subclass of JSONModel

    Contains a MazeConfig, GameplayConfig and ScoresConfig to make up all
    informations necessary to effectively initialize and run a single level.

    ### Attributes:
    - maze: MazeConfig
    - gameplay: GameplayConfig
    - scores: ScoresConfig

    ### Method:
    - config_validator (classmethod) => called for all attributes, if their
    value doesn't correspond to their correct type but rather a dict,
    instantiate them using the dict's values, and otherwise return None to
    generate default configs
    """
    maze: MazeConfig = Field(default_factory=MazeConfig)
    gameplay: GameplayConfig = Field(default_factory=GameplayConfig)
    scores: ScoresConfig = Field(default_factory=ScoresConfig)

    @field_validator("maze", "gameplay", "scores", mode="before")
    @classmethod
    def config_validator(cls, value: Any, info: ValidationInfo) -> Any:
        """Called for all attributes, if their value doesn't
        correspond to their correct type but rather a dict, instantiate them
        using the dict's values, and otherwise return None to generate default
        configs
        """
        field_info: Any = (
            cls.model_fields[str(info.field_name)].asdict())
        if isinstance(value, field_info["attributes"]["default_factory"]):
            return value
        if isinstance(value, dict) and len(value) > 0:
            return field_info["attributes"]["default_factory"](**value)
        return None


class Config(JSONModel):
    """Class Config, subclass of JSONModel

    Configuration object containing all base levels informations to run a
    functioning set of levels.

    ### Attributes:
    - file_name: ClassVar[str] => used to open the right file during parsing
    - player: PlayerConfig => the player's config, as their values are kept
    between levels
    - levels: list[LevelConfig]

    ### Methods:
    - player_validator (staticmethod) => checks if the value passed is already
    a PlayerConfig, and otherwise tries to create one if value is a dict
    - levels_validator (staticmethod) => if the value is an iterable, tries
    recreating a LevelConfig for each element and return the new list
    """
    file_name: ClassVar[str] = "config"

    player: PlayerConfig = Field(default_factory=PlayerConfig)
    levels: list[LevelConfig] = Field(
        min_length=1,
        default=list([LevelConfig(maze=MazeConfig(seed=68771))]
                     + [LevelConfig() for _ in range(9)]))

    @field_validator("player", mode="before")
    @staticmethod
    def player_validator(value: Any) -> Any:
        """If the value passed is already a PlayerConfig, returns it. If it's
        a non-empty dict, return the instantiation of a PlayerConfig using
        its values, and otherwise returns None to use the Field's default
        value.
        """
        if isinstance(value, PlayerConfig):
            return value
        if isinstance(value, dict) and len(value) > 0:
            return PlayerConfig(**value)
        return None

    @field_validator("levels", mode="before")
    @staticmethod
    def levels_validator(value: Any) -> Any:
        """If the value passed isn't an iterable, return None to use the
        Field's default value. Otherwise, for each elements, if it's a
        LevelConfig, appends it to a new list, if it's a non-empty dict, use
        its values to create a new LevelConfig, and if it's an empty dict,
        create a LevelConfig with default values.

        Returns the newly created list.
        """
        if isinstance(value, Iterable):
            level_list: list[LevelConfig] = []
            for config in value:
                if isinstance(config, LevelConfig):
                    level_list.append(config)
                elif isinstance(config, dict):
                    if len(config) > 0:
                        level_list.append(LevelConfig(**config))
                    else:
                        level_list.append(LevelConfig())
            return level_list
        return None
