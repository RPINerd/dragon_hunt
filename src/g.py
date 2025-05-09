"""This was originally a 'globals' file, but is currently in the process of being refactored largely into a new config file"""

# needed for save/load game
from os import path
from pathlib import Path

import pygame
from icecream import ic

import config
import game_screen as pygscreen
from player import player
from scripting import *

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


# skills array. Each skill is a separate line in the array. Each line goes:
# name, effect, level, price, description, acquired, scripting, picture.
# effect is an integer that tells battle.py which case in a select to pick.
# (0=Rage, 1=Sneak, 2=Frenzy, 3=Dismember, 4=Scripted (battle),
# 5=Scripted (out of battle), 6=Scripted (both).)
# level is the skillpoints required to get the skill,
# price is the ep needed to use.
# acquired tells if the skill has already been learned by the player.
# scripting is an array (that may be empty) that describes the scripting run on use.
# picture is the picture used to show that skill.


# Add a skill to the skill[] array
def addskill(name: str, effect: int, level: int, price: int, description: str, scripting: list = [], picture: str = "items/rage.png"):
    player.skill.append([])
    i = len(player.skill)
    player.skill[i - 1].append(name)
    player.skill[i - 1].append(int(effect))
    player.skill[i - 1].append(int(level))
    player.skill[i - 1].append(int(price))
    player.skill[i - 1].append(description)
    player.skill[i - 1].append(0)
    player.skill[i - 1].append(scripting)
    player.skill[i - 1].append(picture)


# gives the player a skill; takes the location in skill[] as input
def add_skill(skill_loc):
    if player.skill[skill_loc][5] == 1:
        return 0
    player.skill[skill_loc][5] = 1
    return 1


# Load the skills. Requires config.MODULES_DIR to be set
def read_skills():
    # Add built-in skills.
    addskill("Rage", 0, 1, 10, "Gives you increased damage for the rest of a battle", picture="items/rage.png")
    addskill("Sneak Away", 1, 1, 10, "Attempts to leave a battle.", picture="items/sneak_away.png")
    addskill("Dismember", 3, 2, 20, "Your next attack will do maximum damage, and ignore armor", picture="items/bastard_sword.png")
    addskill("Frenzy", 2, 2, 30, "Your next attack will try to hit more than once", picture="items/frenzy.png")
    if path.exists(config.MODULES_DIR + "/data/skills.txt"):
        temp_skills = read_script_file("/data/skills.txt")

    # temp storage for the skill data
    temp_skill_name = ""
    temp_skill_level = 0
    temp_skill_type = 4
    temp_skill_price = 0
    temp_skill_description = ""
    temp_skill_scripting = []
    # Are we entering skill data (0) or scripting (1)?
    data_or_scripting = 0

    for line in temp_skills:
        line_strip = line.strip()
        if line_strip[0] == ":":
            # switch between data or scripting
            if line_strip[1:].lower() == "scripting":
                data_or_scripting = 1
            elif line_strip[1:].lower() == "data":
                data_or_scripting = 0
            else:  # Or just input a new skill.
                # If we have any data, add the previous skill
                if temp_skill_name != "":
                    addskill(
                        temp_skill_name,
                        temp_skill_type,
                        temp_skill_level,
                        temp_skill_price,
                        temp_skill_description,
                        temp_skill_scripting,
                        temp_skill_picture,
                    )

                temp_skill_name = line_strip[1:]
                temp_skill_level = 0
                temp_skill_type = 4
                temp_skill_price = 0
                temp_skill_description = ""
                temp_skill_scripting = []
                temp_skill_picture = "items/rage.png"
        elif data_or_scripting == 0:
            command = line_strip.split("=", 1)[0].lower().strip()
            value = line_strip.split("=", 1)[1].strip()
            if command == "level":
                temp_skill_level = value
            elif command == "price":
                temp_skill_price = value
            elif command == "type":
                temp_skill_type = value
            elif command == "description":
                temp_skill_description = value
            elif command == "picture":
                temp_skill_picture = value
        else:
            temp_skill_scripting.append(line_strip)
    if not temp_skill_name:
        addskill(
            temp_skill_name,
            temp_skill_type,
            temp_skill_level,
            temp_skill_price,
            temp_skill_description,
            temp_skill_scripting,
            temp_skill_picture,
        )


# Returns the symbol of the given tile. X and Y are absolute coords.
def checklocation(x, y):

    # Assume that all off-map areas are rock.
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
    for i in range(len(config.MAPS)):
        if config.MAPS[i].name == name:
            return i
    ic("file " + name + " not found")
    return -1


def read_script_file(file_name: str | Path, from_editor: int = 0) -> list[str]:
    """
    Parse a script file and return a list of commands/scripts

    The from_editor parameter is used to determine if the call is coming from the map
    editor or not. If it is, the script will be returned as-is, without any parsing.

    TODO if the file provided is a path, could simplify the calling to not require str concat

    Args:
        file_name (str): The name of the file to read
        from_editor (int, optional): 1 if being called from editor. Defaults to 0.

    Returns:
        list[str]: The scripting commands in the file
    """
    temp_array = []
    file = Path.open(config.MODULES_DIR + file_name)
    temp_array.extend(file.readlines())
    file.close()
    if from_editor == 0:
        temp_array = interpret_lines(temp_array)
    return temp_array


# Takes an array of lines, and deals with comments, empty lines,
# and line-continuation, to properly interpret the scripting.
def interpret_lines(temp_array):
    cur_line = 0
    while True:
        if cur_line >= len(temp_array):
            break
        # strip out spaces/tabs
        temp_array[cur_line] = temp_array[cur_line].strip()
        # ignore blank lines and comments
        if temp_array[cur_line][:1] == "#" or temp_array[cur_line] == "":
            temp_array.pop(cur_line)
            continue
        # allow the \ line-continuation character.
        while temp_array[cur_line][-1:] == "\\":  # really a single backslash, BTW.
            temp_array[cur_line] = temp_array[cur_line][:-1] + temp_array[cur_line + 1][:-1].strip()
            temp_array.pop(cur_line + 1)
            temp_array[cur_line].strip()
        cur_line += 1
    return temp_array


# create the fonts needed.
font = pygame.font.Font(None, 14)
