
import pygame as pg

from .display import Display
from pacman.controllers import Control, Menu
from pacman.views import PlaceHolder, Style, MenuRender, new_surface


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
    - create_errors_holder => returns a PlaceHolder object used to display
    error messages
    - draw => fills the screen with a background and draws the main menu
    """
    def __init__(self, control: Control) -> None:
        """Initialized the class using a Control object, declares the
        menu_render attribute and calls load_menu_assets.
        """
        super().__init__(control)
        self.menu_render: MenuRender
        self.error_list: MenuRender
        self.parallax_1: float = 0
        self.parallax_2: float = 0
        self.load_menu_assets()
        self.load_background_assets()

    def startup(self, menu: Menu, error_list: Menu) -> None:
        """Called when the MainMenuState comes up and initialize all needed
        visual variables.
        """
        screen_h: int = self.control.interface.get_height()
        self.scale_background_assets()
        self.menu_render = self.init_menu(self.scale_menu_holders(), menu,
                                          int(screen_h * 0.55))
        self.error_list = self.init_menu(
            self.create_errors_holder(), error_list,
            int(screen_h * 0.03), int(screen_h * 0.26),
            int(screen_h * 0.03))

    def cleanup(self) -> None:
        """Called when the MainMenuState is left, deletes the menu_render
        attribute.
        """
        del self.menu_render

    def create_errors_holder(self) -> PlaceHolder:
        """Returns aPlaceHolder object used to display error messages in the
        main menu.
        """
        screen_h: int = self.control.interface.get_height()
        graphic: pg.Surface = new_surface(
            (int(screen_h * 0.5), int(screen_h * 0.013)))
        g_rect: pg.Rect = graphic.get_rect()
        pg.draw.rect(graphic, pg.Color(15, 15, 15, 40), g_rect,
                     int(screen_h * 0.05))
        return PlaceHolder([
            Style(pg.Color(0, 0, 0),
                  pg.font.Font(self.font_path, int(screen_h * 0.012)),
                  graphic, pg.Rect(g_rect.width * 0.05, g_rect.height * 0.05,
                                   g_rect.width * 0.95, g_rect.height * 0.95),
                  int(screen_h * 0.009)),
            Style(), Style()])

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        screen_w: int = self.control.interface.get_width()
        self.parallax_1 += screen_w * 0.0005
        self.parallax_2 += screen_w * 0.0007
        if self.parallax_1 > screen_w:
            self.parallax_1 = 0
        if self.parallax_2 > screen_w:
            self.parallax_2 = 0

        self.control.screen.fill((0, 0, 0))
        self.control.interface.fill((255, 120, 0))
        self.control.interface.blits([
            (self.bground_assets["backg"], (0, 0)),
            (self.bground_assets["cloud_1"], (screen_w - self.parallax_1, 0)),
            (self.bground_assets["cloud_1"], (-self.parallax_1, 0)),
            (self.bground_assets["cloud_2"], (screen_w - self.parallax_2, 0)),
            (self.bground_assets["cloud_2"], (-self.parallax_2, 0)),
            (self.bground_assets["foreg"], (0, 0))])
        self.menu_render.draw_vertical_options()
        self.error_list.draw_vertical_options()
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
