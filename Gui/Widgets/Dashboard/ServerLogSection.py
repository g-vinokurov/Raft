
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
        
        if app.server.is_configured:
            for entry in app.server.log:
                item = {}
                item['cmd'] = entry.cmd
                item['term'] = entry.term
                table_rows.append(item)
        
        self._log.setRowCount(len(table_rows))
        self._log.setColumnCount(len(table_cols))
        self._log.setHorizontalHeaderLabels(table_cols)

        for i, item in enumerate(table_rows, 1):
            item_0 = QTableWidgetItem(str(i))
            item_1 = QTableWidgetItem(item['cmd'])
            item_2 = QTableWidgetItem(item['term'])

            item_0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self._log.setItem(i - 1, 0, item_0)
            self._log.setItem(i - 1, 1, item_1)
            self._log.setItem(i - 1, 2, item_2)

        self._log.setVisible(False)
        self._log.resizeColumnsToContents()
        self._log.setVisible(True)
