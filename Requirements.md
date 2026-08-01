---

kanban-plugin: board

---

## README

- [ ] ** **Description** **
- [ ] - Gameplay description with game loop and levels content
- [ ] * Highscore with how scores are saved and why
- [ ] - Visual identity and Pygame implementation
- [ ] - Implementation with libraries used, assets origins, classes to link the 2 together, etc. (technicalities)
- [ ] ** **Instructions** **
- [ ] - Installation with ways of playing the game, from the package or the repo, which files to keep next to the executable, different OS support, etc.
- [ ] - Controls with keys to play and keyboard / mouse / controller support or not
- [ ] - Available settings and their effects
- [ ] * Configuration with structure and default values
- [ ] - Maze Generation with how the package is used with configuration
- [ ] ** **Resources** **
- [ ] - General Software Architecture (class UML, MVC structure, data progression through modules (parsing then initializing then looping on characters, etc.))
- [ ] - Project Management with planning, work distribution and link to this conception branch with illustrated README (details on how to open with obsidian)


## Menues

- [ ] ** **Navigation** **
- [ ] Arrows
- [ ] Mouse ?
- [ ] Pygame menu ?
- [ ] ** **Main menu** **
- [ ] Start game
- [ ] Instructions
- [ ] View highscores
- [ ] Setting (?)
- [ ] Exit
- [ ] ** **Pause Menu** **
- [ ] Resume game
- [ ] Return to main menu
- [ ] ** **Game over Menu** **
- [ ] Display final score
- [ ] Name field for highscore saving
- [ ] ** **Victory Screen** **
- [ ] Display final score
- [ ] Name field for highscore saving
- [ ] BOTH return to the main menu


## Config file

- [ ] ** **JSON** **
- [ ] Default configuration in code: any missing or incorrect key must fall back to failsafe
- [ ] Unknown keys must be ignored
- [ ] MUST support comments for lines starting with a # and //
- [ ] [Snippet](https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments)
- [ ] ** **Config** **
	all in root dictionary
- [ ] ** **Player** **
	key: `player`
- [ ] `life_amount` int > 0
- [ ] ** **Levels** **
	key: `level_#` (ID)
- [ ] Configuration for each level
- [ ] `Maze`:
	- `width` int > 3
	- `height` int > 3
	- `seed` int (default value on level 1, random if non existent on others)
- [ ] `Gameplay`:
	- `timer` int > 0
	- `life_regen` int >= 0 ? (life regained on level start)
	- `super_duration` int >= 0
	- `ghost_downtime` int >= 0
	- `pac_man_speed` int >= 0
	- `sup_pac_man_speed` int >= 0
	- `Ghosts`: (for each)
		- `move_strat` str
		- `sup_move_start` str
		- `speed` int >= 0
		- `sup_speed` int >= 0
		- `downtime` int >= 0
- [ ] `Scores`:
	- `gum` int >= 0
	- `supgum` int >= 0
	- `ghost` int >= 0
	- `level` int >= 0 ? (on level complete)


## Maze

- [ ] Snippet [for make install our own A_maze_ing](https://stackoverflow.com/questions/600079/how-do-i-clone-a-subdirectory-only-of-a-git-repository/28039894#28039894)
- [ ] Perfect set to False
- [ ] Handle generation errors


## Levels

- [ ] ** **Interface** **
- [ ] Current score
- [ ] Current lives
- [ ] Current level
- [ ] Current timer
- [ ] ** **Level** **
- [ ] Consist of a Maze displayed on the game surface
- [ ] Pacgum on each Cell except corners, pattern cells and center Cell
- [ ] Super Pacgum on each corner
- [ ] Pac-man spawns on the center cell
- [ ] Each ghost spawns on a corner
- [ ] ** **Loop** **
- [ ] Timer runs
- [ ] Ghosts move autonomously
- [ ] Player moves Pac-man
- [ ] Pacgum disappears when Pac-man passes upon them
- [ ] Enters super mode when Pac-man picks a Super pacgum
- [ ] ** **Winning Conditions** **
- [ ] Collecting every Pacgum and Super pacgum
- [ ] ** **Losing Conditions** **
- [ ] Losing every life
- [ ] Timer depletes


## Super mode

- [ ] ** **Super mode** **
- [ ] When picking up a Super pacgum, enter Super mode
- [ ] Lasts couples of seconds
- [ ] Pac-man can eat ghost by touching them
- [ ] Ghosts run away from Pac-man
- [ ] Timer slows ?


## Player

- [ ] Attributes:
- [ ] `current_score` int >= 0
- [ ] `current_lives` int >= 0
- [ ] `cheated` bool False
- [ ] `name` str <= 10 (letters and spaces)


## Pac-man

- [ ] Movement takes player's input
- [ ] Use Move object to move between cells


## Movement

- [ ] ** **Movement** **
- [ ] Movement on a grid in 4 directions
- [ ] Depends on the Maze walls
- [ ] Depends on a speed while between two cells
- [ ] ** **Move** **
	class
- [ ] `move_up`
- [ ] `move_down`
- [ ] `move_left`
- [ ] `move_right`
- [ ] ** **Pathfinding** **
	abstract class
- [ ] Move object as parameter
- [ ] `find_path(self, Character)` for different methods


## Ghosts

- [ ] Move towards the player
- [ ] ** **Super mode** **
- [ ] Change visual
- [ ] Path finding switch to running away from pacman
- [ ] When touched by Pac-man, deactivates and returns to its starting position (in normal mode ?)
- [ ] ** **Parameters** **
- [ ] `move_statregy` (pathfinding startegy in normal mode)
- [ ] `run_away_strategy` (pathfinding strategy in super mode)


## Pacgums

- [ ] Cell attribute added as a boolean ?
- [ ] Set of coordinates ?


## Highscores

- [ ] ** **Scores** **
- [ ] Non-negative integer (custom type ?)
- [ ] +X score when picking pacgum
- [ ] +Y score when picking super pacgum
- [ ] +Z score when eating a ghost
- [ ] +A score for remaining time ?
- [ ] +B score for level completion ?
- [ ] ** **Highscores** **
- [ ] Saved in json file
- [ ] Saved when winning or losing levels
- [ ] Overload notification if player already has a highscore
- [ ] Error message with inaccessible file
- [ ] Saved with a name and a score
- [ ] Saved with highest level reached ?
- [ ] Saved with time taken on all levels ?
- [ ] ** **Loading** **
- [ ] Loaded when game launches
- [ ] Error message with inaccessible file
- [ ] Put in Queue iterator with score key to keep sorted
- [ ] Maximum 10 scores can be saves
- [ ] Player names policy (10 characters max, letters ans spaces)
- [ ] Scores policy (non negative)


## Cheat mode

- [ ] Turns a flag on that prevent highscore saving


## Error handling

- [ ] ** **Highscores** **
	Error message in main menu with specific error and consequence (can't save any score, had to reset score, etc.)
- [ ] ** **Config** **
	Error message in main menu with specific invalid key, and fact that it was replaced with default value (indicate where possible that missing values with be defaulted)
- [ ] ** **In game** **
	Special screen for corrupted game assets or unexpected exception (back to main menu)




%% kanban:settings
```
{"kanban-plugin":"board","list-collapse":[false,false,false,false,false,false,false,false,false,false,false,false,false,false],"lane-width":300}
```
%%