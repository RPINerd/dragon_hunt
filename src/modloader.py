"""Functions to handler the loading of individual module components."""
import logging
import sys
from os import path, walk
from pathlib import Path

import pygame

import config
import g

# from scripting import Map  # TODO make map its own file/module
import scripting
import utils
from item import read_items
from monster import read_monster
from player import player
from scripting import read_scripts, read_shops

logger = logging.getLogger(__name__)


def load_icons() -> None:
    """Load module icons into the shared icon dictionary."""
    config.ICONS = read_images("/images/icons/")


def load_backgrounds() -> None:
    """Load module battle backgrounds into the shared background dictionary."""
    config.BACKGROUNDS = read_images("/images/backgrounds/")


def load_buttons() -> None:
    """Load module button images into the shared button dictionary."""
    config.BUTTONS = read_images("/images/buttons/")


def load_tiles() -> None:
    """Load module tile images into the shared tile dictionary."""
    config.TILES = read_images("/images/tiles/")


def load_sounds() -> None:
    """Load module sound effects into the shared sound dictionary."""
    if config.MUTE:
        return
    try:
        pygame.mixer.init()
    except pygame.error as message:
        logger.error("Unable to init sound (pygame message: %s)", message)
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
    Load images from a module directory and its subdirectories.

    Args:
        dir_name (str): Directory path relative to the selected module.

    Returns:
        dict[str, pygame.Surface]: Image paths mapped to loaded surfaces.
    """
    def inner_read_images(dir_name: str, image_dictionary: dict[str, pygame.Surface]) -> dict[str, pygame.Surface]:
        """
        Add image files from a directory tree to a shared dictionary.

        Args:
            dir_name (str): Root directory to scan.
            image_dictionary (dict[str, pygame.Surface]): Dictionary to populate and return.

        Returns:
            dict[str, pygame.Surface]: The populated image dictionary.
        """
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
                logger.warning("%s failed to load", root[i:] + "/" + tilename)
        return image_dictionary

    if not pygame.image.get_extended():
        logger.error("SDL_image required. Exiting.")
        sys.exit()
    image_dictionary = {"blank": pygame.Surface((32, 32))}
    image_dictionary = inner_read_images("../data/buttons", image_dictionary)
    image_dictionary = inner_read_images(config.MODULES_DIR + dir_name, image_dictionary)

    return image_dictionary  # ruff: ignore[unnecessary-assign]


def read_maps(from_editor: int = 0) -> None:
    """
    Read module maps and update the maximum map dimensions.

    Args:
        from_editor (int): Whether maps are being read for the editor; 1 enables editor mode.
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
    """Load scripts assigned to game turns."""
    cur_turns = []
    temp_cur_turns = []
    for i in range(30):
        g.per_turn_script.append([])
    per_turn_lines = utils.read_script_file("/data/perturn.txt")  # TODO
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
    """Read settings and update game configuration."""
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


def read_skills() -> None:
    """
    Load built-in and module-defined player skills.

    Module skill definitions may include metadata and scripting lines.
    """
    if Path(config.MODULES_DIR + "/data/skills.txt").exists():
        temp_skills = utils.read_script_file("/data/skills.txt")

    # Built-in/standard skills
    player.skill.append([
        "Rage",
        0,
        1,
        10,
        "Gives you increased damage for the rest of a battle",
        1,
        [],
        "items/rage.png"])
    player.skill.append([
        "Sneak Away",
        1,
        1,
        10,
        "Attempts to leave a battle.",
        1,
        [],
        "items/sneak_away.png"])
    player.skill.append([
        "Dismember",
        3,
        2,
        20,
        "Your next attack will do maximum damage, and ignore armor",
        1,
        [],
        "items/bastard_sword.png"])
    player.skill.append([
        "Frenzy",
        2,
        2,
        30,
        "Your next attack will try to hit more than once",
        1,
        [],
        "items/frenzy.png"])

    # temp storage for the skill data
    temp_skill_name = ""
    temp_skill_level = 0
    temp_skill_type = 4
    temp_skill_price = 0
    temp_skill_description = ""
    temp_skill_scripting = []
    temp_skill_acquired = 0
    temp_skill_picture = "items/rage.png"
    # Are we entering skill data (0) or scripting (1)?
    data_or_scripting = 0

    for line in temp_skills:
        line_strip = line.strip()
        if line_strip[0] == ":":
            # switch between data or scripting
            if line_strip[1:].lower() == "scripting":
                data_or_scripting = 1
            elif line_strip[1:].lower() == "data":
                data_or_scripting = 0
            else:  # Or just input a new skill.
                # If we have any data, add the previous skill
                if temp_skill_name:
                    player.skill.append([
                        temp_skill_name,
                        temp_skill_type,
                        temp_skill_level,
                        temp_skill_price,
                        temp_skill_description,
                        temp_skill_acquired,
                        temp_skill_scripting,
                        temp_skill_picture,
                    ])

                temp_skill_name = line_strip[1:]
                temp_skill_level = 0
                temp_skill_type = 4
                temp_skill_price = 0
                temp_skill_description = ""
                temp_skill_scripting = []
                temp_skill_picture = "items/rage.png"
        elif data_or_scripting == 0:
            command = line_strip.split("=", 1)[0].lower().strip()
            value = line_strip.split("=", 1)[1].strip()
            if command == "level":
                temp_skill_level = value
            elif command == "price":
                temp_skill_price = value
            elif command == "type":
                temp_skill_type = value
            elif command == "description":
                temp_skill_description = value
            elif command == "picture":
                temp_skill_picture = value
        else:
            temp_skill_scripting.append(line_strip)
    if not temp_skill_name:
        player.skill.append([
            temp_skill_name,
            temp_skill_type,
            temp_skill_level,
            temp_skill_price,
            temp_skill_description,
            temp_skill_acquired,
            temp_skill_scripting,
            temp_skill_picture,
        ])


def read_variables() -> None:
    """Load module variables and player defaults."""
    def _read_dice(index: int, dice_string: str) -> None:
        """
        Parse a dice expression into the configured dice table.

        Args:
            index (int): Dice-table slot to update.
            dice_string (str): Expression in the form NdS or NdS+M.
        """
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
        logger.error("No variables file found in %s/data/.. Exiting.", config.MODULES_DIR)
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
        logger.warning("No game name found in variables file. Defaulting to 'Dragon Hunt'")
        config.mut["GAME_NAME"] = "Dragon Hunt"


def init_gamedata() -> None:
    """Load settings and module data required to start the game."""
    logger.info("Read settings")
    read_settings()
    logger.info("Load backgrounds")
    load_backgrounds()
    logger.info("Read scripts")
    read_scripts()
    logger.info("Read items")
    read_items()
    logger.info("Read skills")
    read_skills()
    logger.info("Read monsters")
    read_monster()
    logger.info("Read variables")
    read_variables()
    logger.info("Read shops")
    read_shops()
    logger.info("Read perturn")
    read_perturn()
    logger.info("Load buttons")
    load_buttons()
    logger.info("Load icons")
    load_icons()
    logger.info("Load sounds")
    load_sounds()
