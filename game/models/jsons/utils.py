
from json import JSONDecoder, load
from typing import Any, ClassVar, Annotated
from collections.abc import Callable

from pydantic import (
    BaseModel, Field, field_validator, ValidationInfo, model_serializer,
    SerializerFunctionWrapHandler)
from pydantic_core import PydanticUseDefault


class JSONModel(BaseModel):
    """BaseModel class JSONModel

    Parent class to all "JSON" objects, BaseModel classes made to hold
    configuration values parsed from json files and to be saves back into the
    files. Implements a validate_or_fallback field validator method to apply
    Pydantic's Field verifications but, instead of raising a ValidationError
    upon issues, falling back to the set default values to avoid unnecessary
    crashes. See the method's docstring for more details.

    ### Attribute:
    - file_name: ClassVar[str] => string containing the name of the json file
    from which the values used to instantiate the JSONModel object will be
    parsed.
    - status: bool => used by Config, Settings, Dialogs and
    Highscores only, to check if their respective file has been correctly
    opened

    ### Method:
    - serialize_model (model_serializer) => returns the dict normally obtained
    through the model_dump method after popping the file_name and status
    entries
    - validate_or_fallback (field_validator, class_method) => Field validator
    applied to every Field the subclasses can have, checking if the inserted
    value can fit in the field before returning it, otherwise returning the set
    default value.
    """
    file_name: ClassVar[str] = ""
    status: bool = False

    @model_serializer(mode='wrap')
    def serialize_model(self, handler: SerializerFunctionWrapHandler
                        ) -> dict[str, Any]:
        """As file_name and status are used internally, they are excluded when
        dumping the model into a dictionary.
        """
        serialized: dict[str, Any] = handler(self)
        serialized.pop("file_name", None)
        serialized.pop("status", None)
        return serialized

    @field_validator("*", mode="before")
    @classmethod
    def validate_or_fallback(cls, value: Any, info: ValidationInfo) -> Any:
        """Field validator applied for all Fields in this class and its
        subclasses, before Pydantic's actual verifications are made. This
        method, being a validator, receives the value inserted at construct and
        a ValidationInfo object from Pydantic, containing all informations
        about the field that's being filled.

        Recreates the field in a closed environment based on its info and tries
        to insert the value into it in a try except bloc. If no exception is
        raised, returns the value to validate it. Otherwise, raise the
        PydanticUseDefault exception which would not be possibly raised at
        this state of the verification without this validator, making
        JSONModels' instantiation easier.

        The value received as argument and returned is of type Any.

        Can raise: PydanticUseDefault
        """
        try:
            field_info: Any = (
                cls.model_fields[str(info.field_name)].asdict())

            class DummyClass(BaseModel):
                """Dummy class created to test the JSONModel's fields one by
                one with the associated value. Recreates the pertinent field
                from a ValidationInfo object.
                """
                field_copy: Annotated[
                    Any, *field_info["metadata"],
                    Field(**field_info["attributes"])]

            DummyClass(field_copy=value)
            return value
        except Exception:
            print(
                f"On {cls.__name__} parsing, the value {value} for the entry",
                f"{info.field_name} is invalid, defaulting value.")
            raise PydanticUseDefault


class JSONCommentedDecoder(JSONDecoder):
    """Class JSONCommentedDecoder, subclass of JSONDecoder (json module)

    Implemented class to override JSONDecoder's decode method, during which
    the string recovered from the json file is parsed into a dict typed Any.

    This enables the skipping of any comments within the file as they are not
    part of the basic json implementation. Supports lines starting with "//"
    and "#", even with whitespaces before.

    Attributes are declared by JSONDecoder's init method with no explicit
    argument.

    ### Method:
    - decode (override) => Override of the decode method to modify the string
    read from the json file before it's parsed into a dictionary.
    """
    def decode(self, s: str, _: Callable[..., Any] = lambda: "") -> Any:
        """Override of the JSONDecoder method, taking in the same arguments
        given by json's module load function. Modify the s string to remove
        lines starting with "//" and "#" considered as comments.

        Returns the original decode implementation with the modified s.
        """
        s = '\n'.join(line if not (
            line.lstrip().startswith("//")
            or line.lstrip().startswith("#")
            ) else "" for line in s.split("\n"))
        return super().decode(s)


def check_missing_json_entry(
        model: type[JSONModel], config: dict[Any, Any]) -> None:
    """For each missing key to create a JSONModel object in the given config
    dict, print an explicit warning message in the terminal
    """
    missings: list[str] = [
        key for key in model.model_fields.keys()
        if key not in (*config.keys(), "status", "file_name")]
    if missings != []:
        print(
            f"On {model.__name__} parsing, entries: {missings} are "
            "missing, defaulting or randomizing value.")
        print()


def json_to_model(model: type[JSONModel], file_path: str = "") -> JSONModel:
    """Function made to easily import a json file into a JSONModel object.
    Takes a JSONModel type and optional file_path as string.

    The model is inspected for its file_name to recreate the file's path if the
    file_path argument is empty. In a try except block, opens the file and
    loading it using the json's module load function with the cls argument
    being the above declared JSONCommentedDecoder. Returns an instantiation of
    the model type by unpacking the config_dict in its constructor, with status
    at True.

    If any Exception is raised, return the model's constructor.
    """
    path: str = (file_path if file_path != ""
                 else "game/" + model.file_name + ".json")
    try:
        with open(path, "r") as file:
            config_dict: dict[str, Any] = load(file, cls=JSONCommentedDecoder)
            for key in [key for key in config_dict.keys()
                        if key not in model.model_fields.keys()]:
                print(
                    f"On {model.__name__} parsing, entry {key} is missing, "
                    "defaulting or randomizing value.")
            config_dict.pop("status", "")
            return model(status=True, **config_dict)
    except (FileNotFoundError, PermissionError):
        return model(status=False)


def model_to_json(model: JSONModel, file_path: str = "") -> bool:
    """Takes a JSONModel object and an optional file_path to save its content
    back into a json file.

    The model is inspected for its file_name to recreate the file's path if the
    file_path argument is empty. In a try except block, opens the file and
    write it with the model_dump_json BaseModel method, excluding the
    file_name field.
    """
    success: bool = False
    path: str = (file_path if file_path != ""
                 else "game/" + model.file_name + ".json")
    try:
        with open(path, "w") as file:
            format: str = model.model_dump_json(
                indent=4, warnings="error")
            print(format, file=file)
            print(
                "Information written out from Model of type "
                f"{model.__class__.__name__}:\n{format}")
            success = True
    except PermissionError:
        pass
    return success
