""""""
import logging
from pathlib import Path
from random import random

import pygame

import config

logger = logging.getLogger(__name__)


def play_sound(sound_name: str) -> None:
    """
    Play a randomly selected variant of a named sound effect.

    Args:
        sound_name (str): Key of the sound set to play.
    """
    try:
        dict_size = len(config.SOUNDS[sound_name])
        config.SOUNDS[sound_name][int(random() * dict_size)].play()
    except KeyError:
        raise KeyError(f"Missing sound set {sound_name}")
    except pygame.error:
        logger.warning("Unable to play sound %s", sound_name)


def die_roll(dice: int, sides: int, modfy: int = 0) -> int:
    """
    Roll dice and return their total with a modifier applied to each die.

    Use a separate addition to modify the total roll instead of each individual die.

    Args:
        dice (int): Number of dice to roll.
        sides (int): Number of sides on each die.
        modfy (int): Modifier added to each die roll.

    Returns:
        int: Sum of all modified die results.
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
    Read a script file, optionally preserving its source formatting.

    Args:
        file_name (str | Path): Path relative to the selected module.
        from_editor (int): Set to 1 to return lines without parsing.

    Returns:
        list[str]: Script lines, with comments and blank lines removed unless editor mode is enabled.
    """

    def interpret_lines(script_lines: list[str]) -> list[str]:
        """
        Normalize script lines and remove comments and blank lines.

        Args:
            script_lines (list[str]): Lines read from a script file.

        Returns:
            list[str]: Interpreted script lines.
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
