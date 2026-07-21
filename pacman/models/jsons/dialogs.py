
from typing import ClassVar
from pydantic import Field

from .utils import JSONModel


class Dialogs(JSONModel):
    file_name: ClassVar[str] = ""

    title: str = Field(default="Pac-Man")
    play: str = Field(default="Play")
    settings: str = Field(default="Settings")
    quit: str = Field(default="Quit")
