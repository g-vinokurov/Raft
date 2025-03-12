
import pydantic


class Cmd(pydantic.BaseModel):
    name: str
    args: list = []
    kwargs: dict = {}
