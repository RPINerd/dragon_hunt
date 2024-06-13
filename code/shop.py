#file: shop.py
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

#This file controls the town shops.


#from Tkinter import *
import pygame

##needed for the buttons.
#import ImageTk
#import Image

import main
import g
import item
from player import *



#location of the store in the g.shops[] array
global store_num
store_num = 0

#width/height of inv and shop windows, in tiles.
# (g.tilesize + the 3 pixel border)
shop_width = 4
shop_height = 7

#Currently selected item number
curr_item = 0
#If inv (0) or shop (1) has focus.
curr_focus = 1

#currently selected button: 0=sell 1=leave 2=buy
cur_button=2

leave_height=0
buy_height=0
sell_height=0

#array containing the item[] index of all inventory items.
#Used to determine which item to sell/drop
#global listbox_inv_array
#listbox_inv_array = []

#variables for the middle info display
#item_name  = StringVar()
#item_cost  = StringVar()
#item_value = StringVar()
#item_power = StringVar()
#item_desc  = StringVar()
#curr_gold  = StringVar()
#curr_skill = StringVar()

#global store_name
#store_name = StringVar()

temp_canvas_width=0
temp_canvas_height=0
canvas_x_start = 0
canvas_y_start = 0


temp_button_x = 0
temp_button_width = 0
temp_button_y = 0


#back_to_main = StringVar()

#refresh the button canvas
def refresh_buttons():
	global prev_button

	if prev_button == cur_button: return
	prev_button = cur_button

#	main.canvas_map.delete("shop_buttons")
	g.create_norm_box((temp_button_x, temp_button_y),
		(temp_button_width, g.buttons["sell.png"].get_height()))

# 	main.canvas_map.create_rectangle(temp_button_x, temp_button_y,
# 				temp_button_x+temp_button_width,
# 				temp_button_y+g.buttons["sell.png"].get_height(), fill=bgcolour,
# 				tags=("shop_buttons", "shop"))
	if (cur_button == 0):
		g.screen.blit(g.buttons["sell_sel.png"], (temp_button_x, temp_button_y))
# 		 main.canvas_map.create_image(
# 						temp_button_x, temp_button_y, anchor=NW,
# 						image=g.buttons["sell_sel.png"],
# 						tags=("shop_buttons", "shop"))
	else: g.screen.blit(g.buttons["sell.png"], (temp_button_x, temp_button_y))
# 		 main.canvas_map.create_image(temp_button_x, temp_button_y, anchor=NW,
# 						image=g.buttons["sell.png"],
# 						tags=("shop_buttons", "shop"))

	if (cur_button == 1):
		g.screen.blit(g.buttons["leave_shop_sel.png"],
			(temp_button_x+leave_height, temp_button_y))
# 		 main.canvas_map.create_image(
# 						temp_button_x+leave_height, temp_button_y,
# 						anchor=NW, image=g.buttons["leave_shop_sel.png"],
# 						tags=("shop_buttons", "shop"))
	else:
		g.screen.blit(g.buttons["leave_shop.png"],
			(temp_button_x+leave_height, temp_button_y))
# 		 main.canvas_map.create_image(temp_button_x+leave_height,
# 						temp_button_y, anchor=NW,
# 						image=g.buttons["leave_shop.png"],
# 						tags=("shop_buttons", "shop"))

	if (cur_button == 2):
		g.screen.blit(g.buttons["buy_sel.png"],
			(temp_button_x+buy_height, temp_button_y))
# 		 main.canvas_map.create_image(
# 						temp_button_x+buy_height, temp_button_y, anchor=NW,
# 						image=g.buttons["buy_sel.png"],
# 						tags=("shop_buttons", "shop"))
	else:
		g.screen.blit(g.buttons["buy.png"],
			(temp_button_x+buy_height, temp_button_y))
# 		 main.canvas_map.create_image(temp_button_x+buy_height,
# 						temp_button_y, anchor=NW,
# 						image=g.buttons["buy.png"],
# 						tags=("shop_buttons", "shop"))
	pygame.display.flip()

#refresh the inventory canvas
# def refresh_inv():
# 	canvas_inv.delete("inv")

#Actually sets the info in the middle of the shop screen.
def set_details(name, cost, value, costtype, power, description, inv_or_shop):
#	main.canvas_map.delete("shop_details")

	g.screen.fill(g.colors["light_gray"],
		(canvas_x_start+temp_canvas_width, canvas_y_start+25, 137, 190))

	g.print_string(g.screen, name, g.font, (canvas_x_start+temp_canvas_width+5,
		canvas_y_start+25))

# 	main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 		canvas_y_start+25, anchor=W, text=name, tags=("shop_details", "shop"))

	if inv_or_shop == "shop":
		if cost != "":
				g.print_string(g.screen, "Cost: "+str(cost), g.font,
					(canvas_x_start+temp_canvas_width+5,
					canvas_y_start+40))
# 				main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 				canvas_y_start+40, anchor=W, text="Cost: "+str(cost),
# 				tags=("shop_details", "shop"))
	elif inv_or_shop == "inv":
		if value != "":
			g.print_string(g.screen, "Value: "+str(value), g.font,
				(canvas_x_start+temp_canvas_width+5,
				canvas_y_start+40))
# 			main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 			canvas_y_start+40, anchor=W, text="Value: "+str(value),
# 			tags=("shop_details", "shop"))
	if power == "" or power == "-1": pass
	else: g.print_string(g.screen, "Power: "+str(power), g.font,
				(canvas_x_start+temp_canvas_width+5,
				canvas_y_start+55))
# 		 main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 		canvas_y_start+55, anchor=W, text="Power: "+str(power),
# 		tags=("shop_details", "shop"))

	g.print_multiline(g.screen, description, g.font,
		130, (canvas_x_start+temp_canvas_width+5,
		canvas_y_start+70))
# 	main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 		canvas_y_start+70, anchor=NW, width=130, text=description,
# 		tags=("shop_details", "shop"))
	pygame.display.flip()

#show info for a selected item in the middle of the window.
def show_details(event=0, sel_item=-1):
	#The use of sel_item gives the ability to look at an item without selecting
	#it, while working normally the rest of the time.
	if sel_item == -1: sel_item = curr_item
	if curr_focus == 0:  #inv
		if sel_item < len(item.inv):
			if item.inv[sel_item] != -1:
				tempitem = item.item[item.inv[sel_item]]
				if (tempitem.type == 14 and
					g.shops[store_num].name == "a Gem Shop"):
					set_details(tempitem.name, tempitem.price, tempitem.price, "gold",
									tempitem.quality, tempitem.description, "inv")
				else:
					set_details(tempitem.name, tempitem.price, tempitem.value, "gold",
									tempitem.quality, tempitem.description, "inv")
		#if there is no item selected, blank details.
			else: set_details("", "", "", "", "", "", "inv")
		else: set_details("", "", "", "", "", "", "inv")

	else:  #shop
		if sel_item < len(g.shops[store_num].itemlist):
			tempitem = g.shops[store_num].itemlist[sel_item]
			set_details(tempitem.item_name, tempitem.cost, tempitem.value, tempitem.buytype,
										tempitem.power, tempitem.description, "shop")
		else: set_details("", "", "", "", "", "", "shop")

#place appropriate items into the store.
def refresh_shop():
# 	main.canvas_map.delete("item")
	invpos = 0
# 		main.canvas_map.create_rectangle(
# 			canvas_x_start+temp_canvas_width*2+(curr_item%shop_width)*g.tilesize + 2 *
# 												((curr_item%shop_width)+1),
# 			canvas_y_start+(curr_item/shop_width)*g.tilesize + 2 *
# 												((curr_item/shop_width)+1),
# 			canvas_x_start+temp_canvas_width*2+((curr_item%shop_width)+1)*(g.tilesize + 2),
# 			canvas_y_start+((curr_item/shop_width)+1)*(g.tilesize + 2),
# 											fill=g.fill_sel_colour, tags=("item", "shop"))

	#per-item borders
	for y in range(shop_height):
		for x in range(shop_width):
			g.create_norm_box((canvas_x_start+x*g.tilesize+2*(x+1),
				canvas_y_start+y*g.tilesize + 2 * (y+1)),
				(g.tilesize, g.tilesize), inner_color="dh_green")
	for y in range(shop_height):
		for x in range(shop_width):
			g.create_norm_box((
				temp_canvas_width*2+canvas_x_start+x*g.tilesize + 2 * (x+1),
				canvas_y_start+y*g.tilesize + 2 * (y+1)),
				(g.tilesize, g.tilesize), inner_color="dh_green")


	#if the shop is selected, draw a selection box around the current item.
	if curr_focus == 1:
		g.create_norm_box(((canvas_x_start+temp_canvas_width*2+
			(curr_item%shop_width)*g.tilesize + 2 *((curr_item%shop_width)+1)),
			canvas_y_start+(curr_item/shop_width)*g.tilesize + 2 *
			((curr_item/shop_width)+1)), (g.tilesize, g.tilesize),
				inner_color="dark_green")

	#draw the item pictures.
	for i in range(len(g.shops[store_num].itemlist)):
		if i != -1:
			g.screen.blit(g.tiles[g.shops[store_num].itemlist[i].picture],
			(canvas_x_start+temp_canvas_width*2+(invpos%shop_width)*g.tilesize +
				2 * ((invpos%shop_width)+1),
				canvas_y_start+(invpos/shop_width)*g.tilesize + 2
				* ((invpos/shop_width)+1)))
# 			main.canvas_map.create_image(
# 				canvas_x_start+temp_canvas_width*2+(invpos%shop_width)*g.tilesize + 2 *
# 													((invpos%shop_width)+1),
# 				canvas_y_start+(invpos/shop_width)*g.tilesize + 2 * ((invpos/shop_width)+1),
# 				image=g.tiles[g.shops[store_num].itemlist[i].picture],
# 				anchor="nw", tags=("item", "shop"))
			invpos += 1
	invpos = 0
	#if the inv is selected, draw a selection box around the current item.
	if curr_focus == 0:
		g.create_norm_box((canvas_x_start+(curr_item%shop_width)*g.tilesize +
							2 * ((curr_item%shop_width)+1),
				canvas_y_start+(curr_item/shop_width)*g.tilesize +
							2 * ((curr_item/shop_width)+1)),
							 (g.tilesize, g.tilesize), inner_color="dark_green")
# 		main.canvas_map.create_rectangle(
# 				canvas_x_start+(curr_item%shop_width)*g.tilesize +
# 							2 * ((curr_item%shop_width)+1),
# 				canvas_y_start+(curr_item/shop_width)*g.tilesize +
# 							2 * ((curr_item/shop_width)+1),
# 				canvas_x_start+((curr_item%shop_width)+1)*(g.tilesize + 2),
# 				canvas_y_start+((curr_item/shop_width)+1)*(g.tilesize + 2),
# 							fill=g.fill_sel_colour, tags=("item", "shop"))

	#draw the item pictures.
	for i in range(len(item.inv)):
		if item.inv[i] != -1:
			g.screen.blit(g.tiles[item.item[item.inv[i]].picturename],
				(canvas_x_start+(i%shop_width)*g.tilesize + 2 * ((i%shop_width)+1),
				canvas_y_start+(i/shop_width)*g.tilesize + 2 * ((i/shop_width)+1)))
# 			main.canvas_map.create_image(canvas_x_start+(i%shop_width)*g.tilesize + 2 *
# 												((i%shop_width)+1),
# 				canvas_y_start+(i/shop_width)*g.tilesize + 2 * ((i/shop_width)+1),
# 				image=g.tiles[item.item[item.inv[i]].picturename],
# 				anchor="nw", tags=("item", "shop"))
			invpos += 1

	#set gold and skillpoints
	g.screen.fill(g.colors["light_gray"], (canvas_x_start+temp_canvas_width+5,
		canvas_y_start+temp_canvas_height-26, 120, 25))

	g.print_string(g.screen, g.gold_name+": "+str(player.gold), g.font,
		(canvas_x_start+temp_canvas_width+5,
		canvas_y_start+temp_canvas_height-26))
	g.print_string(g.screen, g.skill_name+": "+str(player.skillpoints), g.font,
		(canvas_x_start+temp_canvas_width+5,
		canvas_y_start+temp_canvas_height-11))

# 	main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 		canvas_y_start+temp_canvas_height-20, anchor=SW,
# 		text=g.gold_name+": "+str(player.gold), tags=("item", "shop"))
# 	main.canvas_map.create_text(canvas_x_start+temp_canvas_width+5,
# 		canvas_y_start+temp_canvas_height-2, anchor=SW,
# 		text=g.skill_name+": "+str(player.skillpoints), tags=("item", "shop"))
#	curr_gold.set("Gold: " + str(player.gold))
#	curr_skill.set("Skillpoints: " + str(player.skillpoints))
	main.refresh_inv_icon()
	main.refresh_bars()

#called upon pressing "Sell". Uses the selected item.
def sell_item():
	if curr_focus != 0: return 0
	if curr_item > len(item.inv): return 0
	if item.inv[curr_item] == -1: return 0

	if item.item[item.inv[curr_item]].price == 0:
		main.print_message("You feel attached to your " +
			item.item[item.inv[curr_item]].name)
		return 0
	#give the player money
	#note that all stores have a 5 year, money-back guarantee,
	#and accept returns from other stores as well.
	#This means there is no need to doublecheck intent. ;)
	#FIXME: this is no longer true since gems aren't paid for
	#full value anywhere but the gem shop
	#print g.shops[store_num].name
	if (item.item[item.inv[curr_item]].type == 14 and
				g.shops[store_num].name == "a Gem Shop"):
		main.print_message("The Gem Shop owner is happy to pay the true value of your gems.")
		player.give_stat("gold", item.item[item.inv[curr_item]].price)
	else:
		player.give_stat("gold", item.item[item.inv[curr_item]].value)

	main.print_message("You sell your " + item.item[item.inv[curr_item]].name
		+ ".")

	#remove the item
	item.drop_inv_item(curr_item)
	#refresh_inv()
	refresh_shop()
	show_details()


#Call on pressing "Buy". Uses the selected item.
def buy_item():
	if curr_focus != 1: return 0
	if curr_item >= len(g.shops[store_num].itemlist): return 0

	if (g.shops[store_num].itemlist[curr_item].buytype == "gold"):
		#if enough gold
		if int(g.shops[store_num].itemlist[curr_item].cost) <= int(player.gold):
			#if no actions were given
			if (len(g.shops[store_num].itemlist[curr_item].actions) == 0):
				#if given successfully.
				if (main.action.run_command(0, 0, 0, "item(\"" +
						g.shops[store_num].itemlist[curr_item].item_name+"\")")
						== 1):
					main.print_message("You buy a " +
					g.shops[store_num].itemlist[curr_item].item_name + ".")
					player.give_stat("gold", -1*
						int(g.shops[store_num].itemlist[curr_item].cost))
				else: #not enough room
					main.print_message("Your inventory is full.")
			else:
				temp = main.action.activate_lines(0, 0, 0,
						g.shops[store_num].itemlist[curr_item].actions)
				if temp == 1:
					player.give_stat("gold", -1*
							int(g.shops[store_num].itemlist[curr_item].cost))
	else: #skillpoints
		#if enough skillpoints
		if int(g.shops[store_num].itemlist[curr_item].cost) <= \
													int(player.skillpoints):
			#if no actions were given
			if (len(g.shops[store_num].itemlist[curr_item].actions) == 0):
				#if given successfully.
				if (main.action.run_command(0, 0, 0, "item(\"" +
						g.shops[store_num].itemlist[curr_item].item_name+"\")")
						== 1):
					main.print_message("You buy a " +
					g.shops[store_num].itemlist[curr_item].item_name + ".")
					player.give_stat("skillpoints", -1*
					int(g.shops[store_num].itemlist[curr_item].cost))
			else:
				temp = main.action.activate_lines(0, 0, 0,
							g.shops[store_num].itemlist[curr_item].actions)
				if temp == 1:
					player.give_stat("skillpoints", -1*
							int(g.shops[store_num].itemlist[curr_item].cost))

	#refresh_inv()
	refresh_shop()
	show_details()

#Used in mouse_sel_inv and mouse_sel_shop. Takes x y coordinates, and returns
#the selected box, or -1 for none.
def which_box(x, y):
	if x < 3: return -1
	tempx = x - 3
	likelyx = tempx / (g.tilesize + 2)
	tempx = tempx - (likelyx * (g.tilesize + 2))
	if tempx >= g.tilesize - 1: return -1

	if y < 3: return -1
	tempy = y - 3
	likelyy = tempy / (g.tilesize + 2)
	tempy = tempy - (likelyy * (g.tilesize + 2))
	if tempy >= g.tilesize - 1: return -1

	if likelyx >= shop_width: return -1
	if likelyy * shop_width + likelyx >= shop_width * shop_height: return -1

	return likelyy * shop_width + likelyx

#called when the user releases the mouse in the inv canvas.
def mouse_sel_inv(xy):
	#decide if the mouse is within one of the boxes.
	global curr_item
	global curr_focus
	temp_num =  which_box(xy[0], xy[1])
	if temp_num == -1: return
	curr_item = temp_num
	curr_focus = 0
	#refresh_inv()
	refresh_shop()
	show_details()

#called when the user releases the mouse in the shop canvas.
def mouse_sel_shop(xy):
	global curr_item
	global curr_focus
	global cur_button
	global last_click_time
	global last_box
	#Is the mouse at least in the general area?.
	if xy[0] < canvas_x_start or xy[1] < canvas_y_start:
		return 0

	if last_click_time + 200 > pygame.time.get_ticks():
		last_click_time = 0
		return mouse_handler_dbl(xy)
	last_click_time = pygame.time.get_ticks()

	temp_num = which_box(xy[0]-canvas_x_start, xy[1]-canvas_y_start)
	if temp_num != -1:
		curr_item = temp_num
		curr_focus = 0
		cur_button = 0
		refresh_shop()
		show_details()
		return 0

	temp_num = which_box(xy[0]-canvas_x_start-temp_canvas_width*2,
											xy[1]-canvas_y_start)
	if temp_num != -1:
		curr_item = temp_num
		curr_focus = 1
		cur_button = 2
		refresh_shop()
		show_details()
		return 0

	if (xy[0] > temp_button_x and xy[0] < temp_button_x + temp_button_width
			and xy[1] > temp_button_y and
			xy[1] < temp_button_y + g.buttons["buy.png"].get_height()):
		if (xy[0] < temp_button_x + leave_height):
			sell_item()
		elif (xy[0] < temp_button_x + buy_height):
			#leave_shop()
			return 1
		else: buy_item()
		refresh_buttons()

# def leave_shop(xy):
# 	try:
# 		back_to_main.set(1)
# 	except TclError:
# 		pass

def mouse_handler_dbl(xy):
	global curr_item
	global curr_focus
	global cur_button
	#Is the mouse at least in the general area?.
	if xy[0] < canvas_x_start or xy[1] < canvas_y_start:
		return 0

	temp_num = which_box(xy[0]-canvas_x_start, xy[1]-canvas_y_start)
	if temp_num != -1:
		curr_item = temp_num
		curr_focus = 0
		cur_button = 0
		sell_item()
		refresh_shop()
		show_details()
		return 0

	temp_num = which_box(xy[0]-canvas_x_start-temp_canvas_width*2,
											xy[1]-canvas_y_start)
	if temp_num != -1:
		curr_item = temp_num
		curr_focus = 1
		cur_button = 2
		buy_item()
		refresh_shop()
		show_details()
		return 0


def mouse_move(xy):
	global cur_button
	if (xy[0] > temp_button_x and xy[0] < temp_button_x + temp_button_width
			and xy[1] > temp_button_y and
			xy[1] < temp_button_y + g.buttons["buy.png"].get_height()):
		if (xy[0] < temp_button_x + leave_height):
			cur_button = 0
		elif (xy[0] < temp_button_x + buy_height):
			cur_button = 1
		else: cur_button = 2
		refresh_buttons()

#All keypresses in window_shop pass through here. Based on the key name,
#give the right action. ("etc", "left", "right", "up", "down", "return")
def key_handler(switch):
	global curr_item
	global cur_button
	global curr_focus
	#switch based on keycode
	if (switch == g.bindings["cancel"]):
		#leave_shop()
		return 1
	elif (switch == g.bindings["action"]):
		if(curr_focus == 1 and cur_button == 2): buy_item()
		elif(curr_focus !=1 and cur_button == 0): sell_item()
		elif(cur_button == 1):
			#leave_shop()
			return 1
	elif (switch == g.bindings["left"]):
		if (curr_item % shop_width == 0):  #move between lists
			if curr_focus == 0:
				curr_focus = 1
				cur_button = 2
			else:
				curr_focus = 0
				cur_button = 0
			curr_item += shop_width
		curr_item -= 1
	elif (switch == g.bindings["right"]):
		if (curr_item % shop_width == shop_width - 1):  #move between lists
			if curr_focus == 0:
				curr_focus = 1
				cur_button = 2
			else:
				curr_focus = 0
				cur_button = 0
			curr_item -= shop_width
		curr_item += 1
	elif (switch == g.bindings["up"]):
		curr_item = curr_item - shop_width
		if curr_item < 0:
			curr_item += shop_width * shop_height
	elif (switch == g.bindings["down"]):
		curr_item = curr_item + shop_width
		if curr_item >= shop_width * shop_height:
			curr_item -= shop_width * shop_height

	#refresh_inv()
	refresh_shop()
	refresh_buttons()
	show_details()

#create window_shop
def init_window_shop(store_type_input):
	g.cur_window = "shop"
	global last_click_time; last_click_time = 0
	global prev_button; prev_button = 1
	global temp_canvas_width; global temp_canvas_height
	global canvas_x_start; global canvas_y_start
	global temp_button_x; global temp_button_width; global temp_button_y
	temp_canvas_width=(g.tilesize*shop_width)+ ((shop_width+1)*2) + 1
	temp_canvas_height=(g.tilesize*shop_height)+ ((shop_height+1)*2) + 1
	canvas_x_start = ((g.tilesize*main.mapsizex)-temp_canvas_width * 3)/2
	canvas_y_start = ((g.tilesize*main.mapsizey)-temp_canvas_height)/2
	temp_button_x = canvas_x_start + (temp_canvas_width*3)/2- \
			g.buttons["sell.png"].get_width()-g.buttons["leave_shop.png"].get_width()/2
	temp_button_width = g.buttons["sell.png"].get_width()+ \
			g.buttons["leave_shop.png"].get_width() + g.buttons["buy.png"].get_width()
	temp_button_y = canvas_y_start + temp_canvas_height+1

	global bgcolour
	bgcolour = "light_grey"

	g.create_norm_box((canvas_x_start-2,canvas_y_start-19),
		(temp_canvas_width*3+3, temp_canvas_height+20))

	global curr_item
	curr_item = 0
	global curr_focus
	curr_focus = 1
	global cur_button
	cur_button = 2

	store_type_input=store_type_input.lower()
	global store_num
	for i in range(len(g.shops)):
		if (g.shops[i].name.lower() == store_type_input):
			store_num = i
			break

	g.create_norm_box((canvas_x_start,canvas_y_start),
		(temp_canvas_width-1, temp_canvas_height-1))

	#per-item borders
	for y in range(shop_height):
		for x in range(shop_width):
			g.create_norm_box((canvas_x_start+x*g.tilesize+2*(x+1),
				canvas_y_start+y*g.tilesize + 2 * (y+1)),
				(g.tilesize, g.tilesize), inner_color="dh_green")


	g.create_norm_box((temp_canvas_width*2+canvas_x_start,canvas_y_start),
				(temp_canvas_width-1, temp_canvas_height-1))

	#per-item borders
	for y in range(shop_height):
		for x in range(shop_width):
			g.create_norm_box((
				temp_canvas_width*2+canvas_x_start+x*g.tilesize + 2 * (x+1),
				canvas_y_start+y*g.tilesize + 2 * (y+1)),
				(g.tilesize, g.tilesize), inner_color="dh_green")

	#Info labels
	g.print_string(g.screen, "Inventory", g.font,
		(canvas_x_start+(temp_canvas_width*1)/2, canvas_y_start-15),
		align=1)

	g.print_string(g.screen, g.shops[store_num].name, g.font,
		(canvas_x_start+(temp_canvas_width*5)/2, canvas_y_start-15),
		align=1)

# 	main.canvas_map.create_text(canvas_x_start+(temp_canvas_width*1)/2,
# 		 canvas_y_start-1, anchor=S, text="Inventory", tags="shop")
# 	main.canvas_map.create_text(canvas_x_start+(temp_canvas_width*5)/2,
# 		 canvas_y_start-1, anchor=S, text=g.shops[store_num].name, tags="shop")



	global leave_height; leave_height = g.buttons["sell.png"].get_width()
	global buy_height; buy_height = leave_height + g.buttons["leave.png"].get_width()


	#get data in listboxes
#	refresh_inv()
	refresh_shop()
	refresh_buttons()

#	main.canvas_map.unbind("<Motion>")
	#main.canvas_map.unbind("<Button-1>")
	show_details()

	pygame.display.flip()
	g.last_joy_times["ud"] = pygame.time.get_ticks()
	g.last_joy_times["lr"] = pygame.time.get_ticks()
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				if key_handler(event.key) == 1:
					return
			elif event.type == pygame.MOUSEMOTION:
				mouse_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if mouse_sel_shop(event.pos) == 1:
					return
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if key_handler(tmpjoy) == 1:
				return

