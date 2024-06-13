#This file reads in outside2.map from Dark Ages, and outputs the map in
#Dragon Hunt format. Furthermore, it also splits the map into multiple smaller
#maps in order to make loading times reasonable.

def write_file(x, y):
	global map_array
	outfile = open("world"+str(x)+"x"+str(y)+".txt", 'w')

	#the upper-left tile takes care of the monster list. This is the best way
	#to keep the monster-by-level setup Dark Ages has, as I need if statements,
	#which don't work in the :def section. That is also the reason for the bit
	#of wierdness with the print_tile() function and all that, as that tile
	#needs to still display the normal pix.
	special_char = int(map_array[y*24][x*72:x*72+2]) + 50
	map_array[y*24] = \
		map_array[y*24][0:x*72]+str(special_char)+map_array[y*24][x*72+2:]

	for i in range(24):
		if len(map_array) <= y*24+i: break
		outfile.write(map_array[y*24+i][x*72:(x+1)*72]+"\n")

	outfile.write("\n\n:def\n")
	if y > 0:
		outfile.write("level_up=world"+str(x)+"x"+str(y-1)+".txt\n")
	if x > 0:
		outfile.write("level_left=world"+str(x-1)+"x"+str(y)+".txt\n")
	if x < 5:
		outfile.write("level_right=world"+str(x+1)+"x"+str(y)+".txt\n")
	if y < 4:
		outfile.write("level_down=world"+str(x)+"x"+str(y+1)+".txt\n")
	if y > 0 and x > 0:
		outfile.write("level_upleft=world"+str(x-1)+"x"+str(y-1)+".txt\n")
	if y > 0 and x < 5:
		outfile.write("level_upright=world"+str(x+1)+"x"+str(y-1)+".txt\n")
	if y < 4 and x > 0:
		outfile.write("level_downleft=world"+str(x-1)+"x"+str(y+1)+".txt\n")
	if y < 4 and x < 5:
		outfile.write("level_downright=world"+str(x+1)+"x"+str(y+1)+".txt\n")

	#Battle stuff
	outfile.write('\nbattle_bg=generic.png')

	print_tiles(outfile, [1,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,
		24,25,26,30,31,41,56,58,81,84,85,86,89,91,92,93,94,95,96])

	outfile.write('\n:'+str(special_char)+print_tile(special_char-50)+'\n')
	#And here's the biggy. (The base for this is the levelup script.)
	outfile.write("""if(stat("level"), "<", 2)
	mapstat("addmonster", "Orc")
	end()
endif
if(stat("level"), "<", 4)
	mapstat("addmonster", "Orc")
	mapstat("addmonster", "Ferocious Armless")
	end()
endif
if(stat("level"), "<", 6)
	mapstat("addmonster", "Orc")
	mapstat("addmonster", "Ferocious Armless")
	mapstat("addmonster", "Highway Bandit")
	end()
endif
if(stat("level"), "<", 8)
	mapstat("addmonster", "Orc")
	mapstat("addmonster", "Ferocious Armless")
	mapstat("addmonster", "Highway Bandit")
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Acid Slime")
	end()
endif
if(stat("level"), "<", 10)
	mapstat("addmonster", "Orc")
	mapstat("addmonster", "Ferocious Armless")
	mapstat("addmonster", "Highway Bandit")
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Giant Spider")
	end()
endif
if(stat("level"), "<", 12)
	mapstat("addmonster", "Orc")
	mapstat("addmonster", "Ferocious Armless")
	mapstat("addmonster", "Highway Bandit")
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Wizard")
	end()
endif
if(stat("level"), "<", 14)
	mapstat("addmonster", "Orc")
	mapstat("addmonster", "Ferocious Armless")
	mapstat("addmonster", "Highway Bandit")
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Goblin")
	end()
endif
if(stat("level"), "<", 16)
	mapstat("addmonster", "Ferocious Armless")
	mapstat("addmonster", "Highway Bandit")
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Skeleton")
	end()
endif
if(stat("level"), "<", 18)
	mapstat("addmonster", "Highway Bandit")
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Troll")
	end()
endif
if(stat("level"), "<", 20)
	mapstat("addmonster", "Acid Slime")
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Death Knight")
	end()
endif
if(stat("level"), "<", 22)
	mapstat("addmonster", "Giant Spider")
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Bronze Golem")
	end()
endif
if(stat("level"), "<", 24)
	mapstat("addmonster", "Wizard")
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Dark Goblin")
	end()
endif
if(stat("level"), "<", 26)
	mapstat("addmonster", "Goblin")
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Iron Golem")
	mapstat("addmonster", "Iron Golem")
	end()
endif
if(stat("level"), "<", 28)
	mapstat("addmonster", "Skeleton")
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Iron Golem")
	mapstat("addmonster", "Gold Dragon")
	mapstat("addmonster", "Gold Dragon")
	end()
endif
if(stat("level"), "<", 28)
	mapstat("addmonster", "Troll")
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Iron Golem")
	mapstat("addmonster", "Gold Dragon")
	mapstat("addmonster", "Lost Soul")
	mapstat("addmonster", "Lost Soul")
	end()
endif
if(stat("level"), "<", 30)
	mapstat("addmonster", "Death Knight")
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Iron Golem")
	mapstat("addmonster", "Gold Dragon")
	mapstat("addmonster", "Lost Soul")
	mapstat("addmonster", "Ice Dragon")
	mapstat("addmonster", "Ice Dragon")
	end()
endif
if(stat("level"), "<", 32)
	mapstat("addmonster", "Bronze Golem")
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Iron Golem")
	mapstat("addmonster", "Gold Dragon")
	mapstat("addmonster", "Lost Soul")
	mapstat("addmonster", "Ice Dragon")
	mapstat("addmonster", "Platinum Golem")
	mapstat("addmonster", "Platinum Golem")
	end()
endif
if(stat("level"), "<", 34)
	mapstat("addmonster", "Dark Goblin")
	mapstat("addmonster", "Iron Golem")
	mapstat("addmonster", "Gold Dragon")
	mapstat("addmonster", "Lost Soul")
	mapstat("addmonster", "Ice Dragon")
	mapstat("addmonster", "Platinum Golem")
	mapstat("addmonster", "Black Dragon")
	mapstat("addmonster", "Black Dragon")
	end()
endif

#above level 34:
mapstat("addmonster", "Iron Golem")
mapstat("addmonster", "Gold Dragon")
mapstat("addmonster", "Lost Soul")
mapstat("addmonster", "Ice Dragon")
mapstat("addmonster", "Platinum Golem")
mapstat("addmonster", "Black Dragon")
mapstat("addmonster", "Black Dragon")
""")

	outfile.close()

def print_tiles(outfile, tile_array):
	for tile in tile_array:
		tile2 = str(tile)
		if tile < 10: tile2 = "0"+str(tile)
		outfile.write('\n:'+tile2+print_tile(tile))

def print_tile(tilenum):
	if tilenum == 1:
		return '\npix("grass.png")\nwalk(1)' #grass
	if tilenum == 6:
		return '\npix("hills/hills_w.png")\nwalk(1)' #mountains+edges
	if tilenum == 7:
		return '\npix("hills/hills_n3.png")\nwalk(1)'
	if tilenum == 8:
		return '\npix("hills/hills_e.png")\nwalk(1)'
	if tilenum == 9:
		return '\npix("hills/hills_n4.png")\nwalk(0)'
	if tilenum == 10:
		return '\npix("hills/hills_e.png")\nwalk(1)'
	if tilenum == 11:
		return '\npix("hills/hills_w.png")\nwalk(1)'
	if tilenum == 12:
		return '\npix("forest_s.png")\nwalk(1)' #forest+edges
	if tilenum == 13:
		return '\npix("forest.png")\nwalk(1)'
	if tilenum == 14:
		return '\npix("forest_se.png")\nwalk(1)'
	if tilenum == 15:
		return '\npix("forest_e.png")\nwalk(1)'
	if tilenum == 16:
		return '\npix("forest_sw.png")\nwalk(1)'
	if tilenum == 17:
		return '\npix("forest_nw.png")\nwalk(1)'
	if tilenum == 18:
		return '\npix("water/water.png")\nwalk(0)'
	if tilenum == 19:
		return '\npix("water/water_s.png")\nwalk(1)' #water edges
	if tilenum == 20:
		return '\npix("water/water_e.png")\nwalk(1)'
	if tilenum == 21:
		return '\npix("water/water_n.png")\nwalk(1)'
	if tilenum == 22:
		return '\npix("water/water_w.png")\nwalk(1)'
	if tilenum == 23:
		return '\npix("water/water_sw.png")\nwalk(1)'
	if tilenum == 24:
		return '\npix("water/water_se.png")\nwalk(1)'
	if tilenum == 25:
		return '\npix("water/water_ne.png")\nwalk(1)'
	if tilenum == 26:
		return '\npix("water/water_nw.png")\nwalk(1)' #end water edges
	if tilenum == 30:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 31:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 41:
		return '\npix("grass.png")\nwalk(1)' #cave enterance
	if tilenum == 56:
		return '\npix("water/bridge_ew.png")\nwalk(1)' #bridge left-right
	if tilenum == 58:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 81:
		return '\npix("grass.png")\nwalk(1)' #cave enterance
	if tilenum == 84:
		return '\npix("grass.png")\nwalk(1)' #hills
	if tilenum == 85:
		return '\npix("grass.png")\nwalk(1)' #hills
	if tilenum == 86:
		return '\npix("grass.png")\nwalk(1)' #hills
	if tilenum == 89:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 91:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 92:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 93:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 94:
		return '\npix("water/bridge_ns.png")\nwalk(1)' #bridge up-down
	if tilenum == 95:
		return '\npix("town.png")\nwalk(1)' #town
	if tilenum == 96:
		return '\npix("town.png")\nwalk(1)' #town

def read_file():
	infile=open("outside2.map", 'r')

	infile.readline() #get rid of size line

	global map_array
	map_array = infile.readlines()

	infile.close()
	for i in range(len(map_array)):
		map_array[i] = map_array[i].replace(",", " ").strip()


read_file()

for x in range(6):
	for y in range(5):
		write_file(x, y)