
import os

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QFileDialog

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from Gui.Fonts import Font
from Gui.Themes import CurrentTheme as Theme

from Log import log
from App import app


class StartStopServer(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('dashboard-start-stop-server')

        self.setStyleSheet(f'''
            color: {Theme.DashboardStartStopServerColor};
            background: {Theme.DashboardStartStopServerBackgroundColor};
            border: none;
            outline: none;
            padding: 16px;
        ''')
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        font = Font(Theme.DashboardStartStopServerFont)
        font.setPointSize(Theme.DashboardStartStopServerFontSize)
        font.setWeight(Theme.DashboardStartStopServerFontWeight)
        self.setFont(font)
