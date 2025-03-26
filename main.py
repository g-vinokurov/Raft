
import aiohttp.web as web
import raft


class Storage(raft.RaftServer):
    def __init__(self, this: str, others: list[str] = []):
        super().__init__(this, others)

        self.route('/api/get', self._api_get)
        self.route('/api/put', self._api_put)

    async def _api_get(self, request: web.Request):
        return web.Response(text='get')
    
    async def _api_put(self, request: web.Request):
        return web.Response(text='put')


if __name__ == '__main__':
    server = Storage('localhost:9001', ['localhost:9002', 'localhost:9003'])
    server.start()
