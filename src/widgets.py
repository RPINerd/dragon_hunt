"""Widgets for neater implememntation of UI elements."""
import logging

import pygame

import config
import game_screen as pygscreen

logger = logging.getLogger(__name__)

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
        """
        Create a button with its position, appearance, and optional content.

        Args:
            coords (tuple[int, int]): Top-left screen coordinates.
            dimensions (tuple[int, int]): Button width and height.
            color (pygame.typing.ColorLike): Fill color.
            text (str): Button label.
            font (pygame.font): Font associated with the button.
            image (pygame.image): Image associated with the button.
        """
        self.x = coords[0]
        self.y = coords[1]
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.text = text
        self.font = font
        self.color = color
        self.image = image

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the button rectangle on a surface.

        Args:
            screen (pygame.Surface): Surface to draw on.
        """
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))


class Listbox:

    """"""

    def __init__(self, xy, size, viewable_items, lines_per_item, bg_color, sel_color, out_color, font_color, font):
        """
        Create a list box with the requested layout and colors.

        Args:
            xy (tuple[int, int]): Top-left screen coordinates.
            size (tuple[int, int]): List-box width and height.
            viewable_items (int): Number of visible list entries.
            lines_per_item (int): Text lines displayed for each entry.
            bg_color (pygame.typing.ColorLike): Entry background color.
            sel_color (pygame.typing.ColorLike): Selected-entry color.
            out_color (pygame.typing.ColorLike): List-box outline color.
            font_color (pygame.typing.ColorLike): Text color.
            font (pygame.font.Font): Font used to render entries.
        """
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
        """
        Draw the list entries and indicate the selected entry.

        Args:
            selected (int): Visible entry index to highlight.
            lines_array (list[str]): Text lines for the visible entries.

        Returns:
            int: 1 on success, or 0 if the supplied list is invalid.
        """
        if len(lines_array) != self.viewable_items:
            logger.error(
                "Listbox line count %d does not match viewable item count %d.",
                len(lines_array),
                self.viewable_items,
            )
            return 0

        if selected >= self.viewable_items:
            logger.warning("Invalid refresh_listbox selection: %s", selected)
            selected = 0

        if len(lines_array) % (self.viewable_items * self.lines_per_item) != 0:
            logger.error("Invalid refresh_listbox line count: %d", len(lines_array))
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
        """
        Return the visible entry under a pointer position.

        Args:
            xy (tuple[int, int]): Pointer coordinates.

        Returns:
            float: Entry position within the list box, or -1 if outside.
        """
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
        """
        Create and draw a scrollbar for a list.

        Args:
            xy (tuple[int, int]): Top-left screen coordinates.
            size (int): Scrollbar height.
            viewable_items (int): Number of list entries visible at once.
            bg_color (pygame.typing.ColorLike): Scrollbar track color.
            fore_color (pygame.typing.ColorLike): Thumb and arrow background color.
            out_color (pygame.typing.ColorLike): Scrollbar outline color.
        """
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
        """
        Redraw the scrollbar thumb for the current list position.

        Args:
            start_item (int): Index of the first visible list item.
            total_items (int): Total number of list items.
        """
        start_item = min(start_item, total_items - self.viewable_items)

        screen.blit(self.scroll_surface, self.xy)

        # middle gripper
        self.start_y = self.size[0] + (self.scroll_area * start_item) / total_items
        self.size_y = (self.scroll_area * self.viewable_items) / total_items

        screen.fill(self.fore_color, (self.xy[0] + 1, self.xy[1] + self.start_y, self.size[0] - 2, self.size_y))

    def is_over(self, xy):
        """
        Identify the scrollbar region at a pointer position.

        Args:
            xy (tuple[int, int]): Pointer coordinates.

        Returns:
            int: Region code for an arrow or gutter, or -1 if outside the scrollbar.
        """
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
        """
        Adjust the list position in response to a scrollbar click.

        Args:
            event (pygame.event.Event): Mouse event to process.
            list_pos (int): Current selected list index.
            item_list (list): Items in the list.

        Returns:
            int: Updated selected list index.
        """
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
    """
    Redraw a list box and its optional scrollbar.

    Args:
        listbox (Listbox): List box to refresh.
        scrollbar (Scrollbar): Scrollbar to refresh, or 0 if absent.
        list_pos (int): Selected item index.
        list_array (list): List content to display.
    """
    selected_item = list_pos % listbox.viewable_items
    viewable_items = listbox.viewable_items
    start_pos = int((list_pos / viewable_items) * viewable_items)
    end_pos = int(start_pos + viewable_items)

    tmp = listbox.refresh_listbox(selected_item, list_array[start_pos:end_pos])

    if tmp == 0:
        logger.debug("Listbox items: %s", list_array)
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
    Draw a filled box with an outline.

    Args:
        screen (pygame.Surface): Surface to draw on.
        xy (list | tuple): Top-left coordinates.
        size (list | tuple): Box width and height.
        outline_color (str): Configured outline color name.
        inner_color (str): Configured fill color name.
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
    Render a single line of text on a surface.

    Args:
        surface (pygame.Surface): Surface to draw on.
        text (str): Text to render.
        font (pygame.font.Font): Font used to render the text.
        xy (tuple[int, int]): Position or alignment anchor.
        color (pygame.typing.ColorLike): Text color.
        align (int): Alignment: 0 left, 1 center, 2 right.
        width (int): Optional clipping width; -1 disables clipping.
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
    """
    Render text wrapped to fit within a maximum width.

    Tabs are expanded before wrapping; script line breaks are preserved.

    Args:
        surface (pygame.Surface): Surface to draw on.
        text (str): Text to render.
        font (pygame.font.Font): Font used to render the text.
        width (int): Maximum line width in pixels.
        xy (tuple[int, int]): Top-left position.
        color (pygame.typing.ColorLike): Text color.

    Returns:
        int: Number of lines rendered.
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
