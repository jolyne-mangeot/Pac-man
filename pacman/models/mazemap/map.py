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

from .utils import maze_interface, Cell, Node, Directions, Movements


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
            self.nb_simple_gum += 1

    def update_gum(self, pos_pacman: tuple[int, int]) -> str:
        """Update gum on the grid depending on Pacman position."""
        if self.map[pos_pacman[0]][pos_pacman[1]].simple_gum == True:
            self.map[pos_pacman[0]][pos_pacman[1]].simple_gum = False
            self.nb_simple_gum -= 1
            return "simple_gum"
        elif self.map[pos_pacman[0]][pos_pacman[1]].super_gum == True:
            self.map[pos_pacman[0]][pos_pacman[1]].super_gum = False
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
    #                         A* ALGORITHM UTILS
    # _________________________________________________________________________

    def get_cell(self, cell: tuple[int, int]) -> Cell:
        """Returns the Cell object present at the given coordinates."""
        return self.cells[cell[0]][cell[1]]

    def record_maze_intersections(self) -> None:
        """Loops through every cell of the Maze to append them to the
        intersection_cells set when they are surrounded by 0 or 1 wall,
        meaning they connect more than 3 cells.
        """
        for x in range(self.maze.width):
            for y in range(self.maze.height):
                if self.maze.cells[x][y].walls in (0, 1, 2, 4, 8):
                    self.intersection_cells.add(self.get_cell((x, y)))

    def find_next_intersect(
            self, cell: tuple[int, int], dir: Directions) -> Node:
        """Given a cell and a direction, connects to the first found
        intersection_cell and returns a Node object from the information found
        during navigation. Raise FoundDeadEnd error when hitting a wall.
        Automatically turns when the path winds.
        """
        distance_bet_cells: int = 1
        next_cell = self.maze.get_neighbor_coords(
            cell, Movements[dir.name].value)
        route_taken: list[tuple[int, int]] = [next_cell]
        while next_cell not in self.intersection_cells:
            if self.maze.get_cell(next_cell).walls[dir] is False:
                pass
            elif self.maze.get_cell(next_cell).walls[(dir + 1) % 4] is False:
                dir = Directions((dir + 1) % 4)
            elif self.maze.get_cell(next_cell).walls[(dir + 3) % 4] is False:
                dir = Directions((dir + 3) % 4)
            else:
                raise ValueError
            next_cell = self.maze.get_neighbor_coords(
                next_cell, Movements[dir.name].value)
            distance_bet_cells += 1
            route_taken.append(next_cell)
        return Node(
            next_cell, distance_bet_cells, tuple(route_taken))

    def generate_cell_graph(self) -> None:
        """Calls record_maze_intersections to instantiate the
        intersection_cells set. Then calls find_next_intersect methods to
        instanciate a Node object for each neighbour of an intersection.
        These Node are inserted into a list added as attribute to Cell
        objects for future reference.
        """
        self.record_maze_intersections()
        found_node: Node
        for inter in self.intersection_cells:
            for direction in filter(
                    lambda dir: not self.maze.get_cell(inter).walls & dir.value,
                    Directions):
                try:
                    found_node = (self.find_next_intersect(inter, direction))
                except ValueError:
                    continue
                if found_node.coords == inter:
                    continue
                for neighbour in self.get_neighbour_nodes(inter):
                    if neighbour.coords == found_node.coords:
                        if found_node.distance < neighbour.distance:
                            neighbour.distance = found_node.distance
                            neighbour.path = found_node.path
                        break
                else:
                    inter.neighbour_nodes.append(found_node)