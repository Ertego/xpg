import pygame

import os

import sys

_ASSETPATH = os.path.dirname(os.path.realpath(__file__)) + "/assets"

GLOBAL_SURFACE = pygame.Surface((0, 0))

_titlebar_components = {"left_end": pygame.image.load("%s/theme/titlebar_left.png" % _ASSETPATH),
                        "right_end": pygame.image.load("%s/theme/titlebar_right.png" % _ASSETPATH),
                        "middle": pygame.image.load("%s/theme/titlebar_tile.png" % _ASSETPATH),
                        "closebutton": pygame.image.load("%s/theme/closebutton.png" % _ASSETPATH)}

UPDATE = []

pygame.font.init()

_titlefont = pygame.font.Font(None, 30)

rlarrow_strings = (  # sized 24x24
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "   XXX           XXX    ",
    "  X..X           X..X   ",
    " X...XXXXXXXXXXXXX...X  ",
    "X.....................X ",
    " X...XXXXXXXXXXXXX...X  ",
    "  X..X           X..X   ",
    "   XXX           XXX    ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ",
    "                        ")

cursor_rlarrow = pygame.cursors.compile(pygame.cursors.sizer_x_strings, black='X', white='.', xor='o')
cursor_udarrow = pygame.cursors.compile(pygame.cursors.sizer_y_strings, black='X', white='.', xor='o')


class WindowManager:
    def __init__(self, input_manager=None):
        self.windows = []
        self.ddm = None

        self.im = input_manager

        self.scheduled_updates = []

        self.closed_window_rects = []

    def register_window(self, window):
        self.windows.append(window)
        window.reblit()

    def loop(self):
        global UPDATE
        # print [x.__str__() for x in self.windows]
        for window in self.windows[:]:
            window.tick()
            window.blit()

        for window in self.windows[:]:

            # TODO: Remove Patchwork

            if window.closed:
                self.windows.remove(window)

                sur = pygame.Surface(window.size, pygame.SRCALPHA, 32)
                # sur.fill((0, 0, 0))
                GLOBAL_SURFACE.blit(sur, window.position)

                UPDATE.append(window.rect)

                self.closed_window_rects.append([20, window.rect])
                self.closed_window_rects.append([20, window.titlebar.rect])

        for i in self.closed_window_rects[:]:
            UPDATE.append(i[1])
            i[0] = i[0] - 1
            if i[0] == 0:
                self.closed_window_rects.remove(i)

        pygame.display.update(UPDATE)
        UPDATE = []

    def reblit_all_windows(self, update=True):
        for window in self.windows:
            window.reblit(update)
            window.titlebar.blit()

    def click(self, pos):
        for window in self.windows[::-1]:
            if window.rect.collidepoint(pos):
                self.focus_window(window)
                window.click(pos)
                break

    def focus_window(self, window):
        if window not in self.windows:
            raise ValueError("Window not managed by this WindowManager")
        print window
        self.windows.remove(window)
        self.windows.append(window)
        # self.reblit_all_windows(False)
        self.ddm.mouse_down(window.titlebar.position)
        self.ddm.drop_mousedrag = True
        window.titlebar.blit()  # 27.11.17 experimental edit

        if self.im is not None:
            self.im.hooks = []


class DragDropManager:
    def __init__(self, window_manager):
        self.mouse_pressed = False
        self.wm = window_manager
        self.wm.ddm = self
        self.moving_window = None
        self.drop_mousedrag = False
        self.resizing_window = [None]
        self.last_cursor = "arrow"

    def mouse_down(self, pos=None):
        if pos is None:
            pos = pygame.mouse.get_pos()
        self.mouse_pressed = True
        for window in self.wm.windows[:]:
            if window.titlebar.rect.collidepoint(pos):
                window.moving = True
                self.moving_window = window
                pygame.mouse.get_rel()
                self.wm.windows.remove(window)
                self.wm.windows.append(window)
                # break
        for window in self.wm.windows[::-1]:
            for idx, button in enumerate(window.titlebar.buttons):
                button.update(idx)
                if button.abs_rect.collidepoint(pos):
                    button.click()
                    break

    def mouse_up(self):
        self.mouse_pressed = False
        if self.moving_window:
            self.moving_window.moving = False
        self.moving_window = None
        self.resizing_window = [None]

    def loop(self):
        if self.moving_window or self.resizing_window[0]:
            # screen.fill((0, 0, 0))
            delta = 0

            if self.moving_window:
                delta = pygame.mouse.get_rel()
                self.moving_window.move(delta[0], delta[1])
                self.moving_window.reblit()

            if self.resizing_window[0]:
                if self.resizing_window[2] == 0:
                    delta = pygame.mouse.get_rel()
                    self.resizing_window[0].resize(delta[0], 0, True)
                if self.resizing_window[2] == 2:
                    delta = pygame.mouse.get_rel()
                    self.resizing_window[0].resize(delta[0], 0, False)

                if self.resizing_window[2] == 1:  # up/down resize
                    delta = pygame.mouse.get_rel()
                    self.resizing_window[0].resize(0, delta[1], False)

            update_field = (abs(delta[0]) + abs(delta[1]) + 10) * 2

            if self.moving_window:
                rect = self.moving_window.rect.copy()
                window = self.moving_window
            if self.resizing_window[0]:
                rect = self.resizing_window[1]
                window = self.resizing_window[0]

            rect.topleft = [rect.topleft[0] - update_field / 2,
                            rect.topleft[1] - (update_field / 2 + window.titlebar.height)]
            rect.size = [rect.size[0] + update_field, rect.size[1] + update_field + window.titlebar.height]

            # pygame.draw.rect(screen, (0, 255, 0), rect)

            UPDATE.append(rect)

            if self.moving_window:
                for window in self.wm.windows:
                    if window.rect.colliderect(rect) or window.titlebar.rect.colliderect(rect):
                        window.reblit()
                        window.titlebar.blit()
            if self.resizing_window[0]:
                for window in self.wm.windows:
                    window.reblit()
                    window.titlebar.blit()

        if self.drop_mousedrag:
            self.mouse_up()
            self.drop_mousedrag = False

        # do drag-resize

        over_border = False
        if not self.moving_window:
            for window in self.wm.windows:
                if window.resizeable:
                    for idx, border in enumerate(window.border.borderrects):
                        if border.collidepoint(pygame.mouse.get_pos()):
                            over_border = True
                            self.last_cursor = "lr"
                            # print idx

                            if idx in (0, 2):  # left or right border
                                pygame.mouse.set_cursor((24, 16), (12, 12), cursor_rlarrow[0], cursor_rlarrow[1])
                            if idx == 1:
                                self.last_cursor = "uo"
                                pygame.mouse.set_cursor((24, 16), (12, 12), cursor_udarrow[0], cursor_udarrow[1])

                            if pygame.mouse.get_pressed()[0]:
                                self.resizing_window = [window, border, idx]
                                pygame.mouse.get_rel()

        if not over_border and not self.last_cursor == "arrow" and not pygame.mouse.get_pressed()[0]:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self.last_cursor = "arrow"


class InputManager:
    def __init__(self):
        self.pressed_keys = []
        self.hooks = []

    def report_input(self, key, symbol):
        self.pressed_keys.append([key, symbol])
        for element in self.hooks:
            element(key, symbol)

    def report_release(self, key):
        symbol = ""

        for ev in self.pressed_keys:
            if ev[0] == key:
                symbol = ev[1]

        if key in self.pressed_keys:
            self.pressed_keys.remove([key, symbol])


class WindowBorder:
    def __init__(self, window, size, bordersize=3):
        self.size = size
        self.window = window
        self.bordersize = bordersize
        self.draw()
        self.borderrects = []

    def draw(self):
        if not self.window.borderless:
            self.borderrects = []
            a = pygame.draw.line(self.window.texture, (0, 0, 0), (0, 0), (0, self.window.size[1]), self.bordersize)
            b = pygame.draw.line(self.window.texture, (0, 0, 0), (0, self.window.size[1] - 1),
                                 (self.window.size[0], self.window.size[1] - 1), self.bordersize)
            c = pygame.draw.line(self.window.texture, (0, 0, 0), (self.window.size[0] - 1, self.window.size[1]),
                                 (self.window.size[0] - 1, 0), self.bordersize)

            a.width = self.bordersize
            a.topleft = [a.topleft[0] + self.window.position[0], a.topleft[1] + self.window.position[1]]

            c.width = self.bordersize
            c.topleft = [c.topleft[0] + self.window.position[0], c.topleft[1] + self.window.position[1]]

            b.height = self.bordersize
            b.topleft = [b.topleft[0] + self.window.position[0], b.topleft[1] + self.window.position[1]]

            self.borderrects.extend((a, b, c))


class Window:
    def __init__(self, surface, size=(100, 100), title="", icon=None, position=(50, 50)):
        self.surface = surface
        self.contents = []
        self.size = list(size)
        self.title = title

        self.closeable = True
        self.resizeable = True
        self.borderless = False
        self._disabled = False

        self.icon = icon
        self.position = list(position)
        self.titlebar = TitleBar(self, self.title)
        self.texture = pygame.Surface(self.size)
        self.border = WindowBorder(self, self.size)

        self.rect = pygame.Rect((self.position[0], self.position[1], self.size[0], self.size[1]))
        self.reblit()
        self.moving = False

        self.minimal_size = [50, 50]

        self.closed = False

    def __str__(self):
        return "xpg window %s at %s" % (self.title, self.position)

    def tick(self):
        for component in self.contents:
            if hasattr(component, "tick"):
                component.tick(self)

    def get_elements(self, parent_class):
        return [x for x in self.contents if isinstance(x, parent_class)]

    def disable(self, im=None):
        self._disabled = True
        self.reblit()
        im.hooks = []

    def enable(self):
        self._disabled = False
        self.reblit()

    def reblit(self, update=True):
        self.texture.fill((255, 255, 255))
        self.border.draw()
        self.surface.blit(self.texture, self.position)
        for element in self.contents:
            self.texture.blit(element.texture, element.rect)
            element.absolute_rect = element.rect.copy()
            element.absolute_rect.top += self.rect.top
            element.absolute_rect.left += self.rect.left
            # print element.absolute_rect

        if self._disabled:
            t = pygame.Surface(self.size)
            t.set_alpha(100)
            self.texture.blit(t, (0, 0))
            UPDATE.append(self.rect)

        if update:
            UPDATE.append(self.rect)

    def move(self, d_x, d_y):
        self.position[0] += d_x
        self.position[1] += d_y
        self.titlebar.recalculate()
        self.rect.topleft = self.position
        self.surface.blit(self.texture, self.position)
        UPDATE.append(self.rect)

        self.titlebar.update_buttons()

        # update components

        for element in self.contents:
            element.absolute_rect = element.rect.copy()
            element.absolute_rect.top += self.rect.top
            element.absolute_rect.left += self.rect.left
            # print element.absolute_rect

    def blit(self, update=True):
        global UPDATE
        for element in self.contents:
            if element.changed:
                self.texture.blit(element.texture, element.rect)
                element.absolute_rect = element.rect.copy()
                element.absolute_rect.top += self.rect.top
                element.absolute_rect.left += self.rect.left
                # print element.absolute_rect
                element.changed = False
                if update:
                    UPDATE.append(element.absolute_rect)
            else:
                if update:
                    UPDATE.append(element.absolute_rect)

        if self.titlebar.changed:
            self.titlebar.blit()
            self.titlebar.changed = False

        self.surface.blit(self.texture, self.position)  # TODO Think about this line (performance)

    def click(self, pos):
        if not self._disabled:
            # print pos
            click_pos = [pos[0] - self.position[0], pos[1] - self.position[1]]
            # print click_pos

            for element in self.contents:
                if element.clickable:
                    if element.rect.collidepoint(click_pos):
                        element.click()

    def resize(self, d_x=0, d_y=0, change_pos=False):
        if change_pos:
            if d_x != 0:
                self.position[0] += d_x
                self.size[0] -= d_x

        else:
            if d_x != 0:
                # self.position[0] -= d_x
                self.size[0] += d_x

        if d_y != 0:
            self.size[1] += d_y

        if self.minimal_size[0] > self.size[0] + d_x:
            self.size[0] = self.minimal_size[0]
            self.size[0] += 1

        if self.minimal_size[1] > self.size[1] + d_y:
            self.size[1] = self.minimal_size[1]
            self.size[1] += 1

        self.rect.topleft = self.position
        self.rect.size = self.size
        self.texture = pygame.Surface(self.size)
        self.titlebar.texture = pygame.Surface(self.titlebar.size, pygame.SRCALPHA, 32)
        self.titlebar.size[0] = self.size[0]
        self.reblit()
        self.titlebar.reinit()
        self.titlebar.recalculate()
        UPDATE.append(self.rect)

        self.titlebar.update_buttons()

    def close(self, *_):
        self.closed = True
        return True


class TitleBar:
    def __init__(self, window, title):
        self.window = window
        self.title = title
        self.original_title = title
        self.titlefont = None
        self.position = [0, 0]
        self.size = [0, 0]
        self.height = _titlebar_components["middle"].get_rect().height
        self.rect = pygame.Rect((self.position[0], self.position[1], 0, 0))
        self.recalculate()
        self.texture = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.reinit()
        self.changed = True
        self.buttons = [TitleBarButton(self, "close")]

    def reinit(self):
        self.changed = True
        self.texture.blit(_titlebar_components["left_end"], (0, 0))
        widths = [_titlebar_components["left_end"].get_rect().width, _titlebar_components["right_end"].get_rect().width,
                  _titlebar_components["middle"].get_rect().width]
        for i in range(widths[0], self.window.size[0] - widths[1], widths[2]):
            self.texture.blit(_titlebar_components["middle"], (i * widths[2], 0))
        self.texture.blit(_titlebar_components["right_end"], (self.window.size[0] - widths[1], 0))

        self.title = self.original_title

        if len(self.title) * 8 > self.size[0]:
            self.title = self.title[:self.size[0] / 8 - 8] + "..."

        self.titlefont = _titlefont.render(self.title, True, (255, 255, 255))

        titlefontrect = self.titlefont.get_rect()
        titlefontrect.center = (self.rect.width / 2, self.rect.height / 2)

        self.texture.blit(self.titlefont, titlefontrect)

        self.buttons = []

        if self.window.closeable:
            self.buttons.append(TitleBarButton(self, "close"))

        for idx, button in enumerate(self.buttons):
            button.render(idx)

    def recalculate(self):
        self.changed = True
        self.position = [self.window.position[0],
                         self.window.position[1] - _titlebar_components["middle"].get_rect().height]
        self.size = self.window.size[:]
        self.size[1] = self.height
        self.rect.topleft = self.position
        self.rect.size = self.size

    def blit(self, update=True):
        if not self.window.borderless:
            GLOBAL_SURFACE.blit(self.texture, self.position)
            if update:
                self._update()

    def _update(self):
        global UPDATE
        UPDATE.append(self.rect)

    def update_buttons(self):
        for idx, button in enumerate(self.buttons):
            button.update(idx)


class TitleBarButton:
    def __init__(self, titlebar, button):
        self.texture = pygame.Surface((30, 30))
        self.action = object()
        self.titlebar = titlebar
        self.rect = self.texture.get_rect()
        self.abs_rect = None
        if button == "close":
            self.texture = _titlebar_components["closebutton"]
            self.action = titlebar.window.close

    def render(self, idx):
        self.update(idx)
        self.titlebar.texture.blit(self.texture, self.rect)

    def click(self):
        self.action()

    def update(self, idx):
        self.rect.topleft = (self.titlebar.size[0] - self.rect.size[0] * (idx + 1), 0)
        self.abs_rect = self.rect.copy()
        self.abs_rect.topleft = [self.abs_rect.topleft[0] + self.titlebar.position[0],
                                 self.abs_rect.topleft[1] + self.titlebar.position[1]]


def demo_init_windows(screen, wm, im):
    from text import Text
    from button import Button
    from textField import TextField

    window = Window(screen, (300, 300), "Test")

    window.contents.append(Text(0, 0, "Hi", (0, 0, 0)))

    window.contents.append(Button(0, 200, "Close", window.close))

    window.contents.append(TextField(im, 0, 150, "Hallo"))

    window.minimal_size = [100, 250]

    # w1 = window

    wm.register_window(window)

    window = Window(screen, (300, 300), "Very long title, too long for this small window", None, (200, 200))
    window.closeable = False
    window.resizeable = False
    window.borderless = True
    window.titlebar.reinit()

    window.contents.append(Button(0, 200, "Close", window.close))

    wm.register_window(window)


def demo_btn_onclick(button):
    button.move(8, 15)


def demo():
    global GLOBAL_SURFACE
    global UPDATE

    from gui.text import Text
    from gui.button import Button

    sys.path.insert(0, os.path.abspath("./gui"))

    screen = pygame.display.set_mode((1200, 800))

    im = InputManager()
    wm = WindowManager(im)
    ddm = DragDropManager(wm)

    bg = pygame.image.load("%s/bg.png" % _ASSETPATH)
    bg = bg.convert()

    GLOBAL_SURFACE = screen

    demo_init_windows(screen, wm, im)

    win = Window(screen, (400, 400), "AGUGU")

    b = Button(0, 0, "Click!", demo_btn_onclick)
    win.contents.append(b)

    wm.register_window(win)

    screen.blit(bg, (0, 0))

    wm.reblit_all_windows()

    pygame.display.update(UPDATE)
    UPDATE = [screen.get_rect()]

    # window.reblit()

    while 1:
        # window.blit()
        screen.blit(bg, (0, 0))
        ddm.loop()
        # wm.reblit_all_windows()
        wm.loop()

        # screen.blit(w1.texture, (0, 0))

        # pygame.display.update(pygame.Rect(0, 0, 50, 50))

        # pygame.display.update(_UPDATE)

        # _UPDATE = []

        if not wm.windows:
            print("Reopening Windows")
            demo_init_windows(screen, wm, im)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                ddm.mouse_down()
                wm.click(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                ddm.mouse_up()
            if event.type == pygame.KEYDOWN:
                im.report_input(event.key, event.unicode)
            if event.type == pygame.KEYUP:
                im.report_release(event.key)


if __name__ == '__main__':
    demo()
