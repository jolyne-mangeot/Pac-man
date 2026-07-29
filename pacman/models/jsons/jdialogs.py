
from typing import ClassVar
from pydantic import Field

from .utils import JSONModel


class Dialogs(JSONModel):
    file_name: ClassVar[str] = ""

    title: str = Field(default="Pac-Man")
    play: str = Field(default="Play")
    highscores: str = Field(default="Highscores")
    settings: str = Field(default="Settings")
    quit: str = Field(default="Quit")

    lang: str = Field(default="Language")
    res: str = Field(default="Resolution")
    sfx_vol: str = Field(default="SFX volume")
    bgm_vol: str = Field(default="BGM volume")
    up_key: str = Field(default="up")
    down_key: str = Field(default="down")
    left_key: str = Field(default="left")
    right_key: str = Field(default="right")
    confirm_key: str = Field(default="confirm")
    return_key: str = Field(default="return")
    reset_settings: str = Field(default="reset settings")
    apply: str = Field(default="apply")
    back: str = Field(default="back")
