"""File: /pacman/models/entity/strategies.py

Date: 2026-08-17
#### Description: This module manages

#### Classes:
- Strategy(ABC)
"""
from abc import ABC, abstractmethod
from typing import Literal
from random import choice

from pacman.models import Cell
from .entity import Directions


class Strategy(ABC):
    """Class Strategy, heriting from ABC.
    
    Atributes:
    - maze: list[list[Cell]]

    Methods:
    @abstractmethod
    - move(self, ghost_pos: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]

    Description:
    """
    def __init__(self, maze: list[list[Cell]]):
        """Initialises the attributes of the Strategy instance."""
        self.maze: list[list[Cell]] = maze

    @abstractmethod
    def move(self, ghost_pos: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
        pass


class AlternateAngleStrat(Strategy):
    """Class AlternateAngleStrat, inheriting from Strategy.
    
    Atributes:
    - target: tuple[int, int]
    - path: list[Directions]
    - ghost_saved_pos: tuple[int, int]

    Methods:
    - choose_target(self, ghost_pos: tuple[int, int]) -> tuple[int, int]
    - move(self, ghost_pos: tuple[int, int], _: tuple[int, int]) -> tuple[int, int]

    Description:
    """
    def __init__(self):
        """Initialises the attributes of the AlternateAngleStrat instance."""
        self.target: tuple[int, int] = ()
        self.path: list[Directions] = []
        self.ghost_saved_pos: tuple[int, int] = ()

    def choose_target(self, ghost_pos: tuple[int, int]) -> tuple[int, int]:
        """"""
        width: int = len(self.maze)
        height: int = len(self.maze[0])
        targets: list[tuple[int, int]] = [(0, 0),
                                          (0, height - 1),
                                          (width - 1 , 0),
                                          (width - 1, height - 1),
                                          ((width - 1) // 2, (height - 1) // 2)]
        if ghost_pos in targets:
            targets.remove(ghost_pos)
        return choice(targets)


    def move(self, ghost_pos: tuple[int, int], _: tuple[int, int]) -> tuple[int, int]:
        """"""
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            target: tuple[int, int] = self.choose_target(ghost_pos)


def calculate_manhattan(ghost: tuple[int, int], target: tuple[int, int]) -> int:
    """Returns an int corresponding to the Manhattan distance as an
    absolute, to be used in priorizing the closest node from the
    destination.
    """
    return abs(ghost[0] - target[0]) + abs(ghost[1] - target[1])


strat_dict: dict[str, Strategy] = {"AlternateAngleStrat": AlternateAngleStrat}
strategies = Literal["AlternateAngleStrat"]