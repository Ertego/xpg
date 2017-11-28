import os
import pygame

_ASSETPATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/../assets")

texture = pygame.image.load("%s/theme/gui/button.png" % _ASSETPATH)

font = pygame.font.Font(None, 30)


class Button:
    def __init__(self, x, y, text, onclick):
        self.text = text
        self.onclick = onclick
        self.position = [x, y]
        self.clickable = True

        self.text = font.render(self.text, True, (0, 0, 0))

        self.texture = texture.copy()

        self.text_rect = self.text.get_rect()
        self.texture_rect = self.texture.get_rect()
        self.text_rect.center = self.texture_rect.center

        self.texture.blit(self.text, self.text_rect)

        self.rect = self.texture.get_rect()
        self.rect.topleft = self.position

        self.absolute_rect = self.rect.copy()

        self.changed = True  # force initial blit

    def __str__(self):
        return self.texture

    def click(self):
        self.onclick(self)

    def move(self, d_x, d_y):
        self.position[0] = self.position[0] + d_x
        self.position[1] = self.position[1] + d_y
        self.rect.topleft = self.position
        self.absolute_rect.topleft = [self.absolute_rect.topleft[0] + d_x, self.absolute_rect.topleft[1] + d_y]
        self.changed = True

