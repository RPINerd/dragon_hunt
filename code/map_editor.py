#file: map_editor.py
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

# This file runs a map editing program.
# Author: Allison Marles
# Date: Sept.1, 2004

#from Tkinter import *
#needed for the tiles.
#import ImageTk
#import Image
import pygame
#import re
import os
import sys
#import tkMessageBox
import re

pygame.init()
pygame.font.init()

#window = Toplevel()
#window.master.withdraw()
#window.title("Map Editor")

import g
import scripting
import listbox
import scrollbar

pygame.display.set_caption("Map Editor")

g.screen_size = g.editor_xy
g.screen = pygame.display.set_mode(g.screen_size)

mapsize_x =25
mapsize_y =25

portal_x = 0
portal_y = 0
portalsize = g.editor_tilesize

cur_tilecopy_x = 0
cur_tilecopy_y = 0

bgcolour='lightgrey'

cur_tile = ""
cur_tile_num = 0
cur_mode = "replace"
border = "rock.png"
background = "grass.png"
map_name = "map.txt"
tile_set_size = 0
tilebox_width = 4
tilegrid = 0 #whether or not to display the map grid
cur_map = "" #this will normally be a g.map class.
global dirnames
dirnames = []
#all possible items so we can make unique variables for each one
global item_list
item_list = {"blank": 4}

#create a new map. Set mapsize_* first.
def create_map():

	#this creates the actual map.
	global cur_map
	cur_map = g.map("")
	#g.maps.append(g.map(map_name))
	#g.zgrid = len(g.maps) -1

	cur_map.field.append([])
	for y in range(mapsize_x): #upper border
		cur_map.field[0].append(g.tile(""))
		cur_map.field[0][len(cur_map.field[0])-1].onload.append("pix(\""+border+"\")")
		cur_map.field[0][len(cur_map.field[0])-1].onload.append("walk(0)")

	for x in range(mapsize_y-2):
		cur_map.field.append([])
		cur_map.field[x+1].append(g.tile("")) #left border
		cur_map.field[x+1][0].onload.append("pix(\""+border+"\")")
		cur_map.field[x+1][0].onload.append("walk(0)")
		for y in range(mapsize_x - 2):
			cur_map.field[x+1].append(g.tile("")) #inside
			cur_map.field[x+1][len(cur_map.field[x+1])-1].onload.append("pix(\""+background+"\")")
			cur_map.field[x+1][len(cur_map.field[x+1])-1].onload.append("walk(1)")
		cur_map.field[x+1].append(g.tile("")) #right border
		cur_map.field[x+1][len(cur_map.field[x+1])-1].onload.append("pix(\""+border+"\")")
		cur_map.field[x+1][len(cur_map.field[x+1])-1].onload.append("walk(0)")

	cur_map.field.append([])
	map_len = len(cur_map.field)-1
	for y in range(mapsize_x):
		cur_map.field[map_len].append(g.tile("")) #lower border
		cur_map.field[map_len][len(cur_map.field[map_len])-1].onload.append("pix(\""+border+"\")")
		cur_map.field[map_len][len(cur_map.field[map_len])-1].onload.append("walk(0)")

	global portal_x
	global portal_y
	portal_x = 0
	portal_y = 0

	refresh_map()
# 	scroll_from_map()

def move_up(dist=1):
	global portal_y
	portal_y -= dist
	if portal_y < 0:
		portal_y = 0
	refresh_map()

def move_down(dist=1):
	global portal_y
	portal_y += dist
	if portal_y + portalsize > mapsize_y:
		portal_y =  mapsize_y - portalsize
	if portal_y < 0:
		portal_y = 0
	refresh_map()

def move_left(dist=1):
	global portal_x
	portal_x -= dist
	if portal_x < 0:
		portal_x = 0
	refresh_map()

def move_right(dist=1):
	global portal_x
	portal_x += dist
	if portal_x + portalsize > mapsize_x:
		portal_x = mapsize_x - portalsize
	if portal_x < 0:
		portal_x = 0
	refresh_map()

def click_map(xy):
	if(cur_tile != "" or cur_mode == "remove" or cur_mode == "walkable"
			or cur_mode == "scripting" or cur_mode == "scripting2"):
		set_tile((xy[0] / g.tilesize)+portal_x, (xy[1] / g.tilesize)+portal_y, cur_tile)

#set mode to add, replace, remove, or walkable
def set_mode(mode):
	global cur_mode
	cur_mode = mode
	refresh_map()

#set all interior tiles to background tile
def set_bkg(bkg):
	global background
	background = bkg
	for y in range(mapsize_y-2):
		for x in range(mapsize_x - 2):
			cur_map.field[y+1][x+1].onload = []
			cur_map.field[y+1][x+1].onload.append("pix(\""+bkg+"\")")
			cur_map.field[y+1][x+1].onload.append("walk(1)")
	refresh_map()

#what will appear around edges of map (must be walk 0 to keep hero penned in)
def set_border(edge):
	global border
	border = edge
	for y in range(mapsize_y):
		cur_map.field[y][0].onload = []
		cur_map.field[y][0].onload.append("pix(\""+edge+"\")")
		cur_map.field[y][0].onload.append("walk(0)")
		temp_len = len(cur_map.field[y])-1
		cur_map.field[y][temp_len].onload = []
		cur_map.field[y][temp_len].onload.append("pix(\""+edge+"\")")
		cur_map.field[y][temp_len].onload.append("walk(0)")
	for x in range(mapsize_x):
		cur_map.field[0][x].onload = []
		cur_map.field[0][x].onload.append("pix(\""+edge+"\")")
		cur_map.field[0][x].onload.append("walk(0)")
		temp_len = len(cur_map.field)-1
		cur_map.field[temp_len][x].onload = []
		cur_map.field[temp_len][x].onload.append("pix(\""+edge+"\")")
		cur_map.field[temp_len][x].onload.append("walk(0)")

	refresh_map()

global last_xy
last_xy = (0, 0)
def print_cur_xy(xy, ignore_and_force=False):
	global last_xy
	if ignore_and_force:
		xy = last_xy
	if last_xy != xy or ignore_and_force:
		g.screen.fill(g.colors["black"], (g.screen_size[0]-100,
			g.screen_size[1]-30, 100, 12))
		g.print_string(g.screen, cur_mode +"  "+str(xy[0])+", "+str(xy[1]), g.font,
			(g.screen_size[0]-3, g.screen_size[1]-30),
				color=g.colors["white"], align=2)
		last_xy = xy
		g.unclean_screen = True


#refresh map. This refreshes every tile, as accuracy is rather important here.
#(compared to the main game)
def refresh_map():
	g.screen.fill(g.colors["black"])
#	canvas_map.delete(ALL)
	for y in range(portal_y, portal_y+portalsize):
		if y >= mapsize_y: break
		for x in range(portal_x, portal_x+portalsize):
			if x >= mapsize_x: break
			try:
				for line in cur_map.field[y][x].onload:
					line=line.strip()
					if line == "": continue
					if line[:3].lower() == "pix" or line[:6].lower() == "addpix" \
							or line[:10].lower() == "addoverpix":
						g.screen.blit(g.tiles[line[
							line.find("(")+2:g.action.match_command(line)-2]],
							((x-portal_x)*g.tilesize, (y-portal_y)*g.tilesize))
			except IndexError:
				print "Crash prevention: ", x, y, len(cur_map.field)
	#If we are adjusting walkable status, display black/white box on tile.
	#White for walkable, Black for non. Note that if the walkable status
	#depends on an if statement, this may have incorrect results. (No good
	#way to fix this, though.)
	if cur_mode == "walkable":
		for y in range(portal_y, portal_y+portalsize):
			if y >= mapsize_y: break
			for x in range(portal_x, portal_x+portalsize):
				if x >= mapsize_x: break
				for line in cur_map.field[y][x].onload:
					line=line.strip().lower()
					if line == "walk(1)":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + g.tilesize/3,
							(y-portal_y)*g.tilesize + g.tilesize/3),
							(g.tilesize/3, g.tilesize/3), inner_color="white")
					if line == "walk(0)":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + g.tilesize/3,
							(y-portal_y)*g.tilesize + g.tilesize/3),
							(g.tilesize/3, g.tilesize/3), inner_color="black")
					#The wall_* display. Show a black bar on the given side.
					if line == "wall_n(1)":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + g.tilesize/8,
							(y-portal_y)*g.tilesize + 2),
							(7*g.tilesize/8, 5), "white", "black")
					if line == "wall_s(1)":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + g.tilesize/8,
							(y-portal_y)*g.tilesize +g.tilesize-7),
							(7*g.tilesize/8, 5), "white", "black")
					if line == "wall_w(1)":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + 2,
							(y-portal_y)*g.tilesize +g.tilesize/8),
							(5, 7*g.tilesize/8), "white", "black")
					if line == "wall_e(1)":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + g.tilesize-7,
							(y-portal_y)*g.tilesize +g.tilesize/8),
							(5, 7*g.tilesize/8), "white", "black")
	#If the tiles have some scripting, display a black-bordered white square.
	#(To make sure it displays well on all tiles.)
	#This ignores the pix and walk commands that all tiles must have.
	if cur_mode == "scripting" or cur_mode == "scripting2":
		for y in range(portal_y, portal_y+portalsize):
			if y >= mapsize_y: break
			for x in range(portal_x, portal_x+portalsize):
				if x >= mapsize_x: break
				draw_boxes = 0
				for line in cur_map.field[y][x].onload:
					temp_command = line.strip()[:3].lower()
					if temp_command != "wal" and temp_command != "pix":
						g.create_norm_box((
							(x-portal_x)*g.tilesize + g.tilesize/3,
							(y-portal_y)*g.tilesize + g.tilesize/3),
							(g.tilesize/3, g.tilesize/3), inner_color="white")
				if len(cur_map.field[y][x].actions) > 0:
					g.create_norm_box((
						(x-portal_x)*g.tilesize + g.tilesize/3+2,
						(y-portal_y)*g.tilesize + g.tilesize/3+2),
						(g.tilesize/3-4, g.tilesize/3-4), inner_color="white")
					g.screen.fill(g.colors["black"], ((x-portal_x)*g.tilesize + g.tilesize/2-2,
						(y-portal_y)*g.tilesize + g.tilesize/2-2,
						2, 2))
	if cur_mode == "tilecopy":
		for y in range(portal_y, portal_y+portalsize):
			if y >= mapsize_y: break
			for x in range(portal_x, portal_x+portalsize):
				if x >= mapsize_x: break
				if x == cur_tilecopy_x and y == cur_tilecopy_y:
					g.create_norm_box((
						(x-portal_x)*g.tilesize + g.tilesize/3+2,
						(y-portal_y)*g.tilesize + g.tilesize/3+2),
						(g.tilesize/3-4, g.tilesize/3-4), inner_color="white")
	#grid display
	if tilegrid == 1:
		for y in range(portalsize):
			g.screen.fill(g.colors["black"], (0, y*g.tilesize,
				portalsize*g.tilesize, 1))
		for x in range(portalsize):
			g.screen.fill(g.colors["black"], (x*g.tilesize, 0,
				1, portalsize*g.tilesize))

	g.unclean_screen = True

	#scrollbars
	scroll_length = g.screen_size[1]-2
	g.create_norm_box((0, scroll_length-1), (scroll_length, 4))
	g.create_norm_box(((scroll_length*portal_x)/mapsize_x,
		scroll_length-1), ((scroll_length*portalsize)/mapsize_x, 4),
		 inner_color="ep_blue")
	g.create_norm_box((scroll_length-1, 0), (4, scroll_length))
	g.create_norm_box((scroll_length-1, (scroll_length*portal_y)/mapsize_y),
		(4, (scroll_length*portalsize)/mapsize_y),
		 inner_color="ep_blue")

	make_menus()
	display_tiles()

#set tile at x, y to name.
def set_tile(x, y, name):
	if x >= mapsize_x: return
	if y >= mapsize_y: return

	#if the tile is an item, add it to the current tile
	tile_prefix = name.split("/", 1)[0]
	if tile_prefix == "items" and cur_mode != "remove":
		add_item(x, y, name)
	elif cur_mode == "add":
		cur_map.field[y][x].onload.append("addpix(\""+name+"\")");
	elif cur_mode == "addover":
		cur_map.field[y][x].onload.append("addoverpix(\""+name+"\")");
	elif cur_mode == "remove":
		cur_map.field[y][x].onload = []
		cur_map.field[y][x].onload.append("pix(\""+background+"\")")
		cur_map.field[y][x].onload.append("walk(1)")
	elif cur_mode == "walkable":
		for line_num in range(len(cur_map.field[y][x].onload)):
			if cur_map.field[y][x].onload[line_num] == "walk(1)":
				cur_map.field[y][x].onload[line_num] = "walk(0)"
			elif cur_map.field[y][x].onload[line_num] == "walk(0)":
				cur_map.field[y][x].onload[line_num] = "walk(1)"
	elif cur_mode == "scripting":
		change_scripting(x, y, 0)
	elif cur_mode == "scripting2":
		change_scripting(x, y, 1)
	elif cur_mode == "tilecopy":
		if pygame.key.get_mods() & pygame.KMOD_SHIFT:
			global cur_tilecopy_x
			global cur_tilecopy_y
			cur_tilecopy_x = x
			cur_tilecopy_y = y
		else:
			copy_tile(cur_map.field[y][x],
					cur_map.field[cur_tilecopy_y][cur_tilecopy_x])
	else:
		temp_name = name
		for line_num in range(len(cur_map.field[y][x].onload)):
			if cur_map.field[y][x].onload[line_num][:3].strip().lower() == "pix":
				cur_map.field[y][x].onload[line_num] = "pix(\""+name+"\")"
				temp_name = name
		for line_num in range(len(cur_map.field[y][x].onload)):
			if cur_map.field[y][x].onload[line_num][:4].strip().lower() == "walk":
				try: cur_map.field[y][x].onload[line_num] = "walk("+walk_vals[temp_name]+")"
				#default to walkable.
				except KeyError: cur_map.field[y][x].onload[line_num] = "walk(1)"
	refresh_map()

#add name item to tile at x, y
def add_item(x, y, name):
	tmp = g.main.ask_for_string("Amount of item? (examples: 5, a)")
	if tmp == -1:
		refresh_map()
		return
	amount = tmp
	item = name.split("/", 1)[1]
	item = item[0:len(item)-4]
	item_name = re.sub("_", " ", item)
	var_name = item + "_" + map_name + "_" + str(item_list[name])
	item_list[name] += 1
	cur_map.field[y][x].onload.append("if(var(\""+var_name+"\"), \"=\", 0)")
	cur_map.field[y][x].onload.append("	addpix(\""+name+"\")")
	cur_map.field[y][x].onload.append("endif")
	cur_map.field[y][x].actions.append("if(var(\""+var_name+"\"), \"=\", 0)")
	cur_map.field[y][x].actions.append("	if(find(\""+item_name+"\", \""+amount+"\"), \"=\", 1)")
	cur_map.field[y][x].actions.append("		set(\""+var_name+"\", \"=\", 1)")
	cur_map.field[y][x].actions.append("		delpix(\""+name+"\")")
	cur_map.field[y][x].actions.append("	endif")
	cur_map.field[y][x].actions.append("endif")


#given the x,y coords of the current tile, will display the onload and action
#lines of the tile, and allow for editing.
#BUGGED
def change_scripting(x, y, modetype):
	scripting_list = []
	if modetype == 0:
		for line in cur_map.field[y][x].onload:
			scripting_list.append(line)
	elif modetype == 1:
		for line in cur_map.field[y][x].actions:
			scripting_list.append(line)
	scripting_list.append("")

	editor = ""
	if os.environ.has_key("EDITOR"): editor = os.environ["EDITOR"]
	if os.environ.has_key("DH_EDITOR"): editor = os.environ["DH_EDITOR"]
	if editor != "":
		for line_num in range(len(scripting_list)):
			scripting_list[line_num] += "\n"
		tmp_file = open("temp_editor_script.txt", 'w')
		tmp_file.writelines(scripting_list)
		tmp_file.close()
		tmp = os.spawnlp(os.P_WAIT, editor, editor, "temp_editor_script.txt")
		tmp_file = open("temp_editor_script.txt", 'r')
		scripting_list = []
		while 1:
			tmp_line = tmp_file.readline()
			if tmp_line == "": break
			if tmp_line[-1] == "\n": tmp_line = tmp_line[:-1]
			scripting_list.append(tmp_line)


	while 1:
		if editor != "": break
		tmp = select_from_list(scripting_list, False, True, True)
		if tmp == -1: break
		if tmp >= len(scripting_list):
			tmp = g.main.ask_for_string("New line?")
			if tmp != -1 and tmp.strip() != "":
				scripting_list.append(tmp)
		else:
			tmp2 = g.main.ask_for_string("Change line... (change to --- to"+
				" insert a line).",
				textbox_text=scripting_list[tmp])
			if tmp2 != -1:
				if tmp2 == "---":
					scripting_list.insert(tmp, "")
				else:
					scripting_list[tmp] = tmp2
	for i in range(len(scripting_list)-1, -1, -1):
		if scripting_list[i].strip() == "":
			scripting_list.pop(i)
		else: break
	if modetype == 0:
		cur_map.field[y][x].onload = []
		for line in scripting_list:
			cur_map.field[y][x].onload.append(line)
	elif modetype == 1:
		cur_map.field[y][x].actions = []
		for line in scripting_list:
			cur_map.field[y][x].actions.append(line)


#Given xy coords, and the scripting for a tile, each line separated by \n,
#set the tile data.
def really_change_scripting(x, y, onload, action):
	onload_array = onload.split("\n")
	action_array = action.split("\n")
	cur_map.field[y][x].onload = []
	for line in onload_array:
		if line != "":
			cur_map.field[y][x].onload.append(line)
	cur_map.field[y][x].actions = []
	for line in action_array:
		if line != "":
			cur_map.field[y][x].actions.append(line)
	close_scripting_window()



	scrollleft = float(portal_x)/mapsize_x
	scrollright = float((portal_x+portalsize))/mapsize_x
# 	x_scroll.set(scrollleft, scrollright)

#this loads the various tiles.
def load_tiles():
	global tiles
	tiles = {"blank" : pygame.Surface((32, 32))}
	global tilenames
	tilenames= []
	global num_tiles
	num_tiles = 0

	for root, dirs, files in os.walk(g.mod_directory + "/images/tiles/"):
		(head, tail) = os.path.split(root)
		if (tail != "CVS"):
			files.sort()
			for tilename in files:
				num_tiles = num_tiles + 1
				#if image is in a sub-dir:
				if (root != g.mod_directory + "/images/tiles/"):
					i = len(g.mod_directory + "/images/tiles/")
					tilenames.append(root[i:] + "/" + tilename)
					tiles[root[i:] + "/" + tilename] = \
					pygame.image.load(root + "/" + tilename).convert_alpha()
				else: #if image is in root dir
					tilenames.append(tilename)
					tiles[tilename] = \
						pygame.image.load(root + "/" + tilename).convert_alpha()
	get_walk_values()

def get_walk_values():
	global walk_vals
	walk_vals = {"blank" : 0}
	walk_defs_loc = g.mod_directory + "/data/" + "walk_defs.txt"
	walk_defs = open(walk_defs_loc, 'r')
	#read lines, store in walk[tilename] = 1 or 0
	walk_line = walk_defs.readline()
	while walk_line != '' and walk_line[:1] != ":":
		#strip out leading and trailing whitespace
		walk_line = walk_line.strip()

		#ignore blank lines and comments
		if walk_line[:1] == "#" or walk_line[:1] == "" or walk_line[:1] == "\n":
			walk_line = walk_defs.readline()
			continue

		#add the line
		line = walk_line.split(" ")
		walk_vals[line[0]] = line[1]

		#ready another line
		walk_line = walk_defs.readline()


def set_codes():
	global codes
	codes = []
	#This gives me a few thousand (3844) distinct tiles per map.
	for i in  "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
		for j in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
			codes.append(i + j)

#set current tile to work with
def choose_tile(file, num):
	global cur_tile
	global cur_tile_num
	cur_tile = file
	cur_tile_num = num
	display_tiles()

#set up tile
def setup_tilebox():
	#this creates the tile display portion
	global tilebox
	tilebox = []

def click_tiles(xy):
	if xy[0] < g.screen_size[0]-(tilebox_width)*(g.tilesize+1):
		return 0
	else:
		global cur_tile_num
		global cur_tile
		tmp = cur_tile_num
		x = xy[0] - (g.screen_size[0]-(tilebox_width)*(g.tilesize+1))
		cur_tile_num = x/(g.tilesize+1) + tilebox_width*(xy[1]/(g.tilesize+1))
		tmp_dir = cur_tile_set
		if tmp_dir == "default": tmp_dir = ""
		i = 0
		j = 0
		for tile_name in tilenames:
			tmp_name = tile_name.split("/")[0]
			if tmp_name[-4:] == ".png":
				tmp_name = ""
			if (tmp_dir == tmp_name):
				if j == cur_tile_num:
					cur_tile = tilenames[i]
				j += 1
			i += 1
		if tmp != cur_tile_num:
			display_tiles()
			return 2
		return 1

# show tile set as buttons
def display_tiles(set = ""):
	global cur_tile_set
	global cur_tile
	cur_tile = ""
	if set != "":
		cur_tile_set = set
	else:
		try:
			set = cur_tile_set
		except NameError:
			set = cur_tile_set = "default"
	cur_row = 0
	col_start = mapsize_x+1
	col_span = tilebox_width
	cur_col = 0
	cur = 0
	global tile_set_size
	tile_set_size = 0
	g.screen.fill(g.colors["black"],
		(g.screen_size[0]-(tilebox_width)*(g.tilesize+1)-1, 0,
		(tilebox_width)*(g.tilesize+1)+1, g.screen_size[1]))

	for file in tilenames:
		file_prefix = file.split("/", 1)[0]
		end_in_png = file_prefix[len(file_prefix)-4:len(file_prefix)]
		#if not in a sub-dir, then this tile is in default set
		if(end_in_png == ".png"):
			file_prefix = "default"

		#only show tiles in appropriate set (ie. correct subdir)
		if(file_prefix == set):
			tile_set_size = tile_set_size + 1
			if cur_col == col_span:
				cur_row = cur_row + 1
				cur_col = 0
			if cur_tile_num == cur_col + tilebox_width*cur_row:
				g.screen.fill(g.colors["hp_red"], (g.screen_size[0]-
				(col_span-cur_col)*(g.tilesize+1)-1,
				cur_row*(g.tilesize+1)-1, g.tilesize+2, g.tilesize+2))
				cur_tile = file
			g.screen.blit(tiles[file],
				(g.screen_size[0]-(col_span-cur_col)*(g.tilesize+1),
				cur_row*(g.tilesize+1)))
			cur_col = cur_col + 1
			cur = cur + 1
	g.print_string(g.screen, cur_tile.split("/")[-1], g.font, (g.screen_size[0]-4,
		g.screen_size[1]-18), color=g.colors["white"], align=2)


def check_repeat_tile(x, y):
	for in_y in range(y):
		for in_x in range(mapsize_x): #for each previous tile.
			if tiles_equal(cur_map.field[y][x], cur_map.field[in_y][in_x]) == 1:
				cur_map.field[y][x].name = cur_map.field[in_y][in_x].name
				return 1
	for in_x in range(x):
		if tiles_equal(cur_map.field[y][x], cur_map.field[y][in_x]) == 1:
			cur_map.field[y][x].name = cur_map.field[y][in_x].name
			return 1
	return 0

#save map to map dir
def save_map():
	set_codes()
	map_loc = g.mod_directory + "/data/maps/" + map_name
	print "Saving map to " + map_loc
	try: os.rename(map_loc, map_loc+"~")
	except OSError: pass
	map_file = open(map_loc, 'w')
	count = 0
	for y in range(mapsize_y):
		for x in range(mapsize_x): #for each tile
			try:
				if(check_repeat_tile(x, y) == 0): #if tile was not repeated
					cur_map.field[y][x].name = codes[count]
					count += 1
			except IndexError:
					print "Crash prevention:", x, y
					return

	for y in range(mapsize_y):
		string = ""
		for x in range(mapsize_x): #for each tile
			string += cur_map.field[y][x].name + " "
		map_file.write(string + "\n")

	map_file.write("\n:def\n")
	for monster_name in cur_map.monster:
		map_file.write("monster=" + monster_name + "\n")
	if cur_map.battle_background_name != "":
		map_file.write("battle_bg=" + cur_map.battle_background_name + "\n")
	if cur_map.hero_suffix != "":
		map_file.write("hero_bg=" + cur_map.hero_suffix + "\n")
	if cur_map.under_level != "":
		map_file.write("level_under=" + cur_map.under_level + "\n")
	if cur_map.left_level != "":
		map_file.write("level_left=" + cur_map.left_level + "\n")
	if cur_map.right_level != "":
		map_file.write("level_right=" + cur_map.right_level + "\n")
	if cur_map.down_level != "":
		map_file.write("level_down=" + cur_map.down_level + "\n")
	if cur_map.up_level != "":
		map_file.write("level_up=" + cur_map.up_level + "\n")

	if cur_map.downleft_level != "":
		map_file.write("level_downleft=" + cur_map.downleft_level + "\n")
	if cur_map.upleft_level != "":
		map_file.write("level_upleft=" + cur_map.upleft_level + "\n")
	if cur_map.upright_level != "":
		map_file.write("level_upright=" + cur_map.upright_level + "\n")
	if cur_map.downright_level != "":
		map_file.write("level_downright=" + cur_map.downright_level + "\n")


	for tile_type in range(count): #for each tile type.
		map_file.write(":" + codes[tile_type] + "\n")
		for y in range(mapsize_y): #Find an example of that tile.
			for x in range(mapsize_x):
				if cur_map.field[y][x].name == codes[tile_type]:
					for onload_line in cur_map.field[y][x].onload:
						map_file.write(onload_line + "\n")
					if len(cur_map.field[y][x].actions) > 0:
						map_file.write("Action\n")
					for actions_line in cur_map.field[y][x].actions:
						map_file.write(actions_line + "\n")
					break
			else: continue #bit confusing here; this breaks out of both loops
			break          #when the tile is found.

	map_file.close()

	g.zgrid = g.mapname2zgrid(cur_map.name)
	copy_map(g.maps[g.zgrid], cur_map)
	try: os.remove(map_loc+"~")
	except OSError: pass

#loads the loadmap window, then loads the returned map into cur_map.
def do_load_map():
	array_maps = os.listdir(g.mod_directory + "/data/maps/")
	array_maps.sort()
	#remove CVS directory
	i = 0
	while i < len(array_maps):
		if array_maps[i] == "CVS":
			array_maps.pop(i)
		else:
			i += 1
	tmp = select_from_list(array_maps)
	if tmp == -1:
		refresh_map()
		return
	g.print_string(g.screen, "Loading", g.font, (250, 150), g.colors["white"])
	pygame.display.flip()
	g.zgrid = g.mapname2zgrid(tmp)
	global cur_map
	cur_map = g.map("")
	#Rereading all the maps is a bit roundabout, but prevents a nasty bug.
	g.read_maps(1)
	copy_map(cur_map, g.maps[g.zgrid])
	global mapsize_x
	mapsize_x = len(cur_map.field[0])
	global mapsize_y
	mapsize_y = len(cur_map.field)
	global portal_x
	global portal_y
	portal_x = 0
	portal_y = 0
	pygame.display.set_caption("Map Editor: "+ cur_map.name)
	refresh_map()
# 	scroll_from_map()

#given input and output maps, copies the important parts.
def copy_map(output_map, input_map):
	output_map.name = input_map.name
	global map_name
	map_name = output_map.name
	for y in range(len(input_map.field)):
		output_map.field.append([])
		for x in range(len(input_map.field[y])):
			output_map.field[y].append(g.tile(""))
			copy_tile(output_map.field[y][x], input_map.field[y][x])
	for monster in input_map.monster:
		output_map.monster.append(monster)
	output_map.battle_background_name = input_map.battle_background_name
	output_map.hero_suffix = input_map.hero_suffix
	output_map.under_level = input_map.under_level

	output_map.left_level = input_map.left_level
	output_map.right_level = input_map.right_level
	output_map.up_level = input_map.up_level
	output_map.down_level = input_map.down_level

	output_map.upleft_level = input_map.upleft_level
	output_map.upright_level = input_map.upright_level
	output_map.downleft_level = input_map.downleft_level
	output_map.downright_level = input_map.downright_level


#given input and output tiles, copies the important parts.
def copy_tile(output_tile, input_tile):
	output_tile.walk = input_tile.walk
	output_tile.onload = []
	for line in input_tile.onload:
		output_tile.onload.append(line)
	output_tile.actions = []
	for line in input_tile.actions:
		output_tile.actions.append(line)

#given two tiles, return 1 if they are equal, 0 if not.
#Checks onload and actions.
def tiles_equal(tile1, tile2):
	if len(tile1.onload) != len(tile2.onload):
		return 0
	if len(tile1.actions) != len(tile2.actions):
		return 0
	for x in range(len(tile2.onload)):
		if tile1.onload[x] != tile2.onload[x]:
			return 0
	for x in range(len(tile2.actions)):
		if tile1.actions[x] != tile2.actions[x]:
			return 0
	return 1


#given x and y in tiles, resizes the map, destroying and creating tiles as needed.
def really_change_mapsize(x, y):
	global mapsize_x
	global mapsize_y
	mapsize_x = int(x)
	mapsize_y = int(y)
	if len(cur_map.field) > int(y):
		for tmpy in range(len(cur_map.field) - int(y)):
			cur_map.field.pop()
	elif len(cur_map.field) < int(y):
		for tmpy in range(int(y) - len(cur_map.field)):
			cur_map.field.append([])
	for tmpy in range(len(cur_map.field)):
		if len(cur_map.field[tmpy]) > int(x):
			for tmpx in range(len(cur_map.field[tmpy]) - int(x)):
				cur_map.field[tmpy].pop()
		elif len(cur_map.field[tmpy]) < int(x):
			for tmpx in range(int(x) - len(cur_map.field[tmpy])):
				cur_map.field[tmpy].append(g.tile(""))
				cur_map.field[tmpy][len(cur_map.field[tmpy])-1].onload.append(
						"pix(\"" + background+"\")")
				cur_map.field[tmpy][len(cur_map.field[tmpy])-1
						].onload.append("walk(1)")

	global portal_x
	global portal_y
	portal_x = 0
	portal_y = 0
	line = "Reset border and background for new map size ? "  \
		"(This will clear the contents of the map.)"
	if ask_yesno(line):
		set_border(border)
		set_bkg(background)
	refresh_map()

def ask_yesno(line=None):
	tmp_surface = pygame.Surface(g.screen_size)
	tmp_surface.blit(g.screen, (0, 0))
	tmp_answer = g.main.show_yesno(line)
	g.screen.blit(tmp_surface, (0, 0))
	g.unclean_screen = True
	return tmp_answer

def toggle_grid():
	global tilegrid
	if tilegrid == 0:
		tilegrid = 1
		#g.tilesize += 1
	elif tilegrid == 1:
		tilegrid = 0
		#g.tilesize -= 1
	refresh_map()

def quick_button(command_string, xy, size):
	g.create_norm_box(xy, size)
	g.print_string(g.screen, command_string, g.font, (xy[0]+2, xy[1]+1))
	g.unclean_screen = True

def make_menus():
	quick_button("File", (0,0), (25,14))
	quick_button("Tileset", (25,0), (35,14))
	quick_button("Map Settings", (60,0), (70,14))
	quick_button("Grid", (130,0), (45,14))
	pass

def click_menu(xy):
	if xy[0] > 175: return 0
	if xy[1] > 14: return 0
	if xy[0] < 25: return 1
	if xy[0] < 60: return 2
	if xy[0] < 130: return 3
	return 4

def select_from_list(input_array, act_as_menu=False, return_pos=False,
			extra_wide=False):
	cur_pos = 0
	while len(input_array) % 16 != 0 or len(input_array) == 0:
		input_array.append("")
	width =200
	if extra_wide: width =500
	input_listbox = listbox.listbox((10, 10), (width, 350),
		16, 1, g.colors["light_gray"], g.colors["dh_green"],
		g.colors["black"], g.colors["black"], g.font)
	input_scroll = scrollbar.scrollbar((width+10, 10), 350,
		16, g.colors["light_gray"], g.colors["hp_green"],
		g.colors["white"])

	g.screen.blit(g.buttons["load_sel.png"], (10, 360))
	g.screen.blit(g.buttons["quit.png"],
		(10+g.buttons["load_sel.png"].get_width(), 360))
	listbox.refresh_list(input_listbox, input_scroll, cur_pos, input_array)
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		if g.break_one_loop > 0:
			g.break_one_loop -= 1
			break
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				g.unclean_screen = True
				return -1
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					cur_pos -= 1
					if cur_pos < 0: cur_pos = 0
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				if event.key == pygame.K_PAGEUP:
					cur_pos -= 16
					if cur_pos < 0: cur_pos = 0
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				if event.key == pygame.K_DOWN:
					cur_pos += 1
					if cur_pos >= len(input_array): cur_pos=len(input_array)-1
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				if event.key == pygame.K_PAGEDOWN:
					cur_pos += 16
					if cur_pos >= len(input_array): cur_pos=len(input_array)-1
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				elif (event.key == pygame.K_RETURN or
						event.key == pygame.K_KP_ENTER):
					if return_pos: return cur_pos
					if input_array[cur_pos] != "":
						return input_array[cur_pos]
				elif event.key == pygame.K_HOME:
					cur_pos = 0
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				elif event.key == pygame.K_END:
					cur_pos = len(input_array) -1
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				elif event.key == pygame.K_ESCAPE:
					g.unclean_screen = True
					return -1
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					if event.pos[0] < 10 or event.pos[1] < 360:
						tmp = input_listbox.is_over(event.pos)
						if tmp != -1:
							cur_pos = (cur_pos/16)*16+tmp
							listbox.refresh_list(input_listbox, input_scroll,
								cur_pos, input_array)
							if act_as_menu:
								if return_pos: return cur_pos
								if input_array[cur_pos] != "":
									return input_array[cur_pos]
					elif event.pos[1] > 360+g.buttons["load_sel.png"].get_height():
						break
					elif event.pos[0] < 10+g.buttons["load_sel.png"].get_width():
						if return_pos: return cur_pos
						if input_array[cur_pos] != "":
							return input_array[cur_pos]
					elif (event.pos[0] < 10+g.buttons["load_sel.png"].get_width()+
							g.buttons["quit.png"].get_width()):
						g.unclean_screen = True
						return -1
				elif event.button == 4:
					cur_pos -= 1
					if cur_pos < 0: cur_pos = 0
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
				elif event.button == 5:
					cur_pos += 1
					if cur_pos >= len(input_array): cur_pos=len(input_array)-1
					listbox.refresh_list(input_listbox, input_scroll, cur_pos,
						input_array)
		if g.unclean_screen:
			pygame.display.flip()


def tile_dir_list(autoselect=-1):
	global cur_tile_set
	list_of_dirs = []
	cur_dir = 0
	for root, dirs, files in os.walk(g.mod_directory + "/images/tiles/"):
		(head, tail) = os.path.split(root)
		if (tail != "CVS"):
			if(tail == ""):
				list_of_dirs.append("default")
			else:
				list_of_dirs.append(tail)

	if autoselect != -1:
		if len(list_of_dirs) > autoselect:
			tmp = list_of_dirs[autoselect]
		else: return
	else:
		tmp = select_from_list(list_of_dirs)
		if tmp == -1:
			refresh_map()
			return
	cur_tile_set = tmp
	display_tiles(tmp)
	refresh_map()


def change_portal(size):
	global portalsize
	portalsize = size
	refresh_map()

def main_menu():
	list_of_opts = ["New", "Rename", "Load", "Save", "Quit"]
	tmp = select_from_list(list_of_opts, True)
	if tmp == -1:
		refresh_map()
		return
	if tmp == "New":
		create_map()
	if tmp == "Rename":
		global map_name
		tmp = g.main.ask_for_string("Name of map?", map_name)
		if tmp == -1:
			refresh_map()
			return
		map_name = tmp
		cur_map.name = tmp
	if tmp == "Load":
		do_load_map()
	elif tmp == "Save":
		save_map()
	elif tmp == "Quit":
		if ask_yesno("Quit the editor?"):
			sys.exit()
	refresh_map()

def map_menu():
	list_of_opts = ["Map Mode", "Map Size", "Background", "Border", "Monsters",
		"Battle Background"]
	tmp = select_from_list(list_of_opts, True)
	if tmp == -1:
		refresh_map()
		return
	if tmp == "Map Mode":
		list_of_opts = ["Replace Tile (default)", "Add Tile (transparency)",
			"Reset Tile (clear to background)", "Adjust walkable status",
			"Edit Onload", "Edit Action", "Add Overtile", "Copy Tile"]
		tmp = select_from_list(list_of_opts, True)
		if tmp == -1:
			refresh_map()
			return
		if tmp == "Replace Tile (default)": set_mode("replace")
		elif tmp == "Add Tile (transparency)": set_mode("add")
		elif tmp == "Reset Tile (clear to background)": set_mode("remove")
		elif tmp == "Adjust walkable status": set_mode("walkable")
		elif tmp == "Edit Onload": set_mode("scripting")
		elif tmp == "Edit Action": set_mode("scripting2")
		elif tmp == "Add Overtile": set_mode("addover")
		elif tmp == "Copy Tile": set_mode("tilecopy")
	elif tmp == "Map Size":
		list_of_opts = ["Custom", "15x15", "20x20", "25x25", "30x30", "35x35",
			"40x40"]
		tmp = select_from_list(list_of_opts, True)
		if tmp == -1:
			refresh_map()
			return
		if tmp == "Custom":
			tmp = g.main.ask_for_string("New Size. Enter in form XxY (eg 23x54)",
					str(mapsize_x)+"x"+str(mapsize_y))
			if tmp == -1:
				refresh_map()
				return
			size_array = tmp.split("x")
			if len(size_array) != 2:
				print "Bad size of "+tmp
				refresh_map()
				return
			else:
				try: xysize = (int(size_array[0]), int(size_array[1]))
				except ValueError:
					print "Bad size of "+tmp
					refresh_map()
					return
				if xysize[0] < 1 or xysize[1] < 1:
					print "Bad size of "+tmp
					refresh_map()
					return
				really_change_mapsize(xysize[0], xysize[1])
		else:
			tmp = int(tmp[:2])
			really_change_mapsize(tmp, tmp)
	elif tmp == "Background":
		list_of_opts = ["Current Tile", "Water", "Dirt", "Void", "Grass", "Desert"]
		tmp = select_from_list(list_of_opts, True)
		if tmp == -1:
			refresh_map()
			return
		if tmp == "Current Tile": change_tile = cur_tile
		elif tmp == "Water": change_tile = "water/water.png"
		elif tmp == "Dirt": change_tile = "underground/dirt.png"
		elif tmp == "Void": change_tile = "underground/void.png"
		elif tmp == "Grass": change_tile = "grass.png"
		elif tmp == "Desert": change_tile = "desert/desert_grass.png"
		set_bkg(change_tile)
	elif tmp == "Border":
		list_of_opts = ["Current Tile", "Cave", "Grass", "Hills", "Rock", "Void", "Water"]
		tmp = select_from_list(list_of_opts, True)
		if tmp == -1:
			refresh_map()
			return
		if tmp == "Current Tile": change_tile = cur_tile
		elif tmp == "Cave": change_tile = "underground/rock.png"
		elif tmp == "Grass": change_tile = "grass.png"
		elif tmp == "Hills": change_tile = "hills/hills_n4.png"
		elif tmp == "Rock": change_tile = "rock.png"
		elif tmp == "Void": change_tile = "underground/void.png"
		elif tmp == "Water": change_tile = "water/water.png"
		set_border(change_tile)
	elif tmp == "Monsters":
		monster_list = []
		for monster_name in cur_map.monster:
			monster_list.append(monster_name)
		monster_list.append("")
		while 1:
			tmp = select_from_list(monster_list, False, True)
			if tmp == -1: break
			if tmp >= len(monster_list):
				tmp = g.main.ask_for_string("What is the monster's name?")
				if tmp != -1 and tmp.strip() != "":
					monster_list.append(tmp)
			else:
				tmp2 = g.main.ask_for_string("What is the monster's name?",
					textbox_text=monster_list[tmp])
				if tmp2 != -1:
					if tmp2.strip() == "":
						monster_list.pop(tmp)
					else:
						monster_list[tmp] = tmp2
		cur_map.monster = []
		for monster_line in monster_list:
			cur_map.monster.append(monster_line)
		refresh_map()
	elif tmp == "Battle Background":
		tmp = g.main.ask_for_string("Filename for battle background?",
			textbox_text=cur_map.battle_background_name)
		if tmp != -1:
			cur_map.battle_background_name = tmp
		refresh_map()


def sel_mod(selected_mod):
#	window_sel_game.withdraw()
	g.mod_directory = "../modules/" + selected_mod
	# put all items in a list
	global item_dir
	item_dir = os.listdir(g.mod_directory + "/images/tiles/items")
	j=0
	while j<len(item_dir):
		if item_dir[j] != "CVS":
			name = "items/" + item_dir[j]
			item_list[name] = 0
		j += 1
	g.read_maps(1)
	g.load_tiles()
	g.read_variables()
# 	window.deiconify()
	make_menus()
	load_tiles()
	create_map()
	setup_tilebox()
	display_tiles("default")
	pygame.display.flip()
	mouse_button_down = False
	last_square =(0, 0)
	while 1:
		pygame.time.wait(30)
		g.clock.tick(30)
		if g.break_one_loop > 0:
			g.break_one_loop -= 1
			break
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				if ask_yesno("Quit the editor?"): sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP: move_up()
				elif event.key == pygame.K_DOWN: move_down()
				elif event.key == pygame.K_LEFT: move_left()
				elif event.key == pygame.K_RIGHT: move_right()
				elif event.key == pygame.K_PAGEUP: move_up(portalsize)
				elif event.key == pygame.K_PAGEDOWN: move_down(portalsize)
				elif event.key == pygame.K_HOME: move_left(portalsize)
				elif event.key == pygame.K_END: move_right(portalsize)
				elif event.key == pygame.K_ESCAPE:
					if ask_yesno("Quit the editor?"): sys.exit()
				elif event.key == pygame.K_f: main_menu()
				elif event.key == pygame.K_t: tile_dir_list()
				elif event.key == pygame.K_m: map_menu()
				elif event.key == pygame.K_g: toggle_grid()
				elif event.key == pygame.K_s: save_map()
				elif event.key == pygame.K_l: do_load_map()
				elif (event.key == pygame.K_1 or event.key == pygame.K_2 or
						event.key == pygame.K_3 or event.key == pygame.K_4 or
						event.key == pygame.K_5 or event.key == pygame.K_6 or
						event.key == pygame.K_7 or event.key == pygame.K_8 or
						event.key == pygame.K_9):
					try: tile_dir_list(int(event.unicode)-1)
					except ValueError:
						if event.unicode == "!": tile_dir_list(13)
						elif event.unicode == "@": tile_dir_list(14)
						elif event.unicode == "#": tile_dir_list(15)
						elif event.unicode == "$": tile_dir_list(16)
						elif event.unicode == "%": tile_dir_list(17)
						elif event.unicode == "^": tile_dir_list(18)
						elif event.unicode == "&": tile_dir_list(19)
						elif event.unicode == "*": tile_dir_list(20)
						elif event.unicode == "(": tile_dir_list(21)
				elif event.unicode == "!":
					tile_dir_list(13)
				elif event.unicode == "@":
					tile_dir_list(14)
				elif event.unicode == "#":
					tile_dir_list(15)
				elif event.unicode == "$":
					tile_dir_list(16)
				elif event.unicode == "%":
					tile_dir_list(17)
				elif event.unicode == "^":
					tile_dir_list(18)
				elif event.unicode == "&":
					tile_dir_list(19)
				elif event.unicode == "*":
					tile_dir_list(20)
				elif event.unicode == "(":
					tile_dir_list(21)
				elif event.key == pygame.K_0:
					if event.unicode == "0": tile_dir_list(9)
					else: tile_dir_list(22)
				elif event.key == pygame.K_MINUS:
					if event.unicode == "-": tile_dir_list(10)
					else: tile_dir_list(23)
				elif event.key == pygame.K_EQUALS:
					if event.unicode == "=": tile_dir_list(11)
					else: tile_dir_list(24)
				elif event.key == pygame.K_BACKSLASH:
					if event.unicode == "\\": tile_dir_list(12)
					else: tile_dir_list(25)
				elif event.key == pygame.K_F1: set_mode("replace")
				elif event.key == pygame.K_F2: set_mode("add")
				elif event.key == pygame.K_F3: set_mode("remove")
				elif event.key == pygame.K_F4: set_mode("walkable")
				elif event.key == pygame.K_F5: set_mode("scripting")
				elif event.key == pygame.K_F6: set_mode("scripting2")
				elif event.key == pygame.K_F7: set_mode("addover")
				elif event.key == pygame.K_F8: set_mode("tilecopy")
				print_cur_xy((0,0), True)

			elif event.type == pygame.MOUSEMOTION:
				tmp_square = ((event.pos[0] / g.tilesize)+portal_x,
					(event.pos[1] / g.tilesize)+portal_y)
				print_cur_xy(tmp_square)
				if mouse_button_down == True:
					if tmp_square != last_square:
						last_square = tmp_square
						tmp = click_map(event.pos)
						if tmp > 0: break

			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1:
					mouse_button_down = False
					last_square = (0, 0)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					tmp = click_menu(event.pos)
					if tmp > 0:
						if tmp == 1: main_menu()
						if tmp == 2: tile_dir_list()
						if tmp == 3: map_menu()
						if tmp == 4: toggle_grid()
						break
					tmp = click_tiles(event.pos)
					if tmp > 0: break
					if (cur_mode == "replace" or cur_mode == "add" or
						cur_mode == "remove" or cur_mode == "walkable"):
						mouse_button_down = True
						last_square = ((event.pos[0] / g.tilesize)+portal_x,
							(event.pos[1] / g.tilesize)+portal_y)
					tmp = click_map(event.pos)
					if tmp > 0: break
				elif event.button == 4:
					move_up()
				elif event.button == 5:
					move_down()

		if g.unclean_screen:
			pygame.display.flip()



array_mods = os.listdir("../modules/")
i = 0
while i < len(array_mods):
	if array_mods[i] == "CVS" or array_mods[i] == "default":
		array_mods.pop(i)
	else:
		i += 1

cur_mod = 0
g.load_buttons()
if (len(array_mods) == 1):
	tmp = array_mods[cur_mod]
elif len(sys.argv) > 1:
	try:
		mod_loc = array_mods.index(sys.argv[1])
		tmp = array_mods[mod_loc]
	except ValueError:
		print "The module "+sys.argv[1]+" was not found"
		tmp = array_mods[0]
else:
	pygame.display.set_caption("Select module")
	tmp = select_from_list(array_mods, True)
	if tmp == -1: sys.exit()
	g.print_string(g.screen, "Loading", g.font, (250, 150), g.colors["white"])
	pygame.display.flip()
pygame.display.set_caption("Map Editor")
sel_mod(tmp)
