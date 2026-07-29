
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from typing import Any


class Option(ABC):
    """Abstract class Option:

    Class made to contain all attributes and methods to update a container's
    value based on different behaviors and input handling.

    ### Attributes:
    - name: str => name of the instantiated option, must correspond to a key
    in the container if the option object will modify a value
    - text: str => text returned by the str method when printing the object,
    if the container contains a value by the name of the option, formats it
    into the text with value=container[name] format
    - container: dict[str, Any] => dict reference to be modified by the option
    if needed

    ### Methods:
    - str => return the text attribute, formatted if the option's name is a key
    in the container
    - input_event (abstract) => takes an action and a raw_input to handle
    different behavior and update the container's values if needed
    """
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}) -> None:
        """Assign name, text and container arguments to the Option object."""
        self.name: str = name
        self.text: str = text
        self.container: dict[str, Any] = container

    def __str__(self) -> str:
        """Returns self.text formatted with the corresponding value from
        the container dict if appropriate. The format is called by inserting
        the container's value into a "value" format flag.
        (ex: self.text="I am {value}")
        """
        if self.container.get(self.name, None) is not None:
            return self.text.format(
                value=str(self.container.get(self.name)).replace("_", " "))
        return self.text

    @abstractmethod
    def input_event(self, action_key: str, raw_input: str) -> Any:
        """Method called to pass down input to the Option object, as an action
        and a raw_input, depending on the option's needs.
        """
        pass


class InputOption(Option):
    """Class InputOption, child of Option

    ### Attributes:
    - active =>
    - value_len =>
    - erase_text_on_pick =>
    - input_require_return =>
    - char_list =>
    - char_checker =>
    """
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}, value_len: int = 0,
            erase_text_on_pick: bool = False,
            input_require_return: bool = True, char_list: list[str] = [],
            char_checker: Callable[[str], bool] = str.isprintable) -> None:
        Option.__init__(self, name, text, container)
        self.active: bool = False
        self.value_len: int = value_len
        self.erase_text_on_pick: bool = erase_text_on_pick
        self.input_require_return: bool = input_require_return
        self.char_list: list[str] = char_list
        self.char_checker: Callable[[str], bool] = char_checker

    def __str__(self) -> str:
        """Returns self.text formatted with the corresponding value from
        the config dict if appropriate.
        """
        if self.container.get(self.name, None) is not None:
            if self.container[self.name] == "":
                return self.text.format(
                    value=str("_" * self.value_len))
            return self.text.format(
                value=str(self.container.get(self.name)).replace("_", " "))
        return self.text

    def handle_input(self, action_key: str, raw_input: str) -> str:
        if len(self.container[self.name]) < self.value_len and (
                (self.char_list != [] and raw_input in self.char_list)
                or (self.char_list == [] and self.char_checker(raw_input))):
            self.container[self.name] += raw_input
            if (self.input_require_return is False
                    and len(self.container[self.name]) >= self.value_len):
                self.active = False
                return "action_done"
        elif (raw_input == "backspace"
                and len(self.container[self.name]) > 0):
            self.container[self.name] = (
                self.container[self.name][:-1])
        elif raw_input == "return" or (
                raw_input.isalpha() is False and action_key == "confirm_key"):
            self.active = False
            return "action_done"
        return ""

    def input_event(self, action_key: str, raw_input: str) -> Any:
        if self.active is False:
            self.active = True
            if self.erase_text_on_pick is True:
                self.container[self.name] = ""
            return ""
        return self.handle_input(action_key, raw_input)


class SliderOption(Option):
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}, value_range: range = range(0, 0),
            up_factor: int = 10, down_factor: int = 10, left_factor: int = 1,
            right_factor: int = 1) -> None:
        Option.__init__(self, name, text, container)
        self.value_range: range = value_range
        self.up_factor: int = up_factor
        self.down_factor: int = down_factor
        self.left_factor: int = left_factor
        self.right_factor: int = right_factor

    def value_up(self, factor: int) -> None:
        """Handles the modification of slider values upward by the given
        factor, checking if the upper limit is reached and updating the
        corresponding config entry accordingly.
        """
        value: int = int(self.container[self.name])
        value += factor
        if value > self.value_range[-1]:
            value = self.value_range[0]
        self.container[self.name] = str(value)

    def value_down(self, factor: int) -> None:
        """Handles the modification of slider values downward by the given
        factor, checking if the lower limit is reached and updating the
        corresponding config entry accordingly.
        """
        value: int = int(self.container[self.name])
        value -= factor
        if value < self.value_range[0]:
            value = self.value_range[-1]
        self.container[self.name] = str(value)

    def input_event(self, action_key: str, _: str) -> Any:
        actions: dict[str, partial[None]] = {
            "up_key": partial(self.value_up, self.up_factor),
            "down_key": partial(self.value_down, self.down_factor),
            "left_key": partial(self.value_down, self.left_factor),
            "right_key": partial(self.value_up, self.right_factor)}
        actions.get(action_key, lambda: "")()


class ActivateOption(Option):
    def __init__(
            self, name: str, text: str,
            exec: partial[Any] = partial(lambda: "")) -> None:
        Option.__init__(self, name, text)
        self.exec: partial[Any] = exec

    def input_event(self, action_key: str, _: str) -> Any:
        if action_key == "confirm_key":
            return self.exec()
        return ""


class SelectionOption(Option):
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}, options: list[Any] = [],) -> None:
        Option.__init__(self, name, text, container)
        self.options: list[str] = options

    def selection_left(self) -> None:
        """Updates the pertinent container dict entry, by switching the
        selected value with the one preceding it in the options list.
        """
        self.container[self.name] = self.options[
            self.options.index(self.container[self.name]) - 1]

    def selection_right(self) -> None:
        """Updates the pertinent container dict entry, by switching the
        selected value with the one following it in the options list.
        """
        self.container[self.name] = self.options[
            (self.options.index(self.container[self.name]) + 1)
            % len(self.options)]

    def input_event(self, action_key: str, _: str) -> Any:
        actions: dict[str, Callable[[], None]] = {
            "left_key": self.selection_left,
            "right_key": self.selection_right}
        actions.get(action_key, lambda: "")()


class ToggleOption(Option):
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}) -> None:
        Option.__init__(self, name, text, container)

    def toggle(self) -> None:
        """Switch to "True" or "False" the corresponding config entry
        if the Option object is of type "toggle", otherwise return the calling
        of the exec attribute if the option_type is "activate".
        """
        if self.container[self.name] == "True":
            self.container[self.name] = "False"
        else:
            self.container[self.name] = "True"

    def input_event(self, action_key: str, _: str) -> Any:
        if action_key == "confirm_key":
            self.toggle()
