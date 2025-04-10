
from PyQt5.QtWidgets import QPushButton

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme

from Log import log


class GetFromStorage(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('client-get-from-storage')

        self.setStyleSheet(f'''
            color: {Theme.ClientGetFromStorageColor};
            background: {Theme.ClientGetFromStorageBackgroundColor};
            border: none;
            outline: none;
            padding: 16px;
        ''')
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        font = Font(Theme.ClientGetFromStorageFont)
        font.setPointSize(Theme.ClientGetFromStorageFontSize)
        font.setWeight(Theme.ClientGetFromStorageFontWeight)
        self.setFont(font)
