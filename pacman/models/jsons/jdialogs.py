
from pydantic import Field

from .utils import JSONModel


class Dialogs(JSONModel):
    """Class Dialogs, subclass of JSONModel

    Instantiate fields for each and every piece of text in the program. Default
    values are in english, and should be updated in a different language from
    a dictionary parsed from its corresponding json file.
    """
    title: str = Field(default="Pac-Man")
    play: str = Field(default="Play")
    highscores: str = Field(default="Highscores")
    settings: str = Field(default="Settings")
    quit: str = Field(default="Quit")

    lang: str = Field(default="Language")
    res: str = Field(default="Window")
    fullscreen: str = Field(default="fullscreen")
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

    resume: str = Field(default="Resume")
    back_to_main: str = Field(default="back to main menu")
