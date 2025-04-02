
import sys
import enum
import random

from google.protobuf.message import Message as ProtobufMessage

from PyQt5.QtNetwork import QUdpSocket
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtNetwork import QNetworkDatagram

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

import Proto.raft_pb2 as protocol

from Log import log


class RaftLogEntry:
    def __init__(self):
        pass


class RaftState(enum.Enum):
    Follower  = 0
    Candidate = 1
    Leader    = 2


class RaftServer(QObject):
    updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.__is_configured = False
        self.__is_active = False
    
    def config(self, this: str, others: list[str] = []):
        if self.__is_active:
            log.debug('Could not reconfigure server while it is active. Stop it before.')
            return
        
        self.__state : RaftState = RaftState.Follower
        self.__this : str = this
        self.__others : list[str] = others[::]
        
        self.__leader: str | None = None
        
        self.__current_term : int = 0
        self.__voted_for : str | None = None
        self.__log : list[RaftLogEntry] = []
        
        self.__commit_index : int = 0
        self.__last_applied : int = 0
        
        self.__next_index : dict[str, int] = {}
        self.__match_index : dict[str, int] = {}

        self.__heartbeat_timeout : int = 100
        self.__heartbeat_timer = QTimer()
        self.__heartbeat_timer.timeout.connect(self.__heartbeat)
        
        self.__election_timeout : int = 500 + random.randint(0, 200)
        self.__election_timer = QTimer()
        self.__election_timer.timeout.connect(self.__election)

        host, port = self.__this.split(':')
        self.__host : str = host
        self.__port : int = int(port)
        self.__main_socket : QUdpSocket | None = None
        
        self.__is_configured = True

        self.updated.emit()
    
    def start(self):
        if not self.__is_configured:
            log.debug('Could not start non-configured server. Configure it before.')
            return
        
        if self.__is_active:
            self.stop()
        
        self.__main_socket = QUdpSocket()
        self.__main_socket.bind(QHostAddress(self.__host), self.__port)
        self.__main_socket.readyRead.connect(self.__on_main_socket_ready_read)

        self.__election_timer.start(self.__election_timeout)

        self.__is_active = True

        self.updated.emit()
    
    def stop(self):
        if not self.__is_active:
            log.debug('Server already is stopped.')
            return
        
        self.__is_active = False

        self.__heartbeat_timer.stop()
        self.__election_timer.stop()

        if self.__main_socket is not None:
            self.__main_socket.close()
        self.__main_socket = None

        self.updated.emit()
    
    def __on_main_socket_ready_read(self):
        while self.__main_socket.hasPendingDatagrams():
            datagram = self.__main_socket.receiveDatagram()
            ip = datagram.senderAddress().toString()
            port = int(datagram.senderPort())
            data = bytes(datagram.data())
            self.__process_main_socket_data(ip, port, data)
    
    def __process_main_socket_data(self, ip: str, port: int, data: bytes):
        msg : ProtobufMessage = protocol.Message()
        msg.ParseFromString(data)

        if msg.HasField('request_vote'):
            return self.__process_request_vote(ip, port, msg)
        if msg.HasField('request_vote_response'):
            return self.__process_request_vote_response(ip, port, msg)
        if msg.HasField('append_entries'):
            return self.__process_append_entries(ip, port, msg)
        if msg.HasField('append_entries_response'):
            return self.__process_append_entries_response(ip, port, msg)
        return
    
    def __process_request_vote(self, ip: str, port: int, msg: protocol.Message):
        pass

    def __process_request_vote_response(self, ip: str, port: int, msg: protocol.Message):
        pass

    def __process_append_entries(self, ip: str, port: int, msg: protocol.Message):
        pass

    def __process_append_entries_response(self, ip: str, port: int, msg: protocol.Message):
        pass
    
    def __heartbeat(self):
        log.debug('Heartbeat')
    
    def __election(self):
        log.debug('Election')
