"""This file controls the wilderness and dungeon"""

from random import random

import pygame
from icecream import ic

import action
import battle
import config
import g
import inv
import save_mgmt
import shop
from player import player

# size, in tiles, of the main screen. While this is adjustable,
# odd numbers would work much better. (To keep the player centered.)
mapsizex = 31
mapsizey = 23

width = 20
iconsize = 20

# division is nasty. Only do it once. Used for centering items on the player.
half_mapx = int(mapsizex / 2)
half_mapy = int(mapsizey / 2)

# used for yes/no dialog boxes.
active_button = 0

# used to prevent drawing problems.
global already_refreshed
already_refreshed = 0

# max number of messages to keep.
max_messages = 25

# number of free moves after attack left.
global free_move

# Image used for the inventory icon.
inv_icon_image = "inv.png"
quit_icon_image = "quit.png"
save_icon_image = "save.png"
scroller_icon_image = "scroller.png"

global message_array
message_array = []
global curr_message_num
curr_message_num = 0


global map_canvas
map_canvas = pygame.Surface((1, 1))
global map_over_canvas
map_over_canvas = pygame.Surface((1, 1))
global map_under_canvas
map_under_canvas = pygame.Surface((1, 1))

global key_down
key_down = [False, False, False, False]


# Print a message in status box. Works with ~Action~ embedded commands.
def print_message(message):
    global curr_message_num
    global message_array
    curr_message_num += 1
    if curr_message_num > 5:
        curr_message_num -= 6
    try:
        message = action.interpret_line(message)
        message_array.append(message)

        while len(message_array) > max_messages:
            message_array.pop(0)
        refresh_message_box()
        return 1
    except NameError:
        return 0


def refresh_message_box():
    g.create_norm_box((0, g.screen_size[1] - 64), (g.screen_size[0] * 3 / 5, 64), "black", "dh_green")

    message_start = g.screen_size[1] - 62
    for message in message_array[-5:]:
        g.print_string(g.screen, message, g.font, (5, message_start), width=g.screen_size[0] * 3 / 5 - 5)
        message_start += 12
    g.unclean_screen = True


# save game
def save_game():
    if action.has_dialog == 1:
        return 0
    save_mgmt.savegame(player.name)
    print_message("** Game Saved **")


# determine if the player is dead, and, if so, end the game.
def dead_yet():
    # did you die?
    if player.hp <= 0:
        action.run_command(g.xgrid, g.ygrid, g.zgrid, "die()")
        return 1
    return 0


# back to main menu. Called on death.
def close_window(event=0):
    if action.has_dialog == 1:
        return None
    if player.hp < 1:
        cleanup()
        return 1
    if show_yesno("Leave this game?", False):
        return 1
    refreshmap()
    return 0


# Activate any scripting associated with a tile. X and Y are absolute coords.
# Assumes scripting stored in maps[zgrid].field[y][x].actions[]
def activate_scripting(x, y, z):
    return_num = 0
    temp_zgrid = z

    # Make sure this is a "real" tile:
    if (
        z < 0
        or x < 0
        or y < 0
        or z >= len(g.maps)
        or y >= len(g.maps[g.zgrid].field)
        or x >= len(g.maps[g.zgrid].field[y])
    ):
        return

    itemnum = 0
    while itemnum < len(g.maps[g.zgrid].field[y][x].items):
        itemname = g.maps[g.zgrid].field[y][x].items[itemnum]
        if action.run_command(x, y, z, 'find("' + itemname + '", "a")'):
            g.maps[g.zgrid].del_item(itemname, x, y)
            refresh_tile(x, y, g.zgrid)
            refresh_inv_icon()
            refresh_bars()
        else:
            itemnum += 1

    # if there are no actions, leave immediately
    if len(g.maps[temp_zgrid].field[y][x].actions) == 0:
        return

    # go through all action lines.
    action.activate_lines(x, y, temp_zgrid, g.maps[temp_zgrid].field[y][x].actions)


# redraws the main map. Call after moving.
def refreshmap():
    # redraw the tiles

    redisplay_map()
    refreshhero()
    refresh_inv_icon()
    refresh_bars()
    refresh_message_box()
    g.unclean_screen = True


# refreshes the stat display in the lower-right.
def refresh_inv_icon(redisplay=0):
    info_top_x = mapsizex * config.TILESIZE - 3 * iconsize
    info_top_y = mapsizey * config.TILESIZE - 7 * iconsize
    info_bottom_x = mapsizex * config.TILESIZE
    info_bottom_y = mapsizey * config.TILESIZE - iconsize
    top_of_buttons = mapsizey * config.TILESIZE - iconsize

    g.create_norm_box((info_top_x, info_top_y), (3 * iconsize, 7 * iconsize), "black", "dh_green")

    g.screen.blit(g.icons[inv_icon_image], (mapsizex * config.TILESIZE - 3 * iconsize, top_of_buttons))
    g.screen.blit(g.icons[quit_icon_image], (mapsizex * config.TILESIZE - iconsize, top_of_buttons))
    g.screen.blit(g.icons[save_icon_image], (mapsizex * config.TILESIZE - 2 * iconsize, top_of_buttons))

    icon_x = info_top_x + 5
    icon_y = info_top_y + 5

    g.screen.blit(g.icons["attack.png"], (icon_x, icon_y))
    icon_y += iconsize
    g.screen.blit(g.icons["defense.png"], (icon_x, icon_y))
    icon_y += iconsize
    g.screen.blit(g.icons["gold.png"], (icon_x, icon_y))
    icon_y += iconsize
    g.screen.blit(g.icons["level.png"], (icon_x, icon_y))
    icon_y += iconsize
    g.screen.blit(g.icons["xp.png"], (icon_x, icon_y))
    icon_y += iconsize

    stats_x = info_top_x + iconsize + 10
    stats_y = info_top_y + 7

    g.print_string(g.screen, str(player.adj_attack), g.font, (stats_x, stats_y))
    stats_y += iconsize
    g.print_string(g.screen, str(player.adj_defense), g.font, (stats_x, stats_y))
    stats_y += iconsize
    g.print_string(g.screen, str(player.gold), g.font, (stats_x, stats_y))
    stats_y += iconsize
    g.print_string(g.screen, str(player.level), g.font, (stats_x, stats_y))
    stats_y += iconsize
    g.print_string(g.screen, str(player.exp), g.font, (stats_x, stats_y))
    stats_y += iconsize


def refresh_bars():
    start_width = g.screen_size[0] - 3 * iconsize
    start_height = g.screen_size[1] - 7 * iconsize - 11
    g.create_norm_box((start_width, start_height), (3 * iconsize, 6), "black", "hp_red")
    hpbar_width = 3 * iconsize * player.hp / player.adj_maxhp
    g.create_norm_box((start_width, start_height), (hpbar_width, 6), "black", "hp_green")

    g.create_norm_box((start_width, start_height + 5), (3 * iconsize, 6), "black", "hp_red")
    epbar_width = 3 * iconsize * player.ep / player.adj_maxep
    g.create_norm_box((start_width, start_height + 5), (epbar_width, 6), "black", "ep_blue")


# given x and y (absolute coods.) refresh the given tile. (ADJUST FOR PARTIAL)
def refresh_tile(x, y, input_zgrid, xshift=0, yshift=0):
    for picture in findtile(x, y, input_zgrid):
        map_canvas.blit(
            picture, ((x + half_mapx + 1 + xshift) * config.TILESIZE, (y + half_mapy + 1 + yshift) * config.TILESIZE)
        )
    for picture in findovertile(x, y, input_zgrid):
        map_over_canvas.blit(
            picture, ((x + half_mapx + 1 + xshift) * config.TILESIZE, (y + half_mapy + 1 + yshift) * config.TILESIZE)
        )


# refreshs the hero; faster than refreshing the whole map.
def refreshhero():
    for picture in findtile(g.xgrid, g.ygrid, g.zgrid):
        g.screen.blit(picture, ((mapsizex / 2) * config.TILESIZE, (mapsizey / 2) * config.TILESIZE))

    if player.cur_hero not in g.tiles:
        ic(f"Warning: Hero {player.cur_hero} not found!")
        return

    g.screen.blit(g.tiles[player.cur_hero], ((mapsizex / 2) * config.TILESIZE, (mapsizey / 2) * config.TILESIZE))
    for picture in g.maps[g.zgrid].field[g.ygrid][g.xgrid].addoverpix:
        g.screen.blit(picture, ((mapsizex / 2) * config.TILESIZE, (mapsizey / 2) * config.TILESIZE))


# called to process the onload portion of a level. Called whenever entering
# a level. Set g.zgrid properly before calling, or use input_zgrid.
# Onlypartial is used when you only need to draw part of the map.
# set each one to 5 (for all), 8 (for only north), 7 (for only northwest) and so
# on. Note that this maches up to the arangement of numbers on a keypad.
# This variable is meant to be used for drawing bordering levels.
def process_onload(recurse=True, input_zgrid=-1, onlypartial=5, rootzgrid=-1):
    if config.DEBUG:
        tmp_time = pygame.time.get_ticks()
        if onlypartial == 5:
            ic(f"Entering level {g.maps[g.zgrid].name}")

    if input_zgrid == -1:
        input_zgrid = g.zgrid
    map_size = (
        config.TILESIZE * (len(g.maps[input_zgrid].field[0]) + mapsizex + 1),
        config.TILESIZE * (len(g.maps[input_zgrid].field) + mapsizey + 1),
    )

    global map_canvas

    if g.maps[input_zgrid].under_level != "":
        process_onload(False, g.mapname2zgrid(g.maps[input_zgrid].under_level))

    # over_canvas
    if onlypartial == 5:
        global map_over_canvas
        map_over_canvas = pygame.Surface(map_size).convert_alpha()
        map_over_canvas.fill((0, 0, 0, 0))

    # xy shift
    xshift = 0
    yshift = 0
    if onlypartial == 1:  # upright
        xshift = len(g.maps[rootzgrid].field[0])
        yshift = -len(g.maps[rootzgrid].field)
    elif onlypartial == 2:  # up
        yshift = -len(g.maps[rootzgrid].field)
    if onlypartial == 3:  # upleft
        xshift = -len(g.maps[rootzgrid].field[0])
        yshift = -len(g.maps[rootzgrid].field)
    elif onlypartial == 4:  # right
        xshift = len(g.maps[rootzgrid].field[0])
    elif onlypartial == 6:  # left
        xshift = -len(g.maps[rootzgrid].field[0])
    elif onlypartial == 7:  # downright
        xshift = len(g.maps[rootzgrid].field[0])
        yshift = len(g.maps[rootzgrid].field)
    elif onlypartial == 8:  # down
        yshift = len(g.maps[rootzgrid].field)
    elif onlypartial == 9:  # downleft
        xshift = -len(g.maps[rootzgrid].field[0])
        yshift = len(g.maps[rootzgrid].field)

    # set y range:
    if onlypartial < 4:
        rangey = range(len(g.maps[input_zgrid].field) - half_mapy - 1, len(g.maps[input_zgrid].field))
    elif onlypartial > 6:
        rangey = range(0, half_mapy + 1)
    elif onlypartial != 5:
        rangey = range(0, len(g.maps[input_zgrid].field))
    else:
        rangey = range(-1 * half_mapy - 1, len(g.maps[input_zgrid].field) + half_mapy + 1)

    # set x range
    if onlypartial == 1 or onlypartial == 4 or onlypartial == 7:
        rangex = range(0, (half_mapx + 1))
    elif onlypartial == 3 or onlypartial == 6 or onlypartial == 9:
        rangex = range(len(g.maps[input_zgrid].field[0]) - (half_mapx + 1), len(g.maps[input_zgrid].field[0]))
    elif onlypartial != 5:
        rangex = range(0, len(g.maps[input_zgrid].field[0]))
    else:
        rangex = range(-1 * half_mapx - 1, len(g.maps[input_zgrid].field[0]) + half_mapx + 1)

    for y in range(len(g.maps[input_zgrid].field)):
        for x in range(len(g.maps[input_zgrid].field[y])):
            g.maps[input_zgrid].field[y][x].addpix = []
            g.maps[input_zgrid].field[y][x].addoverpix = []
            action.activate_lines(x, y, input_zgrid, g.maps[input_zgrid].field[y][x].onload)
            if dead_yet() == 1:
                break

    # fill in map.
    for y in rangey:
        for x in rangex:
            refresh_tile(x, y, input_zgrid, xshift, yshift)

    # take care of tiled maps.
    if g.maps[input_zgrid].left_level != "" and recurse:  # left
        left_zgrid = g.mapname2zgrid(g.maps[input_zgrid].left_level)
        process_onload(False, left_zgrid, 6, input_zgrid)
    if g.maps[input_zgrid].right_level != "" and recurse:  # right
        right_zgrid = g.mapname2zgrid(g.maps[input_zgrid].right_level)
        process_onload(False, right_zgrid, 4, input_zgrid)
    if g.maps[input_zgrid].up_level != "" and recurse:  # up
        up_zgrid = g.mapname2zgrid(g.maps[input_zgrid].up_level)
        process_onload(False, up_zgrid, 2, input_zgrid)
    if g.maps[input_zgrid].down_level != "" and recurse:  # down
        down_zgrid = g.mapname2zgrid(g.maps[input_zgrid].down_level)
        process_onload(False, down_zgrid, 8, input_zgrid)
    # Take care of tiled levels. (Diagonal sections.)
    if g.maps[input_zgrid].upleft_level != "" and recurse:  # upleft
        upleft_zgrid = g.mapname2zgrid(g.maps[input_zgrid].upleft_level)
        process_onload(False, upleft_zgrid, 3, input_zgrid)
    if g.maps[input_zgrid].upright_level != "" and recurse:  # upright
        upright_zgrid = g.mapname2zgrid(g.maps[input_zgrid].upright_level)
        process_onload(False, upright_zgrid, 1, input_zgrid)
    if g.maps[input_zgrid].downleft_level != "" and recurse:  # downleft
        downleft_zgrid = g.mapname2zgrid(g.maps[input_zgrid].downleft_level)
        process_onload(False, downleft_zgrid, 9, input_zgrid)
    if g.maps[input_zgrid].downright_level != "" and recurse:  # downright
        downright_zgrid = g.mapname2zgrid(g.maps[input_zgrid].downright_level)
        process_onload(False, downright_zgrid, 7, input_zgrid)
    global free_move
    free_move = 1
    if config.DEBUG:
        ic("loaded " + str(input_zgrid) + " in " + str(pygame.time.get_ticks() - tmp_time))


def debug_print_level():
    if config.DEBUG:
        pygame.image.save(map_canvas, "templevel.bmp")
        ic("Saved level to templevel.bmp")


def redisplay_map(x=0, y=0):

    if (x == 0 and y == 0) or player.hp <= 0:
        g.screen.blit(map_canvas, (-(g.xgrid + 1) * config.TILESIZE, -(g.ygrid + 1) * config.TILESIZE))
        g.screen.blit(map_over_canvas, (-(g.xgrid + 1) * config.TILESIZE, -(g.ygrid + 1) * config.TILESIZE))
    else:
        tmp_msg_scroller = pygame.Surface((384, 64))
        tmp_stat_box = pygame.Surface((60, 151))
        tmp_msg_scroller.blit(g.screen, (0, 0), (0, 416, 384, 64))
        tmp_stat_box.blit(g.screen, (0, 0), (580, 329, 60, 151))
        for i in range(16):
            tmp_time2 = pygame.time.get_ticks()
            g.screen.blit(
                map_canvas,
                (0, 0),
                (
                    (g.xgrid - x + 1) * config.TILESIZE + i * x * 2,
                    (g.ygrid - y + 1) * config.TILESIZE + i * y * 2,
                    g.screen_size[0],
                    g.screen_size[1],
                ),
            )
            tmp_key = player.cur_hero[:-4] + "_" + str(i % 2) + player.cur_hero[-4:]
            if tmp_key in g.tiles:
                g.screen.blit(
                    g.tiles[tmp_key],
                    ((mapsizex / 2) * config.TILESIZE, (mapsizey / 2) * config.TILESIZE),
                )
            elif player.cur_hero in g.tiles:
                g.screen.blit(
                    g.tiles[player.cur_hero], ((mapsizex / 2) * config.TILESIZE, (mapsizey / 2) * config.TILESIZE)
                )
            g.screen.blit(
                map_over_canvas,
                (g.screen_size[0] / 2 - config.TILESIZE, g.screen_size[1] / 2 - config.TILESIZE),
                (
                    (g.xgrid - x + 1) * config.TILESIZE + i * x * 2 + g.screen_size[0] / 2 - config.TILESIZE,
                    (g.ygrid - y + 1) * config.TILESIZE + i * y * 2 + g.screen_size[1] / 2 - config.TILESIZE,
                    config.TILESIZE * 3,
                    config.TILESIZE * 3,
                ),
            )
            g.screen.blit(tmp_msg_scroller, (0, 416))
            g.screen.blit(tmp_stat_box, (580, 329))
            pygame.display.flip()
    g.screen.blit(map_canvas, (-(g.xgrid + 1) * config.TILESIZE, -(g.ygrid + 1) * config.TILESIZE))
    g.screen.blit(map_over_canvas, (-(g.xgrid + 1) * config.TILESIZE, -(g.ygrid + 1) * config.TILESIZE))
    refreshhero()
    g.unclean_screen = True


# Return an array of pictures that the given tile should display.
# x and y are absolute coords.
def findtile(x, y, input_zgrid):
    testing = 0
    returnpix = []
    # If dealing with an off-map area, grab the nearest known tile.
    x = max(x, 0)
    y = max(y, 0)
    if y >= len(g.maps[input_zgrid].field):
        y = len(g.maps[input_zgrid].field) - 1
    if x >= len(g.maps[input_zgrid].field[y]):
        x = len(g.maps[input_zgrid].field[y]) - 1
    try:
        # This should not (normally) fail.
        if g.maps[input_zgrid].field[y][x].pix != "":
            returnpix.append(g.maps[input_zgrid].field[y][x].pix)
        for picture in g.maps[input_zgrid].field[y][x].addpix:
            returnpix.append(picture)
        for itemname in g.maps[input_zgrid].field[y][x].items:
            returnpix.append(g.tiles[g.item.item[g.item.finditem(itemname)].picturename])
        for picture in g.maps[input_zgrid].field[y][x].addoverpix:
            returnpix.append(picture)
        return returnpix
    except IndexError:
        # If it fails, there is rock there.
        returnpix.append(g.maps[input_zgrid].field[0][0].pix)
        return returnpix
    except KeyError:
        # if the author forgot to define the tile, point out the mistake.
        ic(
            "Tile of "
            + g.maps[input_zgrid].field[y][x].name
            + " is not defined"
            + " in map "
            + g.maps[input_zgrid].name
        )
        returnpix.append(g.maps[input_zgrid].field[0][0].pix)
        return returnpix


def findovertile(x, y, input_zgrid):
    testing = 0
    returnpix = []
    # If dealing with an off-map area, return nothing
    if x < 0:
        return []
    if y < 0:
        return []
    if y >= len(g.maps[input_zgrid].field):
        return []
    if x >= len(g.maps[input_zgrid].field[y]):
        return []
    try:
        # This should not (normally) fail.
        for picture in g.maps[input_zgrid].field[y][x].addoverpix:
            returnpix.append(picture)
        return returnpix
    except IndexError:
        # If it fails, there is rock there.
        return []
    except KeyError:
        # if the author forgot to define the tile, point out the mistake.
        ic("Tile is not defined in map " + g.maps[input_zgrid].name)
        returnpix.append(g.maps[input_zgrid].field[0][0].pix)
        return returnpix


# movement commands. Check to see if window_main is visible, and if there is no
# dialog box showing, then if travel is possible to a spot, move there.
# requires the change in xy coordinates. Called with move_north and the like.
def move_hero(x, y):
    global movement_done
    tempy = g.ygrid + y
    tempx = g.xgrid + x

    # check for either the main window not existing, or a current dialog
    if action.has_dialog == 1:
        return
    # check for any objects of interest. Called before moving, in case
    # the scripting changes the walkable status.
    testing_time = pygame.time.get_ticks()
    activate_scripting(tempx, tempy, g.zgrid)

    # I need to re-grab the xy loc in case a move command was in the scripting
    tempy = g.ygrid + y
    tempx = g.xgrid + x

    if g.iswalkable(tempx, tempy, x, y):
        if config.ALLOW_MOVE:
            g.xgrid = g.xgrid + x
            g.ygrid = g.ygrid + y
            passturn()
            if g.allow_change_hero == 1:
                if y == -1:
                    player.cur_hero = "people/hero_n" + g.maps[g.zgrid].hero_suffix + ".png"
                if y == 1:
                    player.cur_hero = "people/hero_s" + g.maps[g.zgrid].hero_suffix + ".png"
                if x == -1:
                    player.cur_hero = "people/hero_w" + g.maps[g.zgrid].hero_suffix + ".png"
                if x == 1:
                    player.cur_hero = "people/hero_e" + g.maps[g.zgrid].hero_suffix + ".png"
            g.allow_change_hero = 1
            # Sometimes, quick refresh is bad.
            global already_refreshed
            if already_refreshed == 1:
                refreshhero()
                already_refreshed = 0
                return

            # quick refresh.
            # Moves the canvas over a bit
            redisplay_map(x, y)
            # Refreshes the new part.
            config.ALLOW_MOVE = True
            refresh_inv_icon()
            refresh_bars()
            refresh_message_box()

    else:
        redisplay_later = False
        if tempx < 0 and g.maps[g.zgrid].left_level != "":  # left
            new_zgrid = g.mapname2zgrid(g.maps[g.zgrid].left_level)
            if g.maps[new_zgrid].field[g.ygrid][len(g.maps[new_zgrid].field[g.ygrid]) - 1].walk != 0:
                g.action.script_move(
                    g.xgrid,
                    g.ygrid,
                    g.zgrid,
                    [
                        ['"' + g.maps[g.zgrid].left_level + '"', 1],
                        [len(g.maps[new_zgrid].field[g.ygrid]) - 1, 0],
                        [g.ygrid, 0],
                    ],
                )
                player.cur_hero = "people/hero_w"
                redisplay_later = True
        elif tempy < 0 and g.maps[g.zgrid].up_level != "":  # up
            new_zgrid = g.mapname2zgrid(g.maps[g.zgrid].up_level)
            if g.maps[new_zgrid].field[len(g.maps[new_zgrid].field) - 1][g.xgrid].walk != 0:
                g.action.script_move(
                    g.xgrid,
                    g.ygrid,
                    g.zgrid,
                    [['"' + g.maps[g.zgrid].up_level + '"', 1], [g.xgrid, 0], [len(g.maps[new_zgrid].field) - 1, 0]],
                )
                player.cur_hero = "people/hero_n"
                redisplay_later = True
        elif tempx >= len(g.maps[g.zgrid].field[0]) and g.maps[g.zgrid].right_level != "":  # right
            new_zgrid = g.mapname2zgrid(g.maps[g.zgrid].right_level)
            if g.maps[new_zgrid].field[g.ygrid][0].walk != 0:
                g.action.script_move(
                    g.xgrid, g.ygrid, g.zgrid, [['"' + g.maps[g.zgrid].right_level + '"', 1], [0, 0], [g.ygrid, 0]]
                )
                player.cur_hero = "people/hero_e"
                redisplay_later = True
        elif tempy >= len(g.maps[g.zgrid].field) and g.maps[g.zgrid].down_level != "":  # down
            new_zgrid = g.mapname2zgrid(g.maps[g.zgrid].down_level)
            if g.maps[new_zgrid].field[0][g.xgrid].walk != 0:
                g.action.script_move(
                    g.xgrid, g.ygrid, g.zgrid, [['"' + g.maps[g.zgrid].down_level + '"', 1], [g.xgrid, 0], [0, 0]]
                )
                player.cur_hero = "people/hero_s"
                redisplay_later = True
        if redisplay_later:
            player.cur_hero += g.maps[g.zgrid].hero_suffix + ".png"
            redisplay_map(x, y)
            refresh_inv_icon()
            refresh_bars()
            refresh_message_box()

        if (tempx == g.xgrid + x) and (tempy == g.ygrid + y) and (g.allow_change_hero == 1):
            if y == -1:
                player.cur_hero = "people/hero_n"
            if y == 1:
                player.cur_hero = "people/hero_s"
            if x == -1:
                player.cur_hero = "people/hero_w"
            if x == 1:
                player.cur_hero = "people/hero_e"
            player.cur_hero += g.maps[g.zgrid].hero_suffix + ".png"
        g.allow_change_hero = 1
        refreshhero()
        g.unclean_screen = True
    config.ALLOW_MOVE = True
    g.allow_change_hero = 1


# called at the end of movement. Controls the passing of time.
def passturn():
    global free_move

    # handle timed effects
    g.timestep = g.timestep + 1
    if g.timestep >= 30:
        g.timestep = g.timestep - 30

    action.activate_lines(g.xgrid, g.ygrid, g.zgrid, g.per_turn_script[g.timestep])
    if dead_yet() == 1:
        return

    # is there a monster here?
    chance = random() * 100
    # allow free moves after attack
    if free_move > 0:
        free_move = free_move - 1
        chance = 99

    if player.name == "ghostie":
        chance = 99

    if chance < 15:
        # battle
        temp = g.monster.find_level_monster(g.zgrid)
        # if there exists a monster to battle:
        if temp != -1:
            global key_down
            key_down = [False, False, False, False]
            start_battle(temp)
            if dead_yet() != 1:
                # If I don't do this, the quick refresh wigs out.
                global already_refreshed
                already_refreshed = 1


# Starts a battle. Takes the index of the monster in g.monster.monster_groups
def start_battle(mon_index):
    global free_move
    tmp = battle.begin(mon_index)
    if tmp == 1:  # if you ran, you failed
        return_num = 0
    elif tmp == 0:
        return_num = 1  # otherwise, you succeeded.
    elif tmp == "end":
        return_num = "end"
        dead_yet()
    # number of free moves after attack:
    free_move = 4
    g.cur_window = "main"
    player.reset_stats()
    refreshmap()
    bind_keys()
    return return_num


# Call to display a dialog box. Used to work with action.py.
# Note this only works if window_main is visible.
def show_dialog(line=None, txt_width=-1, allow_move=True):
    return show_popup(line, ["begin.png"], allow_move, txt_width)


# given a string, display that string, along with yes and no buttons.
def show_yesno(line="", allow_move=True):
    return show_popup(line, ["no.png", "yes.png"], allow_move)


# Ask for a string. line is the help text displayed, default_text is the text
# displayed in the textbox. Max_len is the maximum length of the text.
# Note that we always use the standard Arrows/Return arrangement, instead of the
# normal customizable keys, to prevent problems.
def ask_for_string(line="", textbox_text="", max_len=100, extra_restrict=0, allow_move=True, input_width=-1):
    # Move the array of button names to a global array. We'll need it later.
    global button_array2
    button_array2 = ["no.png", "yes.png"]
    usable_chars = "`~!@#$%^&*()-_=+|[{]};:'\",<.>/? \t"
    if extra_restrict == 1:
        usable_chars = "!-_,. "

    line = action.interpret_line(line)

    cursor_loc = len(textbox_text)
    action.has_dialog = 1
    config.ALLOW_MOVE = allow_move
    global active_button
    active_button = 1

    global key_down
    key_down = [False, False, False, False]
    # button_width_array stores the starting and ending x-coords for each button
    global button_width_array
    button_width_array = []

    # find widths
    box_width = 0
    for button_line in button_array2:
        box_width += g.buttons[button_line].get_width()
    button_width_array.append((g.screen_size[0]) / 2 - (box_width) / 2)
    for i in range(len(button_array2)):
        button_width_array.append(button_width_array[i] + g.buttons[button_array2[i]].get_width())
    text_width = 300
    if input_width != -1:
        text_width = input_width

    temp_surface = pygame.Surface((text_width, 480)).convert_alpha()
    temp_surface.fill((0, 0, 0, 0))
    num_of_lines = g.print_multiline(temp_surface, line, g.font, text_width - 10, (5, 0), "black")

    line_height = num_of_lines * 13 + 40
    line_height = max(line_height, 40)

    tmp_height = g.buttons[button_array2[0]].get_height()

    # store the appearance before displaying the box.
    restore_surface = pygame.Surface((text_width, 480))
    restore_surface.blit(g.screen, (0, 0), ((g.screen_size[0] - text_width) / 2, 0, text_width, 480))

    # create the box around the text
    g.create_norm_box(
        ((g.screen_size[0] - text_width) / 2, (g.screen_size[1] - line_height) / 2),
        (text_width, line_height),
        inner_color="dh_green",
    )
    global button_height
    button_height = (g.screen_size[1] - line_height) / 2 + line_height - 1

    g.screen.blit(temp_surface, ((g.screen_size[0] - text_width) / 2 + 5, (g.screen_size[1] - line_height) / 2 + 5))

    # create the box around the buttons
    g.create_norm_box(
        ((g.screen_size[0] - box_width) / 2, button_height), (box_width, tmp_height), inner_color="dark_green"
    )

    action.has_dialog = 0
    refresh_buttons()
    g.unclean_screen = True

    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.ALLOW_MOVE = True
                return -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    cursor_loc -= 1
                    cursor_loc = max(cursor_loc, 0)
                    g.unclean_screen = True
                elif event.key == pygame.K_RIGHT:
                    cursor_loc += 1
                    cursor_loc = min(cursor_loc, len(textbox_text))
                    g.unclean_screen = True
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    if active_button == 0:
                        active_button = 1
                    else:
                        active_button = 0
                    refresh_buttons()
                elif event.key == pygame.K_HOME:
                    cursor_loc = 0
                    g.unclean_screen = True
                elif event.key == pygame.K_END:
                    cursor_loc = len(textbox_text)
                    g.unclean_screen = True
                elif event.key == pygame.K_BACKSPACE:
                    if cursor_loc > 0:
                        textbox_text = textbox_text[: cursor_loc - 1] + textbox_text[cursor_loc:]
                        cursor_loc -= 1
                        cursor_loc = max(cursor_loc, 0)
                        g.unclean_screen = True
                elif event.key == pygame.K_DELETE:
                    if cursor_loc < len(textbox_text):
                        textbox_text = textbox_text[:cursor_loc] + textbox_text[cursor_loc + 1 :]
                        g.unclean_screen = True
                elif event.key == pygame.K_RETURN:
                    config.ALLOW_MOVE = True
                    g.screen.blit(restore_surface, ((g.screen_size[0] - text_width) / 2, 0))
                    if active_button == 1:
                        g.unclean_screen = True
                        return textbox_text
                    if active_button == 0:
                        g.unclean_screen = True
                        return -1
                elif event.key == pygame.K_ESCAPE:
                    config.ALLOW_MOVE = True
                    g.screen.blit(restore_surface, ((g.screen_size[0] - text_width) / 2, 0))
                    return -1
                else:
                    if event.unicode.isalnum() == 0:
                        if event.unicode == "":
                            break
                        if usable_chars.find(event.unicode) == -1:
                            break
                    if len(textbox_text) >= max_len:
                        break
                    textbox_text = textbox_text[:cursor_loc] + event.unicode + textbox_text[cursor_loc:]
                    cursor_loc += 1
                    g.unclean_screen = True

            elif event.type == pygame.MOUSEMOTION:
                if event.pos[1] > button_height and event.pos[1] < button_height + tmp_height:
                    change_button(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    event.pos[1] < button_height
                    or event.pos[1] > button_height + tmp_height
                    or event.pos[0] < button_width_array[0]
                    or event.pos[0] > button_width_array[-1]
                ):
                    break
                change_button(event.pos)
                if active_button != -1:
                    config.ALLOW_MOVE = True
                    g.screen.blit(restore_surface, ((g.screen_size[0] - text_width) / 2, 0))
                    if active_button == 1:
                        g.unclean_screen = True
                        return textbox_text
                    if active_button == 0:
                        g.unclean_screen = True
                        return -1

        if g.unclean_screen:
            g.unclean_screen = False
            g.create_norm_box(
                ((g.screen_size[0] - text_width) / 2 + 5, (g.screen_size[1] + line_height) / 2 - 20),
                (text_width - 10, 17),
                inner_color="light_gray",
            )
            g.print_string(
                g.screen,
                textbox_text,
                g.font,
                ((g.screen_size[0] - text_width) / 2 + 7, (g.screen_size[1] + line_height) / 2 - 18),
            )
            draw_cursor_pos = g.font.size(textbox_text[:cursor_loc].replace("\t", "     "))

            g.screen.fill(
                config.COLORS["black"],
                (
                    (g.screen_size[0] - text_width) / 2 + 7 + draw_cursor_pos[0],
                    (g.screen_size[1] + line_height) / 2 - 18,
                    1,
                    draw_cursor_pos[1],
                ),
            )
            pygame.display.flip()


# given a string and an array of buttons,
# display that string, along with the given buttons.
def show_popup(line="", button_array=[], allow_move=True, input_width=-1):
    # Move the array of button names to a global array. We'll need it later.
    global button_array2
    button_array2 = button_array
    line = action.interpret_line(line)

    action.has_dialog = 1
    config.ALLOW_MOVE = allow_move
    global active_button
    active_button = 0

    global key_down
    key_down = [False, False, False, False]
    # button_width_array stores the starting and ending x-coords for each button
    global button_width_array
    button_width_array = []

    # find widths
    box_width = 0
    for button_line in button_array2:
        box_width += g.buttons[button_line].get_width()
    button_width_array.append((g.screen_size[0]) / 2 - (box_width) / 2)
    for i in range(len(button_array2)):
        button_width_array.append(button_width_array[i] + g.buttons[button_array2[i]].get_width())
    text_width = 300
    if input_width != -1:
        text_width = input_width

    temp_surface = pygame.Surface((text_width, 480)).convert_alpha()
    temp_surface.fill((0, 0, 0, 0))
    num_of_lines = g.print_multiline(temp_surface, line, g.font, text_width - 10, (5, 0), "black")

    line_height = num_of_lines * 13 + 10
    line_height = max(line_height, 40)

    tmp_height = g.buttons[button_array2[0]].get_height()

    # store the appearance before displaying the box.
    surface_width = box_width
    if box_width < text_width:
        surface_width = text_width
    restore_surface = pygame.Surface((surface_width, 400))
    restore_surface.blit(g.screen, (0, 0), ((g.screen_size[0] - surface_width) / 2, 0, surface_width, 400))

    # create the box around the text
    g.create_norm_box(
        ((g.screen_size[0] - text_width) / 2, (g.screen_size[1] - line_height) / 2),
        (text_width, line_height),
        inner_color="dh_green",
    )
    global button_height
    button_height = (g.screen_size[1] - line_height) / 2 + line_height - 1

    g.screen.blit(temp_surface, ((g.screen_size[0] - text_width) / 2 + 5, (g.screen_size[1] - line_height) / 2 + 5))

    # create the box around the buttons
    g.create_norm_box(
        ((g.screen_size[0] - box_width) / 2, button_height), (box_width, tmp_height), inner_color="dark_green"
    )

    action.has_dialog = 0
    refresh_buttons()

    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.ALLOW_MOVE = True
                return -1
            if event.type == pygame.KEYDOWN:
                if event.key == g.bindings["up"] or event.key == g.bindings["left"]:
                    decrease_button()
                elif event.key == g.bindings["down"] or event.key == g.bindings["right"]:
                    increase_button()
                elif event.key == g.bindings["action"]:
                    config.ALLOW_MOVE = True
                    g.screen.blit(restore_surface, ((g.screen_size[0] - surface_width) / 2, 0))
                    return active_button
            elif event.type == pygame.MOUSEMOTION:
                if event.pos[1] > button_height and event.pos[1] < button_height + tmp_height:
                    change_button(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    event.pos[1] < button_height
                    or event.pos[1] > button_height + tmp_height
                    or event.pos[0] < button_width_array[0]
                    or event.pos[0] > button_width_array[-1]
                ):
                    break
                change_button(event.pos)
                if active_button != -1:
                    config.ALLOW_MOVE = True
                    g.screen.blit(restore_surface, ((g.screen_size[0] - surface_width) / 2, 0))
                    return active_button
        if g.unclean_screen:
            pygame.display.flip()


def change_button(xy):
    global active_button
    old_button = active_button
    for i in range(len(button_array2)):
        if xy[0] >= button_width_array[i] and xy[0] <= button_width_array[i + 1]:
            active_button = i
            break
    if old_button != active_button:
        refresh_buttons()


def refresh_buttons():
    global active_button
    for i in range(len(button_array2)):
        if active_button == i:
            tmp = button_array2[i][0:-4] + "_sel" + button_array2[i][-4:]
            g.screen.blit(g.buttons[tmp], (button_width_array[i], button_height))
        else:
            g.screen.blit(g.buttons[button_array2[i]], (button_width_array[i], button_height))
    g.unclean_screen = True


def increase_button():
    global active_button
    active_button += 1
    if active_button >= len(button_array2):
        active_button -= len(button_array2)
    refresh_buttons()


def decrease_button():
    global active_button
    active_button -= 1
    if active_button < 0:
        active_button += len(button_array2)
    refresh_buttons()


# Display the scripting console. This window will take scripting, then
# execute it.
def load_console():
    # Only let cheaters access the console.
    if player.name not in ["god", "testing123", "script_test", "ghostie"]:
        return 0
    global console_text
    console_text = ""

    global curr_name_loc
    curr_name_loc = 0

    tmp = ask_for_string("Enter a scripting command", "")
    if tmp == -1:
        return 0

    action.activate_lines(g.xgrid, g.ygrid, g.zgrid, g.interpret_lines([tmp]))


# If the main window is destroyed unexpectedly, try to prevent the worst errors.
def cleanup(event=None):
    g.break_one_loop = 50
    try:
        inv.leave_inv()
    except AttributeError:
        pass
    action.has_dialog = 0


# call to create window_main.
def init_window_main(is_new_game=0):
    g.load_tiles()
    global map_canvas
    tmp_map_size = (
        config.TILESIZE * (config.MAX_MAPSIZE[0] + mapsizex + 1),
        config.TILESIZE * (config.MAX_MAPSIZE[1] + mapsizey + 1),
    )

    map_canvas = pygame.Surface(tmp_map_size)

    if config.DEBUG:
        tmp_time2 = pygame.time.get_ticks()
    if not config.FASTBOOT:
        # This cuts a small amount off the loading time for each level. (From about
        # 370ms to about 270ms.)
        g.screen.fill(config.COLORS["light_gray"], (g.screen_size[0] / 2 - 150, g.screen_size[1] / 2 - 20, 300, 40))
        g.print_string(g.screen, "Processing Maps", g.font, (g.screen_size[0] / 2, g.screen_size[1] / 2), align=1)
        pygame.display.flip()
        for mapindex in range(len(g.maps)):
            g.maps[mapindex].preprocess_map(mapindex)
            g.create_norm_box(
                (g.screen_size[0] / 4 + 2, g.screen_size[1] * 2 / 3 - 10),
                (((g.screen_size[0] / 2 - 4) * mapindex) / len(g.maps), 8),
                "black",
                "ep_blue",
            )
            pygame.display.flip()
    if config.DEBUG:
        ic("Level loading time: ", pygame.time.get_ticks() - tmp_time2)

    # width of the hp/ep bars.
    g.hpbar_width = config.TILESIZE * 3

    # put in the map, and do finishing touches on the window.
    player.reset_stats()
    if is_new_game == 0 or len(g.maps) == 1:
        process_onload()
    player.cur_hero = "people/hero_w" + g.maps[g.zgrid].hero_suffix + ".png"

    top_of_buttons = mapsizey * config.TILESIZE - iconsize

    info_top_x = mapsizex * config.TILESIZE - 3 * iconsize
    info_top_y = mapsizey * config.TILESIZE - 7 * iconsize
    info_bottom_x = mapsizex * config.TILESIZE
    info_bottom_y = mapsizey * config.TILESIZE - iconsize
    icon_x = info_top_x + 5
    icon_y = info_top_y + 5
    stats_x = info_top_x + iconsize + 10
    stats_y = info_top_y + 7

    stuff_width = 3 * iconsize

    refreshmap()
    global free_move
    free_move = 0
    g.cur_window = "main"

    bind_keys()

    # call newgame script
    if is_new_game == 1:
        action.activate_lines(g.xgrid, g.ygrid, g.zgrid, g.newgame_act)
    else:
        g.allow_change_hero = 1  # needed else first move after load looks wrong
    config.ALLOW_MOVE = True

    repeat_key = 0
    global key_down
    key_down = [False, False, False, False]
    while True:
        pygame.time.wait(10)
        repeat_key += g.clock.tick()
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if key_handler_down(event.key) == 1:
                    return
                repeat_key = 140
            elif event.type == pygame.KEYUP:
                key_handler_up(event.key)
            elif event.type == pygame.MOUSEMOTION:
                mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_handler(event.pos) == 1:
                    return
        # this is after the event loop, as otherwise, moving from map to map
        # creates a timing bug that fires this once too much.
        if repeat_key > 140:
            if key_down[0]:
                key_handler(g.bindings["up"])
            elif key_down[1]:
                key_handler(g.bindings["down"])
            elif key_down[2]:
                key_handler(g.bindings["left"])
            elif key_down[3]:
                key_handler(g.bindings["right"])
            repeat_key = 0
        if g.unclean_screen:
            pygame.display.flip()


# this binds keys to the appropriate commands. Needs to be called after
# returning from various subwindows.
def bind_keys():
    pass


def key_handler_down(key_name):
    global key_down
    if key_name == g.bindings["up"]:
        key_down[0] = True
    elif key_name == g.bindings["down"]:
        key_down[1] = True
    elif key_name == g.bindings["left"]:
        key_down[2] = True
    elif key_name == g.bindings["right"]:
        key_down[3] = True
    else:
        return key_handler(key_name)


def key_handler(key_name):
    if config.DEBUG:
        tmp_time = pygame.time.get_ticks()
    global key_down
    if key_name == g.bindings["up"]:
        move_hero(0, -1)
    elif key_name == g.bindings["down"]:
        move_hero(0, 1)
    elif key_name == g.bindings["left"]:
        move_hero(-1, 0)
    elif key_name == g.bindings["right"]:
        move_hero(1, 0)
    elif key_name == g.bindings["quit"] or key_name == g.bindings["cancel"]:
        if close_window() == 1:
            return 1
    elif key_name == g.bindings["action"] or key_name == g.bindings["inv"]:
        show_inv()
    elif key_name == g.bindings["save"]:
        save_game()
    elif key_name == g.bindings["load_console"]:
        load_console()
    elif key_name == pygame.K_F10:
        debug_print_level()
    if config.DEBUG:
        ic(pygame.time.get_ticks() - tmp_time)
    return 0


def key_handler_up(key_name):
    global key_down
    if key_name == g.bindings["up"]:
        key_down[0] = False
    elif key_name == g.bindings["down"]:
        key_down[1] = False
    elif key_name == g.bindings["left"]:
        key_down[2] = False
    elif key_name == g.bindings["right"]:
        key_down[3] = False


def unbind_keys():
    pass


# handles mouse clicks on the main tile canvas.
def mouse_handler(xy):
    icon_y1 = mapsizey * config.TILESIZE - iconsize
    icon_y2 = mapsizey * config.TILESIZE

    inv_x1 = mapsizex * config.TILESIZE - 3 * iconsize
    inv_x2 = inv_x1 + iconsize
    if xy[0] > inv_x1 and xy[0] < inv_x2 and xy[1] > icon_y1 and xy[1] < icon_y2:
        show_inv()
        return 0

    save_x1 = inv_x2
    save_x2 = save_x1 + iconsize
    if xy[0] > save_x1 and xy[0] < save_x2 and xy[1] > icon_y1 and xy[1] < icon_y2:
        save_game()
        return 0

    quit_x1 = save_x2
    quit_x2 = quit_x1 + iconsize
    if xy[0] > quit_x1 and xy[0] < quit_x2 and xy[1] > icon_y1 and xy[1] < icon_y2:
        return close_window()

    if (
        xy[0] > mapsizex * config.TILESIZE - 3 * iconsize - g.buttons["scroller.png"].get_width()
        and xy[0] < mapsizex * config.TILESIZE - 3 * iconsize
        and xy[1] > mapsizey * config.TILESIZE - g.buttons["scroller.png"].get_height()
    ):
        tmpline = ""
        for line in message_array:
            tmpline += line + "\n"
        show_dialog(tmpline, 650, False)
        return 0

    # set variables, based on the shape of the main window. (tall or wide)
    if mapsizex > mapsizey:
        mapsz = mapsizey * config.TILESIZE
        mapstartx = (mapsizex * config.TILESIZE - mapsz) / 2
        mapstarty = 0
    else:
        mapsz = mapsizex * config.TILESIZE
        mapstartx = 0
        mapstarty = (mapsizey * config.TILESIZE - mapsz) / 2

    # This basically divides the screen along diagonals, then finds the
    # current quadrent of the mouse.
    if xy[0] - mapstartx < xy[1] - mapstarty:  # south or west
        if xy[0] + xy[1] > mapstartx + mapstarty + mapsz:
            move_hero(0, 1)
        else:
            move_hero(-1, 0)
    elif xy[0] + xy[1] > mapstartx + mapstarty + mapsz:  # north or east
        move_hero(1, 0)
    else:
        move_hero(0, -1)


# called whenever the mouse moves
def mouse_move(xy):
    global inv_icon_image
    global quit_icon_image
    global save_icon_image
    global scroller_icon_image

    icon_y1 = mapsizey * config.TILESIZE - iconsize
    icon_y2 = mapsizey * config.TILESIZE

    inv_x1 = mapsizex * config.TILESIZE - 3 * iconsize
    inv_x2 = inv_x1 + iconsize
    if xy[0] > inv_x1 and xy[0] < inv_x2 and xy[1] > icon_y1 and xy[1] < icon_y2:
        new_icon_image = "inv_sel.png"
    else:
        new_icon_image = "inv.png"

    save_x1 = inv_x2
    save_x2 = save_x1 + iconsize
    if xy[0] > save_x1 and xy[0] < save_x2 and xy[1] > icon_y1 and xy[1] < icon_y2:
        new_save_image = "save_sel.png"
    else:
        new_save_image = "save.png"

    quit_x1 = save_x2
    quit_x2 = quit_x1 + iconsize
    if xy[0] > quit_x1 and xy[0] < quit_x2 and xy[1] > icon_y1 and xy[1] < icon_y2:
        new_quit_image = "quit_sel.png"
    else:
        new_quit_image = "quit.png"

    if (
        xy[0] > mapsizex * config.TILESIZE - iconsize * 3 - g.buttons["scroller.png"].get_width()
        and xy[0] < mapsizex * config.TILESIZE - 3 * iconsize
        and xy[1] > mapsizey * config.TILESIZE - g.buttons["scroller.png"].get_height()
    ):
        new_scroll_icon_image = "scroller_sel.png"
    else:
        new_scroll_icon_image = "scroller.png"

    if (
        new_icon_image != inv_icon_image
        or quit_icon_image != new_quit_image
        or save_icon_image != new_save_image
        or scroller_icon_image != new_scroll_icon_image
    ):
        inv_icon_image = new_icon_image
        quit_icon_image = new_quit_image
        save_icon_image = new_save_image

        scroller_icon_image = new_scroll_icon_image
        refresh_inv_icon(1)
        pygame.display.flip()


# show the inventory.
def show_inv():
    global key_down
    key_down = [False, False, False, False]
    if action.has_dialog == 1:
        return
    inv.init_window_inv()
    refreshmap()
    refresh_bars()
    g.cur_window = "main"


def enter_store(cur_loc):
    global key_down
    key_down = [False, False, False, False]
    shop.init_window_shop(cur_loc)
    refreshmap()
    refresh_bars()
    g.cur_window = "main"
