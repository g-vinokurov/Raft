
from PyQt5.QtWidgets import QLineEdit

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme

from Log import log


class KeyValueArgs(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setStyleSheet(f'''
            color: {Theme.ClientKeyValueArgsColor};
            padding: 15px;
            border: 1px solid {Theme.ClientKeyValueArgsBorderColor};
        ''')
        self.setPlaceholderText('host:port:key[:value]')
        
        font = Font(Theme.ClientKeyValueArgsFont)
        font.setPointSize(Theme.ClientKeyValueArgsFontSize)
        font.setWeight(Theme.ClientKeyValueArgsFontWeight)
        self.setFont(font)
