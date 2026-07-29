
from json import JSONDecoder, load
from typing import Any, ClassVar, Annotated
from collections.abc import Callable
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from pydantic_core import PydanticUseDefault


class JSONModel(BaseModel):
    file_name: ClassVar[str] = ""

    @field_validator("*", mode="before")
    @classmethod
    def validate_or_fallback(cls, value: Any, info: ValidationInfo) -> Any:
        try:
            field_info: Any = (
                cls.model_fields[str(info.field_name)].asdict())

            class DummyClass(BaseModel):
                field_copy: Annotated[
                    Any,
                    *field_info["metadata"],
                    Field(**field_info["attributes"])]

            DummyClass(field_copy=value)
            return value
        except Exception:
            raise PydanticUseDefault


class JSONCommentedDecoder(JSONDecoder):
    def __init__(self) -> None:
        super().__init__()

    def decode(self, s: str, _w: Callable[..., Any] = lambda: "") -> Any:
        s = '\n'.join(line if not (
            line.lstrip().startswith("//")
            or line.lstrip().startswith("#")
            ) else "" for line in s.split("\n"))
        _w
        return super().decode(s)


def json_to_model(
        model: type[JSONModel], file_path: str = "",
        extra_args: dict[str, Any] = {}, sub_dict: str = "") -> JSONModel:
    path: str = (file_path if file_path != ""
                 else "pacman/" + model.file_name + ".json")
    try:
        with open(path, "r") as file:
            config_dict: dict[str, Any] = load(file, cls=JSONCommentedDecoder)
            if sub_dict != "":
                config_dict = config_dict[sub_dict]
            config_dict.update(extra_args)
            return model(**config_dict)
    except (FileNotFoundError, PermissionError):
        return model(**extra_args)


def model_to_json(model: JSONModel, file_path: str = "") -> None:
    path: str = (file_path if file_path != ""
                 else "pacman/" + model.file_name + ".json")
    with open(path, "w") as file:
        format: str = model.model_dump_json(
            indent=4, exclude={"file_name"}, warnings="error")
        print(format, file=file)
        print(
            "Information written out from Model of type "
            f"{model.__class__.__name__}:\n{format}")
