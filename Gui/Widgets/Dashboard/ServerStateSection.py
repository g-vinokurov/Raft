
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
        
        if app.server.is_configured:
            table_rows = [
                ['is_configured', str(app.server.is_configured)],
                ['is_active', str(app.server.is_active)],
                ['state', str(app.server.state.name)],
                ['this', str(app.server.this)],
                ['leader', str(app.server.leader)],
                ['current_term', str(app.server.current_term)],
                ['voted_for', str(app.server.voted_for)],
                ['votes', str(app.server.votes)],
                ['commit_index', str(app.server.commit_index)],
                ['last_applied', str(app.server.last_applied)],
                ['next_index', str(list(app.server.next_index.values()))],
                ['match_index', str(list(app.server.match_index.values()))],
                ['heartbeat_timeout', str(app.server.heartbeat_timeout)],
                ['election_timeout', str(app.server.election_timeout)]
            ]
        else:
            table_rows = []
        
        self._vars.setRowCount(len(table_rows))
        self._vars.setColumnCount(len(table_cols))
        self._vars.setHorizontalHeaderLabels(table_cols)

        for i, item in enumerate(table_rows, 1):
            item_0 = QTableWidgetItem(str(i))
            item_1 = QTableWidgetItem(item[0])
            item_2 = QTableWidgetItem(item[1])

            item_0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self._vars.setItem(i - 1, 0, item_0)
            self._vars.setItem(i - 1, 1, item_1)
            self._vars.setItem(i - 1, 2, item_2)

        self._vars.setVisible(False)
        self._vars.resizeColumnsToContents()
        self._vars.setVisible(True)
