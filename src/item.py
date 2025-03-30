"""This file contains the item/inv structures and functions."""

from os import listdir

import config
import g


# Item definition.
class Item:

    """Item definition"""

    def __init__(self,
        name: str,
        type: int,
        qual: int,
        price: int,
        val: int,
        desc: str,
        img_name: str,
        bonuses: tuple[int, int, int, int],
        script: list[str]) -> None:
        """"""
        self.name = name
        # type is 0-5 for equipment, 10-20 for items, and 99 for system items.
        # type 10 is unusable (use for story items/keys) 11 is healing, 12 is
        # explosive, 14 is gems, 15-17 is scripted (15=usable in battle,
        # 16=usable out of battle, 17=usable in both).
        self.type = type
        # The power of the item.
        self.quality = qual
        # If price is 0, the item is un sell/buy/drop able. (For story items.)
        self.price = price
        # value is how much you can sell it for, vs. price is the cost to buy
        self.value = val
        self.description = desc
        self.picturename = img_name
        self.hp_bonus = bonuses[0]
        self.ep_bonus = bonuses[1]
        self.attack_bonus = bonuses[2]
        self.defense_bonus = bonuses[3]
        # An array of lines, describing the scripting run when the item is used.
        self.scripting = script


class DroppedItem:

    """An array of dropped items. Used for keeping dropped items around through save/loads."""

    def __init__(self, name: str, pos: tuple[int, int], mapname: str) -> None:
        """"""
        self.name = name
        self.x = pos[0]
        self.y = pos[1]
        self.mapname = mapname


# Item arrays. Each item is a separate element in the array. Each element is
# a member of the class Item. See the start of this file for details.
# Duplicate item names are bad.
item: list[Item] = []
dropped_items: list[DroppedItem] = []

# inventory: 28 spaces.
# An array of numbers, which are either the index of the
# item in the item[] array, or -1 for empty.
inv = []
for x in range(28):
    inv.append(-1)


def find_inv_item(num: int) -> int:
    """
    Find an item in the inventory

    Given an index in the item[] array, return the index of the first occurance in the inv[] array

    Args:
        num (int): The index in the item[] array

    Returns:
        int: The index of the first occurance in the inv; -1 for failure
    """
    for i in range(len(inv)):
        if inv[i] == num:
            return i
    return -1


def take_inv_item(num: int) -> int:
    """
    Takes the index of an item in the item[] array, and places it in the first empty spot in the inv[] array

    Args:
        num (int): An index of the item from the item[] array

    Retuns:
        (int): Index of inv[] item is placed at; -1 for failure
    """
    for i in range(len(inv)):
        if inv[i] == -1:
            inv[i] = num
            return i
    return -1


def drop_inv_item(num: int) -> None:
    """
    Takes the index of an item in the inv[] array, removes it, then removes the empty space

    Args:
        num (int): The index of the item in the inv[] array
    """
    inv[num] = -1
    for i in range(num + 1, len(inv)):
        inv[i - 1] = inv[i]
    inv[len(inv) - 1] = -1


def finditem(name: str) -> int:
    """
    Find an item in the item[] array

    Args:
        name (str): The name of the item to find

    Returns:
        int: The index of the item in the item[] array; -1 if not found
    """
    tmpname = name.lower()
    for i in range(len(item)):
        if tmpname == item[i].name.lower():
            return i
    return -1


def read_items() -> None:
    """Read items directory; called on startup"""
    # Put the names of the available items in array_items.
    array_items = listdir(config.MODULES_DIR + "/data/items")

    # remove all .* files.
    i = 0
    while i < len(array_items):
        extension_start = len(array_items[i]) - 4
        if extension_start <= 0 or array_items[i][:1] == "." or array_items[i][extension_start : extension_start + 4] != ".txt":
            array_items.pop(i)
        else:
            i += 1

    # go through all items, adding them to our knowledge.
    for item_filename in array_items:
        additem(item_filename)


def additem(item_filename: str) -> None:
    """
    Given the filename of an item, load the data into the item array

    Args:
        item_filename (str): The filename of the item to load
    """
    global item

    item.append(Item("", 0, 0, -1, -1, "", None, (0, 0, 0, 0), []))
    item_array_loc = len(item) - 1

    # default values
    item[item_array_loc].name = ""
    item[item_array_loc].type = 0
    item[item_array_loc].quality = 0
    item[item_array_loc].price = -1
    item[item_array_loc].value = -1
    item[item_array_loc].description = ""
    item[item_array_loc].picturename = None
    item[item_array_loc].scripting = []

    item_file = g.read_script_file("/data/items/" + item_filename)

    # go through all lines of the file
    cur_line = 0
    while cur_line < len(item_file):
        # strip out spaces/tabs
        item_line = item_file[cur_line]
        item_line = item_line.strip()

        # determine the command entered.
        item_command = item_line.split("=", 2)[0]
        item_command = item_command.strip()
        if item_command.lower() == "name":
            item[item_array_loc].name = str(item_line.split("=", 1)[1])
        elif item_command.lower() == "type":
            item[item_array_loc].type = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "quality":
            item[item_array_loc].quality = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "price":
            item[item_array_loc].price = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "value":
            item[item_array_loc].value = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "description":
            item[item_array_loc].description = str(item_line.split("=", 1)[1])
        elif item_command.lower() == "picture":
            item[item_array_loc].picturename = str(item_line.split("=", 1)[1])
        elif item_command.lower() == "hp_bonus":
            item[item_array_loc].hp_bonus = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "ep_bonus":
            item[item_array_loc].ep_bonus = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "attack_bonus":
            item[item_array_loc].attack_bonus = int(item_line.split("=", 1)[1])
        elif item_command.lower() == "defense_bonus":
            item[item_array_loc].defense_bonus = int(item_line.split("=", 1)[1])
        elif item_command.lower() == ":scripting":
            cur_line += 1
            while cur_line < len(item_file):
                item_line = item_file[cur_line]
                item_line = item_line.strip()
                if item_line.lower() == ":values":
                    break
                item[item_array_loc].scripting.append(item_line)
                cur_line += 1
        cur_line += 1
    if item[item_array_loc].value == -1:
        item[item_array_loc].value = item[item_array_loc].price
    if item[item_array_loc].price == -1:
        item[item_array_loc].price = item[item_array_loc].value


def add_dropped_item(name: str, pos: tuple[int, int], mapname: str) -> None:
    """Add a dropped item to the dropped_items array."""
    dropped_items.append(DroppedItem(name, pos, mapname))


def del_dropped_item(name: str, pos: tuple[int, int], mapname: str) -> None:
    """Delete a dropped item from the dropped_items array."""
    x, y = pos
    for i in range(len(dropped_items)):
        if (
            dropped_items[i].name == name
            and dropped_items[i].x == x
            and dropped_items[i].y == y
            and dropped_items[i].mapname == mapname
        ):
            del dropped_items[i]
            return


def load_dropped_items() -> None:
    """"""
    for dropped_item in dropped_items:
        z = g.mapname2zgrid(dropped_item.mapname)
        config.MAPS[z].field[dropped_item.y][dropped_item.x].additem(dropped_item.name)
