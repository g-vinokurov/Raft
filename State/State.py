
class State:
    def __init__(self):
        self._storage : dict[str, str] = {}
    
    def apply(self, cmd: str):
        pass
