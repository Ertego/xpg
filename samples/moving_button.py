import sys
import os
import pygame

sys.path.insert(0, os.path.abspath("../"))

import xpg

from gui.button import Button


def button_onclick(button):
    button.move(10, 0)


wm = xpg.WindowManager()
ddm = xpg.DragDropManager(wm)

screen = pygame.display.set_mode((1200, 800))
xpg.GLOBAL_SURFACE = screen

window = xpg.Window(screen, (300, 300), "Moving Button")

b = Button(0, 0, "MOVE!", button_onclick)

window.contents.append(b)

wm.register_window(window)

pygame.display.update(xpg.UPDATE)
xpg.UPDATE.append(screen.get_rect())

while 1:
    wm.loop()
    ddm.loop()
    screen.fill((0, 0, 0))

    b.move(0, 0.1)

    if b.position[1] > window.size[1]:
        b.move(0, -window.size[1])

    window.reblit()

    if not window in wm.windows:
        window = xpg.Window(screen, (300, 300), "Moving Button")

        b = Button(0, 0, "MOVE!", button_onclick)

        window.contents.append(b)

        wm.register_window(window)

        print "reopening window..."

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            ddm.mouse_down()
            wm.click(event.pos)
        if event.type == pygame.MOUSEBUTTONUP:
            ddm.mouse_up()
