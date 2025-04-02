
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem

from PyQt5.QtCore import Qt

from Gui.Widgets.Table import Table

from Gui.Themes import CurrentTheme as Theme

from Log import log
from App import app


class ServerLogSection(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('dashboard-server-log-section')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#dashboard-server-log-section {{
                background-color: {Theme.DashboardServerLogSectionBackgroundColor};
                outline: none;
                border: none;
                padding: 0px;
            }}
        ''')

        self._log = Table()

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._log)

        self.setLayout(self._layout)
        self.updateUI()
    
    def updateUI(self):
        self._log.clear()

        table_cols = ['#', 'Cmd', 'Term']
        table_rows = []
        
        self._log.setRowCount(len(table_rows))
        self._log.setColumnCount(len(table_cols))
        self._log.setHorizontalHeaderLabels(table_cols)

        self._log.setVisible(False)
        self._log.resizeColumnsToContents()
        self._log.setVisible(True)
