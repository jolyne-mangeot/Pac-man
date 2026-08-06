"""### File: /pacman/models/map/map.py

### Date: 2026-08-06

### Description: This module contains the `map` class, which manages the
# distribution of `gum` and `super_gum` across the grid.

### Classes:
- Map
"""
from random import shuffle

from utils import maze_interface, Cell, CellCoordinates


class Map:
    """Class Map

    The Map of Pacman is instancied here. Contains the matrix of cell and
    manage gum and super gum position on the grid.

    ### Atributes:
    - width: int
    - height: int
    - gum_percent: int
    - seed: int
    - map: list[list[Cell]]

    ### Methods:
    - init()
    - super_gum_placement()
    - simple_gum_placement()
    """
    def __init__(self, map_config: dict[str, int]) -> None:
        """Initialises the attributes of the Map instance."""
        self.width: int = map_config["width"]
        self.height: int = map_config["height"]
        self.gum_percent: int = map_config["gum_percent"]
        self.seed: int = map_config["seed"]
        self.map: list[list[Cell]] = maze_interface(self.width, self.height, self.seed)

    def display_map(self):
        """Method to display debug mode of the map"""
        for x in range(self.width):
            toplane: str = "+"
            for y in range(self.height):
                if self.map[x][y].walls & 1:
                    toplane += "---+"
                else:
                    toplane += "   +"
            print(toplane)
            midlane: str = ""
            for y in range(self.height):
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
            print(midlane)
            botlane: str = "+"
            for y in range(self.height):
                if self.map[x][y].walls & 4:
                    botlane += "---+"
                else:
                    botlane += "   +"
            print(botlane)

    def super_gum_placement(self):
        """Add super gum at each corner of the map."""
        self.map[0][0].super_gum = True
        self.map[0][(self.height - 1)].super_gum = True
        self.map[(self.width - 1)][0].super_gum = True
        self.map[((self.width - 1))][(self.height - 1)].super_gum = True





if __name__ == "__main__":
    """Test the map display : maze and gum placement with ASCII char."""
    map_config_test: dict[str, int] = {"width": 15, "height": 15, "seed": 42,
                                       "gum_percent": 80}
    map_test: Map = Map(map_config_test)
    map_test.display_map()
