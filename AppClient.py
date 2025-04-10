
from PyQt5.QtWidgets import QApplication

from Gui.Widgets.Window import Window


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._gui = Window()

    @property
    def gui(self):
        return self._gui


app = App([])
