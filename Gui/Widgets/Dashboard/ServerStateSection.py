
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem

from PyQt5.QtCore import Qt

from Gui.Widgets.Table import Table

from Gui.Themes import CurrentTheme as Theme

from Log import log
from App import app


class ServerStateSection(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('dashboard-server-state-section')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#dashboard-server-state-section {{
                background-color: {Theme.DashboardServerStateSectionBackgroundColor};
                outline: none;
                border-left: 1px solid {Theme.DashboardServerStateSectionBorderColor};
                border-right: 1px solid {Theme.DashboardServerStateSectionBorderColor};
                padding: 0px;
            }}
        ''')

        self._vars = Table()

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._vars)

        self.setLayout(self._layout)
        self.updateUI()
    
    def updateUI(self):
        self._vars.clear()

        table_cols = ['#', 'Var', 'Value']
        table_rows = []
        
        self._vars.setRowCount(len(table_rows))
        self._vars.setColumnCount(len(table_cols))
        self._vars.setHorizontalHeaderLabels(table_cols)

        self._vars.setVisible(False)
        self._vars.resizeColumnsToContents()
        self._vars.setVisible(True)
