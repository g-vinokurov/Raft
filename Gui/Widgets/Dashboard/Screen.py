
from PyQt5.QtWidgets import QHBoxLayout

from PyQt5.QtCore import Qt

from Gui.Widgets.Screen import Screen
from Gui.Widgets.Dashboard.ServerConfigSection import ServerConfigSection
from Gui.Widgets.Dashboard.ServerLogSection import ServerLogSection
from Gui.Widgets.Dashboard.ServerStateSection import ServerStateSection

from Gui.Themes import CurrentTheme as Theme

from Log import log
from App import app


class DashboardScreen(Screen):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('dashboard-screen')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#dashboard-screen {{
                background-color: {Theme.DashboardScreenBackgroundColor};
                border: none;
                outline: none;
                padding: 0px;
            }}
        ''')

        self._server_config_section = ServerConfigSection(self)
        self._server_state_section = ServerStateSection(self)
        self._server_log_section = ServerLogSection(self)
        
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(32, 32, 32, 32)
        self._layout.setSpacing(32)
        
        self._layout.addWidget(self._server_config_section)
        self._layout.addWidget(self._server_state_section)
        self._layout.addWidget(self._server_log_section)
        
        self.setLayout(self._layout)
        
        app.gui.setWindowTitle('Dashboard')
        app.server.updated.connect(self._on_server_updated)
    
    def _on_server_updated(self):
        self._server_config_section.updateUI()
        self._server_state_section.updateUI()
        self._server_log_section.updateUI()
