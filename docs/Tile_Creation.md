# Game Tile Creation

Information about game tiles

## Overview

The tiles directory is "modules/Dragon\ Hunt/images/tiles".

Sets of tiles should go in a sub-directory that is logically named.

New tiles must be added to the walk definition file
"modules/Dragon\ Hunt/data/walk_defs.txt"
with the binary value of whether or not this tile can be walked upon.

## Item Tile Requirements

The pictures must go in the items directory.  They must be named
item_name.png, and have a transparent background.

For example, an item tile called "healing_potion.png" is a "healing potion".
It can be added to a level either through the level editor, or by using the
following code:

```text
pix("grass.png")
walk(1)
if(var("healing_potion_3"), "=", 0)
    addpix("items/healing_potion.png")
endif
Action
if(var("healing_potion_3"), "=", 0)
    if(find("healing potion", "a"), "=", 1)
        set(healing_potion_3", "=", 1)
        delpix("items/healing_potion.png")
    endif
endif
```

It is also recomended to add the picture to the item definition. Add the line
picture=items/item_name.png to the relevant item definition file in
Module Name/data/items/
Doing this gives the item a non-generic picture in the shop, inventory, and
on the ground.
