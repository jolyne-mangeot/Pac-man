"""### File: /pacman/models/map/utils.py

### Date: 2026-08-06

### Description: This module contains all tools used by the map module. Cell
class is declared here.

### Classes:
- Cell

### Functions:
- maze_interface(width: int, height: int, seed: int) -> list[list[Cell]]:
"""

from mazegenerator import MazeGenerator


CellCoordinates = tuple[int, int]


class Cell:
    """Class Cell

    All cells of the grid are instancied here. Each Cell instance contains
    information about its walls and its coordinates.

    ### Attributes:
    - coordinates: CellCoordinates
    - walls: int
    - super_gum: bool
    - simple_gum: bool

    ### Methods:
    - init()
    """
    def __init__(self, coordinates: CellCoordinates, walls: int) -> None:
        """Initialises the attributes of the Cell instance."""
        self.coordinates: CellCoordinates = coordinates
        self.walls: int = walls
        self.super_gum: bool = False
        self.simple_gum: bool = False


def maze_interface(width: int, height: int, seed: int) -> list[list[Cell]]:
    """Formats the maze grid created by the maze generator wich is ordered
    by y,x as we need a grid ordered by x,y.
    Returns an array of Cell instances, each containing its coordinates and
    information about its walls.
    """
    maze = MazeGenerator(size=(width, height), seed=seed)
    grid = maze.maze
    print(grid)
    cells_list: list[list[Cell]] = []
    for x in range(width):
        cells_list.append([])
        for y in range(height):
            cells_list[x].append(Cell(coordinates=(x, y), walls=grid[y][x]))
    return cells_list


if __name__ == "__main__":
    """Test the maze_interface() function to formats the grid made by
    mazegenerator."""
    grid_test = maze_interface(15, 15, 42)
    for x in range(len(grid_test)):
            for y in range(len(grid_test[0])):
                print(grid_test[x][y].coordinates)
                print(grid_test[x][y].walls)