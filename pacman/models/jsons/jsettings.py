
from typing import ClassVar, Iterable, Final
from enum import Enum

from pydantic import Field, field_validator, model_validator
from pydantic_core import PydanticUseDefault
import pygame as pg

from .utils import JSONModel


class Languages(Enum):
    """Class Languages, subclass of SettingsEnum

    Contains the name of the language and its unique string indentification
    used to open the right file containing all dialogs translated in the
    corresponding language.

    English is an exception as no file for it exists, the english dialogs
    being the default values of the Dialogs JSONModel class.

    ### Attributes:
    - ENGLISH: "en-en"
    - FRENCH: "fr-fr"
    """
    def __str__(self) -> str:
        """Override of the Enum str method to return a string cast of the
        entry's value.
        """
        return str(self.value)

    ENGLISH = "en-en"
    FRENCH = "fr-fr"


class Resolutions(Enum):
    """Class Resolutions, subclass of SettingsEnum

    Contains names and numeric values for different window resolutions in the
    4:3 format. These numeric values are held in lists, except for the
    fullscreen entry being a litteral string.

    ### Attributes:
    - TINY: [640, 480]
    - SMALL: [800, 600]
    - MEDIUM: [1024, 768]
    - BIG: [1440, 1080]
    - TV: [1920, 1440]
    - FULLSCREEN: "fullscreen"
    """
    def __str__(self) -> str:
        """Override of the Enum str method to return a string cast of the
        entry's value.
        """
        if isinstance(self.value, str):
            return str(self.value)
        return str(self.value[0]) + "x" + str(self.value[1])

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
    """Class KeyConfig, subclass of JSONModel

    BaseModel class made to hold the program's key bindings. Has implementation
    for the four directions, confirm and return keys, defaulted to different
    values. A field validator and a model validator are declared to check for
    correct inputs and avoid duplicates.

    ### Attributes:
    - file_name: ClassVar[str] => attribute set to a literal string "settings"
    - up_key: str => key for the up movement defaulted to "up"
    - down_key: str => key for the down movement defaulted to "down"
    - left_key: str => key for the left movement defaulted to "left"
    - right_key: str => key for the right movement defaulted to "right"
    - confirm_key: str => key for the confirm action defaulted to "return"
    - return_key: str => key for the return action defaulted to "escape"

    ### Methods:
    - pg_key_validator (field_validator, class_method) => Checks if each passed
    key has an associated pygame key_code, otherwise returning the field's
    default value
    - check_key_duplicates (model_validator) => Loops through each key field,
    defaulting them until there are no duplicates
    """
    file_name: ClassVar[str] = "settings"
    up_key: str = Field(default="up")
    down_key: str = Field(default="down")
    left_key: str = Field(default="left")
    right_key: str = Field(default="right")

    confirm_key: str = Field(default="return")
    return_key: str = Field(default="escape")

    @field_validator("up_key", "down_key", "left_key", "right_key",
                     "confirm_key", "return_key", mode="before")
    @classmethod
    def pg_key_validator(cls, value: str) -> str:
        """Applied to all key fields. Takes the passed value as argument and
        check with the pygame key_code method to see if it corresponds to a
        valid input. If not, raise PydanticUseDefault exception.
        """
        try:
            pg.key.key_code(value)
            return value
        except Exception:
            raise PydanticUseDefault

    @model_validator(mode="after")
    def check_key_duplicates(self) -> "KeyConfig":
        """Model validator called after Pydantic's validations, checking for
        any duplicates in the keys. Recovers all key values as well as their
        default from the class's model_fields attributes and, until there
        are no duplicate left, loops through each default value. If the
        currently set value is the same as its own default, but another key is
        also using this input, the second key is defaulted back to its default.

        Returns self for correct validation.
        """
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
    """Class Settings, subclass of JSONModel

    BaseModel class made to hold the program's general settings. Holds Enum
    entries and int values, and implements two field validator.

    ### Attributes:
    - file_name: ClassVar[str] => attribute set to a literal string "settings"
    - lang: Languages => Languages Enum member, defaulted to ENGLISH
    - res: Resolutions => Resolution Enum member, defaulted to SMALL
    - sfx_vol: int => int for the sound effects volume, defaulted to 10
    - bgm_vol: int => int for the background music volume, defaulted to 10
    - key_config: KeyConfig => KeyConfig object holding key configuration.

    ### Methods:
    - lang_validator (field_validator, class_method) => checks if the incoming
    value is part of the Languages Enum to return it.
    - res_validator (field_validator, class_method) => tries to parse the
    incoming resolution value into a member of the Resolutions Enum
    """
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
        """Field validator for the lang field, returning a Languages Enum
        member based on the value passed as argument. Checks computed:
        - Returns the value if it's already a member of the Enum
        - Returns an Enum member from its name if the value doesn't contain
        a dash (common to all members' value)
        - Returns an Enum member from its value otherwise
        - If any Exception occurs, return Languages.ENGLISH
        """
        try:
            if isinstance(value, Languages):
                return value
            if isinstance(value, str) and "-" not in value:
                return Languages[value]
            return Languages(value)
        except Exception:
            return Languages.ENGLISH

    @field_validator("res", mode="before")
    @classmethod
    def res_validator(cls, value: Iterable[int] | str) -> Resolutions:
        """Field validator for the lang field, returning a Resolutions Enum
        member based on the value passed as argument. Checks computed:
        - Returns the value if it's already a member of the Enum
        - Returns an Enum member from its name if the value doesn't contain a
        comma (as the members' value are iterables)
        - Returns an Enum member by casting values into a list from a split
        string if value is one
        - Returns an Enum member from its value by converting value into a list
        otherwise
        - If any Exception occurs, return Resolutions.SMALL
        """
        try:
            if isinstance(value, Resolutions):
                return value
            if isinstance(value, str):
                if value == "fullscreen":
                    return Resolutions.FULLSCREEN
                if "," not in value:
                    return Resolutions[value]
                return Resolutions(
                    list(int(side) for side in value.strip().split(",")))
            return Resolutions(list(value))
        except Exception:
            return Resolutions.SMALL
