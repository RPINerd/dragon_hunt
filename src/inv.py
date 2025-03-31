# inv.py
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

import pygame

import action
import config
import g
import game_screen as pygscreen
import item
import main
import save_mgmt
from player import player

# width/height of inv canvas, in tiles.
# (config.TILESIZE + the 3 pixel border)
inv_width = 4
inv_height = 7

# width/height of the equipment canvas, in tiles.
equip_size = 3

# Currently selected item number. If this is higher than the inventory can hold,
# it represents a position within the equipment display.
curr_item = 0


global active_button
active_button = 0

# currently selected button. 0=Use, 1=Drop, 2=Wear, 3=Skill, 4=Save, 5=Leave
cur_button = 0

# Like config.mut["CURR_BUTTON"], but for the inner menus.
inner_cur_button = 0

# distance from the top of the inv box each button should be placed.
# Values are added in init_window.
equip_height = 0
drop_height = 0
skill_height = 0
save_height = 0
leave_height = 0
total_height = 0

button_width = 0


# xy coords of the upper-left hand corner of the inv area.
base_x = 0
base_y = 0

# xy coords for the inner menus.
tmp_x_base = 0
tmp_y_base = 0

# xy coords for the inner menu buttons.
tmp_menu_x_base = 0
tmp_menu_y_base = 0
# And height.
tmp_menu_width = 0
tmp_menu_height = 0

inv_canvas_width = 0
inv_canvas_height = 0

screen = pygscreen.get_screen()


def convert_equip_loc_to_index(loc: int) -> int:
    """
    Convert the location in the equipment display to the actual index in the player.equip array

    Given a number from 0-8 (as returned by curr_item-inv_height*inv_width) return the
    proper location in the player.equip array.
    Corrects for the empty spaces in the display.

    Args:
        loc (int): The location in the equipment display.

    Returns:
        int: The index in the player.equip array.
    """
    trans_index = {
        0: -1,
        1: 3,
        2: 4,
        3: 0,
        4: 1,
        5: 2,
        6: -1,
        7: 5,
        8: -1,
    }

    return trans_index[loc]


# Called when "Use" is pressed on the inv menu
def open_use_item():
    open_inner_menu("use")
    g.cur_window = "inventory_use"
    refresh_use()
    refresh_inner_buttons("use")
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if use_key_handler(event.key) == 1:
                    return
            elif event.type == pygame.MOUSEMOTION:
                use_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if use_mouse_click(event.pos) == 1:
                    return


# Called when "Drop" is pressed on the inv menu
def open_drop_item():
    open_inner_menu("drop")
    g.cur_window = "inventory_drop"
    refresh_drop()
    refresh_inner_buttons("drop")
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if drop_key_handler(event.key) == 1:
                    return
            elif event.type == pygame.MOUSEMOTION:
                drop_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if drop_mouse_click(event.pos) == 1:
                    return


def open_equip_item():
    global curr_item
    open_inner_menu("equip")

    # Equip also needs the equip screen:
    temp_canvas_width = (config.TILESIZE * equip_size) + 8
    g.create_norm_box((tmp_x_base - temp_canvas_width, tmp_y_base), (temp_canvas_width, temp_canvas_width))

    g.cur_window = "inventory_equip"
    refresh_equip()
    refresh_inner_buttons("equip")
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if equip_key_handler(event.key) == 1:
                    if curr_item >= inv_width * inv_height:
                        curr_item = 0
                    return
            elif event.type == pygame.MOUSEMOTION:
                equip_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and equip_mouse_click(event.pos):
                if curr_item >= inv_width * inv_height:
                    curr_item = 0
                return


def open_skill_menu() -> str | None:
    """"""
    open_inner_menu("skill")
    g.cur_window = "inventory_skill"
    refresh_skill("skill")
    refresh_inner_buttons("skill")
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                tmp = skill_key_handler(event.key)
                if tmp == 1:
                    return None
                if tmp == "end":
                    return "end"
            elif event.type == pygame.MOUSEMOTION:
                skill_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if skill_mouse_click(event.pos) == 1:
                    return None


# Generic function for creating a sub-menu for the inv.
def open_inner_menu(screen_str):
    global inner_cur_button
    inner_cur_button = 0
    global tmp_x_base
    global tmp_y_base
    global tmp_menu_x_base
    global tmp_menu_y_base
    global tmp_menu_width
    global tmp_menu_height
    global inv_canvas_width
    global inv_canvas_height
    if inv_canvas_width == 0:
        inv_canvas_width = (config.TILESIZE * inv_width) + ((inv_width + 1) * 2) + 1
    if inv_canvas_height == 0:
        inv_canvas_height = (config.TILESIZE * inv_height) + ((inv_height + 1) * 2) + 1

    tmp_x_base = (config.TILESIZE * main.mapsizex) / 2 - inv_canvas_width
    tmp_y_base = (config.TILESIZE * main.mapsizey - inv_canvas_height) / 2
    tmp_menu_x_base = (
        ((config.TILESIZE * main.mapsizex) / 2 - tmp_x_base) / 2
        + tmp_x_base
        - config.BUTTONS[screen_str + ".png"].get_width()
    )
    tmp_menu_y_base = (config.TILESIZE * main.mapsizey + inv_canvas_height) / 2
    tmp_menu_width = config.BUTTONS[screen_str + ".png"].get_width() + config.BUTTONS["leave.png"].get_width()
    tmp_menu_height = config.BUTTONS["leave.png"].get_height()

    create_inv_display()

    # button rectangle
    g.create_norm_box((tmp_menu_x_base, tmp_menu_y_base), (tmp_menu_width, tmp_menu_height))


def create_inv_display() -> None:
    """Create a generic inventory display"""
    g.create_norm_box(
        (tmp_x_base, tmp_y_base),
        (
            (config.TILESIZE * main.mapsizex) / 2 - tmp_x_base,
            (config.TILESIZE * main.mapsizey + inv_canvas_height) / 2
            + config.BUTTONS["leave.png"].get_height()
            - tmp_y_base,
        ),
    )

    # Per-item borders
    for y in range(inv_height):
        for x in range(inv_width):
            g.create_norm_box(
                (tmp_x_base + x * config.TILESIZE + 2 * (x + 1), tmp_y_base + y * config.TILESIZE + 2 * (y + 1)),
                (config.TILESIZE, config.TILESIZE),
                inner_color="dh_green",
            )


def refresh_inner_buttons(screen_str: str) -> None:
    """Refreshes the inner menu buttons."""
    first_image = screen_str + ".png"
    leave_image = "leave.png"
    if inner_cur_button == 0:
        first_image = screen_str + "_sel.png"
    elif inner_cur_button == 1:
        leave_image = "leave_sel.png"

    x_start = (
        ((config.TILESIZE * main.mapsizex) / 2 - tmp_x_base) / 2
        + tmp_x_base
        - config.BUTTONS[screen_str + ".png"].get_width()
    )
    y_start = (config.TILESIZE * main.mapsizey + inv_canvas_height) / 2

    screen.blit(config.BUTTONS[first_image], (x_start, y_start))
    screen.blit(config.BUTTONS[leave_image], (x_start + config.BUTTONS[screen_str + ".png"].get_width(), y_start))

    pygame.display.flip()


def refresh_use() -> None:
    """Refreshes the item display in the inner menus."""
    refresh_inv_display("use")


def refresh_drop() -> None:
    """"""
    refresh_inv_display("drop")


def refresh_equip() -> None:
    """"""
    refresh_inv_display("equip")
    # rebuild the equipment display
    temp_canvas_width = (config.TILESIZE * equip_size) + 8
    tmpx = tmp_x_base - temp_canvas_width
    tmpy = tmp_y_base

    for i in range(9):
        g.create_norm_box(
            (
                tmpx + (i % equip_size) * config.TILESIZE + 2 * ((i % equip_size) + 1),
                tmpy + (i / equip_size) * config.TILESIZE + 2 * ((i / equip_size) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dh_green",
        )

    # Draw selection rectangle for equipment display
    if curr_item != -1 and curr_item >= inv_width * inv_height:
        c_item = curr_item - inv_width * inv_height
        g.create_norm_box(
            (
                tmpx + (c_item % equip_size) * config.TILESIZE + 2 * ((c_item % equip_size) + 1),
                tmpy + (c_item / equip_size) * config.TILESIZE + 2 * ((c_item / equip_size) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dark_green",
        )

    # Weapon
    if player.equip[0] != -1:
        draw_item(item.item[player.equip[0]].picturename, 0, 1, tmpx, tmpy)
    else:
        draw_item("items/weapon_eq.png", 0, 1, tmpx, tmpy)
    # Armor
    if player.equip[1] != -1:
        draw_item(item.item[player.equip[1]].picturename, 1, 1, tmpx, tmpy)
    else:
        draw_item("items/armor_eq.png", 1, 1, tmpx, tmpy)
    # Shield
    if player.equip[2] != -1:
        draw_item(item.item[player.equip[2]].picturename, 2, 1, tmpx, tmpy)
    else:
        draw_item("items/shield_eq.png", 2, 1, tmpx, tmpy)
    # Helmet
    if player.equip[3] != -1:
        draw_item(item.item[player.equip[3]].picturename, 1, 0, tmpx, tmpy)
    else:
        draw_item("items/helmet_eq.png", 1, 0, tmpx, tmpy)
    # Gloves
    if player.equip[4] != -1:
        draw_item(item.item[player.equip[4]].picturename, 2, 0, tmpx, tmpy)
    else:
        draw_item("items/gloves_eq.png", 2, 0, tmpx, tmpy)
    # Boots
    if player.equip[5] != -1:
        draw_item(item.item[player.equip[5]].picturename, 1, 2, tmpx, tmpy)
    else:
        draw_item("items/boots_eq.png", 1, 2, tmpx, tmpy)

    main.refresh_bars()
    pygame.display.flip()


def refresh_inv_display(screen_str):
    # Draw a selection box around the current item.
    x = tmp_x_base
    y = tmp_y_base
    for i in range(len(item.inv)):
        g.create_norm_box(
            (
                x + (i % inv_width) * config.TILESIZE + 2 * ((i % inv_width) + 1),
                y + (i / inv_width) * config.TILESIZE + 2 * ((i / inv_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dh_green",
        )

    if curr_item != -1 and curr_item < inv_width * inv_height:
        g.create_norm_box(
            (
                x + (curr_item % inv_width) * config.TILESIZE + 2 * ((curr_item % inv_width) + 1),
                y + (curr_item / inv_width) * config.TILESIZE + 2 * ((curr_item / inv_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dark_green",
        )

    # draw the item pictures.
    for i in range(len(item.inv)):
        if item.inv[i] != -1:
            draw_item(item.item[item.inv[i]].picturename, i % inv_width, i / inv_width, x, y, screen_str)

    # draw the help text
    if curr_item >= inv_width * inv_height:  # equipment
        tempitem = convert_equip_loc_to_index(curr_item - (inv_width * inv_height))
        if tempitem == -1 or player.equip[tempitem] == -1:
            helptext = ""
        else:
            helptext = item.item[player.equip[tempitem]].name
    elif curr_item == -1 or item.inv[curr_item] == -1:
        helptext = ""
    else:
        helptext = item.item[item.inv[curr_item]].name

    g.create_norm_box((tmp_menu_x_base, tmp_menu_y_base + tmp_menu_height), (tmp_menu_width, 17))

    g.print_string(g.screen, helptext, g.font, (tmp_menu_x_base + 2, tmp_menu_y_base + tmp_menu_height + 1))
    pygame.display.flip()


def refresh_skill(screen_str):
    # Draw a selection box around the current item.
    x = tmp_x_base
    y = tmp_y_base
    for i in range(len(item.inv)):
        g.create_norm_box(
            (
                x + (i % inv_width) * config.TILESIZE + 2 * ((i % inv_width) + 1),
                y + (i / inv_width) * config.TILESIZE + 2 * ((i / inv_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dh_green",
        )

    if curr_item != -1 and curr_item < inv_width * inv_height:
        g.create_norm_box(
            (
                x + (curr_item % inv_width) * config.TILESIZE + 2 * ((curr_item % inv_width) + 1),
                y + (curr_item / inv_width) * config.TILESIZE + 2 * ((curr_item / inv_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dark_green",
        )

    # draw the skill pictures.
    for i in range(len(player.skill)):
        if player.skill[i][5] != 0 and (player.skill[i][1] == 5 or player.skill[i][1] == 6):
            draw_item(player.skill[i][7], i % inv_width, i / inv_width, x, y, screen_str)

    # draw the help text
    g.create_norm_box((tmp_menu_x_base, tmp_menu_y_base + tmp_menu_height), (tmp_menu_width, 17))
    if len(player.skill) <= curr_item or curr_item == -1 or player.skill[curr_item][5] == 0 or player.skill[curr_item][1] <= 4:
        helptext = ""
    else:
        helptext = player.skill[curr_item][0] + " (" + str(player.skill[curr_item][2]) + " EP)"
    g.print_string(g.screen, helptext, g.font, (tmp_menu_x_base + 2, tmp_menu_y_base + tmp_menu_height + 1))

    pygame.display.flip()


# Refreshes the stat display to the right side of the inv.
def refresh_stat_display():

    start_x = (config.TILESIZE * main.mapsizex) / 2
    start_y = (config.TILESIZE * main.mapsizey - total_height) / 2
    # hp/ep bars
    # 	main.canvas_map.delete("stats")
    # Create the hp/ep background bars

    bar_height = 15
    bar_start = start_y + 21

    g.create_norm_box((start_x + 5, bar_start - 1), (g.hpbar_width, bar_height), inner_color="hp_red")
    g.create_norm_box((start_x + 5, bar_start + bar_height + 1), (g.hpbar_width, bar_height), inner_color="hp_red")

    temp_width = g.hpbar_width * player.hp / player.adj_maxhp
    temp_width = max(temp_width, 0)

    bar_height = 15
    bar_start = start_y + 21
    g.create_norm_box((start_x + 5, bar_start - 1), (temp_width, bar_height), inner_color="hp_green")
    # 	main.canvas_map.create_rectangle(start_x+5, bar_start-1, start_x+temp_width+5,
    # 		bar_start+bar_height-1, fill="#05BB05", tags=("stats", "inv"))
    # 	main.canvas_map.delete("show_ep")
    temp_width = g.hpbar_width * player.ep / player.adj_maxep
    temp_width = max(temp_width, 0)
    g.create_norm_box((start_x + 5, bar_start + bar_height + 1), (temp_width, bar_height), inner_color="ep_blue")
    # 	main.canvas_map.create_rectangle(start_x+5, bar_start+bar_height+1, start_x+temp_width+5,
    # 		bar_start+bar_height*2+1, fill="#2525EE", tags=("stats", "inv"))
    # 	main.canvas_map.lift("bar")

    tmp_width = 52
    screen.fill(
        config.COLORS["light_gray"],
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 5, 50, 14),
    )
    g.print_string(
        g.screen, player.name, g.font, (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 5)
    )
    g.print_string(
        g.screen,
        str(player.hp) + "/" + str(player.adj_maxhp),
        g.font,
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 22),
    )
    g.print_string(
        g.screen,
        str(player.ep) + "/" + str(player.adj_maxep),
        g.font,
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 39),
    )

    screen.fill(
        config.COLORS["light_gray"],
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 55, 50, 80),
    )
    g.print_string(
        g.screen,
        str(player.adj_attack),
        g.font,
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 55),
    )
    g.print_string(
        g.screen,
        str(player.adj_defense),
        g.font,
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 70),
    )
    g.print_string(
        g.screen,
        str(player.gold),
        g.font,
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 85),
    )
    g.print_string(
        g.screen,
        str(player.level),
        g.font,
        (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 100),
    )
    tmp = str(player.exp_till_level())
    if tmp == "9999":
        g.print_string(
            g.screen,
            str(player.exp) + "/----",
            g.font,
            (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 115),
        )
    else:
        g.print_string(
            g.screen,
            str(player.exp) + "/" + str(player.exp_till_level() + player.exp),
            g.font,
            (start_x + tmp_width, (config.TILESIZE * main.mapsizey - total_height) / 2 + 115),
        )

    main.refresh_bars()
    main.refresh_inv_icon()
    pygame.display.flip()


def leave_inv() -> None:
    """Called when "Leave" is pressed"""
    if action.has_dialog == 1:
        return
    g.cur_window = "main"


def rm_equip() -> None:
    """Puts a worn item into the inventory. Called from the remove button."""
    if action.has_dialog == 1:
        return
    # Curr_item is the current location in the equipment canvas.
    # The missing numbers in this sequence are the blank spots in the display.
    sel_equipment = -1
    c_item = curr_item - inv_width * inv_height
    if c_item == 1:
        sel_equipment = 3
    elif c_item == 2:
        sel_equipment = 4
    elif c_item == 3:
        sel_equipment = 0
    elif c_item == 4:
        sel_equipment = 1
    elif c_item == 5:
        sel_equipment = 2
    elif c_item == 7:
        sel_equipment = 5
    if sel_equipment == -1:
        return

    if player.equip[sel_equipment] != -1 and item.take_inv_item(player.equip[sel_equipment]) != -1:
        main.print_message("You take off your " + item.item[player.equip[sel_equipment]].name)
        player.equip[sel_equipment] = -1
    player.reset_stats()
    refresh_equip()
    refresh_stat_display()


def wear_item() -> None:
    """Wears the item at the current location in the inventory."""
    if action.has_dialog == 1:
        return
    if curr_item >= inv_width * inv_height:
        rm_equip()
        return

    try:
        item_value = item.inv[curr_item]
    except IndexError:
        return

    if item_value == -1:
        return

    # Put the equip slot into item_loc
    item_loc = item.item[item_value].type

    # If item is equipment, trade the item and whatever is in the equip slot
    if item_loc < 6:
        temp = player.equip[item_loc]
        player.equip[item_loc] = item_value
        item.drop_inv_item(curr_item)
        item.take_inv_item(temp)
        main.print_message("You equip yourself with your " + item.item[player.equip[item_loc]].name + ".")
        player.reset_stats()
        if config.mut["CURR_BUTTON"] == 0:
            refresh_use()
        elif config.mut["CURR_BUTTON"] == 1:
            refresh_equip()
    refresh_stat_display()


def drop_item() -> None:
    """Drops the item at the current location in the inventory."""
    if action.has_dialog == 1:
        return
    if curr_item >= len(item.inv) or item.inv[curr_item] == -1:
        return
    try:
        item_to_delete = item.find_inv_item(item.inv[curr_item])
    except IndexError:
        return

    if item.item[item.inv[item_to_delete]].price == 0 and item.item[item.inv[item_to_delete]].value == 0:
        main.print_message("You feel attached to your " + item.item[item.inv[item_to_delete]].name)
        return
    # the inv[] location of the item is now in item_to_delete.

    # Ask if the player really wants to drop it.
    tmp_surface = pygame.Surface((300, 200))
    tmp_surface.blit(screen, (0, 0), (170, 140, 300, 200))
    if main.show_yesno("Drop your " + item.item[item.inv[item_to_delete]].name + "?"):
        screen.blit(tmp_surface, (170, 140))
        main.print_message("You drop your " + item.item[item.inv[curr_item]].name)

        # Add dropped item to map
        config.MAPS[g.zgrid].additem(item.item[item.inv[item_to_delete]].name, g.xgrid, g.ygrid)

        # Remove the item from inventory
        item.drop_inv_item(curr_item)
    else:
        screen.blit(tmp_surface, (170, 140))
    main.refresh_tile(g.xgrid, g.ygrid, g.zgrid)
    g.cur_window = "inventory_drop"
    refresh_drop()


def use_item(item_index: int = -1) -> None:
    """
    Uses the item at the current location in the inventory

    Args:
        item_index (int): The index of the item to use. If -1, uses the current item.
    """
    # 	if action.has_dialog == 1: return 0
    if item_index == -1:
        if curr_item >= len(item.inv) or item.inv[curr_item] == -1:
            return

        # put the item[] index of the item into item_value
        try:
            item_value = item.inv[curr_item]
        except IndexError:
            return

        # put the equip slot into item_loc
        item_loc = item.item[item_value].type
        # if equipment
        if item_loc < 6:
            wear_item()
            return
        if item_loc == 15:
            return
        main.print_message("You use your " + item.item[item_value].name)
    else:
        item_value = item_index
        item_loc = item.item[item_index].type
    # if item is healing
    if item_loc == 11:
        # heal the player, delete the item
        player.take_damage(item.item[item_value].quality)
        if item_index == -1:
            item.drop_inv_item(curr_item)
    if item_loc in {16, 17} and action.activate_lines(g.xgrid, g.ygrid, g.zgrid, item.item[item_value].scripting) == 1 and item_index == -1:
        item.drop_inv_item(curr_item)

    if item_index == -1:
        refresh_use()
        refresh_stat_display()


def useskill(free_skill: int = 0) -> bool:
    """"""
    # sanity checks
    skill_index = curr_item
    if skill_index >= len(player.skill):
        return True

    if free_skill == 0:
        if player.skill[skill_index][5] == 0:
            return True
        if player.skill[skill_index][2] > player.ep:
            return True

    if player.skill[skill_index][1] in {5, 6}:  # Scripted
        tempxy = (g.xgrid, g.ygrid, g.zgrid)
        # If the scripting ends with an "end" command,
        if action.activate_lines(g.xgrid, g.ygrid, g.zgrid, player.skill[skill_index][6]) == 1 and free_skill == 0:
            # Pay for the skill
            player.use_ep(-1 * player.skill[skill_index][2])
        main.refresh_bars()
        refresh_stat_display()
        if tempxy != (g.xgrid, g.ygrid, g.zgrid):
            return False
    return True


def refresh_menu_buttons() -> None:
    """Refreshes the buttons in the main inventory menu."""
    global oldbutton
    if action.has_dialog == 1:
        return
    if oldbutton == config.mut["CURR_BUTTON"]:
        return
    oldbutton = config.mut["CURR_BUTTON"]
    use_image = "use.png"
    equip_image = "equip.png"
    drop_image = "drop.png"
    skill_image = "skill.png"
    save_image = "save.png"
    leave_image = "leave.png"
    if config.mut["CURR_BUTTON"] == 0:
        use_image = "use_sel.png"
    elif config.mut["CURR_BUTTON"] == 1:
        equip_image = "equip_sel.png"
    elif config.mut["CURR_BUTTON"] == 2:
        drop_image = "drop_sel.png"
    elif config.mut["CURR_BUTTON"] == 3:
        skill_image = "skill_sel.png"
    elif config.mut["CURR_BUTTON"] == 4:
        save_image = "save_sel.png"
    elif config.mut["CURR_BUTTON"] == 5:
        leave_image = "leave_sel.png"

    screen.blit(config.BUTTONS[use_image], (base_x, base_y))
    screen.blit(config.BUTTONS[equip_image], (base_x, base_y + equip_height))
    screen.blit(config.BUTTONS[drop_image], (base_x, base_y + drop_height))
    screen.blit(config.BUTTONS[skill_image], (base_x, base_y + skill_height))
    screen.blit(config.BUTTONS[save_image], (base_x, base_y + save_height))
    screen.blit(config.BUTTONS[leave_image], (base_x, base_y + leave_height))

    pygame.display.flip()


def draw_item(input_picture: str, x: int, y: int, x_offset: int, y_offset: int) -> None:
    """
    Draw an item at the specified coordinates

    Args:
        input_picture (str): The name of the picture to draw.
        x (int): The x coordinate in tiles.
        y (int): The y coordinate in tiles.
        x_offset (int): The x offset from the upper-left of the canvas.
        y_offset (int): The y offset from the upper-left of the canvas.
    """
    screen.blit(
        config.TILES[input_picture],
        (x_offset + x * config.TILESIZE + 2 * (x + 1), y_offset + y * config.TILESIZE + 2 * (y + 1)),
    )


def menu_key_handler(key_name: int) -> bool:
    """
    All keypresses in window_inv pass through here.

    Based on the key name, give the right action ("etc", "left", "right", "up", "down", "return").
    """
    if key_name == config.BINDINGS["cancel"]:
        return True
    if (key_name == config.BINDINGS["right"]) or (key_name == config.BINDINGS["down"]):
        config.mut["CURR_BUTTON"] += 1
        if config.mut["CURR_BUTTON"] > 5:
            config.mut["CURR_BUTTON"] = 0
    elif (key_name == config.BINDINGS["left"]) or (key_name == config.BINDINGS["up"]):
        config.mut["CURR_BUTTON"] -= 1
        if config.mut["CURR_BUTTON"] < 0:
            config.mut["CURR_BUTTON"] = 5
    elif key_name == config.BINDINGS["action"]:
        # I take care of refresh by grabbing the current window as a bitmap,
        # then redisplaying it. Note that the -64 is to prevent the message
        # scroller from being clobbered
        old_screen_refresh = pygame.Surface((pygscreen.SCREEN_WIDTH, pygscreen.SCREEN_HEIGHT - 64))
        old_screen_refresh.blit(screen, (0, 0))
        if config.mut["CURR_BUTTON"] == 0:
            open_use_item()
        elif config.mut["CURR_BUTTON"] == 1:
            open_equip_item()
        elif config.mut["CURR_BUTTON"] == 2:
            open_drop_item()
        elif config.mut["CURR_BUTTON"] == 3:
            tmp = open_skill_menu()
            if tmp == "end":
                return True
        elif config.mut["CURR_BUTTON"] == 4:
            if action.has_dialog == 1:
                return False
            save_mgmt.savegame(player.name)
            main.print_message("** Game Saved **")
            pygame.display.flip()
            return False
        elif config.mut["CURR_BUTTON"] == 5:
            leave_inv()
            return True
        screen.blit(old_screen_refresh, (0, 0))
    refresh_menu_buttons()
    refresh_stat_display()

    return False


# generic key handler for anytime there is an inner inv window open.
def inner_key_handler(key_name):
    global curr_item
    if key_name == config.BINDINGS["cancel"]:
        return 1
    if key_name == config.BINDINGS["right"]:
        curr_item += 1
        if curr_item >= inv_width * inv_height:
            curr_item -= inv_width * inv_height
    elif key_name == config.BINDINGS["left"]:
        curr_item -= 1
        if curr_item < 0:
            curr_item += inv_width * inv_height
    elif key_name == config.BINDINGS["up"]:
        curr_item -= inv_width
        if curr_item < 0:
            curr_item += inv_width * inv_height
    elif key_name == config.BINDINGS["down"]:
        curr_item += inv_width
        if curr_item >= inv_width * inv_height:
            curr_item -= inv_width * inv_height
    elif key_name == config.BINDINGS["action"]:
        return 2
    return 0


def use_key_handler(key_name):
    tmp = inner_key_handler(key_name)
    if tmp == 2:
        use_item()
    if tmp != 1:
        refresh_use()
    return tmp


def drop_key_handler(key_name):
    tmp = inner_key_handler(key_name)
    if tmp == 2:
        drop_item()
    if tmp != 1:
        refresh_drop()
    return tmp


def skill_key_handler(key_name):
    tmp = inner_key_handler(key_name)
    if tmp == 2:
        tmp2 = useskill()
        if not tmp2:
            return "end"
    if tmp != 1:
        refresh_skill("skill")
    return tmp


# I have to do this separate, as the equip screen has an extra display.
def equip_key_handler(key_name):
    global curr_item
    if key_name == config.BINDINGS["cancel"]:
        return 1
    if key_name == config.BINDINGS["right"]:
        if config.mut["CURR_BUTTON"] == 1:  # if equip screen
            if curr_item < inv_width * inv_height:  # if in inv
                if curr_item % inv_width == inv_width - 1:  # if on right side
                    if curr_item / inv_width >= equip_size:
                        curr_item = equip_size * inv_width - 1
                    curr_item = (curr_item / inv_width) * equip_size + inv_width * inv_height - 1
            else:  # equip
                c_item = curr_item - inv_width * inv_height
                if c_item % equip_size == equip_size - 1:  # if on right side
                    curr_item = (c_item / equip_size) * inv_width - 1
        curr_item += 1
    elif key_name == config.BINDINGS["left"]:
        if config.mut["CURR_BUTTON"] == 1:  # if equip screen
            if curr_item < inv_width * inv_height:  # if in inv
                if curr_item % inv_width == 0:  # if on left side
                    if curr_item / inv_width >= equip_size:
                        curr_item = (equip_size - 1) * inv_width
                    curr_item = ((curr_item / inv_width) + 1) * equip_size + inv_width * inv_height
            else:  # equip
                c_item = curr_item - inv_width * inv_height
                if c_item % equip_size == 0:  # if on left side
                    curr_item = ((c_item / equip_size) + 1) * inv_width
        curr_item -= 1
    elif key_name == config.BINDINGS["up"]:
        if curr_item >= inv_width * inv_height:  # equip
            curr_item -= equip_size
            if curr_item < (inv_width * inv_height):
                curr_item += equip_size * equip_size
        else:  # inv
            curr_item -= inv_width
            if curr_item < 0:
                curr_item += inv_width * inv_height
    elif key_name == config.BINDINGS["down"]:
        if curr_item >= inv_width * inv_height:  # equip
            curr_item += equip_size
            if curr_item >= (inv_width * inv_height) + (equip_size * equip_size):
                curr_item -= equip_size * equip_size
        else:  # inv
            curr_item += inv_width
            if curr_item >= inv_width * inv_height:
                curr_item -= inv_width * inv_height
    elif key_name == config.BINDINGS["action"]:
        wear_item()
    refresh_equip()
    return 0


def menu_mouse_click(xy: tuple[int, int]) -> bool:
    """"""
    if action.has_dialog == 1:
        return False
    base_loc_y = xy[1] - base_y
    base_loc_x = xy[0] - base_x
    if base_loc_y < 0 or base_loc_x < 0 or base_loc_y > total_height or base_loc_x > button_width:
        return False
    return menu_key_handler(config.BINDINGS["action"])


def inner_mouse_click(xy, button) -> int:
    """Generic mouse click while an inner menu is open"""
    # decide if the mouse is within one of the boxes.
    global curr_item
    temp_num = which_box(xy[0] - tmp_x_base, xy[1] - tmp_y_base, inv_width)
    if (
        (xy[0] > tmp_menu_x_base)
        and (xy[1] > tmp_menu_y_base)
        and (xy[0] < tmp_menu_x_base + tmp_menu_width)
        and xy[1] < tmp_menu_y_base + tmp_menu_height
    ):
        if xy[0] < tmp_menu_x_base + config.BUTTONS[button + ".png"].get_width():
            return 2
        return 1
    curr_item = temp_num
    return 0


def use_mouse_click(xy) -> int:
    """"""
    tmp = inner_mouse_click(xy, "use")
    if tmp == 2:
        use_item()
    if tmp != 1:
        refresh_use()
    return tmp


def drop_mouse_click(xy) -> int:
    """"""
    tmp = inner_mouse_click(xy, "use")
    if tmp == 2:
        drop_item()
    if tmp != 1:
        refresh_drop()
    return tmp


def skill_mouse_click(xy) -> int:
    """"""
    tmp = inner_mouse_click(xy, "skill")
    if tmp == 2:
        tmp2 = useskill()
        if not tmp2:
            return "end"
    if tmp != 1:
        refresh_skill("skill")
    return tmp


def equip_mouse_click(xy: tuple[int, int]) -> bool:
    """"""
    # decide if the mouse is within one of the boxes.
    global curr_item
    temp_num = which_box(xy[0] - tmp_x_base, xy[1] - tmp_y_base, inv_width)
    # If the click was outside of the inv area.
    if temp_num == -1:
        temp_canvas_width = (config.TILESIZE * equip_size) + 8
        # If the click was in the button area.
        if (
            (xy[0] > tmp_menu_x_base)
            and (xy[1] > tmp_menu_y_base)
            and (xy[0] < tmp_menu_x_base + tmp_menu_width)
            and xy[1] < tmp_menu_y_base + tmp_menu_height
        ):
            if xy[0] < tmp_menu_x_base + config.BUTTONS["equip.png"].get_width():
                wear_item()
            else:
                return True
        # If the click was inside the equip area.
        elif (
            (xy[0] > tmp_x_base - temp_canvas_width)
            and (xy[1] > tmp_y_base)
            and (xy[0] < tmp_x_base)
            and (xy[1] < tmp_y_base + temp_canvas_width)
        ):
            temp_num = which_box(xy[0] - tmp_x_base + temp_canvas_width, xy[1] - tmp_y_base, equip_size)
            if temp_num != -1:
                curr_item = temp_num + inv_width * inv_height
    else:
        curr_item = temp_num
    refresh_equip()

    return False


def inner_mouse_dbl_click(xy):
    # decide if the mouse is within one of the boxes.
    global curr_item
    temp_num = which_box(xy[0] - tmp_x_base, xy[1] - tmp_y_base, inv_width)
    if temp_num != -1:
        curr_item = temp_num
        return 1
    return 0


def equip_mouse_dbl_click(xy):
    # decide if the mouse is within one of the boxes.
    global curr_item
    temp_num = which_box(xy[0] - tmp_x_base, xy[1] - tmp_y_base, inv_width)
    # If the click was outside of the inv area.
    if temp_num == -1:
        temp_canvas_width = (config.TILESIZE * equip_size) + 8
        # If the click was inside the equip area.
        if (
            (xy[0] > tmp_x_base - temp_canvas_width)
            and (xy[1] > tmp_y_base)
            and (xy[0] < tmp_x_base)
            and (xy[1] < tmp_y_base + temp_canvas_width)
        ):
            temp_num = which_box(xy[0] - tmp_x_base + temp_canvas_width, xy[1] - tmp_y_base, equip_size)
            if temp_num != -1:
                curr_item = temp_num + inv_width * inv_height
                wear_item()
    else:
        curr_item = temp_num
        wear_item()
    refresh_equip()


def drop_mouse_dbl_click(xy):
    if inner_mouse_dbl_click(xy):
        drop_item()
    refresh_drop()


def use_mouse_dbl_click(xy):
    if inner_mouse_dbl_click(xy):
        use_item()
    refresh_use()


def skill_mouse_dbl_click(xy):
    if inner_mouse_dbl_click(xy):
        useskill()
    refresh_skill("skill")


# Used in mouse_sel_inv. Takes x y coordinates, (relative to the upper-left of
# the inv box) and returns the selected box, or -1 for none. temp_size is
# the width of the inventory box.
def which_box(x, y, temp_size):
    # Check for the left border
    if x < 3:
        return -1
    # Transform x from pixels to tiles
    tempx = x - 3
    likelyx = tempx / (config.TILESIZE + 2)
    tempx -= (likelyx * (config.TILESIZE + 2))
    if tempx >= config.TILESIZE - 1:
        return -1

    # Check for the top border
    if y < 3:
        return -1
    # Transform y from pixels to tiles
    tempy = y - 3
    likelyy = tempy / (config.TILESIZE + 2)
    tempy -= (likelyy * (config.TILESIZE + 2))
    if tempy >= config.TILESIZE - 1:
        return -1
    # Final check, then return the location in the inv.
    if likelyy * temp_size + likelyx >= temp_size * inv_height:
        return -1
    if likelyx >= temp_size:
        return -1
    return likelyy * temp_size + likelyx


def menu_mouse_move(xy):
    base_loc_y = xy[1] - base_y
    base_loc_x = xy[0] - base_x
    if base_loc_y < 0 or base_loc_x < 0 or base_loc_y > total_height or base_loc_x > button_width:
        return
    if base_loc_y < equip_height:
        config.mut["CURR_BUTTON"] = 0
    elif base_loc_y < drop_height:
        config.mut["CURR_BUTTON"] = 1
    elif base_loc_y < skill_height:
        config.mut["CURR_BUTTON"] = 2
    elif base_loc_y < save_height:
        config.mut["CURR_BUTTON"] = 3
    elif base_loc_y < leave_height:
        config.mut["CURR_BUTTON"] = 4
    else:
        config.mut["CURR_BUTTON"] = 5
    refresh_menu_buttons()


def inner_mouse_move(xy, button=""):
    global inner_cur_button
    if (
        (xy[0] > tmp_menu_x_base)
        and (xy[1] > tmp_menu_y_base)
        and (xy[0] < tmp_menu_x_base + tmp_menu_width)
        and xy[1] < tmp_menu_y_base + tmp_menu_height
    ):
        if xy[0] < tmp_menu_x_base + config.BUTTONS[button + ".png"].get_width():
            inner_cur_button = 0
        else:
            inner_cur_button = 1
        return 1
    return 0


def use_mouse_move(xy):
    if inner_mouse_move(xy, "use"):
        refresh_inner_buttons("use")


def drop_mouse_move(xy):
    if inner_mouse_move(xy, "drop"):
        refresh_inner_buttons("drop")


def equip_mouse_move(xy):
    if inner_mouse_move(xy, "equip"):
        refresh_inner_buttons("equip")


def skill_mouse_move(xy):
    if inner_mouse_move(xy, "skill"):
        refresh_inner_buttons("skill")


# This creates the inv area within the map canvas.
def init_window_inv():
    global oldbutton
    oldbutton = 99

    # Location of the various buttons.
    global equip_height
    equip_height = config.BUTTONS["use.png"].get_height()
    global drop_height
    drop_height = equip_height + config.BUTTONS["equip.png"].get_height()
    global skill_height
    skill_height = drop_height + config.BUTTONS["skill.png"].get_height()
    global save_height
    save_height = skill_height + config.BUTTONS["drop.png"].get_height()
    global leave_height
    leave_height = save_height + config.BUTTONS["save.png"].get_height()
    global total_height
    total_height = leave_height + config.BUTTONS["leave.png"].get_height()

    global button_width
    button_width = config.BUTTONS["drop.png"].get_width()

    global base_x
    base_x = (config.TILESIZE * main.mapsizex) / 2 - button_width
    global base_y
    base_y = (config.TILESIZE * main.mapsizey - total_height) / 2

    global inv_canvas_width
    global inv_canvas_height
    inv_canvas_width = (config.TILESIZE * inv_width) + ((inv_width + 1) * 2) + 1
    inv_canvas_height = (config.TILESIZE * inv_height) + ((inv_height + 1) * 2) + 1

    # start_x = (config.TILESIZE * main.mapsizex) / 2
    # start_y = (config.TILESIZE * main.mapsizey - total_height) / 2

    # Create the main inv box.
    # The +20 is just "wiggle room", to prevent the length of the name
    # affecting the dimensions.
    g.create_norm_box(
        (base_x, base_y),
        (
            (config.TILESIZE * main.mapsizex) / 2 + g.hpbar_width + 15 - base_x,
            (config.TILESIZE * main.mapsizey + total_height) / 2 - base_y,
        ),
    )

    global curr_item
    curr_item = 0

    # Set current window to inventory
    g.cur_window = "inventory"

    temp_width = g.hpbar_width * player.ep / player.adj_maxep
    temp_width = max(temp_width, 0)

    # Create the labels to the right:
    tmp_width = 52
    label_start = (
        (config.TILESIZE * main.mapsizex) / 2 + tmp_width,
        (config.TILESIZE * main.mapsizey - total_height) / 2,
    )
    text = "Name:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 5), align=2)
    text = "HP:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 22), align=2)
    text = "MP:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 39), align=2)
    text = "Attack:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 55), align=2)
    text = "Defense:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 70), align=2)
    text = "Gold:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 85), align=2)
    text = "Level:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 100), align=2)
    text = "XP:"
    g.print_string(g.screen, text, g.font, (label_start[0], label_start[1] + 115), align=2)

    # bindings
    menu_bind_keys()
    refresh_menu_buttons()
    refresh_stat_display()
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if menu_key_handler(event.key):
                    return
            elif event.type == pygame.MOUSEMOTION:
                menu_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_mouse_click(event.pos):
                    return


def menu_bind_keys() -> None:
    """
    Bind the keys for the inventory menu.

    Called upon window creation and return from a yes/no box
    """
    g.cur_window = "inventory"
