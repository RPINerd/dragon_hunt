"""
Hopefully this will be able to collect all save/load functionality into one place.
"""
import pickle
from os import mkdir, path, remove
from pathlib import Path

import config
import item
from player import player
from scripting import maps


def savegame(save_file: str) -> None:
    """
    Save the current gamestate

    Saves file into the module folder, under a save subfolder:
    ./dragonhunt/saves/{save_file}

    Args:
        save_file (str): The name of the save file.
    """
    # If there is no save directory, make one.
    if path.isdir(config.MODULES_DIR + "/saves") == 0:
        if path.exists(config.MODULES_DIR + "/saves") == 1:
            remove(config.MODULES_DIR + "/saves")
        mkdir(config.MODULES_DIR + "/saves")
    save_loc = config.MODULES_DIR + "/saves/" + save_file
    savefile = Path.open(save_loc, "w")
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

    # Equipment is stored by name to increase savefile compatability.
    pickle.dump(len(player.equip), savefile)
    for i in range(len(player.equip)):
        if player.equip[i] != -1:
            pickle.dump(item.item[player.equip[i]].name, savefile)
        else:
            pickle.dump("Ignore", savefile)
    pickle.dump(len(item.inv), savefile)
    for i in range(len(item.inv)):
        if item.inv[i] != -1:
            pickle.dump(item.item[item.inv[i]].name, savefile)
        else:
            pickle.dump("Ignore", savefile)
    pickle.dump(xgrid, savefile)
    pickle.dump(ygrid, savefile)
    pickle.dump(config.MAPS[zgrid].name, savefile)
    # skills are stored by name as well.
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
    """
    Load a gamestate from a save file.

    Args:
        save_file (str): The name of the save file.
    """
    save_loc = config.MODULES_DIR + "/saves/" + save_file
    savefile = Path.open(save_loc, "r")
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

    # equipment is stored by name to increase savefile compatability.
    equip_len = pickle.load(savefile)
    for i in range(equip_len):
        player.equip[i] = item.finditem(pickle.load(savefile))
        if item.item[player.equip[i]].name == "Ignore":
            player.equip[i] = -1
    global inv
    inv_len = pickle.load(savefile)
    for i in range(inv_len):
        item.inv[i] = item.finditem(pickle.load(savefile))
        if item.item[item.inv[i]].name == "Ignore":
            item.inv[i] = -1
    global xgrid
    xgrid = pickle.load(savefile)
    global ygrid
    ygrid = pickle.load(savefile)
    global zgrid
    zgrid = pickle.load(savefile)
    if not str(zgrid).isdigit():
        zgrid = mapname2zgrid(str(zgrid))
    skill_len = pickle.load(savefile)
    for i in range(skill_len):
        loaded_skill = player.findskill(pickle.load(savefile))
        player.skill[loaded_skill][5] = 1
    item.dropped_items = pickle.load(savefile)
    global timestep
    timestep = pickle.load(savefile)
    global var_list
    var_list = pickle.load(savefile)
    savefile.close()
