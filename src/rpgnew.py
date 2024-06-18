"""
    This file is the first file accessed upon game start.
    It allows the player to select the module, or, if there is only one, automatically selects for the player.
"""

# Built-in/Generic Imports
import sys

# 3rd party lib imports
import pygame

import config

# Local Imports
import modules


def sel_mod(selected_mod: str = "DragonHunt") -> None:
    """
    Given a selected module, run it.
    This is effectively the main launching point for the game, starting up the core game
    window and loop.

    :param selected_mod: The selected module to run.
    """

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    g.mod_directory = "../modules/" + selected_mod

    g.create_norm_box(
        (config.SCREEN_WIDTH / 4, config.SCREEN_HEIGHT / 3),
        (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 3),
        "black",
        "light_gray",
    )

    g.print_string(
        g.screen, "Loading. Please wait", g.font, (config.SCREEN_WIDTH / 2, config.SCREEN_HEIGHT / 2), align=1
    )
    pygame.display.set_caption("Loading")
    pygame.display.flip()
    g.init_data()
    new_game.init_window()
    quit_game()


def quit_game():
    g.break_one_loop = 50


def refresh_module_info() -> None:
    g.unclean_screen = True
    tmp = config.mut["MODULE_POS"] - (config.mut["MODULE_POS"] % 5)
    for i in range(5):
        if i == config.mut["MODULE_POS"] % 5:
            tmp_color = "dh_green"
        else:
            tmp_color = "light_gray"
        g.create_norm_box(
            (
                config.TILESIZE * g.main.mapsizex / 4 + 2,
                config.TILESIZE * g.main.mapsizey / 3 + g.buttons["loadgame_down.png"].get_height() + 1 + i * 20,
            ),
            (g.buttons["loadgame_down.png"].get_width() - 5, 17),
            inner_color=tmp_color,
        )

        if len(config.MODULES) <= tmp + i:
            savetext = ""
        else:
            savetext = config.MODULES[int(tmp) + i]
        g.print_string(
            g.screen,
            savetext,
            g.font,
            (
                config.TILESIZE * g.main.mapsizex / 4 + 5,
                config.TILESIZE * g.main.mapsizey / 3 + g.buttons["loadgame_down.png"].get_height() + 3 + i * 20,
            ),
        )


# All keypresses pass through here. Based on the key name,
# give the right action. ("etc", "left", "right", "up", "down", "return")
# TODO pygame has event handlers for this exact reason, need to refactor this to use them.
def key_handler(switch):
    if switch == g.bindings["cancel"]:
        quit_game()
    elif switch == g.bindings["left"] or switch == g.bindings["right"]:
        if config.mut["CURR_BUTTON"] == 0:
            config.mut["CURR_BUTTON"] = 1
        else:
            config.mut["CURR_BUTTON"] = 0
        refresh_buttons()
    elif switch == g.bindings["up"]:
        config.mut["MODULE_POS"] -= 1
        if config.mut["MODULE_POS"] <= -1:
            config.mut["MODULE_POS"] = len(config.MODULES) - 1
        refresh_module_info()
    elif switch == g.bindings["down"]:
        config.mut["MODULE_POS"] += 1
        if config.mut["MODULE_POS"] >= len(config.MODULES):
            config.mut["MODULE_POS"] = 0
        refresh_module_info()
    elif switch == g.bindings["action"]:
        if config.mut["CURR_BUTTON"] != 1:
            sel_mod(config.MODULES[config.mut["MODULE_POS"]])
        else:
            quit_game()


def refresh_buttons() -> None:
    g.unclean_screen = True
    up_pic = "loadgame_up.png"
    down_pic = "loadgame_down.png"
    load_pic = "load.png"
    quit_pic = "quit.png"
    if config.mut["CURR_BUTTON"] == 0:
        load_pic = "load_sel.png"
    elif config.mut["CURR_BUTTON"] == 1:
        quit_pic = "quit_sel.png"
    elif config.mut["CURR_BUTTON"] == 2:
        up_pic = "loadgame_up_sel.png"
    else:
        down_pic = "loadgame_down_sel.png"
    g.screen.blit(g.buttons[up_pic], (config.TILESIZE * g.main.mapsizex / 4, config.TILESIZE * g.main.mapsizey / 3))
    g.screen.blit(
        g.buttons[down_pic],
        (
            config.TILESIZE * g.main.mapsizex / 4,
            config.TILESIZE * g.main.mapsizey / 3 + 140 - g.buttons["loadgame_down.png"].get_height(),
        ),
    )
    g.screen.blit(
        g.buttons[load_pic], (config.TILESIZE * g.main.mapsizex / 4, config.TILESIZE * g.main.mapsizey / 3 + 140)
    )
    g.screen.blit(
        g.buttons[quit_pic],
        (
            config.TILESIZE * g.main.mapsizex / 4 + g.buttons["load.png"].get_width(),
            config.TILESIZE * g.main.mapsizey / 3 + 140,
        ),
    )


def init_window():

    g.screen.fill(config.COLORS["purple"])
    g.load_buttons()

    # Allow the activation of debug mode from the command line
    if len(sys.argv) > 1:
        if sys.argv[1] == "-debug":
            g.debug = True
            print("Activating debug mode")

    # If there is only one module, run it.
    if len(config.MODULES) == 1:
        sel_mod(config.MODULES[0])
        return 0

    pygame.display.set_caption("Select module")
    g.mod_directory = "../modules/default/"

    # black bar
    g.create_norm_box(
        (0, config.TILESIZE * g.main.mapsizey / 2), (config.TILESIZE * g.main.mapsizex, 30), inner_color="black"
    )
    g.print_string(
        g.screen,
        "You have multiple modules installed. Pick one to play.",
        g.font,
        (config.TILESIZE * g.main.mapsizex / 2 + 10, config.TILESIZE * g.main.mapsizey / 2 + 15),
        color=config.COLORS["white"],
    )

    # box for listbox
    g.create_norm_box(
        (config.TILESIZE * g.main.mapsizex / 4 - 2, config.TILESIZE * g.main.mapsizey / 3 - 2),
        (g.buttons["loadgame_up.png"].get_width() + 4, 140 + g.buttons["load.png"].get_height() + 4),
    )

    refresh_module_info()
    refresh_buttons()

    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                key_handler(event.key)
            elif event.type == pygame.MOUSEMOTION:
                mouse_handler_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_handler_move(event.pos)
                mouse_handler_down(event.pos)

        if g.unclean_screen:
            g.unclean_screen = False
            pygame.display.flip()


def main():
    """
    The main function of the game. This is the first function called upon game start.

    :return: None
    """

    # Load assets into memory

    # Check modules to decide if selection is needed
    if len(config.MODULES) == 1:
        sel_mod(config.MODULES[0])
        return
    # TODO sel_mod can be load() within modules.py
    # Call the module selection script
    module_index = modules.select()
    sel_mod(config.MODULES[module_index])


if __name__ == "__main__":

    pygame.init()
    pygame.font.init()

    import g
    import new_game

    main()
