
import json


class State:
    def __init__(self):
        self._storage : dict[str, str] = {}
    
    def apply(self, cmd: str):
        cmd = json.loads(cmd)
        if not isinstance(cmd, dict):
            return
        
        action = cmd.get('action', '')
        if action not in ['put', 'delete']:
            return
        
        args = cmd.get('args', {})
        if not isinstance(args, dict):
            return
        
        if action == 'put':
            if 'key' not in args or 'val' not in args:
                return
            key = args['key']
            val = args['val']
            self._storage[key] = val
        
        if action == 'delete':
            if 'key' not in args:
                return
            key = args['key']
            self._storage.pop(key, None)
        return
    
    def get(self, key: str) -> str | None:
        return self._storage.get(key, None)
