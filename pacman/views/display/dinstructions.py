
import pygame as pg

from .display import Display
from pacman.views import MenuRender
from pacman.models import Languages
from pacman.controllers import Control, Menu


class InstructionsMenuDisplay(Display):
    """Class InstructionsMenuDisplay, subclass of Display

    #### Description:
    Display class for the OptionsMenuState, initializing the menu rendering
    object and visual scalings. Implement the draw method to display all needed
    elements.

    ### Attributes:
    - *Display instance attributes*
    - instructions_menu: MenuRender => object used to display the main menu

    ### Methods:
    - *Display instance methods*
    - startup => initialize the instructions_menu using the menu passed as
    argument
    - cleanup => deletes the MenuRender object to save memory
    - draw => fills the screen with a background and draws the main menu
    """
    def __init__(self, control: Control) -> None:
        """Initializes the class using Control, declared the options_menu
        attribute and calls load_menu_assets.
        """
        super().__init__(control)
        self.instructions_menu: MenuRender
        self.instructions: dict[str, pg.Surface]
        self.scaled_instructions: tuple[pg.Surface, pg.Rect]
        self.load_menu_assets()
        self.load_background_assets()
        self.load_instructions()

    def startup(self, instructions_menu: Menu) -> None:
        """Called when the OptionsMenuState comes up and initialize all needed
        visual variables.
        """
        self.scale_background_assets()
        self.scaled_instructions = (pg.transform.scale(
            self.instructions[self.control.settings.lang.value],
            self.control.interface.get_size()),
            pg.Rect(0, 0, 0, 0))
        screen_h: int = self.control.screen.get_height()
        self.instructions_menu = self.init_menu(
            self.scale_menu_holders(), instructions_menu, screen_h // 11,
            spacer=int(screen_h * 0.83))

    def cleanup(self) -> None:
        """Called when the OptionsMenuState is left, deletes the options_menu
        attribute.
        """
        del self.instructions_menu

    def load_instructions(self) -> None:
        self.instructions = {
            lang.value: pg.image.load(
                "pacman/assets/menues/instructions-" + lang.value + ".png"
            ).convert_alpha() for lang in Languages}

    def draw(self) -> None:
        """Called by update to display all visual elements of the menu, namely
        the background and the main_menu object using its dedicated method.
        """
        self.control.screen.fill((0, 0, 0))
        self.control.interface.blits([
            (self.bground_assets["backg"], (0, 0)),
            (self.bground_assets["foreg"], (0, 0)),
            self.scaled_instructions])
        self.instructions_menu.draw_vertical_options()
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
