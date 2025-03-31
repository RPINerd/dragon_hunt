"""Functions to handler the loading of individual module components."""
import sys
from os import path, walk
from pathlib import Path

import pygame
from icecream import ic

import config
import g

# from scripting import Map  # TODO make map its own file/module
import scripting
from item import read_items
from monster import read_monster
from scripting import read_scripts, read_shops


def load_icons() -> None:
    """This loads the icons"""
    config.ICONS = read_images("/images/icons/")


def load_backgrounds() -> None:
    """Load the background images for battles"""
    config.BACKGROUNDS = read_images("/images/backgrounds/")


def load_buttons() -> None:
    """This loads the buttons"""
    config.BUTTONS = read_images("/images/buttons/")


def load_tiles() -> None:
    """Loads the various tiles."""
    config.TILES = read_images("/images/tiles/")


def load_sounds() -> None:
    """Walk the sound directory and load all sounds into the SOUNDS dictionary."""
    if config.MUTE:
        return
    try:
        pygame.mixer.init()
    except pygame.error as message:
        ic(f"Error: Unable to init sound (pygame message: {message})")
        MUTE = True
        return

    for root, dirs, files in walk(config.MODULES_DIR + "/sound"):
        (head, tail) = path.split(root)
        if tail != "CVS":
            for soundname in files:
                # if image is in a sub-dir:
                tmp_name = soundname[:-5] + soundname[-4:]
                tmp_number = int(soundname[-5])
                if root != config.MODULES_DIR + "/sound":
                    i = len(config.MODULES_DIR + "/sound")
                    base_name = root[i:] + "/" + tmp_name
                else:  # if image is in root dir
                    base_name = tmp_name
                if base_name not in config.SOUNDS:
                    config.SOUNDS[base_name] = {}
                config.SOUNDS[base_name][tmp_number] = pygame.mixer.Sound(root + "/" + soundname)


def read_images(dir_name: str) -> dict[str, pygame.Surface]:
    """
    Read all images in the given directory and its subdirectories

    Args:
        dir_name (str): The directory to read images from

    Returns:
        image_dictionary (dict[str, pygame.Surface]): A dictionary of all images in the directory
    """
    def inner_read_images(dir_name: str, image_dictionary: dict[str, pygame.Surface]) -> dict[str, pygame.Surface]:
        """"""
        i = 0
        for root, dirs, files in walk(dir_name):
            (head, tail) = path.split(root)
            try:
                if tail != "CVS":
                    for tilename in files:
                        # if image is in a sub-dir:
                        if root != dir_name:
                            i = len(dir_name)
                            image_dictionary[root[i:] + "/" + tilename] = pygame.image.load(
                                root + "/" + tilename
                            ).convert_alpha()
                        else:  # if image is in root dir
                            image_dictionary[tilename] = pygame.image.load(root + "/" + tilename).convert_alpha()
            except pygame.error:
                ic(root[i:] + "/" + tilename + " failed to load")
        return image_dictionary

    if not pygame.image.get_extended():
        ic("Error: SDL_image required. Exiting.")
        sys.exit()
    image_dictionary = {"blank": pygame.Surface((32, 32))}
    image_dictionary = inner_read_images("../data/buttons", image_dictionary)
    image_dictionary = inner_read_images(config.MODULES_DIR + dir_name, image_dictionary)

    return image_dictionary  #noqa


def read_maps(from_editor: int = 0) -> None:
    """
    Read the data/maps directory and place in maps[]

    This called at startup

    Args:
        from_editor (int, optional): 1 if being called from editor. Defaults to 0.
    """
    del config.MAPS[:]
    load_backgrounds()

    # Create an iterator of all the *.txt map files in the directory
    array_maps: list[Path] = Path(config.MODULES_DIR + "/data/maps").glob("*.txt")

    # Iterate through all maps, adding them to our knowledge.
    config.MAX_MAPSIZE = (0, 0)
    for mapname in array_maps:
        config.MAPS.append(scripting.Map(mapname, from_editor))
        if config.MAX_MAPSIZE[0] < len(config.MAPS[-1].field[0]):
            config.MAX_MAPSIZE = (len(config.MAPS[-1].field[0]), config.MAX_MAPSIZE[1])
        if config.MAX_MAPSIZE[1] < len(config.MAPS[-1].field):
            config.MAX_MAPSIZE = (config.MAX_MAPSIZE[0], len(config.MAPS[-1].field))


def read_perturn() -> None:
    """
    Read the perturn file for the selected module"

    Expects config.MODULES_DIR to be set
    """
    cur_turns = []
    temp_cur_turns = []
    for i in range(30):
        g.per_turn_script.append([])
    per_turn_lines = g.read_script_file("/data/perturn.txt")  # TODO
    for fline in per_turn_lines:
        line = fline.strip()
        if line[:1] == ":":  # start defining more tiles.
            cur_turns = []
            temp_cur_turns = line[1:].split(",")
            for turn in temp_cur_turns:
                if turn.strip().isdigit():
                    cur_turns.append(int(turn.strip()))

        # give scripting to the current tiles
        else:
            for turn_num in cur_turns:
                g.per_turn_script[turn_num].append(line)


def read_settings() -> None:
    """Read the settings file and set the global variables accordingly"""
    # global editor_xy

    # editor_xy = (1024, 768)

    with Path.open("../settings.txt") as settings_file:
        for fline in settings_file:

            # Strip whitespace
            line = fline.strip()

            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue

            line_key, line_value = line.split("=")
            if line_key == "difficulty":
                config.DIFFICULTY = int(line_value)
            elif line_key == "editor_xy_size":
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT = (int(line_value.split(",")[0]), int(line_value.split(",")[1]))
            elif line_key == "fullscreen":
                config.FULLSCREEN = int(line_value)
            else:
                config.BINDINGS[line_key.lower()] = int(line_value)


def read_variables() -> None:
    """Read the variables file for the selected module"""
    def _read_dice(index: int, dice_string: str) -> None:
        """Load a dice set string of the form 2d4+5"""
        first = dice_string.split("d", 1)[0].strip()
        temp = dice_string.split("d", 1)[1].strip()
        if "+" not in temp:
            second = temp.strip()
            third = "0"
        else:
            second, third = temp.split("+", 1)

        dice_list = [int(first), int(second), int(third)]
        config.DICE[index] = dice_list

    variable_path = Path(config.MODULES_DIR + "/data/variables.txt")
    # Verify that the variables file exists.
    if not Path.exists(variable_path):
        ic(f"Error: No variables file found in {config.MODULES_DIR}/data/.. Exiting.")
        sys.exit()

    # Open the module variables file and parse it
    with Path.open(config.MODULES_DIR + "/data/variables.txt") as file:
        for fline in file:
            line = fline.strip()

            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue

            line_key = line.split("=", 1)[0].strip().lower()
            line_value = line.split("=", 1)[1].strip()
            if line_key == "hp":
                _read_dice(0, line_value)
            elif line_key == "ep":
                _read_dice(1, line_value)
            elif line_key == "attack":
                _read_dice(2, line_value)
            elif line_key == "defense":
                _read_dice(3, line_value)
            elif line_key == "gold":
                _read_dice(4, line_value)
            elif line_key == "game_name":
                config.mut["GAME_NAME"] = line_value
            elif line_key == "default_player_name":
                config.DEFAULT_NAME = line_value
            elif line_key == "exp_list":
                config.mut["EXP_LIST"] = line_value.split(" ")

    if not config.mut["GAME_NAME"]:
        ic("Warning: No game name found in variables file. Defaulting to 'Dragon Hunt'")
        config.mut["GAME_NAME"] = "Dragon Hunt"


def init_gamedata() -> None:
    """
    Initialize the game data.

    ? Originally had a lot of loading screens but is now way too fast to even percieve

    TODO "read maps" has a nifty bar that I should emulate throughout the other loads
    TODO refactor so that everyone just uses pygscreen.get_screen() instead of screen
    TODO refactor this to just use confiscreensizes across everything

    Returns:
        None
    """
    ic("Read settings")
    read_settings()
    ic("Load backgrounds")
    load_backgrounds()
    ic("Read scripts")
    read_scripts()
    ic("Read items")
    read_items()
    ic("Read skills")
    g.read_skills()  # TODO
    ic("Read monsters")
    read_monster()
    ic("Read variables")
    read_variables()
    ic("Read shops")
    read_shops()
    ic("Read perturn")
    read_perturn()
    ic("Load buttons")
    load_buttons()
    ic("Load icons")
    load_icons()
    ic("Load sounds")
    load_sounds()
