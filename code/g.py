#g.py
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

#This file contains everything that needs to be accessed by most or all files.


#Dragon Hunt 3.56. Released under the GPL. Copyright 2005
#(Note to self: when changing version, change variables.txt, README.txt,
# and setup.py.)

#from Tkinter import *
#import ImageTk
#needed for die_roll
import pygame

from random import random
#needed for save/load game
import pickle
from os import path, mkdir, remove, walk

#needed for scripting
from scripting import *

#player info
from player import *

import monster
import item
import main
import action

#This will be displayed on the Title screen and Main screen.
game_name = ""

#This is the main window for the entire game. (Will be filled in with
#a Tkinter window reference later.)
window_main = ""

#Call rpg with the debug argument to show debug info.
debug = False
#Call rpg with the faststart argument to not preprocess the map files.
faststart = False

#fill colour
fill_colour = "#b9e5ad"
fill_sel_colour = "#7aa96e"
outline_colour = "#70a662"
#fill_colour = "#5050ff"
#fill_sel_colour = "#A0A0ff"
#outline_colour = "#202090"

#default tile width. Set in variables.txt, or default to 32.
tilesize = 32

#location on map: x, y, z coordinate. Map names are given a zgrid on loading.
xgrid = 0
ygrid = 0
zgrid = 1

#controls timed effects such as healing. Loops around every 30 turns (0-29);
#controls perturn.txt.
timestep = 0

#dictionary of script variables.
var_list = {}

#current monster hp. Used to allow activation
#of bombs from inv. UNUSED
cur_mon_hp = 0

#Current window in use (main, battle, inventory, shop)
cur_window = "main"

#Should the player be allowed to move? Used with the move scripting command,
#to prevent moving again after moving.
allow_move = 1

#Should the automatic changing of the hero picture be allowed?
#Used with the manual hero() command, to prevent the change from being undone.
allow_change_hero = 1

#width of the hp/ep bars
hpbar_width = 0

#current module directory
mod_directory = ""

#per turn scripting, for hp recovery and the like.
per_turn_script = []

#Default key bindings for the game.
bindings = {}

message_lines = 6
difficulty = 1

name_name = "Name"
hp_name = "HP"
ep_name = "EP"
attack_name = "Attack"
defense_name = "Defense"
gold_name = "Gold"
skill_name = "Skill"
exp_name = "EXP"
level_name = "Level"
exp_list = ""


#Used in new_game
default_player_name = "Alfred"

#Used in place of some of the Tkinter variables.
break_one_loop = 0

#used to decide whether or not to refresh (flip) the screen.
unclean_screen = False

global clock
clock = pygame.time.Clock()

#save the game in saves/input.
#uses pickle, first line is a version number.
def savegame(save_file):
	#If there is no save directory, make one.
	if path.isdir(g.mod_directory + "/saves") == 0:
		if path.exists(g.mod_directory + "/saves") == 1:
			remove(g.mod_directory + "/saves")
		mkdir(g.mod_directory + "/saves")
	save_loc = g.mod_directory + "/saves/" + save_file
	savefile=open(save_loc, 'w')
	#savefile version; update whenever the data saved changes.
	pickle.dump("dh3.3", savefile)
	pickle.dump(player.name, savefile)
	pickle.dump(player.hp, savefile)
	pickle.dump(player.ep, savefile)
	pickle.dump(player.maxhp, savefile)
	pickle.dump(player.maxep, savefile)
	pickle.dump(player.attack, savefile)
	pickle.dump(player.defense, savefile)
	pickle.dump(player.gold, savefile)
	pickle.dump(player.exp, savefile)
	pickle.dump(player.level, savefile)
	pickle.dump(player.skillpoints, savefile)

	#equipment is stored by name to increase savefile compatability.
	pickle.dump(len(player.equip), savefile)
	for i in range(len(player.equip)):
		if player.equip[i] != -1:
			pickle.dump(item.item[player.equip[i]].name, savefile)
		else: pickle.dump("Ignore", savefile)
	pickle.dump(len(item.inv), savefile)
	for i in range(len(item.inv)):
		if item.inv[i] != -1:
			pickle.dump(item.item[item.inv[i]].name, savefile)
		else: pickle.dump("Ignore", savefile)
	pickle.dump(xgrid, savefile)
	pickle.dump(ygrid, savefile)
	pickle.dump(g.maps[zgrid].name, savefile)
	#skills are stored by name as well.
	num = 0
	for i in range(len(player.skill)):
		if player.skill[i][5] == 1:
			num += 1
	pickle.dump(num, savefile)
	for i in range(len(player.skill)):
		if player.skill[i][5] == 1:
			pickle.dump(player.skill[i][0], savefile)

	pickle.dump(item.dropped_items, savefile)
	pickle.dump(timestep, savefile)
	pickle.dump(var_list, savefile)
	savefile.close()

def loadgame(save_file):
	save_loc = g.mod_directory + "/saves/" + save_file
	savefile=open(save_loc, 'r')
	version = pickle.load(savefile)
	if version != "dh3.3":
		return loadgame_31(save_file)
	player.name = pickle.load(savefile)
	player.hp = pickle.load(savefile)
	player.ep = pickle.load(savefile)
	player.maxhp = pickle.load(savefile)
	player.maxep = pickle.load(savefile)
	player.attack = pickle.load(savefile)
	player.defense = pickle.load(savefile)
	player.gold = pickle.load(savefile)
	player.exp = pickle.load(savefile)
	player.level = pickle.load(savefile)
	player.skillpoints = pickle.load(savefile)

	#equipment is stored by name to increase savefile compatability.
	equip_len = pickle.load(savefile)
	for i in range(equip_len):
		player.equip[i] = item.finditem(pickle.load(savefile))
		if item.item[player.equip[i]].name == "Ignore":
			player.equip[i] = -1
	global inv;			inv_len = pickle.load(savefile)
	for i in range(inv_len):
		item.inv[i] = item.finditem(pickle.load(savefile))
		if item.item[item.inv[i]].name == "Ignore":
			item.inv[i] = -1
	global xgrid;		xgrid = pickle.load(savefile)
	global ygrid;		ygrid = pickle.load(savefile)
	global zgrid;		zgrid = pickle.load(savefile)
	if str(zgrid).isdigit() != True:
		zgrid = mapname2zgrid(str(zgrid))
	skill_len = pickle.load(savefile)
	for i in range(skill_len):
		player.skill[findskill(pickle.load(savefile))][5] = 1
	item.dropped_items = pickle.load(savefile)
	global timestep;	timestep = pickle.load(savefile)
	global var_list;	var_list = pickle.load(savefile)
	savefile.close()

def loadgame_31(save_file):
	save_loc = g.mod_directory + "/saves/" + save_file
	savefile=open(save_loc, 'r')
	version = pickle.load(savefile)
	if version != "dh3.2":
		print "Old savefile version. Try an earlier version of DH."
		return -1
	player.name = pickle.load(savefile)
	player.hp = pickle.load(savefile)
	player.ep = pickle.load(savefile)
	player.maxhp = pickle.load(savefile)
	player.maxep = pickle.load(savefile)
	player.attack = pickle.load(savefile)
	player.defense = pickle.load(savefile)
	player.gold = pickle.load(savefile)
	player.exp = pickle.load(savefile)
	player.level = pickle.load(savefile)
	player.skillpoints = pickle.load(savefile)

	#equipment is stored by name to increase savefile compatability.
	equip_len = pickle.load(savefile)
	for i in range(equip_len):
		player.equip[i] = item.finditem(pickle.load(savefile))
		if item.item[player.equip[i]].name == "Ignore":
			player.equip[i] = -1
	global inv;			inv_len = pickle.load(savefile)
	for i in range(inv_len):
		item.inv[i] = item.finditem(pickle.load(savefile))
		if item.item[item.inv[i]].name == "Ignore":
			item.inv[i] = -1
	global xgrid;		xgrid = pickle.load(savefile)
	global ygrid;		ygrid = pickle.load(savefile)
	global zgrid;		zgrid = pickle.load(savefile)
	skill_len = pickle.load(savefile)
	for i in range(skill_len):
		player.skill[findskill(pickle.load(savefile))][5] = 1
	global timestep;	timestep = pickle.load(savefile)
	global cur_mon_hp;	cur_mon_hp = pickle.load(savefile)
	savefile.close()

#this calls scripting.py to read the datafiles.
def init_data():
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Settings", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	read_settings()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Backgrounds", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	load_backgrounds()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Scripts", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	read_scripts()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Items", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	item.read_items()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Skills", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	read_skills()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Monsters", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	monster.read_monster()
	global game_name
	game_name = read_game_name()
	read_variables()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Shops", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	read_shops()
	read_perturn()
	screen.fill(colors["light_gray"], (screen_size[0]/2-150, screen_size[1]/2-20,
		300, 40))
	print_string(screen, "Loading Images", font,
		(screen_size[0]/2, screen_size[1]/2), align=1)
	pygame.display.flip()
	load_buttons()
	load_icons()
	load_sounds()

#Get the name of the module from the variables.txt file. Note that this
#does not set the game name, only returns it. This lets it be used in rpg.py
def read_game_name():
	file = open(mod_directory + "/data/variables.txt", 'r')
	line = file.readline()
	while (line != ''):
		line = line.strip()
		if (line[:1] == "#" or line[:1] == ""):
			line = file.readline()
			continue
		if (line.split("=", 1)[0].strip() == "game_name"):
			return line.split("=", 1)[1].strip()
		line = file.readline()

#What dice to roll when starting a new game. 2d array.
new_game_dice = []


global joystick
joystick = 0

global use_joy
use_joy = 1

global joy_num
joy_num = 0

global joykey_action
joykey_action = 0
global joykey_cancel
joykey_cancel = 1
global joy_axis0
joy_axis0 = 0
global joy_axis1
joy_axis1 = 1

#get the key bindings from settings.txt
def read_settings():
	global bindings; global message_lines; global difficulty
	global use_joy; global editor_xy; global editor_tilesize
	global fullscreen; global joy_num; global joykey_action
	global joykey_cancel; global joy_axis0; global joy_axis1
	editor_xy = (640, 480)
	editor_tilesize = 15
	fullscreen = 0
	#try to open settings.txt. If it doesn't exist,
	# just use the default settings.
	try: file = open("../settings.txt", 'r')
	except IOError: return 0
	line = file.readline()
	while (line != ''):
		line = line.strip()
		if (line[:1] == "#" or line[:1] == ""):
			line = file.readline()
			continue
		if (line.split("=", 1)[0].strip() == "message_lines"):
			message_lines = line.split("=", 1)[1].strip()
		elif (line.split("=", 1)[0].strip() == "difficulty"):
			difficulty = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "editor_xsize"):
			editor_xy = (int(line.split("=", 1)[1].strip()), editor_xy[1])
		elif (line.split("=", 1)[0].strip() == "editor_ysize"):
			editor_xy = (editor_xy[0], int(line.split("=", 1)[1].strip()))
		elif (line.split("=", 1)[0].strip() == "editor_tilesize"):
			editor_tilesize = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "fullscreen"):
			fullscreen = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "usejoystick"):
			use_joy = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "joystick_number"):
			joy_num = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "joystick_action"):
			joykey_action = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "joystick_cancel"):
			joykey_cancel = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "joystick_lr_axis"):
			joy_axis0 = int(line.split("=", 1)[1].strip())
		elif (line.split("=", 1)[0].strip() == "joystick_ud_axis"):
			joy_axis1 = int(line.split("=", 1)[1].strip())
		else:
			bind_line = line.split("=", 1)[0].strip()
			bindings[bind_line] = int(line.split("=", 1)[1].strip())
		line = file.readline()
read_settings()

def read_variables():
	for i in range(5):
		new_game_dice.append([])
	file = open(mod_directory + "/data/variables.txt", 'r')
	line = file.readline()
	while (line != ''):
		line = line.strip()
		if (line[:1] == "#" or line[:1] == ""):
			line = file.readline()
			continue
		switch2 = line.split("=", 1)[0].strip().lower()
		if (switch2 == "hp"):
			read_dice(0, line.split("=", 1)[1].strip())
		elif (switch2 == "ep"):
			read_dice(1, line.split("=", 1)[1].strip())
		elif (switch2 == "attack"):
			read_dice(2, line.split("=", 1)[1].strip())
		elif (switch2 == "defense"):
			read_dice(3, line.split("=", 1)[1].strip())
		elif (switch2 == "gold"):
			read_dice(4, line.split("=", 1)[1].strip())
		elif (switch2 == "tilesize"):
			global tilesize
			tilesize = int(line.split("=", 1)[1].strip())
		elif (switch2 == "default_player_name"):
			global default_player_name
			default_player_name = line.split("=", 1)[1].strip()
		elif (switch2 == "name_name"):
			global name_name
			name_name = line.split("=", 1)[1].strip()
		elif (switch2 == "hp_name"):
			global hp_name
			hp_name = line.split("=", 1)[1].strip()
		elif (switch2 == "ep_name"):
			global ep_name
			ep_name = line.split("=", 1)[1].strip()
		elif (switch2 == "attack_name"):
			global attack_name
			attack_name = line.split("=", 1)[1].strip()
		elif (switch2 == "defense_name"):
			global defense_name
			defense_name = line.split("=", 1)[1].strip()
		elif (switch2 == "gold_name"):
			global gold_name
			gold_name = line.split("=", 1)[1].strip()
		elif (switch2 == "skill_name"):
			global skill_name
			skill_name = line.split("=", 1)[1].strip()
		elif (switch2 == "exp_name"):
			global exp_name
			exp_name = line.split("=", 1)[1].strip()
		elif (switch2 == "level_name"):
			global level_name
			level_name = line.split("=", 1)[1].strip()
		elif (switch2 == "exp_list"):
			global exp_list
			exp_list = line.split("=", 1)[1].strip().split(" ")
		line = file.readline()

#given a dice set and string of the form 2d4+5, place in new_game_dice
def read_dice(variable, dice_string):
	first = dice_string.split("d", 1)[0].strip()
	temp = dice_string.split("d", 1)[1].strip()
	if temp.find("+") == -1:
		second = temp.strip()
		third = "0"
	else:
		second = temp.split("+", 1)[0].strip()
		third = temp.split("+", 1)[1].strip()
	new_game_dice[variable].append(int(first))
	new_game_dice[variable].append(int(second))
	new_game_dice[variable].append(int(third))

#reads the file data/perturn.txt. Expects mod_directory to be set.
def read_perturn():
	cur_turns = []
	temp_cur_turns = []
	global per_turn_script
	for i in range(30):
		per_turn_script.append([])
	per_turn_lines = read_script_file("/data/perturn.txt")
	for line in per_turn_lines:
		line = line.strip()
		if line[:1] == ":": #start defining more tiles.
			cur_turns = []
			temp_cur_turns = line[1:].split(",")
			for turn in temp_cur_turns:
				if turn.strip().isdigit():
					cur_turns.append(int(turn.strip()))

		#give scripting to the current tiles
		else:
			for turn_num in cur_turns:
				per_turn_script[turn_num].append(line)


#skills array. Each skill is a separate line in the array. Each line goes:
#name, effect, level, price, description, acquired, scripting, picture.
#effect is an integer that tells battle.py which case in a select to pick.
#(0=Rage, 1=Sneak, 2=Frenzy, 3=Dismember, 4=Scripted (battle),
# 5=Scripted (out of battle), 6=Scripted (both).)
#level is the skillpoints required to get the skill,
#price is the ep needed to use.
#acquired tells if the skill has already been learned by the player.
#scripting is an array (that may be empty) that describes the scripting run on use.
#picture is the picture used to show that skill.

#Add a skill to the skill[] array
def addskill(name, effect, level, price, description, scripting=[],
					picture="items/rage.png"):
	player.skill.append([])
	i = len(player.skill)
	player.skill[i-1].append(name)
	player.skill[i-1].append(int(effect))
	player.skill[i-1].append(int(level))
	player.skill[i-1].append(int(price))
	player.skill[i-1].append(description)
	player.skill[i-1].append(0)
	player.skill[i-1].append(scripting)
	player.skill[i-1].append(picture)


#takes a skill name, and returns its location in the
#skill[] array, with -1 == nonexisting.
def findskill(name):
	for i in range(len(player.skill)):
		if name.lower() == player.skill[i][0].lower():
			return i
	return -1

#gives the player a skill; takes the location in skill[] as input
def add_skill(skill_loc):
	if (player.skill[skill_loc][5] == 1):
		return 0
	else:
		player.skill[skill_loc][5] = 1
		return 1

#Load the skills. Requires g.mod_directory to be set
def read_skills():
	#Add built-in skills.
	addskill("Rage", 0, 1, 10, "Gives you increased damage for the"+
		" rest of a battle", picture="items/rage.png")
	addskill("Sneak Away", 1, 1, 10,
		"Attempts to leave a battle.", picture="items/sneak_away.png")
	addskill("Dismember",  3, 2, 20, "Your next attack will do maximum"+
		" damage, and ignore armor", picture="items/bastard_sword.png")
	addskill("Frenzy",  2, 2, 30, "Your next attack will try to hit"+
		" more than once", picture = "items/frenzy.png")
	if path.exists(g.mod_directory + "/data/skills.txt"):
		temp_skills = read_script_file("/data/skills.txt")

	#temp storage for the skill data
	temp_skill_name = ""
	temp_skill_level = 0
	temp_skill_type = 4
	temp_skill_price = 0
	temp_skill_description = ""
	temp_skill_scripting = []
	#Are we entering skill data (0) or scripting (1)?
	data_or_scripting = 0

	for line in temp_skills:
		line_strip = line.strip()
		if line_strip[0] == ":":
			#switch between data or scripting
			if line_strip[1:].lower() == "scripting":
				data_or_scripting = 1
			elif line_strip[1:].lower() == "data":
				data_or_scripting = 0
			else: #Or just input a new skill.
				#If we have any data, add the previous skill
				if temp_skill_name != "":
					addskill(temp_skill_name, temp_skill_type, temp_skill_level,
							temp_skill_price, temp_skill_description,
							temp_skill_scripting, temp_skill_picture)

				temp_skill_name = line_strip[1:]
				temp_skill_level = 0
				temp_skill_type = 4
				temp_skill_price = 0
				temp_skill_description = ""
				temp_skill_scripting = []
				temp_skill_picture = "items/rage.png"
		else:
			if data_or_scripting == 0:
				command = line_strip.split("=", 1)[0].lower().strip()
				value = line_strip.split("=", 1)[1].strip()
				if command == "level": temp_skill_level = value
				elif command == "price": temp_skill_price = value
				elif command == "type": temp_skill_type = value
				elif command == "description": temp_skill_description = value
				elif command == "picture": temp_skill_picture = value
			else:
				temp_skill_scripting.append(line_strip)
	if temp_skill_name != "":
		addskill(temp_skill_name, temp_skill_type, temp_skill_level,
				temp_skill_price, temp_skill_description,
				temp_skill_scripting, temp_skill_picture)


#Rolls dice in the form 2d6, where 2 is the number of dice, and 6 the number of
#sides on each die. modify is the bonus given to each die. Use die_roll(2, 6)

#Modify is the bonus given to each die. Use die_roll(2, 6) + 4 for bonuses on
#the entire roll, die_roll(2, 6, 1) for bonuses on each roll. Default = 0
def die_roll(dice, sides, modfy = 0):
	if sides < 1:
		sides = 1
	if dice < 1:
		dice = 1

	sum = 0
	for x in range(dice):
		die = int(((random() * sides) + 1 + modfy))
		sum = sum + die

	return sum


#Returns the symbol of the given tile. X and Y are absolute coords.
def checklocation(x, y):

	#Assume that all off-map areas are rock.
	if x < 0 or y < 0:
		return 'a'
	try:
		#this will fail when looking too far right or down
		return maps[zgrid].field[y][x].name
	except IndexError:
		#off the map, so rock.
		return 'a'

#like checklocation, but just returns 0 (unwalkable) or 1 (walkable)
def iswalkable(x, y, dx, dy):
	#set direction hero is moving in
	if dy == -1:
		move_direction = "n"
	elif dy == 1:
		move_direction = "s"
	elif dx == -1:
		move_direction = "w"
	else:
		move_direction = "e"

	#Assume that all off-map areas (to north or west) are unwalkable.
	if x < 0 or y < 0:
		return 0
	try:
		#this will fail when looking too far right or down
		if maps[zgrid].field[y][x].walk == 0:
			return 0
		#can't move onto tile if there's a wall in the way
		if maps[zgrid].field[y][x].walk == 1:
			if maps[zgrid].field[y][x].wall_s == 1 and move_direction == "n":
				return 0
			elif maps[zgrid].field[y][x].wall_n == 1 and move_direction == "s":
				return 0
			elif maps[zgrid].field[y][x].wall_e == 1 and move_direction == "w":
				return 0
			elif maps[zgrid].field[y][x].wall_w == 1 and move_direction == "e":
				return 0
		#can't move out of old tile if there's a wall in the way
		if maps[zgrid].field[y-dy][x-dx].wall_s == 1 and move_direction == "s":
			return 0
		elif maps[zgrid].field[y-dy][x-dx].wall_n == 1 and move_direction == "n":
			return 0
		elif maps[zgrid].field[y-dy][x-dx].wall_e == 1 and move_direction == "e":
			return 0
		elif maps[zgrid].field[y-dy][x-dx].wall_w == 1 and move_direction == "w":
			return 0

	except IndexError:
		return 0
	#By this point, it is known to be walkable.
	return 1

#takes the name of a map, and returns its zgrid.
def mapname2zgrid(name):
	for i in range(len(maps)):
		if maps[i].name == name:
			return i
	else:
		print "file " + name + " not found"
		return -1

tiles = {}

#this loads the various tiles.
def load_tiles():
	global tiles
	temp_images = read_images("/images/tiles/")
	tiles = {}
	for image_name, image in temp_images.iteritems():
		tiles[image_name] = image

backgrounds = {}

#This loads the battle backgrounds.
def load_backgrounds():
	global backgrounds
	temp_images = read_images("/images/backgrounds/")
	backgrounds = {}
	for image_name, image in temp_images.iteritems():
		backgrounds[image_name] = image

buttons = {}

#This loads the buttons.
def load_buttons():
	global buttons
	temp_images = read_images("/images/buttons/")
	buttons = {}
	for image_name, image in temp_images.iteritems():
		buttons[image_name] = image

icons = {}

#This loads the icons
def load_icons():
	global icons
	temp_images = read_images("/images/icons/")
	icons = {}
	for image_name, image in temp_images.iteritems():
		icons[image_name] = image



#given a filename, return the script contained in the file. from_editor will
#be used for the map editor, to keep it from shredding formatting.
def read_script_file(file_name, from_editor=0):
	temp_array = []
	file = open(g.mod_directory + file_name, 'r')
	temp_array.extend(file.readlines())
	file.close()
	if from_editor==0:
		temp_array = interpret_lines(temp_array)
	return temp_array

#Takes an array of lines, and deals with comments, empty lines,
#and line-continuation, to properly interpret the scripting.
def interpret_lines(temp_array):
	cur_line = 0
	while 1:
		if cur_line >= len(temp_array): break
		#strip out spaces/tabs
		temp_array[cur_line] = temp_array[cur_line].strip()
		#ignore blank lines and comments
		if temp_array[cur_line][:1] == "#" or temp_array[cur_line] == "":
			temp_array.pop(cur_line)
			continue
		#allow the \ line-continuation character.
		while temp_array[cur_line][-1:] == "\\":  #really a single backslash, BTW.
			temp_array[cur_line] = temp_array[cur_line][:-1] + temp_array[cur_line+1][:-1].strip()
			temp_array.pop(cur_line+1)
			temp_array[cur_line].strip()
		cur_line += 1
	return temp_array


sounds = {}
nosound = 0
#This loads the sounds
def load_sounds():
	global sounds
	global nosound
	sounds =  {}
	if nosound == 1: return 0
	try:
		pygame.mixer.init()
	except:
		print "Unable to init sound."
		nosound = 1
		return 0

	for root, dirs, files in walk(mod_directory + "/sound"):
		(head, tail) = path.split(root)
		if (tail != "CVS"):
			for soundname in files:
				#if image is in a sub-dir:
				tmp_name = soundname[:-5]+soundname[-4:]
				tmp_number = int(soundname[-5])
				if (root != mod_directory + "/sound"):
					i = len(mod_directory + "/sound")
					base_name = root[i:] + "/" + tmp_name
				else: #if image is in root dir
					base_name = tmp_name
				if not sounds.has_key(base_name): sounds[base_name] = {}
				sounds[base_name][tmp_number] = \
					pygame.mixer.Sound(root + "/" + soundname)

def play_sound(sound_name):
	if not sounds.has_key(sound_name):
		print "missing sound set "+sound_name
	dict_size = len(sounds[sound_name])

	sounds[sound_name][int(random() * dict_size)].play()


#create the fonts needed.
font = pygame.font.Font(None, 14)

#colors:
colors = {}

def fill_colors():
	colors["white"] = (255, 255, 255, 255)
	colors["black"] = (0, 0, 0, 255)
	colors["hp_red"] = (238, 5, 5, 255)
	colors["hp_green"] = (5, 187, 5, 255)
	colors["ep_blue"] = (5, 5, 238, 255)
	colors["dark_red"] = (125, 0, 0, 255)
	colors["dark_green"] = (122, 169, 110, 255)
	colors["dark_blue"] = (0, 0, 125, 255)
	colors["light_red"] = (255, 50, 50, 255)
	colors["light_green"] = (50, 255, 50, 255)
	colors["light_blue"] = (50, 50, 255, 255)
	colors["purple"] = (96, 96, 144, 255)
	colors["light_gray"] = (227, 227, 227, 255)
	colors["very_dark_blue"] = (32, 32, 47, 255)
	colors["dh_green"] = (185, 229, 173, 255)
fill_colors()

#given a directory relative to g.mod_directory, will return a dictionary
#of all images in that directory, and all subdirectories.
def read_images(dir_name):
	if pygame.image.get_extended() == 0:
		print "Error: SDL_image required. Exiting."
		sys.exit()
	image_dictionary =  {"blank" : pygame.Surface((32, 32))}
	image_dictionary = inner_read_images("../modules/default/" + dir_name,
			image_dictionary)
	image_dictionary = inner_read_images(g.mod_directory + dir_name,
			image_dictionary)

	return image_dictionary


def inner_read_images(dir_name, image_dictionary):
	i=0
	for root, dirs, files in walk(dir_name):
		(head, tail) = path.split(root)
		try:
			if (tail != "CVS"):
				for tilename in files:
					#if image is in a sub-dir:
					if (root != dir_name):
						i = len(dir_name)
						image_dictionary[root[i:] + "/" + tilename] = \
							pygame.image.load(root + "/" + tilename).convert_alpha()
					else: #if image is in root dir
						image_dictionary[tilename] = \
							pygame.image.load(root + "/" + tilename).convert_alpha()
		except pygame.error:
			print root[i:] + "/" + tilename + " failed to load"
	return image_dictionary

#creates a box, as used throughout the game.
def create_norm_box(xy, size, outline_color="black", inner_color="light_gray"):
	screen.fill(colors[outline_color],
		(xy[0], xy[1], size[0], size[1]))
	screen.fill(colors[inner_color],
		(xy[0]+1, xy[1]+1, size[0]-2, size[1]-2))

#given a surface, string, font, char to underline (int; -1 to len(string)),
#xy coord, and color, print the string to the surface.
#Align (0=left, 1=Center, 2=Right) changes the alignment of the text
def print_string(surface, string_to_print, font, xy, color=colors["black"],
		align=0, width=-1):
	string_to_print = string_to_print.replace("\t", "     ")
	if align != 0:
		temp_size = font.size(string_to_print)
		if align == 1: xy = (xy[0] - temp_size[0]/2, xy[1])
		elif align == 2: xy = (xy[0] - temp_size[0], xy[1])
	temp_text = font.render(string_to_print, 1, color)
	if width != -1:
		surface.blit(temp_text, xy, (0, 0, width, temp_text.get_size()[1]))
	else:
		surface.blit(temp_text, xy)

#Used to display descriptions and such. Automatically wraps the text to fit
#within a certain width.
#Note that \n can be used for newlines, but it must be used as
#line1 \\n line2 in code, (separated by spaces, with the \ escaped), or as
#line1 \n line2 in scripts.
def print_multiline(surface, string_to_print, font, width, xy, color="black"):
	string_to_print = string_to_print.replace("\t", "     ")
	start_xy = xy
	string_array = string_to_print.split(" ")

	num_of_lines = 1
	for string in string_array:
		string += " "
		temp_size = font.size(string)

		if string == "\n ":
			num_of_lines += 1
			xy = (start_xy[0], xy[1]+temp_size[1])
			continue
		temp_text = font.render(string, 1, colors[color])

		if (xy[0]-start_xy[0])+temp_size[0] > width:
			num_of_lines += 1
			xy = (start_xy[0], xy[1]+temp_size[1])
		surface.blit(temp_text, xy)
		xy = (xy[0]+temp_size[0], xy[1])
	return num_of_lines

global last_joy_times
last_joy_times = {}
last_joy_times["lr"]=0
last_joy_times["ud"]=0
last_joy_times["a"]=0
last_joy_times["b"]=0



def run_joystick(delay_time = 400):
	if g.joystick == 0 or use_joy == 0:
		return 0

	global last_joy_times
	if abs(g.joystick.get_axis(g.joy_axis0)) < 0.2:
		last_joy_times["lr"] = 0
	if abs(g.joystick.get_axis(g.joy_axis1)) < 0.2:
		last_joy_times["ud"] = 0
	if not g.joystick.get_button(g.joykey_action):
		last_joy_times["a"] = 0
	if not g.joystick.get_button(g.joykey_cancel):
		last_joy_times["b"] = 0

	if (joystick.get_axis(0) < -0.5 and
				pygame.time.get_ticks()-last_joy_times["lr"]> delay_time):
		last_joy_times["lr"] = pygame.time.get_ticks()
		return bindings["left"]
	if (joystick.get_axis(0) > 0.5 and
				pygame.time.get_ticks()-last_joy_times["lr"]> delay_time):
		last_joy_times["lr"] = pygame.time.get_ticks()
		return bindings["right"]
	if (joystick.get_axis(1) < -0.5 and
				pygame.time.get_ticks()-last_joy_times["ud"]> delay_time):
		last_joy_times["ud"] = pygame.time.get_ticks()
		return bindings["up"]
	if (joystick.get_axis(1) > 0.5 and
				pygame.time.get_ticks()-last_joy_times["ud"]> delay_time):
		last_joy_times["ud"] = pygame.time.get_ticks()
		return bindings["down"]
	if (joystick.get_button(g.joykey_action) and
				pygame.time.get_ticks()-last_joy_times["a"]> delay_time):
		last_joy_times["a"] = pygame.time.get_ticks()
		return bindings["action"]
	if (joystick.get_button(g.joykey_cancel) and
				pygame.time.get_ticks()-last_joy_times["b"]> delay_time):
		last_joy_times["b"] = pygame.time.get_ticks()
		return bindings["cancel"]
	return 0
