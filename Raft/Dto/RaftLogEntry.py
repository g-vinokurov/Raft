
import pydantic

from Raft.Dto.RaftCmd import RaftCmd


class RaftLogEntry(pydantic.BaseModel):
    cmd: RaftCmd
    index: int
    term: int
