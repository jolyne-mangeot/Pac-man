"""File: /pacman/models/entity/strategies.py

Date: 2026-08-17
#### Description:
This module defines the movement strategies used by ghost entities.

A strategy is responsible for calculating the next position of a ghost
according to a specific movement or pathfinding behaviour.

Strategies are separated from the `Ghost` class so that different ghost
behaviours can be implemented, combined and replaced without modifying
the entity itself.

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
from typing import Literal
from heapq import heappop, heappush
from random import choice, randint
from dataclasses import dataclass, field

from pacman.models import Cell
from pacman.models import Map

from ..mazemap.map import Directions, Movements, Node, OPPOSITE_DIRECTION


class AStarState:
    """Class AStarState.

    #### Description:
    Stores the temporary state used by the A* algorithm.

    An instance of this class is created for each call to `find_path` and
    passed along to the various A* helper methods of `Strategy`, so that
    the search state stays local to a single pathfinding request instead
    of being stored on the `Strategy` instance itself.
    
    #### Attributes:
    - open_nodes (list[tuple[int, tuple[int, int]]]): Min-heap (priority
      queue) of nodes still to be explored, as `(priority, coords)` pairs,
      where `priority` is the estimated total cost (distance so far plus
      the Manhattan-distance heuristic to the target). Nodes are popped
      in increasing priority order via `heapq`.
    - closed_nodes (set[tuple[int, int]]): Coordinates of the nodes that
      have already been fully processed by the search, so they are not
      expanded again.
    - g_score (dict[tuple[int, int], int]): Maps each visited node's
      coordinates to the shortest known distance from the ghost's
      starting position to that node.
    - came_from (dict[tuple[int, int], tuple[tuple[int, int],
                      list[Directions]]]):
      Maps each node's coordinates to the predecessor node it was reached
      from, along with the list of directions travelled to get there.
      Used by `reconstruct_path` to rebuild the full path once the
      target has been reached.
    """
    def __init__(self) -> None:
        """Initialises the temporary state used by the A* algorithm."""
        self.open_nodes: list[tuple[int, tuple[int, int]]] = []
        self.closed_nodes: set[tuple[int, int]] = set()
        self.g_score: dict[tuple[int, int], int] = {}
        self.came_from: dict[tuple[int, int],
                             tuple[tuple[int, int],
                             list[Directions]]] = {}


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
    - move(): Calculate the next position for the ghost.

    Description:
    """
    def __init__(self, maze: Map):
        """Initialises the attributes of the Strategy instance."""
        self.maze: Map = maze
        self.grid: list[list[Cell]] = maze.map
        self.xmax: int = len(self.grid) - 1
        self.ymax: int = len(self.grid[0]) - 1

    #@abstractmethod
    #def move(self, ghost_pos: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
    #    """Calculate the ghost's next position. Returns the next position
    #    chosen by the strategy.
    #    """
    #    pass

    def update_node(self, state: AStarState, coords: tuple[int, int],
                    distance: int, path: list[Directions],
                    predecessor: tuple[int, int] | None,
                    target: tuple[int, int]) -> None:
        """Update a node's score if a shorter path to it was found.

        Compares the newly computed `distance` to the best known distance
        for `coords`. If it is not strictly shorter, the node is left
        unchanged. Otherwise, `coords` becomes the new best known distance,
        its predecessor and the directions leading to it are recorded (so
        the path can later be rebuilt via `reconstruct_path`), and the node
        is pushed onto the A* open set with a priority equal to the
        distance plus the Manhattan-distance heuristic to `target`.
        """
        if distance >= state.g_score.get(coords, float("inf")):
            return
        state.g_score[coords] = distance
        if predecessor is not None:
            state.came_from[coords] = (predecessor, path)
        priority = distance + calculate_manhattan(coords, target)
        heappush(state.open_nodes, (priority, coords))

    def initialize_start_nodes(self, state: AStarState,
                                ghost: tuple[int, int],
                                connections: list[Node],
                                target: tuple[int, int]) -> None:
        """Initialize the nodes directly reachable from the ghost.

        Seeds the A* open set with every intersection listed in
        `connections`, i.e. the intersections the ghost can reach without
        crossing another intersection first. Each of these nodes is
        registered via `update_node`, using the ghost's own position as
        predecessor (or `None` when the node's coordinates are the ghost's
        position itself), so the search can start expanding from there.
        """
        for node in connections:
            predecessor = None if node.coords == ghost else ghost
            self.update_node(state, node.coords, node.distance,
                        node.path, predecessor, target)

    def get_best_target_connections(self,
                                    connections: list[Node]) -> dict[
                                        tuple[int, int],
                                        tuple[int, list[Directions]]]:
        """Keep the shortest connection from each intersection to target.

        Several distinct paths may connect the same intersection to the
        target; only the shortest one is relevant to A*. This method
        collapses the list of `Node` connections into a dictionary mapping
        each intersection's coordinates to the shortest known distance and
        corresponding path towards the target, discarding any longer
        alternative found for the same intersection.
        """
        best_connections: dict[tuple[int, int], tuple[int, list[Directions]]] = {}
        for node in connections:
            previous = best_connections.get(node.coords)
            if previous is None or node.distance < previous[0]:
                best_connections[node.coords] = (node.distance, node.path)
        return best_connections

    def reconstruct_path(self, current: tuple[int, int],
                         came_from: dict[tuple[int, int],
                                     tuple[tuple[int, int],
                                     list[Directions]]],
                         target_path: list[Directions]) -> list[Directions]:
        """Reconstruct the path from ghost to target.

        Walks backwards from `current` (the intersection at which the A*
        search reached the target's connections) through the `came_from`
        predecessor chain built during the search, prepending the stored
        directions at each step until the ghost's starting position is
        reached. The `target_path` (the path from `current` to the actual
        target cell) is then appended in reverse, using the opposite
        direction of each step, since it was originally computed from the
        target towards the intersection. The result is the full,
        ordered sequence of directions leading the ghost from its current
        position to the target.
        """
        path: list[Directions] = []
        while current in came_from:
            previous, directions = came_from[current]
            path[0:0] = directions
            current = previous
        path.extend(OPPOSITE_DIRECTION[dir] for dir in reversed(target_path))
        return path

    def a_star(self, state: AStarState,
               target_connections: dict[tuple[int, int],
                                        tuple[int, list[Directions]]],
               target: tuple[int, int]) -> list[Directions]:
        """Run A* on the intersection graph.

        Repeatedly pops the intersection with the lowest priority
        (distance so far + Manhattan-distance heuristic) from the open
        set. Nodes already processed are skipped. As soon as a popped
        intersection is one of the `target_connections`, the search stops
        and the full path is rebuilt via `reconstruct_path`. Otherwise,
        every neighbouring intersection of the current node is relaxed
        through `update_node`, extending the search. If the open set is
        exhausted without reaching a target connection, an empty list is
        returned, meaning no path exists between the ghost and the target.
        """
        while state.open_nodes:
            _, current = heappop(state.open_nodes)
            if current in state.closed_nodes:
                continue
            state.closed_nodes.add(current)
            target_connection = target_connections.get(current)
            if target_connection is not None:
                _, target_path = target_connection
                return self.reconstruct_path(current, state.came_from, target_path)
            current_cell = self.maze.get_cell(current)
            for neighbour in current_cell.neighbor_nodes:
                if neighbour.coords in state.closed_nodes:
                    continue
                self.update_node(state, neighbour.coords,
                            state.g_score[current] + neighbour.distance,
                            list(neighbour.path), current, target)
        return []

    def find_path(self, ghost: tuple[int, int],
                 target: tuple[int, int]) -> list[Directions]:
        """Find the shortest path from ghost to target using A* Algorithm.

        Regenerates the maze's intersection graph, then computes the
        connections linking the ghost's and the target's positions to
        their nearest intersections. If the ghost already stands on the
        target, or if either position cannot reach any intersection, the
        search is skipped (returning `[]` in the latter case). Otherwise,
        the target's connections are reduced to their shortest form, the
        A* open set is seeded from the ghost's position, and the search is
        delegated to `a_star`, which returns the resulting sequence of
        directions.
        """
        if ghost == target:
            return []
        self.maze.generate_cell_graph()
        start_connections = self.maze.get_connections_to_intersections(ghost)
        target_connections = self.maze.get_connections_to_intersections(target)

        if not start_connections or not target_connections:
            return []

        target_connections = self.get_best_target_connections(target_connections)
        state = AStarState()
        self.initialize_start_nodes(state, ghost, start_connections, target)
        return self.a_star(state, target_connections, target)


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
        """Initialises the attributes of the AlternateAngleStrat instance."""
        super().__init__(maze)
        self.target: tuple[int, int] = ()
        self.path: list[Directions] = []
        self.ghost_saved_pos: tuple[int, int] = ()

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


    def move(self, ghost_pos: tuple[int, int], _: tuple[int, int]) -> tuple[int, int]:
        """Calculate the next position towards the current target.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, a new target is chosen
        and a new path towards it should be computed.
        """
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

    def move(self, ghost_pos: tuple[int, int], _: tuple[int, int]) -> tuple[int, int]:
        """Calculate the next position towards the current target.

        If no path is currently stored, or if the ghost's position no
        longer matches the last saved position, the ghost's patrol area
        is recomputed and a new target is chosen within it.
        """
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