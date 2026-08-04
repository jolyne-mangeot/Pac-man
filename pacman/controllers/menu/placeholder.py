
import pygame as pg


def prefilled_surface(size: tuple[int, int], alpha: int,
                      color: pg.Color = pg.Color(0, 0, 0)) -> pg.Surface:
    surface: pg.Surface = pg.Surface(size, pg.SRCALPHA)
    surface.fill((color[0], color[1], color[2], alpha))
    return surface


class Style:
    def __init__(
            self, color: pg.Color = pg.Color(0, 0, 0),
            font: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            graphic: pg.Surface = prefilled_surface((250, 30), 0),
            text_rect: pg.Rect = pg.Rect(10, 5, 230, 20)) -> None:
        self.color: pg.Color = color
        self.font: pg.font.Font = font
        self.text_rect: pg.Rect = text_rect
        self.graphic: pg.Surface = graphic


class PlaceHolder:
    def __init__(
            self, styles: list[Style] = [Style()]) -> None:
        self.styles: list[Style] = styles

    def pre_render(self, texts: list[str]
                   ) -> list[tuple[pg.Surface, pg.Rect]]:
        """Pre-renders the option given as argument in three states: picked,
        deselected and selected, each with their associated fonts and colors,
        then returns a tuple of each state, as a tuple of pygame Surface and
        Rect.
        """
        renders: list[tuple[pg.Surface, pg.Rect]] = []
        for style in self.styles:
            graphic: pg.Surface = style.graphic.copy()
            for index, text in enumerate(texts):
                self.render_text(graphic, style, text, index, len(texts))
            renders.append((graphic, graphic.get_rect()))
        return renders

    def render_text(
            self, surface: pg.Surface, style: Style, text: str,
            position: int, total_slots: int) -> None:
        text_render: pg.Surface = style.font.render(text, True, style.color)
        text_rect: pg.Rect = text_render.get_rect()
        if total_slots == 1:
            text_rect.center = style.text_rect.center
        elif position == 0:
            text_rect.midleft = style.text_rect.midleft
        elif position == total_slots - 1:
            text_rect.midright = style.text_rect.midright
        else:
            text_rect.center = (int(style.text_rect.width / total_slots),
                                style.text_rect.centery)
        surface.blit(text_render, text_rect)
