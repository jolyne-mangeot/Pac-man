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
- Map
"""
from random import shuffle

from .utils import maze_interface, Cell, CellCoordinates


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

    def update_gum(self, pos_pacman: CellCoordinates) -> str:
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
