
from typing import ClassVar, cast
from pydantic import Field, field_validator, ValidationInfo
from enum import Enum
import pygame as pg

from utils import JSONModel


class Languages(Enum):
    FRENCH = "fr-fr"
    ENGLISH = "en-en"


class Resolutions(Enum):
    SMALL = [640, 480]
    MEDIUM = [800, 600]
    BIG = [1024, 768]
    FULLSCREEN = [0, 0]


KeySet = tuple[int, int | None]


class Settings(JSONModel):
    file_name: ClassVar[str] = "settings"
    lang: Languages = Field(default=Languages.ENGLISH)
    res: Resolutions = Field(default=Resolutions.SMALL)
    sfx_vol: int = Field(ge=0, le=10, default=10)
    bgm_vol: int = Field(ge=0, le=10, default=10)

    up_keys: KeySet = Field(default=(pg.K_UP, None))
    down_keys: KeySet = Field(default=(pg.K_DOWN, None))
    left_keys: KeySet = Field(default=(pg.K_LEFT, None))
    right_keys: KeySet = Field(default=(pg.K_RIGHT, None))

    confirm_keys: KeySet = Field(default=(pg.K_RETURN, pg.K_SPACE))
    return_keys: KeySet = Field(default=(pg.K_ESCAPE, pg.K_x))

    @field_validator("lang", mode="before")
    @classmethod
    def lang_validator(cls, value: str) -> Languages:
        try:
            return Languages(value)
        except Exception:
            return Languages.ENGLISH

    @field_validator("res", mode="before")
    @classmethod
    def lang_validator(cls, value: list[int]) -> Resolutions:
        try:
            return Resolutions(value)
        except Exception:
            return Resolutions.SMALL

    @field_validator(
        "up_keys", "down_keys", "left_keys", "right_keys",
        "confirm_keys", "return_keys", mode="after")
    @classmethod
    def pg_key_validator(cls, value: KeySet, info: ValidationInfo) -> KeySet:
        if (pg.key.name(value[0]) == ""
                or value[1] is not None and pg.key.name(value[1]) == ""):
            return cast(KeySet,
                        cls.model_fields[str(info.field_name)].get_default())
        return value


if __name__ == "__main__":
    settings: Settings = Settings(
        lang="fr-fr",
        res=Resolutions.SMALL,
        sfx_vol=9,
        bgm_vol=15,
        up_keys=[16000, 12],
    )
    print(settings)
