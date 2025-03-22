""""""
import pygame


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
