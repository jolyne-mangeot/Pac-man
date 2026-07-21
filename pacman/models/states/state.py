
from abc import ABC, abstractmethod
import pygame as pg

from pacman.controllers import Control


class State(ABC):
    def __init__(self, control: Control) -> None:
        self.control: Control = control
        self.done: bool = False
        self.next: str
        self.previous: str

    @abstractmethod
    def startup(self) -> None:
        """Initiates all menu related data"""

    @abstractmethod
    def cleanup(self) -> None:
        pass

    @abstractmethod
    def get_event(self, event: pg.event.Event) -> None:
        """Get all events and checks for custom conditions for the active
        menu only
        """

    @abstractmethod
    def update(self) -> None:
        """Update the menu with all new informations such as hovering or
        selecting an option as well as playing a sound when happening,
        then launch draw method
        """

    @abstractmethod
    def draw(self) -> None:
        """Launch all display related scripts proper to this menu before
        the main_menu states shared scripts
        """
