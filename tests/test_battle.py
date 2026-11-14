import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_monster_selection_uses_bound_keys_only() -> None:
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    script = """
from types import SimpleNamespace

import pygame
pygame.init()

import action
import battle
import config
import g

config.BINDINGS.update({
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "action": pygame.K_RETURN,
    "attack": pygame.K_a,
})
battle.monster_list = [SimpleNamespace(hp=1), SimpleNamespace(hp=1)]
navigation = []
battle.choose_monster_prev = lambda: navigation.append("previous")
battle.choose_monster_next = lambda: navigation.append("next")
battle.refresh = lambda: None
battle.bind_attack_keys = lambda: None
battle.bind_keys = lambda: None
pygame.display.flip = lambda: None
pygame.time.wait = lambda _: None

def select_with_keys(keys):
    pending_keys = iter(keys)
    event_reads = 0

    def get_events(*args, **kwargs):
        nonlocal event_reads
        event_reads += 1
        return [pygame.event.Event(pygame.KEYDOWN, key=next(pending_keys))]

    pygame.event.get = get_events
    g.break_one_loop = 0
    battle.return_from_dialog = 0
    selected = battle.select_monster()
    return selected, event_reads

assert select_with_keys([
    pygame.K_UP,
    pygame.K_LEFT,
    pygame.K_DOWN,
    pygame.K_RIGHT,
    pygame.K_b,
    pygame.K_RETURN,
]) == (0, 6)
assert navigation == ["previous", "previous", "next", "next"]
assert select_with_keys([pygame.K_RETURN]) == (0, 1)
assert select_with_keys([pygame.K_a]) == (0, 1)
assert select_with_keys([pygame.K_b, pygame.K_a]) == (0, 2)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT / "src",
        env=env,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stdout + result.stderr
