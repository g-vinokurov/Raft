

import enum


class RaftServerState(enum.Enum):
    Follower  = 0
    Candidate = 1
    Leader    = 2
