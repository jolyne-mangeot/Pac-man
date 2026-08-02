
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from typing import Any


class Option(ABC):
    """Abstract class Option:

    Class made to contain all attributes and methods to update a container's
    value based on different behaviors and input handling.

    ### Attributes:
    - name: str (parameter) => name of the instantiated option, must correspond
    to a key in the container if the option object will modify a value
    - text: str (parameter) => text returned by the str method when printing
    the object, if the container contains a value by the name of the option,
    formats it into the text with value=container[name] format
    - container: dict[str, Any] (parameter) => dict reference to be modified by
    the option if needed
    - selectable: bool => self attributed boolean that can be overridden by
    subclasses. If False, the Menu class will skip over the option during
    navigation
    - pickable: bool => same as selectable, but the option will be selectable
    during navigation. The input_event method will still be called, useful
    for Activate and Toggle subclasses
    option needs a pygame.TEXTINPUT event rather than a pygame.KEYDOWN event

    ### Methods:
    - str => return the text attribute, formatted if the option's name is a key
    in the container
    - activate => Called when an option is picked, declared here for any Option
    subclass to be overridden with specialized behavior.
    - deactivate => Called when an option is let down
    - input_event (abstract) => takes an action and a named_key to handle
    different behavior and update the container's values if needed
    """
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}) -> None:
        """Assign name, text and container arguments to the Option object."""
        self.name: str = name
        self.text: str = text
        self.container: dict[str, Any] = container
        self.selectable: bool = True
        self.pickable: bool = True

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

    def activate(self) -> None:
        """Called when an option is picked, declared here for any Option
        subclass to be overridden with specialized behavior.
        """
        pass

    def deactivate(self) -> None:
        """Called when an option is let go of, declared here for any Option
        subclass to be overridden with specialized behavior.
        """
        pass

    @abstractmethod
    def input_event(
            self, action_key: str, named_key: str, text_input: str) -> Any:
        """Method called to pass down input to the Option object, as an action
        and/or a named_key, and a text_input, depending on the option's needs.
        """
        pass


class Spacer(Option):
    """Class Spacer, subclass of Option

    Dummy class to be declared with no argument, useful to separate options in
    a list and create more organised menues. Created to avoid handling None
    values instead.

    ### Attributes:
    - All needed Option attributes to run properly: name, text, container,
    selectable (False), pickable (False).

    ### Methods:
    - *Option instance methods*
    - str (override) => returns an empty string
    - input_event (override) => pass
    """
    def __init__(self) -> None:
        """No arguments, instantiate all Option mandatory attributes with
        dummy values:

        name="spacer", text="", container={}, selectable=False, pickable=False
        """
        self.name: str = "spacer"
        self.text: str = ""
        self.container: dict[str, Any] = {}
        self.selectable: bool = False
        self.pickable: bool = False

    def __str__(self) -> str:
        """Return an empty string. Override of Option to skip conditions."""
        return ""

    def input_event(self, _: str, __: str, ___: str) -> Any:
        """Does nothing. Override of Option for correct implementation"""
        pass


class ActivateOption(Option):
    """Class ActivateOption, subclass of Option

    Made for options to execute functions or methods. Accepts partial returning
    Any, meaning arguments have to be preentered.

    ### Attributes:
    - *Option instance parameters and attributes*
    - exec: partial[Any] (parameter) => function to execute when input_event
    is called with "activate" as argument
    - pickable: bool => Pickable set to False not to be picked by Menu objects

    ### Methods:
    - *Option instance methods*
    - input_event (override) => if action_key is "activate", returns the
    execution of self.exec
    """
    def __init__(
            self, name: str, text: str,
            exec: partial[Any] = partial(lambda: "")) -> None:
        """Initializes ActivateOption attributes with the given parameters and
        Option.__init__.
        """
        Option.__init__(self, name, text)
        self.exec: partial[Any] = exec
        self.pickable: bool = False

    def input_event(self, action_key: str, _: str, __: str) -> Any:
        """If action_key is "activate", returns the execution of self.exec."""
        if action_key == "activate":
            return self.exec()


class ToggleOption(Option):
    """Class ToggleOption, subclass of Option

    ### Attributes:
    - *Option instance parameters and attributes*
    - pickable: bool => Set to False, meaning this option won't be able to be
    picked by Menu objects

    ### Methods:
    - *Option instance methods*
    - toggle => When called, switch from True to False or vice-versa the value
    in the container.
    - input_event (override) => Calls self.toggle if the action as input is
    "activate", otherwise does nothing.
    """
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}) -> None:
        """Initializes ToggleOption attributes with the given parameters and
        Option.__init__.
        """
        Option.__init__(self, name, text, container)
        self.pickable: bool = False

    def toggle(self) -> None:
        """Switch to True or False the corresponding config entry."""
        if self.container[self.name] == "True":
            self.container[self.name] = "False"
        else:
            self.container[self.name] = "True"

    def input_event(self, action_key: str, _: str, __: str) -> Any:
        """If action_key is "activate", calls self.toggle."""
        if action_key == "activate":
            self.toggle()


class SliderOption(Option):
    """Class SliderOption, subclass of Option

    Useful for numeric sliders. Using a range and different factors for each
    direction inputs, updates the container accordingly. Can choose if the
    value cycles around the range or not.

    ### Attributes:
    - *Option instance parameters and attributes*
    - value_range: range => Range used to check if the value in the container
    is correct
    - up_factor: int => factor applied to the value when "up_key" is sent as
    input
    - down_factor: int => factor for down action
    - left_factor: int => factor for left action
    - right_factor: int => factor for right action
    - cycle: bool => boolean checked when the value reaches a range's limit,
    if True the value will cycle back to the opposite range limit, otherwise
    it will sit at the limit that was first reached

    ### Methods:
    - *Option instance methods*
    - update_value => Apply the factor in argument to the value in the
    container, checking for range limits
    - input_event (override) => executes update_values with the corresponding
    factor if a direction key is pressed.
    """
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}, value_range: range = range(0, 0),
            up_factor: int = 10, down_factor: int = -10, left_factor: int = -1,
            right_factor: int = 1, cycle: bool = True) -> None:
        """Initializes SliderOption attributes with the given parameters and
        Option.__init__.
        """
        Option.__init__(self, name, text, container)
        self.value_range: range = value_range
        self.up_factor: int = up_factor
        self.down_factor: int = down_factor
        self.left_factor: int = left_factor
        self.right_factor: int = right_factor
        self.cycle: bool = cycle

    def update_value(self, factor: int) -> None:
        """Handles the modification of slider values by the given
        factor, checking if any range limit is reached and updating the
        corresponding config entry accordingly.
        """
        value: int = int(self.container[self.name])
        value += factor
        if value > self.value_range[-1]:
            value = self.value_range[0 if self.cycle else -1]
        elif value < self.value_range[0]:
            value = self.value_range[-1 if self.cycle else 0]
        self.container[self.name] = value

    def input_event(self, action_key: str, _: str, __: str) -> Any:
        """Calls update_values with the correct factor depending on the
        direction action (up_key, down_key, left and right). If the
        action argument doesn't correspond to any valid direction, returns
        None.
        """
        factors: dict[str, int] = {
            "up_key": self.up_factor,
            "down_key": self.down_factor,
            "left_key": self.left_factor,
            "right_key": self.right_factor}
        if factors.get(action_key, 0) == 0:
            return
        self.update_value(factors.get(action_key, 0))


class SelectionOption(Option):
    """Class SelectionOption, subclass of Option

    Option to use if the value in the container needs to be part of a list of
    options. When interacted with, this option will update the value with ones
    from the list given at construct. Tries to avoid exceptions (see below).

    ### Attributes:
    - *Option instance parameters and attributes*
    - options: list[Any] => list of elements to choose from to assign a value
    in the container
    - up_factor: int => factor applied to the reference value's index in the
    options list when "up_key" is sent as input
    - down_factor: int => factor for down action
    - left_factor: int => factor for left action
    - right_factor: int => factor for right action
    - cycle: bool => boolean checked when the value reaches the selection's
    limit, if True the value will cycle back to the opposite selection limit,
    otherwise it will sit at the limit that was first reached

    ### Methods:
    - *Option instance methods*
    - update_selection => updates the value in the container by updating the
    index of the reference value in the options list, tries to handle errors,
    default to the first elements in the list if the original value is missing
    in it and defaulting to None if the options list is empty.
    - input_event (override) => calls update_selection with the factor
    corresponding to the action_key input as argument, accepting up_key,
    down_key left_key and right_key, otherwise doing nothing
    """
    def __init__(
            self, name: str, text: str, container: dict[str, Any] = {},
            options: list[Any] = [], up_factor: int = 0,
            down_factor: int = 0, left_factor: int = -1,
            right_factor: int = 1, cycle: bool = True) -> None:
        """Initializes SelectionOption attributes with the given parameters and
        Option.__init__.
        """
        Option.__init__(self, name, text, container)
        self.options: list[str] = options
        self.up_factor: int = up_factor
        self.down_factor: int = down_factor
        self.left_factor: int = left_factor
        self.right_factor: int = right_factor
        self.cycle: bool = cycle

    def update_selection(self, factor: int) -> None:
        """Updates the pertinent container dict entry, by switching the
        selected value with the one preceding it in the options list.
        """
        try:
            index: int = self.options.index(self.container[self.name])
            index += factor
            if index < 0:
                index = len(self.options) - 1 if self.cycle else 0
            elif index > len(self.options) - 1:
                index = 0 if self.cycle else len(self.options) - 1
        except ValueError:
            index = 0
        try:
            self.container[self.name] = self.options[index]
        except IndexError:
            self.container[self.name] = None

    def input_event(self, action_key: str, _: str, __: str) -> Any:
        """Calls self.update_selection with the factor corresponding to the
        direction action_key given as argument ("up_key", "down_key", etc.).
        If the action doesn't correspond to a direction, does nothing.
        """
        factors: dict[str, int] = {
            "up_key": self.up_factor,
            "down_key": self.down_factor,
            "left_key": self.left_factor,
            "right_key": self.right_factor}
        if factors.get(action_key, 0) == 0:
            return
        self.update_selection(factors.get(action_key, 0))


class InputOption(Option):
    """Class InputOption, subclass of Option

    Option made to receive input and update a string with it. Handles named key
    input (like up, down, space) and raw text. Named key input should be
    reserved for short input cells such as key bindings and make it easier to
    notice the user of which key they just pressed. Raw text handle the
    keyboard inputs normally. Different flags are implemented and described
    below in attributes.

    ### Attributes:
    - *Option instance parameters and attributes*
    - value_len (parameter): int => maximum len of the text field
    - value_save: str => becomes the value in the container at construct,
    use for implementing revert_to_default flag described below
    - use_text_input (parameter): bool => declares if the incoming input should
    be raw characters like ' ' instead of named keys like 'space'. Enables
    the use of handle_text_input method
    - erase_text_on_pick (parameter): bool => when the option becomes active,
    it can erase the current corresponding value in the container dict
    - input_require_return (parameter): bool => when the value_len has been
    reached, input handling methods return "action_done"
    - revert_to_default (parameter): bool => when the option becomes inactive,
    if this is True and the container's value is empty, its value when first
    being activated is placed back
    - excluded_input: list[str] => holds unique strings to ignore when
    checking the input is validated, even though they would pass the
    character checker.
    - char_checker (parameter): Callable[[str], bool] => function used to
    verify the coming named_key, defaulted to str.isprintable in a lambda
    function

    ### Methods:
    - *Option instance methods*
    - str (override) => same as Option's str, except placing underscores in the
    value's place when it is empty
    - activate (override) => implement the use of the revert_to_default,
    use_text_input and erase_text_on_pick flags by saving the container's value
    in value_save and assigning an empty
    string to the value if needed
    - deactivate (override) => checks if the value is empty at leaving, and if
    the corresponding flag is True, reinstore the value_save if needed.
    - is_input_valid => short method returning the condition of the value being
    shorter than its limit, the input not being excluded and passing the
    character checker
    - handle_input => method handling named key inputs, can have unexpected
    behaviors regarding backspace if the value_len is above 9 so should be
    reserved for single key inputs with use_text_input attribute set to False
    - handle_text_input => called when use_text_input is True and should take
    key inputs as they would appear in normal sentences (' ' instead of
    'space'), doesn't check for the action_key associated with the input and
    relies on backspace to erase characters (cannot move within string with
    directions)
    - input_event (override) => check for "activate" action as it is linked to
    the named_key of the return key and would cause problems, returning an
    empty string in this case, and otherwise calls and returns handle_input or
    handle_text_input depending on the flags.
    """
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}, value_len: int = 0,
            use_text_input: bool = True,
            erase_text_on_pick: bool = False,
            input_require_return: bool = True,
            revert_to_default: bool = True,
            excluded_input: list[str] = [],
            char_checker: Callable[[str], bool] = (
                lambda s: str.isprintable(s))) -> None:
        """Initializes InputOption attributes with the given parameters and
        Option.__init__.
        """
        Option.__init__(self, name, text, container)
        self.value_len: int = value_len
        self.value_save: str = container[self.name]
        self.use_text_input: bool = use_text_input
        self.revert_to_default: bool = revert_to_default
        self.erase_text_on_pick: bool = erase_text_on_pick
        self.input_require_return: bool = input_require_return
        self.excluded_input: list[str] = excluded_input
        self.char_checker: Callable[[str], bool] = char_checker

    def __str__(self) -> str:
        """Returns self.text formatted with the corresponding value from
        the config dict if appropriate. Replace said value with underscores if
        it is an empty string.
        """
        if self.container.get(self.name, None) is not None:
            if str(self.container[self.name]) == "":
                return self.text.format(value=str("_" * self.value_len))
            return self.text.format(value=str(self.container.get(self.name)))
        return self.text

    def activate(self) -> None:
        """Override of Option's, called when the option is picked by a Menu.
        Apply the revert_to_default and erase_text_on_pick
        flags by:
        - saving the current value in the value_save attribute,
        - replacing the value with an empty string if erase_text_on_pick is
        True
        """
        self.value_save = self.container[self.name]
        if self.erase_text_on_pick is True:
            self.container[self.name] = ""

    def deactivate(self) -> None:
        """Override of Option's, called when the option is let down by a Menu.
        Apply the revert_to_default flags by:
        - replacing the value with the value_save if revert_to_default is
        True and the value is left empty
        """
        if self.revert_to_default and self.container[self.name] == "":
            self.container[self.name] = self.value_save

    def is_input_valid(self, input: str) -> bool:
        """Method returning a condition based on the input argument, checking:
        - if the len of the current value is under the max value_len,
        - if the input is not in the excluded_input,
        - if the input passes the char_checker function
        """
        return (len(self.container[self.name]) < self.value_len and
                input not in self.excluded_input and self.char_checker(input))

    def handle_input(self, action_key: str, named_key: str) -> str:
        """Takes an action_key and named_key, both string. Action_key should
        be "return_key" to have an effect, and the named_key is thought to be
        a named key input like "space" or "escape". For full text handling,
        toggle the use_text_input flag to True and handle_text_input will be
        called by the input_event method.

        Checks the rawr_input with is_input_valid. If there is at least one
        space in the value, appends the named_key, and if the
        input_require_return flag is False and the value's len has reached
        the value_len, this method returns "action_done".

        If the named_key is "backspace" or the action_key is "return_key",
        the last character of the value is removed.

        Returns an empty string at the end of the method.
        """
        if self.is_input_valid(named_key):
            print(named_key, flush=True)
            self.container[self.name] += named_key
            if (self.input_require_return is False
                    and len(self.container[self.name]) >= self.value_len):
                return "action_done"
        elif (named_key == "backspace" or action_key == "return_key"
                and len(self.container[self.name]) > 0):
            self.container[self.name] = self.container[self.name][:-1]
        return ""

    def handle_text_input(self, named_key: str, text_input: str) -> str:
        """Takes a named_key string as argument.

        Checks the named_key with is_input_valid. If there is at least one
        space in the value, appends the named_key, and if the
        input_require_return flag is False and the value's len has reached
        the value_len, this method returns "action_done".

        If the named_key is "backspace", the last character of the value is
        removed.

        Returns an empty string at the end of the method.
        """
        if named_key == "backspace":
            if len(self.container[self.name]) > 0:
                self.container[self.name] = self.container[self.name][:-1]
        elif self.is_input_valid(text_input):
            self.container[self.name] += text_input
            if (self.input_require_return is False
                    and len(self.container[self.name]) >= self.value_len):
                return "action_done"
        return ""

    def input_event(
            self, action_key: str, named_key: str, text_input: str) -> Any:
        """Takes an action_key and a named_key arguments, both strings.

        Checks for "activate" action as it is linked to
        the named_key of the return key and would cause problems in the handler
        methods, returning an empty string in this case, and otherwise calls
        and returns handle_input or handle_text_input depending on the
        use_text_input flag.
        """
        if action_key == "activate":
            return ""
        if self.use_text_input is True:
            return self.handle_text_input(named_key, text_input)
        return self.handle_input(action_key, named_key)
