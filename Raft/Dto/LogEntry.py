
import pydantic

from Raft.Dto.Cmd import Cmd


class LogEntry(pydantic.BaseModel):
    cmd: Cmd
    index: int
    term: int
