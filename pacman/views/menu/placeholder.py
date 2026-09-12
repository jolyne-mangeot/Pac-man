
import pygame as pg


def new_surface(size: tuple[int, int] = (0, 0), alpha: int = 0,
                color: pg.Color = pg.Color(0, 0, 0)) -> pg.Surface:
    """Returns a new pygame.Surface object based on the given arguments.
    The color argument will be used to fill in the surface, and the alpha
    will be this color's. An alpha of 0 means the surface will be completely
    transparent.
    """
    surface: pg.Surface = pg.Surface(size, pg.SRCALPHA)
    surface.fill((color[0], color[1], color[2], alpha))
    return surface


def render_word(style: Style, word: str, margin: int = 1) -> pg.Surface:
    """Returns a pygame.Surface containing a rendered text based on a Style
    object, to apply a font, letter spacing and color. The text should be
    approximately centered, but a font with letters of different width may
    sometimes look weird.
    """
    render_width: int = style.letter_spacing * (len(word) + margin)
    surface: pg.Surface = new_surface(
        (render_width, style.text_rect.height), 0)
    for index, letter in enumerate(word):
        letter_render: pg.Surface = style.font.render(
            letter, True, style.color)
        letter_rect: pg.Rect = letter_render.get_rect(midleft=(
            style.letter_spacing * index, int(style.text_rect.height / 2)))
        surface.blit(letter_render, letter_rect)
    return surface


class Style:
    """Class Style

    #### Description:
    Class used by PlaceHolder to display texts with a custom font, color,
    graphical background and set coordinates.

    Attributes:
    - color: pg.Color => pygame Color object used to later render text
    - font: pg.font.Font => pygame Font object used to render text
    - text_rect: pg.Rect => pygame Rect containing coordinates and dimensions
    to later place text in the PlaceHolder
    - letter_spacing: int => space in pixels between each letter of the text
    - graphic: pg.Surface => pygame Surface, either a color shape or image
    """
    def __init__(
            self, color: pg.Color = pg.Color(0, 0, 0),
            font: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            graphic: pg.Surface = new_surface((250, 30), 0),
            text_rect: pg.Rect = pg.Rect(10, 5, 230, 20),
            letter_spacing: int = 8) -> None:
        """Instantiate method for a PlaceHolder object, all attributes have
        default values.
        """
        self.color: pg.Color = color
        self.font: pg.font.Font = font
        self.text_rect: pg.Rect = text_rect
        self.letter_spacing: int = letter_spacing
        self.graphic: pg.Surface = graphic


class PlaceHolder:
    """Class PlaceHolder

    #### Description:
    Class used by the display, including the MenuRender class, to display
    texts in different Styles. Takes a list of Style object as parameter
    and can pre-render a list of text in all of these styles for later use.
    Automatically place each text on the Style's graphic and surface to try and
    space them evenly.

    ### Attribute:
    - styles: list[Style] => all styles in which the texts will be pre-rendered

    ### Methods:
    - pre_render => returns a list of tuple of pygame Surface and Rect to
    be directly blit onto the screen
    - render_texts => blit each text that needs to be placed on the Style's
    surface by spacing them evenly
    """
    def __init__(
            self, styles: list[Style] = [Style(), Style(), Style()]) -> None:
        self.styles: list[Style] = styles

    def pre_render(self, texts: list[str], visible: bool = True
                   ) -> list[tuple[pg.Surface, pg.Rect]]:
        """Pre-renders the option given as argument in three states: picked,
        deselected and selected, each with their associated fonts and colors,
        then returns a  list of tuple for each state, as a tuple of pygame
        Surface and Rect.
        """
        if visible is False:
            return [
                (pg.Surface((0, 0)), pg.Rect(0, 0, 0, 0)) for _ in self.styles]
        renders: list[tuple[pg.Surface, pg.Rect]] = []
        for style in self.styles:
            graphic: pg.Surface = style.graphic.copy()
            for index, text in enumerate(texts):
                self.render_texts(graphic, style, text, index, len(texts))
            renders.append((graphic, graphic.get_rect()))
        return renders

    def render_texts(
            self, surface: pg.Surface, style: Style, text: str,
            position: int, total_slots: int) -> None:
        """Blits a text on the given surface using a style and a positional
        index. Tries to place the text on the surface based on the maximum
        index (total_slots) so all the texts rendered are ultimately evenly
        spaced.
        """
        text_render: pg.Surface = render_word(style, text)
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
