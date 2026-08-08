
from .display import Display
from pacman.controllers import Menu


class MainMenuDisplay(Display):
    """Class MainMenuDisplay, subclass of Display

    Display class for the MainMenuState
    """
    def startup(self, menu: Menu) -> None:
        self.scale_holders((0.3, 0.08), (0.05, 0.05, 0.95, 0.95))
        self.init_menu(menu)

    def cleanup(self) -> None:
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
