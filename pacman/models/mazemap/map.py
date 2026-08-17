"""### File: /pacman/models/map/map.py

### Date: 2026-08-06

### Description: This module contains the `Map` class, which manages the
distribution of `gum` and `super_gum` across the grid.

### Classes:
- Map
"""
from random import shuffle

from .utils import maze_interface, Cell, CellCoordinates


class Map: 
    """Class Map

    #### Description: 
    This class manage the Map of Pacman. It contains the matrix of cell in the
    map attribute which is a list[list[Cell]]. It manage gum and super gum
    position on the grid. It manage gum deletion if Pacman position is on a
    gum. It check nb of gums in the grid to know if the level is finished or
    not.

    ### Atributes:
    - width: int
    - height: int
    - gum_percent: int
    - seed: int
    - map: list[list[Cell]]
    - nb_simple_gum: int
    - nb_super_gum: int

    ### Methods:
    - init(self) -> None
    - repr(self) -> None
    - super_gum_placement(self) -> None
    - simple_gum_placement(self) -> None
    - update_gum(self, pos_pacman: CellCoordinates) -> str
    - check_gum(self) -> bool
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
        """Method to display debug mode of the map"""
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
