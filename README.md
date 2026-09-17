## Enter the crypt

*And put down the dead before they get the chance to rise from their tomb again.*

![Banner for the game Enter the Crypt](docs/gifs/banner.gif)

## Description

![Demonstration gif showing the main character running inside a dungeon-themed maze from armed skeletons before taking a weapon and chasing them down.](docs/gifs/demo.gif)

First released in 1980 by Namco, Pac-Man quickly became a cultural icon and one of the most influential video games of all time. Designed by Toru Iwatani, its goal was to create a game that could appeal to women and casual players, contrasting with the space shooters of the era. The game introduced the now-famous ghost AI, each with unique behavior.

Pac-Man was also the first game to popularize the concept of a power-up — the Pacgum (or Power Pellets) that lets you eat the ghosts. The original arcade machine had 256 levels, but due to an integer overflow bug, level 256 was impossible to finish, known as the infamous “kill screen”.

In this project, we had breathe new life into this classic by building our own version — in Python, with modern structure and project organization, ready to be deployed on a real gaming platform.

This project allowed us to greatly improve the following skills:
- 2D rendering
- Object-Oriented programming
- Configuration management
- Game architecture
- Interface design
- Object-Oriented conception
- Dependancy management
- Application packaging & deployment

## Features

![](docs/itch.io/game-instructions.png)

Collect all the coins scattered in each level to progress to the next, but beware of the skeletons risen from the dead !

Taken by surprise, you dropped your weapon. But all hope is not lost ! Gain extra points by picking up knives lost by those more unfortunate than you, and by vanquishing your enemies !

### Customizable levels

10 levels are available by default, with the first alone remaining the same every run. However, the game is bundled with a configuration file that you can modify and which you can find a breakdown of just [below](#Configuration), to create endless possibilities for your adventure !

### Languages and Keybinds support

The game comes right now with english and french support, but is made to be expandable ! All dialogs in addtional languages can come from a new json file in the dedicated assets folder.

On that matter, the game's resolution, sound volumes and keybinds can also all be configurable in and out of game ! This is done using the settings.json file, or the settings menu.

### Highscores

Celebrate your run by saving its statistics next to your name ! Up to ten highscores can be saved at a time, so keep steady to stay on the board !

### Cheats

Feeling stuck, or eager to experiment ? Cheats are included ! Test out levels and the skeleton's limits with invincibility, super speed or infinite timer. Note however that you won't be able to save your score this way.

To access the dedicated menu during a level, enter the Konami code using your set keybinds:

|||||||||||
|-|-|-|-|-|-|-|-|-|-|
| Up | Up | Down | Down | Left | Right | Left | Right | Confirm | Return |

## Instructions / Installation

To use this project, you can download it from its zip file from github, or by running this command in a terminal located in the chosen destination:

```bash
git clone https://github.com/jolyne-mangeot/Pac-man
```

And to run it, ensure python is installed on your computer or virtual environment, and run the following commands:

```bash
pip install -r requirements.txt
python pacman.py pacman/config.json
```

If you're unsure of these commands' action or want to run the program in a virtual environment without typing every command, see the instruction for the Makefile just below.

### Makefile

This project contains a Makefile, a file that is used to pre-enter commands to run to perform different tasks like installation, running and cleaning. The following rules are integrated here:

| Rules | Action |
|---|---|
| run | run the pacman file with preset arguments, ensuring everything is installed |
| skip-install | when dependencies are installed, run the pacman file without checking dependencies |
| debug | run the pacman file with preset arguments through pdb |
| install | create a virtual environment and install dependencies |
| clean | remove mypy cache, python cache, build files and output_file |
| fclean | run clean and remove the virtual environment |
| lint | run flake8 and mypy with flexible rules (code styling and typing) |
| lint-strict | run flake8 and mypy with strict rules |

To run any, enter 'make' followed by the selected rule in a terminal located at the project's root folder, like so:

```bash
make install
```

Executing `make` alone is an equivalent to `make run`.

### Configuration

This programs runs using a configuration file situated in the pacman folder, named `config.json`. Its path must be indicated when running the game, and it's then parsed. This parsing shows multiple caracteristics:
- The `config.json` file supports comments, which are lines starting with `#` or `//`.
- Missing values are replaced with a default one, sometimes randomized to fit gameplay replayability.
- Faulty values are also replaced or randomized.

Any inaccessible files either for retrieving data or saving a highscore will display an error message in relevant areas (main menu or score saving screen).

For a full breakdown of the configuration file and how to customize levels, [see here](docs/ConfigurationFile.md).

## General sofware architecture
We used a MVC architecture which is a fundamental design pattern that helps us organize code by separating the project into three interconnected components : Model - View - Controller. These three distinct layers work together to create well-structured applications. 

<img src="https://www.crio.do/blog/content/images/2021/07/Components-of-MVC-Architecture-Pattern.png" alt="" align="right" width="520"/>

### Controller
"Controllers" are the carrier of the user's inputs to the models, and initiators of the display by the viewers. Here are the modules our program relies on:
- [Control Class](#Architecture-2): head of the program, responsible to cycle through the States and reference models needed in multiple places.
- [States Class family](#Architecture-2): Each state correspond to an independant phase the game can be in, with its own parsing of inputs and data updates, to help divide responsibilities and keep clean a growing game with multiple menues.
- [Menu module](docs/Menu-Options.md): offers the user various ways of manipulating values in real-time. Contains a list of Options models that it manipulates using the user's inputs.

### Model
The "models" module contains all of the game's logic and data, independent of the display (View) and input handling/game loop (Controller). It is divided into several submodules:
- [Entity module](#Entity): contains the logic of movement and variables for all entities.
- [MazeMap module](#MazeMap): Contains an interface to the given maze generator that it takes data from to serialize for the GameState to use along the entities.
- Level module: Heart of the game in itself, pulling data from the JSONModels and keeping the Entities and the MazeMap objects updated.
- [JSONS module](docs/JSONModels.md): BaseModel classes handling the parsing of configuration files, replacing every faulty or missing value with a default one.
- [Menu - Options module](docs/Menu-Options.md): Options class family of the Menu module, taking in simple actions to perform in the purpose of manipulating back-end variables.

### View
The "views" modules effectively handle all visual depiction of the models' data, either it be backgrounds, menues or interfaces.
- [State - Display module](#Display): These classes each are dedicated to the rendering of a single State, dividing even more responsibilities. The `dgame.py` file contains the LevelDisplay class, scaling and displaying everything related to a running level.
- [Menu - Render module](docs/Menu-Options.md): The MenuRender, PlaceHolder and Style classes are utility helping the display of text, buttons and entire menues, tying together to try and optimize thse operations.

## Maze-generator
Unfortunately, the scope of this project did not allow us to use the maze generator we had created for the `Amazing` project. We had to use a pre-built generator. It was provided as a `.whl` file. So we simply ran `pip install` in our virtual environment to make it available in our Python library, and then imported it into the `utils.py` file in our `pacman/models/mazemap/` module.

The generator creates a maze in the form of a y-by-x matrix containing, in binary, information about the maze's walls. 0 represents a cell with no wall, 1 represents a single wall to the north, 2 represents a single wall to the east, 4 represents a single wall to the south, and 8 represents a single wall to the west. Thus:

||||||||||||||||||
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| Int | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| Binary | 0000 | 0001 | 0010 | 0011 | 0100 | 0101 | 0110 | 0111 | 1000 | 1001 | 1010 | 1011 | 1100 | 1101 | 1110 | 1111 |
| Walls | No wall | N | E | NE | S | SN | SE | SNE | O | ON | OE | OEN | OS | OSN | OSE | OSEN

The algorithms we used to solve our maze were designed for an x-by-y maze. To simplify the behavior algorithm for our entities, we therefore formatted the provided maze. The maze generated by the MazeGenerator is formatted in the `utils.py` file of the `pacman/models/mazemap` module using the maze_interface() function. After this formatting, we obtain an x-by-y grid of Cells, which is then stored in the Map class in the `map.py` file.

Our approach to managing wall information was also different: we used a list of four Booleans for each cell in the maze, with each index in the list corresponding to information about a wall. We felt that the binary approach was much more efficient, so we stuck with it. Each cell in the grid therefore contains a `walls` attribute, which is simply an integer between 0 and 15.

## Implementation

### Entity

#### Architecture

![Class diagram for the entity.py file](docs/img/entity-diagram.png)
<img src="docs/img/strategies-diagram.png" alt="Class diagram for the strategies.py file" align="right" width="520"/>

The module is divided into two files with distinct responsibilities:

- `entity.py`: defines what the entities are (Entity, Pacman, Ghost)—their state (position, velocity, direction, lives) and their specific attributes.
- `strategies.py`: defines how ghosts move, using the Strategy pattern. A Strategy is an independent class that calculates a ghost's next position based on its current position and that of a target; Ghost simply delegates the call to one of its three strategies (idle_strat, chase_strat, escape_strat) depending on the game context.

The concrete strategies are divided into three families, each of which inherits from the abstract Strategy class:

|Type|Role|Implementations|
|---|---|---|
|Chase|Chase Pac-Man|ChaseStrumbling, ChaseDynamic, ChaseOnSpot|
|Idle|Patrolling without a pursuit|AlternateAngleStrat, PatrollingAngleStrat|
|Escape|Escape Pacman|EscapeMaxDistance, EscapeToCorner, EscapeDynamic|

All strategies also inherit from `Strategy.find_path()`, which implements the A* algorithm to calculate the shortest path from the ghost to the target.

#### Design Choices
- Pattern Strategy rather than conditional branches in Ghost. Each movement behavior is isolated in its own class, which allows us to add, replace, or combine behaviors without modifying Ghost or the other strategies
- String-based configuration (strat_dict): Ghost receives the names of the strategies (idle_strat: str, chase_strat: str, escape_strat: str) rather than instances, and resolves them via strat_dict. This allows us to define the behavior of each ghost from an external configuration file.
- Reusing the intersection graph for A* algorithm. Rather than running an A* search on all cells, each strategy relies on the intersection graph already constructed by `Map.generate_cell_graph()`, which makes pathfinding significantly less computationally expensive.
- Stamina mechanics. `chase()` artificially limits the duration during which a ghost can continuously chase Pac-Man (`current_stamina`), which regenerates during idle/escape phases.This design prevents a ghost from chasing indefinitely and makes the game more playable.
- Various escape, chase, or idle methods. These allow us to give our ghosts a variety of behaviors and thus adjust the difficulty of the levels by using more or less aggressive strategies.
- `next_direction` (distinct from `direction` in Pac-Man). Allows the player to anticipate a turn before reaching the intersection that allows it, rather than requiring the player to enter at exactly the right moment.

### MazeMap

#### Architecture
The module is divided into two files:

- utils.py: low-level data types (Directions, Movements, Cell, Node) and the maze_interface() function, which acts as an adapter between the external maze generator and the game's internal model.
- map.py: the Map class, which manages the maze's storage, handles the gums, and constructs the intersection graph used for the ghosts' pathfinding.

#### Design Choices
- Representation of walls using a bitmask rather than a list of Booleans. Each Cell stores an integer `walls` (0 to 15) instead of a list of four Booleans. This choice (already explained earlier in the README) allows wall checks to be performed using a simple binary operation
(walls & direction.value) instead of indexed access, and aligns directly with the format returned by the external generator.
- `maze_interface()` as an adaptation layer. The external generator indexes its grid in (y, x). maze_interface() performs the conversion to the (x, y) indexing used by the rest of the game and constructs a Cell object for each cell. Isolating this conversion into a single function prevents the indexing logic from being scattered throughout the rest of the code, and
limits the impact of a generator change to just `utils.py`.
- Intersection graph rather than a full grid for A* algorithm. `record_maze_intersections()` identifies cells with 3 or 4 open walls, and `generate_cell_graph ()` constructs, for each one, a list of its directly accessible neighboring intersections, via `find_intersect()`, which
follows a corridor cell by cell until it reaches the next intersection. This reduces the pathfinding search space to only the actual decision points in the maze.
- Tracking the gums using a Boolean in Cell and a set in Map. Each cell stores a Boolean (simple_gum/super_gum) for display and local testing, while Map maintains, in
parallel, the sets simple_gums/super_gums of coordinates, allowing direct access to the positions of the remaining gums without having to scan the entire grid.
- Turn dictionaries (RIGHT_TURN, LEFT_TURN, OPPOSITE_DIRECTION). Rather than recalculating these relationships on the fly, they are precalculated as module constants, used by
both `find_intersect()` and `Strategy.find_path()`.

### Pygame general implementation

#### Architecture
Pygame being the game's "engine", it had to be implemented in most of our modules and architecture choices. The library is imported in all controllers, many models and all views modules, used to receive the player's output as well as display everything on a graphical interface.

##### Control and States

[See the detailed class diagram for this module](docs/img/controllers-diagram.png)

For inputs and menu management, State classes were created in the controllers/states module to divide our program into standalone pages, such as the main menu, the options menu and the game itself. Managed by the [Control class](pacman/controllers/statecontrol.py) and depending on the user's inputs, these states are activated and deactivated, enabling an easier memory management and how the game progresses. This structure was inspired by this [thread on the python forum by metulburr](https://python-forum.io/thread-336-post-103792.html#pid103792)

##### Display

[See the detailed class diagram for this module](docs/img/statesdisplay-diagram.png)

And for displaying, the views/menu module helps rendering option menues described in this [documentation file](docs/Menu-Options.md), while the Display subclasses, each dedicated to their own state, also have the unique responsibility of rendering assets and variables.

#### Design Choices

Pygame was the main reason we opted for a MVC pattern. With numerous modules, the library can quickly create inter-dependencies and extremely long methods and classes. That's why we thought first-hand on how to keep this project manageable, and clear to approach.

- If navigating multiple folders and cutting up modules between three different folders can seem confusing at first, when the project kept growing, it helped us staying focused on separating the modules' responsibilities. For the menues, the parsing of events is placed in a controllers class, the options themselves are models, and the renderer dedicated to them is in views.
- A Control class centralizing all informations and being referenced in almost the entire project was the key to keeping the user's configuration and the displaying aligned together.
- The same way, a common Display class, parent of all state displaying class, helped centralizing the file accesses for sprites and reducing endless lines of scaling.

## Project management

To facilitate the implementation of this project, we took the time to go through a conception phase. We used the Obsidian software to centralize our documentation and organize the tasks to be completed. We made a list of the prerequisites for the project so we wouldn't forget anything.

![](docs/img/project-kanban.png)

The next step was to think about how to organize the project using the MVC architecture. We considered the various submodules needed and assigned them to the model, controller, or view components of the project. The goal was to optimize the dependencies and communication between these different submodules so that the architecture would be clear and well-organized.

Various of the modules we eventually coded are documented in the docs folder.

### Timeline

**1st Week:** 
- Initialize all project folders and files.
- JSON configuration file and parsing.
- Realization of the Makefile.

**2nd Week:** 
- Start and organization of the menu module.
- Add docstrings for the files that have already been completed.

**3rd Week:**
- Optimization and continuity of the Menu module.
- Start and organization of the Entity module.

**4th Week:**
- Optimization and continuity of the Entity module.
- Creating a tester to test the various subcomponents of the Entity module.

**5th Week:**
- Start and organization of the display module.
- Add and update of docstrings.
- Add the level module to link the maze, Pac-Man, and the ghosts.
- Fix of bugs and conception issues.

**6th Week:**
- Finalization of map management.
- Conceptualization and start of ghost Strategies.
- Optimization and continuity of the display module.

**7th Week:**
- Research and implementation of assets and sprites.
- Continuity and optimization of previous modules and submodules.
- Add and update of docstrings.
- Fix of bugs and conception issues.

**8th Week:**
- README.md creation.
- Optimization of the project.
- Finalization of display.
- Building the game executable file.

## Resources

> [!NOTE]
> No AI was used in the making of this project.

### Credits

Apart fom the game's logo, all assets come from OpenGameArt, by diverse artists. Some were used as is, and other modified. You can find details on how each asset was assembled in this [credits file](pacman/assets/credits.md), and here is a quick list of all artists:
- https://opengameart.org/users/buch
- https://opengameart.org/users/zaphgames
- https://opengameart.org/users/emcee-flesher
- https://opengameart.org/users/craftpixnet-2d-game-assets
- https://opengameart.org/users/trulio
- https://opengameart.org/users/ansimuz
- https://opengameart.org/users/killamaaki

### Parsing
JSON parsing with comment:
- [Code snippet (StackOverflow)](https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments#:~:text=This%20implementation%20slightly%20improves%20the%20previous%20answer%20by%20replacing%20the%20comment%20line%20by%20an%20empty%20line%20rather%20than%20removing%20it%20completely%20because%20this%20breaks%20the%20line%20count)

Pydantic's documentation:
- [Models](https://pydantic.dev/docs/validation/dev/concepts/models/)
- [Field](https://pydantic.dev/docs/validation/latest/concepts/fields/)
- [Validators](https://pydantic.dev/docs/validation/latest/concepts/validators/)
- [Creating dynamic Fields](https://pydantic.dev/docs/validation/dev/examples/dynamic_models/)

### Menu and options
- [Pygame's keys list](https://www.pygame.org/docs/ref/key.html#:~:text=pygame%20Constant%20ASCII%20Description)
- [TEXTINPUT event type](https://www.pygame.org/docs/ref/event.html#:~:text=When%20compiled%20with%20SDL2%2C%20pygame%20has%20these%20additional%20events%20and%20their%20attributes)

### Architecture
- [MVC Structure](https://www.geeksforgeeks.org/system-design/mvc-design-pattern/)
