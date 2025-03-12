
import pydantic


class RaftCmd(pydantic.BaseModel):
    name: str
    args: list = []
    kwargs: dict = {}
