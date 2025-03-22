# Item File Format

Description the format of files in the items directory.

## Overview

Each file consists of several properties of the item, seperated by newlines.
Properties are in a key-value format `Property=Value`.

- Name
  - Any name you want, but must be unique.
- Type
  - 0 : Weapons
  - 1 : Armor
  - 2 : Shield
  - 3 : Helmet
  - 4 : Gloves
  - 5 : Boots
  - 10 : Reserved (Used for story items/keys)
  - 11 : Healing
  - 12 : Explosive
  - 14 : Gems
  - Scripting Types
    - 15 : Usable in battle
    - 16 : Usable out of battle
    - 17 : Usable in both
- Quality
  - This is used to determine how powerful armor/weapons/items are;
  - Has no effect on reserved (type 10) or scripted (type 15-17) items
- Price/Value
  - The cost to buy/sell the item; setting both to 0 makes the item unsellable and undroppable
- Description
  - A description of the item, mainly just used in the stores
- Scripting block (optional)
  - When making a type 15-17 item, add the scripting for it between `:scripting` and `:values`
- Picture
  - The picture to use for the item. If not given, a default picture is used.
  - File must be relative to the images/tiles directory.

## Example

```text
Name=Small Energy Potion
type=17
quality=5
price=10
value=10
description=This potion will rejuvinate you.
:scripting
give("ep", 5)
:values
picture=items/light_energy_potion.png
```
