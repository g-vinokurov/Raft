
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


class RaftRequestVoteRequest:
    def __init__(self, term: int, candidateId: str, lastLogIndex: int, lastLogTerm: int):
        self.term = term
        self.candidateId = candidateId
        self.lastLogIndex = lastLogIndex
        self.lastLogTerm = lastLogTerm
    
    def to_protobuf(self):
        msg = protocol.RequestVoteRequest()
        msg.term = self.term
        msg.candidateId = self.candidateId
        msg.lastLogIndex = self.lastLogIndex
        msg.lastLogTerm = self.lastLogTerm
        return msg

    @classmethod
    def from_protobuf(cls, msg: protocol.RequestVoteRequest):
        term = msg.term
        candidateId = msg.candidateId
        lastLogIndex = msg.lastLogIndex
        lastLogTerm = msg.lastLogTerm
        return cls(term, candidateId, lastLogIndex, lastLogTerm)


class RaftRequestVoteResponse:
    def __init__(self, term: int, voteGranted: bool):
        self.term = term
        self.voteGranted = voteGranted
    
    def to_protobuf(self):
        msg = protocol.RequestVoteResponse()
        msg.term = self.term
        msg.voteGranted = self.voteGranted
        return msg

    @classmethod
    def from_protobuf(cls, msg: protocol.RequestVoteResponse):
        term = msg.term
        voteGranted = msg.voteGranted
        return cls(term, voteGranted)


class RaftLogEntry:
    def __init__(self, cmd: str, term: int):
        self._cmd = cmd
        self._term = term
    
    @property
    def cmd(self):
        return self._cmd
    
    @property
    def term(self):
        return self._term


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
        self.__votes = 0
        self.__log : list[RaftLogEntry] = []
        
        self.__commit_index : int = 0
        self.__last_applied : int = 0
        
        self.__next_index : dict[str, int] = {}
        self.__match_index : dict[str, int] = {}

        self.__heartbeat_timeout : int = 100
        self.__heartbeat_timer = QTimer()
        self.__heartbeat_timer.setSingleShot(True)
        self.__heartbeat_timer.timeout.connect(self.__heartbeat)
        
        self.__election_timeout : int = 500 + random.randint(0, 200)
        self.__election_timer = QTimer()
        self.__election_timer.setSingleShot(True)
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
    
    def __reset_election_timer(self):
        log.debug('__reset_election_timer: Reset')
        self.__election_timeout = 500 + random.randint(0, 200)
        self.__election_timer.start(self.__election_timeout)
    
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

    def __send_raft_message(self, ip: str, port: int, msg: protocol.Message):
        host = QHostAddress(ip)
        port = port
        datagram = QNetworkDatagram(msg.SerializeToString(), host, port)
        self.__main_socket.writeDatagram(datagram)
    
    def __process_request_vote(self, ip: str, port: int, msg: protocol.Message):
        request = RaftRequestVoteRequest.from_protobuf(msg.request_vote)
        
        response = RaftRequestVoteResponse(self.__current_term, False)
        
        if self.__state == RaftState.Leader:
            log.debug(f'__process_request_vote: I am Leader')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)

        # If RPC request or response contains term T > currentTerm: 
        # set currentTerm = T, convert to follower
        if request.term > self.__current_term:
            log.debug(f'__process_request_vote: Become Follower')
            self.__current_term = request.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
            self.__leader = None
            
            self.updated.emit()
        
        #  Reply false if term < currentTerm
        if request.term < self.__current_term:
            log.debug(f'__process_request_vote: Request term less than current term')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        # if already voted for self or another candidate
        if self.__voted_for is not None and self.__voted_for != request.candidateId:
            log.debug(f'__process_request_vote: Is already voted for another candidate')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        # if candidate’s log is not up-to-date
        if request.lastLogIndex < len(self.__log):
            log.debug(f'__process_request_vote: Request is not up-to-date')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        # if candidate’s log is not up-to-date
        if self.__log and request.lastLogTerm < self.__log[-1].term:
            log.debug(f'__process_request_vote: Request term < my last log item term')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        self.__voted_for = request.candidateId
        self.__reset_election_timer()
        
        response.voteGranted = True

        log.debug(f'__process_request_vote: Vote granted to {self.__voted_for}')
        
        self.updated.emit()
        
        msg = protocol.Message()
        msg.request_vote_response.CopyFrom(response.to_protobuf())
        return self.__send_raft_message(ip, port, msg)
    
    def __process_request_vote_response(self, ip: str, port: int, msg: protocol.Message):
        r = RaftRequestVoteResponse.from_protobuf(msg.request_vote_response)
        
        if r.term > self.__current_term:
            log.debug('__process_request_vote_response: My term is outdated')
            self.__current_term = r.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
            self.__leader = None
            
            self.updated.emit()
            return
        
        if r.term < self.__current_term:
            log.debug('__process_request_vote_response: New election is already started')
            return
        
        self.__votes += 1

        # If votes received from majority of servers: become leader
        if self.__votes > len(self.__others) / 2:
            log.debug('__process_request_vote_response: I try to become Leader')
            self.__state = RaftState.Leader
            self.__leader = self.__this
            # for each server,
            # index of the next log entry to send to that server
            self.__next_index = { node: len(self.__log) + 1 for node in self.__others }
            # for each server, 
            # index of highest log entry known to be replicated on server
            self.__match_index = { node: 0 for node in self.__others }
            self.__heartbeat()
        else:
            log.debug('__process_request_vote_response: I got too few votes, now I am Follower again')
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
            self.__leader = None
            self.__reset_election_timer()
        
        self.updated.emit()
    
    def __process_append_entries(self, ip: str, port: int, msg: protocol.Message):
        pass

    def __process_append_entries_response(self, ip: str, port: int, msg: protocol.Message):
        pass
    
    def __heartbeat(self):
        # Upon election: Send initial empty AppendEntries RPCs (heartbeat) to each server
        if not self.__state == RaftState.Leader:
            log.debug('__heartbeat: I am not Leader')
            return
        
        log.debug('__heartbeat: Send heartbeats')

        for server in self.__others:
            host, port = server.split(':')
            self.__append_entries(host, int(port), is_heartbeat=True)
        
        log.debug(f'__heartbeat: Heartbears are sent')
        
        # Repeat during idle periods to prevent election timeouts
        self.__heartbeat_timer.start(self.__heartbeat_timeout)
    
    def __election(self):
        # If node has become Leader and election timer callback was called,
        # new election will not be started
        if self.__state == RaftState.Leader:
            log.debug('__election: I am Leader')
            return
        
        log.debug('__election: Started')
        
        # On conversion to candidate, start election
        if self.__state == RaftState.Follower:
            log.debug('__election: I was Follower, now I am Candidate')
            self.__state = RaftState.Candidate
        
        # Increment current term
        self.__current_term += 1
        # Vote for self
        self.__voted_for = self.__this 
        self.__votes = 1
        
        self.__reset_election_timer()
        
        log.debug(f'__election: Term is {self.__current_term}')
        
        last_log_index = len(self.__log)
        last_log_term = self.__log[-1].term if self.__log else 0
        
        request = RaftRequestVoteRequest(
            self.__current_term, 
            self.__voted_for, 
            last_log_index,
            last_log_term
        )
        
        msg = protocol.Message()
        msg.request_vote.CopyFrom(request.to_protobuf())
        
        for server in self.__others:
            host, port = server.split(':')
            self.__send_raft_message(host, int(port), msg)
        
        log.debug(f'__election: Requets are sent')

        self.updated.emit()
    
    def __append_entries(self, ip: str, port: int, is_heartbeat: bool = False):
        pass
