
import pydantic


class RaftAppendEntriesResponse(pydantic.BaseModel):
    term: int
    success: bool
