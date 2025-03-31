"""
    Dragon Hunt; Game entry point.

    This stub allows the player to select the module, or, if there is only one, automatically selects for the player.
"""

import pygame
from icecream import ic

import config
import game_screen as pygscreen
import modules
import new_game

screen = pygscreen.get_screen()


def main() -> None:
    """
    The main function of the game. This is the first function called upon launch.

    Args:
        None

    Returns:
        None
    """
    # Load assets into memory

    # Check modules to decide if selection is needed
    if len(config.MODULES) == 1:
        modules.load(config.MODULES[0])
        return

    # Call the module selection script
    module_index = modules.select()
    modules.load(config.MODULES[module_index])

    ic("Module loaded, initializing game")
    new_game.init_window()


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    main()
