# loadgame.py
# Copyright (C) 2005 Free Software Foundation
# This file is part of Dragon Hunt.

# Dragon Hunt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# Dragon Hunt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Dragon Hunt; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# This file controls the load game screen. The actual load/save game
# functions are in g.loadgame/savegame

import pickle
from os import listdir, mkdir, path, remove

import pygame

import config
import g
import game_screen as pygscreen

# was a game loaded? Used to determine whether to use newgame script.
did_load = ""

saves_array = []

saves_pos = 0

prevent_dbl_load = 0

name_text = ""
hp_text = ""
ep_text = ""
attack_text = ""
defense_text = ""
gold_text = ""
exp_text = ""
level_text = ""

screen = pygscreen.get_screen()


# called when "Load" is pressed
def load_selected():
    global return_from_loadgame
    global did_load
    global prevent_dbl_load

    if len(saves_array) == 0:
        return

    if prevent_dbl_load == 1:
        return
    prevent_dbl_load = 1
    g.create_norm_box(
        (config.TILESIZE * config.MAPSIZE_X / 4, config.TILESIZE * config.MAPSIZE_Y / 3),
        (config.TILESIZE * config.MAPSIZE_X / 2, 140 + config.BUTTONS["load_scr.png"].get_height()),
    )
    g.print_string(
        screen,
        "Loading game. Please wait",
        g.font,
        (
            config.TILESIZE * config.MAPSIZE_X / 2,
            config.TILESIZE * config.MAPSIZE_Y / 3 + 70 + config.BUTTONS["load_scr.png"].get_height() / 2,
        ),
    )
    pygame.display.flip()

    did_load = saves_array[saves_pos]
    g.break_one_loop = 1


# Uses saves_pos to display infomation about that save.
def refresh_save_info():
    # This is the bad way to do this, as it needs updating whenever the
    # save format changes significantly.
    tmp_stats = {}
    tmp_titles = []

    if len(saves_array) == 0:
        tmp_stats["name"] = ""
        tmp_stats["hp"] = ""
        tmp_stats["ep"] = ""
        tmp_stats["attack"] = ""
        tmp_stats["defense"] = ""
        tmp_stats["gold"] = ""
        tmp_stats["exp"] = ""
        tmp_stats["level"] = ""
        for i in range(5):
            tmp_titles.append("")
    # 		return
    else:
        save_loc = config.MODULES_DIR + "/saves/" + saves_array[saves_pos]
        savefile = open(save_loc)
        version_unused = pickle.load(savefile)
        tmp_stats["name"] = str(pickle.load(savefile))
        tmp_stats["hp"] = str(pickle.load(savefile))
        tmp_stats["ep"] = str(pickle.load(savefile))
        unused_maxhp = pickle.load(savefile)
        unused_maxep = pickle.load(savefile)
        tmp_stats["attack"] = str(pickle.load(savefile))
        tmp_stats["defense"] = str(pickle.load(savefile))
        tmp_stats["gold"] = str(pickle.load(savefile))
        tmp_stats["exp"] = str(pickle.load(savefile))
        tmp_stats["level"] = str(pickle.load(savefile))
        savefile.close()

        tmp = saves_pos - (saves_pos % 5)
        for i in range(5):
            if len(saves_array) <= tmp + i:
                savetext = ""
            else:
                savetext = saves_array[tmp + i]
            tmp_titles.append(savetext)
    display_stats(tmp_stats, tmp_titles)


def display_stats(stat_dict, titles_dict):
    pixels_per_line = 20
    g.unclean_screen = True
    screen.fill(
        config.COLORS["light_gray"],
        (
            config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_up.png"].get_width() + 3,
            config.TILESIZE * config.MAPSIZE_Y / 3,
            150,
            170,
        ),
    )
    info_x = config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_up.png"].get_width() + 5
    info_y = config.TILESIZE * config.MAPSIZE_Y / 3
    linenum = 0
    g.print_string(screen, "Name: " + stat_dict["name"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "HP: " + stat_dict["hp"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "MP: " + stat_dict["ep"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "Attack: " + stat_dict["attack"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "Defense: " + stat_dict["defense"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "Gold: " + stat_dict["gold"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "XP: " + stat_dict["exp"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1
    g.print_string(screen, "Level: " + stat_dict["level"], g.font, (info_x, info_y + pixels_per_line * linenum))
    linenum += 1

    for i in range(5):
        if i == saves_pos % 5:
            inner_color = "dh_green"
        else:
            inner_color = "light_gray"
        g.create_norm_box(
            (
                config.TILESIZE * config.MAPSIZE_X / 4 + 2,
                config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_down.png"].get_height() + 1 + i * 20,
            ),
            (config.BUTTONS["loadgame_down.png"].get_width() - 3, 17),
            inner_color=inner_color,
        )
        g.print_string(
            screen,
            titles_dict[i],
            g.font,
            (
                config.TILESIZE * config.MAPSIZE_X / 4 + 5,
                config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_down.png"].get_height() + 2 + i * 20,
            ),
        )


def key_handler(switch: int) -> None:
    """
    All keypresses in new_game pass through here

    Based on the key name, give the right action. ("etc", "left", "right", "up", "down", "return")
    """
    global saves_pos
    if switch == config.BINDINGS["cancel"]:
        cancel_load()
    elif switch == config.BINDINGS["left"] or switch == config.BINDINGS["right"]:
        if config.mut["CURR_BUTTON"] == 0:
            config.mut["CURR_BUTTON"] = 1
        else:
            config.mut["CURR_BUTTON"] = 0
        refresh_buttons()
    elif switch == config.BINDINGS["up"]:
        saves_pos -= 1
        if saves_pos <= -1:
            saves_pos = len(saves_array) - 1
            # This comes into play when there are very few saves.
            if saves_pos <= -1:
                saves_pos = 0
        refresh_save_info()
    elif switch == config.BINDINGS["down"]:
        saves_pos += 1
        if saves_pos >= len(saves_array):
            saves_pos = 0
        refresh_save_info()
    elif switch == config.BINDINGS["action"]:
        if config.mut["CURR_BUTTON"] != 1:
            load_selected()
        else:
            cancel_load()


# called when "Cancel" is pressed
def cancel_load():
    global did_load
    # 	global return_from_loadgame
    did_load = ""
    g.break_one_loop = 1


def mouse_handler_move(xy):
    # up arrow:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3,
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_up.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_up.png"].get_height(),
    ):
        config.mut["CURR_BUTTON"] = 2

    # down arrow:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 - config.BUTTONS["loadgame_down.png"].get_height(),
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_down.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
    ):
        config.mut["CURR_BUTTON"] = 3

    # load button:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["load_scr.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 + config.BUTTONS["load_scr.png"].get_height(),
    ):
        config.mut["CURR_BUTTON"] = 0

    # leave button:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["load_scr.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
        config.TILESIZE * config.MAPSIZE_X / 4
        + config.BUTTONS["load_scr.png"].get_width()
        + config.BUTTONS["leave.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 + config.BUTTONS["leave.png"].get_height(),
    ):
        config.mut["CURR_BUTTON"] = 1

    refresh_buttons()


def mouse_handler_down(xy):
    global saves_pos
    # up arrow:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3,
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_up.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_up.png"].get_height(),
    ):

        tmp = saves_pos - (saves_pos % 5) - 5
        if tmp < 0:
            if len(saves_array) != 0:
                saves_pos = len(saves_array) - (len(saves_array) % 5) + (saves_pos % 5)
                if saves_pos >= len(saves_array):
                    saves_pos = len(saves_array) - 1
        else:
            saves_pos -= 5
        refresh_save_info()

    # down arrow:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 - config.BUTTONS["loadgame_down.png"].get_height(),
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_down.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
    ):

        tmp = saves_pos - (saves_pos % 5) + 5
        if tmp >= len(saves_array):
            saves_pos = saves_pos % 5
        else:
            saves_pos += 5
            if saves_pos >= len(saves_array):
                saves_pos = len(saves_array) - 1
        refresh_save_info()

    # load button:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["load_scr.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 + config.BUTTONS["load_scr.png"].get_height(),
    ):
        config.mut["CURR_BUTTON"] = 0
        key_handler(pygame.K_RETURN)

    # leave button:
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["load_scr.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
        config.TILESIZE * config.MAPSIZE_X / 4
        + config.BUTTONS["load_scr.png"].get_width()
        + config.BUTTONS["leave.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 + config.BUTTONS["leave.png"].get_height(),
    ):
        config.mut["CURR_BUTTON"] = 1
        key_handler(pygame.K_RETURN)

    # save "listbox"
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_up.png"].get_height(),
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_up.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 - config.BUTTONS["loadgame_down.png"].get_height(),
    ):

        base_y = xy[1] - config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_up.png"].get_height()
        base_y -= 40
        if base_y % 20 < 2 or base_y % 20 > 18:
            return
        tmp = saves_pos - (saves_pos % 5) + (base_y / 20)
        if tmp >= len(saves_array):
            return
        saves_pos = tmp
        refresh_save_info()


def mouse_handler_double(xy):
    global saves_pos
    # save "listbox"
    if mouse_over(
        xy,
        config.TILESIZE * config.MAPSIZE_X / 4,
        config.TILESIZE * config.MAPSIZE_Y / 3 + config.BUTTONS["loadgame_up.png"].get_height(),
        config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["loadgame_up.png"].get_width(),
        config.TILESIZE * config.MAPSIZE_Y / 3 + 140 - config.BUTTONS["loadgame_down.png"].get_height(),
    ):

        load_selected()


def mouse_over(xy, x1, y1, x2, y2):
    if xy[0] >= x1 and xy[0] <= x2 and xy[1] >= y1 and xy[1] <= y2:
        return 1
    return 0


def refresh_buttons():
    g.unclean_screen = True
    # canvas_map.delete("loadgame_buttons")
    load_img = "load_scr.png"
    leave_img = "leave.png"
    up_img = "loadgame_up.png"
    down_img = "loadgame_down.png"
    if config.mut["CURR_BUTTON"] == 0:
        load_img = "load_scr_sel.png"
    elif config.mut["CURR_BUTTON"] == 1:
        leave_img = "leave_sel.png"
    elif config.mut["CURR_BUTTON"] == 2:
        up_img = "loadgame_up_sel.png"
    else:
        down_img = "loadgame_down_sel.png"
    screen.blit(
        config.BUTTONS[load_img], (config.TILESIZE * config.MAPSIZE_X / 4, config.TILESIZE * config.MAPSIZE_Y / 3 + 140)
    )
    screen.blit(
        config.BUTTONS[leave_img],
        (
            config.TILESIZE * config.MAPSIZE_X / 4 + config.BUTTONS["load_scr.png"].get_width(),
            config.TILESIZE * config.MAPSIZE_Y / 3 + 140,
        ),
    )
    screen.blit(config.BUTTONS[up_img], (config.TILESIZE * config.MAPSIZE_X / 4, config.TILESIZE * config.MAPSIZE_Y / 3))
    screen.blit(
        config.BUTTONS[down_img],
        (
            config.TILESIZE * config.MAPSIZE_X / 4,
            config.TILESIZE * config.MAPSIZE_Y / 3 + 140 - config.BUTTONS["loadgame_down.png"].get_height(),
        ),
    )


def init_window_loadgame():
    # create the window
    global prevent_dbl_load
    prevent_dbl_load = 0
    g.create_norm_box(
        (config.TILESIZE * config.MAPSIZE_X / 4 - 2, config.TILESIZE * config.MAPSIZE_Y / 3 - 2),
        (config.TILESIZE * config.MAPSIZE_X / 2 + 2, +140 + config.BUTTONS["load_scr.png"].get_height() + 2),
    )

    global did_load
    did_load = ""

    # add the saves images
    screen.blit(
        config.BUTTONS["loadgame_up.png"], (config.TILESIZE * config.MAPSIZE_X / 4, config.TILESIZE * config.MAPSIZE_Y / 3)
    )
    screen.blit(
        config.BUTTONS["loadgame_down.png"],
        (
            config.TILESIZE * config.MAPSIZE_X / 4,
            config.TILESIZE * config.MAPSIZE_Y / 3 + 140 - config.BUTTONS["loadgame_down.png"].get_height(),
        ),
    )

    pixels_per_line = 20

    # If there is no save directory, make one.
    if path.isdir(config.MODULES_DIR + "/saves") == 0:
        if path.exists(config.MODULES_DIR + "/saves") == 1:
            remove(config.MODULES_DIR + "/saves")
        mkdir(config.MODULES_DIR + "/saves")
    # show the files contained in the saves directory.
    global saves_array
    saves_array = []
    tmp_saves_array = listdir(config.MODULES_DIR + "/saves")
    for save_name in tmp_saves_array:
        if save_name[:1] != "." and save_name != "CVS":
            saves_array.append(save_name)
    global saves_pos
    saves_pos = 0

    refresh_buttons()
    refresh_save_info()

    global repeat_key
    repeat_key = 0
    global key_down
    key_down = ""
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                key_handler(event.key)
                repeat_key = 0
            elif event.type == pygame.KEYUP:
                key_handler_up(event.key)
            elif event.type == pygame.MOUSEMOTION:
                mouse_handler_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_handler_down(event.pos) == 1:
                    return None

        if g.unclean_screen:
            pygame.display.flip()

    return did_load


def key_handler_up(key_name):
    global key_down
    if key_down == "":
        return
    if key_name == key_name:
        key_down = ""
