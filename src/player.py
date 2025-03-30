# file: player.py
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

# This file controls the player info

from typing import TYPE_CHECKING

import config
import g

if TYPE_CHECKING:
    from pathlib import Path


class Player:

    """This class is used to store all the player's information."""

    def __init__(self) -> None:
        """Initialize a blank player object."""
        self.name: str = ""
        self.hp: int = 0
        self.ep: int = 0
        self.maxhp: int = 0
        self.maxep: int = 0
        self.attack: int = 0
        self.defense: int = 0
        self.gold: int = 0
        self.exp: int = 0
        self.level: int = 0
        self.skillpoints: int = 1

        # Values adjusted by equipment.
        # Kept correct by main.refreshmap().
        # Use these for calculations.
        self.adj_attack: int = 0
        self.adj_defense: int = 0
        self.adj_maxhp: int = 0
        self.adj_maxep: int = 0

        # Name of current hero picture.
        self.cur_hero: str | Path = "people/hero_w.png"

        # TODO maybe could be a dict?
        # skills array. Each skill is a separate line in the array. Each line goes:
        # name, effect, level, price, description, acquired, scripting (if any),
        # then picture.
        # effect is an integer that tells battle.py which case in a select to pick.
        # level is the skillpoints required to get the skill,
        # price is the ep needed to use.
        # acquired tells if the skill has already been learned by the player.
        self.skill: list[list] = []

        # A list of numbers representing equipment slots
        # Values are either the index of the item in the item[] array, or -1 for empty.
        # Array: weapon (0), armor (1), shield (2), helmet (3), gloves (4), boots (5)
        self.equip: list[int] = [-1 for _ in range(6)]

    def add_exp(self, input_exp: int) -> None:
        """
        Adds experience to the player and handles level gains.

        Args:
            input_exp (int): The amount of experience to add.

        Returns:
            None
        """
        self.exp += input_exp
        if self.exp < 1:
            self.exp = 0

        # Has the player gained a level?
        if self.exp_till_level() <= 0:
            self.level += 1
            # !main.print_message("You gain a level!")
            g.action.activate_lines(g.xgrid, g.ygrid, g.zgrid, g.levelup_act)

    def exp_till_level(self) -> int:
        """
        Calculates experience needed to reach the next level.

        Returns:
            (int): Exp needed for next level
        """
        if not config.mut["EXP_LIST"]:
            return_val = int(10 * (self.level + 1) * (self.level + 1)) - int(self.exp)
        elif len(config.mut["EXP_LIST"]) > self.level:
            return_val = int(config.mut["EXP_LIST"][self.level]) - int(self.exp)
        else:
            return_val = 9999
        return max(return_val, 0)

    def take_damage(self, damage: int) -> None:
        """
        Inflict damage on the player.

        Args:
            damage (int): The amount of damage to inflict.

        Returns:
            None
        """
        self.hp -= damage
        self.hp = min(self.adj_maxhp, self.hp)

    def use_ep(self, ep_cost: int) -> None:
        """
        Use energy/mana/etc. points

        Args:
            ep_cost (int): The amount of energy points to use.

        Returns:
            None
        """
        self.ep -= ep_cost
        self.ep = min(self.adj_maxep, self.ep)
        self.ep = max(self.ep, 0)

    def raise_hp(self, hp_raise: int) -> None:
        """
        Raise the player's max hit points.

        Args:
            hp_raise (int): The amount of hit points to gain.
        """
        self.maxhp += hp_raise
        self.maxhp = max(self.maxhp, 1)
        self.adj_maxhp += hp_raise
        self.adj_maxhp = max(self.adj_maxhp, 1)

    def raise_ep(self, ep_raise: int) -> None:
        """
        Raise the player's max energy/mana points.

        Args:
            ep_raise (int): The amount of energy points to gain.
        """
        self.maxep += ep_raise
        self.maxep = max(self.maxep, 1)
        self.adj_maxep += ep_raise
        self.adj_maxep = max(self.adj_maxep, 1)

    def raise_attack(self, attack_raise: int) -> None:
        """
        Raise the player's attack power.

        Args:
            attack_raise (int): The amount of attack power to gain.
        """
        self.attack += attack_raise
        self.attack = max(self.attack, 1)
        self.adj_attack += attack_raise
        self.adj_attack = max(self.adj_attack, 1)

    def raise_defense(self, defense_raise: int) -> None:
        """
        Raise the player's defense power.

        Args:
            defense_raise (int): The amount of defense power to gain.
        """
        self.defense += defense_raise
        self.defense = max(self.defense, 1)
        self.adj_defense += defense_raise
        self.adj_defense = max(self.adj_defense, 1)

    def buff_hp(self, hp_buff: int) -> None:
        """
        Buff the player's hit points.

        Args:
            hp_buff (int): The amount of hit points to gain.
        """
        self.adj_maxhp += hp_buff
        self.adj_maxhp = max(self.adj_maxhp, 1)

    def buff_ep(self, ep_buff: int) -> None:
        """
        Buff the player's energy/mana points.

        Args:
            ep_buff (int): The amount of energy points to gain.
        """
        self.adj_maxep += ep_buff
        self.adj_maxep = max(self.adj_maxep, 1)

    def buff_attack(self, attack_buff: int) -> None:
        """
        Buff the player's attack power.

        Args:
            attack_buff (int): The amount of attack power to gain.
        """
        self.adj_attack += attack_buff
        self.adj_attack = max(self.adj_attack, 1)

    def buff_defense(self, defense_buff: int) -> None:
        """
        Buff the player's defense power.

        Args:
            defense_buff (int): The amount of defense power to gain.
        """
        self.adj_defense += defense_buff
        self.adj_defense = max(self.adj_defense, 1)

    def add_skillpoints(self, points: int) -> None:
        """
        Add skill points to the player.

        Args:
            points (int): The amount of skill points to add.
        """
        self.skillpoints += points
        if self.skillpoints < 1:
            self.skillpoints = 0

    def findskill(self, name: str) -> int:
        """
        Find a skill in the player's skill list by name

        Args:
            name (str): The name of the skill to find

        Returns:
            (int): The index of the skill in the player's skill list, -1 if not found.
        """
        for i in range(len(self.skill)):
            if name.lower() == self.skill[i][0].lower():
                return i
        return -1

    def give_gold(self, gold: int) -> None:
        """
        Give gold to the player.

        Args:
            gold (int): The amount of gold to give.
        """
        self.gold += gold
        if self.gold < 1:
            self.gold = 0

    def reset_stats(self) -> None:
        """Recalculate the players adjusted stats."""
        self.adj_attack = self.attack
        self.adj_defense = self.defense
        self.adj_maxhp = self.maxhp
        self.adj_maxep = self.maxep

        for index, slot in enumerate(self.equip):
            if slot == -1:  # Empty slot
                continue

            # Weapon quality increases attack, other item quality increase defense
            if index == 0:
                self.adj_attack += g.item.item[slot].quality
            else:
                self.adj_defense += g.item.item[slot].quality

            self.adj_attack += g.item.item[slot].attack_bonus
            self.adj_defense += g.item.item[slot].defense_bonus
            self.adj_maxhp += g.item.item[slot].hp_bonus
            self.adj_maxep += g.item.item[slot].ep_bonus

        self.hp = min(self.hp, self.adj_maxhp)
        self.ep = min(self.ep, self.adj_maxep)


player = Player()
