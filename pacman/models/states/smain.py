
import pygame as pg
from .state import State

from pacman.controllers import Control


class MainMenu(State):
    def __init__(self, control: Control) -> None:
        """
            inits values specific to the menu such as navigation and
            placement of options
        """
        State.__init__(self, control)
        self.next = "game_menu"
        self.options = ["Play", "Options", "Quit"]
        self.next_list = ["game_menu", "options_menu"]
        self.pre_render_options()
        self.from_top = 200
        self.spacer = 75

    def cleanup(self) -> None:
        """
            cleans up all menu related data
        """
        pass

    def startup(self) -> None:
        """
            initiates all menu-related data
        """
        pass

    def get_event(self, event) -> None:
        """
            get all pygame-related events proper to the menu before
            checking main menu shared events
        """
        if event.type == pg.KEYDOWN:
            if event.key in [pg.K_ESCAPE, pg.K_LSHIFT]:
                self.control.done = True
        self.get_event_menu(event)

    def update(self) -> None:
        """
            trigger all changes such as mouse hover or changing selected
            option, done after having checked in control class change on
            done and quit attribute from menu_manager inheritance
        """
        self.update_menu()
        self.draw()

    def draw(self) -> None:
        """
            init all display related script
        """
        self.control.screen.fill((255, 0, 0))
        self.draw_menu_options()
