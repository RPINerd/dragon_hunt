"""This file controls the options screen."""

from os import path

import pygame

import config
import g

# -1=none, 0=fullscreen, 1=difficulty, 2=custom key
# 5=save, 6=reset, 7=cancel
# 9=none, 10=Up, 11=Right, 12=Down, 13=Left, 14=Action, 15=Cancel, 16=reset,
# 17=back
global curr_button
curr_button = 1
global tmp_keys
tmp_keys = {}


# unfocused, inactive=gray; focused, inactive=green; focused, active=red
def box_with_text(xy, text, focused, active=False):
    in_color = "light_gray"
    if focused:
        in_color = "dh_green"
        if active:
            in_color = "light_red"
    g.create_norm_box((xy[0] + 2, xy[1] + 2), (176, 23), inner_color=in_color)
    g.print_string(g.screen, text, g.font, (xy[0] + 9, xy[1] + 10))


def refresh_window() -> None:
    """"""
    # create the window
    x_start = config.TILESIZE * config.MAPSIZE_X / 2 - 90
    y_start = config.TILESIZE * config.MAPSIZE_Y / 2 - 80
    x_width = 180
    g.create_norm_box((x_start, y_start), (x_width, 212))

    # fullscreen
    fullscreen_img = "check.png"
    if tmp_fullscreen == 1:
        fullscreen_img = "check_sel.png"
    in_color = "light_gray"
    if curr_button == 0:
        in_color = "dh_green"
    g.create_norm_box((x_start + 2, y_start + 2), (x_width - 4, 23), inner_color=in_color)
    g.screen.blit(config.BUTTONS[fullscreen_img], (x_start + 7, y_start + 3))
    g.print_string(g.screen, "Fullscreen", g.font, (x_start + 27, y_start + 10))

    # difficulty
    if tmp_difficulty == 0:
        diff_string = "Difficulty: Easy"
    elif tmp_difficulty == 1:
        diff_string = "Difficulty: Normal"
    else:
        diff_string = "Difficulty: Hard"
    focused = False
    if curr_button == 1:
        focused = True
    box_with_text((x_start, y_start + 25), diff_string, focused)

    # custom keyboard
    focused = False
    if curr_button == 2:
        focused = True
    box_with_text((x_start, y_start + 50), "Customize Keyboard", focused)

    # save setttings
    focused = False
    if curr_button == 5:
        focused = True
    box_with_text((x_start, y_start + 135), "Apply and Save Settings", focused)

    # reset setttings
    focused = False
    if curr_button == 6:
        focused = True
    box_with_text((x_start, y_start + 160), "Reset Settings", focused)

    # leave
    focused = False
    if curr_button == 7:
        focused = True
    box_with_text((x_start, y_start + 185), "Cancel (Don't Save)", focused)

    pygame.display.flip()


def refresh_key_window(adjusting: bool = False) -> None:
    """"""
    # create the window
    x_start = config.TILESIZE * config.MAPSIZE_X / 2 - 90
    y_start = config.TILESIZE * config.MAPSIZE_Y / 2 - 80
    x_width = 180
    g.create_norm_box((x_start, y_start), (x_width, 212))

    # up
    tmp_string = "Up: " + pygame.key.name(tmp_keys["up"])
    focused = False
    if curr_button == 10:
        focused = True
    box_with_text((x_start, y_start), tmp_string, focused, adjusting)

    # right
    tmp_string = "Right: " + pygame.key.name(tmp_keys["right"])
    focused = False
    if curr_button == 11:
        focused = True
    box_with_text((x_start, y_start + 25), tmp_string, focused, adjusting)

    # down
    tmp_string = "Down: " + pygame.key.name(tmp_keys["down"])
    focused = False
    if curr_button == 12:
        focused = True
    box_with_text((x_start, y_start + 50), tmp_string, focused, adjusting)

    # Left
    tmp_string = "Left: " + pygame.key.name(tmp_keys["left"])
    focused = False
    if curr_button == 13:
        focused = True
    box_with_text((x_start, y_start + 75), tmp_string, focused, adjusting)

    # Action
    tmp_string = "Action: " + pygame.key.name(tmp_keys["action"])
    focused = False
    if curr_button == 14:
        focused = True
    box_with_text((x_start, y_start + 100), tmp_string, focused, adjusting)

    # Cancel
    tmp_string = "Cancel: " + pygame.key.name(tmp_keys["cancel"])
    focused = False
    if curr_button == 15:
        focused = True
    box_with_text((x_start, y_start + 125), tmp_string, focused, adjusting)

    # reset setttings
    focused = False
    if curr_button == 16:
        focused = True
    box_with_text((x_start, y_start + 160), "Reset Settings", focused)

    # leave
    focused = False
    if curr_button == 17:
        focused = True
    box_with_text((x_start, y_start + 185), "Back", focused)

    pygame.display.flip()


def key_handler(switch: int) -> None:
    """
    All keypresses in new_game pass through here

    Based on the key name, give the right action. ("etc", "left", "right", "up", "down", "return")
    """
    global curr_button
    global tmp_fullscreen
    global tmp_difficulty
    global tmp_keys
    if switch == config.BINDINGS["cancel"]:
        cancel_settings()
    elif switch == config.BINDINGS["up"]:
        curr_button -= 1
        if curr_button <= -1:
            curr_button = 7
    elif switch == config.BINDINGS["down"]:
        curr_button += 1
        if curr_button > 7:
            curr_button = 0
    elif switch == config.BINDINGS["action"]:
        if curr_button == 0:  # fullscreen
            if tmp_fullscreen == 0:
                tmp_fullscreen = 1
            else:
                tmp_fullscreen = 0
        elif curr_button == 1:  # difficulty
            if tmp_difficulty == 0:
                tmp_difficulty = 1
            elif tmp_difficulty == 1:
                tmp_difficulty = 2
            else:
                tmp_difficulty = 0
        elif curr_button == 2:  # custom key
            curr_button = 10
            custom_key()
            curr_button = 2
        elif curr_button == 5:  # save

            # apply settings to the game
            if g.fullscreen != tmp_fullscreen:
                pygame.display.toggle_fullscreen()
            g.fullscreen = tmp_fullscreen
            g.difficulty = tmp_difficulty
            config.BINDINGS["up"] = tmp_keys["up"]
            config.BINDINGS["down"] = tmp_keys["down"]
            config.BINDINGS["right"] = tmp_keys["right"]
            config.BINDINGS["left"] = tmp_keys["left"]
            config.BINDINGS["action"] = tmp_keys["action"]
            config.BINDINGS["cancel"] = tmp_keys["cancel"]
            # Restore any shortcuts that had been removed before.
            config.BINDINGS["attack"] = pygame.K_a
            config.BINDINGS["save"] = pygame.K_s
            config.BINDINGS["quit"] = pygame.K_q
            config.BINDINGS["inv"] = pygame.K_i
            config.BINDINGS["load_console"] = pygame.K_BACKQUOTE
            # Remove any shortcuts that are already taken.
            for binding in ["up", "down", "right", "left", "action", "cancel"]:
                if config.BINDINGS[binding] == pygame.K_a:
                    config.BINDINGS["attack"] = 0
                if config.BINDINGS[binding] == pygame.K_s:
                    config.BINDINGS["save"] = 0
                if config.BINDINGS[binding] == pygame.K_q:
                    config.BINDINGS["quit"] = 0
                if config.BINDINGS[binding] == pygame.K_i:
                    config.BINDINGS["inv"] = 0
                if config.BINDINGS[binding] == pygame.K_BACKQUOTE:
                    config.BINDINGS["load_console"] = 0

            # save the settings to disk
            options_file_text = []
            if path.exists(config.MODULES_DIR + "/../../settings.txt") == 1:
                optionfile = open(config.MODULES_DIR + "/../../settings.txt")
                options_file_text = optionfile.readlines()
            else:
                "Could not open settings.txt. Not saving settings."
                cancel_settings()
                refresh_window()
                return

            for linenum in range(len(options_file_text)):
                command = options_file_text[linenum].split("=")[0].strip().lower()
                if (
                    command == "up"
                    or command == "down"
                    or command == "left"
                    or command == "right"
                    or command == "action"
                    or command == "cancel"
                    or command == "attack"
                    or command == "save"
                    or command == "quit"
                    or command == "inv"
                    or command == "load_console"
                ):
                    options_file_text[linenum] = command + "=" + str(config.BINDINGS[command]) + "\n"
                if command == "difficulty":
                    options_file_text[linenum] = command + "=" + str(g.difficulty) + "\n"
                if command == "fullscreen":
                    options_file_text[linenum] = command + "=" + str(g.fullscreen) + "\n"

            optionfile.close()
            optionfile = open(config.MODULES_DIR + "/../../settings.txt", "w")
            optionfile.writelines(options_file_text)

            cancel_settings()
        elif curr_button == 6:  # reset
            tmp_fullscreen = 0
            tmp_difficulty = 1
            tmp_keys = {}
            tmp_keys["up"] = pygame.K_UP
            tmp_keys["down"] = pygame.K_DOWN
            tmp_keys["right"] = pygame.K_RIGHT
            tmp_keys["left"] = pygame.K_LEFT
            tmp_keys["action"] = pygame.K_RETURN
            tmp_keys["cancel"] = pygame.K_ESCAPE
        elif curr_button == 7:
            cancel_settings()  # cancel
    refresh_window()


def bind_new_key(start_key):
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                return event.key
    return start_key


# key handler for the key customizer window.
def key_key_handler(switch):
    global curr_button
    global tmp_keys
    if switch == config.BINDINGS["cancel"]:
        cancel_settings()
    elif switch == config.BINDINGS["up"]:
        curr_button -= 1
        if curr_button <= 9:
            curr_button = 17
    elif switch == config.BINDINGS["down"]:
        curr_button += 1
        if curr_button > 17:
            curr_button = 10
    elif switch == config.BINDINGS["action"]:
        if curr_button == 10:  # up
            refresh_key_window(True)
            tmp_keys["up"] = bind_new_key(tmp_keys["up"])
        if curr_button == 11:  # right
            refresh_key_window(True)
            tmp_keys["right"] = bind_new_key(tmp_keys["right"])
        if curr_button == 12:  # down
            refresh_key_window(True)
            tmp_keys["down"] = bind_new_key(tmp_keys["down"])
        if curr_button == 13:  # left
            refresh_key_window(True)
            tmp_keys["left"] = bind_new_key(tmp_keys["left"])
        if curr_button == 14:  # action
            refresh_key_window(True)
            tmp_keys["action"] = bind_new_key(tmp_keys["action"])
        if curr_button == 15:  # cancel
            refresh_key_window(True)
            tmp_keys["cancel"] = bind_new_key(tmp_keys["cancel"])
        if curr_button == 16:  # reset
            tmp_keys = {}
            tmp_keys["up"] = config.BINDINGS["up"]
            tmp_keys["down"] = config.BINDINGS["down"]
            tmp_keys["right"] = config.BINDINGS["right"]
            tmp_keys["left"] = config.BINDINGS["left"]
            tmp_keys["action"] = config.BINDINGS["action"]
            tmp_keys["cancel"] = config.BINDINGS["cancel"]
        if curr_button == 17:  # back
            cancel_settings()
    refresh_key_window()


def custom_key():
    refresh_key_window()
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                key_key_handler(event.key)
                repeat_key = 0
            elif event.type == pygame.MOUSEMOTION:
                mouse_handler_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_handler_down(event.pos) == 1:
                    return


def mouse_handler_move(pos):
    pos = (pos[0], pos[1] - config.TILESIZE * config.MAPSIZE_Y / 2 + 80)
    global curr_button
    if (
        pos[0] < config.TILESIZE * config.MAPSIZE_X / 2 - 90
        or pos[0] > config.TILESIZE * config.MAPSIZE_X / 2 + 90
        or pos[1] < 0
        or pos[1] > 212
    ):
        if curr_button >= 19:
            curr_button = 19
        elif curr_button >= 9:
            curr_button = 9
            refresh_key_window()
        else:
            curr_button = -1
            refresh_window()
    elif curr_button >= 19:
        if pos[1] < 25:
            curr_button = 20
        elif pos[1] < 50:
            curr_button = 21
        elif pos[1] < 75:
            curr_button = 22
        elif pos[1] < 100:
            curr_button = 23
        elif pos[1] < 160:
            curr_button = 19
        elif pos[1] < 185:
            curr_button = 24
        elif pos[1] < 210:
            curr_button = 25
    elif curr_button >= 9:
        if pos[1] < 25:
            curr_button = 10
        elif pos[1] < 50:
            curr_button = 11
        elif pos[1] < 75:
            curr_button = 12
        elif pos[1] < 100:
            curr_button = 13
        elif pos[1] < 125:
            curr_button = 14
        elif pos[1] < 150:
            curr_button = 15
        elif pos[1] < 160:
            curr_button = 9
        elif pos[1] < 185:
            curr_button = 16
        elif pos[1] < 210:
            curr_button = 17
        refresh_key_window()
    else:
        if pos[1] < 25:
            curr_button = 0
        elif pos[1] < 50:
            curr_button = 1
        elif pos[1] < 75:
            curr_button = 2
        elif pos[1] < 100:
            curr_button = 3
        elif pos[1] < 125:
            curr_button = 4
        elif pos[1] < 135:
            curr_button = -1
        elif pos[1] < 160:
            curr_button = 5
        elif pos[1] < 185:
            curr_button = 6
        elif pos[1] < 210:
            curr_button = 7
        refresh_window()


def mouse_handler_down(pos):
    global curr_button
    if curr_button >= 9:
        key_key_handler(pygame.K_RETURN)
    else:
        key_handler(pygame.K_RETURN)


def init_window_options():
    global curr_button
    curr_button = 0

    global tmp_fullscreen
    global tmp_difficulty
    global tmp_keys
    tmp_fullscreen = g.fullscreen
    tmp_difficulty = g.difficulty
    tmp_keys = {}
    tmp_keys["up"] = config.BINDINGS["up"]
    tmp_keys["down"] = config.BINDINGS["down"]
    tmp_keys["right"] = config.BINDINGS["right"]
    tmp_keys["left"] = config.BINDINGS["left"]
    tmp_keys["action"] = config.BINDINGS["action"]
    tmp_keys["cancel"] = config.BINDINGS["cancel"]
    refresh_window()
    while True:
        pygame.time.wait(30)
        g.clock.tick(30)
        if g.break_one_loop > 0:
            g.break_one_loop -= 1
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                key_handler(event.key)
                repeat_key = 0
            elif event.type == pygame.MOUSEMOTION:
                mouse_handler_move(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_handler_down(event.pos) == 1:
                    return


def cancel_settings():
    g.break_one_loop = 1
