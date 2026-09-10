
from typing import Any, ClassVar, Iterable

from pydantic import BaseModel, Field, field_validator, ValidationError

from .utils import JSONModel


class Score(BaseModel):
    player: str = Field(max_length=10)
    score: int = Field(ge=0)
    level_reached: int = Field(gt=0)
    time_taken: int = Field(ge=0)
    remaining_lives: int = Field(ge=0)

    @field_validator("player", mode="after")
    @staticmethod
    def name_validator(value: str) -> str:
        if value.isalnum() is True:
            return value
        else:
            raise ValidationError


class Highscores(JSONModel):
    file_name: ClassVar[str] = "highscores"

    scores: list[Score] = Field(max_length=10, default=[])

    @field_validator("scores", mode="before")
    @staticmethod
    def scores_validator(value: Any) -> Any:
        scores: list[Score] = []
        if isinstance(value, Iterable):
            for score in value:
                if isinstance(score, Score):
                    scores.append(score)
                elif isinstance(score, dict):
                    try:
                        scores.append(Score(**score))
                    except ValidationError:
                        continue
            scores = sorted(scores, key=lambda sc: sc.score, reverse=True)
            if len(scores) > 10:
                scores = scores[:10]
        return scores
