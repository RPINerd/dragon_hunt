""""""
from os import path, walk
from random import random

import pygame

from config import MODULES_DIR

SOUNDS: dict[str, dict[int, pygame.Sound]] = {}
MUTE: bool = False


def load_sounds() -> None:
    """Walk the sound directory and load all sounds into the SOUNDS dictionary."""
    global SOUNDS
    global MUTE

    if MUTE:
        return
    try:
        pygame.mixer.init()
    except pygame.error as message:
        print(f"Error: Unable to init sound (pygame message: {message})")
        MUTE = True
        return

    for root, dirs, files in walk(MODULES_DIR + "/sound"):
        (head, tail) = path.split(root)
        if tail != "CVS":
            for soundname in files:
                # if image is in a sub-dir:
                tmp_name = soundname[:-5] + soundname[-4:]
                tmp_number = int(soundname[-5])
                if root != MODULES_DIR + "/sound":
                    i = len(MODULES_DIR + "/sound")
                    base_name = root[i:] + "/" + tmp_name
                else:  # if image is in root dir
                    base_name = tmp_name
                if base_name not in SOUNDS:
                    SOUNDS[base_name] = {}
                SOUNDS[base_name][tmp_number] = pygame.mixer.Sound(root + "/" + soundname)


def play_sound(sound_name: str) -> None:
    """"""
    try:
        dict_size = len(SOUNDS[sound_name])
        SOUNDS[sound_name][int(random() * dict_size)].play()
    except KeyError:
        raise KeyError(f"Missing sound set {sound_name}")
    except pygame.error:
        print(f"Error: Unable to play sound {sound_name}")
