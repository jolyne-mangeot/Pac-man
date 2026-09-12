
from functools import partial

import pygame as pg

from pacman.controllers import Control, State, Menu
from pacman.models import (
    LevelConfig, Level, LevelOutput, Cheats, Highscores, Score,
    ActivateOption, Spacer, TextHolder, TextValueHolder, InputOption,
    ToggleOption, SliderOption)
from pacman.views import GameDisplay


CHEAT_CODE: tuple[str, ...] = (
    "up_key", "up_key", "down_key", "down_key", "left_key", "right_key",
    "left_key", "right_key", "confirm_key", "return_key")


class Player:
    """Class Player

    #### Description:
    Holds all updated informations about the player and their progression.
    Used to display variables in menues, but also conditions such as the cheats
    checker. Also contains various methods related to updating said values.

    ### Attributes:
    <u>Parameters:</u>
    - player_name: str => passed as parameter as the name is also held by the
    GameState class to save it between game runs
    - max_lives: int => passed down from the configuration file
    - cheats_allowed: bool => also passed down from the configuration file

    <u>Self attributed:</u>
    - cheats_used: bool => set to False, updated if any cheat is used at any
    time during a level
    - lives: int => set to the max_lives parameter, updated using dedicated
    method
    - playtime: int => time in seconds passed down in all levels
    - current_score: int => total score for every level
    - scores: dict[str, int] => detail of the total score between gums,
    super gums, eating ghosts and passing levels

    ### Methods:
    - regen_life => add the lives argument to the Player's attribute, holding
    it under the max_lives
    - update_with_output => using a LevelOutput dict, update lives, playtime
    and all scores
    """
    def __init__(self, player_name: str, max_lives: int, cheats_allowed: bool
                 ) -> None:
        """Instantiate a Player object using values from the configuration
        file and the GameState. Assigns default values to all other declared
        attributes.
        """
        self.player_name: str = player_name
        self.max_lives: int = max_lives
        self.cheats_allowed: bool = cheats_allowed
        self.cheats_used: bool = False
        self.lives: int = max_lives
        self.playtime: int = 0
        self.current_score: int = 0
        self.scores: dict[str, int] = {
            "gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}

    def regen_life(self, life_regen: int) -> None:
        """Appends the life_regen argument to the lives attribute of the
        instance, resetting it to the max_lives attribute if it surpasses it.
        """
        self.lives += life_regen
        if self.lives > self.max_lives:
            self.lives = self.max_lives

    def update_with_output(self, output: LevelOutput) -> None:
        """Update the Player's attribute using a LevelOutput TypedDict, namely
        lives as it comes, and appending playtime, current_score and all
        score details in the score dict with the newest values.
        """
        self.lives = output["lives"]
        self.playtime += output["time_taken"]
        self.current_score += output["score"]
        for key, value in output["scores"].items():
            self.scores[key] += value


class GameState(State):
    """Class GameState, subclass of State

    Handles everything game-related, from the level creation and running to
    the pause and cheats menues, the end of levels when its output is
    displayed, and the end of runs, where players can save their final score.

    Apart from menues, this class uses the Level class to run the game, calling
    its get_event and update methods, before displaying informations using the
    GameDisplay class.

    ### Attributes:
    - *State instance parameters and attributes*
    - display: GameDisplay => displays the level or the current Menu using
    various methods, and is kept updated with latest variables
    - current_state: str => name of the current state of the game, from "level"
    to all different menues names, used to update and display correctly
    - menues: dict[str, Menu] => dict containing the different menues
    accessible during a game run
    - level_reached: int => index used to browse the level list from the config
    - player_name: str => name of the player, set to "Player" then kept between
    game runs with the one entered by the user
    - player: Player => Player object instantiated every game run
    - current_level: Level => latest Level object to run the game with, renewed
    every time a new level is reached
    - cheats: Cheats => TypedDict containing booleans and an int to apply the
    correct cheats, shared with current_level
    - cheats_save: Cheats => Copy of cheats to revert all changes in case of
    return_key being pressed to leave the cheats menu
    - cheat_code_index: int => Int used as reference to check if the player
    is inputting the cheat code
    - current_output: LevelOutput => LevelOutput updated everytime a level ends

    ### Methods
    - *State instance methods*
    - init_menues => initializes the menues dict with Menu objects, giving
    them all needed containers to work correctly
    <u>Game state-related methods:</u>
    - startup => method called once everytime this class is brought up by
    Control
    - cleanup => method called by Control when this class is let down, only
    cleans up the display elements of GameState
    - leave_game => method called by GameState when the level is left
    voluntarily by the user, cleans up all attributes that will be reset later
    - change_game_state => changes the game's state, and if it's a menu, calls
    the change_menu GameDisplay method
    <u>Level progression methods:</u>
    - update_output => updates the current_output attribute with the one
    returned by Level, making sure the reference is kept with the display
    - skip_level => calls the Level's output creating method prior to its
    normal end and move on to the victory menu
    - access_next_level => called in the victory and defeat menues by the user,
    moves onto the next level or the end menu when right
    - instantiate_level => creates a new instance of Level and makes all
    necessary updates accordingly
    - access_run_end => accesses the end menu, updating the buttons if cheats
    were used
    <u>Menues-related methods:</u>
    - apply_cheats => runs through every value of the cheats attributes and
    makes the ponctual changes if needed
    - save_score => modifies the highscore Control attribute and saves it
    using the right Control method
    - get_event => recovers the current pygame event to parse it towards
    level or the current menu
    - update => called after all events have been parsed, checks if the
    Level returns an output
    """
    def __init__(self, control: Control) -> None:
        """Instantiate the GameState object at the start of the program.
        Initializes the GameDisplay instance and declare all attributes that
        will be used later when this class is accessed.
        """
        State.__init__(self, control)
        self.next = "main_menu"
        self.display: GameDisplay = GameDisplay(control)
        self.current_state: str = "level"
        self.menues: dict[str, Menu]

        self.level_reached: int = -1
        self.player_name: str = "Player"
        self.player: Player
        self.current_level: Level
        self.cheats: Cheats
        self.cheats_save: Cheats
        self.cheat_code_index: int = 0
        self.current_output: LevelOutput = {
            "victorious": True, "lives": 0, "time_taken": 0, "score": 0,
            "scores": {"gum": 0, "sup_gum": 0, "ghost": 0, "level": 0}}

    def __init_menues__(self) -> None:
        """Instantiate the pause, cheats, level_end and end_screen menues,
        used in different conditions to make the user able to progress
        through the levels. Uses preset values and objects like the Player
        and Cheats to share variables by reference.

        Place all menues in the menues dict attribute.
        """
        pause_menu = Menu(loop_cursor=False, options=[
            TextHolder("paused", static_style="picked"), Spacer(), Spacer(),
            ActivateOption("resume", partial(self.change_game_state, "level")),
            ActivateOption("settings",
                           partial(self.switch_state, "options_menu")),
            Spacer(), ActivateOption("give_up", partial(self.leave_game))])

        cheats_menu = Menu(loop_cursor=False, options=[
            TextHolder("cheats_menu", static_style="picked"), Spacer(),
            ToggleOption("invincibility", self.cheats),
            ToggleOption("infinite_super", self.cheats),
            ToggleOption("infinite_time", self.cheats),
            ToggleOption("super_speed", self.cheats),
            SliderOption("life_gains", self.cheats,
                         range(0, self.player.max_lives), 0, 0, cycle=False),
            ToggleOption("skip_level", self.cheats),
            Spacer(), ActivateOption("apply", partial(self.apply_cheats))])

        level_end_menu = Menu(loop_cursor=False, options=[
            TextHolder("level_win", static_style="picked"),
            TextValueHolder("time_taken", self.current_output),
            *[TextValueHolder(name, self.current_output["scores"])
              for name in self.current_output["scores"].keys()], Spacer(),
            TextValueHolder("score", self.current_output),
            TextValueHolder("current_score", self.player), Spacer(),
            ActivateOption("continue_next", partial(self.access_next_level))])

        end_screen = Menu(loop_cursor=False, options=[
            TextHolder("run_end", static_style="picked"),
            TextValueHolder("level_reached", self),
            TextValueHolder("playtime", self.player),
            *[TextValueHolder(name, self.player.scores)
              for name in self.player.scores.keys()], Spacer(),
            TextValueHolder("current_score", self.player),
            InputOption("player_name", self.player, 10,
                        char_checker=lambda s: s.isalnum()),
            ActivateOption("save_score", partial(self.save_score)),
            ActivateOption("end_run", partial(self.leave_game))])

        self.menues = {"pause": pause_menu, "cheats": cheats_menu,
                       "victory": level_end_menu, "defeat": level_end_menu,
                       "end": end_screen}

    # _________________________________________________________________________
    #                        GAME STATE-RELATED METHODS
    # _________________________________________________________________________

    def startup(self) -> None:
        """Called once by Control when this class is accessed. If level_reached
        is -1, instantiate a new Player and calls instantiate_level to start
        a new game. Otherwise, only updates the display in case changes were
        made in the options menu.
        """
        if self.level_reached == -1:
            self.level_reached = 0
            self.player = Player(
                self.player_name, self.control.config.player.lives_count,
                self.control.config.player.cheats_allowed)
            self.cheats = {
                "invincibility": False, "infinite_super": False,
                "infinite_time": False, "super_speed": False,
                "skip_level": False, "life_gains": 0}
            self.cheats_save = self.cheats.copy()
            self.__init_menues__()
            self.display.startup(self.menues)
            self.instantiate_level()
        else:
            self.display.startup(self.menues)
            self.display.update_level(self.current_level)

    def cleanup(self) -> None:
        """Cleans up the State when it's switched for another. Calls the
        cleanup method of Display only in case the options menu is accessed,
        not to delete the current level entirely.
        """
        self.display.cleanup()

    def leave_game(self) -> None:
        """Cleans up all level-related attributes for them to be reinitialized
        when the GameState is accessed again. It puts the level_reached to -1
        for this matter.
        """
        self.level_reached = -1
        del self.menues
        del self.player
        del self.current_level
        self.switch_state("main_menu")

    def change_game_state(self, state: str) -> None:
        """Updates the current state of the game with the one given in
        argument. If it's a menu, resets its cursor and calls the change_menu
        method of display for correct updating.
        """
        self.current_state = state
        if state in self.menues.keys():
            self.menues[state].reset_cursor()
            self.display.change_menu(self.current_state)

    # _________________________________________________________________________
    #                       LEVELS PROGRESSION METHODS
    # _________________________________________________________________________

    def update_output(self, level_output: LevelOutput) -> None:
        """Updates the GameState instance current_output with the one
        returned by the Level. Updates each entry one by one to keep
        references, especially for the scores dict, so the right values are
        displayed by the level_end_menu.
        """
        self.current_output["victorious"] = level_output["victorious"]
        self.current_output["lives"] = level_output["lives"]
        self.current_output["time_taken"] = level_output["time_taken"]
        self.current_output["score"] = level_output["score"]
        self.current_output["scores"].update(level_output["scores"])

    def skip_level(self) -> None:
        """Calls the Level's skip_level method to recover an early output for
        the level. Updates the GameState with it, and switch its state to
        "victory".
        """
        self.update_output(self.current_level.create_level_output(True))
        self.player.update_with_output(self.current_output)
        self.change_game_state("victory")

    def access_next_level(self) -> None:
        """Called by the user in the level_end menues. Increments the
        level_reached attribute and, in case of a "victory" state, checks if
        the last level was won to move on to the "end" state, as when the
        state isn't victory, and otherwise instantiate a new level using the
        dedicated method.
        """
        self.level_reached += 1
        if (self.current_state == "victory"
                and self.level_reached < len(self.control.config.levels)):
            self.instantiate_level()
        else:
            self.access_run_end()

    def instantiate_level(self) -> None:
        """Regens the Player's life using its method and the life_regen
        attribute of the current level before instantiating a new Level
        object using the config. When done, pass it down to the display,
        apply cheats if some were active before, and change the game state.
        """
        level: LevelConfig = self.control.config.levels[self.level_reached]
        self.player.regen_life(level.gameplay.life_regen)
        self.current_level = Level(
            self.level_reached + 1, self.player.max_lives, self.player.lives,
            level.maze, level.gameplay, level.scores, self.cheats)
        self.display.update_level(self.current_level)
        self.apply_cheats()
        self.change_game_state("level")

    def access_run_end(self) -> None:
        """Change the game state to "end". If cheats were used, change the
        save score button to a TextHolder stating so.
        """
        if self.player.cheats_used is True:
            self.menues["end"].options[10] = TextHolder("cheats_used")
        self.change_game_state("end")

    # _________________________________________________________________________
    #                           MENUES-RELATED METHODS
    # _________________________________________________________________________

    def apply_cheats(self) -> None:
        """Updates the cheats_used attribute if any are active, then apply
        some that are ponctual:
        - Regenerates the player's life with the relevant value;
        - if infinite_super is True, calls the Level's activate_super method;
        - if skip_level is true, calls the skip_level method;
        otherwise, change the game state to "level".
        """
        if self.player.cheats_used is False:
            self.player.cheats_used = any(self.cheats.values())
        self.player.lives = self.current_level.lives
        self.player.regen_life(self.cheats["life_gains"])
        self.current_level.lives = self.player.lives
        if self.cheats["infinite_super"] is True:
            self.current_level.activate_super()
        if self.cheats["skip_level"] is True:
            self.skip_level()
            self.cheats["skip_level"] = False
        else:
            self.change_game_state("level")

    def save_score(self) -> None:
        """Updates the Control highscores object with a new one, using the
        currently existing list and appending it with a new Score object
        made of the current player's statistics.

        Calls Control's update_highscores method. If it returns True, change
        the save score button to a success text, otherwise add a TextHolder
        with an error message to the menu.
        """
        self.control.highscores = Highscores(
            scores=self.control.highscores.scores + [Score(
                player=self.player.player_name,
                score=self.player.current_score,
                level_reached=self.level_reached,
                time_taken=self.player.playtime,
                remaining_lives=self.player.lives)])
        if self.control.update_highscores() is True:
            self.menues["end"].options[10] = TextHolder("score_saved")
            self.menues["end"].select_index = 11
            self.display.update_menu(self.current_state, 10)
        else:
            if len(self.menues["end"].options) < 13:
                self.menues["end"].options.append(TextHolder("error_occured"))
                self.display.update_menu(self.current_state, 12)

    # _________________________________________________________________________
    #                           EVENTS-RELATED METHODS
    # _________________________________________________________________________

    def get_event(self, event: pg.event.Event) -> None:
        """Method to parse all pygame events.
        Recover input variables using the dedicated State method, and use
        them to check if the pause or cheats menues were accessed, and
        otherwise pass the events down to the Level or the correct menu.
        """
        inputs: tuple[str, str, str] = self.read_input_events(event)
        if self.current_state == "level":
            if inputs[1] != "":
                if inputs[1] == CHEAT_CODE[self.cheat_code_index]:
                    self.cheat_code_index += 1
                else:
                    self.cheat_code_index = 0
            if inputs[1] == "return_key":
                if self.cheat_code_index == 10:
                    self.change_game_state("cheats")
                    self.cheats_save.update(self.cheats)
                    self.cheat_code_index = 0
                else:
                    self.change_game_state("pause")
            else:
                self.current_level.get_event(event, inputs[1])
        elif self.current_state == "pause":
            if inputs[1] == "return_key":
                self.change_game_state("level")
        elif self.current_state == "cheats":
            if inputs[1] == "return_key":
                self.cheats.update(self.cheats_save)
                self.change_game_state("level")
        if self.current_state in self.menues.keys():
            self.menues[self.current_state].get_event(*inputs, "vertical")

    def update(self) -> None:
        """Calls the Level's update method to check if the level has ended.
        If so, updates the current_output with the one returned and access
        the right game state ("victory" or "defeat"). Calls then the display's
        draw method.
        """
        if self.current_state == "level":
            level_output: LevelOutput | None = self.current_level.update()
            if level_output is not None:
                self.update_output(level_output)
                self.player.update_with_output(self.current_output)
                if level_output["victorious"] is False:
                    self.menues["defeat"].options[0].static_style = "select"
                    self.menues["defeat"].options[0].name = "level_fail"
                self.change_game_state(
                    "victory" if level_output["victorious"] else "defeat")
        else:
            self.display.menu_mixer([self.menues[self.current_state]])
        self.display.draw(self.current_state)
