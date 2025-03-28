
import sys
import asyncio

import raft


class Storage(raft.RaftServer):
    def __init__(self, this: str, others: list[str] = []):
        super().__init__(this, others)
        
        # self.route('/api/get', self._api_get)
        # self.route('/api/put', self._api_put)
    
    def _api_get(self, request: dict) -> dict:
        return {'msg': 'Not implemented'}
    
    def _api_put(self, request: dict) -> dict:
        return {'msg': 'Not implemented'}


async def main(this_idx):
    servers = [
        'localhost:9001',
        'localhost:9002',
        'localhost:9003', 
        'localhost:9004',
        'localhost:9005'
    ]
    
    this = servers.pop(this_idx - 1)
    others = servers
    
    await Storage(this, others).run()


asyncio.run(main(int(sys.argv[1])))
