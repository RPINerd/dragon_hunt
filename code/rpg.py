#file: rpg.py
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

#This file is the first file accessed upon game start.
#It allows the player to select the module, or, if there is only one,
#automatically selects for the player.

#from Tkinter import *
import pygame

try:
	import psyco
	psyco.full()
except ImportError:
	print "Psyco not found. Installing Psyco will increase performance."


pygame.init()
pygame.font.init()


from os import listdir

#Load other windows after starting the main one,
#to prevent Tk trouble.
#unused_window = Tk()
#unused_window.withdraw()
import g
import sys


pygame.display.set_caption("Loading")

#I can't use the standard image dictionary, as that requires the screen to
#be created.
tmp_icon = pygame.image.load("../modules/default/images/buttons/icon.png")
pygame.display.set_icon(tmp_icon)

g.screen_size = (640, 480)

if g.fullscreen == 1:
	g.screen = pygame.display.set_mode(g.screen_size, pygame.FULLSCREEN)
else:
	g.screen = pygame.display.set_mode(g.screen_size)

tmpjoycount = pygame.joystick.get_count()
if pygame.joystick.get_init() == 0:
	pygame.joystick.init()

g.joystick = 0
if tmpjoycount > g.joy_num:
	g.joystick = pygame.joystick.Joystick(g.joy_num)
	g.joystick.init()
elif tmpjoycount > 0:
	print "Bad joystick_number detected. Did you unplug a joystick recently?"
	print "Switching to first joystick."
	g.joystick = pygame.joystick.Joystick(0)
	g.joystick.init()

import new_game

global array_mods
array_mods = []

global module_pos
module_pos = 0

global cur_button
cur_button = 0

global prevent_dbl_load
prevent_dbl_load = 0

#take the selected module, and send to sel_mod
def sel_list_mod():
	if module_pos < 0 or module_pos >= len(array_mods): return 0
	mod_name = array_mods[module_pos]
	sel_mod(mod_name)

#given a certain mod, run it.
def sel_mod(selected_mod):
	global prevent_dbl_load
	if prevent_dbl_load == 1: return 0
	prevent_dbl_load = 1
	g.mod_directory = "../modules/" + selected_mod

	g.create_norm_box((g.screen_size[0]/4,
		g.screen_size[1]/3), (g.screen_size[0]/2,
		g.screen_size[1]/3),
		"black", "light_gray")

# 	g.main.canvas_map.create_rectangle(g.tilesize*g.main.mapsizex/4,
# 		g.tilesize*g.main.mapsizey/3, g.tilesize*g.main.mapsizex*3/4,
# 		g.tilesize*g.main.mapsizey/3+140+g.buttons["load.png"].get_height(),
# 		fill="#e3e3e3", tags="loadgame")

	g.print_string(g.screen, "Loading. Please wait", g.font,
		(g.screen_size[0]/2, g.screen_size[1]/2), align=1)
#	g.main.canvas_map.create_text(, text="Loading. Please wait")
	pygame.display.set_caption("Loading")
	pygame.display.flip()
#	g.window_main.update_idletasks()
	g.init_data()
	new_game.init_window()
	quit_game()

def quit_game():
	g.break_one_loop = 50

def refresh_module_info():
	g.unclean_screen = True
	tmp = module_pos - (module_pos % 5)
	for i in range(5):
		if i == module_pos % 5: tmp_color = "dh_green"
		else: tmp_color = "light_gray"
		g.create_norm_box((g.tilesize*g.main.mapsizex/4+2,
			g.tilesize*g.main.mapsizey/3+
			g.buttons["loadgame_down.png"].get_height()+1+i*20),
			(g.buttons["loadgame_down.png"].get_width()-5, 17),
			inner_color=tmp_color)


		if len(array_mods) <= tmp+i: savetext = ""
		else: savetext = array_mods[tmp+i]
		g.print_string(g.screen, savetext, g.font, (g.tilesize*g.main.mapsizex/4+5,
			g.tilesize*g.main.mapsizey/3+
			g.buttons["loadgame_down.png"].get_height()+3+i*20))

# 		g.main.canvas_map.itemconfigure("load_module"+str(i), text=savetext)

#All keypresses pass through here. Based on the key name,
#give the right action. ("etc", "left", "right", "up", "down", "return")
def key_handler(switch):
	global module_pos
	if (switch == g.bindings["cancel"]): quit_game()
	elif (switch == g.bindings["left"] or switch == g.bindings["right"]):
		global cur_button
		if cur_button == 0: cur_button = 1
		else: cur_button = 0
		refresh_buttons()
	elif (switch == g.bindings["up"]):
		module_pos -= 1
		if module_pos <= -1: module_pos = len(array_mods) - 1
		refresh_module_info()
	elif (switch == g.bindings["down"]):
		module_pos += 1
		if module_pos >= len(array_mods): module_pos = 0
		refresh_module_info()
	elif (switch == g.bindings["action"]):
		if cur_button != 1: sel_list_mod()
		else: quit_game()


def mouse_over(xy, x1, y1, x2, y2):
	if xy[0] >= x1 and xy[0] <= x2 and xy[1] >= y1 and xy[1] <= y2:
		return 1
	return 0

def mouse_handler_move(xy):
	global cur_button
	#up arrow:
	if mouse_over(xy, g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3,
		g.tilesize*g.main.mapsizex/4+g.buttons["loadgame_up.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+g.buttons["loadgame_up.png"].get_height()):
		cur_button = 2

	#down arrow:
	if mouse_over(xy, g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+140-g.buttons["loadgame_down.png"].get_height(),
		g.tilesize*g.main.mapsizex/4+g.buttons["loadgame_down.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140):
		cur_button = 3

	#load button:
	if mouse_over(xy, g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+140,
		g.tilesize*g.main.mapsizex/4+g.buttons["load.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140+g.buttons["load.png"].get_height()):
		cur_button = 0

	#leave button:
	if mouse_over(xy,
		g.tilesize*g.main.mapsizex/4+g.buttons["load.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140,
		g.tilesize*g.main.mapsizex/4+g.buttons["load.png"].get_width()+
		g.buttons["quit.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140+g.buttons["quit.png"].get_height()):
		cur_button = 1
	refresh_buttons()

def mouse_handler_down(xy):
	global cur_button
	global module_pos
	#up arrow:
# 	if mouse_over(xy, g.tilesize*g.main.mapsizex/4,
# 		g.tilesize*g.main.mapsizey/3,
# 		g.tilesize*g.main.mapsizex/4+g.buttons["loadgame_up.png"].get_width(),
# 		g.tilesize*g.main.mapsizey/3+g.buttons["loadgame_up.png"].get_height()):
	if cur_button == 2:
		tmp = module_pos - (module_pos % 5) - 5
		if tmp < 0:
			module_pos = len(array_mods) - (len(array_mods)%5) + (module_pos%5)
			if module_pos >= len(array_mods):
				module_pos = len(array_mods) - 1
		else:
			module_pos -= 5
		refresh_module_info()

	#down arrow:
# 	if mouse_over(xy, g.tilesize*g.main.mapsizex/4,
# 		g.tilesize*g.main.mapsizey/3+140-g.buttons["loadgame_down.png"].get_height(),
# 		g.tilesize*g.main.mapsizex/4+g.buttons["loadgame_down.png"].get_width(),
# 		g.tilesize*g.main.mapsizey/3+140):
	if cur_button == 3:
		tmp = module_pos - (module_pos % 5) + 5
		if tmp >= len(array_mods):
			module_pos = (module_pos % 5)
		else:
			module_pos += 5
			if module_pos >= len(array_mods):
				module_pos = len(array_mods) - 1
		refresh_module_info()

	#load button:
	if mouse_over(xy, g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+140,
		g.tilesize*g.main.mapsizex/4+g.buttons["load.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140+g.buttons["load.png"].get_height()):
		key_handler(pygame.K_RETURN)

	#leave button:
	if mouse_over(xy,
		g.tilesize*g.main.mapsizex/4+g.buttons["load.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140,
		g.tilesize*g.main.mapsizex/4+g.buttons["load.png"].get_width()+
		g.buttons["quit.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140+g.buttons["quit.png"].get_height()):
		key_handler(pygame.K_RETURN)

	#save "listbox"
	if mouse_over(xy,
		g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+g.buttons["loadgame_up.png"].get_height(),
		g.tilesize*g.main.mapsizex/4+g.buttons["loadgame_up.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140-g.buttons["loadgame_down.png"].get_height()):

		base_y = (xy[1] -
			g.tilesize*g.main.mapsizey/3+g.buttons["loadgame_up.png"].get_height())
		base_y -= 40
		if base_y % 20 < 2 or base_y % 20 > 18: return
		tmp = module_pos - (module_pos % 5) + (base_y / 20)
		if tmp >= len(array_mods): return
		else: module_pos = tmp
		refresh_module_info()

def mouse_handler_double(xy):
	global module_pos
	#save "listbox"
	if mouse_over(xy,
		g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+g.buttons["loadgame_up.png"].get_height(),
		g.tilesize*g.main.mapsizex/4+g.buttons["loadgame_up.png"].get_width(),
		g.tilesize*g.main.mapsizey/3+140-g.buttons["loadgame_down.png"].get_height()):

		sel_list_mod()

def refresh_buttons():
	g.unclean_screen = True
	up_pic = "loadgame_up.png"
	down_pic = "loadgame_down.png"
	load_pic = "load.png"
	quit_pic = "quit.png"
	if (cur_button == 0): load_pic = "load_sel.png"
	elif (cur_button == 1): quit_pic = "quit_sel.png"
	elif (cur_button == 2): up_pic = "loadgame_up_sel.png"
	else: down_pic = "loadgame_down_sel.png"
	g.screen.blit(g.buttons[up_pic], (g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3))
	g.screen.blit(g.buttons[down_pic], (g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+140-g.buttons["loadgame_down.png"].get_height()))
	g.screen.blit(g.buttons[load_pic], (g.tilesize*g.main.mapsizex/4,
		g.tilesize*g.main.mapsizey/3+140))
	g.screen.blit(g.buttons[quit_pic], (g.tilesize*g.main.mapsizex/4+
		g.buttons["load.png"].get_width(), g.tilesize*g.main.mapsizey/3+140))


def init_window():
#	g.window_main.protocol("WM_DELETE_WINDOW", quit_game)
	global array_mods
	array_mods = listdir("../modules/")

	#remove CVS directory
	i = 0
	while i < len(array_mods):
		if array_mods[i] == "CVS":
			array_mods.pop(i)
		elif array_mods[i] == "default":
			array_mods.pop(i)
		else:
			i += 1

	g.screen.fill(g.colors["purple"])
# 	g.main.canvas_map = Canvas(g.window_main, width=g.tilesize*g.main.mapsizex,
# 		height=g.tilesize*g.main.mapsizey, highlightthickness=0,
# 		background="#606090")
# 	g.main.canvas_map.grid(column=0, row=0)

	g.load_buttons()

	#if there is only one module, run it.
	if len(sys.argv) > 1:
		sys.argv.pop(0)
		for arg in sys.argv:
			if arg.strip().lower() == "-debug":
				g.debug = True
				print "Activating debug mode"
			elif arg.strip().lower() == "-faststart":
				g.faststart = True
				print "Activating faststart mode"
			else:
				try:
					mod_loc = array_mods.index(arg)
				except ValueError:
					print "Unknown module: " + arg
					return 0
				sel_mod(array_mods[mod_loc])
				return 0
	if (len(array_mods) == 1):
		sel_mod(array_mods[0])
		return 0

	#global window_sel_game

	#g.window_main.title("Select module")
	pygame.display.set_caption("Select module")
	g.mod_directory = "../modules/default/"


# 	window_sel_game.resizable(0, 0)
# 	window_sel_game.maxsize(900, 900)
# 	window_sel_game.wm_geometry("+%d+%d" % (20, 20))

	#black bar
	g.create_norm_box((0, g.tilesize*g.main.mapsizey/2),
		(g.tilesize*g.main.mapsizex, 30), inner_color="black")
# 	g.main.canvas_map.create_rectangle(0,
# 		g.tilesize*g.main.mapsizey/2,
# 		g.tilesize*g.main.mapsizex,
# 		g.tilesize*g.main.mapsizey/2+30,
# 		fill="#000000", tags="loadgame")
	g.print_string(g.screen,
		"You have multiple modules installed. Pick one to play.", g.font,
		(g.tilesize*g.main.mapsizex/2+10, g.tilesize*g.main.mapsizey/2+15),
		color=g.colors["white"])
# 	g.main.canvas_map.create_text(g.tilesize*g.main.mapsizex/2,
# 		g.tilesize*g.main.mapsizey/2+15,
# 		text="You have multiple modules installed. Pick one to play.",
# 		anchor=W, tags=("module"), fill="#FFFFFF")

	#box for listbox
	g.create_norm_box((g.tilesize*g.main.mapsizex/4-2,
		g.tilesize*g.main.mapsizey/3-2), (g.buttons["loadgame_up.png"].get_width()+4,
		140+g.buttons["load.png"].get_height()+4))

	refresh_module_info()
	refresh_buttons()
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		if g.break_one_loop > 0:
			g.break_one_loop -= 1
			return
		for event in pygame.event.get():
			if event.type == pygame.QUIT: return
			elif event.type == pygame.KEYDOWN:
				key_handler(event.key)
			elif event.type == pygame.MOUSEMOTION:
				mouse_handler_move(event.pos)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				mouse_handler_move(event.pos)
				mouse_handler_down(event.pos)
		tmpjoy=g.run_joystick()
		if tmpjoy != 0:
			if tmpjoy != g.bindings["left"] and tmpjoy != g.bindings["right"]:
				global cur_button
				if cur_button != 0:
					cur_button = 0
					refresh_buttons()
				key_handler(tmpjoy)

		if g.unclean_screen:
			g.unclean_screen = False
			pygame.display.flip()

# 	g.window_main.mainloop()

init_window()
