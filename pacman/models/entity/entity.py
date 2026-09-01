"""File: /pacman/models/entity/entity.py

Date: 2026-08-04
#### Description:
This module defines the entities and movement-related types used by the
Pacman game.

It provides the common `Entity` base class for all movable characters,
as well as the `Pacman` and `Ghost` classes that implement their specific
behaviours.

The module also defines the movement directions used by entities and the
coordinate offsets associated with each direction.

`Entity` contains the attributes and behaviours shared by Pacman and ghosts,
such as their position, speed, movement direction, life state and respawn
position.

`Pacman` extends `Entity` with player-controlled movement and special-mode
behaviour.

`Ghost` extends `Entity` with strategy-based movement and behaviours such as
chasing or escaping from Pacman. Ghost movement is delegated to strategy
objects defined in the `strategies` module, allowing different pathfinding
and movement behaviours to be implemented independently from the entity.


### Classes:
- Entity(ABC): Base class for all movable game entities.
- Pacman(Entity): Represents the player-controlled Pacman entity.
- Ghost(Entity): Represents a ghost controlled by movement strategies.

### Dependencies:
- strategies: Provides the strategy interface and implementations used by
  ghosts.
- Cell: Represents the cells of the game map used by ghost strategies.
"""
from abc import ABC

from .strategies import Strategy, strat_dict, calculate_manhattan, AlternateAngleStrat, Directions, Movements
from pacman.models import Cell


class Entity(ABC):
    """Class Entity, inheriting from ABC.

    #### Description:
    Base class for all movable game entities.

    An entity represents an object that has a position in the maze and can
    move during the game. Pacman and ghosts inherit from this class.

    The base class provides common attributes and operations shared by
    all entities, such as their position, movement speed, direction and
    respawn position.


    Atributes:
    - speed (int): Normal movement speed of the entity.
    - super_speed (int): Movement speed used when the entity is in a
      special movement mode.
    - initial_pos (tuple[int, int]): Position where the entity is
      initially spawned and where it will respawn.
    - pos (tuple[int, int]): Current position of the entity in the maze.
    - direction (Directions): Current movement direction.
    - is_alive (bool): Whether the entity is currently alive.

    Methods:
    - respaw(): Reset the entity to its initial position.
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
    """Class Pacman, inheriting from Entity.

    #### Description:
    Represent the player-controlled Pacman entity.

    Pacman extends `Entity` with player-specific movement behaviour.
    It stores both its current movement direction and the direction requested
    by the player.

    The requested direction is kept in `next_direction` until the maze
    allows Pacman to move in that direction. This allows the player to
    choose a direction before reaching an intersection.

    Pacman can also enter a special mode after collecting a super gum.
    
    #### Inherited attributes:
    - speed (int): Normal movement speed.
    - super_speed (int): Movement speed used in super mode.
    - initial_pos (tuple[int, int]): Initial spawn position.
    - pos (tuple[int, int]): Current position.
    - direction (Directions): Current movement direction.
    - is_alive (bool): Whether Pacman is alive.

    #### Attributes:
    - next_direction (Directions): Direction requested by the player.
    - pacman_super (bool): Whether Pacman is currently in super mode.

    #### Methods:
    - move(): Move Pacman according to the current and requested directions.
    - update_user_input(): Update the requested direction from player input.
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
        If not, pacman keep and move in his initial direction if possible. If
        not, direction' become None and pacman stop moving.
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
    
    #### Description:
    Represent a ghost entity controlled by a movement strategy.

    A ghost extends `Entity` with behaviour specific to enemy entities.
    Its movement is determined by three strategies corresponding to its
    different behaviours: idle, chase and escape.

    The ghost selects the appropriate strategy according to the current
    game conditions. Strategies are responsible for calculating the next
    position, while the `Ghost` class manages the state and configuration
    required to use them.

    This design allows different ghost behaviours to be implemented and
    combined without modifying the base `Ghost` class.

    #### Inherited attributes:
    - speed (int): Normal movement speed.
    - super_speed (int): Movement speed used in a special mode.
    - initial_pos (tuple[int, int]): Initial spawn position.
    - pos (tuple[int, int]): Current position.
    - direction (Directions): Current movement direction.
    - is_alive (bool): Whether the ghost is alive.

    #### Attributes:
    - down_time (int): Time before the ghost becomes active after dying.
    - chase_radius (int): Maximum Manhattan distance at which the ghost
      starts chasing Pacman.
    - escape_radius (int): Manhattan distance used to determine when the
      ghost should escape from Pacman.
    - idle_strat (Strategy): Strategy used when the ghost is not chasing.
    - chase_strat (Strategy): Strategy used when the ghost is chasing.
    - escape_strat (Strategy): Strategy used when the ghost is escaping.
    - max_stamina (int): number of chasing movements before the ghost
      become 'exhausted' and stop his chasing behavior.
    - current_stamina (int): actual stamina of the ghost.

    #### Methods:
    - chase(): Chase Pacman when he is within the chase radius.
    - escape(): Move away from Pacman according to the escape behaviour.
    """
    def __init__(self, speed: int, super_speed: int,
                 initial_pos: tuple[int, int], down_time: int,
                 chase_radius: int, escape_radius: int, idle_strat: str,
                 chase_strat: str, escape_strat: str, chasing_stamina: int,
                 maze: list[list[Cell]]):
        """Initialises the attributes of the Ghost instance."""
        super().__init__(speed, super_speed, initial_pos)
        self.down_time: int = down_time
        self.chase_radius: int = chase_radius
        self.escape_radius: int = escape_radius
        self.idle_strat: Strategy = strat_dict[idle_strat](maze)
        self.chase_strat: Strategy = strat_dict[chase_strat](maze)
        self.escape_strat: Strategy = strat_dict[escape_strat](maze)
        self.max_stamina: int = chasing_stamina
        self.current_stamina: int = chasing_stamina

    def chase(self, pacman_pos: tuple[int, int]) -> None:
        """Function to move ghost when Pacman is not in Super mode.

        If Pacman is is the chasing radius and ghost max_stamina is equal to 0
        or ghost current_stamina is superior to 0, the movement of ghost use a
        chasing strategy. Each move with chasing strategy reduce the ghost
        current_stamina.

        If not, it use a idling strategy to move.Each move in idling strategy
        augment the ghost current_stamina if it is inferior to max_stamina.
        """
        if (calculate_manhattan(self.pos, pacman_pos) <= self.chase_radius and
            (self.max_stamina == 0 or self.current_stamina > 0)):
            self.pos = self.chase_strat.move()
            self.current_stamina -= 1
        else:
            self.pos = self.idle_strat.move(self.pos)
            if self.current_stamina < self.max_stamina:
                self.current_stamina += 1

    def escape(self, pacman_pos: tuple[int, int]) -> None:
        """Function to move away from Pacman according to the escape
        behaviour.
        """
        pass

