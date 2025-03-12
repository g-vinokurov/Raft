
from Raft.Dto.Cmd import Cmd
from Raft.Dto.LogEntry import LogEntry


class RaftLog:
    def __init__(self):
        self._entries = []
    
    def add(self, cmd: Cmd, term: int):
        index = len(self._entries) + 1
        entry = LogEntry(cmd, index, term)
        self._entries.append(entry)
