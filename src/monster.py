"""This file contains everything about the monsters"""

from os import listdir
from random import random

from icecream import ic

import config
import g


class MonsterGroup:

    """This class contains one or more monster, that can attack the player in a group."""

    def __init__(self, name: str) -> None:
        """"""
        self.name = str(name)
        # The message given when the monster group attacks.
        self.attack_message = "The " + self.name + " attacks you."
        # The xy coords of the upper-middle of each monster.
        self.x_pos = []
        self.y_pos = []
        # Filled with strings matched up to names in Monster class upon attack.
        self.monster_list = []


class Monster:

    """This class contains all the information about a monster."""

    def __init__(self, name: str, hp: int, attack: int, defense: int, exp: int, gold: int, descript: str) -> None:
        """"""
        self.name = name
        self.hp = hp
        self.maxhp = hp
        self.attack = attack
        self.defense = defense
        self.exp = exp
        self.gold = gold
        self.description = descript

        # An array of lines, describing the scripting run when the monster dies.
        # If given, this *replaces* the exp/gold giving code, making those
        # entries useless.
        self.on_death = []

    def reset(self) -> None:
        """Resets the monster for a battle"""
        self.hp = self.maxhp


monsters: list[Monster] = []

# ? Maybe rename monster groups to 'encounters'
monster_groups: list[MonsterGroup] = []


def monster_name_to_index(name: str) -> int:
    """Given the name of a monster, return the index in the monsters[] array"""
    for i in range(len(monsters)):
        if name.lower() == monsters[i].name.lower():
            return i
    ic("monster " + name + " not found in monsters directory.")
    return -1


def find_level_monster(level: int) -> int:
    """
    Find an appropriate monster group for the given (zgrid) dungeon level

    Args:
        level (int): The zgrid level of the dungeon.

    Returns:
        int: The index of the monster group in the monster_groups list, or -1 if no monsters are available.
    """
    # Pick a random entry in the monster table of the map.
    if len(config.MAPS[level].monster) == 0:
        return -1
    mon_name = config.MAPS[level].monster[int(random() * len(config.MAPS[level].monster))]
    # Take the monster name, and find the monsters[] index.
    for i in range(len(monster_groups)):
        if mon_name.lower() == monster_groups[i].name.lower():
            return i
    ic("monster " + mon_name + " not found in monsters directory.")
    return -1


def read_monster() -> None:
    """
    Read monsters directory, and place in monsters[]. This is called on startup.

    TODO should be part of the module loading process?
    """
    # put the names of the available monsters in array_monsters.
    array_monsters = listdir(config.MODULES_DIR + "/data/monsters")

    # remove all .* files.
    i = 0
    while i < len(array_monsters):
        extension_start = len(array_monsters[i]) - 4
        if extension_start <= 0 or array_monsters[i][:1] == "." or array_monsters[i][extension_start : extension_start + 4] != ".txt":
            array_monsters.pop(i)
        else:
            i += 1

    # go through all monsters, adding them to our knowledge.
    for monster_filename in array_monsters:
        addmonster(monster_filename)

    # Now read and interpret monsters.txt for grouping information.
    global monster_groups
    monster_groups = []
    cur_group = -1
    monster_file = g.read_script_file("/data/monsters.txt")

    # go through all lines of the file
    for monster_line in monster_file:
        if monster_line[:1] == ":":
            monster_groups.append(MonsterGroup(monster_line[1:]))
            cur_group += 1
            continue
        monster_command = monster_line.split("=")[0].strip().lower()
        monster_command2 = monster_line.split("=", 1)[1].strip()
        if monster_command == "monster":
            monster_groups[cur_group].monster_list.append(monster_command2)
        elif monster_command == "attack":
            monster_groups[cur_group].attack_message = monster_command2
        elif monster_command == "x_pos":
            for entry in monster_command2.split(","):
                monster_groups[cur_group].x_pos.append(int(entry.strip()))
        elif monster_command == "y_pos":
            for entry in monster_command2.split(","):
                monster_groups[cur_group].y_pos.append(int(entry.strip()))


def addmonster(filename: str) -> None:
    """
    Given a filename, open and interpret the monster

    Filename should be relative to {config.MODULES_DIR}/data/monsters

    Args:
        filename (str): The name of the monster file to read.
    """
    global monsters

    temp_name = ""
    temp_hp = 0
    temp_attack = 0
    temp_defense = 0
    temp_exp = 0
    temp_gold = 0
    temp_description = ""
    temp_on_death = []

    curr_mode = 0  # are we reading in a script (1) or variables (0)?

    monster_file = g.read_script_file("/data/monsters/" + filename)
    # go through all lines of the file
    for fline in monster_file:
        monster_line = fline.strip()

        if curr_mode == 1:
            temp_on_death.append(monster_line)
            continue

        monster_command = monster_line.split("=", 2)[0].strip()
        if monster_command.lower() == "name":
            temp_name = monster_line.split("=", 1)[1]
        elif monster_command.lower() == "hp":
            temp_hp = monster_line.split("=", 1)[1]
        elif monster_command.lower() == "attack":
            temp_attack = monster_line.split("=", 1)[1]
        elif monster_command.lower() == "defense":
            temp_defense = monster_line.split("=", 1)[1]
        elif monster_command.lower() == "exp":
            temp_exp = monster_line.split("=", 1)[1]
        elif monster_command.lower() == "gold":
            temp_gold = monster_line.split("=", 1)[1]
        elif monster_command.lower() == "description":
            temp_description = monster_line.split("=", 1)[1]
        elif monster_command.lower() == ":on_death":
            curr_mode = 1
        else:
            ic("bad line of " + monster_line + " found in " + filename)

    monsters.append(Monster(temp_name, temp_hp, temp_attack, temp_defense, temp_exp, temp_gold, temp_description))

    for line in temp_on_death:
        monsters[len(monsters) - 1].on_death.append(line)


def copy_monster(from_monster: Monster) -> Monster:
    """
    Copies an instance of a monster class to another instance

    # TODO this should just be a class method or copy constructor

    Args:
        from_monster (Monster): The monster to copy.

    Returns:
        Monster: A new instance of the monster with the same attributes.
    """
    to_monster = Monster(
        from_monster.name,
        from_monster.maxhp,
        from_monster.attack,
        from_monster.defense,
        from_monster.exp,
        from_monster.gold,
        from_monster.description,
    )
    for line in from_monster.on_death:
        to_monster.on_death.append(line)

    to_monster.hp = from_monster.hp
    return to_monster
