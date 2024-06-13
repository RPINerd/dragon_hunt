#monster.py
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

#This file contains everything about the monsters.

from random import random
from os import listdir

import g

#This class contains one or more monster, that can attack the player in a group.
class monster_group_class:
	def __init__(self, name):
		self.name = str(name)
		#The message given when the monster group attacks.
		self.attack_message = "The " + self.name + " attacks you."
		#The xy coords. of the upper-middle of each monster.
		self.x_pos = []
		self.y_pos = []
		#filled with strings matched up to names in monster_class upon attack.
		self.monster_list = []

class monster_class:
	def __init__(self, name, hp, attack, defense, exp, gold, descript):
		self.name = str(name)
		self.hp = int(hp)
		self.maxhp = int(hp)
		self.attack = int(attack)
		self.defense = int(defense)
		self.exp = int(exp)
		self.gold = int(gold)
		self.description = str(descript)
		#An array of lines, describing the scripting run when the monster dies.
		#If given, this *replaces* the exp/gold giving code, making those
		#entries useless.
		self.on_death = []
	def reset(self):  #resets the monster for a battle
		self.hp = self.maxhp

global monsters
monsters = []

global monster_groups
monster_groups = []

#Given the name of a monster, return the index in the monsters[] array.
def monster_name_to_index(name):
	for i in range(len(monsters)):
		if name.lower() == monsters[i].name.lower():
			return i
	print "monster " + name + " not found in monsters directory."
	return -1


#find an appropriate monster group for the given (zgrid) dungeon level.
#-1 is returned if no monsters are available for this level;
#otherwise, the position in monster_groups[] is returned.
def find_level_monster(level):
	#Pick a random entry in the monster table of the map.
	if len(g.maps[level].monster) == 0: return -1
	mon_name = g.maps[level].monster[
		int(random() * len(g.maps[level].monster))]
	#Take the monster name, and find the monsters[] index.
	for i in range(len(monster_groups)):
		if mon_name.lower() == monster_groups[i].name.lower():
			return i
	print "monster " + mon_name + " not found in monsters directory."
	return -1

#read monsters directory, and place in monsters[]. This is called on startup.
def read_monster():
	#put the names of the available monsters in array_monsters.
	array_monsters = listdir(g.mod_directory + "/data/monsters")

	#remove all .* files.
	i = 0
	while i < len(array_monsters):
		extension_start = len(array_monsters[i]) - 4
		if(extension_start <= 0):
			array_monsters.pop(i)
		else:
			if array_monsters[i][:1] == ".":
				array_monsters.pop(i)
			elif array_monsters[i][extension_start:extension_start+4] != ".txt":
				array_monsters.pop(i)
			else:
				i += 1

	#go through all monsters, adding them to our knowledge.
	for monster_filename in array_monsters:
		addmonster(monster_filename)


	#Now read and interpret monsters.txt for grouping information.
	global monster_groups
	monster_groups = []
	cur_group = -1
	monster_file = g.read_script_file("/data/monsters.txt")

	#go through all lines of the file
	for monster_line in monster_file:
		if monster_line[:1] == ":":
			monster_groups.append(monster_group_class(monster_line[1:]))
			cur_group += 1
			continue
		monster_command = monster_line.split("=")[0].strip().lower()
		monster_command2 = monster_line.split("=", 1)[1].strip()
		if monster_command == "monster":
			monster_groups[cur_group].monster_list.append(monster_command2)
		elif monster_command == "attack":
			monster_groups[cur_group].attack_message = monster_command2
		elif monster_command == "x_pos":
			for entry in monster_command2.split(","):
				monster_groups[cur_group].x_pos.append(int(entry.strip()))
		elif monster_command == "y_pos":
			for entry in monster_command2.split(","):
				monster_groups[cur_group].y_pos.append(int(entry.strip()))

#given a filename, (relative to g.mod_directory + "/data/monsters")
#open and interpret the monster.
def addmonster(filename):
	global monsters

	temp_name = ""
	temp_hp = 0
	temp_attack = 0
	temp_defense = 0
	temp_exp = 0
	temp_gold = 0
	temp_description = ""
	temp_on_death = []

	curr_mode = 0  #are we reading in a script (1) or variables (0)?

	monster_file = g.read_script_file("/data/monsters/" + filename)
	#go through all lines of the file
	for monster_line in monster_file:
		monster_line = monster_line.strip()

		if curr_mode == 1:
			temp_on_death.append(monster_line)
			continue

		monster_command = monster_line.split("=", 2)[0].strip()
		if (monster_command.lower() == "name"):
			temp_name = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == "hp"):
			temp_hp = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == "attack"):
			temp_attack = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == "defense"):
			temp_defense = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == "exp"):
			temp_exp = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == "gold"):
			temp_gold = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == "description"):
			temp_description = monster_line.split("=", 1)[1]
		elif (monster_command.lower() == ":on_death"):
			curr_mode = 1
		else:
			print "bad line of " + monster_line + " found in " + filename

	#actually add the monster
	monsters.append(monster_class(temp_name, temp_hp, temp_attack,
		temp_defense, temp_exp, temp_gold, temp_description))

	for line in temp_on_death:
		monsters[len(monsters)-1].on_death.append(line)

#copies an instance of a monster class to another instance. Used to get a
#clean copy.
def copy_monster(from_monster):
	to_monster = monster_class(
			from_monster.name,
			from_monster.maxhp,
			from_monster.attack,
			from_monster.defense,
			from_monster.exp,
			from_monster.gold,
			from_monster.description)
	for line in from_monster.on_death:
		to_monster.on_death.append(line)

	to_monster.hp= from_monster.hp
	return to_monster
