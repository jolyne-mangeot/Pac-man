
from .display import Display
from pacman.controllers import Menu


class OptionsMenuDisplay(Display):
    def startup(self, menu: Menu) -> None:
        self.scale_holders((0.55, 0.08), (0.12, 0.07, 0.8, 0.86))
        self.init_menu(menu, int(self.control.screen.get_height() / 10))

    def cleanup(self) -> None:
        del self.menu_render

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((0, 0, 0))
        self.control.interface.fill((255, 255, 255))
        self.menu_render.draw_chart_options(int(
            self.control.interface.get_width() / 2))
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
