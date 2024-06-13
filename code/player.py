#file: player.py
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

#This file controls the player info

import g

#player definition.
class player_class:
	def __init__(self):
		self.name = ""
		self.hp = 0
		self.ep = 0
		self.maxhp = 0
		self.maxep = 0
		self.attack = 0
		self.defense = 0
		self.gold = 0
		self.exp = 0
		self.level = 0
		self.skillpoints = 1

		#stores attack/defense/hp/ep, adjusted by equipment.
		#kept correct by main.refreshmap(). Use these for calculations.
		self.adj_attack = 0
		self.adj_defense = 0
		self.adj_maxhp = 0
		self.adj_maxep = 0

		#Name of current hero picture.
		self.cur_hero = "people/hero_w.png"

		#skills array. Each skill is a separate line in the array. Each line goes:
		#name, effect, level, price, description, acquired, scripting (if any),
		#then picture.
		#effect is an integer that tells battle.py which case in a select to pick.
		#level is the skillpoints required to get the skill,
		#price is the ep needed to use.
		#acquired tells if the skill has already been learned by the player.
		self.skill = []

		#equipment:
		#equip[0]=weapon, [1]=armor, [2]=shield
		#[3]=helmet, [4]=gloves, [5]=boots

		#An array of numbers, which are either the index of the
		#item in the item[] array, or -1 for empty.
		self.equip = []
		for x in range(6):
			self.equip.append(-1)

	#Gives the player the specified amount of experience; also handles level gains.
	def add_exp(self, input_exp):
		self.exp = int(self.exp) + int(input_exp)
		if 1 > self.exp: self.exp = 0
		#Has the player gained a level?
		if self.exp_till_level() <= 0:
			self.level=self.level+1
			g.main.print_message("You gain a level.")
			g.action.activate_lines(g.xgrid, g.ygrid, g.zgrid,
					g.levelup_act)

	def exp_till_level(self):
		if g.exp_list == "":
			return_val = int(10*(self.level+1)*(self.level+1)) - int(self.exp)
		else:
			if len(g.exp_list) > self.level:
				return_val = int(g.exp_list[self.level]) - int(self.exp)
			else: return_val = 9999
		if return_val < 0: return_val = 0
		return return_val

	#function for permanently changing the stats of a player.
	#stat=hp, ep, (adj_)maxhp, (adj_)maxep, (adj_)attack, (adj_)defense,
	#gold, skillpoints.
	#Value is a number
	def give_stat(self, stat, value):
		if stat == "hp":
			self.hp = self.hp + int(value)
			if self.hp >= self.adj_maxhp: self.hp = self.adj_maxhp
		elif stat == "ep":
			self.ep = self.ep + int(value)
			if self.ep >= self.adj_maxep: self.ep = self.adj_maxep
			if self.ep < 0: self.ep = 0
		elif stat == "maxhp":
			self.maxhp = self.maxhp + int(value)
			if 1 > self.maxhp: self.maxhp = 1
			self.adj_maxhp = self.adj_maxhp + int(value)
			if 1 > self.adj_maxhp: self.adj_maxhp = 1
		elif stat == "maxep":
			self.maxep = self.maxep + int(value)
			if 1 > self.maxep: self.maxep = 1
			self.adj_maxep = self.adj_maxep + int(value)
			if 1 > self.adj_maxep: self.adj_maxep = 1
		elif stat == "attack":
			self.attack = self.attack + int(value)
			if 1 > self.attack: self.attack = 1
			self.adj_attack = self.adj_attack + int(value)
			if 1 > self.adj_attack: self.adj_attack = 1
		elif stat == "defense":
			self.defense = self.defense + int(value)
			if 1 > self.defense: self.defense = 1
			self.adj_defense = self.adj_defense + int(value)
			if 1 > self.adj_defense: self.adj_defense = 1
		elif stat == "adj_maxhp":
			self.adj_maxhp = self.adj_maxhp + int(value)
			if 1 > self.adj_maxhp: self.adj_maxhp = 1
		elif stat == "adj_maxep":
			self.adj_maxep = self.adj_maxep + int(value)
			if 1 > self.adj_maxep: self.adj_maxep = 1
		elif stat == "adj_attack":
			self.adj_attack = self.adj_attack + int(value)
			if 1 > self.adj_attack: self.adj_attack = 1
		elif stat == "adj_defense":
			self.adj_defense = self.adj_defense + int(value)
			if 1 > self.adj_defense: self.adj_defense = 1
		elif stat == "gold":
			self.gold = int(self.gold) + int(value)
			if 1 > self.gold: self.gold = 0
		elif stat == "skillpoints":
			self.skillpoints = self.skillpoints + int(value)
			if 1 > self.skillpoints: self.skillpoints = 0
		else:
			print "player.give_stat called with unknown stat of " + stat

	#recalculates the adj_ values.
	def reset_stats(self):
		self.adj_attack = int(self.attack)
		if self.equip[0] != -1:
			self.adj_attack = self.adj_attack + g.item.item[self.equip[0]].quality
		for i in range(6):
			if self.equip[i] != -1:
				self.adj_attack = self.adj_attack + \
							g.item.item[self.equip[i]].attack_bonus

		self.adj_defense = int(self.defense)
		for i in range(1, 6):
			if self.equip[i] != -1:
				self.adj_defense = self.adj_defense + \
							g.item.item[self.equip[i]].quality
		for i in range(6):
			if self.equip[i] != -1:
				self.adj_defense = self.adj_defense + \
							g.item.item[self.equip[i]].defense_bonus

		self.adj_maxhp = int(self.maxhp)
		for i in range(6):
			if self.equip[i] != -1:
				self.adj_maxhp = self.adj_maxhp + g.item.item[self.equip[i]].hp_bonus
		if self.hp > self.adj_maxhp: self.hp = self.adj_maxhp

		self.adj_maxep = int(self.maxep)
		for i in range(6):
			if self.equip[i] != -1:
				self.adj_maxep = self.adj_maxep + g.item.item[self.equip[i]].ep_bonus
		if self.ep > self.adj_maxep: self.ep = self.adj_maxep



player = player_class()
