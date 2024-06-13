#file: scripting.py
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

#This file controls the datafile scripting, both loading and executing.

from player import *

import g
import main
import battle
import monster

debug = 0
if debug == 1:
	from time import clock

#set to 1 whenever the player really shouldn't be moving.
global has_dialog
has_dialog = 0





#given a string such as info or question uses, interpret all ~Action~
#embedded variables, and return the displayable string.
def interpret_line(message):
	#The ~Variable~ sequence enables variables to be inserted into info.
	num_of_tildes = message.count("~")
	#Check for no ~'s. This should be most common.
	if num_of_tildes == 0:
		return message

	#See if the string is formatted correctly.
	if num_of_tildes % 2 == 1:
		print "Unmatched ~ character: " + message
		return "Unmatched ~ character: " + message

	#Interpret the embedded variables:
	cur_str_pos = -1  #The current pointer into message
	endstring = ""  #The interpreted string.
	while cur_str_pos <= len(message):
		start_tilde = message.find("~", cur_str_pos+1)
		if start_tilde == -1:
			endstring += message[cur_str_pos+1:]
			break
		endstring += message[cur_str_pos+1:start_tilde]
		end_tilde = message.find("~", start_tilde+1)
		if start_tilde+1 == end_tilde: endstring += "~"

		#we now know that message[start_tilde+1:end_tilde] is a variable
		else:
			line_return = script_var(g.xgrid, g.ygrid, g.zgrid,
						 [["\""+message[start_tilde+1:end_tilde]+"\"", 1]])
			#Add the returned data into the end string.
			if type(line_return) == str or type(line_return) == unicode:
				line_return = line_return[1:-1]
			endstring += str(line_return)
		cur_str_pos = end_tilde
	return endstring


#given an array of commands, run them. See scripting.txt for details.
#x and y are absolute values.
#Returns 1 if the scripting completed, or 0 if it ended somewhere.
def activate_lines(x, y, z, commands):
	i = 0
	#go through all action lines.
	while i < len(commands):
		temp = run_command(x, y, z, commands[i])
		if temp == "end": return 0
		elif temp == "if":
			else_loc, endif_loc = find_if_else_block(commands[i+1:], i+1)
			if (else_loc == -1) or (endif_loc == -1):
				print "surrounding code:"
				for line in commands: print line
				return "bad"
			if activate_lines(x, y, z, commands[i+1:else_loc]) == 0:
				return 0
			i = endif_loc
		elif temp == "else":
			else_loc, endif_loc = find_if_else_block(commands[i+1:], i+1)
			if (else_loc == -1) or (endif_loc == -1):
				print "surrounding code:"
				for line in commands: print line
				return "bad"
			if else_loc != endif_loc:
				if activate_lines(x, y, z, commands[else_loc+1:endif_loc]) == 0:
					return 0
			i = endif_loc
		elif temp == "bad":
			print "surrounding code:"
			for line in commands: print line
		i += 1
	return 1

#Given a block of scripting in array form, starting with the first line
#after the if command in question, return the location of the "else" and
#"endif" associated with the command. corrector is the current position in the
#file as a whole, used to correct for missing part of the array.
def find_if_else_block(commands, corrector):
	num_of_ifs = 0
	else_loc = -1
	endif_loc = -1
	for i in range(len(commands)):
		if commands[i][:2].lower() == "if":
			num_of_ifs += 1
		elif commands[i][:4].lower() == "else" and num_of_ifs == 0:
			else_loc = i + corrector
		elif commands[i][:5].lower() == "endif" and num_of_ifs == 0:
			endif_loc = i + corrector
			if else_loc == -1: else_loc = i + corrector
			break
		elif commands[i][:5].lower() == "endif":
			num_of_ifs -= 1
	if else_loc == -1 or endif_loc == -1:
		print "Unmatched if command. Ending script."
	return else_loc, endif_loc


#Given a string/command, return either 0 (if the command is a number),
#1 (if it is a string), or 2 (if it is an actual command).
def command_type(command):
	command = command.strip()

	#Note that this only checks the first character. This is purposeful, as
	#this function may be called with several commands "stuck together".
	#This means functions cannot start with quotes, numbers, or dash.
	if command[0].isdigit() == 1 or command[0] == "-":
		return 0
	if command[0] == "\"":
		return 1
	else:
		return 2


#Given a string/command that starts with "(", return the location of the
#matching ")". Note that the beginning "(" is required to help prevent
#off-by-one errors.
def match_parenth(command):
	command = command.strip()
	if command[0] != "(":
		print "match_parenth() called with a bad string:"
		print command
		return -1
	s=command[1:]
	par_num = 0
	i = 0
	#This is a while loop to allow for skipping forward when a string is
	#encountered. This allows for the "()" characters to appear in strings.
	while i < len(s):
		if s[i] == "(":
			par_num += 1
		elif s[i] == "\"":
			tmp = match_quotes(s[i:])
			if tmp == -1: break
			i += tmp
			if i == -1: return -1
		elif s[i] == ")":
			if par_num == 0:
				return i
			else:
				par_num -= 1
		i += 1
	print "match_parenth() cannot find the end of this parenthesis pair:"
	print command
	return -1

#Like match_parenth(), but allows beginning characters before the (. Meant for
#matching the end of a command.
def match_command(command):
	command = command.strip()
	tmp = command.find("(")
	if tmp == -1:
		print "match_command() called with a bad string:"
		print command
		return -1

	return match_parenth(command[command.find("("):])+len(command[:command.find("(")])+2


#Given a string/command that starts with ", return the location of the
#matching ". Note that the beginning " is required to help prevent
#off-by-one errors. Also note that this function allows the \" sequence
#for the literal " character.
def match_quotes(command):
	if command[0] != "\"":
		print "match_quotes() called with a bad string:"
		print command
		return -1
	is_code = 0
	s=command[1:]
	for i in range(len(s)):
		if is_code == 0:
			if s[i] == "\"":
				return i + 1
			elif s[i] == "\\":
				is_code = 1
		else:
			is_code = 0
	print "match_quotes() cannot find the end of this string:"
	print command
	return -1

#Given a string, replace the sequence \n with the actual newline character.
def insert_newlines(command):
	return command.replace("\\n", "\n")


#Given a list of ,-separated commands, return an array of the return values
#for each command. Used to parse argument lists.
def run_arguments(x, y, z, commands):
	commands = commands.strip()
	return_vals = []

	#Keep pulling out commands, placing them in return_vals, and shrinking
	#the length of commands. When commands is entirely gone, return return_vals
	while commands:
		commands= commands.strip()
		tmp = command_type(commands)
		if tmp == 0:
			go_to = commands.find(",")
			if go_to == -1: go_to = len(commands)
			return_vals.append([int(commands[:go_to]), 0])
			commands = commands[go_to+1:]
		elif tmp == 1:
			return_vals.append([commands[:match_quotes(commands)+1], 1])
			commands = commands[match_quotes(commands)+1:]
			commands = commands[commands.find(",")+1:]
		elif tmp == 2:
			tmp_command = commands[:match_command(commands)]
			tmp_return_val = run_command(x, y, z, tmp_command)
			tmp = command_type(str(tmp_return_val))
			return_vals.append([tmp_return_val, tmp])
			if tmp_return_val == "end": return "end"
			if tmp_return_val == "bad": return "bad"
			commands = commands[match_command(commands)+1:]
	return return_vals

#Activate one script command. See scripting.txt for details.
#returns either a number, a string (with first and last chars of "),
#"end" (end script), or "bad" (same as end, but also print debugging info).
#x and y are absolute values.
def run_command(x, y, z, command):
	command = command.strip()

	#if command is a number, just return the number.
	if command.isdigit() == 1:
		return_num = int(command)
	elif command[:1] == "-" and command[1:].isdigit() == 1:
		return_num = int(command)

	#if command is a string, just return the string.
	if command[0] == "\"" and command[-1] == "\"":
		return command

	#We now "know" the command is an actual command. Make sure.
	if command.find("(") == -1 or match_parenth(command[command.find("("):]) \
						!= len(command[command.find("("):])-2:
		print "run_command called with a bad string:"
		print command
		return "bad"

	global has_dialog
	switch = command.split("(", 1)[0].lower()
	arg_list = run_arguments(x, y, z, command[command.find("(")+1:-1])
	if arg_list == "end": return "end"
	global just_found

	#This is a mostly alphabetical list of all functions. Do minor
	#input-checking, then call the relevant function. Note that pix and walk
	#are out of order. This is to hopefully speed up processing.

	if switch == "pix":  #change tile picture
		if check_num_args(len(arg_list), 1, 1, "pix"):
			return script_pix(x, y, z, arg_list)
	elif switch == "walk":  #change tile walkability
		if check_num_args(len(arg_list), 1, 1, "walk"):
			return script_walk(x, y, z, arg_list)
	elif switch == "addpix": #add a picture to the tile.
		if check_num_args(len(arg_list), 1, 1, "addpix"):
			return script_addpix(x, y, z, arg_list)
	elif switch == "addoverpix": #add a picture to the tile.
		if check_num_args(len(arg_list), 1, 1, "addoverpix"):
			return script_addoverpix(x, y, z, arg_list)
	elif switch == "addskill": #add a skill
		if check_num_args(len(arg_list), 1, 1, "addskill"):
			return script_addskill(x, y, z, arg_list)
	elif switch == "attack":  #cause creature to attack
		if check_num_args(len(arg_list), 1, 2, "attack"):
			return script_attack(x, y, z, arg_list)
	elif switch == "damage_monster":  #In battle, hurt monster for either
		if check_num_args(len(arg_list), 1, 2, "damage_monster"):
			return script_damage_monster(x, y, z, arg_list)
	elif switch == "delpix": #remove a picture from the tile.
		if check_num_args(len(arg_list), 1, 1, "delpix"):
			return script_delpix(x, y, z, arg_list)
	elif switch == "dialog":  #show a message in a dialog box.
		if check_num_args(len(arg_list), 1, 1, "dialog"):
			return script_dialog(x, y, z, arg_list)
	elif switch == "die":  #process endgame.txt script
		if check_num_args(len(arg_list), 0, 0, "die"):
			return script_die(x, y, z, arg_list)
	elif switch == "end":  #end the script
		if check_num_args(len(arg_list), 0, 0, "end"):
			return script_end(x, y, z, arg_list)
	elif switch == "equip":  #adjust equipment
		if check_num_args(len(arg_list), 2, 2, "equip"):
			return script_equip(x, y, z, arg_list)
	elif switch  == "fade":
		if check_num_args(len(arg_list), 1, 1, "fade"):
			return script_fade(x, y, z, arg_list)
	elif switch  == "find":
		if check_num_args(len(arg_list), 2, 2, "find"):
			return script_find(x, y, z, arg_list)
	elif switch == "gamestat":
		if check_num_args(len(arg_list), 1, 1, "gamestat"):
			return script_gamestat(x, y, z, arg_list)
	elif switch == "generic_dialog":  #Create a generic dialog box
		if check_num_args(len(arg_list), 2, 999, "generic_dialog"):
			return script_generic_dialog(x, y, z, arg_list)
	elif switch == "give":  #Change stats. Note that negative numbers also work
		if check_num_args(len(arg_list), 2, 2, "give"):
			return script_give(x, y, z, arg_list)
	elif switch == "hero":  #change hero pix
		if check_num_args(len(arg_list), 1, 1, "hero"):
			return script_hero(x, y, z, arg_list)
	elif switch == "hurt":  #hurt player (reduced by armor)
		if check_num_args(len(arg_list), 1, 1, "hurt"):
			return script_hurt(x, y, z, arg_list)
	elif switch == "hurt_monster":  #In battle, hurt monster for either
		if check_num_args(len(arg_list), 1, 2, "hurt_monster"):
			return script_hurt_monster(x, y, z, arg_list)
	elif switch == "if":
		if check_num_args(len(arg_list), 1, 3, "if"):
			return script_if(x, y, z, arg_list)
	elif switch == "info":  #display line of text in textbox below main screen
		if check_num_args(len(arg_list), 1, 1, "info"):
			return script_info(x, y, z, arg_list)
	elif switch == "inv":  #inv functions
		if check_num_args(len(arg_list), 2, 2, "inv"):
			return script_inv(x, y, z, arg_list)
	elif switch == "inv_spot":  #return inv item
		if check_num_args(len(arg_list), 1, 1, "inv_spot"):
			return script_inv_spot(x, y, z, arg_list)
	elif switch == "is_equipped": #is the given item equipped?
		if check_num_args(len(arg_list), 1, 1, "is_equipped"):
			return script_is_equipped(x, y, z, arg_list)
	elif switch == "item":  #give item
		if check_num_args(len(arg_list), 1, 1, "item"):
			return script_item(x, y, z, arg_list)
	elif switch == "lose":
		if check_num_args(len(arg_list), 0, 0, "lose"):
			return script_lose(x, y, z, arg_list)
	elif switch == "mapspot":
		if check_num_args(len(arg_list), 4, 4, "mapspot"):
			return script_mapspot(x, y, z, arg_list)
	elif switch == "mapstat":
		if check_num_args(len(arg_list), 2, 2, "mapstat"):
			return script_mapstat(x, y, z, arg_list)
	elif switch == "monster_give_stat":  #In battle, select a monster.
		if check_num_args(len(arg_list), 3, 3, "monster_give_stat"):
			return script_monster_give_stat(x, y, z, arg_list)
	elif switch == "monster_stat":  #In battle, select a monster.
		if check_num_args(len(arg_list), 2, 2, "monster_stat"):
			return script_monster_stat(x, y, z, arg_list)
	elif switch == "monster_select":  #In battle, select a monster.
		if check_num_args(len(arg_list), 0, 0, "monster_select"):
			return script_monster_select(x, y, z, arg_list)
	elif switch == "move":  #move the player
		if check_num_args(len(arg_list), 3, 3, "move"):
			return script_move(x, y, z, arg_list)
	elif switch == "pass":  #do nothing
		if check_num_args(len(arg_list), 0, 0, "pass"):
			return script_pass(x, y, z, arg_list)
	elif switch == "printvars": #debug: print all variables
		if check_num_args(len(arg_list), 0, 0, "printvars"):
			return script_printvars(x, y, z, arg_list)
	elif switch == "question":  #yes/no dialog box
		if check_num_args(len(arg_list), 1, 1, "question"):
			return script_question(x, y, z, arg_list)
	elif switch == "refresh": #refresh the screen manually.
		if check_num_args(len(arg_list), 0, 0, "refresh"):
			return script_refresh(x, y, z, arg_list)
	elif switch == "rng":  #Random Number Generator
		if check_num_args(len(arg_list), 2, 2, "rng"):
			return script_rng(x, y, z, arg_list)
	elif switch == "run":  #Run the actions of a different tile.
		if check_num_args(len(arg_list), 3, 3, "run"):
			return script_run(x, y, z, arg_list)
	elif switch == "set":  #set variable (in g.var_list)
		if check_num_args(len(arg_list), 2, 3, "set"):
			return script_set(x, y, z, arg_list)
	elif switch == "skill":  #skill actions
		if check_num_args(len(arg_list), 2, 2, "skill"):
			return script_skill(x, y, z, arg_list)
	elif switch == "stat":  #return stat
		if check_num_args(len(arg_list), 1, 1, "stat"):
			return script_stat(x, y, z, arg_list)
	elif switch == "store":  #enter store
		if check_num_args(len(arg_list), 1, 1, "store"):
			return script_store(x, y, z, arg_list)
	elif switch == "take":  #Drop item, by name.
		if check_num_args(len(arg_list), 1, 1, "take"):
			return script_take(x, y, z, arg_list)
	elif switch == "var":  #return variable (in g.var_list)
		if check_num_args(len(arg_list), 1, 1, "var"):
			return script_var(x, y, z, arg_list)
	elif switch == "wall_n":  #change tile wall values
		if check_num_args(len(arg_list), 1, 1, "wall_n"):
			return script_wall_n(x, y, z, arg_list)
	elif switch == "wall_s":  #change tile wall values
		if check_num_args(len(arg_list), 1, 1, "wall_s"):
			return script_wall_s(x, y, z, arg_list)
	elif switch == "wall_e":  #change tile wall values
		if check_num_args(len(arg_list), 1, 1, "wall_e"):
			return script_wall_e(x, y, z, arg_list)
	elif switch == "wall_w":  #change tile wall values
		if check_num_args(len(arg_list), 1, 1, "wall_w"):
			return script_wall_w(x, y, z, arg_list)
	elif switch == "win":  #process wingame.txt script
		if check_num_args(len(arg_list), 0, 0, "win"):
			return script_win(x, y, z, arg_list)
	else:
		print "Bad action of: " + switch + " given."
		return "bad"
	#This falls through whenever check_num_args returns false.
	print "argument list:"
	print arg_list

#Make sure the number of arguments to a function is good.
def check_num_args(num_of_args, lower_num, upper_num, command_name):
	if num_of_args < lower_num or num_of_args > upper_num:
		print command_name + " called with wrong number of arguments."
		return 0
	return 1

#Make sure the script arguments are of the right type.
#(0=number, 1=string, 2=don't care)
#Note that all "command" arguments should have disappeared by the time this
#function is called.
def check_types_args(args, arg_types, command_name, quiet=0):
	for i in range(len(arg_types)):
		if args[i] == "bad": return 0
		if args[i][1] != arg_types[i] and arg_types[i] != 2:
			if quiet == 0:
				print command_name + " called with wrong type of arguments:"
				print args
			return 0
	return 1



#Following are the actual functions used by the various scripting commands.
#All take an array of script arguments, and the xyz location.
#Thay all return something that can be used by the scripting
#engine. (number, string, end, or bad)

def script_addpix(x, y, z, argument_array): #add a picture to the tile.
	if check_types_args(argument_array, [1], "addpix") == 0:
		return "bad"

	if not g.tiles.has_key(argument_array[0][0][1:-1]):
		print "Tile "+argument_array[0][0][1:-1]+" does not exist in map "+\
			g.maps[z].name
		return 0
	g.maps[z].field[y][x].add_pix(g.tiles[argument_array[0][0][1:-1]])
	return 1

def script_addoverpix(x, y, z, argument_array): #add a picture to the tile.
	if check_types_args(argument_array, [1], "addoverpix") == 0:
		return "bad"

	g.maps[z].field[y][x].add_over_pix(g.tiles[argument_array[0][0][1:-1]])
	return 1

def script_addskill(x, y, z, argument_array): #add a skill
	if check_types_args(argument_array, [1], "addskill") == 0:
		return "bad"

	temp = g.findskill(argument_array[0][0][1:-1])
	if temp == -1:
		print "Unknown skill: " + argument_array[0][0][1:-1]
		return 0
	else:
		return g.add_skill(temp)

def script_attack(x, y, z, argument_array):  #cause creature to attack
	if check_types_args(argument_array, [1], "attack") == 0:
		return "bad"

	temp = -1
	if len(argument_array) == 2:
		if check_types_args(argument_array, [1, 1], "attack") == 0:
			return "bad"
		#battle random monster
		i = g.mapname2zgrid(argument_array[1][0][1:-1])
		temp = monster.find_level_monster(i)
	else:
		#battle named monster
		temp_name = argument_array[0][0][1:-1].lower()
		for monster_num in range(len(monster.monster_groups)):
			if monster.monster_groups[monster_num].name.lower() == temp_name:
				temp = monster_num
				break
		else:
			print "monster " + temp_name + " not found"
	#if there exists a monster to battle:
	if temp != -1:
		main.key_down = [False, False, False, False]
		return main.start_battle(temp)
	return 0

def script_damage_monster(x, y, z, argument_array):  #In battle, hurt monster for either
		#adj_attack points, or Command points. *NOT* reduced by armor.
	if (g.cur_window != "battle" and g.cur_window != "battle_item" and
		g.cur_window != "battle_skill"):
		print "damage_monster called outside of battle."
		return -1

	mon_num = battle.select_monster()
	if mon_num == -1: return 0

	if len(argument_array) == 0: #Basic damage_monster command.
		battle.monster_hurt(mon_num, player.adj_attack)
		return 1
	else: #Of the format damage_monster Command.
		if check_types_args(argument_array, [0], "damage_monster") == 0:
			return "bad"
		battle.monster_hurt(mon_num, argument_array[0][0])
		return 1

def script_delpix(x, y, z, argument_array): #remove a picture from the tile.
	if check_types_args(argument_array, [1], "delpix") == 0:
		return "bad"

	try:
		g.maps[z].field[y][x].del_pix(g.tiles[argument_array[0][0][1:-1]])
		main.refresh_tile(x, y, z)
		return 1
	except ValueError:
		return 0

def script_dialog(x, y, z, argument_array):  #show a message in a dialog box.
	if check_types_args(argument_array, [1], "dialog") == 0:
		return "bad"
	main.show_dialog(insert_newlines(argument_array[0][0][1:-1]))
	return 1

def script_die(x, y, z, argument_array):  #process endgame.txt script
	player.hp = -1
	activate_lines(x, y, z, g.endgame_act)
	return "end"

def script_end(x, y, z, argument_array):  #end the script
	return "end"

def script_equip(x, y, z, argument_array): #adjust equipment
	if check_types_args(argument_array, [1, 1], "equip") == 0:
		return "bad"

	switch2 = argument_array[0][0][1:-1].lower()
	switch3 = argument_array[1][0][1:-1].lower()

	if switch2 == "in_slot":
		if switch3 == "weapon": equip_loc = 0
		elif switch3 == "armor": equip_loc = 1
		elif switch3 == "shield": equip_loc = 2
		elif switch3 == "helmet": equip_loc = 3
		elif switch3 == "gloves": equip_loc = 4
		elif switch3 == "boots": equip_loc = 5
		else:
			print "unknown equipment space of " + switch3
			return "bad"
		if player.equip[equip_loc] == -1: return "\"\""
		return "\""+g.item.item[player.equip[equip_loc]].name+"\""
	if switch2 == "has":
		for i in range(len(player.equip)):
			if switch3 == g.item.item[player.equip[i]].name.lower():
				return 1
		return 0
	elif switch2 == "take":
		for i in range(len(player.equip)):
			if switch3 == g.item.item[player.equip[i]].name.lower():
				player.equip[i] = -1
				return 1
		return 0
	elif switch2 == "give":
		item_loc = g.item.finditem(switch3)
		if item_loc == -1:
			print "unknown item " + switch3
			return "bad"
		if g.item.item[item_loc].type > 5:
			print "item "+switch3+" cannot be worn"
			return "bad"
		player.equip[g.item.item[item_loc].type] = item_loc
		return 1
	else:
		print "unknown switch for equip(): "+switch2
		return "bad"

def script_fade(x, y, z, argument_array):
	if check_types_args(argument_array, [0], "fade") == 0:
		return "bad"

	if argument_array[0][1] == 0:
		for i in range(40):
			g.pygame.time.wait(15)
			g.screen.fill(g.colors["black"], (0, i*12, g.screen_size[0], 12))
			g.screen.fill(g.colors["black"], (0, g.screen_size[1]-i*12-12,
				g.screen_size[0], 12))
			g.screen.fill(g.colors["black"], (0, g.screen_size[1]/2+i*12,
				g.screen_size[0], 12))
			g.screen.fill(g.colors["black"], (0, g.screen_size[1]/2-i*12-12,
				g.screen_size[0], 12))
			g.pygame.display.flip()

def script_find(x, y, z, argument_array):
	if check_types_args(argument_array, [1, 2], "find") == 0:
		return "bad"

	founditem = argument_array[0][0][1:-1]
	if argument_array[1][1] == 0:
		amount = int(argument_array[1][0])
	else:
		amount = argument_array[1][0][1:-1]

	main.print_message("You found " + str(amount) + " " + founditem + ".")
	has_dialog = 1
	if main.show_yesno("You found " + str(amount) + " " + founditem +
			"! Would you like to pick it up ?"):
		if(founditem.lower() == "gold"):
			player.give_stat("gold", int(amount))
			main.print_message("You picked up " + str(amount) + " " +
					founditem + ".")
			has_dialog = 0
			return 1
		if( g.item.take_inv_item(g.item.finditem(founditem)) != -1):
			main.print_message("You picked up " + str(amount) + " " +
					founditem + ".")
			has_dialog = 0
			return 1
		else:
			main.print_message("You have no room for the " +
					founditem + ".")
			has_dialog = 0
			return 0
	else:
		has_dialog = 0
		return 0

def script_gamestat(x, y, z, argument_array):
	if check_types_args(argument_array, [1], "gamestat") == 0:
		return "bad"

	switch2 = argument_array[0][0][1:-1].lower()

	if switch2 == "loc":
		return "\"" + g.cur_window + "\""
	elif switch2 == "difficulty":
		return int(g.difficulty)
	elif switch2 == "gamename":
		return "\"" + g.game_name + "\""
	elif switch2 == "x":
		return int(g.xgrid)
	elif switch2 == "y":
		return int(g.ygrid)
	elif switch2 == "newx":
		return int(x)
	elif switch2 == "newy":
		return int(y)
	elif switch2 == "mapname":
		return "\"" + g.maps[g.zgrid].name + "\""
	else: print "Unknown stat: " + switch2
	return "bad"

def script_generic_dialog(x, y, z, argument_array):  #Custom dialog box.
	if check_types_args(argument_array, [1], "generic_dialog") == 0:
		return "bad"
	line = argument_array.pop(0)
	line = insert_newlines(line[0][1:-1])
	dialog_array = []
	for entry in argument_array:
		if check_types_args([entry], [1], "generic_dialog") == 0:
			return "bad"
		dialog_array.append(entry[0][1:-1])
	return main.show_popup(line, dialog_array)

def script_give(x, y, z, argument_array):  #Change stats. Note that negative numbers also work
	if check_types_args(argument_array, [1, 2], "give") == 0:
		return "bad"

	switch2 = argument_array[0][0][1:-1].lower()

	if switch2 == "name":
		if check_types_args(argument_array, [1, 1], "give") == 0:
			return "bad"

		#note that name is not interpreted as a command.
		player.name = interpret_line(argument_array[1][0][1:-1])
		main.refresh_bars()
		main.refresh_inv_icon()
		return 1

	else:
		if check_types_args(argument_array, [1, 0], "give") == 0:
			return "bad"
		set_to = int(argument_array[1][0])

	if switch2 == "hp": player.give_stat("hp", set_to)
	elif switch2 == "ep": player.give_stat("ep", set_to)
	elif switch2 == "maxhp": player.give_stat("maxhp", set_to)
	elif switch2 == "maxep": player.give_stat("maxep", set_to)
	elif switch2 == "attack": player.give_stat("attack", set_to)
	elif switch2 == "defense": player.give_stat("defense", set_to)
	elif switch2 == "adj_maxhp": player.give_stat("adj_maxhp", set_to)
	elif switch2 == "adj_maxep": player.give_stat("adj_maxep", set_to)
	elif switch2 == "adj_attack": player.give_stat("adj_attack", set_to)
	elif switch2 == "adj_defense": player.give_stat("adj_defense", set_to)
	elif switch2 == "gold": player.give_stat("gold", set_to)
	elif switch2 == "exp": player.add_exp(set_to)
	elif switch2 == "skillpoints": player.give_stat("skillpoints", set_to)
	else: print "Unknown stat: " + switch2
	main.refresh_bars()
	main.refresh_inv_icon()
	if set_to == 0: return 0
	else: return 1

def script_hero(x, y, z, argument_array):  #change hero pix
	if check_types_args(argument_array, [1], "hero") == 0:
		return "bad"

	player.cur_hero = "people/" + argument_array[0][0][1:-1] + ".png"
	g.g.allow_change_hero = 0
	main.refreshmap()

def script_hurt(x, y, z, argument_array):  #hurt player (reduced by armor)
	if check_types_args(argument_array, [0], "hurt") == 0:
		return "bad"

	#interpret the second part of the command
	damage = g.die_roll(1, int(argument_array[0][0]) + 2)
	damage = damage - g.die_roll(1, player.adj_defense + 2)
	player.give_stat("hp", -1*damage)
	return 1

def script_hurt_monster(x, y, z, argument_array):  #In battle, hurt monster for either
		#adj_attack points, or Command points. Reduced by armor.
	if (g.cur_window != "battle" and g.cur_window != "battle_item" and
		g.cur_window != "battle_skill"):
		print "hurt_monster called outside of battle."
		return -1

	mon_num = battle.select_monster()
	if mon_num == -1: return 0

	if len(argument_array) == 0: #Basic hurt_monster command.
		battle.attack_monster(mon_num, player.adj_attack)
		return 1
	else: #Of the format hurt_monster Command.
		if check_types_args(argument_array, [0], "hurt_monster") == 0:
			return "bad"

		battle.attack_monster(mon_num, argument_array[0][0])
		return 1

def script_if(x, y, z, argument_array):
	if len(argument_array) == 1:
		argument_array.append(["\"==\"", 1])
		argument_array.append([1, 0])
	if check_types_args(argument_array, [2, 1, 2], "if") == 0:
		return "bad"

	#Note that comparisons between numbers and strings works in Python.
	#This makes my job easier.
	#Also note that I am not stripping off the beginning/end quotes from
	#strings. This is because, since I am not doing this to either (possible)
	#string, equality still works.
	line_return1 = argument_array[0][0]
	compare = argument_array[1][0][1:-1]
	line_return2 = argument_array[2][0]

	#something that should end the script
	if (line_return1 == "end" or line_return2 == "end"):
		return "end"

	if (compare == "<="):
		if (line_return1 <= line_return2): return "if"
		else: return "else"
	elif (compare == ">="):
		if (line_return1 >= line_return2): return "if"
		else: return "else"
	elif (compare == "=" or compare == "=="):
		if (line_return1 == line_return2): return "if"
		else: return "else"
	elif (compare == "!="):
		if (line_return1 != line_return2): return "if"
		else: return "else"
	elif (compare == "<"):
		if (line_return1 < line_return2): return "if"
		else: return "else"
	elif (compare == ">"):
		if (line_return1 > line_return2): return "if"
		else: return "else"
	else: #of the form eg "if var something
		print "if command was given an unknown comparison: " + compare
		return 0

def script_info(x, y, z, argument_array):  #display line of text in textbox below main screen
	if check_types_args(argument_array, [2], "info") == 0:
		return "bad"

	has_dialog = 1
	if argument_array[0][1] == 0: message_txt = str(argument_array[0][0])
	else: message_txt = argument_array[0][0][1:-1]
	main.print_message(message_txt)
	has_dialog = 0
	return 1

def script_inv(x, y, z, argument_array): #inventory functions.
	if check_types_args(argument_array, [1, 1], "inv") == 0:
		return "bad"

	temp = g.item.finditem(argument_array[1][0][1:-1])
	if temp == -1:
		print "Item " + argument_array[1][0][1:-1] + " does not exist."
		return "bad"

	switch2 = argument_array[0][0][1:-1].lower()

	if switch2 == "has":
		if g.item.find_inv_item(temp) > -1: return 1
		else: return 0
	elif switch2 == "take":
		temp = g.item.find_inv_item(temp)
		if temp > -1:
			g.item.drop_inv_item(temp)
			return 1
		else: return 0
	elif switch2 == "give":
		if g.item.take_inv_item(temp) == -1:
			return 0
		else: return 1
	elif switch2 == "use":
		tmptype = g.item.item[temp].type
		if (tmptype != 11 and tmptype != 12 and tmptype != 14 and tmptype != 15
							and tmptype != 16 and tmptype != 17):
			print "item " + g.item.item[temp].name + " cannot be used."
			return "bad"
		if (g.cur_window == "battle" or g.cur_window == "battle_item" or
		g.cur_window == "battle_skill") and (tmptype != 16):
			battle.useitem(temp, 1)
		elif (g.cur_window != "battle" and g.cur_window != "battle_item" and
		g.cur_window != "battle_skill") and (tmptype == 11 or tmptype == 16 or
							tmptype == 17):
			main.inv.use_item(temp)
			return 1
		else:
			print "item " + g.item.item[temp].name + " cannot be used in " \
				+ g.cur_window
			return "bad"
	elif switch2 == "type":
		return g.item.item[temp].type
	elif switch2 == "quality":
		return g.item.item[temp].quality
	elif switch2 == "price":
		return g.item.item[temp].price
	elif switch2 == "value":
		return g.item.item[temp].value
	elif switch2 == "description":
		return "\""+g.item.item[temp].description+"\""
	elif switch2 == "picturename":
		return "\""+g.item.item[temp].picturename+"\""
	elif switch2 == "hp_bonus":
		return g.item.item[temp].hp_bonus
	elif switch2 == "ep_bonus":
		return g.item.item[temp].ep_bonus
	elif switch2 == "attack_bonus":
		return g.item.item[temp].attack_bonus
	elif switch2 == "defense_bonus":
		return g.item.item[temp].defense_bonus
	else:
		print "Unknown switch " + argument_array[0][0][1:-1] + "found."
		return "bad"

def script_inv_spot(x, y, z, argument_array): #return name of given inv item.
	if check_types_args(argument_array, [0], "inv_spot") == 0:
		return "bad"

	#hardcoding is temporary.
	if argument_array[0][0] < 0 or argument_array[0][0] > 27:
		print "inv location is impossible: " + str(argument_array[0][0])
		return "bad"
	if g.item.inv[argument_array[0][0]] == -1: return "\"\""
	return "\""+g.item.item[g.item.inv[argument_array[0][0]]].name+"\""

def script_is_equipped(x, y, z, argument_array): #is the given item equipped?
	if check_types_args(argument_array, [1], "is_equipped") == 0:
		return "bad"

	match = argument_array[0][0][1:-1].lower()
	for item_title in player.equip:
		if item_title == -1: continue
		if g.item.item[item_title].name.lower() == match:
			return 1
	return 0

def script_item(x, y, z, argument_array):  #give item
	argument_array = [["\"give\"", 1], argument_array[0]]
	tmp= script_inv(x, y, z, argument_array)
	if check_types_args(argument_array, [1], "item") == 0:
		return "bad"

	if g.item.take_inv_item(g.item.finditem(argument_array[0][0][1:-1])) == -1:
		return 0
	else: return 1

def script_lose(x, y, z, argument_array):
	player.hp = -1
	main.close_window()
	return "end"

def script_mapspot(x, y, z, argument_array):
	if check_types_args(argument_array, [1, 0, 0, 1], "mapspot") == 0:
		return "bad"

	tmpzgrid = g.mapname2zgrid(argument_array[0][0][1:-1])
	if tmpzgrid == -1: return "bad"

	tmpxgrid = argument_array[1][0]
	tmpygrid = argument_array[2][0]

	switch2 = argument_array[3][0][1:-1].lower()

	if switch2 == "walk":
		return g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].walk
	if switch2 == "pix":
		return "\""+g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].name+"\""
	if switch2 == "num_of_dropped":
		return len(g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].items)
	if switch2 == "num_of_addpix":
		return len(g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].addpix)
	if switch2 == "num_of_addoverpix":
		return len(g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].addoverpix)
	if switch2 == "wall_n":
		return g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].wall_n
	if switch2 == "wall_s":
		return g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].wall_s
	if switch2 == "wall_w":
		return g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].wall_w
	if switch2 == "wall_e":
		return g.maps[tmpzgrid].field[tmpygrid][tmpxgrid].wall_e
	if switch2 == "within_bounds":
		if tmpygrid < len(g.maps[tmpzgrid].field):
			if tmpxgrid < len(g.maps[tmpzgrid].field[tmpygrid]): return 1
			else: return 0
		else: return 0
	if switch2 == "y_bound":
		return len(g.maps[tmpzgrid].field)
	if switch2 == "x_bound":
		return len(g.maps[tmpzgrid].field[0])
	else:
		print "unknown switch "+switch2+" in mapspot."
		print "possible: walk, pix, num_of_dropped, num_of_addpix,"
		print "num_of_addoverpix, wall_n, wall_s, wall_w, wall_e,"
		print "within_bounds, y_bound, or x_bound."
		return "bad"

def script_mapstat(x, y, z, argument_array):
	if check_types_args(argument_array, [1, 1], "mapstat") == 0:
		return "bad"
	switch2 = argument_array[0][0][1:-1].lower()
	switch3 = argument_array[1][0][1:-1]

	if switch2 == "addmonster":
		switch3 = interpret_line(switch3)
		g.maps[z].monster.append(switch3)
		return 1
	elif switch2 == "delmonster":
		try:
			switch3 = interpret_line(switch3)
			g.maps[z].monster.remove(switch3)
			return 1
		except ValueError: return 0
	elif switch2 == "hero_bg":
		switch3 = interpret_line(switch3)
		g.maps[z].hero_suffix = switch3
		return 1
	elif switch2 == "battle_bg":
		switch3 = interpret_line(switch3)
		g.maps[z].battle_background = g.backgrounds[switch3]
		g.maps[z].battle_background_name = switch3
		return 1
	elif switch2 == "change_titlebar":
		switch3 = interpret_line(switch3)
		g.game_name = switch3
		g.pygame.display.set_caption(g.game_name)
		return 1

#In battle, change the stats of the given monster
def script_monster_give_stat(x, y, z, argument_array):
	if check_types_args(argument_array, [2, 1, 2], "monster_give_stat") == 0:
		return "bad"
	if (g.cur_window != "battle" and g.cur_window != "battle_item" and
		g.cur_window != "battle_skill"):
		print "monster_stat called outside of battle."
		return -1

	if (type(argument_array[0][0])=="str" and
						argument_array[0][0].lower() == "\"all\""):
		for i in range(len(battle.monster_list)):
			if battle.monster_list[i].hp > 0:
				tmp = [[i][0]]
				tmp.append(argument_array[1])
				tmp.append(argument_array[2])
				script_monster_give_stat(x, y, z, tmp)
		return 1

	mon_num = int(argument_array[0][0])
	switch3 = argument_array[1][0][1:-1].lower()
	if switch3 == "name":
		battle.monster_list[mon_num].name = \
			interpret_line(argument_array[2][0][1:-1])
	elif switch3 == "hp":
		if argument_array[2][0] > 0:
			battle.monster_list[mon_num].hp += argument_array[2][0]
		else:
			battle.monster_hurt(mon_num, (-1)*argument_array[2][0])
	elif switch3 == "maxhp":
		battle.monster_list[mon_num].maxhp += argument_array[2][0]
	elif switch3 == "attack":
		battle.monster_list[mon_num].attack += argument_array[2][0]
	elif switch3 == "defense":
		battle.monster_list[mon_num].defense += argument_array[2][0]
	elif switch3 == "gold":
		battle.monster_list[mon_num].gold += argument_array[2][0]
	elif switch3 == "exp":
		battle.monster_list[mon_num].exp += argument_array[2][0]
	else:
		print "Bad stat of " + switch3 + " used in monster_give_stat."
		return -1
	battle.set_description_text(mon_num)


#In battle, return the stats of the given monster
def script_monster_stat(x, y, z, argument_array):
	if check_types_args(argument_array, [0, 1], "monster_stat") == 0:
		return "bad"
	if (g.cur_window != "battle" and g.cur_window != "battle_item" and
		g.cur_window != "battle_skill"):
		print "monster_stat called outside of battle."
		return -1

	switch2 = argument_array[0][0]

	#Choose the monster to examine
	mon_num = int(switch2)
	if mon_num == -1: return -1

	#Choose the stat to examine
	switch3 = argument_array[1][0][1:-1].lower()
	if switch3 == "name":
		return battle.monster_list[mon_num].name
	elif switch3 == "hp":
		return battle.monster_list[mon_num].hp
	elif switch3 == "maxhp":
		return battle.monster_list[mon_num].maxhp
	elif switch3 == "attack":
		return battle.monster_list[mon_num].attack
	elif switch3 == "defense":
		return battle.monster_list[mon_num].defense
	elif switch3 == "gold":
		return battle.monster_list[mon_num].gold
	elif switch3 == "exp":
		return battle.monster_list[mon_num].exp
	else:
		print "Bad stat of " + switch3 + " used in monster_stat."
		return -1

def script_monster_select(x, y, z, argument_array):  #In battle, ask the player to
									#select a monster
	if (g.cur_window != "battle" and g.cur_window != "battle_item" and
		g.cur_window != "battle_skill"):
		print "monster_select called outside of battle."
		return -1

	mon_num = battle.select_monster()
	if mon_num == -1: return -1
	return mon_num

def script_move(x, y, z, argument_array):  #move the player
	if check_types_args(argument_array, [1, 0, 0], "move") == 0:
		return "bad"

	if debug == 1:
		tmp = clock()

	g.xgrid = int(argument_array[1][0])
	g.ygrid = int(argument_array[2][0])

	curr_zgrid = g.zgrid
	temp_zgrid = g.mapname2zgrid(argument_array[0][0][1:-1])
	if temp_zgrid != -1:
		g.zgrid = temp_zgrid

	if curr_zgrid != g.zgrid:
		main.process_onload()
	main.refreshmap()
	if curr_zgrid == g.zgrid:
		g.pygame.time.wait(90)
	g.allow_move = 0
	if debug == 1:
		print clock() - tmp
	return 1

def script_pass(x, y, z, argument_array):  #do nothing
	return 1

def script_pix(x, y, z, argument_array):  #change tile picture
	if check_types_args(argument_array, [1], "pix") == 0:
		return "bad"

	g.maps[z].field[y][x].pix = g.tiles[argument_array[0][0][1:-1]]
	g.maps[z].field[y][x].name = argument_array[0][0][1:-1]
	g.maps[z].field[y][x].addpix = []
	return 1

def script_printvars(x, y, z, argument_array): #debug: print all variables
	print g.var_list
	return 1

def script_question(x, y, z, argument_array):  #yes/no dialog box
	if check_types_args(argument_array, [1], "question") == 0:
		return "bad"

	has_dialog = 1
	if main.show_yesno(str(insert_newlines(argument_array[0][0][1:-1]))):
		has_dialog = 0
		return 1
	else:
		has_dialog = 0
		return 0

def script_refresh(x, y, z, argument_array): #refresh the screen manually.
	main.refreshmap()
	return 1

def script_rng(x, y, z, argument_array):  #Random Number Generator
	if check_types_args(argument_array, [0, 0], "rng") == 0:
		return "bad"

	temp = g.die_roll(1, int(argument_array[1][0]))
	if int(argument_array[0][0]) >= temp:
		return temp
	else: return 0

def script_run(x, y, z, argument_array):  #Run the actions of a different tile.
	if check_types_args(argument_array, [1, 0, 0], "run") == 0:
		return "bad"

	z2 = g.mapname2zgrid(argument_array[0][0][1:-1])
	if z2 == -1:
		z2 = g.zgrid
	x2 = int(argument_array[1][0])
	y2 = int(argument_array[2][0])

	#if there are no actions, leave immediately
	if len(g.maps[z2].field[y2][x2].actions) == 0: return 1
	#go through all action lines.
	return activate_lines(x2, y2, z2, g.maps[z2].field[y2][x2].actions)

def script_set(x, y, z, argument_array):  #set variable (in g.var_list)
	if len(argument_array) == 2:
		argument_array = [argument_array[0], ["\"=\"", 1], argument_array[1]]

	if check_types_args(argument_array, [1, 1, 2], "set") == 0:
		return "bad"

	command2 = argument_array[0][0][1:-1].strip().lower()

	operation_char = argument_array[1][0][1:-1]
	if len(operation_char) != 1:
		print "set command called with unknown operator: " + operation_char
		return "bad"

	if argument_array[2][1] == 0: #int
		set_to = int(argument_array[2][0])
	elif argument_array[2][1] == 1: #string
		set_to = argument_array[2][0][1:-1]
		set_to = interpret_line(set_to)

	if operation_char == "=":
		g.var_list[command2] = set_to
		return 1

	#All the following operations require both variables to be numbers. Confirm.

	#Make sure the number to add is a number.
	if argument_array[2][1] == 1:
		print "set cannot add a string to a variable."
		return "bad"

	#Make sure the var to change exists.
	if g.var_list.has_key(command2) == 0:
		g.var_list[command2] = 0

	#Make sure the var to change is a number.
	if type(g.var_list[command2]) == str:
		if (g.var_list[command2].isdigit() == 1) or \
								(g.var_list[command2][0] == "-" and \
								g.var_list[command2][1:].isdigit() == 1):
			g.var_list[command2] = int(g.var_list[command2])
		else:
			print "set cannot add a variable to a string."
			return "bad"

	#Now we know that both numbers are actually numbers. Add them together.
	if operation_char == "+":
		g.var_list[command2] = g.var_list[command2] + set_to
		return 1
	elif operation_char == "-":
		g.var_list[command2] = g.var_list[command2] - set_to
		return 1
	elif operation_char == "*":
		g.var_list[command2] = g.var_list[command2] * set_to
		return 1
	elif operation_char == "/":
		g.var_list[command2] = g.var_list[command2] / set_to
		return 1
	elif operation_char == "%":
		g.var_list[command2] = g.var_list[command2] % set_to
		return 1
	elif operation_char == "^":
		g.var_list[command2] = pow(g.var_list[command2], set_to)
		return 1
	else:
		print "set command called with unknown operator: " + operation_char
		print "possible operators: +, -, *, /, %, ^."
		return "bad"

def script_skill(x, y, z, argument_array):  #skill functions
	if check_types_args(argument_array, [2, 2], "skill") == 0:
		return "bad"

	temp = g.findskill(argument_array[1][0][1:-1])
	if temp == -1:
		print "Skill " + argument_array[1][0][1:-1] + " does not exist."
		return "bad"

	if argument_array[0][0][1:-1].lower() == "has":
		if g.player.skill[temp][5] > 0: return 1
		else: return 0
	elif argument_array[0][0][1:-1].lower() == "take":
		if g.player.skill[temp][5] > 0:
			g.player.skill[temp][5] = 0
			return 1
		else:
			g.player.skill[temp][5] = 0
			return 0
	elif argument_array[0][0][1:-1].lower() == "give":
		if g.player.skill[temp][5] > 0:
			g.player.skill[temp][5] = 1
			return 0
		else:
			g.player.skill[temp][5] = 1
			return 1
	elif argument_array[0][0][1:-1].lower() == "use":
		if (g.cur_window != "battle" and g.cur_window != "battle_item" and
				g.cur_window != "battle_skill"):
			print "Cannot use skills outside of battle."
			return "bad"
		battle.useskill(temp, 1)
		return 1
	else:
		print "Unknown switch " + argument_array[0][0][1:-1] + "found."
		return "bad"

def script_stat(x, y, z, argument_array):  #return stat
	if check_types_args(argument_array, [1], "stat") == 0:
		return "bad"

	switch2 = argument_array[0][0][1:-1].lower()
	if switch2 == "name": return "\"" + player.name + "\""
	elif switch2 == "hp": return player.hp
	elif switch2 == "ep": return player.ep
	elif switch2 == "maxhp": return player.maxhp
	elif switch2 == "maxep": return player.maxep
	elif switch2 == "attack": return player.attack
	elif switch2 == "defense": return player.defense
	elif switch2 == "adj_maxhp": return player.adj_maxhp
	elif switch2 == "adj_maxep": return player.adj_maxep
	elif switch2 == "adj_attack": return player.adj_attack
	elif switch2 == "adj_defense": return player.adj_defense
	elif switch2 == "gold": return player.gold
	elif switch2 == "exp": return player.exp
	elif switch2 == "level": return player.level
	elif switch2 == "skillpoints": return player.skillpoints
	else:
		print "Unknown stat: " + switch2
		return 0

def script_store(x, y, z, argument_array):  #enter store
	if check_types_args(argument_array, [1], "store") == 0:
		return "bad"

	has_dialog = 1
	main.enter_store(argument_array[0][0][1:-1])
	has_dialog = 0
	return 1

def script_take(x, y, z, argument_array):  #Drop item, by name.
	argument_array = [["\"take\"", 1], argument_array[0]]
	return script_inv(x, y, z, argument_array)

	if check_types_args(argument_array, [1], "take") == 0:
		return "bad"

	temp = g.item.find_inv_item(g.item.finditem(argument_array[0][0][1:-1]))
	if temp == -1:
		return 0
	else:
		g.item.drop_inv_item(temp)
		return 1

def script_var(x, y, z, argument_array):  #return variable (in g.var_list)
	if check_types_args(argument_array, [1], "var") == 0:
		return "bad"

	#Strip beginning/ending quotes.
	command2 = argument_array[0][0][1:-1].lower().strip()
	if (g.var_list.has_key(command2)):
		try:
			if g.var_list[command2].isdigit():
				return int(g.var_list[command2])
			else: return "\"" + g.var_list[command2] + "\""
		except AttributeError:
			#This gets called when the var is an actual number. (and thus
			#has no isdigit() attribute)
			return int(g.var_list[command2])
	else: return 0

def script_walk(x, y, z, argument_array):  #change tile walkability
	if check_types_args(argument_array, [0], "walk") == 0:
		return "bad"
	g.maps[z].field[y][x].walk = argument_array[0][0]
	return_num = 1

def script_wall_n(x, y, z, argument_array):  #change tile wall values
	if check_types_args(argument_array, [0], "wall_n") == 0:
		return "bad"
	g.maps[z].field[y][x].wall_n = argument_array[0][0]
	return 1

def script_wall_s(x, y, z, argument_array):  #change tile wall values
	if check_types_args(argument_array, [0], "wall_s") == 0:
		return "bad"
	g.maps[z].field[y][x].wall_s = argument_array[0][0]
	return 1

def script_wall_e(x, y, z, argument_array):  #change tile wall values
	if check_types_args(argument_array, [0], "wall_e") == 0:
		return "bad"
	g.maps[z].field[y][x].wall_e = argument_array[0][0]
	return 1

def script_wall_w(x, y, z, argument_array):  #change tile wall values
	if check_types_args(argument_array, [0], "wall_w") == 0:
		return "bad"
	g.maps[z].field[y][x].wall_w = argument_array[0][0]
	return 1

def script_win(x, y, z, argument_array):  #process wingame.txt script
	return activate_lines(x, y, z, g.wingame_act)

