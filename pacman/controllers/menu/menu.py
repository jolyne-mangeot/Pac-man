
from typing import Any

from pacman.models import Option


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
    - action_done: str => string containing various key words used to check
    which action has been done during the get_event method (ex. "cursor_move")

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
        self.action_done: str = ""

    # _________________________________________________________________________
    #                           Events-related Methods
    # _________________________________________________________________________
    def unpick_option(self) -> None:
        """Called to deactivate a picked option. Calls its deactivate method,
        update the last_picked index with the picked_index that's later reset
        to -1, and action_done is set to "cursor_unpick".
        """
        self.options[self.picked_index].deactivate()
        self.last_picked = self.picked_index
        self.picked_index = -1
        self.action_done = "cursor_unpick"

    def get_event(self, named_key: str, action_key: str, text_input: str,
                  arrangement: str) -> Any:
        """Takes a key_config, a pygame event and an arrangement as arguments.

        Using the currently selected option, which can also be the picked
        option, handles the way the user can interact with it.

        The input is first converted to a string, either as a text_input if
        the option needs it, or a named key, then translated into an action
        key based on the key_config. When done, if the confirm_key or
        return_key was pressed, either activate or deactivate the option by
        calling its dedicated methods, and the unpick_method if needed.

        Otherwise, pass down the event strings to the picked option by
        calling its input_event method, and recovering its output. If it's
        "action_done", deactivate it, and otherwise return this output. If
        action_done remained as an empty string, updates it with the output.

        Finally, if no option was picked and the input in different from
        confirm and return, the method to move the cursor based on the given
        arrangement is called.

        Returns Any as options input_event method can also do.
        """
        curr_option: Option = self.options[self.select_index]
        self.action_done = ""
        if action_key == "confirm_key":
            if self.picked_index == -1:
                self.picked_index = self.select_index
                self.last_picked = -1
                self.options[self.picked_index].activate()
                self.action_done = "cursor_pick"
                action_key = "activate"
            else:
                self.unpick_option()
        if action_key == "return_key" and self.picked_index != -1:
            self.unpick_option()
        if self.picked_index != -1:
            output: str = curr_option.input_event(
                action_key, named_key, text_input)
            if curr_option.pickable is False:
                self.action_done = ""
                self.picked_index = -1
            if output == "action_done":
                self.unpick_option()
                return
            else:
                if self.action_done == "":
                    self.action_done = output
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
        attribute. Checks if the select_index attribute has effectively
        changed, and if so, set action_done to "cursor_move"
        """
        index: int = self.select_index
        self.change_selected_option(operant)
        while self.options[self.select_index].selectable is False:
            self.change_selected_option(operant)
        if self.select_index != index:
            self.action_done = "cursor_move"

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
