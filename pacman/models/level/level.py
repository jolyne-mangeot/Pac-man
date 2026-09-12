
from enum import IntEnum
from typing import TypedDict, cast

import pygame as pg

from pacman.models import (
    MazeConfig, GameplayConfig, ScoresConfig,
    Entity, Pacman, Ghost,
    Map, Directions, OPPOSITE_DIRECTION, Movements)


ANIM_TICK: int = 15


class Cheats(TypedDict):
    """TypedDict containing all necessary entries to make cheats work:

    - invincibility: bool => makes ghosts unable to eat Pacman
    - infinite_super: bool => the super_mode is always on
    - infinite_time: bool => prevents the level timer from decreasing
    - super_speed: bool => Pacman moves 5 cells every seconds
    - skip_level: bool => wins the level instantly
    - life_gains: int => give the player's x lives back (cannot exceed max)
    """
    invincibility: bool
    infinite_super: bool
    infinite_time: bool
    super_speed: bool
    skip_level: bool
    life_gains: int


class Timers(IntEnum):
    """Integer values used by pygame to set custom events related to timers."""
    LEVEL = pg.USEREVENT + 0
    SUPER = pg.USEREVENT + 1
    ANIMATIONS = pg.USEREVENT + 2


class LevelOutput(TypedDict):
    """TypedDict containing all values to return when the level is complete:

    - victorious: bool => weither the level was won or lost
    - lives: int => the player's remaining lives
    - time_taken: int => the level timer's remaining seconds
    - score: int => the final score of the level
    - scores: dict[str, int] => the detail of the score for each source:
        - "gum"
        - "sup_gum"
        - "ghost"
        - "level": when the level is complete
    """
    victorious: bool
    lives: int
    time_taken: int
    score: int
    scores: dict[str, int]


class Level:
    """Class Level

    #### Description:
    Class implementing the game's logic using multiple configuration objects.
    Moves the characters around, updates the maze and the gums, runs the
    timers for the animations and the level, and let the player progress
    through, passing values up and down with GameState.

    ### Attributes:
    <u>Parameters:</u>
    - level_id: int => index of the level displayed at the top of the screen
    - max_lives: int => reference used to display lives
    - player_lives: int => the current player's lives
    - maze_config: MazeConfig => Config objects containing all set values to
    generate the level
    - gameplay: GameplayConfig
    - scores_config: ScoresConfig
    - cheats: Cheats => TypedDict containing all running cheats that impact the
    game's logic directly.

    <u>Using Config objects</u>:
    - theme: str => theme of the level, only used for the display for now
    - level_duration: int => max duration of the level, used to create a
    countdown
    - super_duration: int => the time during which the super mode lasts
    - scores_ref: ScoresConfig => the scores gained for each possible ways
    - map: Map => Map object instantiated using the maze_config argument
    - pacman: Pacman => Pacman instance created using the config
    - chars: dict[str, Entity] => dict filled with all the ghosts declared
    in the configuration file

    <u>Self-attributes:</u>
    - level_timer: int => remaining time for the level, going down from
    level_duration
    - score: int => the score gained by the player during this level, going
    from 0
    - scores: dict => a dict containing the details of the obtained score for
    each source
    - ghosts: list[str] => list of string for every ghost instantiated
    - char_anim: dict[str, int] => dict of int going from 0 and updated every
    animation tick to track cooldowns for each entity
    - super_anim: int => set to 0, used to check if the super mode is over
    and display the super bar emptying

    ### Methods:
    <u>Entity-instantiating methods:</u>
    - calc_speed (staticmethod) => using an int, calculates a speed in
    milliseconds to return as an int
    - instantiate_pacman => using the maze and gameplay configs, instantiate a
    Pacman object with position, speeds, etc.
    - instantiate_ghosts => same as pacman, instantiating every ghost in the
    GameplayConfig ghosts dict
    <u>Entity-updating methods:</u>
    - move_pacman => calls the Pacman move method and checks if it's stuck in
    a wall to set its animation tick to max, and otherwise 0
    - move_ghost => calls the chase or escape Ghost method based on the current
    mode
    - activate_super => sets to True the is_super attribute to every entity
    - deactivate_super => sets to False the attribute
    - entity_die => sets the is_alive attribute to False to the given Entity
    - entity_respawn => sets the is_alive attribute to True and calls the
    respawn method for the given Entity
    - entity_theoric_pos => for an Entity, calculates if it's moved closer
    to its current cell or its origin, based on animation ticks and speed
    <u>Game-updating methods:</u>
    - update_pacman => checks if Pacman is alive and if it needs updating
    based on its animation ticks
    - update_maze => using Pacman's theoric position, checks if it has stepped
    on a gum or super gum, and gain score accordingly
    - update_entities => checks if the any Entity needs to move or respawn
    based on animation ticks and factors, and checks if Pacman has collided
    with a Ghost
    - update_animations => increments every animation tick tracker if needed
    - update => called every frame by GameState to update the game
    <u>Progression-related methods:</u>
    - gain_score => increments the score and detail score based on the given
    name
    - create_level_output => using the Level's attribute, create a LevelOutput
    object to return
    - get_event => gets the current pygame event and parse it between Timers
    and the user's input
    """
    def __init__(
            self, level_id: int, max_lives: int, player_lives: int,
            maze_config: MazeConfig, gameplay: GameplayConfig,
            scores_config: ScoresConfig, cheats: Cheats) -> None:
        """Recovers all configuration variables to instantiate every needed
        attribute to run correctly, declare others with starting values,
        and calls instantiating methods for every entity. Finally, starts
        the Timers for the level and the animation ticks.
        """
        self.level_id: int = level_id
        self.max_lives: int = max_lives
        self.lives: int = player_lives
        self.theme: str = gameplay.theme
        self.cheats: Cheats = cheats
        self.level_duration: int = gameplay.timer
        self.level_timer: int = gameplay.timer
        self.super_duration: int = gameplay.super_duration * 1000
        self.scores_ref: ScoresConfig = scores_config
        self.score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}
        self.map: Map = Map(**maze_config.model_dump())
        self.map.super_gum_placement()
        self.map.simple_gum_placement()
        self.map.generate_cell_graph()
        self.pacman: Pacman
        self.ghosts: list[str] = []
        self.chars: dict[str, Entity] = {}
        self.char_anim: dict[str, int] = {}
        self.super_anim: int = 0
        self.instantiate_pacman(maze_config, gameplay)
        self.instantiate_ghosts(maze_config, gameplay)
        pg.time.set_timer(Timers.LEVEL.value, 1000)
        pg.time.set_timer(Timers.ANIMATIONS.value, ANIM_TICK)

    # _________________________________________________________________________
    #                       ENTITY-INSTANTIATING METHODS
    # _________________________________________________________________________

    @staticmethod
    def calc_speed(speed: int) -> int:
        """Using a speed from 1 to 20, substract it times 100 from 2000,
        meaning the slowest speed is a movement every 2 seconds, and the
        fastest being instant movement.

        Returns the result
        """
        if speed > 0:
            return 2000 - speed * 100
        return speed

    def instantiate_pacman(self, maze: MazeConfig,
                           config: GameplayConfig) -> None:
        """Instantiate the pacman attribute using the maze's config for an
        initial position and the gameplay config for speeds.

        The Entity is then appended to the chars list and char_anim with its
        current speed.
        """
        self.pacman = Pacman(
            config.pac_man_speed, config.super_pac_man_speed,
            ((maze.width - 1) // 2, (maze.height - 1) // 2))
        self.pacman.speed = self.calc_speed(self.pacman.speed)
        self.pacman.super_speed = self.calc_speed(self.pacman.super_speed)
        self.pacman.current_speed = self.pacman.speed
        self.chars.update({"Pacman": self.pacman})
        self.char_anim.update({"Pacman": self.pacman.current_speed})

    def instantiate_ghosts(self, maze: MazeConfig,
                           config: GameplayConfig) -> None:
        """For each ghost in the gameplay config, instantiate it with an
        initial position based on the maze's angles and its connected values
        from the config. Appends the newly created Ghost to the chars list,
        and its name to the ghosts list and char_anim.
        """
        positions: dict[str, tuple[int, int]] = {
            "Blinky": (0, 0),
            "Pinky": (maze.width - 1, 0),
            "Inky": (0, maze.height - 1),
            "Clyde": (maze.width - 1, maze.height - 1)}
        for name, pos in positions.items():
            if config.ghosts.get(name, None) is not None:
                new_ghost: Ghost = Ghost(
                    **config.ghosts[name].model_dump(),
                    initial_pos=pos, maze=self.map)
                new_ghost.speed = self.calc_speed(new_ghost.speed)
                new_ghost.super_speed = self.calc_speed(new_ghost.super_speed)
                new_ghost.down_time *= 1000
                new_ghost.current_speed = new_ghost.speed
                self.ghosts.append(name)
                self.chars.update({name: new_ghost})
                self.char_anim.update({name: new_ghost.current_speed})

    # _________________________________________________________________________
    #                          ENTITY-UPDATING METHODS
    # _________________________________________________________________________

    def move_pacman(self) -> None:
        """Calls the pacman move methods with the walls of the cells it's in.
        If Pacman has a dummy direction (Directions.NONE), it's char_anim
        entry is set to its current_speed, otherwise it is set to 0.
        """
        self.pacman.move(self.map.get_cell(self.pacman.pos).walls)
        if self.pacman.direction.value == 15:
            self.char_anim["Pacman"] = self.pacman.current_speed
        else:
            self.char_anim["Pacman"] = 0

    def move_ghost(self, name: str) -> None:
        """For a given name, calls the right Ghost's chase or escape method
        based on the current mode. Resets its char_anim entry to 0.
        """
        ghost: Ghost = cast(Ghost, self.chars[name])
        if ghost.is_super is True:
            ghost.escape(self.pacman.pos)
        else:
            ghost.chase(self.pacman.pos)
        self.char_anim[name] = 0

    def activate_super(self) -> None:
        """Sets the char_anim to the super duration for a countdown, and
        activates the is_super attribute of all entities if it's alive.
        """
        self.super_anim = self.super_duration
        for char in self.chars.values():
            if char.is_alive is True:
                char.is_super = True
                char.current_speed = char.super_speed
        pg.time.set_timer(Timers.SUPER.value, self.super_duration, 1)

    def deactivate_super(self) -> None:
        """Sets super_anim to 0 and, for all entities, sets their is_super
        attribute to False and resets their current speed to their normal
        speed.
        """
        self.super_anim = 0
        for char in self.chars.values():
            char.is_super = False
            char.current_speed = char.speed

    def entity_die(self, name: str) -> None:
        """Sets the anim_char for the given entity name to 0 and its is_alive
        attribute to False.
        """
        self.char_anim[name] = 0
        self.chars[name].is_alive = False

    def entity_respawn(self, name: str) -> None:
        """For a given name, sets the is_alive attribute to True and resets its
        direction, speed and is_super flag if the infinite_super cheat isn't
        running. Calls its respawn method.
        """
        char: Entity = self.chars[name]
        char.is_alive = True
        char.direction = Directions.NONE
        if self.cheats["infinite_super"] is False:
            char.current_speed = char.speed
            char.is_super = False
        else:
            char.current_speed = char.super_speed
        self.char_anim[name] = 0
        char.respawn()

    def entity_theoric_pos(self, name: str) -> tuple[int, int]:
        """Based on the char_anim of the given name, calculates if the entity
        is closer to its destination or origin cell for more fluid updates.
        Returns the closest cell's coordinates.
        """
        entity: Entity = self.chars[name]
        theoric_pos: tuple[int, int] = entity.pos
        if (entity.direction.value != 15
                and self.char_anim[name] < entity.current_speed // 2.2):
            opposite_move: tuple[int, int] = (
                Movements[OPPOSITE_DIRECTION[entity.direction].name].value)
            theoric_pos = (theoric_pos[0] + opposite_move[0],
                           theoric_pos[1] + opposite_move[1])
        return theoric_pos

    # _________________________________________________________________________
    #                           GAME-UPDATING METHODS
    # _________________________________________________________________________

    def update_pacman(self) -> None:
        """For different factors, updates Pacman's attributes and calls its
        move method if necessary. Otherwise, if Pacman is dead and its
        char_anim is above 2000, respawns all entities.
        """
        if self.pacman.is_alive is True:
            speed_ref: int = (self.pacman.current_speed
                              if self.cheats["super_speed"] is False else 200)
            if self.char_anim["Pacman"] >= speed_ref:
                self.move_pacman()
        elif self.char_anim["Pacman"] >= 2000:
            self.lives -= 1
            self.pacman.next_direction = Directions.NONE
            for name in self.chars.keys():
                self.entity_respawn(name)

    def update_entities(self) -> None:
        """Calls update_pacman and update_maze if its alive. Then, for every
        ghost, checks if it needs to move, if it's colliding with pacman,
        in which case one of the two dies, or if it needs to respawn.
        """
        self.update_pacman()

        pac_pos: tuple[int, int] = self.entity_theoric_pos("Pacman")
        if self.pacman.is_alive is True:
            self.update_maze(pac_pos)

        for name in self.ghosts:
            ghost: Ghost = cast(Ghost, self.chars[name])
            if ghost.is_alive is True:
                if self.char_anim[name] >= ghost.current_speed:
                    self.move_ghost(name)
            elif self.char_anim[name] >= ghost.down_time:
                self.entity_respawn(name)
            if self.pacman.is_alive is True and ghost.is_alive is True:
                ghost_pos: tuple[int, int] = self.entity_theoric_pos(name)
                if ghost_pos == pac_pos:
                    if ghost.is_super is True:
                        self.gain_score("ghost")
                        self.entity_die(name)
                    elif self.cheats["invincibility"] is False:
                        self.entity_die("Pacman")

    def update_maze(self, pacman_pos: tuple[int, int]) -> None:
        """For the given pacman position, checks if it's running into gums
        or super gums, and gaining the according score, as well as
        activating the super mode.
        """
        output: str = self.map.update_gum(pacman_pos)
        if output == "simple_gum":
            self.gain_score("gum")
        elif output == "super_gum":
            self.gain_score("sup_gum")
            self.activate_super()

    def update_animations(self) -> None:
        """Increments all animations ticks in char_anim, and decrements the
        super_anim.
        """
        if self.pacman.is_super is True:
            if self.cheats["infinite_super"] is False:
                self.super_anim -= ANIM_TICK
            if self.super_anim < 0:
                self.deactivate_super()
                self.super_anim = 0
        for name in self.chars.keys():
            self.char_anim[name] += ANIM_TICK

    def update(self) -> None | LevelOutput:
        """Called by GameState. Calls update_entities, and checks for winning
        and losing conditions, before returning either None or a LevelOutput
        object with the create_level_output method.
        """
        self.update_entities()
        if self.map.check_gum() is True:
            return self.create_level_output(True)
        if self.level_timer == 0 or self.lives == 0:
            return self.create_level_output(False)
        return None

    # _________________________________________________________________________
    #                        PROGRESSION-RELATED METHODS
    # _________________________________________________________________________

    def gain_score(self, type: str) -> None:
        """For a type as string, appends the total and detail scores with the
        correct amount based on the score_ref.
        """
        amount: int = getattr(self.scores_ref, type)
        self.score += amount
        self.scores[type] += amount

    def create_level_output(self, victorious: bool) -> LevelOutput:
        """When called, if victorious is True, gains the level score and
        returns a LevelOutput object with the updated values.
        """
        if victorious is True:
            self.gain_score("level")
        return {"victorious": victorious, "lives": self.lives,
                "time_taken": self.level_duration - self.level_timer,
                "score": self.score, "scores": self.scores}

    def get_event(self, event: pg.event.Event, action_key: str) -> None:
        """Gets a pygame.Event object and parse it with Timers, and an action
        key string to pass down to pacman using its dedicated method.
        """
        if event.type == pg.KEYDOWN:
            self.pacman.update_user_input(action_key)
            if self.pacman.direction.value == 15:
                self.move_pacman()
        elif (event.type == Timers.LEVEL.value
                and self.cheats["infinite_time"] is False):
            self.level_timer -= 1
        elif event.type == Timers.ANIMATIONS.value:
            self.update_animations()
