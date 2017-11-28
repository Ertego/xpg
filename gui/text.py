import pygame

font = pygame.font.Font(None, 30)


class Text:
    def __init__(self, x, y, text, color):
        self.font = font
        self.text = text
        self.color = color
        self.clickable = False
        self.position = [x, y]

        self.texture = self.font.render(self.text, True, self.color)

        self.rect = self.texture.get_rect()
        self.rect.topleft = self.position

        self.absolute_rect = self.rect.copy()

        self.changed = True  # force initial blit

    def __str__(self):
        return self.texture
