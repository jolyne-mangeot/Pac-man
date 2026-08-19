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
- Strategy(ABC): Base class for ghost movement strategies.
- AlternateAngleStrat(Strategy): Move the ghost between randomly selected
  points of the maze.
- PatrollingAngleStrat(Strategy): Move the ghost in a patrolling behavior
  inside a specific area.
"""
from abc import ABC, abstractmethod
from typing import Literal
from random import choice, randint

from pacman.models import Cell
from pacman.models import Map

from ..mazemap.map import Directions, Movements


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
    - xmax (int): number of cells in horizontal axis.
    - ymax (int): number of cells in vertical axis.

    #### Methods:
    @abstractmethod
    - ove(): Calculate the next position for the ghost.

    Description:
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the Strategy instance."""
        self.maze: Map = maze
        self.grid: list[list[Cell]] = maze.map
        self.xmax: int = len(self.grid) - 1
        self.ymax: int = len(self.grid[0]) - 1

    @abstractmethod
    def move(self, ghost_pos: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
        """Calculate the ghost's next position. Returns the next position
        chosen by the strategy.
        """
        pass

    def find_path(self, ghost: tuple[int, int],
                  target: tuple[int, int]) -> list[Directions]:
        """Finds the shortest path in the maze using a A-star algortihm.

        Sets a list of intersection_cells and calculate the distance between
        each to generate a weighted graph, including the ghost and target
        cells. Checks then each of their distance from the ghost,
        priorizing lighter distances, either until all paths are counted for
        or the target is found.

        Goes back from the target, adding to the shortest_path each direction
        to take to go back an intersection that's the closest from the ghost.

        Return a list[Direction] from ghost to target.
        """
        

class AlternateAngleStrat(Strategy):
    """Class AlternateAngleStrat, inheriting from Strategy.
    
    #### Description:
    Move the ghost between randomly selected points of the maze.

    This strategy selects a destination from a predefined set of important
    positions, such as map corners or the central area.

    Once a target has been selected, the strategy calculates a path from
    the ghost's current position towards that target.

    The target is changed when the ghost reaches it, after entering in chase
    mode or after dying, allowing the ghost to continuously patrol different
    areas of the maze.

    #### Inherited attributes:
    - maze(Map): The Map instancied.
    - grid (list[list[Cell]]): Reference to the gris of Cells used by the
        strategy to determine valid movements and paths.
    - xmax (int): number of cells in horizontal axis.
    - ymax (int): number of cells in vertical axis.

    #### Atributes:
    - target (tuple[int, int]): Current destination selected by the strategy.
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    Methods:
    - choose_target(): Select a new destination for the ghost.
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the PatrollingAngleStrat instance."""
        super().__init__(maze)
        self.target: tuple[int, int] = ()
        self.path: list[Directions] = []
        self.ghost_saved_pos: tuple[int, int] = ()

    def choose_target(self, ghost_pos: tuple[int, int]) -> tuple[int, int]:
        """"""
        targets: list[tuple[int, int]] = [(0, 0),
                                          (0, self.ymax),
                                          (self.xmax, 0),
                                          (self.xmax, self.ymax),
                                          (self.xmax // 2, self.ymax // 2)]
        if ghost_pos in targets:
            targets.remove(ghost_pos)
        return choice(targets)


    def move(self, ghost_pos: tuple[int, int], _: tuple[int, int]) -> tuple[int, int]:
        """"""
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            target: tuple[int, int] = self.choose_target(ghost_pos)


class PatrollingAngleStrat(Strategy):
    """Class PatrollingAngleStrat, inheriting from Strategy.

    #### Description:
    Move the ghost in a patrolling behavior inside a specific area.

    This strategy identifies the area in a corner that covers a quarter of the
    entire grid in which the ghost is located.

    Once the area has been identified, the strategy randomly selects a cell
    within that area and calculates the shortest path to that cell. 

    The ghost cannot leave its zone (unless it changes strategy). If it does,
    the patrol zone is reset to the one in which it currently finds itself, or
    reappears, so that a new cell can be chosen and the patrol behaviour can
    continue.

    #### Inherited attributes:
    - maze(Map): The Map instancied.
    - grid (list[list[Cell]]): Reference to the gris of Cells used by the
      strategy to determine valid movements and paths.
    - xmax (int): number of cells in horizontal axis.
    - ymax (int): number of cells in vertical axis.

    #### Attributes:
    - target (tuple[int, int]): Current destination selected by the strategy.
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Methods:
    - ghost_area(): Identify the area in which the ghost is located. 
    - chose_target(): Select a new destination for the ghost.
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the PatrollingAngleStrat instance."""
        super().__init__(maze)
        self.target: tuple[int, int] = ()
        self.path: list[Directions] = []
        self.ghost_saved_pos: tuple[int, int] = ()

    def ghost_area(self, ghost_pos:tuple[int, int]) -> list[tuple[int, int]]:
        """Identifies the area in which the ghost is located. Returns the
        coordinates of the cells at the bottom-left and top-right corners of
        this area.
        """
        middle_x: int = self.xmax // 2
        middle_y: int = self.ymax // 2

        if ghost_pos[0] >= middle_x and ghost_pos[1] >= middle_y:
            return [(middle_x, middle_y), (self.xmax, self.ymax)]

        elif ghost_pos[0] >= middle_x and ghost_pos[1] < middle_y:
            return [(middle_x, 0), (self.xmax, middle_y)]

        elif ghost_pos[0] < middle_x and ghost_pos[1] >= middle_y:
            return [(0, middle_y), (middle_x, self.ymax)]

        else:
            return [(0, 0), (middle_x, middle_y)]

    def choose_target(self, area: list[tuple[int, int]],
                      ghost_pos: tuple[int, int]) -> tuple[int, int]:
        """"""
        target: tuple[int, int] = (randint(area[0][0], area[1][0]),
                                   randint(area[0][1], area[1][1]))
        if (self.grid[target[0]][target[1]].walls == 15 or
            self.grid[target[0]][target[1]].coordinates == ghost_pos):
            return self.choose_target(area, ghost_pos)
        return target

    def move(self, ghost_pos: tuple[int, int], _: tuple[int, int]) -> tuple[int, int]:
        """"""
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            area = self.ghost_area(ghost_pos)
            target: tuple[int, int] = self.choose_target(area, ghost_pos)
            print("area", area)
            print("target", target)


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