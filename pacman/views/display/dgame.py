
from typing import TypedDict, cast, Literal
from random import randint as rand, choice

import pygame as pg

from .display import Display, SpriteSheet
from pacman.controllers import Control, Menu
from pacman.models import (
    Level, OPPOSITE_DIRECTION, Movements, Directions, Entity)
from pacman.views import (
    Style, PlaceHolder, MenuRender, render_word, new_surface)


class LevelDisplay:
    """Class LevelDisplay

    #### Description:
    Responsible to render all visual elements related to the currently running
    level. Namely, scales the maze based on its size and the interface's,
    and render it once. Scales the characters and gums based on the maze,
    and implement all necessary methods to display them efficiently.

    ### Attributes:
    <u>Parameters:</u>
    - display: GameDisplay => used to recover all assets that have already been
    loaded
    - level: Level => used to recover all informations about the gums, the
    entities and all evolving variables

    <u>Self attributed:</u>
    - maze_surf: pg.Surface => Surface created once when the level is loaded in
    and copied to display the characters and gums onto
    - characters: dict[str, CharacterSprites] => dict of CharacterSprites,
    TypedDicts containing directional sprites for all characters, here scaled
    - life_bar: pg.Surface => Surface created once to fit the visual life_bar
    in the interface, showing how many lives the player has left
    - cell_size: int => integer for the size of a cell after scaling
    - cell_gap: int => integer for the size between all maze cells
    - gum: list[pg.Surface] => sprites to animate and display gums
    - sup_gum: list[pg.Surface] => sprites for the super gums

    ### Methods:
    - scale_cells => scale the cell size and gaps based on the maze and display
    - coords => return a position based on the cell size and gap
    - render_maze => scales the maze and generate a Surface with all its
    static visual elements
    - scale_characters_and_gums => scales the characters, gums and super gums
    based on the cell_size
    - scale_ui => scales the visual elements of the interface
    - render_entity => place the entities on the maze based on the direction
    they're facing and render their right sprite
    - render_interface => updates texts and bars to display them on the
    interface based on updated values
    - draw => calls the right rendering methods to display all the levels
    elements
    """
    def __init__(self, display: GameDisplay, level: Level) -> None:
        """Instantiate the LevelDisplay with a GameDisplay object containing
        loaded assets, and a Level, containing every needed values to display
        the right informations in real-time.

        Calls scaling methods and pre-renders the maze.
        """
        self.display: GameDisplay = display
        self.level: Level = level

        self.maze_surf: pg.Surface
        self.characters: dict[str, CharacterSprites]
        self.life_bar: pg.Surface

        self.cell_size: int
        self.cell_gap: int
        self.gum: list[pg.Surface]
        self.sup_gum: list[pg.Surface]

        self.scale_cells()
        self.render_maze()
        self.scale_characters_and_gums()
        self.scale_ui()

    # _________________________________________________________________________
    #                           MAZE-RELATED METHODS
    # _________________________________________________________________________

    def scale_cells(self) -> None:
        """Calculates the size of a maze cell and sets its gap between its
        neighbours based on the maze size and display.

        Sets the size based on either the width or height of the interface
        based on the aspect ratio of the maze.
        """
        if self.level.map.width > self.level.map.height * 1.7:
            maze_width: int = int(
                self.display.control.interface.get_width() * 0.98)
            maze_height: int = int(maze_width * self.level.map.height
                                   / self.level.map.width * 0.98)
        else:
            maze_height = int(
                self.display.control.interface.get_height() * 0.82)
            maze_width = int(maze_height * self.level.map.width
                             / self.level.map.height * 0.98)

        self.cell_size = maze_width // int(self.level.map.width * 1.5)
        self.cell_gap = int(self.cell_size // 2.3)

    def coords(self, x: int, y: int, h_path: float = 0, v_path: float = 0
               ) -> tuple[int, int]:
        """Returns the calculated position of a point (x, y) in the maze based
        on the cell size and gap. h_path and v_path arguments append to this
        position the value times the cell size, to access all angles of a
        cell.
        """
        return ((x * self.cell_size) + (x * self.cell_gap)
                + int(h_path * self.cell_size),
                (y * self.cell_size) + (y * self.cell_gap)
                + int(v_path * self.cell_size))

    def render_maze(self) -> None:
        """Creates the maze_surf attribute's Surface and scales elements that
        will only be used to this matter, namely the path between cells and
        the walls, and decorations displayed in inaccessible cells.

        Then, for every cells, render their borders and place their walls
        before rendering them on the maze_surf. Has a 25% chance to place a
        decoration in a closed-off cell.
        """
        cell_s: int = self.cell_size
        cell_g: int = self.cell_gap

        self.maze_surf = new_surface(self.coords(
            self.level.map.width, self.level.map.height + 1, -0.5, -0.6))

        assets: LevelTheme = self.display.themed_assets[self.level.theme]

        p_a_w: dict[str, pg.Surface] = assets["paths_and_walls"]
        scale: dict[str, pg.Surface] = {
            "h_path": pg.transform.scale(p_a_w["h_path"], (cell_g, cell_s)),
            "v_path": pg.transform.scale(p_a_w["v_path"], (cell_s, cell_g)),
            "wall": pg.transform.scale(p_a_w["wall"], (cell_s, cell_s)),
            "s_wall": pg.transform.scale(
                p_a_w["small_wall"], (cell_g, cell_s)),
            "down_wall": pg.transform.scale(
                p_a_w["down_wall"], (cell_s, cell_s * 2)),
            "s_down_wall": pg.transform.scale(
                p_a_w["small_down_wall"], (cell_g, cell_s * 2))}

        props: list[pg.Surface] = [pg.transform.scale(
            prop, (cell_s, cell_s)) for prop in assets["decorations"]]

        for y in range(self.level.map.height):
            for x in range(self.level.map.width):
                walls: int = self.level.map.map[x][y].walls

                cell: pg.Surface = new_surface((16, 16))
                cell.blits([
                    (p_a_w["ground_surface"], (rand(-48, 0), rand(-48, 0))),
                    (assets["binary_cell_borders"][walls], (0, 0))])

                cell = pg.transform.scale(cell, (cell_s, cell_s))
                elems: list[tuple[pg.Surface, tuple[int, int]]] = [
                    (cell, self.coords(x, y))]

                if not (walls & 2):
                    elems.append((scale["h_path"], self.coords(x, y, 1)))
                    elems.append((scale[
                        "s_down_wall" if y == self.level.map.height - 1
                        else "s_wall"], self.coords(x, y, 1, 1)))
                if not (walls & 4):
                    elems.append((scale["v_path"], self.coords(x, y, 0, 1)))
                else:
                    elems.append((scale[
                        "down_wall" if y == self.level.map.height - 1
                        else "wall"], self.coords(x, y, 0, 1)))
                if walls == 15:
                    if rand(0, 100) < 25:
                        elems.append((choice(props), self.coords(x, y)))

                self.maze_surf.blits(elems)

    # _________________________________________________________________________
    #                           SCALING METHODS
    # _________________________________________________________________________

    def scale_characters_and_gums(self) -> None:
        """For every character, gum and super gum's sprites, scale them based
        on the cell_size and place these renders in their dedicated attributes.
        """
        assets: LevelTheme = self.display.themed_assets[self.level.theme]
        cell_s: int = self.cell_size

        self.gum = [pg.transform.scale(gum, (cell_s, cell_s))
                    for gum in assets["gum"]]
        self.sup_gum = [pg.transform.scale(sup_gum, (cell_s, cell_s))
                        for sup_gum in assets["sup_gum"]]

        self.characters = {}
        for char, sprites in self.display.characters.items():
            self.characters.update({char: {"normal": {}, "super": {}}})
            for mode in ("normal", "super"):
                for dir, frames in sprites[mode].items():
                    self.characters[char][mode].update({
                        dir: [pg.transform.scale(
                            frame, (cell_s, cell_s)) for frame in frames]})

    def scale_ui(self) -> None:
        """Scales and renders the life bar for the interface. Calculates a
        life bit's size based on the player's max lives, and renders them
        on a the life_bar attribute until the bar is full.
        """
        ui_size: tuple[int, int] = (
            self.display.scaled_ui["level_ui"].get_size())
        bar_w: int = int(ui_size[1] * 2.92)
        bar_h: int = int(ui_size[1] * 0.29)
        if self.level.max_lives > 1:
            life_size: float = bar_w / (self.level.max_lives + 1)
            life_gap: float = ((bar_w - life_size * self.level.max_lives)
                               / (self.level.max_lives - 1))
        else:
            life_size = bar_w
            life_gap = 0
        life_part: pg.Surface = pg.transform.scale(
            self.display.interface["life_bar"], (life_size, bar_h))
        bar_start: pg.Surface = pg.transform.scale(
            self.display.interface["life_bar_s"], (ui_size[1] * 0.02, bar_h))
        bar_end: pg.Surface = pg.transform.scale(
            self.display.interface["life_bar_e"], (ui_size[1] * 0.02, bar_h))

        blits: list[tuple[pg.Surface, pg.Rect]] = []
        for i in range(self.level.max_lives):
            blits.append((life_part,
                         pg.Rect((life_size * i) + (life_gap * i), 0, 0, 0)))
        blits.extend([(bar_start, pg.Rect(0, 0, 0, 0)),
                      (bar_end, bar_end.get_rect(topright=(bar_w, 0)))])
        self.life_bar = new_surface((bar_w, bar_h))
        self.life_bar.blits(blits)

    # _________________________________________________________________________
    #                            RENDERING METHODS
    # _________________________________________________________________________

    def render_entity(
            self, name: str, char: Entity, speed: int
            ) -> tuple[pg.Surface, pg.Rect]:
        """Render an entity based on arguments, placing them on the maze based
        on their direction and their animation progression from the Level.

        #### Arguments:
        - name: str => used to retrieve the character's animation progression
        from the Level, as well as correct sprite from the scaled characters
        attribute
        - char: Entity => used to retrieve the character's direction and
        current mode
        - speed: int => reference for how much the character has progressed
        from one cell to another.

        Returns a tuple of the character's render surface and a pygame.Rect
        object containing its correct position to be displayed at.
        """
        direction: Directions = next(dir for dir in (
            char.direction, getattr(char, "next_direction", Directions.NONE),
            Directions.DOWN) if dir.value != 15)
        coords: tuple[int, int] = self.coords(*char.pos)
        origin: tuple[int, int] = Movements[
            OPPOSITE_DIRECTION[direction].name].value
        offset: int = 0
        if char.direction.value != 15:
            progression: int = speed - self.level.char_anim[name]
            progression = progression if progression > 0 else 0
            offset = int(
                progression * (self.cell_size + self.cell_gap) / speed)
        position: tuple[int, int] = (
            coords[0] + (origin[0] * offset), coords[1] + (origin[1] * offset))
        mode: str = "super" if char.is_super else "normal"
        frame: int = int(self.level.char_anim[name] * 3 / speed) % 3
        return (
            self.characters[name][cast(Literal["normal", "super"], mode)][
                direction.name][frame],
            pg.Rect(*position, self.cell_size, self.cell_size))

    def render_interface(self) -> tuple[pg.Surface, pg.Rect]:
        """Renders all interface visuals and return a tuple containing the
        full surface and a pygame.Rect object containing its positional
        values to be displayed with.

        Renders the level's id and timer and the player's score in text,
        calculates the length of the life and super bars to display and puts
        everything together on the scaled ui.
        """
        ui_surf: pg.Surface = new_surface(
            self.display.scaled_ui["level_ui"].get_size())
        ui_h: int = ui_surf.get_height()
        ui_w: int = ui_surf.get_width()
        ui_surf.fill((15, 15, 15))
        level_id: pg.Surface = render_word(
            self.display.ui_styles["level"], str(self.level.level_id % 100), 0)
        score: pg.Surface = render_word(
            self.display.ui_styles["score"], str(self.level.score % 10000), 0)
        time: int = self.level.level_timer
        timer: pg.Surface = render_word(self.display.ui_styles["timer"],
                                        f"{time // 60:02d}:{time % 60:02d}", 0)

        life_size: tuple[int, int] = self.life_bar.get_size()
        life_bar: tuple[pg.Surface, pg.Rect, pg.Rect] = (
            self.life_bar, pg.Rect(ui_h * 5.66, ui_h * 0.175, 0, 0),
            pg.Rect(0, 0,
                    (life_size[0] - (self.level.max_lives - self.level.lives)
                     * life_size[0] / self.level.max_lives), life_size[1]))

        super_size: tuple[int, int] = (
            self.display.scaled_ui["super_bar"].get_size())
        super_visual: tuple[pg.Surface, pg.Rect, pg.Rect] = (
            self.display.scaled_ui["super_bar"],
            pg.Rect(ui_h * 7.46, ui_h * 0.65, 0, 0),
            pg.Rect(0, 0, self.level.super_anim * super_size[0]
                    / self.level.super_duration, super_size[1]))

        ui_surf.blits([
            (self.display.scaled_ui["level_ui"], pg.Rect(0, 0, 0, 0)),
            (level_id, level_id.get_rect(midright=(ui_h * 0.91, ui_h * 0.5))),
            (score, score.get_rect(midright=(ui_h * 3.39, ui_h * 0.5))),
            (timer, timer.get_rect(center=(ui_w / 2, ui_h / 2))),
            life_bar, super_visual])
        return (ui_surf, ui_surf.get_rect())

    def draw(self) -> None:
        """Puts all visual elements together to display the level.
        Creates a copy of the maze surface to display gums and super gums on,
        followed by characters. Renders the interface and place both on
        the game's interface.
        """
        control_interface: pg.Surface = self.display.control.interface
        self.display.control.screen.fill((0, 0, 0))
        game_surf: pg.Surface = new_surface((
            control_interface.get_width(),
            int(control_interface.get_height() * 0.85)))

        maze_surf: pg.Surface = self.maze_surf.copy()
        visual_elements: list[tuple[pg.Surface, pg.Rect]] = []

        visual_elements.extend([(
            self.gum[self.level.level_timer % 3],
            pg.Rect(*self.coords(*gum), self.cell_size, self.cell_size))
            for gum in self.level.map.simple_gums])

        visual_elements.extend([(
            self.sup_gum[self.level.level_timer % 3],
            pg.Rect(*self.coords(*sup_gum), self.cell_size, self.cell_size))
            for sup_gum in self.level.map.super_gums])

        for name, char in self.level.chars.items():
            if char.is_alive is True:
                if name != "Pacman":
                    visual_elements.append(self.render_entity(
                        name, char, char.current_speed))
                else:
                    speed: int = (
                        200 if self.level.cheats["super_speed"] is True
                        else char.current_speed)
                    visual_elements.append(self.render_entity(
                        name, char, speed))

        maze_surf.blits(visual_elements)
        game_surf.fill((15, 15, 15))
        game_surf.blit(maze_surf, maze_surf.get_rect(
            center=game_surf.get_rect().center))
        control_interface.blits([
            (game_surf, (0, int(control_interface.get_height() * 0.15))),
            self.render_interface()])


class LevelTheme(TypedDict):
    """TypedDict shared by the GameDisplay and LevelDisplay to efficiently
    transport loaded assets and sprites. Almost all are lists of pygame.Surface
    to hold multiple animations sprites, except for the path_and_walls,
    containing named surfaces for the maze's environment.
    """
    binary_cell_borders: list[pg.Surface]
    paths_and_walls: dict[str, pg.Surface]
    decorations: list[pg.Surface]

    gum: list[pg.Surface]
    sup_gum: list[pg.Surface]


class CharacterSprites(TypedDict):
    """TypedDict shared by the GameDisplay and LevelDisplay containing
    dictionaries for the characters sprites in all direction for both the
    normal and super mode. Could be a simple dict, but was named as a class
    to help organizing and storing multiple levels of dicts and lists.
    """
    normal: dict[str, list[pg.Surface]]
    super: dict[str, list[pg.Surface]]


class GameDisplay(Display):
    """Class GameDisplay, subclass of Display

    #### Description:
    Class used to display everything related to the running game. From the
    level with its maze and characters and the game interface, to the pause
    and cheats menues, as well as the level and run end menues. Implements
    all needed methods to scale and render all sprites, and for the GameState
    to easily update visuals if needed.

    ### Attributes:
    - *Display instance parameters and attributes*
    - themed_assets: dict[str, LevelTheme] => dict containing an entry for each
    existing theme for rendering the level's maze
    - interface: dict[str, pg.Surface] => dict for all level interface-related
    assets like the life and super bars
    - characters: dict[str, CharacterSprites] => dict for every character to
    store their directional sprites in all modes (normal and super)

    - level_display: LevelDisplay => instance created everytime a new level
    is accessed using the update_level method
    - scaled_ui: dict[str, pg.Surface] => as the game's interface depends on
    the size of the screen, they are scaled and stored in this class rather
    than LevelDisplay
    - ui_fonts: dict[str, pg.font.Font] => scaled fonts for the game's
    interface

    - menu_renders: dict[str, MenuRender] => dict for every menu accessible
    from the GameState

    ### Methods
    - *Display instance methods*
    <u>Game state-related methods:</u>
    - startup => called everytime GameState is accessed, updates the
    menu_renders dict and their positional variables
    - cleanup => deletes all scaled attributes in case the size of the window
    changes, called when the GameState is left
    - update_level => pass down a Level object from the GameState to a newly
    instantiated LevelDisplay instance
    - change_menu => called everytime a new menu is accessed within the game,
    pre-render all its options in case values have changed
    - update_menu => enable the GameState to update a menu's single option if
    needed
    <u>Assets-loading methods:</u>
    - load_level_assets => loads from files all level-related assets
    - load_characters_sprites => loads all directional sprites for every
    characters in the normal and super mode
    - load_theme_sprites => loads all level assets for a single theme
    <u>Scaling and rendering methods:</u>
    - scale_level_ui => scales all level interface assets based on the current
    window
    - draw => either call the LevelDisplay's draw method or the one of the
    current menu
    """
    def __init__(self, control: Control) -> None:
        """Initializes a GameDisplay instance using a reference to Control.
        Calls the Display init method, declared all attributes and calls
        sprites-loading methods.
        """
        super().__init__(control)
        self.themed_assets: dict[str, LevelTheme]
        self.interface: dict[str, pg.Surface]
        self.characters: dict[str, CharacterSprites]

        self.level_display: LevelDisplay
        self.scaled_ui: dict[str, pg.Surface]
        self.ui_fonts: dict[str, pg.font.Font]

        self.menu_renders: dict[str, MenuRender]

        self.load_menu_assets()
        self.load_level_assets()
        self.load_characters_sprites()

    # _________________________________________________________________________
    #                        GAME STATE-RELATED METHODS
    # _________________________________________________________________________

    def startup(self, menues: dict[str, Menu]) -> None:
        """Does every action needed to correctly scale the game based on the
        current window size.

        Takes a dict of menues in argument to create its own version with
        MenuRenders objects.
        """
        self.scale_level_ui()

        holder: PlaceHolder = self.scale_menu_holders(
            (0.8, 0.075), (0.12, 0.12, 0.76, 0.76))
        from_top: int = self.control.interface.get_height() // 8
        level_end: MenuRender = self.init_menu(
            holder, menues["victory"], from_top)

        self.menu_renders = {
            "pause": self.init_menu(self.scale_menu_holders(), menues["pause"],
                                    from_top),
            "cheats": self.init_menu(holder, menues["cheats"], from_top),
            "victory": level_end,
            "defeat": level_end,
            "end": self.init_menu(holder, menues["end"], from_top)}

    def cleanup(self) -> None:
        """Deletes attributes that are scaled based on the current window's
        size, in case it changes later on.
        """
        del self.menu_renders
        del self.level_display
        del self.scaled_ui
        del self.ui_fonts

    def update_level(self, level: Level) -> None:
        """Takes a new Level object in argument to replace the level_display
        attribute with a newly created one.
        """
        self.level_display = LevelDisplay(self, level)

    def change_menu(self, menu: str) -> None:
        """For a menu which name is given as argument, pre-renders all its
        options using its dedicated method. To call when a menu is accessed
        in case some of its values has changed.
        """
        self.menu_renders[menu].pre_render_all_options(self.control.dialogs)

    def update_menu(self, menu: str, index: int) -> None:
        """For a menu and option index, pre-render its text using the
        MenuRender method, for cases when GameState has to ponctually
        change displayed values or options without the user's input.
        """
        self.menu_renders[menu].pre_render_option(self.control.dialogs, index)

    # _________________________________________________________________________
    #                        ASSETS-LOADING METHODS
    # _________________________________________________________________________

    def load_level_assets(self) -> None:
        """Calls load_theme_assets to load up all level-themed assets, then
        loads up the level interface's sprites to place them in the interface
        attribute.
        """
        self.themed_assets = {}
        for theme in ("grassy", "dungeon"):
            self.load_theme_sprites(theme)
        level_ui_sheet: SpriteSheet = SpriteSheet(
            "pacman/assets/interface/life_and_energy.png")
        self.interface = {
            "level_ui": level_ui_sheet.get_sprite((0, 0), (640, 72)),
            "life_bar": level_ui_sheet.get_sprite((498, 94), (30, 21)),
            "life_bar_s": level_ui_sheet.get_sprite((494, 94), (2, 21)),
            "life_bar_e": level_ui_sheet.get_sprite((530, 94), (2, 21)),
            "super_bar": level_ui_sheet.get_sprite((537, 94), (85, 14))}

    def load_characters_sprites(self) -> None:
        """For every character, loads their sprites for each directions
        and modes using nested functions.
        """
        normal_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/skellies_premade_1.png")
        super_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/skellies_premade_2.png")
        pacman_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/example_characters.png")

        def get_frames(coords: tuple[int, int], sheet: SpriteSheet
                       ) -> list[pg.Surface]:
            """Gets sprites in a line from a given starting point and on a
            SpriteSheet object, returning them in a list of pygame.Surface.
            """
            return [
                sheet.get_sprite((coords[0] + 16 * index, coords[1]), (16, 16))
                for index in range(3)]

        def load_sprites(coords: tuple[int, int], sheet: SpriteSheet
                         ) -> dict[str, list[pg.Surface]]:
            """For coordinates on a given SpriteSheet, recovers frames for
            the four directions a character can face, and return them in a
            dict.
            """
            return {
                    "UP": get_frames((coords[0], coords[1] + 48), sheet),
                    "RIGHT": get_frames((coords[0], coords[1] + 32), sheet),
                    "LEFT": get_frames((coords[0], coords[1] + 16), sheet),
                    "DOWN": get_frames((coords[0], coords[1]), sheet)}

        pacman_pos: tuple[int, int] = (5 * 16 * 3, 4 * 16 * 4)
        sheet_pos: dict[str, tuple[int, int]] = {
            "Blinky": (10 * 16 * 3, 2 * 16 * 4),
            "Pinky": (8 * 16 * 3, 14 * 16 * 4),
            "Inky": (9 * 16 * 3, 29 * 16 * 4),
            "Clyde": (0, 0)}
        self.characters = {
            "Pacman": {"normal": load_sprites(pacman_pos, pacman_sht),
                       "super": load_sprites(pacman_pos, pacman_sht)}}
        for name, coords in sheet_pos.items():
            self.characters.update({
                name: {"normal": load_sprites(coords, normal_sht),
                       "super": load_sprites(coords, super_sht)}})

    def load_theme_sprites(self, theme: str) -> None:
        """Using a string, loads all theme-related sprites to make levels.
        This includes cells floor, borders and walls, decorations, gums and
        supergums. Place everything in the themed_assets dict attribute.
        """
        sheet: SpriteSheet = SpriteSheet(
            "pacman/assets/level/" + theme + "_tiles_sheet.png")
        tile_sprites: dict[str, pg.Surface] = {
            "n_wall": sheet.get_sprite((64, 0), (16, 16)),
            "s_wall": sheet.get_sprite((80, 0), (16, 16)),
            "e_wall": sheet.get_sprite((96, 0), (16, 16)),
            "w_wall": sheet.get_sprite((112, 0), (16, 16)),
            "nw_angle": sheet.get_sprite((64, 16), (16, 16)),
            "se_angle": sheet.get_sprite((80, 16), (16, 16)),
            "ne_angle": sheet.get_sprite((96, 16), (16, 16)),
            "sw_angle": sheet.get_sprite((112, 16), (16, 16))}

        def cell_borders(borders: list[str]) -> pg.Surface:
            cell: pg.Surface = new_surface((16, 16))
            cell.blits([(tile_sprites[border], (0, 0)) for border in borders])
            return cell

        binary_cell_borders: list[pg.Surface] = [
            cell_borders(["nw_angle", "se_angle", "ne_angle", "sw_angle"]),
            cell_borders(["n_wall", "se_angle", "sw_angle"]),
            cell_borders(["e_wall", "nw_angle", "sw_angle"]),
            cell_borders(["n_wall", "e_wall", "sw_angle"]),
            cell_borders(["s_wall", "nw_angle", "ne_angle"]),
            cell_borders(["n_wall", "s_wall"]),
            cell_borders(["e_wall", "s_wall", "nw_angle"]),
            cell_borders(["n_wall", "e_wall", "s_wall"]),
            cell_borders(["w_wall", "ne_angle", "se_angle"]),
            cell_borders(["w_wall", "n_wall", "se_angle"]),
            cell_borders(["w_wall", "e_wall"]),
            cell_borders(["n_wall", "e_wall", "w_wall"]),
            cell_borders(["s_wall", "w_wall", "ne_angle"]),
            cell_borders(["n_wall", "s_wall", "w_wall"]),
            cell_borders(["e_wall", "s_wall", "w_wall"]),
            cell_borders(["n_wall", "s_wall", "w_wall", "e_wall"])]

        paths_and_walls: dict[str, pg.Surface] = {
            "ground_surface": sheet.get_sprite((0, 0), (64, 64)),
            "wall": sheet.get_sprite((64, 32), (16, 16)),
            "small_wall": sheet.get_sprite((64, 32), (8, 16)),
            "down_wall": sheet.get_sprite((80, 32), (16, 32)),
            "small_down_wall": sheet.get_sprite((80, 32), (8, 32)),
            "h_path": new_surface((8, 16)),
            "v_path": new_surface((16, 8))}
        paths_and_walls["h_path"].blits([
            (paths_and_walls["ground_surface"], (0, 0)),
            (tile_sprites["n_wall"], (0, 0)),
            (tile_sprites["s_wall"], (0, 0))])
        paths_and_walls["v_path"].blits([
            (paths_and_walls["ground_surface"], (0, 0)),
            (tile_sprites["e_wall"], (0, 0)),
            (tile_sprites["w_wall"], (0, 0))])

        decorations: list[pg.Surface] = [
            sheet.get_sprite((coords), (16, 16)) for coords in (
                (128, 0), (144, 0), (128, 16), (144, 16))]

        gum: list[pg.Surface] = [new_surface((16, 16))] * 3
        pg.draw.circle(gum[0], pg.Color(255, 255, 255), (8, 8), 1.2)

        sup_gum_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/" + theme + "_sup_gum.png")
        sup_gum: list[pg.Surface] = []
        for x in range(3):
            sup_gum.append(sup_gum_sht.get_sprite((x * 192, 192), (192, 192)))

        self.themed_assets.update({theme: {
            "binary_cell_borders": binary_cell_borders,
            "paths_and_walls": paths_and_walls,
            "decorations": decorations,
            "gum": gum, "sup_gum": sup_gum}})

    # _________________________________________________________________________
    #                      SCALING AND RENDERING METHODS
    # _________________________________________________________________________

    def scale_level_ui(self) -> None:
        """Scale all elements of the level's interface to the current window.
        Places the result in the scaled_ui, ui_fonts and ui_styles attributes
        to be used by the LevelDisplay.
        """
        ui_h: int = int(self.control.interface.get_height() * 0.15)
        ui_w: int = int(self.control.interface.get_width())
        self.scaled_ui = {
            "level_ui": pg.transform.scale(
                self.interface["level_ui"], (ui_w, ui_h)),
            "super_bar": pg.transform.scale(
                self.interface["super_bar"], (ui_h * 1.19, ui_h * 0.19))}
        self.ui_fonts = {
            "level": pg.font.Font(self.font_path, int(ui_h * 0.45)),
            "score": pg.font.Font(self.font_path, int(ui_h * 0.45)),
            "timer": pg.font.Font(self.font_path, int(ui_h * 0.32))}
        self.ui_fonts["level"].set_bold(True)
        self.ui_fonts["timer"].set_bold(True)
        color: pg.Color = pg.Color(255, 255, 255)
        self.ui_styles: dict[str, Style] = {
            "level": Style(
                color, self.ui_fonts["level"], new_surface(),
                pg.Rect(ui_h * 0.194, ui_h * 0.194, ui_h * 0.76, ui_h * 0.58),
                int(ui_h * 0.35)),
            "score": Style(
                color, self.ui_fonts["score"], new_surface(),
                pg.Rect(ui_h * 1.08, ui_h * 0.194, ui_h * 2.33, ui_h * 0.58),
                int(ui_h * 0.35)),
            "timer": Style(
                color, self.ui_fonts["timer"], new_surface(),
                pg.Rect(ui_h * 3.9, ui_h * 0.2, ui_h * 1.06, ui_h * 0.56),
                int(ui_h * 0.27))}

    def draw(self, game_state: str) -> None:
        """Based on the given game_state, calls the draw method of either the
        LevelDisplay, or the current menu.
        """
        self.control.interface.fill((71, 71, 71))
        if game_state == "level":
            self.level_display.draw()
        if game_state in self.menu_renders.keys():
            menu_render: MenuRender = self.menu_renders[game_state]
            menu_render.pre_render_option(self.control.dialogs)
            menu_render.draw_vertical_options()
        self.control.screen.blit(
            self.control.interface, self.control.interface_rect)
