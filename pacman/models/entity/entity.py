"""File: /pacman/models/entity/entity.py

Date: 2026-08-04
#### Description: This module manages entity(Pacman and ghosts) for the
pacman game.

#### Classes:
- Entity(ABC)
- Pacman(Entity)
- Ghost(Entity)

#### Enums:
- Directions(IntEnum)
- Movements(Enum)
"""
from abc import ABC
from enum import IntEnum, Enum

from .strategies import Strategy, strat_dict, calculate_manhattan, AlternateAngleStrat
from pacman.models import Cell

class Directions(IntEnum):
    """Class Direction (IntEnum)
    - UP = 1
    - RIGHT = 2
    - DOWN = 4
    - LEFT = 8
    - NONE = 15
    """
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8
    NONE = 15


class Movements(Enum):
    """Class Movements.
    - NORTH = (0, -1)
    - EAST = (+1, 0)
    - SOUTH = (0, +1)
    - WEST = (-1, 0)
    """
    UP = (0, -1)
    RIGHT = (+1, 0)
    DOWN = (0, +1)
    LEFT = (-1, 0)
 

class Entity(ABC):
    """Class Entity

    Atributes:
    - speed: int
    - super_speed: int
    - initial_pos: tuple[int, int]
    - pos: tuple[int, int]
    - direction: Directions
    - is_alive: bool

    Methods:
    - respaw(self) -> None

    Description:
    """

    def __init__(self, speed: int, super_speed: int, initial_pos: tuple[int, int]):
        """Initialises the attributes of the Entity instance."""
        self.speed: int = speed
        self.super_speed: int = super_speed
        self.initial_pos: tuple[int, int] = initial_pos
        self.pos: tuple[int, int] = initial_pos
        self.direction: Directions = Directions.NONE
        self.is_alive: bool = True

    def respawn(self) -> None:
        """Put the entity back to its initial position."""
        self.pos = self.initial_pos


class Pacman(Entity):
    """Class Pacman, heriting from Entity.
    
    Atributes:
    - speed: int
    - super_speed: int
    - initial_pos: tuple[int, int]
    - pos: tuple[int, int]
    - direction: Directions
    - is_alive: bool
    - next_direction: Directions
    - pacman_super: bool

    Methods:
    - move(self, wall_in_actual_cell: int) -> None
    - update_user_input(self, user_input: str) -> None

    Description:
    """

    def __init__(self, speed: int, super_speed: int,
                 initial_pos: tuple[int, int]):
        """Initialises the attributes of the Pacman instance."""
        super().__init__(speed, super_speed, initial_pos)
        self.next_direction: Directions = Directions.UP
        self.pacman_super: bool = False

    def move(self, walls_in_actual_cell: int) -> None:
        """Manage Pacman movement. If the wall in 'next_direction" is open,
        pacman move in that direction and 'direction' became 'next_direction'.
        If not, pacman move in his initial direction if possible. If not,
        'direction' become None.
        """
        if self.direction != self.next_direction:
            if not (walls_in_actual_cell & (self.next_direction.value)):
                self.direction = self.next_direction
        if walls_in_actual_cell & (self.direction.value):
            self.direction = Directions.NONE
            return
        self.pos = (
            self.pos[0] + Movements[self.direction.name].value[0],
            self.pos[1] + Movements[self.direction.name].value[1])

    def update_user_input(self, user_input: str) -> None:
        """Manage the update of next_direction depending on the user input."""
        if user_input == "up_key":
            self.next_direction = Directions.UP
        elif user_input == "down_key":
            self.next_direction = Directions.DOWN
        elif user_input == "right_key":
            self.next_direction = Directions.RIGHT
        elif user_input == "left_key":
            self.next_direction = Directions.LEFT


class Ghost(Entity):
    """Class Ghost, heriting from Entity.
    
    Atributes:
    - speed: int
    - super_speed: int
    - initial_pos: tuple[int, int]
    - pos: tuple[int, int]
    - is_alive: bool
    - down_time: int
    - chase_radius: int
    - escape_radius: int
    - idle_strat: str
    - chase_strat: str
    - escape_strat: str

    Methods:
    - chase(self, pacman_pos: tuple[int, int]) -> None
    - escape(self, pacman-pos: tuple[int, int]) -> None

    Description:
    """
    def __init__(self, speed: int, super_speed: int,
                 initial_pos: tuple[int, int], down_time: int,
                 chase_radius: int, escape_radius: int, idle_strat: str,
                 chase_strat: str, escape_strat: str,
                 maze: list[list[Cell]]):
        """Initialises the attributes of the Ghost instance."""
        super().__init__(speed, super_speed, initial_pos)
        self.down_time: int = down_time
        self.chase_radius: int = chase_radius
        self.escape_radius: int = escape_radius
        self.idle_strat: Strategy = strat_dict[idle_strat](maze)
        self.chase_strat: Strategy = strat_dict[chase_strat](maze)
        self.escape_strat_strat: Strategy = strat_dict[escape_strat](maze)

    def chase(self, pacman_pos: tuple[int, int]) -> None:
        if calculate_manhattan(self.pos, pacman_pos) <= self.chase_radius:
            self.pos = self.chase_strat.move()
        else:
            self.pos = self.idle_strat.move(self.pos)

    def escape(self, pacman_pos: tuple[int, int]) -> None:
        pass

