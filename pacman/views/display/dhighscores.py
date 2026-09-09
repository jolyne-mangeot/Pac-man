
from .display import Display
from pacman.controllers import Control, Menu
from pacman.views import MenuRender, PlaceHolder


class HighscoresMenuDisplay(Display):
    """Class MainMenuDisplay, subclass of Display

    Display class for the MainMenuState, initializing the menu rendering object
    and visual scalings. Implement the draw method to display all needed
    elements.

    ### Attributes:
    - *Display instance attributes*

    ### Methods:
    - *Display instance methods*
    - startup => initialize a PlaceHolder and a MenuRender objects
    - cleanup => deletes the MenuRender object to save memory
    - draw => fills the screen with a background and draws the main menu
    """
    def __init__(self, control: Control) -> None:
        super().__init__(control)
        self.highscore_title: MenuRender
        self.highscore_index: MenuRender
        self.highscore_list: MenuRender
        self.reset_menu: MenuRender

        self.load_menu_buttons()
        self.scale_menu_holders()

    def startup(self, highscore_title: Menu, highscore_index: Menu,
                highscore_list: Menu, reset_menu: Menu) -> None:
        """Called when the MainMenuState comes up and initialize all needed
        visual variables.
        """
        holder: PlaceHolder = self.scale_menu_holders(
            (0.8, 0.075), (0.12, 0.12, 0.76, 0.76))
        height: int = self.control.interface.get_height()
        self.highscore_title = self.init_menu(
            holder, highscore_title, height // 12)
        self.highscore_index = self.init_menu(
            self.scale_menu_holders(), highscore_index, height // 5)
        self.highscore_list = self.init_menu(
            holder, highscore_list, height // 3, spacer=height // 12)
        self.reset_menu = self.init_menu(
            self.scale_menu_holders(), reset_menu, int(height * 0.85))

    def cleanup(self) -> None:
        """Called when the MainMenuState is left, deletes the menu_render
        attribute.
        """
        del self.highscore_title
        del self.highscore_index
        del self.highscore_list
        del self.reset_menu

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((0, 0, 0))
        self.control.interface.fill((255, 120, 0))
        self.highscore_index.pre_render_option(self.control.dialogs)
        self.highscore_index.draw_vertical_options()
        self.highscore_title.draw_vertical_options()
        self.highscore_list.draw_list_options(0, 4)
        self.reset_menu.draw_horizontal_options()
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
