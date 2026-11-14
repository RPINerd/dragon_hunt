"""This was originally a 'globals' file, but is currently in the process of being refactored largely into a new config file"""

# needed for save/load game

import logging

import pygame

import config
import game_screen as pygscreen
from scripting import *

logger = logging.getLogger(__name__)

# This is the screen that will be used for the game.
screen = pygscreen.get_screen()

# This will be displayed on the Title screen and Main screen.
game_name = ""

# This is the main window for the entire game. (Will be filled in with
# a Tkinter window reference later.)
window_main = ""

# location on map: x, y, z coordinate. Map names are given a zgrid on loading.
xgrid = 0
ygrid = 0
zgrid = 1

# controls timed effects such as healing. Loops around every 30 turns (0-29);
# controls perturn.txt.
timestep = 0

# dictionary of script variables.
var_list = {}

# Current window in use (main, battle, inventory, shop)
cur_window = "main"

# Should the automatic changing of the hero picture be allowed?
# Used with the manual hero() command, to prevent the change from being undone.
allow_change_hero = 1

# width of the hp/ep bars
hpbar_width = 0

# per turn scripting, for hp recovery and the like.
per_turn_script = []

# Used in place of some of the Tkinter variables.
# ? Wut?
break_one_loop = 0

# used to decide whether or not to refresh (flip) the screen.
unclean_screen = False

clock = pygame.time.Clock()


# Returns the symbol of the given tile. X and Y are absolute coords.
def checklocation(x, y):

    # Assume that all off-map areas are rock.
    """
    Return the tile symbol at the given map coordinates.

    Args:
        x (int): Absolute map x-coordinate.
        y (int): Absolute map y-coordinate.

    Returns:
        str: Tile symbol at the coordinates, or "a" if they are off-map.
    """
    if x < 0 or y < 0:
        return "a"
    try:
        # this will fail when looking too far right or down
        return config.MAPS[zgrid].field[y][x].name
    except IndexError:
        # off the map, so rock.
        return "a"


# like checklocation, but just returns 0 (unwalkable) or 1 (walkable)
def iswalkable(x, y, dx, dy):
    # set direction hero is moving in
    """
    Check whether the player can move to the given map coordinates.

    Args:
        x (int): Absolute map x-coordinate.
        y (int): Absolute map y-coordinate.
        dx (int): Horizontal movement offset for the attempted step.
        dy (int): Vertical movement offset for the attempted step.

    Returns:
        int: 1 if the move is allowed; otherwise 0.
    """
    if dy == -1:
        move_direction = "n"
    elif dy == 1:
        move_direction = "s"
    elif dx == -1:
        move_direction = "w"
    else:
        move_direction = "e"

    # Assume that all off-map areas (to north or west) are unwalkable.
    if x < 0 or y < 0:
        return 0
    try:
        # this will fail when looking too far right or down
        if config.MAPS[zgrid].field[y][x].walk == 0:
            return 0
        # can't move onto tile if there's a wall in the way
        if config.MAPS[zgrid].field[y][x].walk == 1:
            if (config.MAPS[zgrid].field[y][x].wall_s == 1 and move_direction == "n") or (config.MAPS[zgrid].field[y][x].wall_n == 1 and move_direction == "s"):
                return 0
            if (config.MAPS[zgrid].field[y][x].wall_e == 1 and move_direction == "w") or (config.MAPS[zgrid].field[y][x].wall_w == 1 and move_direction == "e"):
                return 0
        # can't move out of old tile if there's a wall in the way
        if (config.MAPS[zgrid].field[y - dy][x - dx].wall_s == 1 and move_direction == "s") or (config.MAPS[zgrid].field[y - dy][x - dx].wall_n == 1 and move_direction == "n"):
            return 0
        if (config.MAPS[zgrid].field[y - dy][x - dx].wall_e == 1 and move_direction == "e") or (config.MAPS[zgrid].field[y - dy][x - dx].wall_w == 1 and move_direction == "w"):
            return 0

    except IndexError:
        return 0
    # By this point, it is known to be walkable.
    return 1


# takes the name of a map, and returns its zgrid.
def mapname2zgrid(name):
    """
    Find the map index with the requested name.

    Args:
        name (str): Map name to find.

    Returns:
        int: Matching map index, or -1 if the name is not found.
    """
    for i in range(len(config.MAPS)):
        if config.MAPS[i].name == name:
            return i
    logger.warning("Map file %s not found.", name)
    return -1


# create the fonts needed.
font = pygame.font.Font(None, 14)
