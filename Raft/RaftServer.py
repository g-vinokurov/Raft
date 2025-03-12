
import random

from Raft.RaftLog import RaftLog
from Raft.RaftServerState import RaftServerState
from Raft.Dto.RaftAppendEntriesRequest import RaftAppendEntriesRequest
from Raft.Dto.RaftAppendEntriesResponse import RaftAppendEntriesResponse
from Raft.Dto.RaftRequestVoteRequest import RaftRequestVoteRequest
from Raft.Dto.RaftRequestVoteResponse import RaftRequestVoteResponse


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

    def _recv_request_vote(self, request: RaftRequestVoteRequest):
        pass

    def _send_append_entries(self):
        pass

    def _recv_append_entries(self, request: RaftAppendEntriesRequest):
        pass
    
    def _start_election(self):
        if not self._state == RaftServerState.Follower:
            return
        
        self._state = RaftServerState.Candidate
        self._current_term += 1
        self._voted_for = self._this
    
    def _reset_election_timer(self):
        pass
