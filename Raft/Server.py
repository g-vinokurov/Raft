
import sys
import enum
import random
import json

from google.protobuf.message import Message as ProtobufMessage

from PyQt5.QtNetwork import QUdpSocket
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtNetwork import QNetworkDatagram

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

from State.State import State as FSM

import Proto.raft_pb2 as protocol

from Config import RAFT_SERVERS
from Config import REST_API_SERVERS

from Log import log


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
    
    def to_protobuf(self):
        msg = protocol.LogEntry()
        msg.term = self.term
        msg.cmd = self.cmd
        return msg

    @classmethod
    def from_protobuf(cls, msg: protocol.LogEntry):
        term = msg.term
        cmd = msg.cmd
        return cls(cmd, term)
    
    def __str__(self):
        return json.dumps({'cmd': self._cmd, 'term': self._term})


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


class RaftAppendEntriesRequest:
    def __init__(self, term: int, leaderId: str, prevLogIndex: int, prevLogTerm: int, entries: list[RaftLogEntry], leaderCommit: int):
        self.term = term
        self.leaderId = leaderId
        self.prevLogIndex = prevLogIndex
        self.prevLogTerm = prevLogTerm
        self.entries = entries[::]
        self.leaderCommit = leaderCommit
    
    def to_protobuf(self):
        msg = protocol.AppendEntriesRequest()
        msg.term = self.term
        msg.leaderId = self.leaderId
        msg.prevLogIndex = self.prevLogIndex
        msg.prevLogTerm = self.prevLogTerm
        msg.leaderCommit = self.leaderCommit
        msg.entries.extend([entry.to_protobuf() for entry in self.entries])
        return msg

    @classmethod
    def from_protobuf(cls, msg: protocol.AppendEntriesRequest):
        term = msg.term
        leaderId = msg.leaderId
        prevLogIndex = msg.prevLogIndex
        prevLogTerm = msg.prevLogTerm
        leaderCommit = msg.leaderCommit
        entries = [RaftLogEntry.from_protobuf(x) for x in msg.entries]
        return cls(term, leaderId, prevLogIndex, prevLogTerm, entries, leaderCommit)


class RaftAppendEntriesResponse:
    def __init__(self, term: int, success: bool, lastLogIndex: int):
        self.term = term
        self.success = success
        self.lastLogIndex = lastLogIndex
    
    def to_protobuf(self):
        msg = protocol.AppendEntriesResponse()
        msg.term = self.term
        msg.success = self.success
        msg.lastLogIndex = self.lastLogIndex
        return msg

    @classmethod
    def from_protobuf(cls, msg: protocol.AppendEntriesResponse):
        term = msg.term
        success = msg.success
        lastLogIndex = msg.lastLogIndex
        return cls(term, success, lastLogIndex)


class RaftState(enum.Enum):
    Follower  = 0
    Candidate = 1
    Leader    = 2


class RaftServer(QObject):
    updated = pyqtSignal()

    def __init__(self, fsm: FSM):
        super().__init__()
        
        self.__is_configured = False
        self.__is_active = False
        self.__fsm = fsm
    
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
            log.debug(f'{self.__this}: Server already is stopped.')
            return
        
        self.__state : RaftState = RaftState.Follower
        self.__leader: str | None = None
        
        self.__current_term : int = 0
        self.__voted_for : str | None = None
        self.__votes = 0
        
        self.__commit_index : int = 0
        self.__last_applied : int = 0
        
        self.__next_index : dict[str, int] = {}
        self.__match_index : dict[str, int] = {}
        
        self.__is_active = False

        self.__heartbeat_timer.stop()
        self.__election_timer.stop()

        if self.__main_socket is not None:
            self.__main_socket.close()
        self.__main_socket = None

        self.updated.emit()
    
    def client_request_handler(self, request: str, client: QTcpSocket):
        log.debug(f'\n{request}')

        method = request.split()[0]
        path = request.split()[1]
        
        if not self.__is_configured:
            msg = {'msg': 'Raft Server is not configured'}
            msg = json.dumps(msg)
            return 500, 'Internal Server Error', msg
        
        if not self.__is_active:
            msg = {'msg': 'Raft Server is not active'}
            msg = json.dumps(msg)
            return 500, 'Internal Server Error', msg
        
        if self.__state != RaftState.Leader:
            if self.__leader is None:
                msg = {'msg': 'Leader not found'}
                msg = json.dumps(msg)
                return 404, 'Not Found', msg
            
            leader_index = RAFT_SERVERS.index(self.__leader)
            leader_api = REST_API_SERVERS[leader_index]

            msg = {'msg': f'Send request to Leader at {leader_api}'}
            msg = json.dumps(msg)
            return 302, 'Redirect', msg
    
        if method == 'GET' and path == '/get':
            r = request.split('\n\n')
            if len(r) < 2:
                msg = {'msg': 'Request body is empty'}
                msg = json.dumps(msg)
                return 400, 'Bad request', msg
            
            r = r[1]
            r = json.loads(r)
            if not isinstance(r, dict):
                msg = {'msg': 'Request body must contain onject'}
                msg = json.dumps(msg)
                return 400, 'Bad request', msg
            
            key = r.get('key', 'no-key')
            val = self.__fsm.get(key)
            if val is None:
                msg = {'msg': f'Key {key} not found'}
                msg = json.dumps(msg)
                return 404, 'Not found', msg
            
            response = {'value': val}
            response = json.dumps(response)
            return 200, 'Ok', response
        
        if method == 'PUT' and path == '/put':
            r = request.split('\n\n')
            if len(r) < 2:
                msg = {'msg': 'Request body is empty'}
                msg = json.dumps(msg)
                return 400, 'Bad request', msg
            
            r = r[1]
            r = json.loads(r)
            cmd = {'action': 'put', 'args': r}
            cmd = json.dumps(cmd)
            self.__add_cmd_to_log(cmd)
            return 200, 'Ok', cmd
        
        if method == 'DELETE' and path == '/delete':
            r = request.split('\n\n')
            if len(r) < 2:
                msg = {'msg': 'Request body is empty'}
                msg = json.dumps(msg)
                return 400, 'Bad request', msg
            
            r = r[1]
            r = json.loads(r)
            cmd = {'action': 'delete', 'args': r}
            cmd = json.dumps(cmd)
            self.__add_cmd_to_log(cmd)
            return 200, 'Ok', cmd
        
        return 400, 'Bad request', ''
    
    def __reset_election_timer(self):
        log.debug(f'{self.__this}: __reset_election_timer: Reset')
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

        log.debug(f'{self.__this}: __process_main_socket: Message from {ip}:{port}')

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
        n = self.__main_socket.writeDatagram(datagram)
        log.debug(f'{self.__this}: __send_raft_message: n = {n}, to {ip}:{port}')
    
    def __process_request_vote(self, ip: str, port: int, msg: protocol.Message):
        request = RaftRequestVoteRequest.from_protobuf(msg.request_vote)
        
        response = RaftRequestVoteResponse(self.__current_term, False)
        
        if self.__state == RaftState.Leader:
            log.debug(f'{self.__this}: __process_request_vote: I am Leader')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        #  Reply false if term < currentTerm
        if request.term < self.__current_term:
            log.debug(f'{self.__this}: __process_request_vote: Request term less than current term')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)

        # If RPC request or response contains term T > currentTerm: 
        # set currentTerm = T, convert to follower
        if request.term > self.__current_term:
            log.debug(f'{self.__this}: __process_request_vote: Become Follower')
            self.__current_term = request.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
            self.__leader = None
            
            response.term = self.__current_term
            
            self.updated.emit()
        
        # if already voted for self or another candidate
        if self.__voted_for is not None and self.__voted_for != request.candidateId:
            log.debug(f'{self.__this}: __process_request_vote: Is already voted for another candidate')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        # if candidate’s log is not up-to-date
        if request.lastLogIndex < len(self.__log):
            log.debug(f'{self.__this}: __process_request_vote: Request is not up-to-date')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        # if candidate’s log is not up-to-date
        if self.__log and request.lastLogTerm < self.__log[-1].term:
            log.debug(f'{self.__this}: __process_request_vote: Request term < my last log item term')
            msg = protocol.Message()
            msg.request_vote_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        self.__voted_for = request.candidateId
        self.__reset_election_timer()
        
        response.voteGranted = True

        log.debug(f'{self.__this}: __process_request_vote: Vote granted to {self.__voted_for}')
        
        self.updated.emit()
        
        msg = protocol.Message()
        msg.request_vote_response.CopyFrom(response.to_protobuf())
        return self.__send_raft_message(ip, port, msg)
    
    def __process_request_vote_response(self, ip: str, port: int, msg: protocol.Message):
        r = RaftRequestVoteResponse.from_protobuf(msg.request_vote_response)
        
        if r.term > self.__current_term:
            log.debug(f'{self.__this}: __process_request_vote_response: My term is outdated')
            self.__current_term = r.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
            self.__leader = None
            
            self.updated.emit()
            return
        
        if r.term < self.__current_term:
            log.debug(f'{self.__this}: __process_request_vote_response: New election is already started')
            return
        
        self.__votes += 1

        # If votes received from majority of servers: become leader
        log.debug(f'{self.__this}: Votes: {self.__votes}')
        if self.__votes > len(self.__others) / 2:
            log.debug(f'{self.__this}: __process_request_vote_response: I try to become Leader')
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
            pass
        
        self.updated.emit()
    
    def __process_append_entries(self, ip: str, port: int, msg: protocol.Message):
        log.debug(f'{self.__this}: __process_append_entries: From {ip}:{port}')

        request = RaftAppendEntriesRequest.from_protobuf(msg.append_entries)

        response = RaftAppendEntriesResponse(self.__current_term, False, len(self.__log) + 1)

        # Reply false if term < currentTerm
        if request.term < self.__current_term:
            log.debug(f'{self.__this}: __process_append_entries: Request term less than current term')
            msg = protocol.Message()
            msg.append_entries_response.CopyFrom(response.to_protobuf())
            return self.__send_raft_message(ip, port, msg)
        
        # If any append entries RPC received - reset election timer
        self.__reset_election_timer()
        
        # If RPC request or response contains term T > currentTerm: 
        # set currentTerm = T, convert to follower
        if request.term > self.__current_term:
            log.debug(f'{self.__this}: __process_append_entries: My term is outdated')
            self.__current_term = request.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
        
        # If AppendEntries RPC received from new leader:
        # convert to follower
        if self.__state == RaftState.Candidate or self.__state == RaftState.Leader:
            log.debug(f'{self.__this}: __process_append_entries: I am Candidate or Leader, I become Follower')
            self.__current_term = request.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
        
        self.__leader = request.leaderId

        self.updated.emit()
        
        # Reply false if log doesn’t contain an entry at prevLogIndex 
        # whose term matches prevLogTerm
        if request.prevLogIndex > 0:
            if len(self.__log) < request.prevLogIndex:
                log.debug(f'{self.__this}: __process_append_entries: my log last index < request prev log index')
                msg = protocol.Message()
                msg.append_entries_response.CopyFrom(response.to_protobuf())
                return self.__send_raft_message(ip, port, msg)
            # If the follower does not find an entry in
            # its log with the same index and term, then it refuses the
            # new entries. 
            if self.__log[request.prevLogIndex - 1].term != request.prevLogTerm:
                log.debug(f'{self.__this}: __process_append_entries: my log prev term != request prev log term')
                msg = protocol.Message()
                msg.append_entries_response.CopyFrom(response.to_protobuf())
                return self.__send_raft_message(ip, port, msg)
        
        # If existing entry conflicts with new one, delete it and next
        # To bring a follower’s log into consistency with its own,
        # the leader must find the latest log entry where the two
        # logs agree, delete any entries in the follower’s log after
        # that point, and send the follower all of the leader’s entries
        # after that point.
        if request.entries:
            log.debug(f'{self.__this}: __process_append_entries: Request Entries = {len(request.entries)}')
            if request.prevLogIndex > 0:
                log.debug(f'{self.__this}: __process_append_entries: Request PrevLogIndex = {request.prevLogIndex}')
                self.__log = self.__log[:request.prevLogIndex] + request.entries[::]
            else:
                self.__log = request.entries[::]
        
        log.debug(f'{self.__this}: __process_append_entries: Log = {[str(x) for x in self.__log]}')
        response.lastLogIndex = len(self.__log) + 1
        
        # Update commit index if leaderCommit > commitIndex
        if request.leaderCommit > self.__commit_index:
            log.debug(f'{self.__this}: __process_append_entries: Request Leader Commit = {request.prevLogIndex}')
            self.__commit_index = min(request.leaderCommit, len(self.__log))
        
        # If commitIndex > lastApplied: increment lastApplied, apply
        # log[lastApplied] to state machine
        if self.__commit_index > self.__last_applied:
            self.__apply(self.__last_applied + 1, self.__commit_index)
            self.__last_applied = self.__commit_index

        response.success = True

        log.debug(f'{self.__this}: __process_append_entries: Success')

        self.updated.emit()

        msg = protocol.Message()
        msg.append_entries_response.CopyFrom(response.to_protobuf())
        return self.__send_raft_message(ip, port, msg)

    def __process_append_entries_response(self, ip: str, port: int, msg: protocol.Message):
        r = RaftAppendEntriesResponse.from_protobuf(msg.append_entries_response)
        
        if r.term > self.__current_term:
            log.debug(f'{self.__this}: __process_append_entries_response: My term is outdated')
            self.__current_term = r.term
            self.__state = RaftState.Follower
            self.__voted_for = None
            self.__votes = 0
            self.__leader = None
            
            self.updated.emit()
            return
        
        if r.term < self.__current_term:
            log.debug(f'{self.__this}: __process_append_entries_response: Response from old term - rejected')
            return
        
        server = f'{ip}:{port}'

        if r.success:
            # Update nextIndex and matchIndex for Follower
            self.__next_index[server] = r.lastLogIndex
            self.__match_index[server] = self.__next_index[server] - 1
            
            # If there exists an N such that N > commitIndex, a majority
            # of matchIndex[i] >= N, and log[N].term == currentTerm:
            # set commitIndex = N 
            # ...
            for N in range(len(self.__log), 0, -1):
                if N <= self.__commit_index:
                    continue
                if self.__log[N - 1].term != self.__current_term:
                    continue
                replicated = [x >= N for x in self.__match_index.values()].count(True)
                
                if replicated + 1 <= (len(self.__others) + 1) // 2:
                    continue

                self.__commit_index = N
                break
            
            log.debug(f'{self.__this}: __process_append_entries_response: Success = {r.lastLogIndex}')

            if self.__commit_index > self.__last_applied:
                self.__apply(self.__last_applied + 1, self.__commit_index)
                self.__last_applied = self.__commit_index

            self.updated.emit()
            return
        
        # After a rejection, the leader decrements nextIndex and retries
        # the AppendEntries RPC.
        self.__next_index[server] = max(1, self.__next_index[server] - 1)
        # When nextIndex will reach a point where the leader and follower logs match,
        # AppendEntries will succeed, which removes any conflicting entries 
        # in the follower’s log and appends entries from the leader’s log (if any).
        self.updated.emit()
        return
    
    def __heartbeat(self):
        # Upon election: Send initial empty AppendEntries RPCs (heartbeat) to each server
        if not self.__state == RaftState.Leader:
            log.debug(f'{self.__this}: __heartbeat: I am not Leader')
            return
        
        log.debug(f'{self.__this}: __heartbeat: Send heartbeats')

        self.__append_entries_for_all(is_heartbeat=False)  # To send entries any time
        
        log.debug(f'{self.__this}: __heartbeat: Heartbears are sent')
        
        # Repeat during idle periods to prevent election timeouts
        self.__heartbeat_timer.start(self.__heartbeat_timeout)
    
    def __election(self):
        # If node has become Leader and election timer callback was called,
        # new election will not be started
        if self.__state == RaftState.Leader:
            log.debug(f'{self.__this}: __election: I am Leader')
            return
        
        log.debug(f'{self.__this}: __election: Started')
        
        # On conversion to candidate, start election
        if self.__state == RaftState.Follower:
            log.debug(f'{self.__this}: __election: I was Follower, now I am Candidate')
            self.__state = RaftState.Candidate
        
        # Increment current term
        self.__current_term += 1
        # Vote for self
        self.__voted_for = self.__this 
        self.__votes = 1
        
        self.__reset_election_timer()
        
        log.debug(f'{self.__this}: __election: Term is {self.__current_term}')
        
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
        
        log.debug(f'{self.__this}: __election: Requets are sent')

        self.updated.emit()
    
    def __append_entries_for_all(self, is_heartbeat: bool = False):
        for server in self.__others:
            self.__append_entries(server, is_heartbeat)
    
    def __append_entries(self, server: str, is_heartbeat: bool = False):
        # Invoked by leader to replicate log entries
        # Also used as heartbeat
        if not self.__state == RaftState.Leader:
            log.debug(f'{self.__this}: __append_entries: I am not Leader')
            return
        
        log.debug(f'{self.__this}: __append_entries: Try for server {server}.')
        
        # When sending an AppendEntries RPC, the leader includes the index
        # and term of the entry in its log that immediately precedes
        # the new entries.
        next_log_index = self.__next_index.get(server, 1)
        prev_log_index = next_log_index - 1
        prev_log_term = self.__log[prev_log_index - 1].term if self.__log else 0

        log.debug(f'{self.__this}: __append_entries: NLI = {next_log_index}, PLI = {prev_log_index}.')
        
        # log entries to store (may send more than one for efficiency)
        if next_log_index <= len(self.__log):
            entries = self.__log[next_log_index - 1:]
        else:
            entries = []

        log.debug(f'{self.__this}: __append_entries: ES = {entries[-1].cmd if entries else None}.')
        
        # empty for heartbeat
        if is_heartbeat:
            entries = []

        request = RaftAppendEntriesRequest(
            term = self.__current_term,
            leaderId = str(self.__this),
            prevLogIndex = prev_log_index,
            prevLogTerm = prev_log_term,
            entries = entries,
            leaderCommit = self.__commit_index
        )
        
        msg = protocol.Message()
        msg.append_entries.CopyFrom(request.to_protobuf())
        
        host, port = server.split(':')
        self.__send_raft_message(host, int(port), msg)

        log.debug(f'{self.__this}: __append_entries: Sent to {server}.')
    
    def __apply(self, start: int, stop: int):
        for i in range(start, stop + 1):
            self.__fsm.apply(self.__log[i - 1].cmd)
        
    def __add_cmd_to_log(self, cmd: str):
        entry = RaftLogEntry(cmd, self.__current_term)
        self.__log += [entry]
        self.__append_entries_for_all(is_heartbeat=False)
    
    @property
    def is_configured(self):
        return self.__is_configured
    
    @property
    def is_active(self):
        return self.__is_active
    
    @property
    def state(self):
        return self.__state
    
    @property
    def this(self):
        return self.__this
    
    @property
    def leader(self):
        return self.__leader
    
    @property
    def current_term(self):
        return self.__current_term
    
    @property
    def voted_for(self):
        return self.__voted_for
    
    @property
    def votes(self):
        return self.__votes
    
    @property
    def commit_index(self):
        return self.__commit_index
    
    @property
    def last_applied(self):
        return self.__last_applied
    
    @property
    def next_index(self):
        return self.__next_index
    
    @property
    def match_index(self):
        return self.__match_index
    
    @property
    def heartbeat_timeout(self):
        return self.__heartbeat_timeout
    
    @property
    def election_timeout(self):
        return self.__election_timeout
    
    @property
    def log(self):
        return self.__log[::]
