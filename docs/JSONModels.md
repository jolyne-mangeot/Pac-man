### JSON parsing with comments

The parsing was done using JSON files parsed by the json module and turned into object with Pydantic's BaseModel classes

JSON files had to support comments (// and # styles), so we first had to override the JSONDecoder class implemented by the json module. To do so, we declared our own decoder and wrote a new decode method:

```python
class JSONCommentedDecoder(JSONDecoder):
    def decode(self, s: str, _w: Callable[..., Any] = lambda: "") -> Any:
        s = '\n'.join(line if not (
            line.lstrip().startswith("//")
            or line.lstrip().startswith("#")
            ) else "" for line in s.split("\n"))
        _w
        return super().decode(s)
```

Using this class, the load function of the json module will, before parsing the string into a dictionary, strip it of all its lines starting with white spaces and the comment characters.

### Building a BaseModel with fallback validations

When loaded into a dict of type `dict[str, Any]`, the information can be unpacked into the constructor of a BaseModel class using `**`. This means declaring BaseModel classes, and attributing them Fields with restraints.

```python
class Settings(JSONModel):
    file_name: ClassVar[str] = "settings"
    lang: Languages = Field(default=Languages.ENGLISH)
    res: Resolutions = Field(default=Resolutions.SMALL)
    sfx_vol: int = Field(ge=0, le=10, default=10)
    bgm_vol: int = Field(ge=0, le=10, default=10)
    key_config: KeyConfig = Field(default=KeyConfig())
```

See our Settings Model. When the json file is dumped, any missing value would be assigned its default. However, as a design choice, we'd need invalid values to also fall back to their default. Because this isn't implemented in Pydantic, we had to work around each Field's validation, thus declaring a JSONModel parent class that would generalize this step to all our json based models.

```python
class JSONModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def validate_or_fallback(cls, value: Any, info: ValidationInfo) -> Any:
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
```

This class contains only a method declared as a `field_validator`, and a `class_method`. The field validator flag takes `"*"` as argument, meaning it will be called on the verification of all Fields, and `mode="before"`, so it's called before any validation is done by Pydantic itself, so when the data is still raw out of the json files. It's also declared as a class method as, in the latest version of Pydantic, the information gathered from the Fields have to be drawn from the class itself, rather than one of its instances.

The `validate_or_fallback` method goes this way:

- It takes a `value`, corresponding to what's passed to the Field at the instance construction
- It also takes a `ValidationInfo` object, containing all information linked to the Field like its type hint, all its Field's parameters (default values, etc.) and metadata (unused here).
- With these, our method has all the tools necessary to recreate a dummy Field with all the informations from the Field that was first declared in our Model. This is where the `field_copy` is declared using an `Annotated` type hint.
- The `Annotated` type hint works when given at least a type (int, str, Any...), a metadata and/or validation or operation methods. It's another way to declare Fields that is well documented in Pydantic's documentation. The annotation here is given the type `Any` as the informations in the `ValidationInfo` are enough to validate the value's type, and using the type hint present in the info dict would raise a flake8 error.
- With this `field_copy` declared with the same information as the original Field, we can use it to pass our raw value to see if it works with the type restraints (if it's an int, if it's greater and or lower than a certain value, etc.).
- In Pydantic's classic validation, if the value didn't pass these tests, it would raise a `ValidationError`, and we would have to restart the Model's instance construction with different values. To avoid this, when our dummy class raises one such exception, we catch it and raise another one, `PydanticUseDefault`. This exception lets Pydantic know it should use the value's default value, and is available to use in any validator method we implement.
- If no exception is raised by our dummy Field, it means the value passes every conditions, and is returned, meaning Pydantic will use it to build our Model object, and we can be sure no exception will be raised then.

### Concrete examples of Field validators

Because we need to use `Enum` classes to access literal values within our program, we have to account of the fact JSON files can't store any type of values. They can hold dictionaries, iterators, integers and strings, and we have to work around this fact to parse what the user writes it their JSON files to try and link it back to our own `Enum`s.

See below two validators for two different Fields. Because they are declared with the same mode in the `field_validator` as our `validate_or_fallback` method seen above, these overrides it, so we need to implement a default fallback value here as well.

```python
	@field_validator("lang", mode="before")
	@classmethod
	def lang_validator(cls, value: str) -> Languages:
	    try:
	        if isinstance(value, Languages):
	            return value
	        if isinstance(value, str) and "-" not in value:
	            return Languages[value]
	        return Languages(value)
	    except Exception:
	        return Languages.ENGLISH

	@field_validator("res", mode="before")
	@classmethod
	def res_validator(cls, value: Iterable[int] | str) -> Resolutions:
	    try:
            if isinstance(value, Resolutions):
                return value
            if isinstance(value, str):
                if value == "fullscreen":
                    return Resolutions.FULLSCREEN
                if "," not in value:
                    return Resolutions[value]
                return Resolutions(
                    list(int(side) for side in value.strip().split(",")))
            return Resolutions(list(value))
        except Exception:
            return Resolutions.SMALL
```

`Enum`s in python are declared with a KEY, and a value of any type. To enable the use of either of the two in the input of the JSON files, we determine the multiple types of the value that could help recognize what the user is trying to access in the Enum and, if no value or KEY in recognized in the corresponding `Enum`, we return a default value.