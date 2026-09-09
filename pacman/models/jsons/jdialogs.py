
from pydantic import Field

from .utils import JSONModel


class Dialogs(JSONModel):
    """Class Dialogs, subclass of JSONModel

    Instantiate fields for each and every piece of text in the program. Default
    values are in english, and should be updated in a different language from
    a dictionary parsed from its corresponding json file.
    """
    title: str = Field(default="Pac-Man")
    play: str = Field(default="Play")
    highscores: str = Field(default="Highscores")
    settings: str = Field(default="Settings")
    quit: str = Field(default="Quit")

    lang: str = Field(default="Language")
    res: str = Field(default="Window")
    fullscreen: str = Field(default="fullscreen")
    sfx_vol: str = Field(default="SFX volume")
    bgm_vol: str = Field(default="BGM volume")
    up_key: str = Field(default="up")
    down_key: str = Field(default="down")
    left_key: str = Field(default="left")
    right_key: str = Field(default="right")
    confirm_key: str = Field(default="confirm")
    return_key: str = Field(default="return")
    reset_settings: str = Field(default="reset settings")
    apply: str = Field(default="apply")
    back: str = Field(default="back")

    highscores_menu: str = Field(default="Highscore menu")
    no_highscores: str = Field(default="No highscores saved")
    player: str = Field(default="Player")
    score: str = Field(default="Total score")
    level_reached: str = Field(default="Level reached")
    time_taken: str = Field(default="Time taken")
    remaining_lives: str = Field(default="Remaining lives")
    reset_highscores: str = Field(default="reset")

    resume: str = Field(default="Resume")
    give_up: str = Field(default="give up")

    gum: str = Field(default="Gums")
    sup_gum: str = Field(default="Super gums")
    ghost: str = Field(default="Ghosts")
    level: str = Field(default="Level")
    current_score: str = Field(default="Current score")
    continue_next: str = Field(default="Continue")

    run_end: str = Field(default="End of run")
    playtime: str = Field(default="Run time")

    player_name: str = Field(default="Enter your name")
    save_score: str = Field(default="Save score")
    score_saved: str = Field(default="Score saved !")
    cheats_used: str = Field(default="Cheats were used...")
    end_run: str = Field(default="Return to main menu")
