
from typing import Any

import pygame as pg

from pacman.models import KeyConfig, Option


def key_unicode_to_action(key_config: KeyConfig, input: str) -> str:
    """Takes a KeyConfig object and an input as string in arguments.

    Checks in the KeyConfig, which contains duos of pygame keys with their
    action, to find what action corresponds to the input key. Does so by
    looping on items in the dict version of the KeyConfig object by the
    model_dump BaseModel method.
    """
    for action, key in key_config.model_dump(exclude={"file_name"}).items():
        if key == input:
            return action
    return ""


class Menu:
    """Class Menu

    Made to list options of different types on the pygame window, and handling
    the user's input accordingly.

    Takes a list of Option subclasses objects which text's attribute to
    display in multiple available arrangements and to pass down the user's
    input to, supporting the use of different fonts and colors for the states
    of the options: deselected, selected and picked.

    ### Attributes:
    <u>Parameters:</u>
    - options: list[Option] => list containing all Option instances
    to manage the Menu

    <u>Self attributed:</u>
    - select_index: int => index of the selected option, like a cursor
    - picked_index: int => index of the picked option, which will receive
    further inputs
    - last_picked: int => index of the last picked option to update its render
    after it's been interacted with
    - rendered: dict[str, list[tuple[pg.Surface, pg.Rect]]] => options rendered
    as pygame Surfaces, saving their font, size, style and color for later
    display.
    - renders: list[tuple[pg.Surface, pg.Rect]] => list made to contain the
    render of each option to be iterated over, with the renders of the selected
    and picked options placed in.

    ### Methods:
    <u>Event handling:</u>
    - get_event => get a pygame Event object to manage options, either changing
    the selected one, picking one or deactivating one. Handles different
    visual configuration like vertical or horizontal menues.
    - get_event_vertical => handles action input to accord to a vertical
    arrangement of the options with "up_key" and "down_key" inputs
    - get_event_horizontal => handles action input to accord to a horizontal
    arrangement of the options
    - get_event_chart => handles action input to accord to a chart-like
    arrangement of the options (like table cells)
    - move_cursor => calls change_selected_option until the currently selected
    option has its attribute "selectable" on True
    - change_selected_option => Apply the factor in argument to the
    select_index, checking for range limits
    """
    def __init__(self, options: list[Option] = [],
                 loop_cursor: bool = True) -> None:
        """Initialize a Menu object with multiple arguments and self attributed
        variables. To see details on each attribute and their use, refer to the
        Menu class docstring.

        Calls pre_render_all_options at the end of the method.
        """
        self.options: list[Option] = options
        self.loop_cursor: bool = loop_cursor
        self.select_index: int = 0
        self.picked_index: int = -1
        self.last_picked: int = -1

    # _________________________________________________________________________
    #                           Events-related Methods
    # _________________________________________________________________________
    def get_event(self, key_config: KeyConfig,
                  event: pg.event.Event, arrangement: str) -> Any:
        """Takes a key_config, a pygame event and an arrangement as arguments.

        Using the currently selected option, which can also be the picked
        option, handles the way the user can interact with it.

        The input is first converted to a string, either as a text_input if
        the option needs it, or a named key, then translated into an action
        key based on the key_config. When done, if the confirm_key or
        return_key was pressed, either activate or deactivate the option by
        calling its dedicated methods, and reinitialize the picked_index to -1.

        Otherwise, pass down the event strings to the picked option by
        calling its input_event method, and recovering its output. If it's
        "action_done", deactivate it, and otherwise return it.

        Finally, if no option was picked and the input in different from
        confirm and return, the method to move the cursor based on the given
        arrangement is called.

        Returns Any as options input_event method can also do.
        """
        curr_option: Option = self.options[self.select_index]
        named_key: str = ""
        text_input: str = ""
        if event.type == pg.TEXTINPUT:
            text_input = event.text
        elif event.type == pg.KEYDOWN:
            named_key = pg.key.name(event.key)
        else:
            return
        action_key: str = key_unicode_to_action(key_config, named_key)
        if action_key == "confirm_key":
            if self.picked_index == -1:
                self.picked_index = self.select_index
                self.last_picked = -1
                self.options[self.picked_index].activate()
                action_key = "activate"
            else:
                self.options[self.picked_index].deactivate()
                self.last_picked = self.picked_index
                self.picked_index = -1
        if action_key == "return_key" and self.picked_index != -1:
            self.options[self.picked_index].deactivate()
            self.last_picked = self.picked_index
            self.picked_index = -1
        if self.picked_index != -1:
            output: str = curr_option.input_event(
                action_key, named_key, text_input)
            if curr_option.pickable is False:
                self.picked_index = -1
            if output == "action_done":
                self.options[self.picked_index].deactivate()
                self.last_picked = self.picked_index
                self.picked_index = -1
                return
            else:
                return output
        {
            "horizontal": self.get_event_horizontal,
            "vertical": self.get_event_vertical,
            "chart": self.get_event_chart}[arrangement](action_key)

    def get_event_vertical(self, key_input: str) -> None:
        """Processes vertical movement (up and down) in the menu based on key
        events. The key_input given as argument, if in "up_key" and "down_key",
        is used to move the selection cursor along the options, using the
        move_cursor method with a set factor.
        """
        if key_input == "up_key":
            self.move_cursor(-1)
        elif key_input == "down_key":
            self.move_cursor(1)

    def get_event_horizontal(self, key_input: str) -> None:
        """Processes horizontal movement (left and right) in the menu based on
        key events. The key_input given as argument, if in "left_key" and
        "right_key", is used to move the selection cursor along the options,
        using the move_cursor method with a set factor.
        """
        if key_input == "left_key":
            self.move_cursor(-1)
        elif key_input == "right_key":
            self.move_cursor(1)

    def get_event_chart(self, key_input: str) -> None:
        """Processes movements in all directions in the menu based on key
        events. The key_input given as argument, is used to move the selection
        cursor along the options, using the move_cursor method with a set
        factor. Calls get_event_horizontal to handle left right movements.
        """
        if key_input == "up_key":
            self.move_cursor(-2)
        elif key_input == "down_key":
            if (len(self.options) % 2 != 0
                    and self.select_index == len(self.options) - 2):
                self.move_cursor(1)
            else:
                self.move_cursor(2)
        else:
            self.get_event_horizontal(key_input)

    def move_cursor(self, operant: int) -> None:
        """Updates the selected index with the change_selected_option method
        until the currently held option can be selected, by its selectable
        attribute.
        """
        self.change_selected_option(operant)
        while self.options[self.select_index].selectable is False:
            self.change_selected_option(operant)

    def change_selected_option(self, operant: int) -> None:
        """Modifies the select_index with the operant given as argument, and
        compares it with the range of the number of options in the list.
        If any limit of this range is reached, if the loop_cursor flag is
        True, the select_index cycles back to minimum or maximum depending on
        the case, otherwise sitting at the first reached limit.
        """
        self.select_index += operant
        max_indicator = len(self.options)
        if self.select_index < 0:
            if self.loop_cursor is True:
                self.select_index = max_indicator + self.select_index
            else:
                self.select_index = next((
                    index for index in range(max_indicator)
                    if self.options[index].selectable), 0)
        elif self.select_index > max_indicator - 1:
            if self.loop_cursor is True:
                self.select_index = self.select_index % max_indicator
            else:
                self.select_index = next((
                    index for index in range(max_indicator - 1, 0, -1)
                    if self.options[index].selectable), 0)
