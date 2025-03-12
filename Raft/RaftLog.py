
from Raft.Dto.RaftCmd import RaftCmd
from Raft.Dto.RaftLogEntry import RaftLogEntry


class RaftLog:
    def __init__(self):
        self._entries = []
    
    def add(self, cmd: RaftCmd, term: int):
        index = len(self._entries) + 1
        entry = RaftLogEntry(cmd, index, term)
        self._entries.append(entry)
