*This documentation was written early in the project and was made for structural choices clarity and conceptual guidance. It only reflects early renders of the program and code described here may differ from the final version.*

## Customization in games

When creating a game with multiple levels, being able to customize and adapt each level efficiently is mandatory. Meaning, setting up a system where most variables are data-driven is quickly unavoidable.

Using our [JSONModel class](JSONModels.md), parsing json files stopped being a problem, and so we found ourselves able to maximize the customization of anything possible. This documentation stands to explain and guide the making and understanding of the `config.json` file, main source of configuration values to run our game.

## config.json

First and foremost, as everything in this file is parsed using an implementation of [Pydantic](JSONModels.md#Building a BaseModel with fallback validations), any faulty value will be reset to either a default, or a randomized value.

Each Config listed below is parsed using its dedicated class, which you can all find declared in this [python file](../game/models/jsons/jconfig.py).

### PlayerConfig

Entry:
```json
{
	"player": {
		"lives_count": 3,
		"cheats_allowed": false}
}
```
As lives and cheats enabling are shared across all levels, this entry is at the root of our
config file. Simply, it contains the number of lives the player will have starting a game, and weither or not they can active cheats.

Regenerating life either through cheats or by entering a new level will never surpass the lives_count stated here.

Cheats cheats are allowed, you can enter the dedicated menu in game using the Konami code with your chosen key configuration, B standing for the confirm key, and A the return key (used to open the pause menu normally).

### LevelConfig

Entry:
```json
{
	"levels" : [
		{
			"maze": {},
			"gameplay": {},
			"scores": {}
		},
		{}
	]
}
```

The game levels consist of a list declared at the root of the configuration file. Each is a dictionary, containing entries for the MazeConfig, GameplayConfig and ScoresConfig.

Leaving blank any of these configurations or their own entries will, again, replace them with default or randomized values. In that matter, any empty dictionary added in the list will create a randomly generated level.

### MazeConfig

Entry:
```json
{
	"levels" : [
		{
			"maze": {
				"width": 6,
				"height": 6,
				"gum_percent": 50,
				"seed": 68771
			},
		}
	]
}
```

While width and height are straightforward, the `gum_percent` variables is used during the maze's generation so only a certain percentage of all accessible cells contain a simple gum, or coin in our instance. A value of 0 will generate a maze without coin, and 100 one with coins in every cell, excluding: inaccessible cells (related to the central pattern), and angle cells, where are situated the super gums, or knives.

The seed is what's used to make the randomization of walls reproducible. Meaning, two levels with the same width, height and seed will have the exact same paths, and if the gum percentage is also identical, both will have the same coins distribution.

### GameplayConfig

Entry:
``` json
{
	"levels" : [
		{
			"gameplay": {
				"timer": 120,
				"theme": "grassy",
				"life_regen": 1,
				"super_duration": 5,
				"pacman_speed": 5,
				"pacman_super_speed": 6,
				"ghosts": {
					"Blinky": {},
					"Pinky": {}
				}
			},
		}
	]
}
```

- `timer`, `theme`, `super_duration`

The gameplay configuration relates to the general settings of the level. The timer and super duration are in seconds. The theme should be either "grassy" or "dungeon" and are linked to the maze's general rendering with paths, walls and decorations changing based on spritesheets.

- `life_regen`

The life regeneration is done upon entering the level. So for the first level, it doesn't actually do anything, as the player starts with their life maxed.

- `pacman_speed`, `pacman_super_speed`

The pacman speed and super speed correspond to the number of cells traveled every 3 seconds. This may seem odd to calculate it this way, but it allows for wider ranges of speed than basing the speed on cells traveled every 1 second. A value between 4 and 8 should be good for small to medium-sized mazes.

- `ghosts`

Finally, the ghosts are arranged in a dict, with each their own configuration. What's important to differenciate them is their name. Any entry in this ghosts dict with an unknown name will be ignored, between the four classic PacMan ghosts:

| Ghost name| Starting position |
|---|---|
| Blinky | Top left |
| Pinky | Top right |
| Inky | Bottom left |
| Clyde | Bottom right |

The names are associated with appearance in the game, but sprites are not customizable.

### GhostConfig

Entry:
```json
{
	"levels" : [
		{
			"gameplay": {
				"ghosts": {
					"Blinky": {
						"idle_strat": "AlternateAngleStrat",
						"chase_strat": "ChaseOnSpot",
						"escape_strat": "EscapeToCorner",
						"speed": 5,
						"super_speed": 5,
						"chase_radius": 2,
						"escape_radius": 3,
						"chasing_stamina": 6,
						"down_time": 3
					},
					"Pinky": {}
				}
			},
		}
	]
}
```

As described in the [level configuration](#LevelConfig), each ghost must be declared independently. Any ghost without an entry will not appear in the game. So, to have a ghost be randomly generated, it must be declared with an empty dictionary, like Pinky's here.

Every attribute of the ghosts are randomized if missing, with values relatively coherent together, but may sometimes be unbalanced regarding the size of the maze, the player's lives, PacMan's speeds, etc.

- `idle_strat`, `chase_strat`, `escape_strat`

The idle, chase and escape strats are strategies, classes we declare in this [python file](../game/models/entity/strategies.py) and that manages how each ghost moves. Here is the currently available list of strategies:

| Strategy name | Description |
|---|---|
| **Idle strategies** |  |
| AlternateAngleStrat | The ghost will constantly move between each angle of the maze and its center, picking one randomly apart from the one it's currently in. |
| PatrollingAngleStrat | The ghost will set off to a random position in the area it's in. An area is a full quarter of the maze. |
| **Chasing strategies** |  |
| ChaseOnSpot | When PacMan enters the ghost's chasing radius, it will go to PacMan's current position, and will update it only when reaching said position. |
| ChaseFumbling | During chasing, the ghost may fumble and access a random cell out of it's initial path, making it easier to escape as PacMan. |
| ChaseDynamic | The ghost will update it's current path towards PacMan every cell it travels, making it hard to escape. |
| **Escaping strategies** |  |
| EscapeMaxDistance | When escaping, the ghost will travel to the farthest cell from PacMan. |
| EscapeToCorner | The ghost will find the path to a maze's angle that's farthest from PacMan. |
| EscapeDynamic | Every cell it travels, it will look for the one distancing it from PacMan. |

The strategies are categorized here for indications, but an escape strategy may very well be written in the `escape_strat` and vice-versa, same for idling.

The `idling` strategy is called when the ghost is away from PacMan by its chase or escape radius (see below). The `chase` strategy is called during normal mode (not super), and if PacMan is close enough. The `escape` strategy is called during super mode if PacMan is close enough.

- `speed`, `super_speed`

Speeds for the ghost work the same as for [PacMan](#GameplayConfig)

- `chase_radius`, `escape_radius`, `chase_stamina`

The chase and escape radius are the Manhattan distance (number of cells between PacMan and the ghost regardless of walls), under which the ghost will move using its `chase_strat` or `escape_strat`, depending on the current mode (normal or super).

- `down_time`

The downtime is the time in seconds during which the ghost will stay inactive after being beaten during the super mode. It will reappear in normal mode, even if the super mode is still active for PacMan.
