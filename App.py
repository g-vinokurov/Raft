
from PyQt5.QtWidgets import QApplication

from Gui.Widgets.Window import Window
from State.State import State


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._state = State()
        self._gui = Window()
    
    @property
    def state(self):
        return self._state
    
    @property
    def gui(self):
        return self._gui


app = App([])
