
import pydantic


class RaftRequestVoteResponse(pydantic.BaseModel):
    term: int
    voteGranted: bool
