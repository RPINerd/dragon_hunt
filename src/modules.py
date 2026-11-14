"""
Module selection screen and game initialization

Select function displays a window where the user can select a module to play
Load function initializes the game and runs the selected module
"""
from pathlib import Path

import pygame
from pygame.locals import K_DOWN, K_ESCAPE, K_RETURN, K_UP, KEYDOWN, MOUSEBUTTONDOWN, QUIT

import config
import game_screen as pygscreen
import modloader

MODULES_ROOT = Path(__file__).resolve().parent.parent / "modules"


def _is_installed_module(module_path: Path) -> bool:
    """
    Check whether a module directory contains its required game data.

    Args:
        module_path (Path): Directory to check for module data.

    Returns:
        bool: True if the required module data files are present.
    """
    maps_path = module_path / "data" / "maps"
    return (
        module_path.is_dir()
        and (module_path / "data" / "variables.txt").is_file()
        and any(map_path.is_file() for map_path in maps_path.glob("*.txt"))
    )


def discover_installed_modules(module_root: Path = MODULES_ROOT) -> list[str]:
    """
    Return module folders that contain the required game data.

    Args:
        module_root (Path): Directory containing candidate module folders.

    Returns:
        list[str]: Names of the installed module folders found.
    """
    if not module_root.is_dir():
        return []
    return sorted(
        module_path.name
        for module_path in module_root.iterdir()
        if not module_path.name.startswith(".") and _is_installed_module(module_path)
    )


def load(selected_mod: str = "DragonHunt") -> None:
    """
    Initialize and run the selected game module.

    Args:
        selected_mod (str): Name of the installed module to start.
    """
    screen = pygscreen.get_screen()
    pygame.display.set_caption("Loading")
    pygame.display.set_icon(pygame.image.load("../data/icon.png"))

    module_path = MODULES_ROOT / selected_mod
    if Path(selected_mod).name != selected_mod or not _is_installed_module(module_path):
        raise ValueError(f"Module is not installed or is missing required data: {selected_mod}")
    config.MODULES_DIR = str(module_path)
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


def select() -> int | None:
    """
    Display the module picker and return the selected module index.

    Returns:
        int | None: The chosen module index, or None if selection is cancelled.
    """
    if not config.MODULES:
        return None

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
    module_names = [
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
    while True:

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
        for i, selection in enumerate(module_names):
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
                return None

            # Keyboard input
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_index = (selected_index - 1) % len(module_names)
                elif event.key == K_DOWN:
                    selected_index = (selected_index + 1) % len(module_names)
                elif event.key == K_RETURN:
                    return selected_index
                elif event.key == K_ESCAPE:
                    return None

            # Mouse input
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                load_pos = (xres - quit_width - 5, yres - quit_height * 2 - 5)
                quit_pos = (xres - quit_width - 5, yres - quit_height - 5)
                if pygame.Rect(load_pos, icons["load"].get_size()).collidepoint(event.pos):
                    return selected_index
                if pygame.Rect(quit_pos, icons["quit"].get_size()).collidepoint(event.pos):
                    return None
                for i in range(len(module_names)):
                    option_rect = pygame.Rect(
                        xres // 4 + 5,
                        yres // 2 - list_box_height // 2 + (arrow_height * 2) + 10 + i * 30,
                        icons["loadup"].get_width(),
                        25,
                    )
                    if option_rect.collidepoint(event.pos):
                        selected_index = i
