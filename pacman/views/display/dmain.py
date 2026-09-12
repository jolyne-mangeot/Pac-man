
from .display import Display
from pacman.controllers import Control, Menu
from pacman.views import MenuRender


class MainMenuDisplay(Display):
    """Class MainMenuDisplay, subclass of Display

    #### Description:
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
        """Initialized the class using a Control object, declares the
        menu_render attribute and calls load_menu_assets.
        """
        super().__init__(control)
        self.menu_render: MenuRender
        self.load_menu_assets()

    def startup(self, menu: Menu) -> None:
        """Called when the MainMenuState comes up and initialize all needed
        visual variables.
        """
        self.menu_render = self.init_menu(self.scale_menu_holders(), menu)

    def cleanup(self) -> None:
        """Called when the MainMenuState is left, deletes the menu_render
        attribute.
        """
        del self.menu_render

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((0, 0, 0))
        self.control.interface.fill((255, 120, 0))
        self.menu_render.draw_vertical_options()
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
