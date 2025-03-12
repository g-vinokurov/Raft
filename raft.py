
import enum
import random
import pydantic


class RaftLogEntryCmd(pydantic.BaseModel):
    name: str
    args: list = []
    kwargs: dict = {}


class RaftLogEntry(pydantic.BaseModel):
    cmd: RaftLogEntryCmd
    index: int
    term: int


class RaftAppendEntriesRequest(pydantic.BaseModel):
    term: int
    leaderId: str
    prevLogIndex: int
    prevLogTerm: int
    entries: list[RaftLogEntry]
    leaderCommit: int


class RaftAppendEntriesResponse(pydantic.BaseModel):
    term: int
    success: bool


class RaftRequestVoteRequest(pydantic.BaseModel):
    term: int
    candidateId: str
    lastLogIndex: int
    lastLogTerm: int


class RaftRequestVoteResponse(pydantic.BaseModel):
    term: int
    voteGranted: bool


class RaftServerState(enum.Enum):
    Follower  = 0
    Candidate = 1
    Leader    = 2


class RaftLog:
    def __init__(self):
        self._entries = []
    
    def add(self, cmd: RaftLogEntryCmd, term: int):
        index = len(self._entries) + 1
        entry = RaftLogEntry(cmd, index, term)
        self._entries.append(entry)


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
