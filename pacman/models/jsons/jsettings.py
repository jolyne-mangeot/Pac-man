
from typing import ClassVar, Iterable, Final
from pydantic import Field, field_validator, ValidationInfo, model_validator
from enum import Enum
import pygame as pg

from .utils import JSONModel


class SettingsEnum(Enum):
    def __str__(self) -> str:
        return str(self.value)


class Languages(SettingsEnum):
    FRENCH = "fr-fr"
    ENGLISH = "en-en"


class Resolutions(SettingsEnum):
    TINY = [640, 480]
    SMALL = [800, 600]
    MEDIUM = [1024, 768]
    BIG = [1440, 1080]
    TV = [1920, 1440]
    FULLSCREEN = "fullscreen"


ACTION_LIST: Final[tuple[str, ...]] = (
    "up_key", "down_key", "left_key", "right_key",
    "confirm_key", "return_key")


class KeyConfig(JSONModel):
    file_name: ClassVar[str] = "settings"
    up_key: str = Field(default="up")
    down_key: str = Field(default="down")
    left_key: str = Field(default="left")
    right_key: str = Field(default="right")

    confirm_key: str = Field(default="return")
    return_key: str = Field(default="escape")

    @field_validator(
            "up_key", "down_key", "left_key", "right_key",
            "confirm_key", "return_key", mode="before")
    @classmethod
    def pg_key_validator(cls, value: str, info: ValidationInfo) -> str:
        key: str = str(cls.model_fields[str(info.field_name)].get_default())
        try:
            pg.key.key_code(value)
            key = value
        except Exception:
            pass
        return key

    @model_validator(mode="after")
    def check_key_duplicates(self) -> "KeyConfig":
        key_fields: tuple[str, ...] = (
            "up_key", "down_key", "left_key", "right_key",
            "confirm_key", "return_key")
        defaults: list[str] = [
            value.asdict()["attributes"]["default"] for value in (
                KeyConfig.model_fields[key] for key in key_fields)]
        attributes: list[str] = [
            self.up_key, self.down_key, self.left_key,
            self.right_key, self.confirm_key, self.return_key]

        while len(attributes) != len(set(attributes)):
            for default_index in range(6):
                for index, key in enumerate(attributes):
                    if default_index == index:
                        continue
                    if key == attributes[default_index]:
                        setattr(self, key_fields[index], defaults[index])
            attributes = [
                self.up_key, self.down_key, self.left_key,
                self.right_key, self.confirm_key, self.return_key]
        return self


class Settings(JSONModel):
    file_name: ClassVar[str] = "settings"
    lang: Languages = Field(default=Languages.ENGLISH)
    res: Resolutions = Field(default=Resolutions.SMALL)
    sfx_vol: int = Field(ge=0, le=10, default=10)
    bgm_vol: int = Field(ge=0, le=10, default=10)

    haha: str = ""

    key_config: KeyConfig = Field(default=KeyConfig())

    @field_validator("lang", mode="before")
    @classmethod
    def lang_validator(cls, value: str) -> Languages:
        try:
            if isinstance(value, Languages):
                return value
            return Languages(value)
        except Exception:
            return Languages.ENGLISH

    @field_validator("res", mode="before")
    @classmethod
    def res_validator(cls, value: Iterable[int] | str) -> Resolutions:
        try:
            if isinstance(value, Resolutions):
                return value
            if isinstance(value, str):
                if value == "fullscreen":
                    return Resolutions.FULLSCREEN
                return Resolutions(
                    list(int(side) for side in value.strip().split(",")))
            if isinstance(value, Iterable):
                return Resolutions(list(value))
        except Exception:
            return Resolutions.SMALL
