
import enum
import random
import pydantic

import asyncio
import aiohttp.web as web


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


class RaftServer:
    def __init__(self, this: str, others: list[str] = []):
        self._state = RaftServerState.Follower
        self._id = this
        self._others = others
    
        self._current_term = 0
        self._voted_for = None
        self._log = RaftLog()

        self._commit_index = 0
        self._last_applied = 0

        self._next_index = {}
        self._match_index = {}

        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._start_election)

        self._heartbeat_timeout = 500
        self._heartbeat_timer = Timer(self._heartbeat_timeout, self._send_heartbeats)

        self._host = str(this.split(':')[0])
        self._port = int(this.split(':')[1])

        self._app = web.Application()
        self._app.add_routes([
            web.post('/raft-rpc/request-vote', self._raft_rpc_request_vote),
            web.post('/raft-rpc/append-entries', self._raft_rpc_append_entries),
        ])
    
    def start(self):
        asyncio.run(self._run())

    async def _run(self):
        runner = web.AppRunner(self._app)
        await runner.setup()

        site = web.TCPSite(runner, self._host, self._port)
        await site.start()

        await self._reset_election_timer()
        
        while True:
            await asyncio.sleep(120)
    
    async def _reset_election_timer(self):
        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._start_election)
        await self._election_timer.start()
    
    async def _start_election(self):
        print('start election')
        await self._reset_election_timer()
        # if self.state == 'follower':
        #     self.state = 'candidate'
        # self.current_term += 1
        # self.voted_for = self.node_id
        # votes_received = 1
        # 
        # for peer in self.peers:
        #     if self.request_vote(peer):
        #         votes_received += 1
        # 
        # if votes_received > len(self.peers) / 2:
        #     self.state = 'leader'
        #     self.election_timer.cancel()
        #     self.send_heartbeats()
        # else:
        #     self.state = 'follower'
        #     self.reset_election_timer()
        pass

    async def _send_heartbeats(self):
        if not self._state == RaftServerState.Leader:
            return
        
        # print('send heartbeats')
        
        __tasks = []
        for node in self._others:
            __task = asyncio.create_task(self._append_entries(node))
            __tasks.append(__task)
        await self._heartbeat_timer.start()
        
        for __task in __tasks:
            await __task
    
    async def _request_vote(self, peer):
        # return random.choice([True, False])
        pass

    async def _append_entries(self, node: str, is_heartbeat: bool = True):
        print(f'append entries: {node}, {is_heartbeat}')
    
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
