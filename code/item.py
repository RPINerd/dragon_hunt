#item.py
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

#This file contains the item/inv structures and functions.

import g
#needed for reading items dir.
from os import listdir

#Item definition.
class item_class:
	def __init__(self):
		self.name = ""
		#type is 0-5 for equipment, 10-20 for items, and 99 for system items.
		#type 10 is unusable (use for story items/keys) 11 is healing, 12 is
		#explosive, 14 is gems, 15-17 is scripted (15=usable in battle,
		#16=usable out of battle, 17=usable in both).
		self.type = 0
		#The power of the item.
		self.quality = 0
		#If price is 0, the item is un sell/buy/drop able. (For story items.)
		self.price = 0
		# value is how much you can sell it for, vs. price is the cost to buy
		self.value = 0
		self.description = ""
		self.picturename = "items/dropped.png"
		self.hp_bonus = 0
		self.ep_bonus = 0
		self.attack_bonus = 0
		self.defense_bonus = 0
		#An array of lines, describing the scripting run when the item is used.
		self.scripting = []


#inventory: 28 spaces.
#An array of numbers, which are either the index of the
#item in the item[] array, or -1 for empty.
inv = []
for x in range(28):
	inv.append(-1)

#takes the index in the item[] array, and returns the index
#of the first occurance in the inv[] array, or -1 for failure.
def find_inv_item(num):
	for i in range(len(inv)):
		if inv[i] == num:
			return i
	return -1

#takes the index of an item in the item[] array, and places it
#in the first empty spot in the inv[] array. Retuns the
#index of inv[] item is placed at, or -1 for failure.
def take_inv_item(num):
	for i in range(len(inv)):
		if inv[i] == -1:
			inv[i] = num
			return i
	return -1

#takes the index of an item in the inv[] array,
#removes it, then removes the empty space.
def drop_inv_item(num):
	inv[num] = -1
	for i in range(num+1, len(inv)):
		inv[i-1]=inv[i]
	inv[len(inv)-1] = -1

#Item arrays. Each item is a separate element in the array. Each element is
#a member of the class item_class. See the start of this file for details.
#Duplicate item names are bad.
global item
item = []

#takes an item name, and returns its location in the
#item[] array, with -1 == nonexisting.
def finditem(name):
	tmpname = name.lower()
	for i in range(len(item)):
		if tmpname == item[i].name.lower():
			return i
	return -1


#read items directory. This is called on startup.
def read_items():
	#put the names of the available items in array_items.
	array_items = listdir(g.mod_directory + "/data/items")

	#remove all .* files.
	i = 0
	while i < len(array_items):
		extension_start = len(array_items[i]) - 4
		if(extension_start <= 0):
			array_items.pop(i)
		else:
			if array_items[i][:1] == ".":
				array_items.pop(i)
			elif array_items[i][extension_start:extension_start+4] != ".txt":
				array_items.pop(i)
			else:
				i += 1

	#go through all items, adding them to our knowledge.
	for item_filename in array_items:
		additem(item_filename)

#given the filename of an item file, load the data from the file into the
#item array.
def additem(item_filename):
	global item

	temp_name = ""
	temp_type = 0
	temp_quality = 0
	temp_price = 0
	temp_value = 0
	temp_description = ""
	temp_picture = None
	item.append(item_class())
	item_array_loc = len(item)-1

	# default values
	item[item_array_loc].name = ""
	item[item_array_loc].type = 0
	item[item_array_loc].quality = 0
	item[item_array_loc].price = -1
	item[item_array_loc].value = -1
	item[item_array_loc].description = ""
	item[item_array_loc].picturename = None
	item[item_array_loc].scripting = []

	item_file = g.read_script_file("/data/items/" + item_filename)

	#go through all lines of the file
	cur_line = 0
	while cur_line < len(item_file):
		#strip out spaces/tabs
		item_line = item_file[cur_line]
		item_line = item_line.strip()

		#determine the command entered.
		item_command = item_line.split("=", 2)[0]
		item_command = item_command.strip()
		if (item_command.lower() == "name"):
			item[item_array_loc].name = str(item_line.split("=", 1)[1])
		elif (item_command.lower() == "type"):
			item[item_array_loc].type = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "quality"):
			item[item_array_loc].quality = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "price"):
			item[item_array_loc].price = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "value"):
			item[item_array_loc].value = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "description"):
			item[item_array_loc].description = str(item_line.split("=", 1)[1])
		elif (item_command.lower() == "picture"):
			item[item_array_loc].picturename = str(item_line.split("=", 1)[1])
		elif (item_command.lower() == "hp_bonus"):
			item[item_array_loc].hp_bonus = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "ep_bonus"):
			item[item_array_loc].ep_bonus = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "attack_bonus"):
			item[item_array_loc].attack_bonus = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == "defense_bonus"):
			item[item_array_loc].defense_bonus = int(item_line.split("=", 1)[1])
		elif (item_command.lower() == ":scripting"):
			cur_line += 1
			while cur_line < len(item_file):
				item_line = item_file[cur_line]
				item_line = item_line.strip()
				if item_line.lower() == ":values":
					break
				item[item_array_loc].scripting.append(item_line)
				cur_line += 1
		cur_line += 1
	if (item[item_array_loc].value == -1):
		item[item_array_loc].value = item[item_array_loc].price
	if (item[item_array_loc].price == -1):
		item[item_array_loc].price = item[item_array_loc].value


#An array of dropped items. Used for keeping dropped items around
#through save/loads.
class dropped_item_class:
	def __init__(self, name, x, y, mapname):
		self.name = name
		self.x = x
		self.y = y
		self.mapname = mapname

dropped_items = []

def add_dropped_item(name, x, y, mapname):
	dropped_items.append(dropped_item_class(name, x, y, mapname))

def del_dropped_item(name, x, y, mapname):
	for i in range(len(dropped_items)):
		if dropped_items[i].name == name and dropped_items[i].x == x and \
			dropped_items[i].y == y and dropped_items[i].mapname == mapname:
				del dropped_items[i]
				return 0

def load_dropped_items():
	for dropped_item in dropped_items:
		z = g.mapname2zgrid(dropped_item.mapname)
		g.maps[z].field[dropped_item.y][dropped_item.x].additem(
														dropped_item.name)
