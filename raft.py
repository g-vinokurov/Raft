
import enum
import random
import pydantic
import json
import time

import asyncio
import aiohttp.web as web
import aiohttp


class Timer:
    def __init__(self, timeout: int, callback):
        self._timeout = timeout / 1000
        self._callback = callback
        self._is_cancelled = False
    
    async def start(self):
        await asyncio.sleep(self._timeout)
        if self._is_cancelled:
            return
        await self._callback()
    
    def cancel(self):
        self._is_cancelled = True


class RaftLogEntryCmd(pydantic.BaseModel):
    name: str
    args: list = []
    kwargs: dict = {}


class RaftLogEntry(pydantic.BaseModel):
    cmd: RaftLogEntryCmd
    term: int


class RaftAppendEntriesRequest(pydantic.BaseModel):
    term: int
    leaderId: str
    prevLogIndex: int
    prevLogTerm: int
    entries: list[RaftLogEntry]
    leaderCommit: int


class RaftAppendEntriesResponse(pydantic.BaseModel):
    term: int
    success: bool


class RaftRequestVoteRequest(pydantic.BaseModel):
    term: int
    candidateId: str
    lastLogIndex: int
    lastLogTerm: int


class RaftRequestVoteResponse(pydantic.BaseModel):
    term: int
    voteGranted: bool


class RaftState(enum.Enum):
    Follower  = 0
    Candidate = 1
    Leader    = 2


class RaftServer:    
    def __init__(self, this: str, others: list[str] = [], echo: bool = True):
        self._echo = echo
        
        self._state = RaftState.Follower
        self._this = this
        self._others = others[::]
        
        self._leader : str | None = None
        
        self._current_term = 0
        self._voted_for : str | None = None
        self._log : list[RaftLogEntry] = []
        
        self._commit_index = 0
        self._last_applied = 0
        
        self._next_index : dict[str, int] = {}
        self._match_index : dict[str, int] = {}

        self._heartbeat_timeout = 100
        self._heartbeat_timer = Timer(self._heartbeat_timeout, self._heartbeat)
        
        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._election)

        host, port = self._this.split(':')
        self._host = host
        self._port = int(port)
        
        self._app = web.Application()
        self._is_running = False
    
    async def run(self):
        if self._is_running:
            return
        self._is_running = True
        
        self._app.add_routes([
            web.post('/', self._rpc_handler),
        ])
        
        runner = web.AppRunner(self._app)
        await runner.setup()
        
        site = web.TCPSite(runner, self._host, self._port)
        await site.start()
        
        self.echo(f'SERVER STARTED. {self._this}')
        
        try:
            while self._is_running:
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            await site.stop()
        self.stop()
    
    def stop(self):
        if not self._is_running:
            return
        self._is_running = False
        
        self.echo('STOPPING SERVER...')
    
    def echo(self, msg):
        if not self._echo:
            return
        print(f'{msg}')
    
    async def _heartbeat(self):
        pass
    
    async def _election(self):
        pass
    
    async def _rpc_handler(self, request: web.Request):
        return web.Response({'message': 'ok'})
