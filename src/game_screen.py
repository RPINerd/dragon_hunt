"""Simple script for housing the pygame screen so that all other files can work from the same window."""

import pygame

import config

# Screen dimensions
SCREEN_WIDTH = config.SCREEN_WIDTH
SCREEN_HEIGHT = config.SCREEN_HEIGHT
# FLAGS = pygame.SCALED
FLAGS = 0

# Pygame screen creation
_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FLAGS)
pygame.display.set_caption("Dragon Hunt - RPG")
pygame.font.init()


def get_screen() -> pygame.Surface:
    """
    Get the pygame screen object.

    Returns:
        The pygame screen object.
    """
    global _screen
    return _screen
