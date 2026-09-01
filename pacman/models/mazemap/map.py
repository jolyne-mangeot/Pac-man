"""### File: /pacman/models/mazemap/map.py

### Date: 2026-08-06

### Description: 
This module defines the `Map` class, which represents the game map and
manages the placement and consumption of gums.

The map is represented as a two-dimensional grid of `Cell` objects.
Each cell stores information about its walls and the gums it contains.

The `Map` class is responsible for:
- storing the maze layout;
- placing regular and super gums on valid cells;
- removing gums when Pacman collects them;
- keeping track of the remaining gums;
- determining whether all gums have been collected.


### Classes:
- Map: Represent the Pacman game map and its gums.
"""
from random import shuffle
from typing import cast

from .utils import maze_interface, Cell, Node, Directions, Movements


RIGHT_TURN: dict[Directions : Directions] = {
    Directions.UP: Directions.RIGHT,
    Directions.RIGHT: Directions.DOWN,
    Directions.DOWN: Directions.LEFT,
    Directions.LEFT: Directions.UP
}

LEFT_TURN: dict[Directions : Directions] = {
    Directions.UP: Directions.LEFT,
    Directions.LEFT: Directions.DOWN,
    Directions.DOWN: Directions.RIGHT,
    Directions.RIGHT: Directions.UP
}

OPPOSITE_DIRECTION: dict[Directions, Directions] = {
    Directions.UP: Directions.DOWN,
    Directions.DOWN: Directions.UP,
    Directions.LEFT: Directions.RIGHT,
    Directions.RIGHT: Directions.LEFT,
}


class Map: 
    """Class Map

    #### Description: 
    This class represent the Pacman game map and its gums.

    The map is stored as a two-dimensional grid of `Cell` objects.
    Each cell contains information about its walls and whether it contains
    a regular gums or a super gums.

    The class also keeps counters for the remaining gums, allowing the
    game to determine when the current level has been completed.


    ### Atributes:
    - width (int): Number of cells along the horizontal axis.
    - height (int): Number of cells along the vertical axis.
    - gum_percent (int): Percentage of valid cells that should contain
      regular gums.
    - seed (int): Seed used to generate the maze layout.
    - map (list[list[Cell]]): Two-dimensional grid representing the maze.
    - nb_simple_gum (int): Number of regular gums currently present.
    - nb_super_gum (int): Number of super gums currently present.
    - intersection_cells(set[tuple[int, int]]): All intersections of the
      maze (cells with 3 or 4 opened walls).


    ### Methods:
    - super_gum_placement(): Place super gums at the map corners.
    - simple_gum_placement(): Randomly place regular gums on valid cells.
    - update_gum(): Remove and return the type of gum at Pacman's position.
    - check_gum(): Check whether all gums have been collected.
    - get_cell(): Return the Cell object at the given coordinates.
    - get_neighbor_coords(): Return the coordinates adjacent to a cell in
      a given direction.
    - get_neighbor_nodes(): Return the recorded neighbour nodes of an
      intersection cell.
    - record_maze_intersections(): Identify and store every intersection
      cell of the maze.
    - find_intersect(): Follow a corridor from a cell to the next
      intersection in a given direction.
      directly reachable from a position.
    - generate_cell_graph(): Build the graph of cells and their
      neighbour nodes, used by the A* pathfinding algorithm.
    """
    def __init__(self, width: int, height: int, gum_percent: int, seed: int) -> None:
        """Initialises the attributes of the Map instance."""
        self.width: int = width
        self.height: int = height
        self.gum_percent: int = gum_percent
        self.seed: int = seed
        self.map: list[list[Cell]] = maze_interface(self.width, self.height, self.seed)
        self.nb_simple_gum: int = 0
        self.nb_super_gum: int = 0
        self.intersection_cells: set[tuple[int, int]] = set()
        self.simple_gums: set[tuple[int, int]] = set()
        self.super_gums: set[tuple[int, int]] = set()

    def __repr__(self) -> None:
        """Method to display debug mode of the map."""
        lines: list[str] = []
        for y in range(self.height):
            toplane: str = "+"
            for x in range(self.width):
                if self.map[x][y].walls & 1:
                    toplane += "---+"
                else:
                    toplane += "   +"
            lines.append(toplane)
            midlane: str = ""
            for x in range(self.width):
                if self.map[x][y].walls & 8:
                    midlane += "|"
                else:
                    midlane += " "
                if self.map[x][y].super_gum is True:
                    midlane += " o "
                elif self.map[x][y].simple_gum is True:
                    midlane += " . "
                else:
                    midlane += "   "
            if self.map[self.width - 1][y].walls & 2:
                midlane += "|"
            else:
                midlane += " "
            lines.append(midlane)
        botlane: str = "+"
        for x in range(self.width):
            botlane += "---+"
        lines.append(botlane)
        return "\n".join(lines)

    # _________________________________________________________________________
    #                           GUMS MANAGEMENT
    # _________________________________________________________________________

    def super_gum_placement(self) -> None:
        """Add super gum at each corner of the map."""
        self.map[0][0].super_gum = True
        self.map[0][(self.height - 1)].super_gum = True
        self.map[(self.width - 1)][0].super_gum = True
        self.map[((self.width - 1))][(self.height - 1)].super_gum = True
        self.super_gums.update((0, 0), (0, self.height - 1),
                            (self.self.width - 1, 0),
                            (self.width - 1, self.height - 1))
        self.nb_super_gum += 4

    def simple_gum_placement(self) -> None:
        """Add simple gum in corridors of the map."""
        available_cells: list[Cell] = []
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].simple_gum is True:
                    continue
                if self.map[x][y].walls == 15:
                    continue
                available_cells.append(self.map[x][y])
        nb_simple_gum: int = ((len(available_cells) * self.gum_percent) // 100)
        shuffle(available_cells)
        for cell in available_cells[:nb_simple_gum]:
            cell.simple_gum = True
            self.simple_gums.add(self.self.get_cell(cell))
            self.nb_simple_gum += 1

    def update_gum(self, pos_pacman: tuple[int, int]) -> str:
        """Update gum on the grid depending on Pacman position."""
        if self.map[pos_pacman[0]][pos_pacman[1]].simple_gum == True:
            self.map[pos_pacman[0]][pos_pacman[1]].simple_gum = False
            self.simple_gums.remove(pos_pacman)
            self.nb_simple_gum -= 1
            return "simple_gum"
        elif self.map[pos_pacman[0]][pos_pacman[1]].super_gum == True:
            self.map[pos_pacman[0]][pos_pacman[1]].super_gum = False
            self.super_gums.remove(pos_pacman)
            self.nb_super_gum -= 1
            return "super_gum"
        else:
            return "none"

    def check_gum(self) -> bool:
        """Check if all gums are eat by Pacman. Return True is it's the case
        to end the level. Return False if they are any gums or super gum left.
        """
        if self.nb_super_gum == 0 and self.nb_simple_gum == 0:
            return True
        else:
            return False

    # _________________________________________________________________________
    #                      INTERSECTION GRAPH UTILS
    # _________________________________________________________________________

    def get_cell(self, cell: tuple[int, int]) -> Cell:
        """Returns the Cell object present at the given coordinates."""
        return self.map[cell[0]][cell[1]]

    def get_neighbor_coords(self, coords: tuple[int, int], mov: Movements) -> tuple[int, int]:
        """Return the coordinates of the cell adjacent to `coords` in the
        direction given by `mov`.
        """
        neighbor: tuple[int, int] = (coords[0] + mov.value[0],
                                     coords[1] + mov.value[1])
        return neighbor

    def get_neighbor_nodes(self, cell: tuple[int, int]) -> list[Node]:
        """Return the list of `Node` objects already recorded as neighbours
        of the intersection at `cell`.
        """
        return cast(list[Node], getattr(self.get_cell(cell), "neighbor_nodes"))

    def record_maze_intersections(self) -> None:
        """Loops through every cell of the Maze to append them to the
        intersection_cells set when they are surrounded by 0 or 1 wall,
        meaning they connect more than 3 cells.
        """
        self.intersection_cells.clear()
        for x in range(self.width):
            for y in range(self.height):
                if self.map[x][y].walls in (0, 1, 2, 4, 8):
                    self.intersection_cells.add((x, y))

    def find_intersect(
            self, cell: tuple[int, int], dir: Directions) -> Node:
        """Starting from `cell` and moving in `dir`, walks the maze corridor
        cell by cell, accumulating the distance travelled and the sequence
        of directions taken. If the path leaves the grid, or reaches a dead
        end where none of the current, right-turn or left-turn directions
        are open, a `ValueError` is raised. As soon as an intersection cell
        is reached, a `Node` is returned, carrying its coordinates, the
        total distance from `cell`, and the full route taken to get there.
        """
        distance_bet_cells: int = 0
        route_taken: list[Directions] = []
        while True:
            next_cell = self.get_neighbor_coords(
                        cell, Movements[dir.name])
            
            if not (0 <= next_cell[0] < self.width
                    and 0 <= next_cell[1] < self.height):
                raise ValueError
            cell = next_cell
            distance_bet_cells += 1
            route_taken.append(dir)
            if cell in self.intersection_cells:
                return Node(cell, distance_bet_cells, route_taken)
            current_cell: Cell = self.get_cell(cell)
            if not (current_cell.walls & dir.value):
                continue

            right = RIGHT_TURN[dir]
            left = LEFT_TURN[dir]
            if not (current_cell.walls & right.value):
                dir = right
                continue
            if not (current_cell.walls & left.value):
                dir = left
                continue
            raise ValueError

    def generate_cell_graph(self) -> None:
        """Calls record_maze_intersections to instantiate the
        intersection_cells set. Then calls find_intersect methods to
        instanciate a Node object for each neighbour of an intersection.
        These Node are inserted into a list added as attribute to Cell
        objects for future reference.

        For every intersection and every one of its open directions, the
        corridor is followed until the next intersection is reached. The
        resulting `Node` is added to that intersection's `neighbor_nodes`
        list, unless a neighbour with the same coordinates already exists,
        in which case only the shorter of the two distances (and its
        corresponding path) is kept. Self-loops (a direction that leads
        back to the same intersection) are ignored.
        """
        self.record_maze_intersections()
        for x in range(self.width):
            for y in range(self.height):
                cell: Cell = self.get_cell((x, y))
                for direction in Directions:
                    if direction == Directions.NONE:
                        continue
                    if cell.walls & direction.value:
                        continue
                    try:
                        found_node: Node = self.find_intersect(
                            (x, y), direction)
                    except ValueError:
                        continue
                    if found_node.coords == (x, y):
                        continue
                    for neighbour in cell.neighbor_nodes:
                        if neighbour.coords == found_node.coords:
                            if found_node.distance < neighbour.distance:
                                neighbour.distance = found_node.distance
                                neighbour.path = found_node.path
                            break
                    else:
                        cell.neighbor_nodes.append(found_node)