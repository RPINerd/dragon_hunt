"""Configuration settings for the Dragon Hunt game."""

# Previously array_mods
MODULES = ["DarkAges", "DragonHunt"]

# Screen resolution
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Tile size notes from original code:
# size (in tiles) of the editor screen. 15 works well with 640x480,
# 20 with 800x600, and 24 with 1024x768
TILESIZE = 32
EDITOR_TILESIZE = 32

# Number of lines to display in the scroller
MESSAGE_LINES = 10

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
mut = {"MODULE_POS": 0, "CURR_BUTTON": 0, "GAME_NAME": ""}
