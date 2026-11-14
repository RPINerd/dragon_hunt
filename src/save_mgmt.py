"""Save and load the current game state."""

import json
import math
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from urllib.parse import quote, unquote

import config
import g
import item
from player import player

SAVE_VERSION = 1


def save_filename(player_name: str) -> str:
    """Return a filesystem-safe save filename for a player name."""
    if not player_name:
        raise ValueError("Player name cannot be empty.")
    return f"save-{quote(player_name, safe=' -_.')}.json"


def display_save_name(save_file: str) -> str:
    """Return a readable name for a save filename."""
    if save_file.startswith("save-") and save_file.endswith(".json"):
        return unquote(save_file[5:-5])
    return save_file


def _save_path(save_file: str) -> Path:
    if not save_file or Path(save_file).name != save_file or "/" in save_file or "\\" in save_file:
        raise ValueError("Save name must be a non-empty filename.")
    return Path(config.MODULES_DIR) / "saves" / save_file


def _is_number(value: Any) -> bool:
    return type(value) is int or (type(value) is float and math.isfinite(value))


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid numeric value: {value}.")


def _validate_save(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Save data must be an object.")
    if type(data.get("version")) is not int or data["version"] != SAVE_VERSION:
        raise ValueError(f"Unsupported save version: {data.get('version')!r}.")

    player_data = data.get("player")
    location = data.get("location")
    game_data = data.get("game")
    dropped_items = data.get("dropped_items")
    if not isinstance(player_data, dict) or not isinstance(location, dict) or not isinstance(game_data, dict):
        raise ValueError("Save data is missing a required section.")
    if not isinstance(dropped_items, list):
        raise ValueError("Save data has an invalid dropped_items section.")

    if not isinstance(player_data.get("name"), str):
        raise ValueError("Save data has an invalid player name.")
    for field in ("hp", "ep", "maxhp", "maxep", "attack", "defense", "gold", "exp", "level", "skillpoints"):
        if not _is_number(player_data.get(field)):
            raise ValueError(f"Save data has an invalid player field: {field}.")

    for field in ("equipment", "inventory", "skills"):
        values = player_data.get(field)
        if not isinstance(values, list):
            raise ValueError(f"Save data has an invalid player field: {field}.")
        if field == "skills":
            if not all(isinstance(value, str) for value in values):
                raise ValueError("Save data has an invalid skill name.")
        elif not all(value is None or isinstance(value, str) for value in values):
            raise ValueError(f"Save data has an invalid {field} entry.")

    if not isinstance(location.get("map"), str):
        raise ValueError("Save data has an invalid map name.")
    for field in ("x", "y"):
        if type(location.get(field)) is not int:
            raise ValueError(f"Save data has an invalid location field: {field}.")

    for dropped_item in dropped_items:
        if not isinstance(dropped_item, dict):
            raise ValueError("Save data has an invalid dropped item.")
        if not isinstance(dropped_item.get("name"), str) or not isinstance(dropped_item.get("map"), str):
            raise ValueError("Save data has an invalid dropped item name or map.")
        if type(dropped_item.get("x")) is not int or type(dropped_item.get("y")) is not int:
            raise ValueError("Save data has an invalid dropped item position.")

    if type(game_data.get("timestep")) is not int or not isinstance(game_data.get("variables"), dict):
        raise ValueError("Save data has an invalid game state.")
    return data


def read_save(save_file: str) -> dict[str, Any]:
    """Read and validate a save file for both the preview and game loader."""
    save_path = _save_path(save_file)
    with save_path.open(encoding="utf-8") as savefile:
        try:
            data = json.load(savefile, parse_constant=_reject_json_constant)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid save file: {error.msg}.") from error
    return _validate_save(data)


def _item_name(item_index: int) -> str | None:
    if item_index == -1:
        return None
    if item_index < 0 or item_index >= len(item.item):
        raise ValueError(f"Invalid item index in game state: {item_index}.")
    return item.item[item_index].name


def savegame(save_file: str) -> None:
    """Write the current game state as a versioned JSON document."""
    save_path = _save_path(save_filename(save_file))
    if g.zgrid < 0 or g.zgrid >= len(config.MAPS):
        raise ValueError(f"Invalid current map index: {g.zgrid}.")
    _check_position(g.zgrid, g.xgrid, g.ygrid, "player")
    for dropped in item.dropped_items:
        dropped_map_index = _find_map(dropped.mapname)
        _check_position(dropped_map_index, dropped.x, dropped.y, "dropped item")

    data = {
        "version": SAVE_VERSION,
        "player": {
            "name": player.name,
            "hp": player.hp,
            "ep": player.ep,
            "maxhp": player.maxhp,
            "maxep": player.maxep,
            "attack": player.attack,
            "defense": player.defense,
            "gold": player.gold,
            "exp": player.exp,
            "level": player.level,
            "skillpoints": player.skillpoints,
            "equipment": [_item_name(index) for index in player.equip],
            "inventory": [_item_name(index) for index in item.inv],
            "skills": [skill[0] for skill in player.skill if skill[5] == 1],
        },
        "location": {
            "x": g.xgrid,
            "y": g.ygrid,
            "map": config.MAPS[g.zgrid].name,
        },
        "dropped_items": [
            {"name": dropped.name, "x": dropped.x, "y": dropped.y, "map": dropped.mapname}
            for dropped in item.dropped_items
        ],
        "game": {
            "timestep": g.timestep,
            "variables": g.var_list,
        },
    }
    _validate_save(data)

    save_path.parent.mkdir(parents=True, exist_ok=True)
    savefile = NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=save_path.parent,
        prefix=f".{save_path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary_path = Path(savefile.name)
    try:
        with savefile:
            json.dump(data, savefile, ensure_ascii=False, allow_nan=False)
        temporary_path.replace(save_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _find_map(map_name: str) -> int:
    for map_index, game_map in enumerate(config.MAPS):
        if game_map.name == map_name:
            return map_index
    raise ValueError(f"Save refers to a map that is not installed: {map_name}.")


def _check_position(map_index: int, x: int, y: int, label: str) -> None:
    field = config.MAPS[map_index].field
    if y < 0 or y >= len(field) or x < 0 or x >= len(field[y]):
        raise ValueError(f"Save contains an invalid {label} position.")


def _resolve_items(item_names: list[str | None]) -> list[int]:
    item_indexes = []
    for name in item_names:
        if name is None:
            item_indexes.append(-1)
            continue
        item_index = item.finditem(name)
        if item_index == -1:
            raise ValueError(f"Save refers to an item that is not installed: {name}.")
        item_indexes.append(item_index)
    return item_indexes


def loadgame(save_file: str) -> None:
    """Load a previously saved game, validating it before changing game state."""
    data = read_save(save_file)
    player_data = data["player"]
    location = data["location"]
    game_data = data["game"]

    equipment = _resolve_items(player_data["equipment"])
    inventory = _resolve_items(player_data["inventory"])
    if len(equipment) != len(player.equip) or len(inventory) != len(item.inv):
        raise ValueError("Save inventory layout does not match this game version.")

    skill_indexes = []
    for name in player_data["skills"]:
        skill_index = player.findskill(name)
        if skill_index == -1:
            raise ValueError(f"Save refers to a skill that is not installed: {name}.")
        skill_indexes.append(skill_index)

    map_index = _find_map(location["map"])
    _check_position(map_index, location["x"], location["y"], "player")
    dropped_items = []
    for dropped in data["dropped_items"]:
        dropped_map_index = _find_map(dropped["map"])
        _check_position(dropped_map_index, dropped["x"], dropped["y"], "dropped item")
        if item.finditem(dropped["name"]) == -1:
            raise ValueError(f"Save refers to a dropped item that is not installed: {dropped['name']}.")
        dropped_items.append(item.DroppedItem(dropped["name"], (dropped["x"], dropped["y"]), dropped["map"]))

    player.name = player_data["name"]
    player.hp = player_data["hp"]
    player.ep = player_data["ep"]
    player.maxhp = player_data["maxhp"]
    player.maxep = player_data["maxep"]
    player.attack = player_data["attack"]
    player.defense = player_data["defense"]
    player.gold = player_data["gold"]
    player.exp = player_data["exp"]
    player.level = player_data["level"]
    player.skillpoints = player_data["skillpoints"]
    player.equip[:] = equipment
    item.inv[:] = inventory
    for skill in player.skill:
        skill[5] = 0
    for skill_index in skill_indexes:
        player.skill[skill_index][5] = 1

    g.xgrid = location["x"]
    g.ygrid = location["y"]
    g.zgrid = map_index
    item.dropped_items[:] = dropped_items
    g.timestep = game_data["timestep"]
    g.var_list = game_data["variables"]
