import pygame


class KeyHandler:
    def __init__(self):
        pygame.init()
        self.key_pressed = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.key_pressed = event.key

    def get_key_pressed(self):
        return self.key_pressed

    def reset_key_pressed(self):
        self.key_pressed = None
