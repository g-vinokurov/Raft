
import enum
import random
import pydantic

from typing import Literal

import asyncio
import aiohttp.web as web
import aiohttp


class Timer:
    def __init__(self, timeout: int, callback):
        self._timeout = timeout / 1000
        self._callback = callback
        self._task = None
    
    async def start(self):
        self._task = asyncio.create_task(self._job())
        await self._task

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        if self._task is None:
            return
        self._task.cancel()


class RaftNodeAddress:
    def __init__(self, address: str):
        host, port = address.split(':')
        self._host = host
        self._port = int(port)
    
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port
    
    def __str__(self):
        return f'{self._host}:{self._port}'


class TimeoutError(asyncio.TimeoutError):
    pass


class RaftLogEntryCmd(pydantic.BaseModel):
    name: str
    args: list = []
    kwargs: dict = {}


class RaftLogEntry(pydantic.BaseModel):
    cmd: RaftLogEntryCmd
    index: int
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


class RaftServerState(enum.Enum):
    Follower  = 0
    Candidate = 1
    Leader    = 2


class RaftLog:
    def __init__(self):
        self._entries = []
    
    def add(self, cmd: RaftLogEntryCmd, term: int):
        index = len(self._entries) + 1
        entry = RaftLogEntry(cmd, index, term)
        self._entries.append(entry)
    
    def __getitem__(self, key: int):
        return self._entries[key]
    
    def __len__(self):
        return len(self._entries)


class RaftServer:
    _RPC_REQUEST_VOTE_URL = '/raft-rpc/request-vote'
    _RPC_APPEND_ENTRIES_URL = '/raft-rpc/append-entries'

    def __init__(self, this: str, others: list[str] = [], echo: bool = True):
        self._echo = echo

        self._state = RaftServerState.Follower
        self._this = RaftNodeAddress(this)
        self._others = list(map(RaftNodeAddress, others))
    
        self._current_term = 0
        self._voted_for = None
        self._log = RaftLog()

        self._commit_index = 0
        self._last_applied = 0

        self._next_index : dict[str, int] = {}
        self._match_index : dict[str, int] = {}

        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._start_election)

        self._heartbeat_timeout = 500
        self._heartbeat_timer = Timer(self._heartbeat_timeout, self._send_heartbeats)

        self._app = web.Application()
        self._is_running = False
    
    def start(self):
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.log('Stopping...')
        self._is_running = False

    def log(self, msg):
        if not self._echo:
            return
        print(msg)
    
    def route(self, url: str, handler, method: Literal['get', 'post', 'put', 'delete'] = 'get'):
        if method == 'get':
            self._app.add_routes([web.get(url, handler)])
        if method == 'post':
            self._app.add_routes([web.post(url, handler)])
        if method == 'put':
            self._app.add_routes([web.put(url, handler)])
        if method == 'delete':
            self._app.add_routes([web.delete(url, handler)])
        return

    async def _run(self):
        self._app.add_routes([
            web.post(self._RPC_REQUEST_VOTE_URL, self._raft_rpc_request_vote),
            web.post(self._RPC_APPEND_ENTRIES_URL, self._raft_rpc_append_entries),
        ])

        runner = web.AppRunner(self._app)
        await runner.setup()

        site = web.TCPSite(runner, self._this.host, self._this.port)
        await site.start()

        self._is_running = True

        await self._reset_election_timer()
        
        try:
            while self._is_running:
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            await site.stop()
    
    async def _send_rpc(self, node: RaftNodeAddress, url: str, json: dict) -> dict | None:
        url = f'http://{node.host}:{node.port}{url}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=json) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            self.log(f'Error sending RPC to {url}: {e}')
            return None
    
    async def _reset_election_timer(self):
        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._start_election)
        await self._election_timer.start()
    
    async def _start_election(self):
        self.log('Start election...')

        if self._state == RaftServerState.Follower:
            self.log('I was Follower, now I am Candidate')
            self._state = RaftServerState.Candidate
        
        self._current_term += 1
        self._voted_for = self._this
        
        votes = 1
        votes += await self._request_votes()

        self.log(f'Votes received: {votes}')

        if votes > len(self._others) / 2:
            self.log('I try to become Leader')
            await self._become_leader()
        else:
            self.log('I got too few votes, now I am Follower again')
            self._state = RaftServerState.Follower
            await self._reset_election_timer()
        return

    async def _send_heartbeats(self):
        if not self._state == RaftServerState.Leader:
            return
        
        self.log('Send heartbeats')
        
        __tasks = []
        for node in self._others:
            __task = asyncio.create_task(self._append_entries(node))
            __tasks.append(__task)
        await self._heartbeat_timer.start()
        
        for __task in __tasks:
            await __task
    
    async def _request_votes(self):
        if not self._state == RaftServerState.Candidate:
            return
        
        self.log('Try request votes...')

        last_log_index = len(self._log)
        last_log_term = self._log[-1] if last_log_index else 0
      
        data = RaftRequestVoteRequest(
            term = self._current_term,
            candidateId = str(self._this),
            lastLogIndex = last_log_index,
            lastLogTerm = last_log_term
        ).model_dump()

        route = self._RPC_REQUEST_VOTE_URL

        __tasks = []
        for node in self._others:
            __task = asyncio.create_task(self._send_rpc(node, route, data))
            __tasks.append(__task)

        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*__tasks, return_exceptions=True),
                timeout=self._election_timeout
            )
        except asyncio.TimeoutError as e:
            self.log(f'Request votes: timeout error')
            return 0
        
        votes = 0

        for r in responses:
            if r is None:
                continue
            try:
                r = RaftRequestVoteResponse(**r)
            except pydantic.ValidationError as e:
                self.log(f'Response parsing error: {e}')
                continue
            if r.voteGranted:
                votes += 1
        return votes
    
    async def _become_leader(self):
        pass

    async def _append_entries(self, node: RaftNodeAddress, is_heartbeat: bool = True):
        pass
    
    async def _receive_append_entries(self):
        # if term < self.current_term:
        #     return False
        # 
        # self.reset_election_timer()
        # 
        # if self.state == 'candidate' and term > self.current_term:
        #     self.state = 'follower'
        # 
        # self.current_term = term
        # self.leader_id = leader_id
        # 
        # if len(self.log) > prev_log_index and self.log[prev_log_index]['term'] == prev_log_term:
        #     self.log = self.log[:prev_log_index + 1] + entries
        #     if leader_commit > self.commit_index:
        #         self.commit_index = min(leader_commit, len(self.log) - 1)
        #     return True
        # else:
        #     return False
        pass
    
    async def _receive_request_vote(self):
        # if term < self.current_term:
        #     return False
        # 
        # if (self.voted_for is None or self.voted_for == candidate_id) and \
        #    (last_log_index >= len(self.log) - 1 and last_log_term >= self.log[-1]['term'] if self.log else True):
        #     self.voted_for = candidate_id
        #     self.reset_election_timer()
        #     return True
        # else:
        #     return False
        pass
    
    async def _raft_rpc_request_vote(self, request: web.Request):
        return web.Response(text='vote!')
    
    async def _raft_rpc_append_entries(self, request: web.Request):
        return web.Resource(text='entries!')
