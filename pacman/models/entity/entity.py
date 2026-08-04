"""File: /pacman/models/entity/entity.py

Date: 2026-08-04
#### Description:

#### Classes:

#### Enums:

#### Errors raised:

"""

from abc import ABC, abstractmethod
from enum import IntEnum


class Direction(IntEnum):
    """class Direction.
    Enum for left(O), down(1), right(2), up(3)
    """
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3
    NONE = 4
 

class Entity(ABC):
    """Class Entity/

    Atributes: position, initial_position, direction, next_direction, speed,
    alive, can_move.
    
    Methods: move(), update(), die(), respawn(), change_direction().
    
    Description:
    """

    def __init__(self, position: tuple[int, int], initial_position:
                 tuple[int, int], direction: Direction, next_direction:
                 Direction, speed: int, alive: bool, can_moove: bool):
        """Initialises the attributes of the Entity instance."""
        self.position: tuple[int, int] = initial_position
        self.initial_position: tuple[int, int] = initial_position
        self.direction: Direction = None
        self.next_direction: Direction = None
        self.alive: bool = True
        self.can_moove: bool = True

    @abstractmethod
    def move():
        """"""

    @abstractmethod
    def respawn():
        """"""

    def update_position():
        """"""

    def teleport():
        """"""

    def change_direction():
        """"""

class Pacman(Entity):
    """Class Pacman, heriting from Entity.
    
    Atributes:

    Methods:

    Description:
    """

    def __init__(self, position: tuple[int, int], initial_position:
                 tuple[int, int], direction: Direction, next_direction:
                 Direction, speed: int, alive: bool, can_moove: bool,
                 lives: int, super_mod: bool, invicible: bool):
            """Initialises the attributes of the Entity instance."""
            super().__init__(position, initial_position, direction,
                             next_direction, speed, alive, can_moove)
            self.lives: int = 3
            self.super_mode: bool = False
            self.invicible: bool = False

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
                self.strategy: GhostStrategy = 
                self.state: GhostState = 
                self.target: tuple[int, int] = 
                self.escape_speed: int = 
    
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
