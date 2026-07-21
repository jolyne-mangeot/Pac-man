
from typing import ClassVar

from .utils import JSONModel


class Config(JSONModel):
    file_name: ClassVar[str] = "config"
