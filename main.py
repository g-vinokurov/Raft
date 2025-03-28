
import aiohttp.web as web
import raft
import sys
import asyncio


class Storage(raft.RaftServer):
    def __init__(self, this: str, others: list[str] = []):
        super().__init__(this, others)

        self.route('/api/get', self._api_get)
        self.route('/api/put', self._api_put)

    async def _api_get(self, request: web.Request):
        return web.Response(text='get')
    
    async def _api_put(self, request: web.Request):
        return web.Response(text='put')


async def main():
    servers = [
        'localhost:9001',
        'localhost:9002',
        'localhost:9003', 
        'localhost:9004',
        'localhost:9005'
    ]
    this_id = int(sys.argv[1])
    this = servers.pop(this_id - 1)
    others = servers
    server = Storage(this, others)
    task = asyncio.create_task(server.run())
    await task


asyncio.run(main())
