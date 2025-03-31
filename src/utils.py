""""""
from pathlib import Path
from random import random

import pygame
from icecream import ic

import config


def play_sound(sound_name: str) -> None:
    """"""
    try:
        dict_size = len(config.SOUNDS[sound_name])
        config.SOUNDS[sound_name][int(random() * dict_size)].play()
    except KeyError:
        raise KeyError(f"Missing sound set {sound_name}")
    except pygame.error:
        ic(f"Error: Unable to play sound {sound_name}")


def die_roll(dice: int, sides: int, modfy: int = 0) -> int:
    """
    Perform a dice roll and return the result.

    Rolls dice in the form 2d6, where 2 is the number of dice, and 6 the number of sides
    on each die. Modify is the bonus given to each die.
    Use die_roll(2, 6) + 4 for bonuses on the entire roll, or die_roll(2, 6, 1) for bonuses on each roll.

    Args:
        dice (int): The number of dice to roll.
        sides (int): The number of sides on each die.
        modfy (int): The modifier to add to each die roll.

    Returns:
        int: The sum of the rolled dice plus the modifier.

    Raises:
        ValueError: If the number of dice or sides is less than 1.
    """
    if dice < 1:
        raise ValueError("Number of dice must be greater than 0")
    if sides < 1:
        raise ValueError("Number of sides must be greater than 0")

    sum = 0
    for x in range(dice):
        die = int((random() * sides) + 1 + modfy)
        sum += die

    return sum


def read_script_file(file_name: str | Path, from_editor: int = 0) -> list[str]:
    """
    Parse a script file and return a list of commands/scripts

    The from_editor parameter is used to determine if the call is coming from the map
    editor or not. If it is, the script will be returned as-is, without any parsing.

    TODO if the file provided is a path, could simplify the calling to not require str concat
    TODO switch to a context manager for file opening, merge in the interpret lines logic
    TODO error handling for file not found, etc.

    Args:
        file_name (str): The name of the file to read
        from_editor (int, optional): 1 if being called from editor. Defaults to 0.

    Returns:
        list[str]: The scripting commands in the file
    """

    def interpret_lines(script_lines: list[str]) -> list[str]:
        """
        Interpret lines of a script file.

        Deals with comments, empty lines, and line-continuation to properly interpret the scripting.

        Args:
            script_lines (list[str]): The lines of the script file to interpret.

        Returns:
            list[str]: The interpreted lines of the script file.
        """
        cur_line = 0
        while True:
            if cur_line >= len(script_lines):
                break
            # strip out spaces/tabs
            script_lines[cur_line] = script_lines[cur_line].strip()
            # ignore blank lines and comments
            if script_lines[cur_line][:1] == "#" or not script_lines[cur_line]:
                script_lines.pop(cur_line)
                continue
            # allow the \ line-continuation character.
            while script_lines[cur_line][-1:] == "\\":  # really a single backslash, BTW.
                script_lines[cur_line] = script_lines[cur_line][:-1] + script_lines[cur_line + 1][:-1].strip()
                script_lines.pop(cur_line + 1)
                script_lines[cur_line].strip()
            cur_line += 1
        return script_lines

    temp_array = []
    file = Path.open(config.MODULES_DIR + file_name)
    temp_array.extend(file.readlines())
    file.close()
    if from_editor == 0:
        return interpret_lines(temp_array)
    return temp_array
