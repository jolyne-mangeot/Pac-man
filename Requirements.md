---

kanban-plugin: board

---

## README



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
- [ ] MUST support comments for lines starting with a #
- [ ] [Snippet](https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments)
- [ ] ** **Config** **
	all in root dictionary
- [ ] `highscore_file` str
- [ ] ** **Player** **
	key: `player`
- [ ] `life_amount` int > 0
- [ ] ** **Levels** **
	key: `level_#` (ID)
- [ ] Configuration for each level
- [ ] `maze_width` int > 3
- [ ] `maze_height` int > 2
- [ ] `timer` int > 0
- [ ] `gum_score` int >= 0
- [ ] `supgum_score` int >= 0
- [ ] `ghost_score` int >= 0
- [ ] `level_score` int >= 0 ? (on level complete)
- [ ] `seed` int (random if non existent)
- [ ] `pac_man_speed` int >= 0
- [ ] `ghost_speed` int >= 0
- [ ] `super_duration` int >= 0
- [ ] `life_regen` int >= 0 ? (life regained on level start)


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
- [ ] Saved in json file ?
- [ ] Saved when winning or losing levels
- [ ] Error message with inaccessible file
- [ ] Saved with a name and a score
- [ ] Saved with highest level reached ?
- [ ] ** **Loading** **
- [ ] Loaded when game launches
- [ ] Error message with inaccessible file
- [ ] Maximum 10 scores can be saves
- [ ] Player names policy (10 characters max, letters ans spaces)
- [ ] Scores policy (non negative)


## Cheat mode

- [ ] Turns a flag on that prevent highscore saving




%% kanban:settings
```
{"kanban-plugin":"board","list-collapse":[false,false,false,false,false,false,false,false,false,false,false,false,false]}
```
%%