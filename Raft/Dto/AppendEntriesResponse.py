
import pydantic


class AppendEntriesResponse(pydantic.BaseModel):
    term: int
    success: bool
