"""Widgets for neater implememntation of UI elements."""
import pygame

import g


class Button:

    """"""

    def __init__(
        self,
        x: int | float,
        y: int | float,
        width: int,
        height: int,
        color,
        text: str = "",
        font: pygame.font = None,
        image: pygame.image = None
    ) -> None:
        """"""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
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
            print("CRASH WARNING: len(lines_array)=" + str(len(lines_array)))
            print("CRASH WARNING: self.viewable_items=" + str(self.viewable_items))
            return 0

        if selected >= self.viewable_items:
            print("Error in refresh_listbox(). selected =" + str(selected))
            selected = 0

        if len(lines_array) % (self.viewable_items * self.lines_per_item) != 0:
            print("Error in refresh_listbox(). len(lines_array)=" + str(len(lines_array)))
            return 0

        g.screen.blit(self.list_surface, self.xy)

        # selected:
        g.screen.fill(
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
                g.print_string(
                    g.screen,
                    lines_array[i * self.lines_per_item + j],
                    self.font,
                    (self.xy[0] + 4, self.xy[1] + (i * self.size[1]) / self.viewable_items + j * (txt_y_size[1] + 2)),
                    self.font_color,
                )
        return 1

    def is_over(self, xy):
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
        self.scroll_surface.blit(g.buttons["arrow.png"], (1, 1))
        self.scroll_surface.blit(pygame.transform.flip(g.buttons["arrow.png"], 0, 1), (1, self.size[1] - 17))

        self.refresh_scroll(0, 100)

    def refresh_scroll(self, start_item, total_items):
        start_item = min(start_item, total_items - self.viewable_items)

        g.screen.blit(self.scroll_surface, self.xy)

        # middle gripper
        self.start_y = self.size[0] + (self.scroll_area * start_item) / total_items
        self.size_y = (self.scroll_area * self.viewable_items) / total_items

        g.screen.fill(self.fore_color, (self.xy[0] + 1, self.xy[1] + self.start_y, self.size[0] - 2, self.size_y))

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


def refresh_list(listbox: Listbox, scrollbar: Scrollbar, list_pos, list_array):
    """"""
    tmp = listbox.refresh_listbox(
        list_pos % listbox.viewable_items,
        list_array[
            (list_pos / listbox.viewable_items)
            * listbox.viewable_items : (list_pos / listbox.viewable_items)
            * listbox.viewable_items
            + listbox.viewable_items
        ],
    )
    if tmp == 0:
        print(list_array)
    if scrollbar != 0:
        scrollbar.refresh_scroll(
            list_pos, ((len(list_array) / listbox.viewable_items) + 1) * listbox.viewable_items - 1
        )
    pygame.display.flip()
