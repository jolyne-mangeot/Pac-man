### Navigating in interfaces

When designing and coding a user interface, joining a smooth navigation with practical features can always be given a great deal of thought.

Choosing which input performs which action, how options are displayed on screen and how they are modified, there's no limit to how these features are implemented, especially with each language, and each graphical library.

We chose Pygame for this project, which comes with its own set of modules and methods, obviously, and the way it was thought out often comes more as a constraint than a support in the making of an interface, depending on the ideas thought out.

### Creating a settings menu

A preferences menu, or settings menu, is the perfect example of a range of option that need to be modified in each their own way. Numeric sliders for the sound volumes, selections for set resolutions or languages, but also input for keybindings, it can easily become overwhelming to manage each type all at the same time.

And as multiple projects can have needs for different types of options, and a same game feature infinite menues and sub-menues, the key in finding the balance in autonomy and efficiency lies in expandable features and generalized behaviors.

<img src="Pygame Settings menu.png" align="right" width="500">
See on the right a bare settings menu. It features all listed-above examples of preferences options, action buttons to reset, apply or leave the settings, and a dummy text field for testing.

It shows where the cursor is, and, when the confirm key is pressed, allows the picking up of fields to modify their value.

For easier variety, it was decided not to accustom to mouse inputs, and controller inputs could be added without much difficulty.

### The Option class family

*file: "pacman/controllers/menu/utils.py"*

Prioritizing polyvalence and expandable features mean finding the way that organizes the code best to our way of thinking and working. In an object-oriented language, it's fast done by deriving a structural class into many that hold different goals, and ways to be interacted with. It also allows for subtle features to be coded in as it would always only impact the class we're working on, and not the main structure.

```python
from abc import ABC, abstractmethod
from functools import partial
from typing import Any

class Option(ABC):
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}) -> None:
        self.name: str = name
        self.text: str = text
        self.container: dict[str, Any] = container
        self.selectable: bool = True
        self.pickable: bool = True
        self.using_text_input: bool = False

    def __str__(self) -> str:
        if self.container.get(self.name, None) is not None:
            return self.text.format(
                value=str(self.container.get(self.name)).replace("_", " "))
        return self.text

    def activate(self) -> None:
        """Called when an option is picked, declared here for any Option
        subclass to be overridden with specialized behavior.
        """
        pass

    def deactivate(self) -> None:
        """Called when an option is let go of, declared here for any Option
        subclass to be overridden with specialized behavior.
        """
        pass

    @abstractmethod
    def input_event(
            self, action_key: str, named_key: str, text_input: str) -> Any:
        """Method called to pass down input to the Option object, as an action
		and/or a named_key, and a text_input, depending on the option's needs.
        """
        pass
```

This Option abstract class holds a lot of information and had far less attributes at first, but, as the reference to all other Option type classes, it's responsibility is to harmonize its subclasses attributes and methods so other parts of the code can be reduced and cleaned of the visual fog that would be taking every different type of option into account.

This means, for a menu holding different types of options, rather than checking the type of option the user has selected to handle inputs differently, the generalized structure of all Options subclasses allow to simply pass down information with less potential crashes or incompatibility.

The core of making the setting actually update with the user's input is the `self.container` attribute, of type `dict[str, Any]`. As one would know, in Python, complex objects and iterables can be passed to other classes and functions by reference, meaning all holders of the variable would always access it in the same memory spot, but for all other types like strings and integers, it would require additional work of returning values and making sure all entities have the most updated changes.

Using a dictionary solves this, first by passing any type of variable by reference, but also by preemptively grouping all the information together. This dictionary is what will be referred to as the container from now on.

Other attributes are more self-explanatory, but here a detailed list of what they do:

- `name:str` => name of the option. Can be used to identify a unique option, but, for most options, should correspond to the key of the value it should modify in the container. For the sfx volume slider, it would be `sfx_vol` (as the attribute in the Settings class seen [here](JSONModels)).
- `text: str` => text used to print the option. If the option's container contains a value with the option's name, it will be formatted into this text (ex: `f"{SFX Volume:<20}""{value}"` will format the int value from the container into the value slot).
- `selectable: bool` => useful for options that the cursor cannot move to and that will be skipped over during navigation like spacers or titles. Set to True by default.
- `pickable: bool` => useful for options that works punctually like a toggle, or one that simply executes a function. These still need to be selectable. Set to True by default.
- `using_text_input: bool` => used only by the input option for now, and to adapt to Pygame's inputs. The menu will pass down `pygame.TEXTINPUT` events down to the option if the flag is True, otherwise `pygame.KEYDOWN`.

#### Sliders

Not every option types included in the game will be explained here, so feel free to checkout their documentation strings for more details on how each work, but let's see one to illustrate specialized behaviors.

```python
# continuity of the Options class file

class SliderOption(Option):
    def __init__(
            self, name: str, text: str,
            container: dict[str, Any] = {}, value_range: range = range(0, 0),
            up_factor: int = 10, down_factor: int = -10, left_factor: int = -1,
            right_factor: int = 1, cycle: bool = True) -> None:
        Option.__init__(self, name, text, container)
        self.value_range: range = value_range
        self.up_factor: int = up_factor
        self.down_factor: int = down_factor
        self.left_factor: int = left_factor
        self.right_factor: int = right_factor
        self.cycle: bool = cycle

    def update_value(self, factor: int) -> None:
        value: int = int(self.container[self.name])
        value += factor
        if value > self.value_range[-1]:
            value = self.value_range[0 if self.cycle else -1]
        elif value < self.value_range[0]:
            value = self.value_range[-1 if self.cycle else 0]
        self.container[self.name] = value

    def input_event(self, action_key: str, _: str, __: str) -> Any:
        factors: dict[str, int] = {
            "up_key": self.up_factor,
            "down_key": self.down_factor,
            "left_key": self.left_factor,
            "right_key": self.right_factor}
        if factors.get(action_key, 0) == 0:
            return
        self.update_value(factors.get(action_key, 0))
```

This Slider Option described before for being adapted to volume settings, takes numerous more parameters at construction. It takes a range object, which will be used as reference, four factors for each directional inputs, and a cycle boolean, to know if the slider should loops back to the maximum value after having reached the lowest, and vice-versa.

This is a good time to talk about inputs. In the `input_event` method, we can see the action_key is used to determine which factor to apply to the container's value, while the named_key and text_input arguments are blanked, unused.

Here is the key difference between the three:

| Input      | Concrete usage                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| action_key | As seen here, corresponds to set names for different actions performed (up_key, down_key..., confirm_key and return_key). They are parsed from the raw_input to determine if it corresponds to an entry in the key configuration.                                                                                                                                                                               |
| named_key  | Corresponds to the name of the key pressed on the keyboard. So instead of " ", it will be "space". This choice was made for more code clarity. For example, the value of the escape key would either be "pygame.K_ESCAPE" or "\x1b", so it seemed clearer for us to parse it using `pygame.key.name` (to "escape"), also making the Option classes easier to implement in other projects that don't use Pygame. |
| text_input | The most literal input of the three. Used here with the `pygame.TEXTINPUT` event, supports capitalized letters and special characters, which could not as easily be reconstructed from the `pygame.KEYDOWN` events.                                                                                                                                                                                             |

The one option type that uses them all is the InputOption subclass, however, as long as it is, we invite you to study its code and different features from the docstrings in the utils file directly.

### Menues to put everything together

*file: "pacman/controllers/menu/menu.py"*

With our different options ready to go, it's time to put them together to create multi-purpose menues. With the same will of giving as many different ways of visualizing and interacting with the menu as there are needs for various options types, we structured our Menu class this way:

- Rendering methods: to generate the text that will be displayed for each option
- Display methods: different ways of organizing the options on screen
- Event methods: To accord to the different arrangements, different behaviors for inputs.

#### Construction

```python
from typing import Any

import pygame as pg

from pacman.models import KeyConfig
from .utils import Option

class Menu:
    def __init__(
            self, screen: pg.Surface, from_left: int = -1, from_top: int = -1,
            spacer: int = -1, options: list[Option] = [],
            loop_cursor: bool = True,
            deselect_color: pg.Color = pg.Color(0, 0, 0),
            select_color: pg.Color = pg.Color(0, 0, 0),
            picked_color: pg.Color = pg.Color(255, 0, 0),
            deselect_ft: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            select_ft: pg.font.Font = pg.font.SysFont("Times New Roman", 22),
            picked_ft: pg.font.Font = pg.font.SysFont("Times New Roman", 22)
            ) -> None:
        self.screen: pg.Surface = screen
        self.from_left: int = (from_left if from_left != -1
                               else int(screen.get_width() / 2))
        self.from_top: int = (from_top if from_top != -1
                              else int(screen.get_height() / 2))
        self.spacer: int = (
            spacer if spacer != -1 else int(
                (screen.get_height() - from_top) / ((len(options) + 1) * 2)))
        self.options: list[Option] = options
        self.loop_cursor: bool = loop_cursor
        self.deselect_color: pg.Color = deselect_color
        self.select_color: pg.Color = select_color
        self.picked_color: pg.Color = picked_color
        self.deselect_ft: pg.font.Font = deselect_ft
        self.select_ft: pg.font.Font = select_ft
        self.picked_ft: pg.font.Font = picked_ft
        self.select_index: int = 0
        self.picked_index: int = -1
        self.last_picked: int = -1
        self.rendered: dict[str, list[tuple[pg.Surface, pg.Rect]]]
        self.renders: list[tuple[pg.Surface, pg.Rect]]
        self.pre_render_all_options()

    def pre_render_all_options(self) -> None:
        self.rendered = {"deselect": [], "select": [], "picked": []}
        des: tuple[pg.Surface, pg.Rect]
        sel: tuple[pg.Surface, pg.Rect]
        pik: tuple[pg.Surface, pg.Rect]
        for option in self.options:
            des, sel, pik = self.pre_render(option)
            self.rendered["deselect"].append(des)
            self.rendered["select"].append(sel)
            self.rendered["picked"].append(pik)

    def pre_render(self, option: Option
                   ) -> tuple[tuple[pg.Surface, pg.Rect], ...]:
        render: str = str(option)
        deselect_render = self.deselect_ft.render(
            render, True, self.deselect_color)
        select_render = self.select_ft.render(
            "◄ " + render + " ►", True, self.select_color)
        picked_render = self.picked_ft.render(
            "◄ " + render + " ►", True, self.picked_color)
```

Let's start with the init method. As you can see, we listed as many customizable variables as possible, with coordinates (from_left, from_top), spacing between the options, the looping around of the cursor and fonts and colors for each style of options (deselected, selected, picked). These are rendered as soon as the Menu is instantiated, using their string representation. So when each of them has been rendered, they are placed in a list of renders depending on their styles, ready to be displayed.

#### Displaying

```python
    def update_rendered_list(self) -> None:
        self.renders = [
            render for render in self.rendered["deselect"]]
        if self.picked_index != -1:
            self.renders[self.picked_index] = self.rendered[
                "picked"][self.picked_index]
        elif self.select_index != -1:
            self.renders[self.select_index] = self.rendered[
                "select"][self.select_index]

    def draw_vertical_options(self) -> None:
        self.update_rendered_list()
        for index, option in enumerate(self.renders):
            option[1].center = (
                self.from_left, self.from_top + index * self.spacer)
            self.screen.blit(option[0], option[1])

    def draw_horizontal_options(self) -> None:
        self.update_rendered_list()
        width: int = self.screen.get_width()
        for index, option in enumerate(self.renders):
            if len(self.renders) == 2:
                option[1].center = (
                    int(width / 3 + index * width / 3), self.from_top)
            else:
                option[1].center = (
                    int(width * 0.25 * (index + 1)), self.from_top)
            self.screen.blit(option[0], option[1])
```

We can see here two different basic styles for the display. The settings menu shown at the beginning uses the `draw_chart_options` method, distributing the options between two columns. Most display methods run on the `renders` attribute, updated to be a list of the pertinent styles of each options

#### Events handling

```python
    def get_event(self, key_config: KeyConfig,
                  event: pg.event.Event, arrangement: str) -> Any:
        curr_option: Option = self.options[self.select_index]
        named_key: str = ""
        text_input: str = ""
        if event.type == pg.TEXTINPUT:
            text_input = event.text
        elif event.type == pg.KEYDOWN:
            named_key = pg.key.name(event.key)
        else:
            return
        action_key: str = key_unicode_to_action(key_config, named_key)
        if action_key == "confirm_key":
            if self.picked_index == -1:
                self.picked_index = self.select_index
                self.last_picked = -1
                self.options[self.picked_index].activate()
                action_key = "activate"
            else:
                self.options[self.picked_index].deactivate()
                self.last_picked = self.picked_index
                self.picked_index = -1
        if action_key == "return_key" and self.picked_index != -1:
            self.options[self.picked_index].deactivate()
            self.last_picked = self.picked_index
            self.picked_index = -1
        if self.picked_index != -1:
            output: str = curr_option.input_event(
                action_key, named_key, text_input)
            if curr_option.pickable is False:
                self.picked_index = -1
            if output == "action_done":
                self.options[self.picked_index].deactivate()
                self.last_picked = self.picked_index
                self.picked_index = -1
                return
            else:
                return output
        {
            "horizontal": self.get_event_horizontal,
            "vertical": self.get_event_vertical,
            "chart": self.get_event_chart}[arrangement](action_key)

    def get_event_vertical(self, key_input: str) -> None:
        if key_input == "up_key":
            self.move_cursor(-1)
        elif key_input == "down_key":
            self.move_cursor(1)

    def get_event_horizontal(self, key_input: str) -> None:
        if key_input == "left_key":
            self.move_cursor(-1)
        elif key_input == "right_key":
            self.move_cursor(1)
```

The events remain the center piece of these interactive menues. The `get_event` method especially represents the play between each type of inputs, the picked option if there is one and the selection.

If the confirm key is pressed, the selection gets picked then sent all inputs. If it's a non-pickable option, it resets the picked index so it doesn't get displayed as such. Otherwise, if it doesn't return "action_done", the output is returned, for example if an Activate option is given a Callable that needs to return a value.

The `activate` and `deactivate` Option methods are called when necessary, ensuring correct behaviors, and if no option needs input, the selection method for the right arrangement is called.

```python
    def move_cursor(self, operant: int) -> None:
        self.change_selected_option(operant)
        while self.options[self.select_index].selectable is False:
            self.change_selected_option(operant)

    def change_selected_option(self, operant: int) -> None:
        self.select_index += operant
        max_indicator = len(self.options)
        if self.select_index < 0:
            if self.loop_cursor is True:
                self.select_index = max_indicator + self.select_index
            else:
                self.select_index = next((
                    index for index in range(max_indicator)
                    if self.options[index].selectable), 0)
        elif self.select_index > max_indicator - 1:
            if self.loop_cursor is True:
                self.select_index = self.select_index % max_indicator
            else:
                self.select_index = next((
                    index for index in range(max_indicator - 1, 0, -1)
                    if self.options[index].selectable), 0)
```

These move the cursor along the options based on the information given by the different arrangement methods, the selectable options and the looping cursor flag.

As non-selectable options need to be skipped, the `change_selected_option` method is called with the same factor until the condition is satisfied. In it, the range of index available, from 0 to the length of the options list, is calculated to check if the new index crosses it. If so, if the cursor can loop, it will select the value from the other end by correctly applying the operant, using the `%` modulo and the fact negative index start from the end of an ordered iterable.

Otherwise, using the `next` function, the selection will stay on either the first or the last selectable option of the list, depending on the end that was reached.

### Instanting all this

*file: "pacman/controllers/states/soptions.py"*

So, to make everything work together, we know we need: a container for the different values that will be changed by our menu, Option objects with each their own type and arguments, as well as a Menu object, from which must be called the render, display and event methods.

```python
class OptionsMenu(State):
    def __init_menu__(self) -> None:
        self.settings = self.control.settings.model_dump()
        dialogs: Dialogs = self.control.dialogs
        self.options_menu = Menu(
            self.control.screen, loop_cursor=False,
            from_top=int(self.control.screen.get_height() / 10), options=[
                SelectionOption(
                    "lang", f"{dialogs.lang:<20}""{value}",
                    self.settings, [lang for lang in Languages]),
                SelectionOption(
                    "res", f"{dialogs.res:<20}""{value}",
                    self.settings, [res for res in Resolutions], cycle=False),
                SliderOption(
                    "sfx_vol", f"{dialogs.sfx_vol:<20}""{value}",
                    self.settings, range(0, 11), 0, 0, cycle=False),
                SliderOption(
                    "bgm_vol", f"{dialogs.bgm_vol:<20}""{value}",
                    self.settings, range(0, 11), 0, 0, cycle=False),
                Spacer(), Spacer(), *[
                    InputOption(
                        key, f"{str(getattr(dialogs, key)) + ":":<20}"
                        "{value}", self.settings["key_config"], 1,
                        False, True, False,
                        excluded_input=["return", "escape", "backspace"]
                    ) for key in ACTION_LIST],
                Spacer(), Spacer(),
                ActivateOption("reset", dialogs.reset_settings,
                               partial(self.reset_settings)),
                ActivateOption("apply", dialogs.apply,
                               partial(self.apply_settings)),
                ActivateOption("back", dialogs.back,
                               partial(self.switch_state, "main_menu")),
                InputOption(
                    "haha", f"{"haha:":<10}""{value}",
                    self.settings, 15, input_require_return=False,
                    char_checker=lambda _: True)
                ])

    def get_event(self, event: pg.event.Event) -> None:
        self.options_menu.get_event(
            self.control.settings.key_config, event, "chart")

    def update(self) -> None:
        self.options_menu.pre_render_option()
        self.draw()

    def draw(self) -> None:
        self.control.screen.fill((255, 255, 255))
        self.options_menu.draw_chart_options(int(
            self.control.screen.get_width() / 2))
```

Five different options were used to make these settings. But as their parent class is the same, they will be seen by the Menu object as standard options. So if the code can seem long behind the scenes for the different options and menu, using them is much simpler. All it takes is a pygame event that will be parsed automatically, updating the options renders and displaying them.

### Resources

Pygame:
- [Pygame's keys list](https://www.pygame.org/docs/ref/key.html#:~:text=pygame%20Constant%20ASCII%20Description)
- [TEXTINPUT event type](https://www.pygame.org/docs/ref/event.html#:~:text=When%20compiled%20with%20SDL2%2C%20pygame%20has%20these%20additional%20events%20and%20their%20attributes)
