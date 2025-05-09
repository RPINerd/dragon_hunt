# file: shop.py
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

# This file controls the town shops.


import pygame
from icecream import ic

import config
import g
import game_screen as pygscreen
import item
import main
import widgets
from player import player

screen = pygscreen.get_screen()

# location of the store in the g.shops[] array
store_num = 0

# width/height of inv and shop windows, in tiles.
# (config.TILESIZE + the 3 pixel border)
shop_width = 4
shop_height = 7

# Currently selected item number
curr_item = 0
# If inv (0) or shop (1) has focus.
curr_focus = 1

# currently selected button: 0=sell 1=leave 2=buy
cur_button = 2

leave_height = 0
buy_height = 0
sell_height = 0

temp_canvas_width = 0
temp_canvas_height = 0
canvas_x_start = 0
canvas_y_start = 0


temp_button_x = 0
temp_button_width = 0
temp_button_y = 0


def refresh_buttons() -> None:
    """Redraw the buttons at the bottom of the shop window."""
    global prev_button

    if prev_button == config.mut["CURR_BUTTON"]:
        return
    prev_button = config.mut["CURR_BUTTON"]

    widgets.bordered_box(screen, (temp_button_x, temp_button_y), (temp_button_width, config.BUTTONS["sell.png"].get_height()))

    if config.mut["CURR_BUTTON"] == 0:
        screen.blit(config.BUTTONS["sell_sel.png"], (temp_button_x, temp_button_y))
    else:
        screen.blit(config.BUTTONS["sell.png"], (temp_button_x, temp_button_y))

    if config.mut["CURR_BUTTON"] == 1:
        screen.blit(config.BUTTONS["leave_shop_sel.png"], (temp_button_x + leave_height, temp_button_y))
    else:
        screen.blit(config.BUTTONS["leave_shop.png"], (temp_button_x + leave_height, temp_button_y))

    if config.mut["CURR_BUTTON"] == 2:
        screen.blit(config.BUTTONS["buy_sel.png"], (temp_button_x + buy_height, temp_button_y))
    else:
        screen.blit(config.BUTTONS["buy.png"], (temp_button_x + buy_height, temp_button_y))

    pygame.display.flip()


def set_details(name: str, cost: int, value: int, power: int, description: str, inv_or_shop: str) -> None:
    """
    Sets the info in the middle of the shop screen

    Args:
        name (str): The name of the item.
        cost (int): The cost of the item (buying).
        value (int): The value of the item (selling).
        power (int): The power or quality level of the item.
        description (str): The description of the item.
        inv_or_shop (str): Whether the item is in the inventory or shop.
    """
    screen.fill(config.COLORS["light_gray"], (canvas_x_start + temp_canvas_width, canvas_y_start + 25, 137, 190))

    widgets.print_string(screen, name, g.font, (canvas_x_start + temp_canvas_width + 5, canvas_y_start + 25))

    if inv_or_shop == "shop":
        if cost:
            widgets.print_string(
                screen, "Cost: " + str(cost), g.font, (canvas_x_start + temp_canvas_width + 5, canvas_y_start + 40)
            )
    elif inv_or_shop == "inv" and value:
        widgets.print_string(
            screen, "Value: " + str(value), g.font, (canvas_x_start + temp_canvas_width + 5, canvas_y_start + 40)
        )

    if not power or power == "-1":
        pass
    else:
        widgets.print_string(
            screen, "Power: " + str(power), g.font, (canvas_x_start + temp_canvas_width + 5, canvas_y_start + 55)
        )

    widgets.print_paragraph(screen, description, g.font, 130, (canvas_x_start + temp_canvas_width + 5, canvas_y_start + 70))

    pygame.display.flip()


def show_details(event: int = 0, sel_item: int = -1) -> None:
    """
    Show info for a selected item in the middle of the window

    The use of sel_item gives the ability to look at an item without selecting it, while working normally the rest of the time

    Args:
        # TODO event (int): The event that triggered this function.
        sel_item (int): The item to show details for
    """
    if sel_item == -1:
        sel_item = curr_item
    if curr_focus == 0:  # inv
        if sel_item < len(item.inv):
            ic(sel_item)
            if item.inv[sel_item] != -1:
                tempitem = item.item[item.inv[sel_item]]
                if tempitem.type == 14 and g.shops[store_num].name == "a Gem Shop":
                    set_details(
                        tempitem.name,
                        tempitem.price,
                        tempitem.price,
                        tempitem.quality,
                        tempitem.description,
                        "inv",
                    )
                else:
                    set_details(
                        tempitem.name,
                        tempitem.price,
                        tempitem.value,
                        tempitem.quality,
                        tempitem.description,
                        "inv",
                    )
            # if there is no item selected, blank details.
            else:
                set_details("", "", "", "", "", "inv")
        else:
            set_details("", "", "", "", "", "inv")

    elif sel_item < len(g.shops[store_num].itemlist):
        tempitem = g.shops[store_num].itemlist[sel_item]
        set_details(
            tempitem.item_name,
            tempitem.cost,
            tempitem.value,
            tempitem.power,
            tempitem.description,
            "shop",
        )
    else:
        set_details("", "", "", "", "", "shop")


# place appropriate items into the store.
def refresh_shop():

    invpos = 0

    # per-item borders
    for y in range(shop_height):
        for x in range(shop_width):
            widgets.bordered_box(screen,
                (
                    canvas_x_start + x * config.TILESIZE + 2 * (x + 1),
                    canvas_y_start + y * config.TILESIZE + 2 * (y + 1),
                ),
                (config.TILESIZE, config.TILESIZE),
                inner_color="dh_green",
            )
    for y in range(shop_height):
        for x in range(shop_width):
            widgets.bordered_box(screen,
                (
                    temp_canvas_width * 2 + canvas_x_start + x * config.TILESIZE + 2 * (x + 1),
                    canvas_y_start + y * config.TILESIZE + 2 * (y + 1),
                ),
                (config.TILESIZE, config.TILESIZE),
                inner_color="dh_green",
            )

    # if the shop is selected, draw a selection box around the current item.
    if curr_focus == 1:
        widgets.bordered_box(screen,
            (
                (
                    canvas_x_start
                    + temp_canvas_width * 2
                    + (curr_item % shop_width) * config.TILESIZE
                    + 2 * ((curr_item % shop_width) + 1)
                ),
                canvas_y_start + (curr_item / shop_width) * config.TILESIZE + 2 * ((curr_item / shop_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dark_green",
        )

    # draw the item pictures.
    for i in range(len(g.shops[store_num].itemlist)):
        if i != -1:
            screen.blit(
                config.TILES[g.shops[store_num].itemlist[i].picture],
                (
                    canvas_x_start
                    + temp_canvas_width * 2
                    + (invpos % shop_width) * config.TILESIZE
                    + 2 * ((invpos % shop_width) + 1),
                    canvas_y_start + (invpos / shop_width) * config.TILESIZE + 2 * ((invpos / shop_width) + 1),
                ),
            )
            invpos += 1
    invpos = 0
    # if the inv is selected, draw a selection box around the current item.
    if curr_focus == 0:
        widgets.bordered_box(screen,
            (
                canvas_x_start + (curr_item % shop_width) * config.TILESIZE + 2 * ((curr_item % shop_width) + 1),
                canvas_y_start + (curr_item / shop_width) * config.TILESIZE + 2 * ((curr_item / shop_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dark_green",
        )

    # draw the item pictures.
    for i in range(len(item.inv)):
        if item.inv[i] != -1:
            screen.blit(
                config.TILES[item.item[item.inv[i]].picturename],
                (
                    canvas_x_start + (i % shop_width) * config.TILESIZE + 2 * ((i % shop_width) + 1),
                    canvas_y_start + (i / shop_width) * config.TILESIZE + 2 * ((i / shop_width) + 1),
                ),
            )
            invpos += 1

    # set gold and skillpoints
    screen.fill(
        config.COLORS["light_gray"],
        (canvas_x_start + temp_canvas_width + 5, canvas_y_start + temp_canvas_height - 26, 120, 25),
    )

    widgets.print_string(
        screen,
        "Gold: " + str(player.gold),
        g.font,
        (canvas_x_start + temp_canvas_width + 5, canvas_y_start + temp_canvas_height - 26),
    )
    widgets.print_string(
        screen,
        "Skill Points: " + str(player.skillpoints),
        g.font,
        (canvas_x_start + temp_canvas_width + 5, canvas_y_start + temp_canvas_height - 11),
    )

    main.refresh_inv_icon()
    main.refresh_bars()


def sell_item() -> None:
    """Called upon pressing "Sell"; uses the selected item."""
    if curr_focus != 0:
        return
    if curr_item > len(item.inv):
        return
    if item.inv[curr_item] == -1:
        return
    if item.item[item.inv[curr_item]].price == 0:
        main.print_message("You feel attached to your " + item.item[item.inv[curr_item]].name)
        return

    # Pay player for item
    """
    All stores have a 5 year, money-back guarantee, and accept returns from other stores as well.
    This means there is no need to doublecheck intent. ;)

    FIXME: this is no longer true since gems aren't paid for full value anywhere but the gem shop
    """
    if item.item[item.inv[curr_item]].type == 14 and g.shops[store_num].name == "a Gem Shop":
        main.print_message("The Gem Shop owner is happy to pay the true value of your gems.")
        player.give_gold(item.item[item.inv[curr_item]].price)
    else:
        player.give_gold(item.item[item.inv[curr_item]].value)

    main.print_message("You sell your " + item.item[item.inv[curr_item]].name + ".")

    # Remove the item from inventory
    item.drop_inv_item(curr_item)
    refresh_shop()
    show_details()


def buy_item() -> None:
    """Called upon pressing "Buy"; uses the selected item."""
    if curr_focus != 1:
        return
    if curr_item >= len(g.shops[store_num].itemlist):
        return

    if g.shops[store_num].itemlist[curr_item].buytype == "gold":
        # if enough gold
        if int(g.shops[store_num].itemlist[curr_item].cost) <= int(player.gold):
            # if no actions were given
            if len(g.shops[store_num].itemlist[curr_item].actions) == 0:
                # if given successfully.
                if (
                    main.action.run_command(0, 0, 0, 'item("' + g.shops[store_num].itemlist[curr_item].item_name + '")')
                    == 1
                ):
                    main.print_message("You buy a " + g.shops[store_num].itemlist[curr_item].item_name + ".")
                    player.give_gold(-1 * int(g.shops[store_num].itemlist[curr_item].cost))
                else:  # not enough room
                    main.print_message("Your inventory is full.")
            else:
                temp = main.action.activate_lines(0, 0, 0, g.shops[store_num].itemlist[curr_item].actions)
                if temp == 1:
                    player.give_gold(-1 * int(g.shops[store_num].itemlist[curr_item].cost))
    # if enough skillpoints
    elif int(g.shops[store_num].itemlist[curr_item].cost) <= int(player.skillpoints):
        # if no actions were given
        if len(g.shops[store_num].itemlist[curr_item].actions) == 0:
            # if given successfully.
            if (
                main.action.run_command(0, 0, 0, 'item("' + g.shops[store_num].itemlist[curr_item].item_name + '")')
                == 1
            ):
                main.print_message("You buy a " + g.shops[store_num].itemlist[curr_item].item_name + ".")
                player.add_skillpoints(-1 * int(g.shops[store_num].itemlist[curr_item].cost))
        else:
            temp = main.action.activate_lines(0, 0, 0, g.shops[store_num].itemlist[curr_item].actions)
            if temp == 1:
                player.add_skillpoints(-1 * int(g.shops[store_num].itemlist[curr_item].cost))

    refresh_shop()
    show_details()


# Used in mouse_sel_inv and mouse_sel_shop. Takes x y coordinates, and returns
# the selected box, or -1 for none.
def which_box(x, y):
    if x < 3:
        return -1
    tempx = x - 3
    likelyx = tempx / (config.TILESIZE + 2)
    tempx -= (likelyx * (config.TILESIZE + 2))
    if tempx >= config.TILESIZE - 1:
        return -1

    if y < 3:
        return -1
    tempy = y - 3
    likelyy = tempy / (config.TILESIZE + 2)
    tempy -= (likelyy * (config.TILESIZE + 2))
    if tempy >= config.TILESIZE - 1:
        return -1

    if likelyx >= shop_width:
        return -1
    if likelyy * shop_width + likelyx >= shop_width * shop_height:
        return -1

    return likelyy * shop_width + likelyx


# called when the user releases the mouse in the inv canvas.
def mouse_sel_inv(xy):
    # decide if the mouse is within one of the boxes.
    global curr_item
    global curr_focus
    temp_num = which_box(xy[0], xy[1])
    if temp_num == -1:
        return
    curr_item = temp_num
    curr_focus = 0
    refresh_shop()
    show_details()


def mouse_sel_shop(xy: tuple[int, int]) -> bool:
    """Called when the user releases the mouse in the shop canvas."""
    global curr_item
    global curr_focus
    global last_click_time
    global last_box
    # Is the mouse at least in the general area?.
    if xy[0] < canvas_x_start or xy[1] < canvas_y_start:
        return False

    if last_click_time + 200 > pygame.time.get_ticks():
        last_click_time = 0
        return mouse_handler_dbl(xy)
    last_click_time = pygame.time.get_ticks()

    temp_num = which_box(xy[0] - canvas_x_start, xy[1] - canvas_y_start)
    if temp_num != -1:
        curr_item = int(temp_num)
        curr_focus = 0
        config.mut["CURR_BUTTON"] = 0
        refresh_shop()
        show_details()
        return False

    temp_num = which_box(xy[0] - canvas_x_start - temp_canvas_width * 2, xy[1] - canvas_y_start)
    if temp_num != -1:
        curr_item = int(temp_num)
        curr_focus = 1
        config.mut["CURR_BUTTON"] = 2
        refresh_shop()
        show_details()
        return False

    if (
        xy[0] > temp_button_x
        and xy[0] < temp_button_x + temp_button_width
        and xy[1] > temp_button_y
        and xy[1] < temp_button_y + config.BUTTONS["buy.png"].get_height()
    ):
        if xy[0] < temp_button_x + leave_height:
            sell_item()
        elif xy[0] < temp_button_x + buy_height:
            # leave_shop()
            return True
        else:
            buy_item()
        refresh_buttons()

    return False


def mouse_handler_dbl(xy: tuple[int, int]) -> bool:
    """"""
    global curr_item
    global curr_focus

    # Is the mouse at least in the general area?.
    if xy[0] < canvas_x_start or xy[1] < canvas_y_start:
        return False

    temp_num = which_box(xy[0] - canvas_x_start, xy[1] - canvas_y_start)
    if temp_num != -1:
        curr_item = temp_num
        curr_focus = 0
        config.mut["CURR_BUTTON"] = 0
        sell_item()
        refresh_shop()
        show_details()
        return False

    temp_num = which_box(xy[0] - canvas_x_start - temp_canvas_width * 2, xy[1] - canvas_y_start)
    if temp_num != -1:
        curr_item = temp_num
        curr_focus = 1
        config.mut["CURR_BUTTON"] = 2
        buy_item()
        refresh_shop()
        show_details()
        return False

    # ! Might be a mistake to add this
    return True


def mouse_move(xy: tuple[int, int]) -> None:
    """Called when the mouse moves over the shop window."""
    if (
        xy[0] > temp_button_x
        and xy[0] < temp_button_x + temp_button_width
        and xy[1] > temp_button_y
        and xy[1] < temp_button_y + config.BUTTONS["buy.png"].get_height()
    ):
        if xy[0] < temp_button_x + leave_height:
            config.mut["CURR_BUTTON"] = 0
        elif xy[0] < temp_button_x + buy_height:
            config.mut["CURR_BUTTON"] = 1
        else:
            config.mut["CURR_BUTTON"] = 2
        refresh_buttons()


def key_handler(switch: int) -> bool:
    """
    All keypresses in new_game pass through here

    Based on the key name, give the right action. ("etc", "left", "right", "up", "down", "return")
    """
    global curr_item
    global curr_focus
    # switch based on keycode
    if switch == config.BINDINGS["cancel"]:
        return True
    if switch == config.BINDINGS["action"]:
        if curr_focus == 1 and config.mut["CURR_BUTTON"] == 2:
            buy_item()
        elif curr_focus != 1 and config.mut["CURR_BUTTON"] == 0:
            sell_item()
        elif config.mut["CURR_BUTTON"] == 1:
            return True
    elif switch == config.BINDINGS["left"]:
        if curr_item % shop_width == 0:  # move between lists
            if curr_focus == 0:
                curr_focus = 1
                config.mut["CURR_BUTTON"] = 2
            else:
                curr_focus = 0
                config.mut["CURR_BUTTON"] = 0
            curr_item += shop_width
        curr_item -= 1
    elif switch == config.BINDINGS["right"]:
        if curr_item % shop_width == shop_width - 1:  # move between lists
            if curr_focus == 0:
                curr_focus = 1
                config.mut["CURR_BUTTON"] = 2
            else:
                curr_focus = 0
                config.mut["CURR_BUTTON"] = 0
            curr_item -= shop_width
        curr_item += 1
    elif switch == config.BINDINGS["up"]:
        curr_item -= shop_width
        if curr_item < 0:
            curr_item += shop_width * shop_height
    elif switch == config.BINDINGS["down"]:
        curr_item += shop_width
        if curr_item >= shop_width * shop_height:
            curr_item -= shop_width * shop_height

    refresh_shop()
    refresh_buttons()
    show_details()

    return False


def init_window_shop(store_type_input: str) -> None:
    """Initialize the shop window."""
    g.cur_window = "shop"
    global last_click_time
    last_click_time = 0
    global prev_button
    prev_button = 1
    global temp_canvas_width
    global temp_canvas_height
    global canvas_x_start
    global canvas_y_start
    global temp_button_x
    global temp_button_width
    global temp_button_y
    temp_canvas_width = (config.TILESIZE * shop_width) + ((shop_width + 1) * 2) + 1
    temp_canvas_height = (config.TILESIZE * shop_height) + ((shop_height + 1) * 2) + 1
    canvas_x_start = ((config.TILESIZE * main.mapsizex) - temp_canvas_width * 3) / 2
    canvas_y_start = ((config.TILESIZE * main.mapsizey) - temp_canvas_height) / 2
    temp_button_x = (
        canvas_x_start
        + (temp_canvas_width * 3) / 2
        - config.BUTTONS["sell.png"].get_width()
        - config.BUTTONS["leave_shop.png"].get_width() / 2
    )
    temp_button_width = (
        config.BUTTONS["sell.png"].get_width() + config.BUTTONS["leave_shop.png"].get_width() + config.BUTTONS["buy.png"].get_width()
    )
    temp_button_y = canvas_y_start + temp_canvas_height + 1

    global bgcolour
    bgcolour = "light_grey"

    widgets.bordered_box(screen, (canvas_x_start - 2, canvas_y_start - 19), (temp_canvas_width * 3 + 3, temp_canvas_height + 20))

    global curr_item
    curr_item = 0
    global curr_focus
    curr_focus = 1
    config.mut["CURR_BUTTON"] = 2

    store_type_input = store_type_input.lower()
    global store_num
    for i in range(len(g.shops)):
        if g.shops[i].name.lower() == store_type_input:
            store_num = i
            break

    widgets.bordered_box(screen, (canvas_x_start, canvas_y_start), (temp_canvas_width - 1, temp_canvas_height - 1))

    # per-item borders
    for y in range(shop_height):
        for x in range(shop_width):
            widgets.bordered_box(screen,
                (
                    canvas_x_start + x * config.TILESIZE + 2 * (x + 1),
                    canvas_y_start + y * config.TILESIZE + 2 * (y + 1),
                ),
                (config.TILESIZE, config.TILESIZE),
                inner_color="dh_green",
            )

    widgets.bordered_box(screen,
        (temp_canvas_width * 2 + canvas_x_start, canvas_y_start), (temp_canvas_width - 1, temp_canvas_height - 1)
    )

    # per-item borders
    for y in range(shop_height):
        for x in range(shop_width):
            widgets.bordered_box(screen,
                (
                    temp_canvas_width * 2 + canvas_x_start + x * config.TILESIZE + 2 * (x + 1),
                    canvas_y_start + y * config.TILESIZE + 2 * (y + 1),
                ),
                (config.TILESIZE, config.TILESIZE),
                inner_color="dh_green",
            )

    # Info labels
    widgets.print_string(
        screen, "Inventory", g.font, (canvas_x_start + (temp_canvas_width * 1) / 2, canvas_y_start - 15), align=1
    )

    widgets.print_string(
        screen,
        g.shops[store_num].name,
        g.font,
        (canvas_x_start + (temp_canvas_width * 5) / 2, canvas_y_start - 15),
        align=1,
    )

    global leave_height
    leave_height = config.BUTTONS["sell.png"].get_width()
    global buy_height
    buy_height = leave_height + config.BUTTONS["leave.png"].get_width()

    # get data in listboxes
    refresh_shop()
    refresh_buttons()
    show_details()

    pygame.display.flip()
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if key_handler(event.key) == 1:
                    return
            elif event.type == pygame.MOUSEMOTION:
                mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and mouse_sel_shop(event.pos):
                return
