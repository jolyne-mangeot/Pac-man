"""#### Date: 2026-08-06

#### Description:
This module provides utility classes and functions used by the map module.

It defines the `Cell` class, which represents a single cell of the game
maze, and the `maze_interface()` function, which converts the maze generated
by `MazeGenerator` into the grid structure used by the Pacman game.

The module acts as an interface between the external maze generator and the
game's map model. It ensures that each cell is represented by a `Cell`
instance containing its coordinates, walls and gum states.

#### Classes:
- Cell: Represents a single cell of the game maze.

#### Functions:
- maze_interface(): Generate a maze and convert it into a two-dimensional
  grid of `Cell` objects.
"""

from mazegenerator import MazeGenerator


class Cell:
    """Class Cell

    #### Description:
    Represent a single cell of the game maze.

    A `Cell` stores the information required by the game to represent one
    position in the maze. It contains its coordinates, the walls surrounding
    it and the gums currently present on the cell.

    Gum states are initialized to `False` and can be modified by the `Map`
    class when gums are placed or collected.

    ### Attributes:
    - coordinates (tuple[int, int]): Position of the cell in the maze,
      represented as an `(x, y)` coordinate.
    - walls (int): Bitmask representing the walls surrounding the cell.
    - super_gum (bool): Whether the cell currently contains a super gum.
    - simple_gum (bool): Whether the cell currently contains a regular gum.
    """
    def __init__(self, coordinates: tuple[int, int], walls: int) -> None:
        """Initialises the attributes of the Cell instance."""
        self.coordinates: tuple[int, int] = coordinates
        self.walls: int = walls
        self.super_gum: bool = False
        self.simple_gum: bool = False


def maze_interface(width: int, height: int, seed: int) -> list[list[Cell]]:
    """Generate and format the maze used by the game.
    This function uses `MazeGenerator` to create a maze and converts its
    internal grid representation into the format more logical.
    `MazeGenerator` provides its grid using `(y, x)` indexing, while the
    we wanted to use `(x, y)` indexing. This function performs this conversion
    and creates one `Cell` instance for each position in the maze.

    Returns a two-dimensional list of `Cell` objects indexed by `[x][y]`.
    Each cell contains its coordinates and wall information.
    """
    maze = MazeGenerator(size=(width, height), seed=seed, entry_cell=(0, 0), exit_cell=(0, 0))
    grid = maze.maze
    cells_list: list[list[Cell]] = []
    for x in range(width):
        cells_list.append([])
        for y in range(height):
            cells_list[x].append(Cell(coordinates=(x, y), walls=grid[y][x]))
    return cells_list
