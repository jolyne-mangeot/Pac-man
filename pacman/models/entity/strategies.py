"""File: /pacman/models/entity/strategies.py

Date: 2026-08-17
#### Description:
This module defines the movement strategies used by ghost entities.

A strategy is responsible for calculating the next position of a ghost
according to a specific movement or pathfinding behaviour.

Strategies are separated from the `Ghost` class so that different ghost
behaviours can be implemented, combined and replaced without modifying
the entity itself.

This module can contain strategies for behaviours such as:
- chasing Pacman;
- escaping from Pacman;
- moving randomly;
- patrolling a specific area;
- following a predefined path;
- implementing special level-specific behaviours.

#### Classes:
- Strategy(ABC)
- AlternateAngleStrat(Strategy)
"""
from abc import ABC, abstractmethod
from typing import Literal
from random import choice

from pacman.models import Cell
from .entity import Directions


class Strategy(ABC):
    """Class Strategy, heriting from ABC.
    
    #### Description:
    Base class for ghost movement strategies.

    A strategy defines how a ghost determines its next position according
    to its current position and a target position.

    Concrete strategies must implement the `move()` method. This allows
    different pathfinding algorithms and movement behaviours to be used
    interchangeably by a ghost.

    #### Attributes:
    - maze (list[list[Cell]]): Reference to the maze used by the strategy
      to determine valid movements and paths.

    #### Methods:
    @abstractmethod
    - ove(): Calculate the next position for the ghost.

    Description:
    """
    def __init__(self, maze: list[list[Cell]]):
        """Initialises the attributes of the Strategy instance."""
        self.maze: list[list[Cell]] = maze

    @abstractmethod
    def move(self, ghost_pos: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
        """Calculate the ghost's next position. Returns the next position
        chosen by the strategy.
        """
        pass


class AlternateAngleStrat(Strategy):
    """Class AlternateAngleStrat, inheriting from Strategy.
    
    #### Description:
    Move the ghost between randomly selected points of the maze.

    This strategy selects a destination from a predefined set of important
    positions, such as map corners and the central area.

    Once a target has been selected, the strategy calculates a path from
    the ghost's current position towards that target.

    The target is changed when the ghost reaches it, after entering in chase
    mode or after dying, allowing the ghost to continuously patrol different
    areas of the maze.

    #### Atributes:
    - target (tuple[int, int]): Current destination selected by the strategy.
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    Methods:
    - choose_target(): Select a new destination for the ghost.
    - move(): Calculate the next position towards the current target.
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
    """Calculate the Manhattan distance between two positions and returns
    it.

    The Manhattan distance is the sum of the absolute differences between
    the two coordinates. It can be used by ghost strategies to estimate
    how close a ghost is to its target.
    """
    return abs(ghost[0] - target[0]) + abs(ghost[1] - target[1])


strat_dict: dict[str, Strategy] = {"AlternateAngleStrat": AlternateAngleStrat}
strategies = Literal["AlternateAngleStrat"]