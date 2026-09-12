
from typing import Any, ClassVar, Iterable

from pydantic import BaseModel, Field, field_validator, ValidationError

from .utils import JSONModel


class Score(BaseModel):
    """Class Score, subclass of BaseModel

    As this class's instance will be used for displaying only, and depends on
    the user's scores, any faulty values will consider the scoring flawed and
    will be skipped during the parsing.

    ### Attributes:
    - player: str => name of the player who saved the score
    - score: int => value of the score itself
    - level_reached: int => level reached before saving the score
    - time_taken: int => time in seconds that went down during all levels
    - remaining_lives: int => lives remaining at the end of the run

    ### Method:
    - name_validator => checks if the name passes the name's policy of it being
    max 10 letters and/or numbers

    Can raise a ValidationError
    """
    player: str = Field(max_length=10)
    score: int = Field(ge=0)
    level_reached: int = Field(gt=0)
    time_taken: int = Field(ge=0)
    remaining_lives: int = Field(ge=0)

    @field_validator("player", mode="after")
    @staticmethod
    def name_validator(value: str) -> str:
        """Checker called after the name is already checked to be a string of
        max length 10. If the names is only made of letters and numbers,
        returns it, and otherwise raise a ValidationError.
        """
        if value.isalnum() is True:
            return value
        else:
            raise ValidationError


class Highscores(JSONModel):
    """Class Highscores, subclass of JSONModel

    Class used to store a list of all highscores to be displayed in the
    dedicated menu.

    ### Attributes:
    - file_name: ClassVar[str] => name of the file containing the scores to
    parse
    - scores: list[Score] => a list of Score objects sorted in a decreasing
    order based on the value of the saved score
    """
    file_name: ClassVar[str] = "highscores"

    scores: list[Score] = Field(max_length=10, default=[])

    @field_validator("scores", mode="before")
    @staticmethod
    def scores_validator(value: Any) -> Any:
        """If the value is an Iterable, for each of its elements, if its a
        Score object, appends it to a list, and if it's a non-empty dict,
        tries creating a Score object with its values. If a ValidationError
        is raised, skips the item.

        Returns the newly created list.
        """
        scores: list[Score] = []
        if isinstance(value, Iterable):
            for score in value:
                if isinstance(score, Score):
                    scores.append(score)
                elif isinstance(score, dict) and len(score) > 0:
                    try:
                        scores.append(Score(**score))
                    except ValidationError:
                        continue
            scores = sorted(scores, key=lambda sc: sc.score, reverse=True)
            if len(scores) > 10:
                scores = scores[:10]
        return scores
