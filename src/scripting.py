"""
    This file controls the loading of datafiles
"""

import logging
from pathlib import Path

import action
import config
import item
import utils

logger = logging.getLogger(__name__)


# map data. Class tile contains data on each tile,
# and is a subclass of map.
# Class map contains data on each map, and the tiles contained within.
class Tile:
    def __init__(self, symbol):
        """
        Create a tile definition.

        Args:
            symbol (str): The tile symbol represented by this tile.
        """
        # Filled in with a Tkinter image reference
        self.pix = ""
        # The actual filename of the tile.
        self.name = symbol
        # Can the tile be walked on?
        self.walk = 0
        # walls
        self.wall_n = 0
        self.wall_s = 0
        self.wall_e = 0
        self.wall_w = 0
        # An array of lines, describing the scripting run on load.
        self.onload = []
        # An array of lines, describing the scripting run when stepped on.
        self.actions = []
        # An array of Tkinter image references, that show extra tiles.
        self.addpix = []
        # An array of Tkinter image references, that show extra tiles for
        # over-hero graphics
        self.addoverpix = []
        # An array of item names; the items that exist on this tile.
        self.items = []

    def add_act(self, action) -> None:
        """
        Action script line on this tile.

        Args:
            action (str): Action script line.
        """
        self.actions.append(action)

    def add_onload(self, onload) -> None:
        """
        On-load script line on this tile.

        Args:
            onload (str): On-load script line.
        """
        self.onload.append(onload)

    def add_pix(self, picture) -> None:
        """
        Picture identifier to add on this tile.

        Args:
            picture (str): Picture identifier to add.
        """
        self.addpix.append(picture)

    def add_over_pix(self, picture) -> None:
        """
        Over-hero picture identifier to add on this tile.

        Args:
            picture (str): Over-hero picture identifier to add.
        """
        self.addoverpix.append(picture)

    def del_pix(self, picture) -> None:
        """
        Remove a picture identifier from this tile.

        Args:
            picture (str): Picture identifier to remove.
        """
        self.addpix.remove(picture)

    def del_over_pix(self, picture) -> None:
        """
        Remove an over-hero picture identifier from this tile.

        Args:
            picture (str): Over-hero picture identifier to remove.
        """
        self.addoverpix.remove(picture)

    def additem(self, itemname) -> None:
        """
        Add an item name to this tile.

        Args:
            itemname (str): Item name to add.
        """
        self.items.append(itemname)

    def del_item(self, itemname) -> None:
        """
        Remove an item name from this tile.

        Args:
            itemname (str): Item name to remove.
        """
        self.items.remove(itemname)


class Map:

    """"""

    def additem(self, itemname, x, y) -> None:
        """
        Place a dropped item on this map.

        Args:
            itemname (str): Name of the item to place.
            x (int): Horizontal tile coordinate.
            y (int): Vertical tile coordinate.
        """
        self.field[y][x].additem(itemname)
        item.add_dropped_item(itemname, (x, y), self.name)

    def del_item(self, itemname, x, y) -> None:
        """
        Remove a dropped item from this map.

        Args:
            itemname (str): Name of the item to remove.
            x (int): Horizontal tile coordinate.
            y (int): Vertical tile coordinate.
        """
        self.field[y][x].del_item(itemname)
        item.del_dropped_item(itemname, x, y, self.name)

    def __init__(self, mapname: Path, from_editor: int = 0) -> None:
        """
        Load a map and build its tile field.

        Args:
            mapname (Path): Path to the map data file.
            from_editor (int): Whether to preserve editor formatting; 1 enables it.
        """
        self.name = mapname.name.strip()
        self.field = []  # multidimentional array of tile class members.
        self.monster = []  # monsters that can attack on this level.

        # filename of the background image used in battles.
        # Used in the map editor, to allow resaving background.
        self.battle_background_name = ""
        # Filled in with a pygame image
        self.battle_background = ""
        # Filled in with strings
        self.under_level = ""
        self.left_level = ""
        self.right_level = ""
        self.up_level = ""
        self.down_level = ""
        self.upleft_level = ""
        self.upright_level = ""
        self.downleft_level = ""
        self.downright_level = ""

        # special hero pix
        self.hero_suffix = ""

        maptext = []  # unused after load
        self.tiles = {}  # unused after load
        self.per_tile_info = []  # unused after load

        # grab the needed data from the file
        if not self.name:
            return
        map_file = utils.read_script_file("/data/maps/" + self.name, from_editor)

        # current mode. 0 for the actual map, 1 for monsters,
        # 2 for tile defines, 3 for per-tile info
        curr_mode = 0
        current_tile = ""
        # 0 for onload, 1 for action.
        tilemode = 0
        for map_line in map_file:
            if map_line == "\n":
                continue
            map_strip = map_line.strip()
            # go through all lines of the file up to ":def"
            if curr_mode == 0:
                if map_strip == "" or map_strip[:1] == ":":
                    curr_mode = 1
                else:
                    # add the line
                    line = map_strip.split(" ")
                    maptext.append(line)

            # input monster data
            elif curr_mode == 1:
                if map_strip == "" or map_strip[:1] == ":":
                    curr_mode = 2
                else:
                    map_command = map_line.split("=", 2)[0].strip().lower()
                    if map_command == "monster":
                        self.monster.append(map_line.split("=", 1)[1].strip())
                    elif map_command == "battle_bg":
                        self.battle_background = config.BACKGROUNDS[map_line.split("=", 1)[1].strip()]
                        self.battle_background_name = map_line.split("=", 1)[1].strip()
                    elif map_command == "hero_bg":
                        self.hero_suffix = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_under":
                        self.under_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_left":
                        self.left_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_right":
                        self.right_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_up":
                        self.up_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_down":
                        self.down_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_upleft":
                        self.upleft_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_upright":
                        self.upright_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_downleft":
                        self.downleft_level = map_line.split("=", 1)[1].strip()
                    elif map_command == "level_downright":
                        self.downright_level = map_line.split("=", 1)[1].strip()
                    else:
                        logger.error("Bad command %s received!", map_command)

            # input tile data
            if curr_mode == 2:
                # if map_line == '':
                # 	break
                # if per-tile information was given
                if map_line[:2].lower() == "xy":
                    curr_mode = 3
                    continue

                # is this line giving us a new tile?
                if map_strip[:1] == ":":
                    current_tile = map_strip[1:]
                    self.tiles[current_tile] = [[], []]
                    tilemode = 0
                    continue

                if map_strip.lower() == "onload":
                    tilemode = 0
                    continue
                if map_strip.lower() == "action":
                    tilemode = 1
                    continue

                if tilemode == 0:  # onload
                    if from_editor == 1:
                        self.tiles[current_tile][0].append(map_line[:-1])
                    else:
                        self.tiles[current_tile][0].append(map_strip)
                elif from_editor == 1:
                    self.tiles[current_tile][1].append(map_line[:-1])
                else:
                    self.tiles[current_tile][1].append(map_strip)

            if curr_mode == 3:
                if map_strip == "":
                    break
                if map_strip.lower() == "tiles":  # switch back
                    curr_mode = 2
                    continue
                # is this line giving us a new tile?
                if map_strip[:1] == ":":
                    curr_x = int(map_strip[1:].split()[0].strip())
                    curr_y = int(map_strip[1:].split()[1].strip())
                    self.per_tile_info.append([curr_x, curr_y, [], []])
                    tilemode = 0
                    continue

                if map_strip.lower() == "onload":
                    tilemode = 0
                    continue
                if map_strip.lower() == "action":
                    tilemode = 1
                    continue

                if tilemode == 0:  # onload
                    self.per_tile_info[len(self.per_tile_info) - 1][2].append(map_strip)
                else:  # action
                    self.per_tile_info[len(self.per_tile_info) - 1][3].append(map_strip)
                continue

        # place the formatted data into self.field
        for cur_line, line in enumerate(maptext):
            self.field.append([])
            for cur_char, character in enumerate(line):
                self.field[cur_line].append(Tile(character))
                try:
                    for obj in self.tiles[character][0]:
                        self.field[cur_line][cur_char].onload.append(obj)
                    for obj in self.tiles[character][1]:
                        self.field[cur_line][cur_char].actions.append(obj)
                except KeyError:
                    logger.warning("Tile %s is undefined in map %s", character, self.name)

        # place the per-tile data into self.field
        for line in self.per_tile_info:
            for onload_line in line[2]:
                self.field[line[1]][line[0]].onload.append(onload_line)
            for action_line in line[3]:
                self.field[line[1]][line[0]].actions.append(action_line)
        if not self.battle_background:
            self.battle_background = config.BACKGROUNDS["generic.png"]

    def add_tile(self, tile_name):
        """
        Add a tile definition to the map.

        Args:
            tile_name (str): Symbol identifying the tile.
        """
        new_tile = Tile(tile_name)
        self.tiles[tile_name] = new_tile

    # I need to call this with zgrid as it is not stored locally.
    def preprocess_map(self, zloc):
        """
        Run eligible tile on-load commands before play.

        Args:
            zloc (int): Map index used by the action system.
        """
        for yloc in range(len(self.field)):
            for xloc in range(len(self.field[yloc])):
                if (
                    self.field[yloc][xloc].onload[0][:4].lower() == "pix("
                    or self.field[yloc][xloc].onload[0][:5].lower() == "walk("
                ):
                    action.activate_lines(xloc, yloc, zloc, [self.field[yloc][xloc].onload[0]])
                    self.field[yloc][xloc].onload.pop(0)
                    # Note that the indentation here is correct, as this prevents
                    # the corner case of an if statement in the first line from
                    # causing incorrect results.
                    if (
                        self.field[yloc][xloc].onload[0][:4].lower() == "pix("
                        or self.field[yloc][xloc].onload[0][:5].lower() == "walk("
                    ):
                        action.activate_lines(xloc, yloc, zloc, [self.field[yloc][xloc].onload[0]])
                        self.field[yloc][xloc].onload.pop(0)


endgame_act = []
wingame_act = []
newgame_act = []
levelup_act = []


# read scripts from disk, and place in *_act[]
def read_scripts():
    """Load the game-wide script files."""
    # This is a bit weird, but Python does not seem to allow the simple way.
    global endgame_act
    global wingame_act
    global newgame_act
    global levelup_act
    endgame = utils.read_script_file("/data/endgame.txt")
    wingame = utils.read_script_file("/data/wingame.txt")
    newgame = utils.read_script_file("/data/newgame.txt")
    levelup = utils.read_script_file("/data/levelup.txt")

    for line in endgame:
        endgame_act.append(line)
    for line in wingame:
        wingame_act.append(line)
    for line in newgame:
        newgame_act.append(line)
    for line in levelup:
        levelup_act.append(line)


# shop data.
class ShopItem:
    def __init__(self, name):
        """
        Create a shop entry, using item defaults when available.

        Args:
            name (str): Item name for this shop entry.
        """
        self.item_name = name
        itemnum = item.finditem(name)
        self.cost = 0
        self.value = 0
        self.buytype = "gold"
        self.power = 0
        self.description = ""
        self.actions = []
        self.picture = ""
        # if adding an actual item, initialize to the item's qualities.
        if itemnum != -1:
            self.cost = item.item[itemnum].price
            self.value = item.item[itemnum].value
            self.buytype = "gold"
            self.power = item.item[itemnum].quality
            self.description = item.item[itemnum].description
            self.picture = item.item[itemnum].picturename

    def add_cost(self, itemcost):
        """
        Set the shop entry purchase cost.

        Args:
            itemcost (str | int): The purchase cost.
        """
        self.cost = itemcost

    def add_value(self, itemvalue):
        """
        Set the shop entry sale value.

        Args:
            itemvalue (str | int): The sale value.
        """
        self.value = itemvalue

    def add_buytype(self, itembuytype):
        """
        Set the shop entry payment type.

        Args:
            itembuytype (str): Payment type.
        """
        self.buytype = itembuytype

    def add_power(self, itempower):
        """
        Set the shop entry displayed power.

        Args:
            itempower (str | int): The displayed power.
        """
        self.power = itempower

    def add_description(self, itemdescription):
        """
        Set the shop entry display description.

        Args:
            itemdescription (str): Item description.
        """
        self.description = itemdescription

    def add_act(self, action):
        """
        Add an action line to the shop entry.

        Args:
            action (str): Action line to append.
        """
        self.actions.append(action)

    def add_picture(self, picture):
        """
        Set the shop entry picture identifier.

        Args:
            picture (str): Picture identifier.
        """
        self.picture = picture


class Shop:
    def __init__(self, shopname):
        """
        Create an empty shop.

        Args:
            shopname (str): Shop name.
        """
        self.name = shopname.strip()
        self.itemlist = []
        self.curitem = -1

    def additem(self, itemname):
        """
        Add an item entry to the shop.

        Args:
            itemname (str): Name of the item to add.
        """
        self.itemlist.append(ShopItem(itemname))
        self.curitem += 1

    def item_add_cost(self, itemcost):
        """
        Set the current shop item purchase cost.

        Args:
            itemcost (str | int): The purchase cost.
        """
        self.itemlist[self.curitem].add_cost(itemcost)

    def item_add_value(self, itemvalue):
        """
        Set the current shop item sale value.

        Args:
            itemvalue (str | int): The sale value.
        """
        self.itemlist[self.curitem].add_value(itemvalue)

    def item_add_buytype(self, itembuytype):
        """
        Set the current shop item payment type.

        Args:
            itembuytype (str): Payment type.
        """
        self.itemlist[self.curitem].add_buytype(itembuytype)

    def item_add_power(self, itempower):
        """
        Set the current shop item displayed power.

        Args:
            itempower (str | int): The displayed power.
        """
        self.itemlist[self.curitem].add_power(itempower)

    def item_add_description(self, itemdescription):
        """
        Set the current shop item description.

        Args:
            itemdescription (str): Item description.
        """
        self.itemlist[self.curitem].add_description(itemdescription)

    def item_add_act(self, action):
        """
        Add an action line to the current shop item.

        Args:
            action (str): Action line to append.
        """
        self.itemlist[self.curitem].add_act(action)

    def item_add_picture(self, picture):
        """
        Set the current shop item picture identifier.

        Args:
            picture (str): Picture identifier.
        """
        self.itemlist[self.curitem].add_picture(picture)


shops = []


# read and interpret shops.txt. Must be called after read_items()
# Places data into shops[].
def read_shops():
    """Load and parse the selected module’s shop definitions."""
    # grab the needed data from the file
    shop_loc = config.MODULES_DIR + "/data/shops.txt"
    shop_file = Path(shop_loc).open()

    cur_shop = -1

    # go through all lines of the file, splitting along :Store
    shop_line = shop_file.readline()
    while shop_line != "":  # till EOF
        # strip out spaces/tabs
        shop_line = shop_line.strip()
        # ignore blank lines and comments
        if shop_line[:1] == "#" or shop_line[:1] == "":
            shop_line = shop_file.readline()
            continue

        if shop_line[:5].lower() == ":shop":
            shops.append(Shop(shop_line[5:].strip()))
            cur_shop += 1
        elif shop_line[:5].lower() == ":item":
            shops[cur_shop].additem(shop_line[5:].strip())
        else:
            command = shop_line.split("=")
            command[0].strip().lower()
            if command[0].strip().lower() == "description":
                shops[cur_shop].item_add_description(command[1].strip())
            elif command[0].strip().lower() == "cost":
                shops[cur_shop].item_add_cost(command[1].strip().lower())
            elif command[0].strip().lower() == "value":
                shops[cur_shop].item_add_value(command[1].strip().lower())
            elif command[0].strip().lower() == "buytype":
                shops[cur_shop].item_add_buytype(command[1].strip().lower())
            elif command[0].strip().lower() == "power":
                shops[cur_shop].item_add_power(command[1].strip().lower())
            elif command[0].strip().lower() == "picture":
                shops[cur_shop].item_add_picture(command[1].strip().lower())
            else:
                shops[cur_shop].item_add_act(shop_line)

        # ready another line
        shop_line = shop_file.readline()
