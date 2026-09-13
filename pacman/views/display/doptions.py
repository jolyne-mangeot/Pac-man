
from .display import Display
from pacman.views import MenuRender, PlaceHolder
from pacman.controllers import Control, Menu


class OptionsMenuDisplay(Display):
    """Class OptionsMenuDisplay, subclass of Display

    #### Description:
    Display class for the OptionsMenuState, initializing the menu rendering
    object and visual scalings. Implement the draw method to display all needed
    elements.

    ### Attributes:
    - *Display instance attributes*
    - options_menu: MenuRender => object used to display the main menu

    ### Methods:
    - *Display instance methods*
    - startup => initialize the options_menu using the menu passed as argument
    - cleanup => deletes the MenuRender object to save memory
    - draw => fills the screen with a background and draws the main menu
    """
    def __init__(self, control: Control) -> None:
        """Initializes the class using Control, declared the options_menu
        attribute and calls load_menu_assets.
        """
        super().__init__(control)
        self.options_title: MenuRender
        self.options_menu: MenuRender
        self.load_menu_assets()

    def startup(self, options_title: Menu, options_menu: Menu) -> None:
        """Called when the OptionsMenuState comes up and initialize all needed
        visual variables.
        """
        holder: PlaceHolder = self.scale_menu_holders(
            (0.55, 0.08), (0.12, 0.07, 0.8, 0.86))
        screen_h: int = self.control.screen.get_height()
        self.options_title = self.init_menu(
            holder, options_title, screen_h // 11)
        self.options_menu = self.init_menu(
            holder, options_menu, int(screen_h * 0.19),
            spacer=int(screen_h * 0.04))

    def cleanup(self) -> None:
        """Called when the OptionsMenuState is left, deletes the options_menu
        attribute.
        """
        del self.options_menu

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((0, 0, 0))
        self.control.interface.fill((255, 120, 0))
        self.options_title.draw_vertical_options()
        self.options_menu.pre_render_option(self.control.dialogs)
        self.options_menu.draw_chart_options(int(
            self.control.interface.get_width() / 2))
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
