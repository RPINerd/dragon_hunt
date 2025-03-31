"""Configuration settings for the Dragon Hunt game."""
from pathlib import Path

import pygame

# Previously array_mods
MODULES: list[str] = ["DarkAges", "DragonHunt", " ", " ", " "]
MODULES_DIR: str | Path = ""

# Screen resolution
SCREEN_WIDTH: int = 1024
SCREEN_HEIGHT: int = 768
FULLSCREEN: bool = False
MUTE: bool = False

# Tile size notes from original code:
# size (in tiles) of the editor screen. 15 works well with 640x480,
# 20 with 800x600, and 24 with 1024x768
TILESIZE: int = 32
MAPSIZE_X: int = 31
MAPSIZE_Y: int = 23
MAX_MAPSIZE: tuple[int, int] = (0, 0)

# Number of lines to display in the scroller
MESSAGE_LINES: int = 10

# Colors used in the game
COLORS = {
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "hp_red": (238, 5, 5, 255),
    "hp_green": (5, 187, 5, 255),
    "ep_blue": (5, 5, 238, 255),
    "dark_red": (125, 0, 0, 255),
    "dark_green": (122, 169, 110, 255),
    "dark_blue": (0, 0, 125, 255),
    "light_red": (255, 50, 50, 255),
    "light_green": (50, 255, 50, 255),
    "light_blue": (50, 50, 255, 255),
    "purple": (96, 96, 144, 255),
    "light_gray": (227, 227, 227, 255),
    "very_dark_blue": (32, 32, 47, 255),
    "dh_green": (185, 229, 173, 255),
}

# Mutable global variables
ALLOW_MOVE = True  # Used with the move scripting command to prevent moving multiple times
mut = {"MODULE_POS": 0, "CURR_BUTTON": 0, "GAME_NAME": "", "EXP_LIST": ""}
BACKGROUNDS: dict[str,] = {}
BINDINGS: dict[str, int] = {
    "up": 273,
    "down": 274,
    "left": 276,
    "right": 275,
    "action": 13,
    "cancel": 27,
    "attack": 97,
    "save": 115,
    "quit": 113,
    "inv": 105,
}
BUTTONS: dict[str,] = {}
DIFFICULTY: int = 1  # 0 = easy, 1 = normal, 2 = hard
DICE: list[list[int]] = [[], [], [], [], []]  # Array of dice for the player
DEFAULT_NAME: str = "Alfred"  # Default name for the player
ICONS: dict[str,] = {}
MAPS: list = []
SOUNDS: dict[str, dict[int, pygame.Sound]] = {}
TILES: dict[str,] = {}

DEBUG = False
FASTBOOT = False  # Skip map preprocessing

# Editor variables
EDITOR_TILESIZE: int = 32  # Size of the editor screen (in tiles)
TILEGRID = False  # Whether or not to display the map grid
EDITOR_MAPSIZE_X: int = 25
EDITOR_MAPSIZE_Y: int = 25
