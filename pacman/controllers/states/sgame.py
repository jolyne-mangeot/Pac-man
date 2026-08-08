
import pygame as pg

from pacman.controllers import Control, State


class GameMenuState(State):
    def __init__(self, control: Control) -> None:
        State.__init__(self, control)
        self.next = "main_menu"

    def cleanup(self) -> None:
        pass

    def startup(self) -> None:
        pass

    def get_event(self, event: pg.event.Event) -> None:
        if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN:
            self.done = True

    def update(self) -> None:
        self.draw()

    def draw(self) -> None:
        self.control.screen.fill((0, 0, 255))
