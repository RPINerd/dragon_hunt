"""Widgets for neater implememntation of UI elements."""
import pygame
from icecream import ic

import config
import game_screen as pygscreen

screen = pygscreen.get_screen()


class Button:

    """"""

    def __init__(
        self,
        coords: tuple[int, int],
        dimensions: tuple[int, int],
        color: pygame.typing.ColorLike,
        text: str = "",
        font: pygame.font = None,
        image: pygame.image = None
    ) -> None:
        """"""
        self.x = coords[0]
        self.y = coords[1]
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.text = text
        self.font = font
        self.color = color
        self.image = image

    def draw(self, screen: pygame.Surface) -> None:
        """"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


class Listbox:

    """"""

    def __init__(self, xy, size, viewable_items, lines_per_item, bg_color, sel_color, out_color, font_color, font):
        """"""
        self.xy = xy
        self.size = (size[0], size[1] - 1)
        self.viewable_items = viewable_items
        self.lines_per_item = lines_per_item
        self.bg_color = bg_color
        self.sel_color = sel_color
        self.out_color = out_color
        self.font_color = font_color
        self.font = font

        self.list_surface = pygame.Surface((self.size[0], self.size[1] + 1))

        # create outline
        self.list_surface.fill(out_color)

        # create inner containers:
        for i in range(viewable_items):
            self.list_surface.fill(
                bg_color,
                (
                    1,
                    1 + i * self.size[1] / self.viewable_items,
                    self.size[0] - 2,
                    self.size[1] / self.viewable_items - 1,
                ),
            )

    def refresh_listbox(self, selected, lines_array):
        if len(lines_array) != self.viewable_items:
            ic("CRASH WARNING: len(lines_array)=" + str(len(lines_array)))
            ic("CRASH WARNING: self.viewable_items=" + str(self.viewable_items))
            return 0

        if selected >= self.viewable_items:
            ic("Error in refresh_listbox(). selected =" + str(selected))
            selected = 0

        if len(lines_array) % (self.viewable_items * self.lines_per_item) != 0:
            ic("Error in refresh_listbox(). len(lines_array)=" + str(len(lines_array)))
            return 0

        screen.blit(self.list_surface, self.xy)

        # selected:
        screen.fill(
            self.sel_color,
            (
                self.xy[0] + 1,
                self.xy[1] + 1 + selected * self.size[1] / self.viewable_items,
                self.size[0] - 2,
                self.size[1] / self.viewable_items - 1,
            ),
        )

        # text:
        txt_y_size = self.font.size("")
        for i in range(self.viewable_items):
            for j in range(self.lines_per_item):
                print_string(
                    screen,
                    lines_array[i * self.lines_per_item + j],
                    self.font,
                    (self.xy[0] + 4, self.xy[1] + (i * self.size[1]) / self.viewable_items + j * (txt_y_size[1] + 2)),
                    self.font_color,
                )
        return 1

    def is_over(self, xy: tuple[int, int]) -> int:
        """"""
        if (
            xy[0] >= self.xy[0]
            and xy[1] >= self.xy[1]
            and xy[0] <= self.xy[0] + self.size[0]
            and xy[1] < self.xy[1] + self.size[1]
        ):
            return (xy[1] - self.xy[1]) * self.viewable_items / self.size[1]

        return -1


class Scrollbar:

    """"""

    def __init__(self, xy, size, viewable_items, bg_color, fore_color, out_color):
        """"""
        self.xy = xy
        self.size = (18, size)
        self.viewable_items = viewable_items
        self.space_for_each = size / viewable_items
        self.bg_color = bg_color
        self.out_color = out_color
        self.fore_color = fore_color

        self.scroll_area = size - 18 * 2

        self.scroll_surface = pygame.Surface(self.size)

        # create outline
        self.scroll_surface.fill(out_color)

        # create arrow bgs
        self.scroll_surface.fill(fore_color, (1, 1, self.size[0] - 2, self.size[0] - 2))

        self.scroll_surface.fill(fore_color, (1, self.size[1] - 17, self.size[0] - 2, self.size[0] - 2))

        # create inner
        self.scroll_surface.fill(bg_color, (1, self.size[0], self.size[0] - 2, self.size[1] - 36))

        # create arrows
        self.scroll_surface.blit(config.BUTTONS["arrow.png"], (1, 1))
        self.scroll_surface.blit(pygame.transform.flip(config.BUTTONS["arrow.png"], 0, 1), (1, self.size[1] - 17))

        self.refresh_scroll(0, 100)

    def refresh_scroll(self, start_item, total_items):
        start_item = min(start_item, total_items - self.viewable_items)

        screen.blit(self.scroll_surface, self.xy)

        # middle gripper
        self.start_y = self.size[0] + (self.scroll_area * start_item) / total_items
        self.size_y = (self.scroll_area * self.viewable_items) / total_items

        screen.fill(self.fore_color, (self.xy[0] + 1, self.xy[1] + self.start_y, self.size[0] - 2, self.size_y))

    def is_over(self, xy):
        if (
            xy[0] >= self.xy[0]
            and xy[1] >= self.xy[1]
            and xy[0] <= self.xy[0] + self.size[0]
            and xy[1] <= self.xy[1] + self.size[1]
        ):
            if xy[1] <= self.xy[1] + self.size[0]:  # up arrow
                return 1
            if xy[1] >= self.xy[1] + self.size[1] - self.size[0]:  # dn arrow
                return 2
            if xy[1] <= self.xy[1] + self.start_y:  # upper gutter
                return 3
            if xy[1] >= self.xy[1] + self.start_y + self.size_y:  # lower gutterx
                return 4
            # If I want the gripper working, code here.
        return -1

    def adjust_pos(self, event, list_pos, item_list):
        if event.type != pygame.MOUSEBUTTONUP:
            return list_pos
        if event.button != 1:
            return list_pos
        xy = event.pos
        tmp = self.is_over(xy)
        if tmp == 1:
            list_pos -= 1
            list_pos = max(list_pos, 0)
        elif tmp == 2:
            list_pos += 1
            if list_pos >= len(item_list):
                list_pos = len(item_list) - 1
        elif tmp == 3:
            list_pos -= self.viewable_items
            list_pos = max(list_pos, 0)
        elif tmp == 4:
            list_pos += self.viewable_items
            list_pos = min(len(item_list) - 1, list_pos)
        return list_pos


def refresh_list(listbox: Listbox, scrollbar: Scrollbar, list_pos: int, list_array: list) -> None:
    """"""
    selected_item = list_pos % listbox.viewable_items
    viewable_items = listbox.viewable_items
    start_pos = int((list_pos / viewable_items) * viewable_items)
    end_pos = int(start_pos + viewable_items)

    tmp = listbox.refresh_listbox(selected_item, list_array[start_pos:end_pos])

    if tmp == 0:
        ic(list_array)
    if scrollbar != 0:
        scrollbar.refresh_scroll(
            list_pos, ((len(list_array) / listbox.viewable_items) + 1) * listbox.viewable_items - 1
        )
    pygame.display.flip()


def bordered_box(
    screen: pygame.Surface,
    xy: list | tuple,
    size: list | tuple,
    outline_color: str = "black",
    inner_color: str = "light_gray") -> None:
    """
    Create a box on the screen with the given parameters.

    Args:
        screen (pygame.Surface): The surface to draw on.
        xy (list | tuple): The coordinates of the box (x, y).
        size (list | tuple): The size of the box (width, height).
        outline_color (str): The color of the box outline.
        inner_color (str): The color of the inner box.
    """
    screen.fill(config.COLORS[outline_color], (xy[0], xy[1], size[0], size[1]))
    screen.fill(config.COLORS[inner_color], (xy[0] + 1, xy[1] + 1, size[0] - 2, size[1] - 2))


def print_string(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    xy: tuple[int, int],
    color: pygame.typing.ColorLike = config.COLORS["black"],
    align: int = 0,
    width: int = -1) -> None:
    """
    Print a string to the screen

    Args:
        surface (pygame.Surface): The surface to print to
        text (str): The string to print
        font (pygame.font.Font): The font to use
        xy (tuple): The xy coordinates to print the text at
        color (pygame.ColorLike): The color to print the text in
        align (int): 0=left, 1=center, 2=right
        width (int): The width of the text box. -1 for no limit.
    """
    text = text.replace("\t", "     ")
    if align != 0:
        temp_size = font.size(text)
        if align == 1:
            xy = (xy[0] - temp_size[0] / 2, xy[1])
        else:
            xy = (xy[0] - temp_size[0], xy[1])
    temp_text = font.render(text, 1, color)
    if width != -1:
        surface.blit(temp_text, xy, (0, 0, width, temp_text.get_size()[1]))
    else:
        surface.blit(temp_text, xy)


def print_paragraph(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    width: int,
    xy: tuple[int, int],
    color: pygame.typing.ColorLike = config.COLORS["black"]) -> int:
    r"""
    Print a string to the screen, wrapping it to fit within a certain width

    Used to display descriptions and such.

    Note that bkshl+n can be used for newlines, but it must be used as
    `line1 \\n line2` in code, separated by spaces, with the bkshl escaped)
    Escape not needed in scripts.

    Args:
        surface (pygame.Surface): The surface to print to
        text (str): The string to print
        font (pygame.font.Font): The font to use
        width (int): The width to wrap the text to
        xy (tuple): The xy coordinates to print the text at
        color (pygame.ColorLike): The color to print the text in

    Returns:
        int: The number of lines printed
    """
    text = text.replace("\t", "     ")
    start_xy = xy
    string_array = text.split(" ")

    num_of_lines = 1
    for string in string_array:
        string += " "
        temp_size = font.size(string)

        if string == "\n ":
            num_of_lines += 1
            xy = (start_xy[0], xy[1] + temp_size[1])
            continue
        temp_text = font.render(string, 1, color)

        if (xy[0] - start_xy[0]) + temp_size[0] > width:
            num_of_lines += 1
            xy = (start_xy[0], xy[1] + temp_size[1])
        surface.blit(temp_text, xy)
        xy = (xy[0] + temp_size[0], xy[1])
    return num_of_lines
