
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTableWidgetItem

from PyQt5.QtCore import Qt

from Gui.Widgets.Table import Table
from Gui.Widgets.Dashboard.StartStopServer import StartStopServer

from Gui.Themes import CurrentTheme as Theme

from Config import RAFT_SERVERS

from Log import log
from App import app


class ServerConfigSection(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('dashboard-server-config-section')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#dashboard-server-config-section {{
                background-color: {Theme.DashboardServerConfigSectionBackgroundColor};
                outline: none;
                border: none;
                padding: 0px;
            }}
        ''')

        self._servers = Table()
        self._servers.cellDoubleClicked.connect(self._on_servers_double_clicked)

        self._start_stop_server = StartStopServer(self)
        self._start_stop_server.clicked.connect(self._on_start_stop_server_clicked)
        self._start_stop_server.setText('Non-configured')
        self._start_stop_server.setDisabled(True)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._layout.addWidget(self._servers)
        self._layout.addWidget(self._start_stop_server, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(self._layout)
        self.updateUI()
    
    def updateUI(self):
        self._servers.clear()

        table_cols = ['#', 'Host', 'Port']
        table_rows = []
        for server in RAFT_SERVERS:
            host, port = server.split(':')
            item = {}
            item['host'] = host
            item['port'] = port
            table_rows.append(item)
        
        self._servers.setRowCount(len(table_rows))
        self._servers.setColumnCount(len(table_cols))
        self._servers.setHorizontalHeaderLabels(table_cols)

        for i, item in enumerate(table_rows, 1):
            item_0 = QTableWidgetItem(str(i))
            item_1 = QTableWidgetItem(item['host'])
            item_2 = QTableWidgetItem(item['port'])

            item_0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_1.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_2.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self._servers.setItem(i - 1, 0, item_0)
            self._servers.setItem(i - 1, 1, item_1)
            self._servers.setItem(i - 1, 2, item_2)
        self._servers.setVisible(False)
        self._servers.resizeColumnsToContents()
        self._servers.setVisible(True)
    
    def _on_servers_double_clicked(self, row, col):
        host = self._servers.item(row, 1).text()
        port = self._servers.item(row, 2).text()

        this = f'{host}:{port}'
        others = [x for x in RAFT_SERVERS if x != this]
        app.server.config(this, others)

        self._start_stop_server.setDisabled(False)
        self._start_stop_server.setText('Start')
    
    def _on_start_stop_server_clicked(self):
        if app.server.is_active:
            app.server.stop()
            self._start_stop_server.setText('Start')
        else:
            app.server.start()
            self._start_stop_server.setText('Stop')
