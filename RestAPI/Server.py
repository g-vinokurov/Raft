
from PyQt5.QtNetwork import QTcpServer
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QByteArray

from Log import log


class HttpServer(QObject):
    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__is_configured = False
        self.__is_active = False
        self.__handler = lambda request, client : 200, 'OK', ''
    
    def config(self, host: str, port: int):
        if self.__is_active:
            log.debug('HCould not reconfigure server while it is active')
            return
        
        self.__host : str = host
        self.__port : int = port
        
        self.__is_configured = True
        
        self.updated.emit()

    def start(self):
        if not self.__is_configured:
            log.debug('Could not start non-configured server')
            return 
        
        self.__server = QTcpServer()
        self.__server.newConnection.connect(self.__handle_new_connection)
        self.__clients : list[QTcpSocket] = []

        if not self.__server.listen(QHostAddress(self.__host), self.__port):
            log.debug(f'Could not start server: {self.__server.errorString()}')
            return
        
        log.info(f'Rest API Server started on host {self.__host} on port {self.__port}')

        self.__is_active = True

        self.updated.emit()
    
    def stop(self):
        self.__server.close()
        for client in self.__clients:
            client.disconnectFromHost()
        
        self.__is_active = False
        
        log.info('RestAPI Server stopped')

        self.updated.emit()
    
    def set_handler(self, handler):
        self.__handler = handler

    def __handle_new_connection(self):
        client = self.__server.nextPendingConnection()
        if not client:
            return
        
        self.__clients.append(client)
        client.readyRead.connect(lambda: self.__read_client_data(client))
        client.disconnected.connect(lambda: self.__client_disconnected(client))

    def __read_client_data(self, client : QTcpSocket):
        data = client.readAll().data()
        
        if data:
            request = data.decode('utf-8')
            
            if request.startswith('GET'):
                self.__handle_request(client, request)
            else:
                self.__send_response(client, 501, 'Not Implemented', 'Unsupported method')

    def __client_disconnected(self, client: QTcpSocket):
        if client in self.__clients:
            self.__clients.remove(client)
        client.deleteLater()

    def __handle_request(self, client: QTcpSocket, request : str):
        path = request.split(' ')[1]
        
        # if path == '/':
        #     response_content = '<h1>Welcome to PyQt5 HTTP Server</h1><p>This is a basic HTTP server implementation.</p>'
        #     self.__send_response(client, 200, 'OK', response_content)
        # elif path == '/hello':
        #     response_content = '<h1>Hello World!</h1>'
        #     self.__send_response(client, 200, 'OK', response_content)
        # else:
        #     self.__send_response(client, 404, 'Not Found', '<h1>404 Not Found</h1>')
        status, status_text, response = self.__handler(request, client)
        
        self.__send_response(client, status, status_text, response)

    def __send_response(self, client : QTcpSocket, status_code : int, status_text : str, content : str):
        response = QByteArray()
        response.append(f'HTTP/1.1 {status_code} {status_text}\n')
        response.append('Content-Type: text/html; charset=utf-8\n')
        response.append(f'Content-Length: {len(content)}\n')
        response.append('Connection: close\n')
        response.append('\n')
        response.append(content)
        
        client.write(response)
        client.disconnectFromHost()
    
    @property
    def is_configured(self):
        return self.__is_configured
    
    @property
    def is_active(self):
        return self.__is_active
    
    @property
    def host(self):
        return self.__host
    
    @property
    def port(self):
        return self.__port
