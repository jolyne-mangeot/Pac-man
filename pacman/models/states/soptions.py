
from .state import State

from pacman.controllers import Control


class OptionsMenu(State):
    def __init__(self, control: Control) -> None:
        """
            states all navigation paths and options to create buttons for,
            as well as their placement on the screen
        """
        State.__init__(self, control)
        self.next = "main_menu"
        self.options = ["Music", "Sound", "Graphics", "Controls", "Main_menu"]
        self.next_list = [
            "options", "options", "options", "options", "main_menu"]
        self.pre_render_options()
        self.from_top = 60
        self.spacer = 60

    def cleanup(self) -> None:
        """
            cleans up all menu related data
        """
        pass

    def startup(self) -> None:
        """
            initiates all menu related data
        """
        pass

    def get_event(self, event) -> None:
        """
            get all events and checks for custom conditions for the active
            menu only
        """
        self.get_event_menu(event)

    def update(self) -> None:
        """
            update the menu with all new informations such as hovering or
            selecting an option as well as playing a sound when happening,
            then launch draw method
        """
        self.update_menu()
        self.draw()

    def draw(self) -> None:
        """
            launch all display related scripts proper to this menu before
            the main_menu states shared scripts
        """
        self.control.screen.fill((255, 0, 0))
        self.draw_menu_options()
