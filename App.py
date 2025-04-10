
from PyQt5.QtWidgets import QApplication

from Gui.Widgets.Window import Window
from State.State import State
from Raft.Server import RaftServer
from RestAPI.Server import HttpServer


class App(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._state = State()
        self._raft_server = RaftServer(self._state)
        self._rest_api = HttpServer()
        self._rest_api.set_handler(self._raft_server.client_request_handler)
        self._gui = Window()
    
    @property
    def state(self):
        return self._state
    
    @property
    def gui(self):
        return self._gui
    
    @property
    def server(self):
        return self._raft_server
    
    @property
    def rest_api(self):
        return self._rest_api


app = App([])
