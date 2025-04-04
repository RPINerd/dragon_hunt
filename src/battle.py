# battle.py
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

# this file controls the battle window.

import pygame
from icecream import ic

import action
import config
import g
import game_screen as pygscreen
import inv
import main
import monster
import utils
import widgets
from player import player

mon_index = 0

# mon_hp = StringVar()
# hp = StringVar()
# ep = StringVar()
# monstername = StringVar()
# monsterattack = StringVar()
# monsterdefense = StringVar()

# back_to_main = StringVar()

# help_text = StringVar()


# return_from_dialog = StringVar()

# location of the various buttons. (Pixels from the left of the canvas)
attack_button_loc = 0
item_button_loc = 0
skill_button_loc = 0
inspect_button_loc = 0
run_button_loc = 0
final_button_loc = 0

button_y_start = 0
button_height = 0

# did you run from this battle? Used for scripting.
did_run = 0

# currently selected button. 0=attack, 1=run/leave, 2=use item, 3=use skill
cur_button = 0

# Copy of monster.monster_groups[mon_index].monster_list.
# Used to reduce line length.
monster_list = []

# Number of times you've tried to run from this monster.
# Used to allow better chances after a while.
run_attempts = 0

# x location of the monster hp bar per monster. Used to redraw it.
base_mon_hp_start = []
base_mon_hp_width = []
# y location of the monster hp bar per monster. Used to redraw it.
base_mon_hp_y_start = []
base_mon_hp_height = []

# the currently selected monster.
active_button = -1

# gem usage stuff
used_gem = 0
num_dice = 1
old_attack = 0

# upper-left of the background/monster display.
monster_start = (0, 0)

screen = pygscreen.get_screen()


# given an index in the monster array, return the y start of the monster.
def y_start(mon_num):
    if len(monster.monster_groups[mon_index].y_pos) > mon_num:
        return monster_start[1] + monster.monster_groups[mon_index].y_pos[mon_num]
    return monster_start[1] + 10


# refreshes the battle view. Call after changing anything.
def refresh():
    global monster_slashes
    screen.fill(
        config.COLORS["black"],
        (
            config.TILESIZE * main.half_mapx - background_pic.get_width() / 2 - 2,
            config.TILESIZE * main.half_mapy - background_pic.get_height() / 2 - 2,
            background_pic.get_width() + 2,
            background_pic.get_height() + 2,
        ),
    )
    screen.blit(
        background_pic,
        (
            config.TILESIZE * main.half_mapx - background_pic.get_width() / 2 - 1,
            config.TILESIZE * main.half_mapy - background_pic.get_height() / 2 - 1,
        ),
    )
    # monsters
    for i in range(len(monster_list)):
        # if x and y positions were given, use them; otherwise, start at the
        # middle, and go right. This works for 1 or two monsters, but xy
        # coords are recommended for more.
        if len(monster.monster_groups[mon_index].x_pos) > i:
            xstart = monster_start[0] + monster.monster_groups[mon_index].x_pos[i]
        else:
            xstart = monster_start[0] + background_pic.get_width() / 2 + i * 40
        ystart = y_start(i)
        screen.blit(monster_pic[i], (base_mon_hp_start[i], ystart))

        # 		if monster_slashes[i][0] == 1:
        # 			screen.blit(config.BUTTONS["slash_attack.png"],
        # 				(base_mon_hp_start[i]+4, ystart+4))

        # Under (red) part of the monster hp display
        widgets.bordered_box(screen,
            (base_mon_hp_start[i], base_mon_hp_y_start[i]), (base_mon_hp_width[i], 5), inner_color="hp_red"
        )
        # Over (green) part of the monster hp display
        temp_width = base_mon_hp_width[i] * int(monster_list[i].hp) / int(monster_list[i].maxhp)
        temp_width = max(temp_width, 0)
        widgets.bordered_box(screen, (base_mon_hp_start[i], base_mon_hp_y_start[i]), (temp_width, 5), inner_color="hp_green")

        widgets.print_string(
            screen,
            str(monster_list[i].hp) + "/" + str(monster_list[i].maxhp),
            g.font,
            (xstart, base_mon_hp_y_start[i] + 6),
            align=1,
        )

    # refresh the player
    screen.blit(hero_pic, hero_loc)
    # 	if monster_slashes[-1][0] == 1:
    # 			screen.blit(config.BUTTONS["slash_attack.png"], (hero_loc[0]+4,hero_loc[1]+4))
    # Under (red) part of the player hp display
    widgets.bordered_box(screen,
        (
            monster_start[0] + (background_pic.get_width() - base_mon_hp_width[0]) / 2,
            monster_start[1] + background_pic.get_height() - hero_pic.get_height() * 3 / 2 - 2,
        ),
        (base_mon_hp_width[0], 5),
        inner_color="hp_red",
    )

    # Over (green) part of the player hp display
    temp_width = base_mon_hp_width[0] * int(player.hp) / int(player.adj_maxhp)
    temp_width = max(temp_width, 0)
    widgets.bordered_box(screen,
        (
            monster_start[0] + (background_pic.get_width() - base_mon_hp_width[0]) / 2,
            monster_start[1] + background_pic.get_height() - hero_pic.get_height() * 3 / 2 - 2,
        ),
        (temp_width, 5),
        inner_color="hp_green",
    )

    widgets.print_string(
        screen,
        str(player.hp) + "/" + str(player.adj_maxhp),
        g.font,
        (
            monster_start[0] + background_pic.get_width() / 2,
            monster_start[1] + background_pic.get_height() - hero_pic.get_height() * 3 / 2 + 4,
        ),
        align=1,
    )

    # refresh the player ep bar
    # Under (red) part of the player ep display
    widgets.bordered_box(screen,
        (
            monster_start[0] + (background_pic.get_width() - base_mon_hp_width[0]) / 2,
            monster_start[1] + background_pic.get_height() - hero_pic.get_height(),
        ),
        (base_mon_hp_width[0], 5),
        inner_color="hp_red",
    )
    # Over (green) part of the player ep display
    temp_width = base_mon_hp_width[0] * int(player.ep) / int(player.adj_maxep)
    temp_width = max(temp_width, 0)
    widgets.bordered_box(screen,
        (
            monster_start[0] + (background_pic.get_width() - base_mon_hp_width[0]) / 2,
            monster_start[1] + background_pic.get_height() - hero_pic.get_height(),
        ),
        (temp_width, 5),
        inner_color="ep_blue",
    )

    widgets.print_string(
        screen,
        str(player.ep) + "/" + str(player.adj_maxep),
        g.font,
        (
            monster_start[0] + background_pic.get_width() / 2,
            monster_start[1] + background_pic.get_height() - hero_pic.get_height() + 7,
        ),
        align=1,
    )

    # slashes
    tmp_surface = pygame.Surface((32, 64))
    for i in range(len(monster_list)):
        if monster_slashes[i][0] == 1:
            monster_slashes[i][0] = 0
            ystart = y_start(i)
            tmp_surface.blit(screen, (0, 0), (base_mon_hp_start[i], ystart - 32, 32, 64))
            for j in range(13):
                screen.blit(tmp_surface, (base_mon_hp_start[i], ystart - 32))
                screen.blit(config.BUTTONS["slash_attack.png"], (base_mon_hp_start[i] + j, ystart + j))
                pygame.display.flip()
            screen.blit(tmp_surface, (base_mon_hp_start[i], ystart - 32))
            pygame.display.flip()
    if monster_slashes[-1][0] == 1:
        monster_slashes[-1][0] = 0
        tmp_surface.blit(screen, (0, 0), (hero_loc[0], hero_loc[1] - 32, 32, 64))
        for j in range(13):
            screen.blit(tmp_surface, (hero_loc[0], hero_loc[1] - 32))
            screen.blit(config.BUTTONS["slash_attack.png"], (hero_loc[0] + j, hero_loc[1] + j))
            pygame.display.flip()
        screen.blit(tmp_surface, (hero_loc[0], hero_loc[1] - 32))
        pygame.display.flip()

    # Draw the monster selection arrow if needed.
    # 	main.canvas_map.delete("monster_arrow")
    global active_button
    if active_button != -1:
        screen.blit(
            config.BUTTONS["sword_pointer.png"], (base_mon_hp_start[active_button], base_mon_hp_y_start[active_button] - 20)
        )
    # 		main.canvas_map.create_image(
    # 			base_mon_hp_start[active_button],
    # 			base_mon_hp_y_start[active_button]-20,
    # 			anchor=N, image=config.BUTTONS["sword_pointer.png"],
    # 			tags=("monster_arrow", "battle"))
    main.refresh_bars()


# attack button was pressed
def attack(event=0):
    global active_button
    if can_leave() == 1:
        return 0
    if active_button == -1:
        last_mon_num = select_monster()
    else:
        last_mon_num = active_button
    if last_mon_num == -1:
        return 0
    config.mut["CURR_BUTTON"] = 0
    clear_slashes()

    # Both hp's *should* be over 0. Just a precaution.
    if monster_list[last_mon_num].hp > 0 and player.hp > 0:
        attack_monster(last_mon_num, player.adj_attack)
    global used_gem
    global num_dice
    if used_gem == 1:
        player.adj_attack = old_attack
        main.refresh_bars()
        num_dice = 1
        used_gem = 0
    attack_player()
    if can_leave() == 0:
        active_button = -1
        monster_mouse_move((0, 0))
        refresh()
        refresh_buttons()


# Returns the array location in monster_list of the monster the player wants to
# attack, or -1 on cancel. If more than one monster exists, displays a selection
# arrow.
def select_monster():
    # find out if we need to make the player select a monster.
    num_of_monsters = 0
    last_mon_num = 0
    for i in range(len(monster_list)):
        if monster_list[i].hp > 0:
            num_of_monsters += 1
            last_mon_num = i

    # If there is only one living monster, last_mon_num holds the array location
    # in monster_list[]. Otherwise, ask the player which monster to attack.
    if num_of_monsters == 1:
        return last_mon_num
    action.has_dialog = 1
    global active_button
    for i in range(len(monster_list)):
        if monster_list[i].hp > 0:
            active_button = i
            break
    else:
        ic("BUG: select_monster called when all monsters were dead")
        return -1

    global return_from_dialog
    return_from_dialog = 0

    # bindings
    bind_attack_keys()

    refresh()
    pygame.display.flip()
    # wait. Continue after activate_yesno() is run.
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.ALLOW_MOVE = True
                return -1
            if event.type == pygame.KEYDOWN:
                if event.key == config.BINDINGS["up"] or event.key == config.BINDINGS["left"]:
                    choose_monster_prev()
                    refresh()
                    pygame.display.flip()
                elif event.key == config.BINDINGS["down"] or event.key == config.BINDINGS["right"]:
                    choose_monster_next()
                    refresh()
                    pygame.display.flip()
                elif event.key == config.BINDINGS["action"] or config.BINDINGS["attack"]:
                    g.break_one_loop = 1
            elif event.type == pygame.MOUSEMOTION:
                monster_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                monster_mouse_move(event.pos)
                g.break_one_loop = 1

        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        if g.unclean_screen:
            pygame.display.flip()

    # cleanup
    if return_from_dialog == 2:
        return -1
    bind_keys()

    action.has_dialog = 0
    refresh()
    return active_button


def choose_monster_prev() -> None:
    """Cycle through the previous monsters when attacking. Used by the keyboard."""
    global active_button
    i = active_button
    while True:
        i -= 1
        if i == -1:
            i = len(monster_list) - 1
        if monster_list[i].hp > 0:
            active_button = i
            break
        if i == active_button:
            ic("choose_monster_prev couldn't find a monster.")
            active_button = -1
            return
    # help_text.set("Attack the " + monster_list[active_button].name)
    set_description_text(active_button)
    refresh()


def choose_monster_next() -> None:
    """Cycle through the next monsters when attacking. Used by the keyboard."""
    global active_button
    i = active_button
    while True:
        i += 1
        if i == len(monster_list):
            i = 0
        if monster_list[i].hp > 0:
            active_button = i
            break
        if i == active_button:
            ic("choose_monster_next couldn't find a monster.")
            active_button = -1
            return
    # help_text.set("Attack the " + monster_list[active_button].name)
    set_description_text(active_button)
    refresh()


# called on Return when the yesno dialog box is active.
def choose_monster(event=None):
    global return_from_dialog
    return_from_dialog.set("1")


# Cancels the monster selection. Called on Esc.
def cancel_monster(event=None):
    global active_button
    active_button = -1
    global return_from_dialog
    return_from_dialog.set("1")


# Called whenever the mouse moves in the monster canvas. Used to select the
# proper monster, given the x and y location of the mouse.
def monster_mouse_move(xy):
    try:
        global active_button
        for i in range(len(monster_list)):
            if monster_list[i].hp > 0:
                if (
                    xy[0] >= base_mon_hp_start[i]
                    and xy[0] <= base_mon_hp_start[i] + base_mon_hp_width[i]
                    and xy[1] >= base_mon_hp_y_start[i] - base_mon_hp_height[i]
                    and xy[1] <= base_mon_hp_y_start[i]
                ):
                    active_button = i
                    # help_text.set("Attack the " + monster_list[i].name)
                    set_description_text(i)
                    refresh()
    except AttributeError:
        active_button = -1


# attack the i'th monster in monster_list[], with an attack of power attack_power.
def attack_monster(i, attack_power):
    if i == -1:
        return None
    # find the damage done
    global num_dice
    damage = utils.die_roll(num_dice, attack_power + 2)
    damage = damage - utils.die_roll(1, monster_list[i].defense + 2)
    if damage > 0:
        if monster_hurt(i, damage) == 1:
            return 0
    else:
        main.print_message("You miss the " + monster_list[i].name + ".")


# Make all monsters attack the player.
def attack_player():
    for i in range(len(monster_list)):
        if monster_list[i].hp > 0 and player.hp > 0:
            attack_player_per_monster(i)


# Make the i'th monster attack you
def attack_player_per_monster(i):
    damage = utils.die_roll(1, monster_list[i].attack + 2)
    damage = damage - utils.die_roll(1, player.adj_defense + 2)
    if damage > 0:
        main.print_message("The " + monster_list[i].name + " hits you for " + str(damage) + " damage.")
        player.take_damage(-1 * damage)
        monster_slashed("h", damage)
        # you dead yet?
        if player.hp <= 0:
            player.hp = 0
            main.print_message("The " + monster_list[i].name + " kills you.")
            config.mut["CURR_BUTTON"] = 1
            refresh()
            refresh_buttons()

    elif monster_list[i].hp > 0:
        main.print_message("The " + monster_list[i].name + " misses you.")


# places a slash mark over the i'th monster, to indicate a hit, or "h" for the
# hero.
def monster_slashed(i, damage):
    global monster_slashes
    if str(i) == "h":
        monster_slashes[-1] = [1, 0, damage]
    else:
        monster_slashes[i] = [1, 0, damage]


# clears slashmarks for all monsters, and the hero.
def clear_slashes():
    global monster_slashes
    for i in range(len(monster_slashes)):
        monster_slashes[i] = [0, 0, 0]


# Hurts monster i for damage points. Kills it if the damage is great enough.
def monster_hurt(i, damage):
    monster_list[i].hp = monster_list[i].hp - damage
    if damage > 0:
        monster_slashed(i, damage)
        main.print_message("The " + monster_list[i].name + " is hit for " + str(damage) + " damage")
    # you kill it?
    if monster_list[i].hp <= 0:
        monster_dead(i)
        return 1
    return 0


# use to reward the player for killing a monster
def monster_dead(i):
    global active_button
    # make the display look better
    monster_list[i].hp = 0
    # add info to listbox_move; add gold and xp
    main.print_message("The " + monster_list[i].name + " dies.")

    if len(monster_list[i].on_death) == 0:
        gold = monster_list[i].gold
        player.give_gold(gold)
        main.print_message(f"You find {gold} gold,")

        exp = monster_list[i].exp
        main.print_message("and get " + str(exp) + " XP.")
        player.add_exp(exp)
    else:
        action.activate_lines(g.xgrid, g.ygrid, g.zgrid, monster_list[i].on_death)

    # finish up
    if can_leave() == 1:
        g.break_one_loop += 1
        # 		main.canvas_map.delete("battle")
        # 		back_to_main.set("2")
        g.cur_window = "main"
        global did_run
        did_run = 0
    else:
        for i in range(len(monster_list)):
            if monster_list[i].hp > 0:
                active_button = i
                break
        refresh()


def can_leave() -> bool:
    """
    Determine if the battle is over.

    Returns:
        bool: True if the battle is over, False otherwise.
        """
    if player.hp <= 0:
        return True
    return all(monster_list[i].hp <= 0 for i in range(len(monster_list)))


# run/leave/quit button was pressed
def runaway(force_success: bool = False) -> bool:
    """
    Attempt to run away from the battle.

    Args:
        force_success (bool): If True, the player will always succeed in running away.
    Returns:
        bool: True if the player successfully ran away, False otherwise.
    """
    global run_attempts
    global did_run
    clear_slashes()
    # leave/quit
    if can_leave():
        g.break_one_loop += 1
        return True
    # Attempt to run. Testers get better chance.
    if (
        (utils.die_roll(1, 10 + run_attempts) > 7)
        or (player.name == "testing123" and utils.die_roll(1, 10) > 5)
        or (force_success)
    ):
        main.print_message("You coward! You ran away from the " + monster.monster_groups[mon_index].name + ".")
        did_run = 1
        g.break_one_loop += 1
        return True

    run_attempts += 1
    main.print_message("You fail to run away.")
    attack_player()
    refresh()
    return False


def open_item_menu() -> None:
    """The use item button was pressed in the battle window. Open the item display."""
    # don't do anything if battle is over.
    if can_leave() == 1:
        return
    tmp_surface = pygame.Surface((300, 420))
    tmp_surface.blit(screen, (0, 0), (170, 0, 300, 420))
    inv.open_inner_menu("use")
    bind_item_keys()
    inv.inner_cur_button = 0
    # 	g.window_main.update_idletasks()
    inv.refresh_inv_display("use")
    inv.refresh_inner_buttons("use")
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                g.break_one_loop = 3
            elif event.type == pygame.KEYDOWN:
                if item_key_handler(event.key) == 2:
                    break
            elif event.type == pygame.MOUSEMOTION:
                item_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                item_mouse_click(event.pos)
        if g.unclean_screen:
            pygame.display.flip()
    screen.blit(tmp_surface, (170, 0))
    refresh()
    refresh_buttons()
    pygame.display.flip()
    bind_keys()


def open_skill_menu() -> None:
    """The use skill button was pressed in the battle window. Open the skill display."""
    # don't do anything if battle is over.
    if can_leave() == 1:
        return
    tmp_surface = pygame.Surface((300, 420))
    tmp_surface.blit(screen, (0, 0), (170, 0, 300, 420))
    inv.open_inner_menu("skill")
    bind_skill_keys()
    inv.inner_cur_button = 0
    # 	g.window_main.update_idletasks()
    refresh_skill_display("skill")
    inv.refresh_inner_buttons("skill")
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                g.break_one_loop = 3
            elif event.type == pygame.KEYDOWN:
                if skill_key_handler(event.key) == 2:
                    break
            elif event.type == pygame.MOUSEMOTION:
                skill_mouse_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                skill_mouse_click(event.pos)
        if g.unclean_screen:
            pygame.display.flip()
    screen.blit(tmp_surface, (170, 0))
    refresh()
    pygame.display.flip()
    bind_keys()


# This is a modification of inv.refresh_inv_display() in order to display
# the skill list.
def refresh_skill_display(screen_str):
    # 	main.canvas_map.delete("item")
    # Draw a selection box around the current item.
    x = inv.tmp_x_base
    y = inv.tmp_y_base
    tmp_item = inv.curr_item
    for i in range(len(g.item.inv)):
        widgets.bordered_box(screen,
            (
                x + (i % inv.inv_width) * config.TILESIZE + 2 * ((i % inv.inv_width) + 1),
                y + (i / inv.inv_width) * config.TILESIZE + 2 * ((i / inv.inv_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dh_green",
        )
    if tmp_item != -1 and tmp_item < inv.inv_width * inv.inv_height:
        widgets.bordered_box(screen,
            (
                x + (inv.curr_item % inv.inv_width) * config.TILESIZE + 2 * ((inv.curr_item % inv.inv_width) + 1),
                y + (inv.curr_item / inv.inv_width) * config.TILESIZE + 2 * ((inv.curr_item / inv.inv_width) + 1),
            ),
            (config.TILESIZE, config.TILESIZE),
            inner_color="dark_green",
        )

    # draw the skill pictures.
    for i in range(len(player.skill)):
        if player.skill[i][5] != 0 and (player.skill[i][1] <= 4 or player.skill[i][1] == 6):
            inv.draw_item(player.skill[i][7], i % inv.inv_width, i / inv.inv_width, x, y)

    # draw the help text
    widgets.bordered_box(screen, (inv.tmp_menu_x_base, inv.tmp_menu_y_base + inv.tmp_menu_height), (inv.tmp_menu_width, 17))
    if len(player.skill) <= tmp_item or tmp_item == -1 or player.skill[tmp_item][5] == 0 or player.skill[tmp_item][1] == 5:
        helptext = ""
    else:
        helptext = player.skill[tmp_item][0] + " (" + str(player.skill[tmp_item][2]) + " EP)"
    widgets.print_string(screen, helptext, g.font, (inv.tmp_menu_x_base + 2, inv.tmp_menu_y_base + inv.tmp_menu_height + 1))
    pygame.display.flip()


# Use a given item. item_index is the location in the item.item[] array.
# If leave_item==1, the item will not be removed from the inventory.
def useitem(item_index, leave_item=0):
    global active_button
    # don't do anything if battle is over.
    if can_leave() == 1 or item_index == -1:
        return 0
    clear_slashes()
    item_value = item_index
    item_type = g.item.item[item_value].type

    # if item is healing
    if item_type == 11:
        # heal the player, delete the item
        player.take_damage(g.item.item[item_value].quality)
        main.print_message("You are healed for " + str(g.item.item[item_value].quality) + " HP.")
        if leave_item == 0:
            g.item.drop_inv_item(g.item.find_inv_item(item_value))
            attack_player()

    # if item is a gem
    if item_type == 14:
        global old_attack
        old_attack = player.adj_attack
        gem_power = g.item.item[item_value].quality
        # gem power increases attack strength potential
        player.buff_attack("adj_attack", gem_power * 0.75)
        # gem power increases num_dice (ie. chance to hit and total damage)
        global num_dice
        num_dice = num_dice + gem_power / 4
        main.print_message("The " + g.item.item[item_value].name + " focuses the power of your attack.")
        main.refresh_bars()
        if leave_item == 0:
            g.item.drop_inv_item(g.item.find_inv_item(item_value))
        global used_gem
        used_gem = 1
        if leave_item == 0:
            attack()

    # if item is explosive
    if item_type == 12:
        sel_mon = select_monster()
        if sel_mon == -1:
            return 0
        # if monster is still alive
        if monster_list[sel_mon].hp > 0:
            damage = int(g.item.item[item_value].quality)
            if leave_item == 0:
                g.item.drop_inv_item(g.item.find_inv_item(item_value))
            monster_hurt(sel_mon, damage)
            if can_leave() == 0 and leave_item == 0:
                attack_player()
        active_button = -1

    # If item is scripted:
    if item_type == 15 or item_type == 17:
        # If the scripting ends with an "end" command,
        if action.activate_lines(g.xgrid, g.ygrid, g.zgrid, g.item.item[item_value].scripting) == 1:
            if leave_item == 0:
                g.item.drop_inv_item(g.item.find_inv_item(item_value))
        if can_leave() == 0 and leave_item == 0:
            attack_player()
        active_button = -1

    # If item is equippable:
    if item_type < 6:
        # trade the item and whatever's in the equip slot
        temp = player.equip[item_type]
        player.equip[item_type] = item_index
        g.item.drop_inv_item(g.item.find_inv_item(item_index))
        g.item.take_inv_item(temp)
        main.print_message("You equip yourself with your " + g.item.item[player.equip[item_type]].name + ".")
        player.reset_stats()
        if can_leave() == 0 and leave_item == 0:
            attack_player()

    if can_leave() == 1:
        g.break_one_loop += 1
        return 0
    refresh()

    # back to battle
    if leave_item == 0:
        g.break_one_loop += 1
        refresh_buttons()


# Use a skill. Called upon hitting the right button; uses skill_index.
# (skill_index is position in player.skill[])
def useskill(skill_index, free_skill=0):
    global active_button
    # don't do anything if monster is dead.
    if can_leave() == 1:
        return 0

    clear_slashes()

    # sanity checks
    if skill_index >= len(player.skill):
        return 0

    if free_skill == 0:
        if player.skill[skill_index][5] == 0:
            return 0
        if player.skill[skill_index][2] > player.ep:
            return 0
        if player.skill[skill_index][1] == 5:
            return 0

    # actually use the skill.
    if player.skill[skill_index][1] == 0:  # rage
        if free_skill == 0:
            # pay for the skill
            player.use_ep(-1 * player.skill[skill_index][2])
        main.print_message("You fly into a rage.")
        # increase attack ability
        player.buff_attack("adj_attack", (1 + int(player.level) / 4))
        main.refresh_bars()
        main.refresh_inv_icon()
        attack_player()

    elif player.skill[skill_index][1] == 1:  # Sneak away
        if free_skill == 0:
            # pay for the skill
            player.use_ep(-1 * player.skill[skill_index][2])
        global run_attempts
        if utils.die_roll(1, 10 + int(player.level) + run_attempts) > 4:
            runaway(True)
            global did_run
            did_run = 1
        else:
            run_attempts += 3
            main.print_message("You fail to sneak away.")
            attack_player()
    elif player.skill[skill_index][1] == 2:  # Frenzy
        if free_skill == 0:
            # pay for the skill
            player.use_ep(-1 * player.skill[skill_index][2])
        mon_num = select_monster()
        for i in range(2 + int(player.level) / 4):
            if monster_list[mon_num].hp < 1:
                mon_num = select_monster()
            if mon_num == -1:
                return 0
            attack_monster(mon_num, player.adj_attack)
            if can_leave() == 1:
                break
            active_button = -1
            monster_mouse_move((0, 0))
            refresh()
        if can_leave() == 0:
            attack_player()
    elif player.skill[skill_index][1] == 3:  # Dismember
        if free_skill == 0:
            # pay for the skill
            player.use_ep(-1 * player.skill[skill_index][2])
        mon_num = select_monster()
        if mon_num == -1:
            return 0
        damage = player.adj_attack
        monster_hurt(mon_num, damage)
        if can_leave() == 0:
            attack_player()
    elif player.skill[skill_index][1] == 4 or player.skill[skill_index][1] == 6:  # Scripted
        # If the scripting ends with an "end" command,
        if action.activate_lines(g.xgrid, g.ygrid, g.zgrid, player.skill[skill_index][6]) == 1:
            if free_skill == 0:
                # pay for the skill
                player.use_ep(-1 * player.skill[skill_index][2])
        if can_leave() == 0:
            attack_player()
        main.refresh_bars()

    if can_leave() == 1:
        g.break_one_loop += 1
        return 0
    active_button = -1
    monster_mouse_move((0, 0))
    refresh()

    # replace the cursor
    if free_skill == 0:
        g.break_one_loop += 1
        refresh_buttons()


def inspect_monst() -> None:
    """The inspect button was pressed in the battle window."""
    if can_leave() == 1:
        return

    tmp = select_monster()
    if tmp == -1:
        return

    display_text = f"{monster_list[tmp].name} \n "
    display_text += f"Attack: {monster_list[tmp].attack}           "
    display_text += f"Defense: {monster_list[tmp].defense} \n "
    display_text += monster_list[tmp].description

    tmp_surface = pygame.Surface((300, 500))
    tmp_surface.blit(screen, (0, 0), (170, 0, 300, 500))
    main.show_dialog(display_text)
    screen.blit(tmp_surface, (170, 0))
    pygame.display.flip()


def refresh_buttons() -> None:
    """Refresh the buttons in the main battle view."""
    attack_name = "attack.png"
    use_name = "use.png"
    skill_name = "skill.png"
    inspect_name = "inspect.png"
    quit_name = "quit.png"
    if config.mut["CURR_BUTTON"] == 0:
        attack_name = "attack_sel.png"
    elif config.mut["CURR_BUTTON"] == 1:
        use_name = "use_sel.png"
    elif config.mut["CURR_BUTTON"] == 2:
        skill_name = "skill_sel.png"
    elif config.mut["CURR_BUTTON"] == 3:
        inspect_name = "inspect_sel.png"
    elif config.mut["CURR_BUTTON"] == 4:
        quit_name = "quit_sel.png"

    screen.blit(config.BUTTONS[attack_name], (attack_button_loc, button_y_start))
    screen.blit(config.BUTTONS[use_name], (item_button_loc, button_y_start))
    screen.blit(config.BUTTONS[skill_name], (skill_button_loc, button_y_start))
    screen.blit(config.BUTTONS[inspect_name], (inspect_button_loc, button_y_start))
    screen.blit(config.BUTTONS[quit_name], (run_button_loc, button_y_start))

    pygame.display.flip()


def key_handler(key_name: int) -> str | int:
    """
    All keypresses in new_game pass through here

    Based on the key name, give the right action. ("etc", "left", "right", "up", "down", "return")
    """
    if key_name == config.BINDINGS["cancel"]:
        return runaway()
    if key_name == config.BINDINGS["right"] or key_name == config.BINDINGS["down"]:
        config.mut["CURR_BUTTON"] += 1
        if config.mut["CURR_BUTTON"] >= 5:
            config.mut["CURR_BUTTON"] = 0
    elif key_name == config.BINDINGS["left"] or key_name == config.BINDINGS["up"]:
        config.mut["CURR_BUTTON"] -= 1
        if config.mut["CURR_BUTTON"] <= -1:
            config.mut["CURR_BUTTON"] = 4  # loop around

    elif key_name == config.BINDINGS["action"]:
        if config.mut["CURR_BUTTON"] == 0:
            attack()
        elif config.mut["CURR_BUTTON"] == 1:
            open_item_menu()
        elif config.mut["CURR_BUTTON"] == 2:
            open_skill_menu()
        elif config.mut["CURR_BUTTON"] == 3:
            inspect_monst()
        elif config.mut["CURR_BUTTON"] == 4:
            return runaway()
        return 0
    elif key_name == config.BINDINGS["attack"]:
        attack()
    refresh_buttons()


def item_key_handler(key_name):
    tmp = inv.inner_key_handler(key_name)
    if tmp == 2:
        useitem(g.item.inv[inv.curr_item])
        return 2
    if tmp == 0:
        inv.refresh_inv_display("use")
    if tmp == 1:
        g.break_one_loop += 1


def skill_key_handler(key_name):
    tmp = inv.inner_key_handler(key_name)
    if tmp == 2:
        useskill(inv.curr_item)
        return 2
    if tmp == 0:
        refresh_skill_display("skill")
    if tmp == 1:
        g.break_one_loop += 1


def item_mouse_click(xy):
    tmp = inv.inner_mouse_click(xy, "use")
    if tmp == 2:
        useitem(g.item.inv[inv.curr_item])
    if tmp == 0:
        inv.refresh_inv_display("use")
    if tmp == 1:
        g.break_one_loop = 1


def skill_mouse_click(xy):
    tmp = inv.inner_mouse_click(xy, "skill")
    if tmp == 2:
        useskill(inv.curr_item)
    if tmp == 0:
        refresh_skill_display("skill")
    if tmp == 1:
        g.break_one_loop = 1


def item_mouse_dbl_click(xy):
    if inv.inner_mouse_dbl_click(xy):
        useitem(g.item.inv[inv.curr_item])
    inv.refresh_inv_display("use")


def skill_mouse_dbl_click(xy):
    if inv.inner_mouse_dbl_click(xy):
        useskill(g.item.inv[inv.curr_item])
    refresh_skill_display("skill")


def item_mouse_move(xy):
    if inv.inner_mouse_move(xy, "use"):
        inv.refresh_inner_buttons("use")


def skill_mouse_move(xy):
    if inv.inner_mouse_move(xy, "skill"):
        inv.refresh_inner_buttons("skill")


# def mouse_handler_click(xy):
# 	mouse_handler_move(xy)
# 	key_handler("return")


def mouse_handler_move(xy):
    tmp_button = config.mut["CURR_BUTTON"]
    if xy[0] < attack_button_loc or xy[1] < button_y_start or xy[1] > button_y_start + button_height:
        config.mut["CURR_BUTTON"] = -1
    elif xy[0] < item_button_loc:
        config.mut["CURR_BUTTON"] = 0
    elif xy[0] < skill_button_loc:
        config.mut["CURR_BUTTON"] = 1
    elif xy[0] < inspect_button_loc:
        config.mut["CURR_BUTTON"] = 2
    elif xy[0] < run_button_loc:
        config.mut["CURR_BUTTON"] = 3
    elif xy[0] < final_button_loc:
        config.mut["CURR_BUTTON"] = 4
    else:
        config.mut["CURR_BUTTON"] = -1
    if tmp_button != config.mut["CURR_BUTTON"]:
        refresh_buttons()


# ! BUG apparently?
def set_description_text(i: int) -> None:
    """Sets the description to the left of the battle view to that of the i'th monster"""
    pass
    # canvas_desc.delete(ALL)
    # canvas_desc.create_text(1, 5, anchor=NW, text=monster_list[i].description, width=195)


def begin(mon_index_input: int) -> str | int:
    """Initiate a battle"""
    # 	global window_battle
    bgcolour = "lightgrey"
    # 	window_battle = Frame(g.window_main, bd=4, relief=GROOVE, bg=bgcolour)
    # 	window_battle.grid(row=0, column=0)
    global mon_index
    mon_index = mon_index_input
    global monster_list
    monster_list = []
    for line in monster.monster_groups[mon_index].monster_list:
        monster_list.append(monster.copy_monster(monster.monsters[monster.monster_name_to_index(line)]))
    for i in range(len(monster_list)):
        monster_list[i].reset()
        if g.difficulty == 0:
            monster_list[i].hp -= monster_list[i].hp / 5
            monster_list[i].maxhp -= monster_list[i].maxhp / 5
            monster_list[i].attack -= monster_list[i].attack / 5
            monster_list[i].defense -= monster_list[i].defense / 5
        if g.difficulty == 2:
            monster_list[i].hp += monster_list[i].hp / 5
            monster_list[i].maxhp += monster_list[i].maxhp / 5
            monster_list[i].attack += monster_list[i].attack / 5
            monster_list[i].defense += monster_list[i].defense / 5

    global did_run
    did_run = 0
    global run_attempts
    run_attempts = 0
    global active_button
    active_button = -1

    # Set the current window
    g.cur_window = "battle"

    global canvas_mon_pic
    global background_pic
    background_pic = config.MAPS[g.zgrid].battle_background

    global monster_pic
    monster_pic = []
    global base_mon_hp_start
    base_mon_hp_start = []
    global base_mon_hp_width
    base_mon_hp_width = []
    global base_mon_hp_y_start
    base_mon_hp_y_start = []
    global monster_slashes
    monster_slashes = []

    global monster_start
    monster_start = (
        config.TILESIZE * main.half_mapx - background_pic.get_width() / 2,
        config.TILESIZE * main.half_mapy - background_pic.get_height() / 2,
    )
    for i in range(len(monster_list)):
        monster_slashes.append([0, 0, 0])
        try:
            monster_pic.append(config.TILES["monsters/" + monster_list[i].name + ".png"])
        except KeyError:
            monster_pic.append(config.TILES["monsters/generic.png"])

        # if x and y positions were given, use them; otherwise, start at the
        # middle, and go right. This works for 1 or two monsters, but xy
        # coords are recommended for more.
        if len(monster.monster_groups[mon_index].x_pos) > i:
            xstart = monster_start[0] + monster.monster_groups[mon_index].x_pos[i]
        else:
            xstart = monster_start[0] + background_pic.get_width() / 2 + i * 40
        ystart = y_start(i)

        base_mon_hp_start.append(xstart - monster_pic[i].get_width() / 2)
        base_mon_hp_width.append(monster_pic[i].get_width())
        base_mon_hp_height.append(monster_pic[i].get_height())
        base_mon_hp_y_start.append(ystart + 5 + monster_pic[i].get_height())

    monster_slashes.append([0, 0, 0])

    global hero_pic
    try:
        hero_pic = config.TILES["people/hero_n" + config.MAPS[g.zgrid].hero_suffix + ".png"]
    except KeyError:
        hero_pic = config.TILES["blank"]

    global hero_loc
    hero_loc = (
        monster_start[0] + (background_pic.get_width() - base_mon_hp_width[0]) / 2,
        background_pic.get_height() - hero_pic.get_height() * 5 / 2 + monster_start[1],
    )

    global attack_button_loc
    global item_button_loc
    global skill_button_loc
    global inspect_button_loc
    global run_button_loc
    global final_button_loc
    global button_y_start
    global button_height
    attack_button_loc = (
        config.TILESIZE * main.half_mapx
        - config.BUTTONS["attack.png"].get_width()
        - config.BUTTONS["use.png"].get_width()
        - config.BUTTONS["skill.png"].get_width() / 2
    )
    item_button_loc = attack_button_loc + config.BUTTONS["attack.png"].get_width()
    skill_button_loc = item_button_loc + config.BUTTONS["use.png"].get_width()
    inspect_button_loc = skill_button_loc + config.BUTTONS["skill.png"].get_width()
    run_button_loc = inspect_button_loc + config.BUTTONS["inspect.png"].get_width()
    final_button_loc = run_button_loc + config.BUTTONS["quit.png"].get_width()

    button_y_start = config.TILESIZE * main.half_mapy + background_pic.get_height() / 2
    button_height = config.BUTTONS["attack.png"].get_height()

    widgets.bordered_box(screen, (attack_button_loc, button_y_start), (final_button_loc - attack_button_loc, button_height))

    # bindings
    bind_keys()

    main.print_message(monster.monster_groups[mon_index].attack_message)
    set_description_text(0)

    refresh()
    refresh_buttons()

    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                g.break_one_loop = 2
            elif event.type == pygame.KEYDOWN:
                if key_handler(event.key) == 1:
                    break
            elif event.type == pygame.MOUSEMOTION:
                if event.pos[1] > button_y_start and event.pos[1] < button_height + button_y_start:
                    mouse_handler_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_handler_move(event.pos)
                if key_handler(pygame.K_RETURN) == 1:
                    break
        if g.unclean_screen:
            pygame.display.flip()

    if player.hp <= 0:
        did_run = "end"
    return did_run


# bind the keys. Called upon window creation and return from a yes/no box
def bind_keys():
    g.cur_window = "battle"


# keybindings when choosing a monster to attack.
def bind_attack_keys():
    g.cur_window = "battle_attack"


def bind_item_keys():
    g.cur_window = "battle_item"


def bind_skill_keys():
    g.cur_window = "battle_skill"
