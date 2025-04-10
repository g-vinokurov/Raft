
from PyQt5.QtWidgets import QHBoxLayout

from PyQt5.QtCore import Qt

from Gui.Widgets.Screen import Screen

from Gui.Themes import CurrentTheme as Theme

from Log import log
from AppClient import app


class ClientScreen(Screen):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('client-screen')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#client-screen {{
                background-color: {Theme.ClientScreenBackgroundColor};
                border: none;
                outline: none;
                padding: 0px;
            }}
        ''')
        
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(32, 32, 32, 32)
        self._layout.setSpacing(32)
        
        self.setLayout(self._layout)
        
        app.gui.setWindowTitle('Dashboard')
