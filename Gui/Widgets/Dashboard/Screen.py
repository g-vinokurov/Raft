
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtCore import Qt

from Gui.Widgets.Screen import Screen

from Gui.Themes import CurrentTheme as Theme

from Log import log
from App import app


class DashboardScreen(Screen):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('dashboard-screen')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#dashboard-screen {{
                background-color: {Theme.DashboardScreenBackgroundColor};
                border: none;
                outline: none;
                padding: 0px;
            }}
        ''')
        
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.setStretch(1, 1)
        
        self.setLayout(self._layout)

        app.gui.setWindowTitle('Dashboard')
