
from .utils import JSONModel


class Dialogs(JSONModel):
    """Class Dialogs, subclass of JSONModel

    Instantiate fields for each and every piece of text in the program. Default
    values are in english, and should be updated in a different language from
    a dictionary parsed from its corresponding json file.
    """
    title: str = "Pac-Man"
    play: str = "Play"
    highscores: str = "Highscores"
    settings: str = "Settings"
    quit: str = "Quit"

    arg_error: str = "No argument given, used default config path"
    config_error: str = "The configuration file could not be opened"
    settings_error: str = "The settings file could not be opened"
    highscores_error: str = "The highscores file could not be opened"
    dialogs_error: str = (
        "The dialogs for the chosen language could not be loaded")
    permission_error: str = "File permissions error"
    error_occured: str = "An error occured..."
    defaulted_values: str = (
        "Faulty configurations replaced with default values")

    options_menu: str = "Game options"
    lang: str = "Language"
    res: str = "Window"
    fullscreen: str = "fullscreen"
    sfx_vol: str = "SFX volume"
    bgm_vol: str = "BGM volume"
    up_key: str = "up"
    down_key: str = "down"
    left_key: str = "left"
    right_key: str = "right"
    confirm_key: str = "confirm"
    return_key: str = "return"
    reset_settings: str = "Reset settings"
    apply: str = "Apply"
    reload_config: str = "Reload config"
    reset_config: str = "Reset config"
    back: str = "back"

    highscores_menu: str = "Highscore menu"
    no_highscores: str = "No highscores saved"
    player: str = "Player"
    score: str = "Total score"
    level_reached: str = "Level reached"
    time_taken: str = "Time taken"
    remaining_lives: str = "Remaining lives"
    reset_highscores: str = "reset"

    paused: str = "Pause menu"
    resume: str = "Resume"
    give_up: str = "Give up"

    cheats_menu: str = "Cheats menu"
    true: str = "True"
    false: str = "False"
    invincibility: str = "Invincibility"
    infinite_super: str = "Infinite Super"
    infinite_time: str = "Infinite time"
    super_speed: str = "Super speed"
    life_gains: str = "Gain life"
    skip_level: str = "Skip level"

    level_win: str = "Level complete !"
    level_fail: str = "Level failed..."
    gum: str = "Coins"
    sup_gum: str = "Knives"
    ghost: str = "Skeletons"
    level: str = "Level"
    current_score: str = "Current score"
    continue_next: str = "Continue"

    run_end: str = "End of run"
    playtime: str = "Run time"

    player_name: str = "Enter your name"
    save_score: str = "Save score"
    score_saved: str = "Score saved !"
    cheats_used: str = "Cheats were used..."
    end_run: str = "Return to main menu"
