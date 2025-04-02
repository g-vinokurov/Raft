
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QDesktopWidget

from Gui.Widgets.Navigator import Navigator


class Window(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        size_policy = QSizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Preferred)

        self._navigator = Navigator(self)
        self._navigator.setSizePolicy(size_policy)

        self.setCentralWidget(self._navigator)
        self.setSizePolicy(size_policy)

        display_geometry = QDesktopWidget().availableGeometry()
        display_w = display_geometry.width()
        display_h = display_geometry.height()

        window_w = display_w * 3 // 4
        window_h = display_h * 3 // 4
        self.resize(window_w, window_h)
    
    @property
    def navigator(self):
        return self._navigator
