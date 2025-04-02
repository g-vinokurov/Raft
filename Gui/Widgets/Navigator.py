
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QGridLayout

from Gui.Widgets.Screen import Screen


class Navigator(QWidget):
    _mapper = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._screens = {}
        
        self.initUI()

    def initUI(self):
        self._current_screen = Screen(self)

        self._layout = QGridLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._current_screen)

        self.setLayout(self._layout)
    
    @property
    def screen(self):
        return self._current_screen

    def load(self, tag: str, *args, **kwargs):
        self._screens[tag] = self._mapper.get(tag, Screen)(self, *args, **kwargs)
        self.update(tag, *args, **kwargs)

    def update(self, tag: str, *args, **kwargs):
        screen : Screen = self._screens.get(tag, Screen(self))
        screen.updateUI(*args, **kwargs)

    def goto(self, tag: str, *args, **kwargs):
        if tag not in self._screens:
            self.load(tag, *args, **kwargs)

        self._layout.removeWidget(self._current_screen)
        self._current_screen.hide()
        self._current_screen : Screen = self._screens[tag]
        self._current_screen.show()
        self._layout.addWidget(self._current_screen)

    @classmethod
    def register(cls, tag: str, screen_cls: type[Screen]):
        if tag in cls._mapper:
            return
        cls._mapper[tag] = screen_cls
