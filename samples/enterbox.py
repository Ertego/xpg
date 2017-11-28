import sys
import os
import pygame

sys.path.insert(0, os.path.abspath("../"))

import xpg

from gui.button import Button
from gui.text import Text
from gui.textField import TextField

import dialog


cbox = None


def button_onclick(button):
    global cbox
    cbox = dialog.ConfirmationBox(wm, screen, "Name: %s" % tf.text, "Sure?")
    window.disable(im)


wm = xpg.WindowManager()
ddm = xpg.DragDropManager(wm)
im = xpg.InputManager()

screen = pygame.display.set_mode((1200, 800))
xpg.GLOBAL_SURFACE = screen

window = xpg.Window(screen, (300, 50), "Your Name:")

window.resizeable = False

tf = TextField(im, 0, 0, "", button_onclick)

b = Button(200, 5, "Submit", button_onclick)

window.contents.append(b)
window.contents.append(tf)

wm.register_window(window)

pygame.display.update(xpg.UPDATE)
xpg.UPDATE.append(screen.get_rect())

wm.reblit_all_windows()

while 1:
    screen.fill((0, 0, 0))
    ddm.loop()
    wm.loop()


    #wm.reblit_all_windows()

    if cbox is not None:
        if cbox.status == "y":
            print tf.text
            sys.exit()

        if cbox.status == "n":
            cbox = None
            window.enable()

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
