"""
Module selection screen and game initialization

Select function displays a window where the user can select a module to play
Load function initializes the game and runs the selected module
"""
import pygame
from pygame.locals import K_DOWN, K_RETURN, K_UP, KEYDOWN, MOUSEBUTTONDOWN, QUIT

import config
import game_screen as pygscreen
import modloader


def load(selected_mod: str = "DragonHunt") -> None:
    """
    Initialize and run the provided module.

    This is effectively the main launching point for the game, starting up the core game window and loop.

    Args:
        selected_mod (str): The selected module to run.

    Returns:
        None
    """
    screen = pygscreen.get_screen()
    pygame.display.set_caption("Loading")
    pygame.display.set_icon(pygame.image.load("../data/icon.png"))

    config.MODULES_DIR = "../modules/" + selected_mod
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    pygame.draw.rect(
        screen,
        config.COLORS["black"],
        (screen_width / 4, screen_height / 3, screen_width / 2, screen_height / 3),
    )

    font = pygame.font.Font(None, 26)
    text = "Loading. Please wait..."
    text_surface = font.render(text, True, config.COLORS["white"])
    text_rect = text_surface.get_rect()
    text_rect.center = (screen_width / 2, screen_height / 2)
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    modloader.init_gamedata()


def select() -> int:
    """
    Display a menu to select a module.

    Returns:
        The index of the selected module to load
    """
    selected_index = 0
    xres = 1024
    yres = 768
    icons = {
        "loadup": pygame.image.load("../data/buttons/loadgame_up.png"),
        "loadupsel": pygame.image.load("../data/buttons/loadgame_up_sel.png"),
        "loaddown": pygame.image.load("../data/buttons/loadgame_down.png"),
        "loaddownsel": pygame.image.load("../data/buttons/loadgame_down_sel.png"),
        "load": pygame.image.load("../data/buttons/load.png"),
        "loadsel": pygame.image.load("../data/buttons/load_sel.png"),
        "quit": pygame.image.load("../data/buttons/quit.png"),
        "quitsel": pygame.image.load("../data/buttons/quit_sel.png"),
    }
    arrow_height = icons["loadup"].get_height()
    quit_height = icons["quit"].get_height()
    quit_width = icons["quit"].get_width()

    # Reformat list of modules so that the words have spaces between them
    modules = [
        module[0] + "".join([" " + char if char.isupper() else char for char in module[1:]])
        for module in config.MODULES
    ]

    # Limit the framerate to 30
    clock = pygame.time.Clock()
    clock.tick(30)

    # Set up the display
    screen = pygscreen.get_screen()
    pygame.display.set_caption("Select Module")
    pygame.display.set_icon(pygame.image.load("../data/icon.png"))

    # Set up the font
    font = pygame.font.Font(None, 18)

    # Main game loop
    running = True
    while running:

        # Clear the screen
        screen.fill(config.COLORS["purple"])

        # Draw the black accent rectangle
        rect_height = int(0.15 * yres)
        pygame.draw.rect(screen, config.COLORS["black"], (0, yres // 2 - rect_height // 2, xres, rect_height))

        # White module selection text
        text = "You have multiple modules installed, please pick one to play!"
        mod_font = pygame.font.Font(None, 26)
        text_surface = mod_font.render(text, True, config.COLORS["white"])
        text_rect = text_surface.get_rect()
        text_rect.right = xres - 30
        text_rect.top = (yres // 2) - (text_rect.height // 2)
        screen.blit(text_surface, text_rect)

        # Create the white background box for the module list
        list_box_height = (25 * 5) + (2 * arrow_height) + quit_height + 10
        pygame.draw.rect(
            screen,
            config.COLORS["white"],
            (xres // 4, yres // 2 - list_box_height // 2, icons["loadup"].get_width() + 10, list_box_height),
        )

        # Place the load and quit buttons in the lower right corner
        screen.blit(icons["load"], (xres - quit_width - 5, yres - quit_height * 2 - 5))
        screen.blit(icons["quit"], (xres - quit_width - 5, yres - quit_height - 5))

        # Highlight the selected option
        pygame.draw.rect(
            screen,
            config.COLORS["light_gray"],
            (
                xres // 4 + 5,
                yres // 2 - list_box_height // 2 + (arrow_height * 1.5) + 5 + selected_index * 30,
                icons["loadup"].get_width(),
                25,
            ),
        )

        # Render the up arrow
        screen.blit(icons["loadupsel"], (xres // 4 + 5, yres // 2 - list_box_height // 2 + 5))

        # Render the selections
        for i, selection in enumerate(modules):
            text = font.render(selection, True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = (
                xres // 4 + icons["loadup"].get_width() // 2 + 5,
                yres // 2 - list_box_height // 2 + (arrow_height * 2) + 10 + i * 30,
            )
            screen.blit(text, text_rect)

        # Render the down arrow
        screen.blit(
            icons["loaddownsel"],
            (xres // 4 + 5, yres // 2 + list_box_height // 2 - icons["loaddown"].get_height() - 5),
        )

        # Update the display
        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():

            # Closing the window
            if event.type == QUIT:
                pygame.quit()

            # Keyboard input
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_index = (selected_index - 1) % len(modules)
                elif event.key == K_DOWN:
                    selected_index = (selected_index + 1) % len(modules)
                elif event.key == K_RETURN:
                    running = False

            # Mouse input
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, selection in enumerate(modules):
                    if (
                        xres // 4 + 5 < mouse_pos[0] < xres // 4 + 5 + icons["loadup"].get_width()
                        and yres // 2 - list_box_height // 2 + (arrow_height * 2) + 10 + i * 30
                        < mouse_pos[1]
                        < yres // 2 - list_box_height // 2 + (arrow_height * 2) + 10 + i * 30 + 25
                    ):
                        selected_index = i

    return selected_index
