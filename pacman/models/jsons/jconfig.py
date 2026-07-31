
from typing import ClassVar

from .utils import JSONModel


class Config(JSONModel):
    """Class Config, subclass of JSONModel

    Configuration object containing all base levels informations to run a
    functioning set of levels.
    """
    file_name: ClassVar[str] = "config"
