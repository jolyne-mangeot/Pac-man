
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
        x: int = pos[1]
        y: int = pos[0]

        rect: pg.Rect = pg.Rect(x, y, *size)
        image: pg.Surface = pg.Surface(size, pg.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pg.RLEACCEL)

        return image


class Display:
    """Class Display

    Parent class of all State displaying classes. Contains attributes and
    methods common to multiple states to avoid repetitions.
    """
    def __init__(self, control: Control) -> None:
        """Init method for all Display subclasses, takes a Control object to
        add as attribute.
        """
        self.control: Control = control

    def load_main_menues(self) -> None:
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
        self.deselect_hold: pg.Surface = sheet.get_sprite((60, 0), (122, 28))
        self.select_hold: pg.Surface = sheet.get_sprite((0, 0), (122, 28))
        self.picked_hold: pg.Surface = sheet.get_sprite((30, 0), (122, 28))
        self.sounds: dict[str, pg.mixer.Sound] = {
            "cursor_pick": pg.mixer.Sound("pacman/assets/sfx/ui/Confirm.wav"),
            "cursor_unpick": pg.mixer.Sound("pacman/assets/sfx/ui/Close.wav"),
            "cursor_move": pg.mixer.Sound("pacman/assets/sfx/ui/Cursor.wav"),
            "option_update": pg.mixer.Sound("pacman/assets/sfx/ui/Open.wav"),
            "option_activate": pg.mixer.Sound(
                "pacman/assets/sfx/ui/Purchase.wav"),
            "option_input_write": pg.mixer.Sound(
                "pacman/assets/sfx/ui/Confirm.wav"),
            "option_input_erase": pg.mixer.Sound(
                "pacman/assets/sfx/ui/Close.wav"),
            "program_quit": pg.mixer.Sound("pacman/assets/sfx/ui/Equip.wav")
        }

    def scale_holders(
            self, holder_size_factor: tuple[float, float],
            text_rect_factor: tuple[float, float, float, float]) -> None:
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

        plain_font: pg.font.Font = pg.font.Font(
            "pacman/assets/fonts/dogica.otf",
            int(screen_h * 0.03))
        picked_font: pg.font.Font = pg.font.Font(
            "pacman/assets/fonts/dogica.otf",
            int(screen_h * 0.03))
        picked_font.set_bold(True)

        des_style: Style = Style(
            font=plain_font, graphic=self.deselect_hold, text_rect=rect,
            letter_spacing=int(screen_h * 0.023))
        sel_style: Style = Style(
            font=plain_font, graphic=self.select_hold, text_rect=rect,
            letter_spacing=int(screen_h * 0.023))
        pik_style: Style = Style(
            font=picked_font, graphic=self.picked_hold, text_rect=rect,
            letter_spacing=int(screen_h * 0.023))

        self.place_holder: PlaceHolder = PlaceHolder([
            des_style, sel_style, pik_style])

    def init_menu(self, menu: Menu, from_top: int = -1) -> None:
        """Method instantiating a MenuRender object and taking it as attribute.
        Pre-enter the control's interface and dialogs, the display's place
        holder and inserts the arguments menu and from_top, which is the only
        changing parameter between different calls.
        """
        self.menu_render: MenuRender = MenuRender(
            self.control.interface, menu, from_top=from_top,
            holder=self.place_holder, dialogs=self.control.dialogs)

    def mixer(self, action: str) -> None:
        """Plays a sound from the sounds dict attribute if the given action
        exists in the sfx control channel.
        """
        if self.sounds.get(action, None) is not None:
            self.control.sfx_channel.play(self.sounds[action])
