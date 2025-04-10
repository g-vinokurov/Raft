
from PyQt5.QtWidgets import QPushButton

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme

from Log import log


class PutToStorage(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('client-put-to-storage')

        self.setStyleSheet(f'''
            color: {Theme.ClientPutToStorageColor};
            background: {Theme.ClientPutToStorageBackgroundColor};
            border: none;
            outline: none;
            padding: 16px;
        ''')
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        font = Font(Theme.ClientPutToStorageFont)
        font.setPointSize(Theme.ClientPutToStorageFontSize)
        font.setWeight(Theme.ClientPutToStorageFontWeight)
        self.setFont(font)
