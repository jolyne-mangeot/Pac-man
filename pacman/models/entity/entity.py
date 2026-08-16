"""File: /pacman/models/entity/entity.py

Date: 2026-08-04
#### Description: This module manages entity(Pacman and ghosts) for the
pacman game.

#### Classes:
- Entity(ABC)
- Pacman(Entity)
- Ghost(Entity)

#### Enums:

#### Errors raised:

"""

from abc import ABC, abstractmethod
from enum import IntEnum


class Direction(IntEnum):
    """Class Direction (IntEnum)
    - NONE = O
    - UP = 1
    - RIGHT = 2
    - DOWN = 4
    - LEFT = 8
    """
    NONE = 0
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8
 

class Entity(ABC):
    """Class Entity

    Atributes:
    - speed: int
    - super_speed: int
    - initial_position: tuple[int, int]
    - position: tuple[int, int]
    - direction: Direction
    - is_alive: bool
    - pacman_super: bool

    Methods:
    - respaw(self) -> None

    Description:
    """

    def __init__(self, speed: int, super_speed: int, initial_pos: tuple[int, int]):
        """Initialises the attributes of the Entity instance."""
        self.speed: int = speed
        self.super_speed: int = super_speed
        self.initial_position: tuple[int, int] = initial_pos
        self.position: tuple[int, int] = initial_pos
        self.direction: Direction = Direction.NONE
        self.is_alive: bool = True
        self.pacman_super: bool = False

    def respawn(self) -> None:
        """Put the entity back to its initial position."""
        self.position = self.initial_position


class Pacman(Entity):
    """Class Pacman, heriting from Entity.
    
    Atributes:
    - speed: int
    - super_speed: int
    - initial_position: tuple[int, int]
    - position: tuple[int, int]
    - direction: Direction
    - is_alive: bool
    - pacman_super: bool
    - next_direction: Direction

    Methods:
    - move(self) -> None

    Description:
    """

    def __init__(self, speed: int, super_speed: int,
                 initial_pos: tuple[int, int]):
            """Initialises the attributes of the Entity instance."""
            super().__init__(speed, super_speed, initial_pos)
            self.next_direction: Direction = Direction.NONE

    def move():
         """"""

    def eat_pacgum():
        """"""

    def eat_super_pacgum():
        """"""

    def fight_ghost():
        """"""

    def lose_life():
        """"""

    def activate_super_mode():
        """"""

    def deactivate_super_mode():
        """"""

    def get_user_input():
        """"""

    def respawn():
        """"""


class Ghost(Entity):
    """Class Ghost, heriting from Entity.
    
    Atributes:

    Methods:

    Description:
    """
    def __init__(self, position: tuple[int, int], initial_position:
                     tuple[int, int], direction: Direction, next_direction:
                     Direction, speed: int, alive: bool, can_moove: bool,
                     strategy: GhostStrategy, state: GhostState, appearance:
                     str, target: tuple[int, int], escape_speed: int):
                """Initialises the attributes of the Entity instance."""
                super().__init__(position, initial_position, direction,
                                 next_direction, speed, alive, can_moove)

    
    def move():
         """"""

    def respawn():
         """"""

    def set_strategy():
         """"""

    def set_state():
         """"""

    def update_target():
         """"""
