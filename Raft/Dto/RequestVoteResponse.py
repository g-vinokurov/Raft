
import pydantic


class RequestVoteResponse(pydantic.BaseModel):
    term: int
    voteGranted: bool
