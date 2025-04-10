
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtCore import Qt

from Gui.Widgets.Screen import Screen
from Gui.Widgets.Client.GetFromStorage import GetFromStorage
from Gui.Widgets.Client.DeleteFromStorage import DeleteFromStorage
from Gui.Widgets.Client.PutToStorage import PutToStorage
from Gui.Widgets.Client.KeyValueArgs import KeyValueArgs
from Gui.Widgets.Client.ResponseText import ResponseText

from RestAPI.Client import HttpClient

from Gui.Themes import CurrentTheme as Theme

from Log import log
from AppClient import app


class ClientScreen(Screen):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        self.setObjectName('client-screen')

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f'''
            QWidget#client-screen {{
                background-color: {Theme.ClientScreenBackgroundColor};
                border: none;
                outline: none;
                padding: 0px;
            }}
        ''')

        self._client = HttpClient()
        self._client.response_received.connect(self._on_response_received)

        self._get = GetFromStorage('Get', self)
        self._put = PutToStorage('Put', self)
        self._delete = DeleteFromStorage('Delete', self)
        self._key_value = KeyValueArgs(self)

        self._get.clicked.connect(self._on_get_clicked)
        self._put.clicked.connect(self._on_put_clicked)
        self._delete.clicked.connect(self._on_delete_clicked)
        
        self._operations_layout = QHBoxLayout()
        self._operations_layout.setContentsMargins(0, 0, 0, 0)
        self._operations_layout.setSpacing(32)

        self._operations_layout.addWidget(self._key_value)
        self._operations_layout.addWidget(self._get)
        self._operations_layout.addWidget(self._put)
        self._operations_layout.addWidget(self._delete)

        self._response_text = ResponseText(self)

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(32, 32, 32, 32)
        self._layout.setSpacing(32)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._layout.addLayout(self._operations_layout)
        self._layout.addWidget(self._response_text)
        
        self.setLayout(self._layout)
        
        app.gui.setWindowTitle('Client')
    
    def _on_get_clicked(self):
        data = self._key_value.text()
        host, port, key = data.split(':')
        self._client.send(host, int(port), 'GET', '/get', str({'key': key}))

    def _on_put_clicked(self):
        data = self._key_value.text()
        host, port, key, val = data.split(':')
        self._client.send(host, int(port), 'PUT', '/put', str({'key': key, 'val': val}))

    def _on_delete_clicked(self):
        data = self._key_value.text()
        host, port, key = data.split(':')
        self._client.send(host, int(port), 'DELETE', '/delete', str({'key': key}))
    
    def _on_response_received(self, response: str):
        self._response_text.setText(response)
