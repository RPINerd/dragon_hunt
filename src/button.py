import pygame


class Button:
    def __init__(
        self, x, y, width, height, color, text: str = "", font: pygame.font = None, image: pygame.image = None
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.color = color
        self.image = image

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
