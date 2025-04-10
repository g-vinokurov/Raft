
from PyQt5.QtNetwork import QTcpSocket

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QByteArray


class HttpClient(QObject):
    connected = pyqtSignal()
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.__socket = QTcpSocket()
        self.__socket.connected.connect(self._on_connected)
        self.__socket.readyRead.connect(self._on_response_received)
        self.__socket.errorOccurred.connect(self._on_error)
    
    def send(self, host: str, port: int, method: str, path: str, data: str):
        self.__socket.connectToHost(host, port)
        
        request = QByteArray()
        request.append(f'{method} {path} HTTP/1.1\n')
        request.append('Content-Type: application/json; charset=utf-8\n')
        request.append(f'Content-Length: {len(data)}\n')
        request.append('Connection: close\n')
        request.append('\n')
        request.append(data)
        request.append('\n\n')

        self.__socket.write(request)
    
    def _on_connected(self):
        self.connected.emit()
    
    def _on_response_received(self):
        data = self.__socket.readAll().data().decode('utf-8', errors='ignore')
        self.response_received.emit(data)

    def _on_error(self, socket_error):
        self.error_occurred.emit(f'Socket error: {self.__socket.errorString()}')
