
from json import JSONDecoder, load
from typing import Any, ClassVar, Annotated
from collections.abc import Callable

from pydantic import BaseModel, Field, field_validator, ValidationInfo
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

    ### Method:
    validate_or_fallback (field_validator, class_method) => Field validator
    applied to every Field the subclasses can have, checking if the inserted
    value can fit in the field before returning it, otherwise returning the set
    default value.
    """
    file_name: ClassVar[str] = ""

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
                    Any,
                    *field_info["metadata"],
                    Field(**field_info["attributes"])]

            DummyClass(field_copy=value)
            return value
        except Exception:
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


def json_to_model(
        model: type[JSONModel], file_path: str = "",
        extra_args: dict[str, Any] = {}, sub_dict: str = "") -> JSONModel:
    """Function made to easily import a json file into a JSONModel object.
    Takes a JSONModel type, and optional file_path as string, extra_args as
    dict and sub_dict as str.

    The model is inspected for its file_name to recreate the file's path if the
    file_path argument is empty. In a try except block, opens the file and
    loading it using the json's module load funtion with the cls argument
    being the above declared JSONCommentedDecoder. If sub_dict is not empty,
    The config_dict that's later returned is zoomed on its entry corresponding
    to the sub_dict string key. In any case, updates this config_dict with the
    extra_args argument before returning an instantiation of the model type
    by unpacking the config_dict in its constructor.

    If any Exception is raised, return the model's constructor with the
    extra_args.

    *(for clarity, the sub_dict argument should be used if the dict that needs
    to be parsed into the model is an entry in the json file, rather than
    its general dictionary.)*
    """
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
    """Takes a JSONModel object and an optional file_path to save its content
    back into a json file.

    The model is inspected for its file_name to recreate the file's path if the
    file_path argument is empty. In a try except block, opens the file and
    write it with the model_dump_json BaseModel method, excluding the
    file_name field.
    """
    path: str = (file_path if file_path != ""
                 else "pacman/" + model.file_name + ".json")
    with open(path, "w") as file:
        format: str = model.model_dump_json(
            indent=4, exclude={"file_name"}, warnings="error")
        print(format, file=file)
        print(
            "Information written out from Model of type "
            f"{model.__class__.__name__}:\n{format}")
