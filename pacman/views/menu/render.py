
import pygame as pg

from pacman.controllers import Menu
from .placeholder import PlaceHolder


class MenuRender:
    """
    ### Attributes:
    - screen: pg.Surface => the screen onto which display the
    options
    - from_left: int => x coordinates of the screen to place the
    display of options, corresponds to the center of the options
    - from_top: int => y coordinates of the screen to place the
    options, corresponds to the center of the upmost option.
    - spacer: int => multiplied factor separating the options

    ### Methods:
    <u>Option rendering:</u>
    - pre_render_all_options => reset self.render and append each of its lists
    with pygame Surfaces and Rects of each option.
    - pre_render_option => override a single option's renders in each render
    lists to update its visual.
    - pre_render => render the visuals for the Option's str cast using the
    associated fonts and colors to return a tuple of visuals for the
    deselected, selected and picked styles.
    - update_rendered_list => updates the renders list with all options
    renders, placing the selected and picked renders in at their own index.

    <u>Displaying:</u>
    - draw_vertical_options => displays the options in a vertical list
    - draw_horizontal_options => displays the options in an horizontal list
    - draw_list_options => displays the options in a vertical list, the
    selected option remaining at the center and a given amount of options
    being displayed around.
    - draw_chart_options => displays the options in a grid of 2 columns
    - draw_selected_option => displays the selected option only
    """
    def __init__(
            self, screen: pg.Surface, menu: Menu, dialogs: dict[str, str],
            from_left: int = -1, from_top: int = -1, spacer: int = -1,
            holder: PlaceHolder = PlaceHolder()) -> None:
        """Initializing method for MenuRender objects. Takes a pygame Surface,
        a dialogs dictionary and visual margins, as well as a PlaceHolder
        object to display options.

        from_left, from_top and spacer are defaulted to -1 and the holder to
        PlaceHolder().
        """
        self.screen: pg.Surface = screen
        self.menu: Menu = menu
        self.holder: PlaceHolder = holder
        self.from_left: int = (
            from_left if from_left != -1 else int(self.screen.get_width() / 2))
        self.from_top: int = (
            from_top if from_top != -1 else int(self.screen.get_height() / 2))
        self.spacer: int = (spacer if spacer != -1
                            else int((self.screen.get_height() - self.from_top)
                                     / (len(self.menu.options) + 1)))
        self.rendered: dict[str, list[tuple[pg.Surface, pg.Rect]]]
        self.renders: list[tuple[pg.Surface, pg.Rect]]
        self.pre_render_all_options(dialogs)

    # _________________________________________________________________________
    #                         Rendering-related Methods
    # _________________________________________________________________________
    def pre_render_all_options(self, dialogs: dict[str, str]) -> None:
        """To be called when all options' visuals need to be updated.

        Reset the rendered dict to empty lists, then loop through every option
        to render their visuals to later be displayed on screen.
        """
        self.rendered = {"deselect": [], "select": [], "picked": []}
        des: tuple[pg.Surface, pg.Rect]
        sel: tuple[pg.Surface, pg.Rect]
        pik: tuple[pg.Surface, pg.Rect]
        for option in self.menu.options:
            des, sel, pik = self.holder.pre_render(
                option.get_texts(dialogs), option.visible)
            self.rendered["deselect"].append(des)
            self.rendered["select"].append(sel)
            self.rendered["picked"].append(pik)

    def pre_render_option(self, dialogs: dict[str, str],
                          index: int = -1) -> None:
        """Call pre_render on the option which index is given as argument,
        updating each list in the rendered dict with the returned tuple of
        renders.
        """
        if index == -1:
            if self.menu.picked_index != -1:
                index = self.menu.picked_index
            else:
                index = self.menu.last_picked
        des: tuple[pg.Surface, pg.Rect]
        sel: tuple[pg.Surface, pg.Rect]
        pik: tuple[pg.Surface, pg.Rect]
        des, sel, pik = self.holder.pre_render(
            self.menu.options[index].get_texts(dialogs),
            self.menu.options[index].visible)
        self.rendered["deselect"][index] = des
        self.rendered["select"][index] = sel
        self.rendered["picked"][index] = pik

    def update_rendered_list(self) -> None:
        """Updates the renders attribute by resetting it to the list of
        deselected renders of all options and replacing the corresponding
        element with its picked or selected style if applicable.
        """
        self.renders = [
            render for render in self.rendered["deselect"]]
        if self.menu.picked_index != -1:
            self.renders[self.menu.picked_index] = self.rendered["picked"][
                self.menu.picked_index]
        elif self.menu.select_index != -1:
            self.renders[self.menu.select_index] = self.rendered["select"][
                self.menu.select_index]

    # _________________________________________________________________________
    #                          Display-related Methods
    # _________________________________________________________________________
    def draw_vertical_options(self) -> None:
        """Places based on the from_left and from_top attributes and displays
        based on the renders list every options in a vertical manner.

        The starting point (from_left, from_top as coordinates) is placed at
        the center of the first displayed option.
        """
        self.update_rendered_list()
        for index, option in enumerate(self.renders):
            option[1].center = (
                self.from_left, self.from_top + index * self.spacer)
            self.screen.blit(option[0], option[1])

    def draw_horizontal_options(self) -> None:
        """Places based on the from_left and from_top attributes and displays
        based on the renders list every options in a horizontal manner.

        The starting point (from_left, from_top as coordinates) is placed at
        the center of the options, but the arrangement can vary based on the
        amount of options to display.
        """
        self.update_rendered_list()
        width: int = self.screen.get_width()
        for index, option in enumerate(self.renders):
            if len(self.renders) == 2:
                option[1].center = (
                    int(width / 3 + index * width / 3), self.from_top)
            else:
                option[1].center = (
                    int(width * 0.25 * (index + 1)), self.from_top)
            self.screen.blit(option[0], option[1])

    def draw_list_options(self, elements_bef: int, elements_aft: int) -> None:
        """Draws a selection of the menu's options, centering on the selected
        option as in a vertical carousel. Draws "elements_bef" number of
        options above the selected option, and "elements_aft" options under.

        The starting point (from_left, from_top as coordinates) is placed at
        the center of the selected option.
        """
        self.update_rendered_list()
        select_index: int = self.menu.select_index
        min_index: int = select_index - elements_bef
        if min_index < 0:
            min_index = 0
        max_index: int = select_index + elements_aft
        if max_index > len(self.menu.options) - 1:
            max_index = len(self.menu.options) - 1

        for index, option in enumerate(
                self.renders[min_index:select_index]):
            option[1].center = (
                self.from_left, self.from_top - (select_index - index)
                * self.spacer)
            self.screen.blit(option[0], option[1])

        select_render = self.renders[select_index]
        select_render[1].center = (
            self.from_left, self.from_top + select_index)
        self.screen.blit(select_render[0], select_render[1])

        for index, option in enumerate(self.renders[
                select_index + 1:max_index + 1], 1):
            option[1].center = (
                self.from_left, self.from_top + index * self.spacer)
            self.screen.blit(option[0], option[1])

    def draw_chart_options(self, h_spacer: int) -> None:
        """Places based on the from_left and from_top attributes and displays
        based on the renders list every options in a chart-like manner. The
        chart will always be 2 columns wide, and the last element will be
        centered if it's alone on its line (when the length of the list option
        is odd).

        The starting point (from_left, from_top as coordinates) is placed
        between the center of the first two options.
        """
        self.update_rendered_list()
        for index, option in enumerate(self.renders):
            if (index == len(self.renders) - 1 and len(self.renders) % 2 != 0):
                option[1].center = (
                    self.from_left,
                    int(self.from_top + index * self.spacer))
            elif index % 2 == 0:
                option[1].center = (
                    self.from_left - int(h_spacer / 2),
                    int(self.from_top + index * self.spacer))
            else:
                option[1].center = (
                    self.from_left + int(h_spacer / 2),
                    int(self.from_top + (index - 1) * self.spacer))
            self.screen.blit(option[0], option[1])

    def draw_selected_option(self) -> None:
        """Draws on the screen only the selected option. The coordinates
        (form_left, from_top) correspond to the center of the text."""
        select_render = self.rendered["select"][self.menu.select_index]
        select_render[1].center = (self.from_left, self.from_top)
        self.screen.blit(select_render[0], select_render[1])
