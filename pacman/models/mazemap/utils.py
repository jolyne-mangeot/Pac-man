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
- Directions(IntEnum): Represents the possible movement directions and the
  corresponding wall bitmasks.
- Movements(Enum): Associates each movement direction with its coordinate
  offset.
- Cell: Represents a single cell of the maze.
- Node: Store additional informations about each cell for path calculation>

#### Functions:
- maze_interface(): Generate a maze and convert it into a two-dimensional
  grid of `Cell` objects.
"""
from enum import IntEnum, Enum

from mazegenerator import MazeGenerator


class Directions(IntEnum):
    """Class Directions, inheriting from IntEnum.

    #### Description:
    Represent the four possible movement directions.

    The enum values correspond to the wall bitmasks used by the maze.
    `NONE` represents an entity that is currently not moving.

    #### Attributes:
    - UP (int): Move towards the top of the map.
    - RIGHT (int): Move towards the right of the map.
    - DOWN (int): Move towards the bottom of the map.
    - LEFT (int): Move towards the left of the map.
    - NONE (int): No movement direction.
    """
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8
    NONE = 15


class Movements(Enum):
    """Class Movements, inheriting from Enum.

    #### Description:
    Map movement directions to their coordinate offsets.

    Each enum value contains the `(x, y)` displacement associated with
    a movement direction.

    #### Attributes:
    - UP (tuple[int, int]): Offset `(0, -1)`.
    - RIGHT (tuple[int, int]): Offset `(1, 0)`.
    - DOWN (tuple[int, int]): Offset `(0, 1)`.
    - LEFT (tuple[int, int]): Offset `(-1, 0)`.
    """
    UP = (0, -1)
    RIGHT = (+1, 0)
    DOWN = (0, +1)
    LEFT = (-1, 0)


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
        self.neighbor_nodes: list[Node] = []
        self.walls: int = walls
        self.super_gum: bool = False
        self.simple_gum: bool = False


class Node:
    """
    Node Class

    #### Description:
    Store additional informations about each cell
    of the Map. In this graph implementation, each intersection cell
    holds these informations about each of their neighbours intersections.
    Helps navigating and saving traveling time.

    Attributes:
    """
    def __init__(
            self, coords: tuple[int, int], distance: int,
            path: tuple[Directions, ...]) -> None:
        self.coords: tuple[int, int] = coords
        self.distance: int = distance
        self.path: tuple[Directions, ...] = path


def maze_interface(width: int, height: int, seed: int) -> list[list[Cell]]:
    """Generate and format the maze used by the game.
    This function uses `MazeGenerator` to create a maze and converts its
    internal grid representation into the format more logical.
    `MazeGenerator` provides its grid using `(y, x)` indexing, while we wanted
    to use `(x, y)` indexing. This function performs this conversion and
    creates one `Cell` instance for each position in the maze.

    Returns a two-dimensional list of `Cell` objects indexed by `[x][y]`.
    Each cell contains its coordinates and wall information.
    """
    maze = MazeGenerator(size=(width, height),
                         seed=seed, entry_cell=(0, 0), exit_cell=(0, 0))
    grid = maze.maze
    cells_list: list[list[Cell]] = []
    for x in range(width):
        cells_list.append([])
        for y in range(height):
            cells_list[x].append(Cell(coordinates=(x, y), walls=grid[y][x]))
    return cells_list
