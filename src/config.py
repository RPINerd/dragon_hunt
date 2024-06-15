from os import listdir

# Previously array_mods
MODULES = listdir("../modules/").remove("default")

# Tile size notes from original code:
# size (in tiles) of the editor screen. 15 works well with 640x480,
# 20 with 800x600, and 24 with 1024x768
TILESIZE = 32
EDITOR_TILESIZE = 24

# Number of lines to display in the scroller
MESSAGE_LINES = 10

# Mutable global variables
mut = {"MODULE_POS": 0, "CURR_BUTTON": 0}
