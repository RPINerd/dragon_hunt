"""
    This file is the first file accessed upon game start.
    It allows the player to select the module, or, if there is only one, automatically selects for the player.
"""

import pygame

import config
import modules


def main():
    """
    The main function of the game. This is the first function called upon launch.

    :return: None
    """

    # Load assets into memory

    # Check modules to decide if selection is needed
    if len(config.MODULES) == 1:
        modules.load(config.MODULES[0])
        return

    # Call the module selection script
    module_index = modules.select()
    modules.load(config.MODULES[module_index])


if __name__ == "__main__":

    pygame.init()

    main()
