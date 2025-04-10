
from PyQt5.QtWidgets import QPushButton

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme

from Log import log


class DeleteFromStorage(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('client-delete-from-storage')

        self.setStyleSheet(f'''
            color: {Theme.ClientDeleteFromStorageColor};
            background: {Theme.ClientDeleteFromStorageBackgroundColor};
            border: none;
            outline: none;
            padding: 16px;
        ''')
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        font = Font(Theme.ClientDeleteFromStorageFont)
        font.setPointSize(Theme.ClientDeleteFromStorageFontSize)
        font.setWeight(Theme.ClientDeleteFromStorageFontWeight)
        self.setFont(font)
