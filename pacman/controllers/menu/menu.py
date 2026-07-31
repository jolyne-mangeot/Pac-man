
import pygame as pg
from typing import cast, Any

from pacman.models import KeyConfig
from .utils import Option


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
    of the options: deselected, selected and picked. Images can also be
    displayed next to the options if given any.

    ### Attributes:
    <u>Parameters:</u>
    - screen: pg.Surface => the screen onto which display the
    options
    - from_left: int => x coordinates of the screen to place the
    display of options, corresponds to the center of the options
    - from_top: int => y coordinates of the screen to place the
    options, corresponds to the center of the upmost option.
    - spacer: int => multiplied factor separating the options
    - options: list[Option] => list containing all Option instances
    to manage the Menu
    - deselected_color: pg.Color => color for unselected options
    - selected_color: pg.Color => color for selected options
    - picked_color: pg.Color => color for picked options
    - deselect_ft: pg.font.Font => font for unselected options
    - selected_ft: pg.font.Font => font for selected options
    - picked_ft: pg.font.Font => font for picked options
    - images: list[pg.Surface] => list of pre-scaled images to
    display next to each options.

    <u>Self attributed:</u>
    - select_index: int => index of the selected option, like a cursor
    - picked_index: int => index of the picked option, which will receive
    further inputs
    - last_picked: int => index of the last picked option to update its render
    after it's been interacted with
    - rendered: dict[str, list[tuple[pg.Surface, pg.Rect]]] => options rendered
    as pygame Surfaces, saving their font, size, style and color for later
    display.

    ### Methods:
    <u>Option rendering:</u>
    - pre_render_all_options => Reset self.render and append each of its lists
    with pygame Surfaces and Rects of each option.
    - pre_render_option => Override a single option's renders in each render
    lists to update its visual.
    - pre_render => Render the visuals for the Option's str cast using the
    associated fonts and colors to return a tuple of visuals for the
    deselected, selected and picked styles.

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
    def __init__(
            self, screen: pg.Surface, from_left: int = -1, from_top: int = -1,
            spacer: int = 50, options: list[Option] = [],
            loop_cursor: bool = True,
            deselected_color: pg.Color = pg.Color(0, 0, 0),
            selected_color: pg.Color = pg.Color(0, 0, 0),
            picked_color: pg.Color = pg.Color(255, 0, 0),
            deselect_ft: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            selected_ft: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            picked_ft: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            images: list[pg.Surface] = []) -> None:
        """
        """
        self.screen: pg.Surface = screen
        self.from_left: int = (
            from_left if from_left != -1 else int(screen.get_width() / 2))
        self.from_top: int = (
            from_top if from_top != -1 else int(screen.get_height() / 2))
        self.spacer: int = spacer
        self.options: list[Option] = options
        self.loop_cursor: bool =loop_cursor
        self.deselected_color: pg.Color = deselected_color
        self.selected_color: pg.Color = selected_color
        self.picked_color: pg.Color = picked_color
        self.deselect_ft: pg.font.Font = deselect_ft
        self.selected_ft: pg.font.Font = selected_ft
        self.picked_ft: pg.font.Font = picked_ft
        self.images: list[pg.Surface] = images
        self.select_index: int = 0
        self.picked_index: int = -1
        self.last_picked: int = -1
        self.rendered: dict[str, list[tuple[pg.Surface, pg.Rect]]]
        self.pre_render_all_options()

    def pre_render_all_options(self) -> None:
        """To be called when all options' visuals need to be updated.

        Reset the rendered dict to empty lists, then loop through every option
        to render their visuals to later be displayed on screen.
        """
        self.rendered = {"deselected": [], "selected": [], "picked": []}
        des: tuple[pg.Surface, pg.Rect]
        sel: tuple[pg.Surface, pg.Rect]
        pik: tuple[pg.Surface, pg.Rect]
        for option in self.options:
            des, sel, pik = self.pre_render(option)
            self.rendered["deselected"].append(des)
            self.rendered["selected"].append(sel)
            self.rendered["picked"].append(pik)

    def pre_render_option(self, index: int = -1) -> None:
        """Call pre_render on the option which index is given as argument,
        updating each list in the rendered dict with the returned tuple of
        renders.
        """
        des: tuple[pg.Surface, pg.Rect]
        sel: tuple[pg.Surface, pg.Rect]
        pik: tuple[pg.Surface, pg.Rect]
        if index == -1:
            if self.picked_index != -1:
                index = self.picked_index
            else:
                index = self.last_picked
        des, sel, pik = self.pre_render(self.options[
            index if index != -1 else self.last_picked])
        self.rendered["deselected"][index] = des
        self.rendered["selected"][index] = sel
        self.rendered["picked"][index] = pik

    def pre_render(self, option: Option) -> tuple[tuple[pg.Surface, pg.Rect]]:
        """Pre-renders the option given as argument in three states: picked,
        deselected and selected, each with their associated fonts and colors,
        then returns a tuple of each state, as a tuple of pygame Surface and
        Rect.
        """
        render: str = str(option) if option is not None else ""
        deselect_render = self.deselect_ft.render(
            render, True, self.deselected_color)
        select_render = self.selected_ft.render(
            "◄ " + render + " ►", True, self.selected_color)
        picked_render = self.selected_ft.render(
            "◄ " + render + " ►", True, self.picked_color)

        return (
            (deselect_render, deselect_render.get_rect()),
            (select_render, select_render.get_rect()),
            (picked_render, picked_render.get_rect()))

    def draw_vertical_options(self) -> None:
        """For all launch_menu states, enumerate buttons and places them before
        checking for selected index button to place it on the same position.
        """
        for index, option in enumerate(self.rendered["deselected"]):
            option[1].center = (
                self.from_left, self.from_top + index * self.spacer)
            if index == self.select_index:
                select_render = self.rendered["selected"][index]
                select_render[1].center = option[1].center
                self.screen.blit(select_render[0], select_render[1])
            else:
                self.screen.blit(option[0], option[1])

    def draw_list_options(self, elements_bef: int, elements_aft: int) -> None:
        """Draws a selection of the menu's options, centering on the selected
        option as in a vertical carousel. Draws "elements_bef" number of
        options above the selected option, and "elements_aft" options under.
        """
        min_index: int = self.select_index - elements_bef
        max_index: int = self.select_index + elements_aft

        for index, option in enumerate(self.rendered["deselected"][
                min_index:self.select_index]):
            option[1].center = (
                self.from_left,
                self.from_top - (self.select_index - index) * self.spacer)
            self.screen.blit(option[0], option[1])

        select_render = self.rendered["selected"][self.select_index]
        option[1].center = select_render[1].center = (
            self.from_left, self.from_top)
        self.screen.blit(select_render[0], select_render[1])

        for index, option in enumerate(self.rendered["deselected"][
                self.select_index + 1:max_index]):
            option[1].center = (
                self.from_left,
                self.from_top + (index - self.select_index) * self.spacer)
            self.screen.blit(option[0], option[1])

        if len(self.images) > 0:
            for index in range(min_index, max_index):
                self.screen.blit(self.images[index], (
                    self.from_left * 0.49,
                    self.rendered["deselected"][index][1].centery
                    - self.screen.get_height() * 0.17))

    def draw_horizontal_options(self) -> None:
        """Draws the menu options in a horizontal arrangement.
        The selected option is highlighted based on its index.
        """
        width: int = self.screen.get_width()
        for index, option in enumerate(self.rendered["deselected"]):
            if len(self.rendered["deselected"]) == 2:
                option[1].center = (
                    int(width / 3 + index * width / 3), self.from_top)
            else:
                option[1].center = (
                    int(width * 0.25 * (index + 1)), self.from_top)
            if index == self.select_index:
                if self.picked_index > -1:
                    if self.select_index == self.picked_index:
                        continue
                select_render = self.rendered["selected"][index]
                select_render[1].midbottom = option[1].midbottom
                self.screen.blit(select_render[0], select_render[1])
            else:
                self.screen.blit(option[0], option[1])

    def draw_picked_options(self) -> None:
        """Draws the menu options with a picked option highlighted in red.
        Also highlights the currently selected option.
        """
        for index, option in enumerate(self.rendered["deselected"]):
            option[1].center = (
                self.from_left, self.from_top + index * self.spacer)
            if index == self.picked_index:
                select_render = self.rendered["picked"][index]
                select_render[1].center = option[1].center
                self.screen.blit(select_render[0], select_render[1])
            elif index == self.select_index:
                select_render = self.rendered["selected"][index]
                select_render[1].center = option[1].center
                self.screen.blit(select_render[0], select_render[1])
            else:
                self.screen.blit(option[0], option[1])

    def draw_chart_options(self) -> None:
        """Draws the menu options in a chart-like arrangement."""
        for index, option in enumerate(self.rendered["deselected"]):
            if (index == len(self.rendered["deselected"]) - 1
                    and len(self.rendered["deselected"]) % 2 != 0):
                option[1].center = (
                    int(self.from_left * 1.75),
                    int(self.from_top + self.spacer * index * 0.5))
            elif index % 2 == 0:
                option[1].center = (
                    self.from_left,
                    int(self.from_top + self.spacer * index * 0.5))
            else:
                option[1].center = (
                    int(self.from_left * 3),
                    int(self.from_top + self.spacer * (index - 1) * 0.5))
            if index == self.picked_index:
                picked_render = self.rendered["picked"][index]
                picked_render[1].center = option[1].center
                self.screen.blit(picked_render[0], picked_render[1])
            elif index == self.select_index:
                select_render = self.rendered["selected"][index]
                select_render[1].center = option[1].center
                self.screen.blit(select_render[0], select_render[1])
            else:
                self.screen.blit(option[0], option[1])

    def draw_only_active_option(self) -> None:
        for index, option in enumerate(self.rendered["selected"]):
            if index == self.select_index:
                select_render = self.rendered["selected"][index]
                select_render[1].center = option[1].center
                self.screen.blit(select_render[0], select_render[1])

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

        Returns Any as options can also do.
        """
        curr_option: Option = self.options[self.select_index]
        input: str = ""
        if event.type == pg.KEYDOWN and (curr_option.using_text_input is False
                or pg.key.name(event.key) in (
                    "backspace", "return", "escape")):
            input = pg.key.name(event.key)
        elif event.type == pg.TEXTINPUT:
            input = event.text
        else:
            return
        action_key: str = key_unicode_to_action(key_config, input)
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
        if self.picked_index != -1:
            output: str = cast(Option, curr_option).input_event(
                action_key, input)
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
        max_indicator = len(self.rendered["deselected"]) - 1
        if self.select_index < 0:
            if self.loop_cursor is True:
                self.select_index = max_indicator + self.select_index
        elif self.select_index > max_indicator:
            if self.loop_cursor is True:
                self.select_index = self.select_index % max_indicator
            else:
                self.select_index = max_indicator
