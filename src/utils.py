""""""
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
