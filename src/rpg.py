"""
    Dragon Hunt; Game entry point.

    This stub allows the player to select the module, or, if there is only one, automatically selects for the player.
"""

import logging

import pygame

from logging_config import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize the game and start the selected module."""
    configure_logging()
    pygame.init()
    pygame.font.init()

    import config
    import modules
    import new_game

    config.MODULES = modules.discover_installed_modules()
    if not config.MODULES:
        logger.error("No installed game modules found. Exiting.")
        pygame.quit()
        return

    if len(config.MODULES) == 1:
        modules.load(config.MODULES[0])
    else:
        module_index = modules.select()
        if module_index is None:
            pygame.quit()
            return
        modules.load(config.MODULES[module_index])

    logger.info("Module loaded, initializing game")
    new_game.init_window()


if __name__ == "__main__":
    main()
