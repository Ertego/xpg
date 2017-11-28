import os
import pygame

_ASSETPATH = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/../assets")

texture = pygame.image.load("%s/theme/gui/textField.png" % _ASSETPATH)

font = pygame.font.Font(None, 30)


class TextField:
    def __init__(self, inputmanager, x, y, value="", onreturn=None):
        self.texture = texture.copy()
        self.base_texture = self.texture.copy()

        self.im = inputmanager

        self.font = font
        self.onreturn = onreturn
        self.text = value
        self.value = value
        self.text1 = font.render(value, True, (0, 0, 0))
        self.text2 = font.render("", True, (0, 0, 0))
        self.clickable = True
        self.position = [x, y]
        self.cursor = "|"

        self.rect = self.texture.get_rect()
        self.rect.topleft = self.position

        self.absolute_rect = self.rect.copy()

        self.cursor_pos = len(value)

        self.active = False

        self.changed = True  # force initial blit

        self.reblit()

        self.tasks = [] # schedule tasks, used to fix a render bug with disabled windows

    def tick(self, window):
        for i in self.tasks:
            i()
        self.tasks = []

        if self.input not in self.im.hooks:
            if self.active:
                self.active = False
                self.reblit()
                self.tasks.append(window.reblit)  # TODO fix blit error

    def reblit(self):
        self.texture = self.base_texture.copy()

        cursor = ""
        if self.active:
            cursor = self.cursor
        self.text1 = font.render(self.text[:self.cursor_pos] + cursor, True, (0, 0, 0))
        self.text2 = font.render(self.text[self.cursor_pos:], True, (0, 0, 0))
        rect = self.text1.get_rect()
        rect.centery = self.texture.get_rect().centery
        self.texture.blit(self.text1, rect)

        rect2 = self.text2.get_rect()
        rect2.centery = rect.centery

        self.texture.blit(self.text2, (rect.right, rect2.top))

        self.changed = True

    def input(self, key, symbol):
        if key == pygame.K_BACKSPACE:
            # self.text = self.text[:-1]
            t = list(self.text)
            if self.cursor_pos == len(self.text):
                t = t[:-1]
            elif not self.text:
                return
            else:
                print self.cursor_pos, len(self.text)
                del t[self.cursor_pos-1]

            self.text = str("".join(t))
            self.cursor_pos -= 1
            self.reblit()

        elif key == pygame.K_DELETE:
            t = list(self.text)
            if not self.cursor_pos == len(self.text):
                del t[self.cursor_pos]
                self.text = str("".join(t))
                self.reblit()

        elif key == pygame.K_RETURN:
            if self.onreturn:
                self.onreturn(self)

        elif key == pygame.K_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
            self.reblit()

        elif key == pygame.K_RIGHT:
            if self.cursor_pos < len(self.text):
                self.cursor_pos += 1
            self.reblit()

        elif key in (pygame.K_RSHIFT, pygame.K_LSHIFT):
            return

        else:
            if key not in [pygame.K_ESCAPE]:  # blacklist keys
                # self.text += symbol
                t = list(self.text)
                t.insert(self.cursor_pos, symbol)
                self.text = "".join(t)
                self.cursor_pos += 1
                self.reblit()

    def click(self):
        if self.input not in self.im.hooks:
            self.im.hooks.append(self.input)
        self.active = True
        self.reblit()
