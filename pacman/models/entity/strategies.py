"""File: /pacman/models/entity/strategies.py

Date: 2026-08-17
#### Description:
This module defines the movement strategies used by ghost entities.

A strategy is responsible for calculating the next position of a ghost
according to a specific movement or pathfinding behaviour.

Strategies are separated from the `Ghost` class so that different ghost
behaviours can be implemented, combined and replaced without modifying the
entity itself.

The module also provides the A* pathfinding utilities shared by every
strategy. Rather than running A* on every single cell of the maze, the
algorithm operates on a graph of intersections (nodes with more than
two accessible neighbours): each strategy first connects the ghost's
and the target's positions to their nearest intersections, then A*
searches the shortest path between those intersections, and the
individual cell-by-cell directions are finally reconstructed into a
full path. The temporary state needed during the search (open/closed
sets, scores, predecessors) is kept in an `AStarState` instance so
that the `Strategy` methods themselves stay stateless between calls.

#### Classes:
- AStarState: Stores the temporary state used by the A* algorithm.
- Strategy(ABC): Base class for ghost movement strategies.
- AlternateAngleStrat(Strategy): Move the ghost between randomly selected
  points of the maze.
- PatrollingAngleStrat(Strategy): Move the ghost in a patrolling behavior
  inside a specific area.
"""
from abc import ABC, abstractmethod
from typing import Type
from random import choice, randint
from heapq import heappush, heappop
from collections import deque

from pacman.models import (Map, Cell, Node, Directions, Movements,
                           OPPOSITE_DIRECTION)


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
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Methods:
    @abstractmethod
    - move(): Calculate the next position for the ghost.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the Strategy instance."""
        self.maze: Map = maze
        self.grid: list[list[Cell]] = maze.map
        self.xmax: int = len(self.grid) - 1
        self.ymax: int = len(self.grid[0]) - 1
        self.path: list[Directions] = []
        self.ghost_saved_pos: tuple[int, int] = (-1, -1)

    @abstractmethod
    def move(self, ghost_pos: tuple[int, int], pacman_pos: tuple[int, int]
             ) -> tuple[tuple[int, int], Directions]:
        pass

    def find_path(
            self, ghost: tuple[int, int], target: tuple[int, int],
            priority_calc) -> list[Directions]:
        """Find the shortest path from ghost to target using a A* Algorithm.
        """
        if ghost == target:
            return []

        def found_target_neighbor(coords: tuple[int, int]) -> Node | None:
            """Returns the node at the given coords if it's in target
            neighbor-nodes. Return None if it's not.
            """
            for node in self.maze.get_cell(target).neighbor_nodes:
                if coords == node.coords:
                    return node
            return None

        def reverse_path(path: list[Directions]) -> list[Directions]:
            """Reverse the given path and change directions in path into
            opposite directions.
            """
            reverse: list[Directions] = []
            for dir in path:
                reverse.append(OPPOSITE_DIRECTION[dir])
            return reverse

        class Origin:
            """Class Origin.

            #### Description:
            Store additional informations about node in a external
            dictionnary.

            #### Attributes:
            - distance_from_start (int): Distance from start to node.
            - path (list[Directions]): Path from start to node.
            - previous_node (tuple[int, int]): coords of previous node.
            """
            def __init__(self, distance_from_start: int = -1,
                         path: list[Directions] = [],
                         previous_node: tuple[int, int] = (-1, -1)) -> None:
                self.distance_from_start: int = distance_from_start
                self.path: list[Directions] = path
                self.previous_node: tuple[int, int] = previous_node

        known_nodes: list[tuple[int, tuple[int, int]]] = [(0, ghost)]
        distances_from_start: dict[tuple[int, int], Origin] = {
            ghost: Origin(0, [], ghost)}

        while target not in distances_from_start.keys():
            current_node: tuple[int, int] = heappop(known_nodes)[1]

            target_neighbor = found_target_neighbor(current_node)
            if target_neighbor is not None:
                distances_from_start.update({
                    target: Origin(-1, reverse_path(
                        list(target_neighbor.path[::-1])), current_node)})
                break

            for next_node in self.maze.get_cell(current_node).neighbor_nodes:
                start_to_next: int = distances_from_start.get(
                    next_node.coords, Origin()).distance_from_start

                sum_of_distances: int = (
                    distances_from_start.get(
                        current_node, Origin()).distance_from_start
                    + next_node.distance)

                if start_to_next == -1 or start_to_next > sum_of_distances:
                    distances_from_start.update({next_node.coords: Origin(
                        sum_of_distances, list(next_node.path),
                        current_node)})


                    heappush(known_nodes, (
                        priority_calc(next_node.coords, target),
                        next_node.coords))

        path_queue: deque[Directions] = deque([])
        previous = target
        while ghost != previous:
            origin: Origin = distances_from_start.get(previous, Origin())
            path_queue.extendleft(origin.path[::-1])
            previous = origin.previous_node

        return list(path_queue)


class ChaseStumbling(Strategy):
    """Class ChaseStalking, inheriting from Strategy.

    #### Description:
    Move the ghost to the node closest to Pacman. If Pac-Man enters the ghost’s
    chase_radius/3, the ghost will then target Pac-Man directly.

    This strategy selects the node closest to Pacman as target and calculates
    the path from the ghost's current position towards that target.

    The target and path are updated with the newest node closest to Pacman
    position when the ghost reach target, if Pacman is still in chasing range
    but not to close to ghost. The target and path are updated with the Pacman
    position if enter chase_radius/3 range. If the ghost quit chasing mode or
    die, the target and path are updated.

    #### Inherited attributes:
    - maze(Map): The Map instancied.
    - grid (list[list[Cell]]): Reference to the gris of Cells used by the
        strategy to determine valid movements and paths.
    - xmax (int): number of cells in horizontal axis.
    - ymax (int): number of cells in vertical axis.
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Methods:
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the AlternateAngleStrat instance."""
        super().__init__(maze)

    def move(self, ghost_pos: tuple[int, int],
             pacman_pos: tuple[int, int]) -> tuple[
                 tuple[int, int], Directions]:
        """Calculate the next position towards pacman position.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, a new path towards pacman is
        computed.
        """
        if self.path != [] and randint(0, 100) > 85:
            ghost_walls: int = self.maze.get_cell(ghost_pos).walls
            passages: list[Directions] = []
            for direction in Directions:
                if ghost_walls & direction.value or direction == self.path[0]:
                    continue
                passages.append(direction)
            if passages != []:
                random_dir: Directions = choice(passages)
                random_pos = (
                    ghost_pos[0] + Movements[random_dir.name].value[0],
                    ghost_pos[1] + Movements[random_dir.name].value[1])
                return (random_pos, random_dir)
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            self.path = self.find_path(ghost_pos, pacman_pos,
                                       calculate_manhattan)
        self.ghost_saved_pos = (
            ghost_pos[0] + Movements[self.path[0].name].value[0],
            ghost_pos[1] + Movements[self.path[0].name].value[1])
        return (self.ghost_saved_pos, self.path.pop(0))


class ChaseDynamic(Strategy):
    """Class ChaseDynamic, inheriting from Strategy.

    #### Description:
    Move the ghost on the Pacman position.

    This strategy selects the Pacman position as target and calculates the
    path from the ghost's current position towards it. The path is
    updated each time the ghost enter a Node, making this strategy more
    aggressive than the ChaseOnSpot one.

    The target and path are updated with the new pacman position when the ghost
    reach a Node, if Pacman is still in chasing range. If the ghost quit
    chasing mode or die, the target and path are updated.

    #### Inherited attributes:
    - maze(Map): The Map instancied.
    - grid (list[list[Cell]]): Reference to the gris of Cells used by the
        strategy to determine valid movements and paths.
    - xmax (int): number of cells in horizontal axis.
    - ymax (int): number of cells in vertical axis.
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Methods:
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the AlternateAngleStrat instance."""
        super().__init__(maze)

    def move(self, ghost_pos: tuple[int, int],
             pacman_pos: tuple[int, int]) -> tuple[
                 tuple[int, int], Directions]:
        """Calculate the next position towards pacman position.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, a new path towards pacman is
        computed.
        """
        if (self.path == [] or ghost_pos != self.ghost_saved_pos or
            ghost_pos in self.maze.intersection_cells):
            self.path = self.find_path(ghost_pos, pacman_pos,
                                       calculate_manhattan)
        self.ghost_saved_pos = (
            ghost_pos[0] + Movements[self.path[0].name].value[0],
            ghost_pos[1] + Movements[self.path[0].name].value[1])
        return (self.ghost_saved_pos, self.path.pop(0))


class ChaseOnSpot(Strategy):
    """Class ChaseOnSpot, inheriting from Strategy.

    #### Description:
    Move the ghost on the Pacman spotted position.

    This strategy selects the Pacman position as target and calculates the
    path from the ghost's current position towards that target.

    The target and path are updated with the new pacman position when the ghost
    reach target, if Pacman is still in chasing range. If the ghost quit
    chasing mode or die, the target and path are updated.

    #### Inherited attributes:
    - maze(Map): The Map instancied.
    - grid (list[list[Cell]]): Reference to the gris of Cells used by the
        strategy to determine valid movements and paths.
    - xmax (int): number of cells in horizontal axis.
    - ymax (int): number of cells in vertical axis.
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Methods:
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the AlternateAngleStrat instance."""
        super().__init__(maze)

    def move(self, ghost_pos: tuple[int, int],
             pacman_pos: tuple[int, int]) -> tuple[
                 tuple[int, int], Directions]:
        """Calculate the next position towards pacman position.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, a new path towards pacman is
        computed.
        """
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            self.path = self.find_path(ghost_pos, pacman_pos,
                                       calculate_manhattan)
        self.ghost_saved_pos = (
            ghost_pos[0] + Movements[self.path[0].name].value[0],
            ghost_pos[1] + Movements[self.path[0].name].value[1])
        return (self.ghost_saved_pos, self.path.pop(0))


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
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Atributes:
    - target (tuple[int, int]): Current destination selected by the strategy.

    #### Methods:
    - choose_target(): Select a new destination for the ghost.
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the AlternateAngleStrat instance."""
        super().__init__(maze)

    def choose_target(self, ghost_pos: tuple[int, int]) -> tuple[int, int]:
        """Select a new destination for the ghost.

        Chooses a target among the predefined set of important positions
        (the four corners of the maze and the central cell), excluding the
        ghost's current position from the choices if it happens to match
        one of them.
        """
        targets: list[tuple[int, int]] = [(0, 0),
                                          (0, self.ymax),
                                          (self.xmax, 0),
                                          (self.xmax, self.ymax),
                                          (self.xmax // 2, self.ymax // 2)]
        if ghost_pos in targets:
            targets.remove(ghost_pos)
        return choice(targets)

    def move(self, ghost_pos: tuple[int, int],
             _: tuple[int, int]) -> tuple[tuple[int, int], Directions]:
        """Calculate the next position towards the current target.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, a new target is chosen
        and a new path towards it should be computed.
        """
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            target: tuple[int, int] = self.choose_target(ghost_pos)
            self.path = self.find_path(ghost_pos, target,
                                       calculate_manhattan)
        self.ghost_saved_pos = (
            ghost_pos[0] + Movements[self.path[0].name].value[0],
            ghost_pos[1] + Movements[self.path[0].name].value[1])
        return (self.ghost_saved_pos, self.path.pop(0))


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
    - path (list[Directions]): Sequence of directions leading to the target.
    - ghost_saved_pos (tuple[int, int]): Previous ghost position used to
      continue to move toward target when this strategy is called again.

    #### Attributes:
    - target (tuple[int, int]): Current destination selected by the strategy.

    #### Methods:
    - ghost_area(): Identify the area in which the ghost is located.
    - chose_target(): Select a new destination for the ghost.
    - move(): Calculate the next position towards the current target.
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the PatrollingAngleStrat instance."""
        super().__init__(maze)

    def ghost_area(self, ghost_pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Identifies the area in which the ghost is located. Returns the
        coordinates of the cells at the bottom-left and top-right corners of
        this area.
        """
        middle_x: int = self.xmax // 2 - 1
        middle_y: int = self.ymax // 2 - 1

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
        """Select a new destination for the ghost within a given area.

        Randomly picks a cell inside the bounds of `area`. If the chosen
        cell is a wall (no accessible neighbours) or corresponds to the
        ghost's current position, the selection is retried recursively
        until a valid cell is found.
        """
        target: tuple[int, int] = (randint(area[0][0], area[1][0]),
                                   randint(area[0][1], area[1][1]))
        if (self.grid[target[0]][target[1]].walls == 15 or
                self.grid[target[0]][target[1]].coordinates == ghost_pos):
            return self.choose_target(area, ghost_pos)
        return target

    def move(self, ghost_pos: tuple[int, int],
             _: tuple[int, int]) -> tuple[tuple[int, int], Directions]:
        """Calculate the next position towards the current target.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, the ghost's patrol area
        is recomputed and a new target is chosen within it.
        """
        if self.path == [] or ghost_pos != self.ghost_saved_pos:
            area = self.ghost_area(ghost_pos)
            target: tuple[int, int] = self.choose_target(area, ghost_pos)
            print("target: ", target)
            self.path = self.find_path(ghost_pos, target,
                                       calculate_manhattan)
            print("path: ", self.path)
        self.ghost_saved_pos = (
            ghost_pos[0] + Movements[self.path[0].name].value[0],
            ghost_pos[1] + Movements[self.path[0].name].value[1])
        return (self.ghost_saved_pos, self.path.pop(0))


def calculate_manhattan(ghost: tuple[int, int],
                        target: tuple[int, int]) -> int:
    """Calculate the Manhattan distance between two positions and returns
    it.

    The Manhattan distance is the sum of the absolute differences between
    the two coordinates. It can be used by ghost strategies to estimate
    how close a ghost is to its target.
    """
    return abs(ghost[0] - target[0]) + abs(ghost[1] - target[1])


strat_dict: dict[str, Type[Strategy]] = {
    "AlternateAngleStrat": AlternateAngleStrat,
    "ChaseOnSpot": ChaseOnSpot,
    "PatrollingAngleStrat": PatrollingAngleStrat,
    "ChaseStumbling": ChaseStumbling}
