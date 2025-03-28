# file: new_game.py
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

# This file creates a new character.
# Either call directly (which will use the first module seen), or
# call from rpg.py after setting config.MODULES_DIR.


import sys

import pygame

import config
import g
import loadgame
import main
import options
import save_mgmt
from player import player

# main stats for character. Taken from g.hp etc.
global name_stat
global hp_stat
global ep_stat
global attack_stat
global defense_stat
global gold_stat

# distance from the top of the button canvas each button should be placed.
# Values are added in init_window. begin is not needed; always zero.
reroll_height = 0
load_height = 0
quit_height = 0

# currently selected button. 0=New, 1=Load, 2=Options, 3=Quit, 4=None,
# 5=Start, 6=Rename, 7=Reroll, 8=Back, 9=None
cur_button = 0

already_started_game = 0

curr_name_loc = -1


# give new stats for the character. Called when pressing the
# "Reroll stats" button.
def reroll_stats():

    # actual re-rolling
    global name_stat
    global hp_stat
    global ep_stat
    global attack_stat
    global defense_stat
    global gold_stat
    hp_stat = g.die_roll(g.new_game_dice[0][0], g.new_game_dice[0][1]) + g.new_game_dice[0][2]
    ep_stat = g.die_roll(g.new_game_dice[1][0], g.new_game_dice[1][1]) + g.new_game_dice[1][2]
    attack_stat = g.die_roll(g.new_game_dice[2][0], g.new_game_dice[2][1]) + g.new_game_dice[2][2]
    defense_stat = g.die_roll(g.new_game_dice[3][0], g.new_game_dice[3][1]) + g.new_game_dice[3][2]
    gold_stat = g.die_roll(g.new_game_dice[4][0], g.new_game_dice[4][1]) + g.new_game_dice[4][2]

    reset_vars()
    refresh_new_game()


def rename_character():
    global name_stat
    global curr_name_loc
    curr_name_loc = len(name_stat)
    global old_name
    old_name = name_stat
    global repeat_key
    repeat_key = 0
    global key_down
    key_down = ""
    tmp = main.ask_for_string("What is your name?", name_stat, 20, 1)
    if tmp != -1:
        name_stat = tmp
    refresh_name()
    return 1


def key_handler_up(key_name):
    global key_down
    if key_down == "":
        return
    if key_name == key_name:
        key_down = ""


def refresh_name():
    g.screen.fill(
        config.COLORS["light_gray"],
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 10, 280, 14),
    )
    tmp_name = name_stat[:curr_name_loc] + "|" + name_stat[curr_name_loc:]
    g.print_string(
        g.screen,
        "Name: " + tmp_name,
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 10),
    )
    g.unclean_screen = True


def name_key_handler(key_name):
    if key_name == pygame.K_BACKSPACE:
        backspace_name()
    elif key_name == g.bindings["action"]:
        return 1
    elif key_name == g.bindings["cancel"]:
        global name_stat
        global old_name
        name_stat = old_name
        return 1
    elif key_name == g.bindings["left"] or key_name == g.bindings["up"]:
        name_left()
    elif key_name == g.bindings["right"] or key_name == g.bindings["down"]:
        name_right()
    elif key_name == pygame.K_HOME:
        name_home()
    elif key_name == pygame.K_END:
        name_end()
    else:
        return 2
    return 0


def adjust_name(input_char):
    global name_stat
    global curr_name_loc
    usable_chars = "`~!@#$%^&*()-_=+|[{]};:'\",<.>/? "
    c = input_char
    if c == "":
        return
    if len(name_stat) > 20:
        return
    if c.isalnum() == 0:
        if usable_chars.find(c) == -1:
            return
    name_stat = name_stat[:curr_name_loc] + input_char + name_stat[curr_name_loc:]
    curr_name_loc += 1


def backspace_name():
    global name_stat
    global curr_name_loc
    if curr_name_loc <= 0:
        return
    name_stat = name_stat[: curr_name_loc - 1] + name_stat[curr_name_loc:]
    curr_name_loc -= 1
    curr_name_loc = max(curr_name_loc, 0)


def name_left():
    global curr_name_loc
    curr_name_loc -= 1
    curr_name_loc = max(curr_name_loc, 0)


def name_right():
    global curr_name_loc
    curr_name_loc += 1
    curr_name_loc = min(curr_name_loc, len(name_stat))


def name_home():
    global curr_name_loc
    curr_name_loc = 0


def name_end():
    global curr_name_loc
    curr_name_loc = len(name_stat)


# call to reset the game
def reset_vars():
    # move variables to player.*
    player.maxhp = int(hp_stat)
    player.maxep = int(ep_stat)
    player.attack = int(attack_stat)
    player.defense = int(defense_stat)
    player.gold = int(gold_stat)

    player.exp = 0
    player.level = 0
    player.skillpoints = 0
    player.hp = player.maxhp
    player.ep = player.maxep

    # place the player
    g.xgrid = 0
    g.ygrid = 0
    g.zgrid = 0

    timestep = 0
    g.var_list = {}
    g.item.dropped_items = []

    # clear the inventory
    for i in range(len(g.item.inv)):
        g.item.inv[i] = -1
    for i in range(len(player.equip)):
        player.equip[i] = -1
    # clear skills
    for i in range(len(player.skill)):
        player.skill[i][5] = 0
    global new_game
    new_game = 1


# get stats from g.*
def get_stats():
    global name_stat
    global hp_stat
    global ep_stat
    global attack_stat
    global defense_stat
    global gold_stat
    name_stat = player.name
    hp_stat = player.hp
    ep_stat = player.ep
    attack_stat = player.attack
    defense_stat = player.defense
    gold_stat = player.gold


# Use the stats given to create a new character.
def begin_game(loadgame_name=""):
    # This prevents a race condition
    global already_started_game
    if already_started_game == 1:
        return 0
    already_started_game = 1

    g.create_norm_box(
        (g.screen_size[0] / 4, g.screen_size[1] / 3),
        (g.screen_size[0] / 2, g.screen_size[1] / 3),
        "black",
        "light_gray",
    )
    g.print_string(
        g.screen, "Starting game. Please wait", g.font, (g.screen_size[0] / 2, g.screen_size[1] / 2), align=1
    )
    pygame.display.flip()

    g.read_maps()
    g.item.load_dropped_items()

    # just in case someone changed the name
    # after rerolling or loading
    global name_stat
    player.name = name_stat

    if player.name == "":
        player.name = "Nameless"
    # bring the main window up.
    if loadgame_name != "":
        save_mgmt.loadgame(loadgame_name)
    main.init_window_main(new_game)
    already_started_game = 0
    g.break_one_loop = 0

    # after returning to this screen, reset everything.
    init_window()
    return 1


def load_game():
    # bring the loadgame window up.
    global new_game
    load_game = 0
    temp_surface = pygame.Surface((400, 300))
    temp_surface.blit(g.screen, (0, 0), (100, 100, 400, 300))
    load_game = loadgame.init_window_loadgame()
    g.screen.blit(temp_surface, (100, 100))
    if load_game != "":
        new_game = 0
    get_stats()
    if load_game != "":
        return begin_game(load_game)


def show_options():
    # bring the options window up.
    temp_surface = pygame.Surface((400, 300))
    temp_surface.blit(g.screen, (0, 0), (100, 100, 400, 300))
    options.init_window_options()
    g.screen.blit(temp_surface, (100, 100))


def quit_game():
    return


# refresh the buttons.
def refresh_buttons():
    if config.mut["CURR_BUTTON"] > 4:
        g.screen.blit(g.buttons["begin.png"], (inner_new_game_width, inner_button_start))
        g.screen.blit(g.buttons["skill.png"], (inner_rename_width, inner_button_start))
        g.screen.blit(g.buttons["reroll.png"], (inner_reroll_width, inner_button_start))
        g.screen.blit(g.buttons["leave.png"], (inner_quit_width, inner_button_start))
        if config.mut["CURR_BUTTON"] == 5:
            g.screen.blit(g.buttons["begin_sel.png"], (inner_new_game_width, inner_button_start))
            refresh_help("Begin a new game")
        if config.mut["CURR_BUTTON"] == 6:
            g.screen.blit(g.buttons["skill_sel.png"], (inner_rename_width, inner_button_start))
            refresh_help("Change your name")
        if config.mut["CURR_BUTTON"] == 7:
            g.screen.blit(g.buttons["reroll_sel.png"], (inner_reroll_width, inner_button_start))
            refresh_help("Reroll your statistics")
        if config.mut["CURR_BUTTON"] == 8:
            g.screen.blit(g.buttons["leave_sel.png"], (inner_quit_width, inner_button_start))
            refresh_help("Back to the main menu")
        if config.mut["CURR_BUTTON"] == 9:
            refresh_help("")

    else:
        g.screen.blit(g.buttons["begin.png"], (new_game_width, button_start))
        g.screen.blit(g.buttons["load.png"], (load_width, button_start))
        g.screen.blit(g.buttons["options.png"], (options_width, button_start))
        g.screen.blit(g.buttons["quit.png"], (quit_width, button_start))
        if config.mut["CURR_BUTTON"] == 0:
            g.screen.blit(g.buttons["begin_sel.png"], (new_game_width, button_start))
            refresh_help("Create a new character")
        if config.mut["CURR_BUTTON"] == 1:
            g.screen.blit(g.buttons["load_sel.png"], (load_width, button_start))
            refresh_help("Load an old game")
        if config.mut["CURR_BUTTON"] == 2:
            g.screen.blit(g.buttons["options_sel.png"], (options_width, button_start))
            refresh_help("Change the options")
        if config.mut["CURR_BUTTON"] == 3:
            g.screen.blit(g.buttons["quit_sel.png"], (quit_width, button_start))
            refresh_help("Quit the game")
        if config.mut["CURR_BUTTON"] == 4:
            refresh_help("")
    pygame.display.flip()


def refresh_help(string):
    start_xy = (15, button_start + button_height / 2)
    size = (180, 14)
    g.screen.fill(config.COLORS["very_dark_blue"], (start_xy[0], start_xy[1], size[0], size[1]))
    g.print_string(g.screen, string, g.font, start_xy, config.COLORS["white"])


# All keypresses in new_game pass through here. Based on the key name,
# give the right action. ("etc", "left", "right", "up", "down", "return")
def key_handler(key_name):
    if key_name == g.bindings["cancel"]:
        if config.mut["CURR_BUTTON"] > 4:
            back_from_new_game()
            return 0
        g.break_one_loop = 100
        return 1
    if key_name == g.bindings["up"] or key_name == g.bindings["left"]:
        if config.mut["CURR_BUTTON"] == 0:
            config.mut["CURR_BUTTON"] = 4
        if config.mut["CURR_BUTTON"] == 5:
            config.mut["CURR_BUTTON"] = 9
        config.mut["CURR_BUTTON"] -= 1
    elif key_name == g.bindings["down"] or key_name == g.bindings["right"]:
        if config.mut["CURR_BUTTON"] == 4 or config.mut["CURR_BUTTON"] == 3:
            config.mut["CURR_BUTTON"] = -1
        if config.mut["CURR_BUTTON"] == 8 or config.mut["CURR_BUTTON"] == 9:
            config.mut["CURR_BUTTON"] = 4
        config.mut["CURR_BUTTON"] += 1
    elif key_name == g.bindings["action"]:
        if config.mut["CURR_BUTTON"] == 0:
            init_new_game()
        elif config.mut["CURR_BUTTON"] == 1:
            load_game()
        elif config.mut["CURR_BUTTON"] == 2:
            show_options()
        elif config.mut["CURR_BUTTON"] == 3:
            sys.exit()
        elif config.mut["CURR_BUTTON"] == 5:
            return begin_game()
        elif config.mut["CURR_BUTTON"] == 6:
            rename_character()
            refresh_new_game()
        elif config.mut["CURR_BUTTON"] == 7:
            reroll_stats()
        elif config.mut["CURR_BUTTON"] == 8:
            back_from_new_game()
            return 0

    refresh_buttons()


def mouse_handler_move(xy):
    prev_button = config.mut["CURR_BUTTON"]
    if config.mut["CURR_BUTTON"] > 4:
        if (
            xy[1] < inner_button_start
            or xy[1] > inner_button_height + inner_button_start
            or xy[0] < inner_new_game_width
        ):
            config.mut["CURR_BUTTON"] = 9
        elif xy[0] < inner_rename_width:
            config.mut["CURR_BUTTON"] = 5
        elif xy[0] < inner_reroll_width:
            config.mut["CURR_BUTTON"] = 6
        elif xy[0] < inner_quit_width:
            config.mut["CURR_BUTTON"] = 7
        elif xy[0] < inner_final_width:
            config.mut["CURR_BUTTON"] = 8
        else:
            config.mut["CURR_BUTTON"] = 9
    elif xy[1] < button_start or xy[1] > button_height + button_start or xy[0] < new_game_width:
        config.mut["CURR_BUTTON"] = 4
    elif xy[0] < load_width:
        config.mut["CURR_BUTTON"] = 0
    elif xy[0] < options_width:
        config.mut["CURR_BUTTON"] = 1
    elif xy[0] < quit_width:
        config.mut["CURR_BUTTON"] = 2
    elif xy[0] < final_width:
        config.mut["CURR_BUTTON"] = 3
    else:
        config.mut["CURR_BUTTON"] = 4
    if prev_button != config.mut["CURR_BUTTON"]:
        refresh_buttons()


# Called when newgame is pressed on the main menu.
def init_new_game():

    global name_stat
    name_stat = g.default_player_name
    global inner_button_start
    inner_button_start = config.TILESIZE * main.mapsizey * 2 / 3 - g.buttons["begin.png"].get_height()
    global inner_button_height
    inner_button_height = g.buttons["begin.png"].get_height()
    global inner_new_game_width
    global inner_rename_width
    global inner_reroll_width
    global inner_quit_width
    global inner_final_width
    inner_new_game_width = (
        config.TILESIZE * main.mapsizex / 2 - g.buttons["begin.png"].get_width() - g.buttons["skill.png"].get_width()
    )
    inner_rename_width = inner_new_game_width + g.buttons["begin.png"].get_width()
    inner_reroll_width = inner_rename_width + g.buttons["skill.png"].get_width()
    inner_quit_width = inner_reroll_width + g.buttons["reroll.png"].get_width()
    inner_final_width = inner_quit_width + g.buttons["leave.png"].get_width()

    config.mut["CURR_BUTTON"] = 5

    reroll_stats()
    refresh_new_game()


def back_from_new_game():
    g.screen.blit(g.backgrounds["new_game.png"], (0, 0))
    config.mut["CURR_BUTTON"] = 0
    refresh_buttons()
    pygame.display.flip()


# called upon game start
def init_window():

    pygame.display.set_caption(g.game_name)

    global bgcolour
    bgcolour = "lightgrey"

    g.screen.fill(config.COLORS["black"])
    g.screen.blit(g.backgrounds["new_game.png"], (0, 0))

    global name_stat
    name_stat = g.default_player_name

    # button coords
    global button_start
    button_start = 331
    global button_height
    button_height = g.buttons["begin.png"].get_height()
    global new_game_width
    global load_width
    global options_width
    global quit_width
    global final_width
    new_game_width = (
        config.TILESIZE * main.mapsizex / 2 - g.buttons["begin.png"].get_width() - g.buttons["load.png"].get_width() / 2
    )
    load_width = new_game_width + g.buttons["begin.png"].get_width()
    options_width = load_width + g.buttons["options.png"].get_width()
    quit_width = options_width + g.buttons["load.png"].get_width()
    final_width = quit_width + g.buttons["quit.png"].get_width()

    config.mut["CURR_BUTTON"] = 0
    refresh_buttons()

    pygame.display.flip()

    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if key_handler(event.key) == 1:
                    return
            elif event.type == pygame.MOUSEMOTION:
                mouse_handler_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if key_handler(pygame.K_RETURN) == 1:
                        return


def refresh_new_game():
    g.create_norm_box(
        (config.TILESIZE * main.mapsizex / 4, config.TILESIZE * main.mapsizey / 3),
        (config.TILESIZE * main.mapsizex / 2, config.TILESIZE * main.mapsizey / 3),
    )
    g.print_string(
        g.screen,
        "Name: " + name_stat,
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 10),
    )
    g.print_string(
        g.screen,
        "HP: " + str(hp_stat),
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 25),
    )
    g.print_string(
        g.screen,
        "MP: " + str(ep_stat),
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 40),
    )
    g.print_string(
        g.screen,
        "Attack: " + str(attack_stat),
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 55),
    )
    g.print_string(
        g.screen,
        "Defense: " + str(defense_stat),
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 70),
    )
    g.print_string(
        g.screen,
        "Gold: " + str(gold_stat),
        g.font,
        (config.TILESIZE * main.mapsizex / 4 + 10, config.TILESIZE * main.mapsizey / 3 + 85),
    )
