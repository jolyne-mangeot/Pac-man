
from typing import TypedDict, cast, Literal
from random import randint as rand, choice

import pygame as pg

from .display import Display, SpriteSheet
from pacman.controllers import Control
from pacman.models import (
    Level, OPPOSITE_DIRECTION, Movements, Directions, Entity)
from pacman.views import Style, render_word, new_surface


class LevelDisplay:
    def __init__(self, display: GameDisplay, level: Level) -> None:
        self.display: GameDisplay = display
        self.level: Level = level

        self.maze_surf: pg.Surface
        self.characters: dict[str, CharacterSprites]
        self.life_bar: pg.Surface

        self.cell_size: int
        self.cell_gap: int
        self.gum: list[pg.Surface]
        self.sup_gum: list[pg.Surface]

        self.render_maze()
        self.scale_characters()
        self.scale_ui()

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

        self.maze_surf = new_surface(self.coords(
            self.level.map.width, self.level.map.height + 1, -0.5, -1))

        assets: LevelTheme = self.display.themed_assets[self.level.theme]
        self.gum = [pg.transform.scale(
            gum, (cell_size, cell_size)) for gum in assets["gum"]]
        sup_size: int = int(cell_size * 1)
        self.sup_gum = [pg.transform.scale(
            sup_gum, (sup_size, sup_size)) for sup_gum in assets["sup_gum"]]

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

                cell: pg.Surface = new_surface((16, 16))
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

    def scale_ui(self) -> None:
        ui_size: tuple[int, int] = (
            self.display.scaled_ui["level_ui"].get_size())
        bar_w: int = int(ui_size[1] * 2.92)
        bar_h: int = int(ui_size[1] * 0.29)
        life_gap: int = int((self.level.max_lives - 1) / bar_w * 100)
        life_size: int = int((bar_w - life_gap) / self.level.max_lives)
        life_part: pg.Surface = pg.transform.scale(
            self.display.interface["life_bar"], (life_size, bar_h))
        bar_start: pg.Surface = pg.transform.scale(
            self.display.interface["life_bar_s"], (ui_size[1] * 0.02, bar_h))
        bar_end: pg.Surface = pg.transform.scale(
            self.display.interface["life_bar_e"], (ui_size[1] * 0.02, bar_h))
        blits: list[tuple[pg.Surface, pg.Rect]] = [
            (bar_start, pg.Rect(0, 0, 0, 0)),
            (bar_end, bar_end.get_rect(topright=(bar_w, 0)))]
        for i in range(self.level.max_lives):
            blits.insert(0, (
                life_part, pg.Rect((life_size * i) + (life_gap * i), 0, 0, 0)))
        self.life_bar = new_surface((bar_w, bar_h))
        self.life_bar.blits(blits)

    def render_entity(
            self, name: str, char: Entity, direction: Directions
            ) -> tuple[pg.Surface, pg.Rect]:
        coords: tuple[int, int] = self.coords(*char.pos)
        origin: tuple[int, int] = Movements[
            OPPOSITE_DIRECTION[direction].name].value
        offset: int = 0
        if char.direction.value != 15:
            offset = int(
                (char.current_speed - self.level.char_anim[name])
                * (self.cell_size + self.cell_gap)
                / char.current_speed)
        position: tuple[int, int] = (
            coords[0] + (origin[0] * offset),
            coords[1] + (origin[1] * offset))
        mode: str = "super" if char.is_super else "normal"
        frame: int = int(
            self.level.char_anim[name] * 3 / char.current_speed) % 3
        return (
            self.characters[name][cast(Literal["normal", "super"], mode)][
                direction.name][frame],
            pg.Rect(*position, self.cell_size, self.cell_size))

    def render_interface(self) -> tuple[pg.Surface, pg.Rect]:
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
        timer: pg.Surface = render_word(
            self.display.ui_styles["timer"],
            f"{time // 60:02d}:{time % 60:02d}", 0)

        life_size: tuple[int, int] = self.life_bar.get_size()
        life_bar: tuple[pg.Surface, pg.Rect, pg.Rect] = (
            self.life_bar, pg.Rect(ui_h * 5.66, ui_h * 0.175, 0, 0), pg.Rect(
                0, 0, (life_size[0] - (self.level.max_lives - self.level.lives)
                       * life_size[0] / self.level.max_lives),
                life_size[1]))

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

        direction: Directions = next(dir for dir in (
            self.level.pacman.direction, self.level.pacman.next_direction,
            Directions.DOWN) if dir.value != 15)
        if self.level.pacman.is_alive is True:
            visual_elements.append(self.render_entity(
                "Pacman", self.level.pacman, direction))
        for name, ghost in self.level.ghosts.items():
            direction = (ghost.direction if ghost.direction.value
                         != 15 else Directions.DOWN)
            if ghost.is_alive is True:
                visual_elements.append(self.render_entity(
                    name, ghost, direction))

        maze_surf.blits(visual_elements)
        game_surf.fill((15, 15, 15))
        game_surf.blit(maze_surf, maze_surf.get_rect(
            center=game_surf.get_rect().center))
        control_interface.blits([
            (game_surf, (0, int(control_interface.get_height() * 0.15))),
            self.render_interface()])

        self.display.control.screen.blit(
            control_interface,
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
        self.themed_assets: dict[str, LevelTheme]
        self.interface: dict[str, pg.Surface]
        self.scaled_ui: dict[str, pg.Surface]
        self.ui_fonts: dict[str, pg.font.Font]
        self.characters: dict[str, CharacterSprites]
        self.level_display: LevelDisplay
        self.load_level_assets()
        self.load_characters_sprites()

    def startup(self) -> None:
        self.scale_level_ui()

    def cleanup(self) -> None:
        del self.level_display
        del self.scaled_ui
        del self.ui_fonts

    def load_level_assets(self) -> None:
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

    def scale_level_ui(self) -> None:
        ui_h: int = int(self.control.interface.get_height() * 0.15)
        ui_w: int = int(self.control.interface.get_width())
        self.scaled_ui = {
            "level_ui": pg.transform.scale(
                self.interface["level_ui"], (ui_w, ui_h)),
            "super_bar": pg.transform.scale(
                self.interface["super_bar"], (ui_h * 1.19, ui_h * 0.19))}
        self.ui_fonts = {
            "level": pg.font.Font(
                "pacman/assets/fonts/dogica.otf", int(ui_h * 0.45)),
            "score": pg.font.Font(
                "pacman/assets/fonts/dogica.otf", int(ui_h * 0.45)),
            "timer": pg.font.Font(
                "pacman/assets/fonts/dogica.otf", int(ui_h * 0.32))}
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

    def load_characters_sprites(self) -> None:
        normal_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/skellies_premade_1.png")
        super_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/skellies_premade_2.png")
        pacman_sht: SpriteSheet = SpriteSheet(
            "pacman/assets/level/example_characters.png")

        def get_frames(coords: tuple[int, int], sheet: SpriteSheet
                       ) -> list[pg.Surface]:
            return [
                sheet.get_sprite((coords[0] + 16 * index, coords[1]), (16, 16))
                for index in range(3)]

        def load_sprites(coords: tuple[int, int], sheet: SpriteSheet
                         ) -> dict[str, list[pg.Surface]]:
            return {
                    "UP": get_frames((coords[0], coords[1] + 48), sheet),
                    "RIGHT": get_frames((coords[0], coords[1] + 32), sheet),
                    "LEFT": get_frames((coords[0], coords[1] + 16), sheet),
                    "DOWN": get_frames((coords[0], coords[1]), sheet)}

        sheet_coords: dict[str, tuple[int, int]] = {
            "Blinky": (10 * 16 * 3, 2 * 16 * 4),
            "Pinky": (8 * 16 * 3, 14 * 16 * 4),
            "Inky": (0, 0),
            "Clyde": (0, 0)}
        pacman_coords: tuple[int, int] = (5 * 16 * 3, 4 * 16 * 4)
        self.characters = {
            "Pacman": {"normal": load_sprites(pacman_coords, pacman_sht),
                       "super": load_sprites(pacman_coords, pacman_sht)}}
        for name, coords in sheet_coords.items():
            self.characters.update({
                name: {"normal": load_sprites(coords, normal_sht),
                       "super": load_sprites(coords, super_sht)}})

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
            cell: pg.Surface = new_surface((16, 16))
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
            "gum": gum,
            "sup_gum": sup_gum}})

    def update_level(self, level: Level) -> None:
        self.level_display = LevelDisplay(self, level)

    def draw(self) -> None:
        self.level_display.draw()
