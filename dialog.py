import xpg

from gui.text import Text
from gui.button import Button


class ConfirmationBox:
    def __init__(self, wm, surface, text, title=""):
        window = xpg.Window(surface, (200, 100), title, None, (400, 400))
        window.contents.append(Text(0, 0, text, (0, 0, 0)))
        window.contents.append(Button(0, 50, "Cancel", self.decline))
        window.contents.append(Button(100, 50, "Ok", self.confirm))

        window.closeable = False
        window.titlebar.reinit()

        wm.register_window(window)

        self.window = window

        self.status = "pending"

    def confirm(self, _):
        self.status = "y"
        self.window.close()

    def decline(self, _):
        self.status = "n"
        self.window.close()
