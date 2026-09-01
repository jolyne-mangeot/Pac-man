
from typing import TypedDict, cast, Literal
from random import randint as rand, choice

import pygame as pg

from pacman.controllers import Control
from pacman.models import Level
from .display import Display, SpriteSheet


class LevelDisplay:
    def __init__(self, display: GameDisplay, level: Level) -> None:
        self.display: GameDisplay = display
        self.level: Level = level

        self.maze_surf: pg.Surface
        self.characters: dict[str, CharacterSprites]

        self.cell_size: int
        self.cell_gap: int
        self.gum: list[pg.Surface]
        self.sup_gum: list[pg.Surface]

        self.render_maze()
        self.scale_characters()

    def coords(self, x: int, y: int, h_path: float = 0,
               v_path: float = 0) -> tuple[int, int]:
        return ((x * self.cell_size) + (x * self.cell_gap)
                + int(h_path * self.cell_size),
                (y * self.cell_size) + (y * self.cell_gap)
                + int(v_path * self.cell_size))

    def render_maze(self) -> None:
        maze_width: int
        maze_height: int
        if self.level.map.width > self.level.map.height * 1.7:
            maze_width = int(self.display.control.interface.get_width() * 0.98)
            maze_height = int(maze_width * self.level.map.height
                              / self.level.map.width * 0.98)
        else:
            maze_height = int(
                self.display.control.interface.get_height() * 0.82)
            maze_width = int(maze_height * self.level.map.width
                             / self.level.map.height * 0.98)

        self.cell_size = maze_width // int(self.level.map.width * 1.5)
        cell_size = self.cell_size
        self.cell_gap = int(cell_size // 2.3)
        cell_gap = self.cell_gap

        self.maze_surf = self.display.new_surface(self.coords(
            self.level.map.width, self.level.map.height + 1, -0.5, -1))

        assets: LevelTheme = self.display.themed_assets[self.level.theme]
        self.gum = [pg.transform.scale(
            gum, (cell_size, cell_size)) for gum in assets["gum"]]
        self.sup_gum = [pg.transform.scale(
            sup_gum, (cell_size, cell_size)) for sup_gum in assets["sup_gum"]]

        p_a_w: dict[str, pg.Surface] = assets["paths_and_walls"]
        scale: dict[str, pg.Surface] = {
            "s_wall": pg.transform.scale(
                p_a_w["small_wall"], (cell_gap, cell_size)),
            "s_down_wall": pg.transform.scale(
                p_a_w["small_down_wall"], (cell_gap, cell_size * 2)),
            "h_path": pg.transform.scale(
                p_a_w["h_path"], (cell_gap, cell_size)),
            "v_path": pg.transform.scale(
                p_a_w["v_path"], (cell_size, cell_gap)),
            "wall": pg.transform.scale(p_a_w["wall"], (cell_size, cell_size)),
            "down_wall": pg.transform.scale(
                p_a_w["down_wall"], (cell_size, cell_size * 2))}

        decorations: list[pg.Surface] = [pg.transform.scale(
            prop, (cell_size, cell_size)) for prop in assets["decorations"]]

        for y in range(self.level.map.height):
            for x in range(self.level.map.width):
                walls: int = self.level.map.map[x][y].walls

                cell: pg.Surface = self.display.new_surface((16, 16))
                cell.blits([
                    (p_a_w["ground_surface"], (rand(-48, 0), rand(-48, 0))),
                    (assets["binary_cell_borders"][walls], (0, 0))])

                elems: list[tuple[pg.Surface, tuple[int, int]]] = [(
                    pg.transform.scale(cell, (cell_size, cell_size)),
                    self.coords(x, y))]
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
                        elems.append((choice(decorations), self.coords(x, y)))

                self.maze_surf.blits(elems)

    def scale_characters(self) -> None:
        self.characters = {}
        for char, sprites in self.display.characters.items():
            self.characters.update({char: {"normal": {}, "super": {}}})
            for mode in ("normal", "super"):
                for dir, frames in sprites[mode].items():
                    self.characters[char][mode].update({
                        dir: [pg.transform.scale(
                            frame, (self.cell_size, self.cell_size))
                            for frame in frames]})

    def draw(self) -> None:
        self.display.control.screen.fill((0, 0, 0))
        game_surf: pg.Surface = self.display.new_surface((
            self.display.control.interface.get_width(),
            int(self.display.control.interface.get_height() * 0.85)))

        maze_surf: pg.Surface = self.maze_surf.copy()
        visual_elements: list[tuple[pg.Surface, pg.Rect]] = []
        # mode: str = "super" if self.level.super_mode else "normal"
        # dir: dict[int, str] = {
        #     1: "north", 2: "east",
        #     3: "south", 4: "west"}
        # visual_elements.extend([(
        #     self.characters[name][mode][dir[char.direction]][self.level.anim_tick],
        #     pg.Rect(*self.coords(char.pos), self.cell_size, self.cell_size))
        #     for name, char in self.level.ghosts.items() if char.is_alive
        # ])
        # visual_elements.extend([(
        #     self.gum[self.level.anim_tick],
        #     pg.Rect(*self.coords(gum), self.cell_size, self.cell_size))
        #     for gum in self.level.map.simple_gums])
        # visual_elements.extend([(
        #     self.sup_gum[self.level.anim_tick],
        #     pg.Rect(*self.coords(sup_gum), self.cell_size, self.cell_size))
        #     for sup_gum in self.level.map.super_gums])
        maze_surf.blits(visual_elements)
        game_surf.fill((15, 15, 15))
        game_surf.blit(maze_surf, maze_surf.get_rect(
            center=game_surf.get_rect().center))
        self.display.control.interface.blit(game_surf, (
            0, int(self.display.control.interface.get_height() * 0.15)))

        self.display.control.screen.blit(
            self.display.control.interface,
            self.display.control.interface_rect)


class LevelTheme(TypedDict):
    binary_cell_borders: list[pg.Surface]
    paths_and_walls: dict[str, pg.Surface]
    decorations: list[pg.Surface]

    gum: list[pg.Surface]
    sup_gum: list[pg.Surface]


class CharacterSprites(TypedDict):
    normal: dict[str, list[pg.Surface]]
    super: dict[str, list[pg.Surface]]


class GameDisplay(Display):
    def __init__(self, control: Control) -> None:
        super().__init__(control)
        self.level_display: LevelDisplay
        self.load_level_assets()
        self.load_characters_sprites()

    def startup(self) -> None:
        pass

    def cleanup(self) -> None:
        del self.level_display

    def load_level_assets(self) -> None:
        self.themed_assets: dict[str, LevelTheme] = {}
        for theme in ("grassy", "dungeon"):
            self.load_theme_sprites(theme)

    def load_characters_sprites(self) -> None:
        normal_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/skellies_premade_1.png")
        super_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/skellies_premade_2.png")

        def get_frames(coords: tuple[int, int], sheet: SpriteSheet
                       ) -> list[pg.Surface]:
            return [
                sheet.get_sprite(
                    (coords[0], coords[1] + 16 * index), (16, 16), -1)
                for index in range(3)]

        def load_sprites(coords: tuple[int, int]) -> CharacterSprites:
            sprites: CharacterSprites = {"normal": {}, "super": {}}
            for mode, sheet in zip(
                    ("normal", "super"), (normal_sht, super_sht)):
                sprites[cast(Literal["normal", "super"], mode)].update({
                    "north": get_frames((coords[0], coords[1]), sheet),
                    "east": get_frames((coords[0] + 32, coords[1]), sheet),
                    "west": get_frames((coords[0] + 16, coords[1]), sheet),
                    "south": get_frames((coords[0] + 48, coords[1]), sheet)})
            return sprites

        sheet_coords: dict[str, tuple[int, int]] = {
            "Pacman": (0, 0),
            "Blinky": (10 * 16 * 3, 2 * 16 * 4),
            "Pinky": (8 * 16 * 3, 14 * 16 * 4),
            "Inky": (0, 0),
            "Clyde": (0, 0)}
        self.characters: dict[str, CharacterSprites] = {}
        for name, coords in sheet_coords.items():
            self.characters.update({name: load_sprites(coords)})

    def load_theme_sprites(self, theme: str) -> None:
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

        def create_cell_borders(borders: list[str]) -> pg.Surface:
            cell: pg.Surface = self.new_surface((16, 16))
            cell.blits([(tile_sprites[border], (0, 0)) for border in borders])
            return cell

        binary_cell_borders: list[pg.Surface] = [
            create_cell_borders(
                ["nw_angle", "se_angle", "ne_angle", "sw_angle"]),
            create_cell_borders(["n_wall", "se_angle", "sw_angle"]),
            create_cell_borders(["e_wall", "nw_angle", "sw_angle"]),
            create_cell_borders(["n_wall", "e_wall", "sw_angle"]),
            create_cell_borders(["s_wall", "nw_angle", "ne_angle"]),
            create_cell_borders(["n_wall", "s_wall"]),
            create_cell_borders(["e_wall", "s_wall", "nw_angle"]),
            create_cell_borders(["n_wall", "e_wall", "s_wall"]),
            create_cell_borders(["w_wall", "ne_angle", "se_angle"]),
            create_cell_borders(["w_wall", "n_wall", "se_angle"]),
            create_cell_borders(["w_wall", "e_wall"]),
            create_cell_borders(["n_wall", "e_wall", "w_wall"]),
            create_cell_borders(["s_wall", "w_wall", "ne_angle"]),
            create_cell_borders(["n_wall", "s_wall", "w_wall"]),
            create_cell_borders(["e_wall", "s_wall", "w_wall"]),
            create_cell_borders(["n_wall", "s_wall", "w_wall", "e_wall"])]

        paths_and_walls: dict[str, pg.Surface] = {
            "ground_surface": sheet.get_sprite((0, 0), (64, 64)),
            "wall": sheet.get_sprite((64, 32), (16, 16)),
            "small_wall": sheet.get_sprite((64, 32), (8, 16)),
            "down_wall": sheet.get_sprite((80, 32), (16, 32)),
            "small_down_wall": sheet.get_sprite((80, 32), (8, 32)),
            "h_path": self.new_surface((8, 16)),
            "v_path": self.new_surface((16, 8))}
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

        sup_gum_sheet: SpriteSheet = SpriteSheet(
            "pacman/assets/level/" + theme + "_sup_gum.png")
        sup_gum: list[pg.Surface] = []
        for y in range(3):
            for x in range(3):
                sup_gum.append(
                    sup_gum_sheet.get_sprite((x * 192, y * 192), (192, 192)))

        self.themed_assets.update({theme: {
            "binary_cell_borders": binary_cell_borders,
            "paths_and_walls": paths_and_walls,
            "decorations": decorations,
            "gum": sup_gum,
            "sup_gum": sup_gum}})

    def update_level(self, level: Level) -> None:
        self.level_display = LevelDisplay(self, level)

    def draw(self) -> None:
        self.control.screen.fill((0, 0, 255))
        self.level_display.draw()
