
import random

from Raft.Log import RaftLog
from Raft.ServerState import RaftServerState
from Raft.Dto.AppendEntriesRequest import AppendEntriesRequest
from Raft.Dto.AppendEntriesResponse import AppendEntriesResponse
from Raft.Dto.RequestVoteRequest import RequestVoteRequest
from Raft.Dto.RequestVoteResponse import RequestVoteResponse


class RaftServer:

    def __init__(self, this: str, others: list[str]):
        self._state = RaftServerState.Follower
        self._this = this
        self._others = others
    
        self._current_term = 0
        self._voted_for = None
        self._log = RaftLog()

        self._commit_index = 0
        self._last_applied = 0

        self._next_index = {}
        self._match_index = {}

        self._election_timeout = 500 + random.randint(0, 200)
        self._heartbeat_timeout = 100
    
    def _send_request_vote(self):
        pass

    def _recv_request_vote(self, request: RequestVoteRequest):
        pass

    def _send_append_entries(self):
        pass

    def _recv_append_entries(self, request: AppendEntriesRequest):
        pass
    
    def _start_election(self):
        if not self._state == RaftServerState.Follower:
            return
        
        self._state = RaftServerState.Candidate
        self._current_term += 1
        self._voted_for = self._this
    
    def _reset_election_timer(self):
        pass
