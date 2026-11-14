import os
import subprocess
import sys
import textwrap
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAVE_TEST_SETUP = """
import pygame
pygame.init()

import rpg
import config
import modules
modules.load("DarkAges")

import g
import item
import modloader
from player import player
import save_mgmt
modloader.read_maps()
"""


def run_save_probe(body: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    return subprocess.run(
        [sys.executable, "-c", SAVE_TEST_SETUP + textwrap.dedent(body)],
        cwd=PROJECT_ROOT / "src",
        env=env,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )


def test_round_trips_game_state_and_rejects_bad_saves_without_mutation() -> None:
    result = run_save_probe(
        """
            import json
            import tempfile
            from pathlib import Path

            save_dir = tempfile.TemporaryDirectory()
            config.MODULES_DIR = save_dir.name
            spear = item.finditem("Spear")
            map_name = config.MAPS[0].name

            player.name = "Round/Trip"
            player.hp = 7
            player.ep = 3
            player.maxhp = 12
            player.maxep = 5
            player.attack = 8
            player.defense = 4
            player.gold = 23
            player.exp = 41
            player.level = 2
            player.skillpoints = 6
            player.equip[:] = [spear, -1, -1, -1, -1, -1]
            item.inv[:] = [-1] * len(item.inv)
            item.inv[0] = spear
            item.inv[3] = spear
            for skill in player.skill:
                skill[5] = 0
            player.skill[0][5] = 1
            g.xgrid = 5
            g.ygrid = 7
            g.zgrid = 0
            g.timestep = 17
            g.var_list = {"quest_flag": 1, "password": "open"}
            item.dropped_items[:] = [item.DroppedItem("Spear", (6, 8), map_name)]

            save_name = save_mgmt.save_filename(player.name)
            save_mgmt.savegame(player.name)
            preview = save_mgmt.read_save(save_name)
            assert preview["version"] == save_mgmt.SAVE_VERSION
            assert save_mgmt.display_save_name(save_name) == "Round/Trip"
            assert preview["player"]["name"] == "Round/Trip"
            assert preview["player"]["hp"] == 7
            import loadgame
            preview_display = {}
            loadgame.saves_array = [save_name]
            loadgame.saves_pos = 0
            loadgame.display_stats = lambda stats, titles, error=None: preview_display.update(
                stats=stats, titles=titles, error=error
            )
            loadgame.refresh_save_info()
            assert preview_display["stats"]["name"] == "Round/Trip"
            assert preview_display["titles"][0] == "Round/Trip"
            assert preview_display["error"] is None

            player.name = "Changed"
            player.hp = 1
            player.equip[:] = [-1] * len(player.equip)
            item.inv[:] = [-1] * len(item.inv)
            for skill in player.skill:
                skill[5] = 0
            g.xgrid = 0
            g.ygrid = 0
            g.zgrid = 1
            g.timestep = 0
            g.var_list = {}
            item.dropped_items.clear()

            save_mgmt.loadgame(save_name)
            assert player.name == "Round/Trip"
            assert (player.hp, player.ep, player.maxhp, player.maxep) == (7, 3, 12, 5)
            assert (player.attack, player.defense, player.gold) == (8, 4, 23)
            assert (player.exp, player.level, player.skillpoints) == (41, 2, 6)
            assert player.equip == [spear, -1, -1, -1, -1, -1]
            assert item.inv[0] == spear and item.inv[3] == spear
            assert player.skill[0][5] == 1
            assert not any(skill[5] for skill in player.skill[1:])
            assert (g.xgrid, g.ygrid, g.zgrid, g.timestep) == (5, 7, 0, 17)
            assert g.var_list == {"quest_flag": 1, "password": "open"}
            assert len(item.dropped_items) == 1
            dropped = item.dropped_items[0]
            assert (dropped.name, dropped.x, dropped.y, dropped.mapname) == ("Spear", 6, 8, map_name)

            item.load_dropped_items()
            assert "Spear" in config.MAPS[0].field[8][6].items

            bad_save = Path(save_dir.name) / "saves" / "bad"
            bad_save.write_text(json.dumps({"version": 99}), encoding="utf-8")
            player.name = "Unchanged"
            loadgame.saves_array = ["bad"]
            loadgame.refresh_save_info()
            assert "Unsupported save version" in preview_display["error"]
            try:
                save_mgmt.loadgame("bad")
            except ValueError:
                pass
            else:
                raise AssertionError("Unsupported save versions must be rejected")
            assert player.name == "Unchanged"
            save_dir.cleanup()
        """
    )

    assert result.returncode == 0, result.stdout + result.stderr
