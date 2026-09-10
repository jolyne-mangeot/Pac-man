
import pygame as pg

from pacman.controllers import Control, Menu
from pacman.views import PlaceHolder, Style, MenuRender


class SpriteSheet:
    """Class SpriteSheet

    Can be instantiated with the path to an image to then create Pygame
    Surfaces from fractions of it.

    ### Attributes:
    - sheet: pygame.Surface => Surface of the whole image loaded from the
    file path in constructor argument

    ### Methods:
    - get_sprite => using a set of coordinates and dimensions, retrieve a
    surface from the sheet attribute to return a new surface
    """
    def __init__(self, filepath: str) -> None:
        """Loads the image from the file path as a sprite sheet."""
        self.sheet: pg.Surface = pg.image.load(filepath).convert_alpha()

    def get_sprite(self, pos: tuple[int, int], size: tuple[int, int],
                   colorkey: pg.Color | int | None = None) -> pg.Surface:
        """Use the position and size tuples from arguments to crop out a new
        surface from the sheet attribute.

        Uses the convert_alpha Surface method to apply the image's
        transparency, and, if the colorkey argument is not None, turns
        transparent all pixels in the surface corresponding to the color.
        If the argument is -1, uses the color of the top-left pixel instead.

        Returns the new surface.
        """
        rect: pg.Rect = pg.Rect(*pos, *size)
        image: pg.Surface = pg.Surface(size, pg.SRCALPHA, 32).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)

        return image


class Display:
    """Class Display

    Parent class of all State displaying classes. Contains attributes and
    methods common to multiple states to avoid repetitions.
    """
    font_path: str = "pacman/assets/fonts/dogica.otf"

    def __init__(self, control: Control) -> None:
        """Init method for all Display subclasses, takes a Control object to
        add as attribute.
        """
        self.control: Control = control

    def mixer(self, action: str) -> None:
        """Plays a sound from the sounds dict attribute if the given action
        exists in the sfx control channel.
        """
        if self.sounds.get(action, None) is not None:
            self.control.sfx_channel.play(self.sounds[action])

    # _________________________________________________________________________
    #                    COMMON METHODS TO MAIN MENUES
    # _________________________________________________________________________

    def load_menu_buttons(self) -> None:
        """Loads all necessary assets for the main and options menus and
        place them in self assigned attributes to be used later.

        Loads:
        - Sprites for the buttons from a sprite sheet as they can be rescaled
        as many times as needed, reducing file access
        - Sounds for the buttons navigation and other actions like the program
        ending
        """
        sheet: SpriteSheet = SpriteSheet(
            "pacman/assets/interface/text_holder.png")
        self.deselect_hold: pg.Surface = sheet.get_sprite((0, 60), (122, 28))
        self.select_hold: pg.Surface = sheet.get_sprite((0, 0), (122, 28))
        self.picked_hold: pg.Surface = sheet.get_sprite((0, 30), (122, 28))
        path: str = "pacman/assets/sfx/ui/"
        self.sounds: dict[str, pg.mixer.Sound] = {
            "cursor_pick": pg.mixer.Sound(path + "Confirm.wav"),
            "cursor_unpick": pg.mixer.Sound(path + "Close.wav"),
            "cursor_move": pg.mixer.Sound(path + "Cursor.wav"),
            "option_update": pg.mixer.Sound(path + "Open.wav"),
            "option_activate": pg.mixer.Sound(path + "Purchase.wav"),
            "option_input_write": pg.mixer.Sound(path + "Confirm.wav"),
            "option_input_erase": pg.mixer.Sound(path + "Close.wav"),
            "program_quit": pg.mixer.Sound(path + "Equip.wav")}

    def scale_menu_holders(
            self, holder_size_factor: tuple[float, float] = (0.3, 0.08),
            text_rect_factor: tuple[float, float, float, float]
            = (0.05, 0.05, 0.95, 0.95)) -> PlaceHolder:
        """Create a PlaceHolder using multiple instantiated Style objects and
        assign it to self for later display usage.

        Uses multiple scaling factors based on which state calls this method.
        """
        screen_h: int = self.control.screen.get_height()
        scale: tuple[int, int] = (
            int(screen_h * holder_size_factor[0]),
            int(screen_h * holder_size_factor[1]))
        self.deselect_hold = pg.transform.scale(self.deselect_hold, scale)
        self.select_hold = pg.transform.scale(self.select_hold, scale)
        self.picked_hold = pg.transform.scale(self.picked_hold, scale)

        rect: pg.Rect = pg.Rect(
            int(scale[0] * text_rect_factor[0]),
            int(scale[1] * text_rect_factor[1]),
            int(scale[0] * text_rect_factor[2]),
            int(scale[1] * text_rect_factor[3]))

        font_size: int = int(screen_h * 0.03)
        plain_font: pg.font.Font = pg.font.Font(self.font_path, font_size)
        picked_font: pg.font.Font = pg.font.Font(self.font_path, font_size)
        picked_font.set_bold(True)

        spacing: int = int(screen_h * 0.023)
        des_style: Style = Style(
            font=plain_font, graphic=self.deselect_hold, text_rect=rect,
            letter_spacing=spacing)
        sel_style: Style = Style(
            font=plain_font, graphic=self.select_hold, text_rect=rect,
            letter_spacing=spacing)
        pik_style: Style = Style(
            font=picked_font, graphic=self.picked_hold, text_rect=rect,
            letter_spacing=spacing)

        return PlaceHolder([des_style, sel_style, pik_style])

    def init_menu(self, place_holder: PlaceHolder, menu: Menu,
                  from_top: int = -1, from_left: int = -1, spacer: int = -1
                  ) -> MenuRender:
        """Method instantiating a MenuRender object and taking it as attribute.
        Pre-enter the control's interface and dialogs, the display's place
        holder and inserts the arguments menu and from_top, which is the only
        changing parameter between different calls.
        """
        return MenuRender(
            self.control.interface, menu,
            from_top=from_top, from_left=from_left, spacer=spacer,
            holder=place_holder, dialogs=self.control.dialogs)
