#inv.py
#Copyright (C) 2005 Free Software Foundation
#This file is part of Dragon Hunt.

#Dragon Hunt is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Dragon Hunt is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Dragon Hunt; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file controls the inventory screen.
#from Tkinter import *
#needed for the buttons.
#import ImageTk
#import Image
import pygame

#import tkMessageBox
import g
import main
import action
import re
import item

from player import *

#width/height of inv canvas, in tiles.
# (g.tilesize + the 3 pixel border)
inv_width = 4
inv_height = 7

#width/height of the equipment canvas, in tiles.
equip_size = 3

#Currently selected item number. If this is higher than the inventory can hold,
#it represents a position within the equipment display.
curr_item = 0


global active_button
active_button = 0

#currently selected button. 0=Use, 1=Drop, 2=Wear, 3=Skill, 4=Save, 5=Leave
cur_button = 0

#Like cur_button, but for the inner menus.
inner_cur_button = 0

#distance from the top of the inv box each button should be placed.
#Values are added in init_window.
# use_height = 0
# remove_height = 0
# save_height = 0
# leave_height = 0
# total_height = 0
#
equip_height = 0
drop_height = 0
skill_height = 0
save_height = 0
leave_height = 0
total_height = 0

button_width = 0


#xy coords of the upper-left hand corner of the inv area.
base_x = 0
base_y = 0

#xy coords for the inner menus.
tmp_x_base = 0
tmp_y_base = 0

#xy coords for the inner menu buttons.
tmp_menu_x_base = 0
tmp_menu_y_base = 0
#And height.
tmp_menu_width = 0
tmp_menu_height = 0

inv_canvas_width = 0
inv_canvas_height = 0

#Change to return to the main game
#back_to_main = StringVar()
#back_to_inv = StringVar()

#when given a number from 0-8 (as returned by curr_item-inv_height*inv_width)
#return the proper location in the player.equip array. Corrects for the empty
#spaces in the display.
def convert_equip_loc_to_index(loc):
	if loc == 0: return -1
	if loc == 1: return 3
	if loc == 2: return 4

	if loc == 3: return 0
	if loc == 4: return 1
	if loc == 5: return 2

	if loc == 6: return -1
	if loc == 7: return 5
	if loc == 8: return -1


#Called when "Use" is pressed on the inv menu
def open_use_item():
	open_inner_menu("use")
	g.cur_window = "inventory_use"
	refresh_use()
	refresh_use_buttons()
#	g.window_main.wait_variable(back_to_inv)
# 	if main.canvas_map.winfo_exists():
# 		main.canvas_map.delete("use")
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				if use_key_handler(event.key) == 1:
					return
			elif event.type == pygame.MOUSEMOTION:
				use_mouse_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if use_mouse_click(event.pos) == 1:
					return
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if use_key_handler(tmpjoy) == 1:
					return
	menu_bind_keys()
	menu_bind_keys()

#Called when "Drop" is pressed on the inv menu
def open_drop_item():
	open_inner_menu("drop")
	g.cur_window = "inventory_drop"
	refresh_drop()
	refresh_drop_buttons()
# 	g.window_main.wait_variable(back_to_inv)
# 	if main.canvas_map.winfo_exists():
# 		main.canvas_map.delete("drop")
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				if drop_key_handler(event.key) == 1:
					return
			elif event.type == pygame.MOUSEMOTION:
				drop_mouse_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if drop_mouse_click(event.pos) == 1:
					return
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if drop_key_handler(tmpjoy) == 1:
				return
	menu_bind_keys()

def open_equip_item():
	global curr_item
	open_inner_menu("equip")

	#Equip also needs the equip screen:
	temp_canvas_width=(g.tilesize*equip_size)+ 8
	g.create_norm_box((tmp_x_base-temp_canvas_width,
				tmp_y_base), (temp_canvas_width, temp_canvas_width))

	g.cur_window = "inventory_equip"
	refresh_equip()
	refresh_equip_buttons()
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				if equip_key_handler(event.key) == 1:
					if curr_item >= inv_width * inv_height:
						curr_item = 0
					return
			elif event.type == pygame.MOUSEMOTION:
				equip_mouse_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if equip_mouse_click(event.pos) == 1:
					if curr_item >= inv_width * inv_height:
						curr_item = 0
					return
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if equip_key_handler(tmpjoy) == 1:
				if curr_item >= inv_width * inv_height:
					curr_item = 0
				return
	menu_bind_keys()

def open_skill_menu():
	open_inner_menu("skill")
	g.cur_window = "inventory_skill"
	refresh_skill("skill")
	refresh_skill_buttons()
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				tmp = skill_key_handler(event.key)
				if tmp == 1:
					return
				elif tmp == "end":
					return "end"
			elif event.type == pygame.MOUSEMOTION:
				skill_mouse_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if skill_mouse_click(event.pos) == 1:
					return
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if skill_key_handler(tmpjoy) == 1:
				return
	menu_bind_keys()

#Generic function for creating a sub-menu for the inv.
def open_inner_menu(screen_str):
	global inner_cur_button; inner_cur_button = 0
	global tmp_x_base; global tmp_y_base
	global tmp_menu_x_base; global tmp_menu_y_base
	global tmp_menu_width; global tmp_menu_height
	global inv_canvas_width; global inv_canvas_height
	if inv_canvas_width == 0:
		inv_canvas_width = (g.tilesize*inv_width)+ ((inv_width+1)*2) + 1
	if inv_canvas_height == 0:
		inv_canvas_height = (g.tilesize*inv_height)+ ((inv_height+1)*2) + 1

	tmp_x_base = (g.tilesize*main.mapsizex)/2-inv_canvas_width
	tmp_y_base = (g.tilesize*main.mapsizey - inv_canvas_height)/2
	tmp_menu_x_base = ((g.tilesize*main.mapsizex)/2-tmp_x_base)/2 + \
							tmp_x_base-g.buttons[screen_str+".png"].get_width()
	tmp_menu_y_base = (g.tilesize*main.mapsizey + inv_canvas_height)/2
	tmp_menu_width =g.buttons[screen_str+".png"].get_width()+g.buttons["leave.png"].get_width()
	tmp_menu_height =g.buttons["leave.png"].get_height()

	create_inv_display(screen_str)

	#button rectangle
	g.create_norm_box((tmp_menu_x_base, tmp_menu_y_base),
		(tmp_menu_width, tmp_menu_height))

#Create a generic inventory display.
def create_inv_display(screen_str):
	g.create_norm_box((tmp_x_base, tmp_y_base),
		((g.tilesize*main.mapsizex)/2-tmp_x_base, (g.tilesize*main.mapsizey +
		inv_canvas_height)/2+g.buttons["leave.png"].get_height()-tmp_y_base))

	#per-item borders
	for y in range(inv_height):
		for x in range(inv_width):
			g.create_norm_box((tmp_x_base+x*g.tilesize + 2 * (x+1),
				tmp_y_base+y*g.tilesize + 2 * (y+1)), (g.tilesize, g.tilesize),
				inner_color="dh_green")

def refresh_use_buttons(event=0): refresh_inner_buttons("use")
def refresh_drop_buttons(event=0): refresh_inner_buttons("drop")
def refresh_equip_buttons(event=0): refresh_inner_buttons("equip")
def refresh_skill_buttons(event=0): refresh_inner_buttons("skill")

#Refreshes the inner menu buttons.
def refresh_inner_buttons(screen_str):
	first_image = screen_str+".png"
	leave_image = "leave.png"
	if (inner_cur_button == 0): first_image = screen_str+"_sel.png"
	elif (inner_cur_button == 1): leave_image = "leave_sel.png"

	x_start = ((g.tilesize*main.mapsizex)/2-tmp_x_base)/2 + \
							tmp_x_base - g.buttons[screen_str+".png"].get_width()
	y_start = (g.tilesize*main.mapsizey + inv_canvas_height)/2

	g.screen.blit(g.buttons[first_image], (x_start, y_start))
	g.screen.blit(g.buttons[leave_image],
			(x_start+g.buttons[screen_str+".png"].get_width(), y_start))

	pygame.display.flip()

#Refreshes the item display in the inner menus.
def refresh_use(): refresh_inv_display("use")
def refresh_drop(): refresh_inv_display("drop")
def refresh_equip():
	refresh_inv_display("equip")
	#rebuild the equipment display
	temp_canvas_width=(g.tilesize*equip_size)+ 8
	tmpx = tmp_x_base-temp_canvas_width
	tmpy = tmp_y_base

	for i in range(9):
		g.create_norm_box((
			tmpx+(i%equip_size)*g.tilesize + 2 * ((i%equip_size)+1),
			tmpy+(i/equip_size)*g.tilesize + 2 * ((i/equip_size)+1)),
			(g.tilesize, g.tilesize), inner_color="dh_green")


	#Draw selection rectangle for equipment display
	if (curr_item != -1 and curr_item >= inv_width * inv_height):
		c_item = curr_item - inv_width * inv_height
		g.create_norm_box((
			tmpx+(c_item%equip_size)*g.tilesize + 2 * ((c_item%equip_size)+1),
			tmpy+(c_item/equip_size)*g.tilesize + 2 * ((c_item/equip_size)+1)),
			(g.tilesize, g.tilesize), inner_color="dark_green")

	#Weapon
	if player.equip[0] != -1: draw_item(item.item[player.equip[0]].picturename,
						0, 1, tmpx, tmpy, "equip")
	else: draw_item("items/weapon_eq.png", 0, 1, tmpx, tmpy, "equip")
	#Armor
	if player.equip[1] != -1: draw_item(item.item[player.equip[1]].picturename,
						1, 1, tmpx, tmpy, "equip")
	else: draw_item("items/armor_eq.png", 1, 1, tmpx, tmpy, "equip")
	#Shield
	if player.equip[2] != -1: draw_item(item.item[player.equip[2]].picturename,
						2, 1, tmpx, tmpy, "equip")
	else: draw_item("items/shield_eq.png", 2, 1, tmpx, tmpy, "equip")
	#Helmet
	if player.equip[3] != -1: draw_item(item.item[player.equip[3]].picturename,
						1, 0, tmpx, tmpy, "equip")
	else: draw_item("items/helmet_eq.png", 1, 0, tmpx, tmpy, "equip")
	#Gloves
	if player.equip[4] != -1: draw_item(item.item[player.equip[4]].picturename,
						2, 0, tmpx, tmpy, "equip")
	else: draw_item("items/gloves_eq.png", 2, 0, tmpx, tmpy, "equip")
	#Boots
	if player.equip[5] != -1: draw_item(item.item[player.equip[5]].picturename,
						1, 2, tmpx, tmpy, "equip")
	else: draw_item("items/boots_eq.png", 1, 2, tmpx, tmpy, "equip")

	main.refresh_bars()
	pygame.display.flip()

def refresh_inv_display(screen_str):
	#Draw a selection box around the current item.
	x = tmp_x_base
	y = tmp_y_base
	for i in range(len(item.inv)):
		g.create_norm_box((
			x+(i%inv_width)*g.tilesize + 2 * ((i%inv_width)+1),
			y+(i/inv_width)*g.tilesize + 2 * ((i/inv_width)+1)),
			(g.tilesize, g.tilesize), inner_color="dh_green")

	if (curr_item != -1 and curr_item < inv_width * inv_height):
		g.create_norm_box((
			x+(curr_item%inv_width)*g.tilesize + 2 * ((curr_item%inv_width)+1),
			y+(curr_item/inv_width)*g.tilesize + 2 * ((curr_item/inv_width)+1)),
			(g.tilesize, g.tilesize), inner_color="dark_green")

	#draw the item pictures.
	for i in range(len(item.inv)):
		if item.inv[i] != -1:
			draw_item(item.item[item.inv[i]].picturename,
						i%inv_width, i/inv_width, x, y, screen_str)

	#draw the help text
	if curr_item >= inv_width * inv_height: #equipment
 		tempitem=convert_equip_loc_to_index(curr_item-(inv_width * inv_height))
		if tempitem == -1: helptext = ""
 		elif player.equip[tempitem] == -1: helptext = ""
 		else: helptext = item.item[player.equip[tempitem]].name
	else: #Inv
		if curr_item == -1 or item.inv[curr_item] == -1: helptext = ""
		else: helptext = item.item[item.inv[curr_item]].name

	g.create_norm_box((tmp_menu_x_base,
		tmp_menu_y_base+tmp_menu_height), (tmp_menu_width, 17))

	g.print_string(g.screen, helptext, g.font, (tmp_menu_x_base+2,
		tmp_menu_y_base+tmp_menu_height+1))
	pygame.display.flip()

def refresh_skill(screen_str):
	#Draw a selection box around the current item.
	x = tmp_x_base
	y = tmp_y_base
	for i in range(len(item.inv)):
		g.create_norm_box((
			x+(i%inv_width)*g.tilesize + 2 * ((i%inv_width)+1),
			y+(i/inv_width)*g.tilesize + 2 * ((i/inv_width)+1)),
			(g.tilesize, g.tilesize), inner_color="dh_green")

	if (curr_item != -1 and curr_item < inv_width * inv_height):
		g.create_norm_box((
			x+(curr_item%inv_width)*g.tilesize + 2 * ((curr_item%inv_width)+1),
			y+(curr_item/inv_width)*g.tilesize + 2 * ((curr_item/inv_width)+1)),
			(g.tilesize, g.tilesize), inner_color="dark_green")

	#draw the skill pictures.
	for i in range(len(player.skill)):
		if player.skill[i][5] != 0 and (player.skill[i][1] == 5 or
				player.skill[i][1] == 6):
			draw_item(player.skill[i][7],
						i%inv_width, i/inv_width, x, y, screen_str)

	#draw the help text
	g.create_norm_box((tmp_menu_x_base,
		tmp_menu_y_base+tmp_menu_height), (tmp_menu_width, 17))
	if len(player.skill) <= curr_item: helptext = ""
	elif curr_item == -1 or player.skill[curr_item][5] == 0 or \
		player.skill[curr_item][1] <= 4: helptext = ""
	else: helptext = (player.skill[curr_item][0] + " ("+
			str(player.skill[curr_item][2]) + " EP)")
	g.print_string(g.screen, helptext, g.font, (tmp_menu_x_base+2,
		tmp_menu_y_base+tmp_menu_height+1))

	pygame.display.flip()


def leave_inner():
	g.break_one_loop += 1

#Refreshes the stat display to the right side of the inv.
def refresh_stat_display():

	start_x = (g.tilesize*main.mapsizex)/2
	start_y = (g.tilesize*main.mapsizey - total_height)/2
	#hp/ep bars
#	main.canvas_map.delete("stats")
	#Create the hp/ep background bars

	bar_height = 15
	bar_start = start_y+21


	g.create_norm_box((start_x+5, bar_start-1), (g.hpbar_width,
		bar_height), inner_color="hp_red")
	g.create_norm_box((start_x+5, bar_start+bar_height+1), (g.hpbar_width,
		bar_height), inner_color="hp_red")

	temp_width = g.hpbar_width*player.hp/player.adj_maxhp
	if temp_width < 0: temp_width=0

	bar_height = 15
	bar_start = start_y+21
	g.create_norm_box((start_x+5, bar_start-1), (temp_width,
		bar_height), inner_color="hp_green")
# 	main.canvas_map.create_rectangle(start_x+5, bar_start-1, start_x+temp_width+5,
# 		bar_start+bar_height-1, fill="#05BB05", tags=("stats", "inv"))
# 	main.canvas_map.delete("show_ep")
	temp_width = g.hpbar_width*player.ep/player.adj_maxep
	if temp_width < 0: temp_width=0
	g.create_norm_box((start_x+5, bar_start+bar_height+1), (temp_width,
		bar_height), inner_color="ep_blue")
# 	main.canvas_map.create_rectangle(start_x+5, bar_start+bar_height+1, start_x+temp_width+5,
# 		bar_start+bar_height*2+1, fill="#2525EE", tags=("stats", "inv"))
# 	main.canvas_map.lift("bar")

	tmp_width = 52
	g.screen.fill(g.colors["light_gray"], (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+5, 50, 14))
	g.print_string(g.screen, player.name, g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+5))
	g.print_string(g.screen, str(player.hp)+"/"+str(player.adj_maxhp),
		g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+22))
	g.print_string(g.screen, str(player.ep)+"/"+str(player.adj_maxep),
		g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+39))

	g.screen.fill(g.colors["light_gray"], (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+55, 50, 80))
	g.print_string(g.screen, str(player.adj_attack),
		g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+55))
	g.print_string(g.screen, str(player.adj_defense),
		g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+70))
	g.print_string(g.screen, str(player.gold),
		g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+85))
	g.print_string(g.screen, str(player.level),
		g.font, (start_x + tmp_width,
		(g.tilesize*main.mapsizey - total_height)/2+100))
	tmp = str(player.exp_till_level())
	if tmp == "9999":
		g.print_string(g.screen, str(player.exp)+"/----", g.font,
			(start_x + tmp_width, (g.tilesize*main.mapsizey -
			total_height)/2+115))
	else:
		g.print_string(g.screen, str(player.exp)+"/"+
			str(player.exp_till_level()+player.exp), g.font,
			(start_x + tmp_width, (g.tilesize*main.mapsizey -
			total_height)/2+115))

	main.refresh_bars()
	main.refresh_inv_icon()
	pygame.display.flip()

#called when "Save" is pressed
def inv_savegame():
	if action.has_dialog == 1: return 0
	g.savegame(player.name)
	main.print_message("** Game Saved **")
	pygame.display.flip()

#	help_text.set("Game Saved")

#called when "Leave" is pressed
def leave_inv():
	if action.has_dialog == 1: return 0
	#leave_inner()
	g.cur_window = "main"
	#main.canvas_map.delete("inv")
	#back_to_inv.set("1")
	#back_to_main.set("1")

#puts a worn item into the inventory. Called from the remove button.
def rm_equip():
	if action.has_dialog == 1: return 0
	#Curr_item is the current location in the equipment canvas.
	#The missing numbers in this sequence are the blank spots in the display.
	sel_equipment = -1
	c_item = curr_item - inv_width * inv_height
	if c_item == 1: sel_equipment = 3
	elif c_item == 2: sel_equipment = 4
	elif c_item == 3: sel_equipment = 0
	elif c_item == 4: sel_equipment = 1
	elif c_item == 5: sel_equipment = 2
	elif c_item == 7: sel_equipment = 5
	if sel_equipment == -1: return 0

	if player.equip[sel_equipment] != -1:
		if -1 != item.take_inv_item(player.equip[sel_equipment]):
			main.print_message("You take off your " +
				item.item[player.equip[sel_equipment]].name)
			player.equip[sel_equipment] = -1
	player.reset_stats()
	refresh_equip()
	refresh_stat_display()

#takes an item from the inventory, and wears it.
def wear_item():
	if action.has_dialog == 1: return 0
	if curr_item >= inv_width * inv_height:
		rm_equip()
		return 0

	try:
		item_value = item.inv[curr_item]
	except IndexError:
		return 0

	if item_value == -1: return
	#put the equip slot into item_loc
	item_loc = item.item[item_value].type

	#if item is equipment
	if item_loc < 6:
		#trade the item and whatever's in the equip slot
		temp = player.equip[item_loc]
		player.equip[item_loc] = item_value
		item.drop_inv_item(curr_item)
		item.take_inv_item(temp)
		main.print_message("You equip yourself with your " +
			item.item[player.equip[item_loc]].name + ".")
		player.reset_stats()
		if cur_button == 0:
			refresh_use()
		elif cur_button == 1:
			refresh_equip()
	refresh_stat_display()

#drops an item from the inventory. Uses curr_item
def drop_item():
	if action.has_dialog == 1: return 0
	if curr_item >= len(item.inv) or item.inv[curr_item] == -1:
		return 0
	try: item_to_delete = item.find_inv_item(item.inv[curr_item])
	except IndexError: return 0

	if item.item[item.inv[item_to_delete]].price == 0 and \
				item.item[item.inv[item_to_delete]].value == 0:
		main.print_message("You feel attached to your " +
			item.item[item.inv[item_to_delete]].name)
		return 0
	#the inv[] location of the item is now in item_to_delete.
	#Ask if the player really wants to drop it.

#	main.canvas_map.unbind("<ButtonRelease-1>")
#	main.canvas_map.unbind("<Motion>")

	tmp_surface = pygame.Surface((300, 200))
	tmp_surface.blit(g.screen, (0,0), (170, 140, 300, 200))
	if main.show_yesno("Drop your " +
			item.item[item.inv[item_to_delete]].name + "?"):
		g.screen.blit(tmp_surface, (170, 140))
		main.print_message("You drop your " +
			item.item[item.inv[curr_item]].name)

		# add dropped item to map
		g.maps[g.zgrid].additem(item.item[item.inv[item_to_delete]].name,
			g.xgrid, g.ygrid)


		#remove the item from inventory
		item.drop_inv_item(curr_item)
	else: g.screen.blit(tmp_surface, (170, 140))
	main.refresh_tile(g.xgrid, g.ygrid, g.zgrid)
	g.cur_window = "inventory_drop"
	refresh_drop()


#called when "Use" is pressed. Either uses the current location in
# the inv, or the item_index.
def use_item(item_index=-1):
#	if action.has_dialog == 1: return 0
	if item_index == -1:
		if curr_item >= len(item.inv) or item.inv[curr_item] == -1:
			return 0

		#put the item[] index of the item into item_value
		try: item_value = item.inv[curr_item]
		except IndexError: return 0

		#put the equip slot into item_loc
		item_loc = item.item[item_value].type
		#if equipment
		if item_loc < 6:
			wear_item()
			return
		if item_loc == 15:
			return
		main.print_message("You use your " + item.item[item_value].name)
	else:
		item_value = item_index
		item_loc = item.item[item_index].type
	#if item is healing
	if item_loc == 11:
		#heal the player, delete the item
		player.give_stat("hp", item.item[item_value].quality)
		if item_index == -1:
			item.drop_inv_item(curr_item)
	if item_loc == 16 or item_loc == 17:
		if action.activate_lines(g.xgrid, g.ygrid, g.zgrid,
										item.item[item_value].scripting) == 1:
			if item_index == -1:
				item.drop_inv_item(curr_item)

	if item_index == -1:
		refresh_use()
		refresh_stat_display()


def useskill(free_skill=0):
	#sanity checks
	skill_index = curr_item
	if skill_index >= len(player.skill): return 0

	if free_skill == 0:
		if player.skill[skill_index][5] == 0: return 0
		if player.skill[skill_index][2] > player.ep: return 0

	if player.skill[skill_index][1] == 5 or \
			player.skill[skill_index][1] == 6: #Scripted
		tempxy = (g.xgrid, g.ygrid, g.zgrid)
		#If the scripting ends with an "end" command,
		if action.activate_lines(g.xgrid, g.ygrid, g.zgrid,
								player.skill[skill_index][6]) == 1:
			if free_skill == 0:
				#pay for the skill
				player.give_stat("ep", -1*player.skill[skill_index][2])
		main.refresh_bars()
		refresh_stat_display()
		if tempxy != (g.xgrid, g.ygrid, g.zgrid):
			return "end"
	return 1


#refresh buttons in the main inv menu.
def refresh_menu_buttons():
	global oldbutton
	if action.has_dialog == 1: return 0


	if oldbutton == cur_button: return
	oldbutton = cur_button
#	if main.canvas_map.winfo_exists() == 0: return 0
#	main.canvas_map.delete("buttons")
	use_image = "use.png"
	equip_image = "equip.png"
	drop_image = "drop.png"
	skill_image = "skill.png"
	save_image = "save.png"
	leave_image = "leave.png"
	if (cur_button == 0): use_image = "use_sel.png"
	elif (cur_button == 1): equip_image = "equip_sel.png"
	elif (cur_button == 2): drop_image = "drop_sel.png"
	elif (cur_button == 3): skill_image = "skill_sel.png"
	elif (cur_button == 4): save_image = "save_sel.png"
	elif (cur_button == 5): leave_image = "leave_sel.png"

	g.screen.blit(g.buttons[use_image], (base_x, base_y))
	g.screen.blit(g.buttons[equip_image], (base_x, base_y+equip_height))
	g.screen.blit(g.buttons[drop_image], (base_x, base_y+drop_height))
	g.screen.blit(g.buttons[skill_image], (base_x, base_y+skill_height))
	g.screen.blit(g.buttons[save_image], (base_x, base_y+save_height))
	g.screen.blit(g.buttons[leave_image], (base_x, base_y+leave_height))

	pygame.display.flip()


#refresh this screen. Call after moving around items. x,y is the location
#of the upper-left of the inv display on the main screen.
def refresh_inv(x, y, input_tag):
	if action.has_dialog == 1: return 0
#	canvas_inv.delete("item")
# 	invpos = 0
	#Draw a selection box around the current item.
#	if cur_button == 0 or (cur_button == 1):
	for i in range(len(item.inv)):
		g.create_norm_box((
			x+(i%inv_width)*g.tilesize + 2 * ((i%inv_width)+1),
			y+(i/inv_width)*g.tilesize + 2 * ((i/inv_width)+1)),
			(g.tilesize, g.tilesize), inner_color="dh_green")

	if (curr_item != -1):
		g.create_norm_box((
			x+(curr_item%inv_width)*g.tilesize + 2 * ((curr_item%inv_width)+1),
			y+(curr_item/inv_width)*g.tilesize + 2 * ((curr_item/inv_width)+1)),
			(g.tilesize, g.tilesize), inner_color="dark_green")

	#draw the item pictures.
	for i in range(len(item.inv)):
		if item.inv[i] != -1:
			draw_item(item.item[item.inv[i]].picturename,
						i%inv_width, i/inv_width, x, y, input_tag)
# 			invpos += 1

#	canvas_equip.delete("item")
	if cur_button == 3: #equipment
		g.create_norm_box((
			(curr_item%equip_size)*g.tilesize + 2 * ((curr_item%equip_size)+1),
			(curr_item/equip_size)*g.tilesize + 2 * ((curr_item/equip_size)+1)),
			(g.tilesize, g.tilesize), inner_color="dark_green")


#Takes a canvas, a string (leading to a picture in g.tiles[]), and xy coords
#(in tiles, starting from 0), an xy offset from the upper-left of canvas_map,
#and draws the picture.
def draw_item(input_picture, x, y, x_offset, y_offset, tag):
	g.screen.blit(g.tiles[input_picture], (x_offset+x*g.tilesize + 2*(x+1),
		y_offset + y*g.tilesize + 2*(y+1)))


#All keypresses in window_inv pass through here. Based on the key name,
#give the right action. ("etc", "left", "right", "up", "down", "return")
def menu_key_handler(key_name):
#	if action.has_dialog == 1: return 0
	global cur_button
	if (key_name == g.bindings["cancel"]):
		return 1
	elif (key_name == g.bindings["right"]) or (key_name == g.bindings["down"]):
		cur_button += 1
		if cur_button > 5: cur_button = 0
	elif (key_name == g.bindings["left"]) or (key_name == g.bindings["up"]):
		cur_button -= 1
		if cur_button < 0: cur_button = 5
	elif (key_name == g.bindings["action"]):
		#I take care of refresh by grabbing the current window as a bitmap,
		#then redisplaying it. Note that the -64 is to prevent the message
		#scroller from being clobbered
		old_screen_refresh = pygame.Surface((g.screen_size[0], g.screen_size[1]-64))
		old_screen_refresh.blit(g.screen, (0,0))
		if (cur_button == 0): open_use_item()
		elif (cur_button == 1): open_equip_item()
		elif (cur_button == 2): open_drop_item()
		elif (cur_button == 3):
			tmp = open_skill_menu()
			if tmp == "end": return 1
		elif (cur_button == 4):
			inv_savegame()
			return 0
		elif (cur_button == 5):
			leave_inv()
			return 1
		g.screen.blit(old_screen_refresh, (0,0))
	refresh_menu_buttons()
	refresh_stat_display()

#generic key handler for anytime there is an inner inv window open.
def inner_key_handler(key_name):
	global cur_button
	global curr_item
	if (key_name == g.bindings["cancel"]):
		#leave_inner()
		return 1
	elif (key_name == g.bindings["right"]):
		curr_item += 1
		if curr_item >= inv_width * inv_height:
			curr_item -= inv_width * inv_height
	elif (key_name == g.bindings["left"]):
		curr_item -= 1
		if curr_item < 0:
			curr_item += inv_width * inv_height
	elif (key_name == g.bindings["up"]):
		curr_item = curr_item - inv_width
		if curr_item < 0:
			curr_item += inv_width * inv_height
	elif (key_name == g.bindings["down"]):
		curr_item = curr_item + inv_width
		if curr_item >= inv_width * inv_height:
			curr_item -= inv_width * inv_height
	elif (key_name == g.bindings["action"]):
		return 2
	return 0

def use_key_handler(key_name):
	tmp = inner_key_handler(key_name)
	if tmp == 2: use_item()
	if tmp != 1: refresh_use()
	return tmp

def drop_key_handler(key_name):
	tmp = inner_key_handler(key_name)
	if tmp == 2: drop_item()
	if tmp != 1: refresh_drop()
	return tmp

def skill_key_handler(key_name):
	tmp = inner_key_handler(key_name)
	if tmp == 2:
		tmp2 = useskill()
		if tmp2 == "end": return "end"
	if tmp != 1: refresh_skill("skill")
	return tmp

#I have to do this separate, as the equip screen has an extra display.
def equip_key_handler(key_name):
	global cur_button
	global curr_item
	if (key_name == g.bindings["cancel"]):
# 		leave_inner()
		return 1
	elif (key_name == g.bindings["right"]):
		if cur_button == 1: #if equip screen
			if curr_item < inv_width * inv_height: #if in inv
				if (curr_item % inv_width == inv_width-1):  #if on right side
					if curr_item / inv_width >= equip_size:
						curr_item = equip_size * inv_width - 1
					curr_item = (curr_item/inv_width)*equip_size + inv_width*inv_height-1
			else: #equip
				c_item = curr_item - inv_width * inv_height
				if (c_item % equip_size == equip_size-1):  #if on right side
					curr_item = (c_item / equip_size) * inv_width - 1
		curr_item += 1
	elif (key_name == g.bindings["left"]):
		if cur_button == 1: #if equip screen
			if curr_item < inv_width * inv_height: #if in inv
				if (curr_item % inv_width == 0):  #if on left side
					if curr_item / inv_width >= equip_size:
						curr_item = (equip_size-1) * inv_width
					curr_item = ((curr_item/inv_width)+1)*equip_size + inv_width*inv_height
			else: #equip
				c_item = curr_item - inv_width * inv_height
				if (c_item % equip_size == 0):  #if on left side
					curr_item = ((c_item / equip_size)+1) * inv_width
		curr_item -= 1
	elif (key_name == g.bindings["up"]):
		if curr_item >= inv_width * inv_height: #equip
			curr_item -= equip_size
			if curr_item < (inv_width * inv_height):
				curr_item += (equip_size*equip_size)
		else: #inv
			curr_item -= inv_width
			if curr_item < 0:
				curr_item += inv_width * inv_height
	elif (key_name == g.bindings["down"]):
		if curr_item >= inv_width * inv_height: #equip
			curr_item += equip_size
			if curr_item >= (inv_width * inv_height) + (equip_size*equip_size):
				curr_item -= (equip_size*equip_size)
		else: #inv
			curr_item += inv_width
			if curr_item >= inv_width * inv_height:
				curr_item -= inv_width * inv_height
	elif (key_name == g.bindings["action"]):
		wear_item()
	refresh_equip()
	return 0

def menu_mouse_click(xy):
	if action.has_dialog == 1: return 0
	base_loc_y = xy[1] - base_y
	base_loc_x = xy[0] - base_x
	if (base_loc_y < 0 or base_loc_x < 0 or base_loc_y > total_height or
				base_loc_x > button_width): return
	return menu_key_handler(g.bindings["action"])

#generic mouse click while an inner menu is open.
def inner_mouse_click(xy, button):
	#decide if the mouse is within one of the boxes.
	global curr_item
	#global curr_focus
	temp_num =  which_box(xy[0]-tmp_x_base, xy[1]-tmp_y_base, inv_width)
	if ((xy[0] > tmp_menu_x_base) and (xy[1] > tmp_menu_y_base) and
				(xy[0] < tmp_menu_x_base + tmp_menu_width) and
				xy[1] < tmp_menu_y_base + tmp_menu_height):
		if xy[0] < tmp_menu_x_base + g.buttons[button+".png"].get_width():
			return 2
		else:
			#leave_inner()
			return 1
	else:
		curr_item = temp_num
	return 0

def use_mouse_click(xy):
	tmp = inner_mouse_click(xy, "use")
	if tmp == 2: use_item()
	if tmp != 1: refresh_use()
	return tmp

def drop_mouse_click(xy):
	tmp = inner_mouse_click(xy, "use")
	if tmp == 2: drop_item()
	if tmp != 1: refresh_drop()
	return tmp

def skill_mouse_click(xy):
	tmp = inner_mouse_click(xy, "skill")
	if tmp == 2:
		tmp2 = useskill()
		if tmp2 == "end": return "end"
	if tmp != 1: refresh_skill("skill")
	return tmp

def equip_mouse_click(xy):
	#decide if the mouse is within one of the boxes.
	global curr_item
	#global curr_focus
	temp_num =  which_box(xy[0]-tmp_x_base, xy[1]-tmp_y_base, inv_width)
	#If the click was outside of the inv area.
	if temp_num == -1:
		temp_canvas_width=(g.tilesize*equip_size)+ 8
		#If the click was in the button area.
		if ((xy[0] > tmp_menu_x_base) and (xy[1] > tmp_menu_y_base) and
		(xy[0] < tmp_menu_x_base + tmp_menu_width) and
		xy[1] < tmp_menu_y_base + tmp_menu_height):
			if xy[0] < tmp_menu_x_base + g.buttons["equip.png"].get_width():
				wear_item()
			else:
				#leave_inner()
				return 1
		#If the click was inside the equip area.
		elif ((xy[0] > tmp_x_base-temp_canvas_width) and
		(xy[1] > tmp_y_base) and (xy[0] < tmp_x_base) and
		(xy[1] < tmp_y_base+temp_canvas_width)):
			temp_num =  which_box(xy[0]-tmp_x_base+temp_canvas_width,
						xy[1]-tmp_y_base, equip_size)
			if temp_num != -1:
				curr_item = temp_num+inv_width * inv_height
	else:
		curr_item = temp_num
	refresh_equip()

def inner_mouse_dbl_click(xy):
	#decide if the mouse is within one of the boxes.
	global curr_item
	temp_num =  which_box(xy[0]-tmp_x_base, xy[1]-tmp_y_base, inv_width)
	if temp_num != -1:
		curr_item = temp_num
		return 1
	return 0

def equip_mouse_dbl_click(xy):
	#decide if the mouse is within one of the boxes.
	global curr_item
	#global curr_focus
	temp_num =  which_box(xy[0]-tmp_x_base, xy[1]-tmp_y_base, inv_width)
	#If the click was outside of the inv area.
	if temp_num == -1:
		temp_canvas_width=(g.tilesize*equip_size)+ 8
		#If the click was inside the equip area.
		if ((xy[0] > tmp_x_base-temp_canvas_width) and
		(xy[1] > tmp_y_base) and (xy[0] < tmp_x_base) and
		(xy[1] < tmp_y_base+temp_canvas_width)):
			temp_num =  which_box(xy[0]-tmp_x_base+temp_canvas_width,
						xy[1]-tmp_y_base, equip_size)
			if temp_num != -1:
				curr_item = temp_num+inv_width * inv_height
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

#Used in mouse_sel_inv. Takes x y coordinates, (relative to the upper-left of
#the inv box) and returns the selected box, or -1 for none. temp_size is
#the width of the inventory box.
def which_box(x, y, temp_size):
	#Check for the left border
	if x < 3: return -1
	#Transform x from pixels to tiles
	tempx = x - 3
	likelyx = tempx / (g.tilesize + 2)
	tempx = tempx - (likelyx * (g.tilesize + 2))
	if tempx >= g.tilesize - 1: return -1


	#Check for the top border
	if y < 3: return -1
	#Transform y from pixels to tiles
	tempy = y - 3
	likelyy = tempy / (g.tilesize + 2)
	tempy = tempy - (likelyy * (g.tilesize + 2))
	if tempy >= g.tilesize - 1: return -1
	#Final check, then return the location in the inv.
	if likelyy * temp_size + likelyx >= temp_size * inv_height: return -1
	if likelyx >= temp_size: return -1
	return likelyy * temp_size + likelyx

def menu_mouse_move(xy):
#	if action.has_dialog == 1: return 0
	global cur_button
	base_loc_y = xy[1] - base_y
	base_loc_x = xy[0] - base_x
	if (base_loc_y < 0 or base_loc_x < 0 or base_loc_y > total_height or
				base_loc_x > button_width): return
	elif (base_loc_y < equip_height): cur_button = 0
	elif (base_loc_y < drop_height): cur_button = 1
	elif (base_loc_y < skill_height): cur_button = 2
	elif (base_loc_y < save_height): cur_button = 3
	elif (base_loc_y < leave_height): cur_button = 4
	else: cur_button = 5
	refresh_menu_buttons()

def inner_mouse_move(xy, button = ""):
	global inner_cur_button
	if ((xy[0] > tmp_menu_x_base) and (xy[1] > tmp_menu_y_base) and
				(xy[0] < tmp_menu_x_base + tmp_menu_width) and
				xy[1] < tmp_menu_y_base + tmp_menu_height):
		if xy[0] < tmp_menu_x_base + g.buttons[button+".png"].get_width():
			inner_cur_button = 0
		else:
			inner_cur_button = 1
		return 1
	else: return 0

def use_mouse_move(xy):
	if inner_mouse_move(xy, "use"):
		refresh_use_buttons()

def drop_mouse_move(xy):
	if inner_mouse_move(xy, "drop"):
		refresh_drop_buttons()

def equip_mouse_move(xy):
	if inner_mouse_move(xy, "equip"):
		refresh_equip_buttons()

def skill_mouse_move(xy):
	if inner_mouse_move(xy, "skill"):
		refresh_skill_buttons()

#This creates the inv area within the map canvas.
def init_window_inv():
#	main.canvas_map.delete("inv")
	global cur_button; cur_button = 0
	global oldbutton; oldbutton = 99

	#Location of the various buttons.
	global equip_height; equip_height = g.buttons["use.png"].get_height()
	global drop_height; drop_height = equip_height + g.buttons["equip.png"].get_height()
	global skill_height; skill_height = drop_height + g.buttons["skill.png"].get_height()
	global save_height; save_height = skill_height + g.buttons["drop.png"].get_height()
	global leave_height; leave_height = save_height + g.buttons["save.png"].get_height()
	global total_height; total_height = leave_height + g.buttons["leave.png"].get_height()

	global button_width; button_width = g.buttons["drop.png"].get_width()

	global base_x; base_x = (g.tilesize*main.mapsizex)/2 - button_width
	global base_y; base_y = (g.tilesize*main.mapsizey - total_height)/2

	global inv_canvas_width; global inv_canvas_height
	inv_canvas_width = (g.tilesize*inv_width)+ ((inv_width+1)*2) + 1
	inv_canvas_height = (g.tilesize*inv_height)+ ((inv_height+1)*2) + 1


	start_x = (g.tilesize*main.mapsizex)/2
	start_y = (g.tilesize*main.mapsizey - total_height)/2
	#Create the main inv box.
	#The +20 is just "wiggle room", to prevent the length of the name
	#affecting the dimensions.
	g.create_norm_box((base_x, base_y), ((g.tilesize*main.mapsizex)/2
		 + g.hpbar_width + 15-base_x,
		(g.tilesize*main.mapsizey + total_height)/2-base_y))

	global curr_item
	curr_item = 0

	#Set current window to inventory
	g.cur_window = "inventory"

	temp_width = g.hpbar_width*player.ep/player.adj_maxep
	if temp_width < 0: temp_width=0

	#Create the labels to the right:
	tmp_width = 52
	label_start = ((g.tilesize*main.mapsizex)/2 + tmp_width,
	(g.tilesize*main.mapsizey - total_height)/2)
	text = g.name_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+5),
		align=2)
	text = g.hp_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+22),
		align=2)
	text = g.ep_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+39),
		align=2)
	text = g.attack_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+55),
		align=2)
	text = g.defense_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+70),
		align=2)
	text = g.gold_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+85),
		align=2)
	text = g.level_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+100),
		align=2)
	text = g.exp_name+":"
	g.print_string(g.screen, text, g.font, (label_start[0], label_start[1]+115),
		align=2)

	#bindings
	menu_bind_keys()
	refresh_menu_buttons()
	refresh_stat_display()
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				if menu_key_handler(event.key) == 1:
					return
			elif event.type == pygame.MOUSEMOTION:
				menu_mouse_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if menu_mouse_click(event.pos) == 1:
					return
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if tmpjoy != g.bindings["left"] and tmpjoy != g.bindings["right"]:
				if menu_key_handler(tmpjoy) == 1:
					return

#bind the keys. Called upon window creation and return from a yes/no box
def menu_bind_keys():
	g.cur_window = "inventory"
