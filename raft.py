
import enum
import random
import pydantic
import json

from typing import Literal

import asyncio
import aiohttp.web as web
import aiohttp


class Timer:
    def __init__(self, timeout: int, callback):
        self._timeout = timeout / 1000
        self._callback = callback
        self._task = None
        self._is_cancelled = False
    
    async def start(self):
        self._task = asyncio.create_task(self._job())
        await self._task

    async def _job(self):
        await asyncio.sleep(self._timeout)
        if self._is_cancelled:
            return
        await self._callback()

    def cancel(self):
        self._is_cancelled = True


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
        self._entries : list[RaftLogEntry] = []
    
    def add(self, cmd: RaftLogEntryCmd, term: int):
        index = len(self._entries) + 1
        entry = RaftLogEntry(cmd, index, term)
        self._entries.append(entry)
    
    def update(self, entries: list[RaftLogEntry]):
        self._entries = entries[::]
    
    @property
    def last(self):
        return self._entries[-1]
    
    def __getitem__(self, key) -> RaftLogEntry:
        return self._entries[key]
    
    def __len__(self):
        return len(self._entries)
    
    def __bool__(self):
        return len(self._entries) > 0


class RaftServer:
    _RPC_REQUEST_VOTE_URL = '/raft-rpc/request-vote'
    _RPC_APPEND_ENTRIES_URL = '/raft-rpc/append-entries'

    def __init__(self, this: str, others: list[str] = [], echo: bool = True):
        self._echo = echo

        self._state = RaftServerState.Follower
        self._this = RaftNodeAddress(this)
        self._others = list(map(RaftNodeAddress, others))
        
        self._leader : RaftNodeAddress | None = None
    
        self._current_term = 0
        self._voted_for : RaftNodeAddress | None = None
        self._log = RaftLog()

        self._commit_index = 0
        self._last_applied = 0

        self._next_index : dict[str, int] = {}
        self._match_index : dict[str, int] = {}

        # self._apply = lambda x: x

        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._start_election)

        self._heartbeat_timeout = 100
        self._heartbeat_timer = Timer(self._heartbeat_timeout, self._send_heartbeats)

        self._app = web.Application()
        self._is_running = False
    
    async def run(self):
        self._app.add_routes([
            web.post(self._RPC_REQUEST_VOTE_URL, self._raft_rpc_request_vote),
            web.post(self._RPC_APPEND_ENTRIES_URL, self._raft_rpc_append_entries),
        ])

        runner = web.AppRunner(self._app)
        await runner.setup()

        site = web.TCPSite(runner, self._this.host, self._this.port)
        await site.start()

        self._is_running = True

        self.echo(f'Started! I am {self._this}')

        await self._reset_election_timer()
        
        try:
            while self._is_running:
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            await site.stop()
    
    def stop(self):
        self.echo('Stopping...')
        self._is_running = False

    def echo(self, msg):
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
    
    async def _send_rpc(self, node: RaftNodeAddress, url: str, data: dict) -> dict | None:
        url = f'http://{node.host}:{node.port}{url}'
        try:
            async with aiohttp.ClientSession() as session:
                self.echo(f'{url} {data}')
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            self.echo(f'Error sending RPC to {url}: {e}')
            return None
    
    async def _reset_election_timer(self):
        # Reset timer with new random value of timeout
        # In order to avoid more than one elections for many vote attempts
        self._election_timer.cancel()
        self._election_timeout = 500 + random.randint(0, 200)
        self._election_timer = Timer(self._election_timeout, self._start_election)
        await self._election_timer.start()
    
    async def _start_election(self):
        # If node has become Leader and election timer callback was called,
        # new election will not be started
        if self._state == RaftServerState.Leader:
            return
        
        self.echo(f'Start election...')
        
        # On conversion to candidate, start election
        if self._state == RaftServerState.Follower:
            self.echo('I was Follower, now I am Candidate')
            self._state = RaftServerState.Candidate
        
        # Increment current term
        self._current_term += 1
        # Vote for self
        self._voted_for = self._this 
        votes = 1
        
        self.echo(f'Term is {self._current_term}')
        
        # Send RequestVote RPCs to all other servers
        votes += await self._request_votes()
        
        self.echo(f'Total Votes: {votes}')
        
        # If votes received from majority of servers: become leader
        if votes > len(self._others) / 2:
            self.echo('I try to become Leader')
            await self._become_leader()
        else:
            self.echo('I got too few votes, now I am Follower again')
            self._state = RaftServerState.Follower
            await self._reset_election_timer()
        return

    async def _send_heartbeats(self):
        # Upon election: Send initial empty AppendEntries RPCs (heartbeat) to each server
        if not self._state == RaftServerState.Leader:
            return
        
        self.echo('Send heartbeats')
        
        __tasks = []
        for node in self._others:
            __task = asyncio.create_task(self._append_entries(node, True))
            __tasks.append(__task)
        
        # Repeat during idle periods to prevent election timeouts
        await self._heartbeat_timer.start()
        
        # Gather? Maybe, but now such solution:
        for __task in __tasks:
            await __task
    
    async def _request_votes(self):
        if not self._state == RaftServerState.Candidate:
            return
        
        self.echo('Try request votes...')

        last_log_index = len(self._log)
        last_log_term = self._log.last if self._log else 0
      
        data = RaftRequestVoteRequest(
            term = self._current_term,
            candidateId = str(self._this),
            lastLogIndex = last_log_index,
            lastLogTerm = last_log_term
        ).model_dump()

        route = self._RPC_REQUEST_VOTE_URL

        __tasks = []
        for node in self._others:
            __task = asyncio.create_task(
                asyncio.wait_for(
                    self._send_rpc(node, route, data),
                    self._election_timeout / 1000
                )
            )
            __tasks.append(__task)
        
        votes = 0
        for __task in __tasks:
            try:
                r = await __task
            except asyncio.TimeoutError:
                self.echo('Timeout Error')
                continue
             
            self.echo(f'RESPONSE: {r}')
            if r is None:
                continue
            try:
                r = RaftRequestVoteResponse(**r)
            except pydantic.ValidationError as e:
                self.echo(f'Request Votes: Response parsing error: {e}')
                continue
            if r.voteGranted:
                votes += 1
        return votes
    
    async def _become_follower(self, term: int):
        self.echo(f'Became Follower with term {term}')
        self._current_term = term
        self._state = RaftServerState.Follower
        self._voted_for = None
        self._leader = None
        await self._reset_election_timer()
    
    async def _become_leader(self):
        self._state = RaftServerState.Leader
        self._leader = self._this
        # for each server,
        # index of the next log entry to send to that server
        self._next_index = { node: len(self._log) + 1 for node in self._others }
        # for each server, 
        # index of highest log entry known to be replicated on server
        self._match_index = { node: 0 for node in self._others }
        await self._send_heartbeats()

    async def _append_entries(self, node: RaftNodeAddress, is_heartbeat: bool = False):
        # Invoked by leader to replicate log entries
        # Also used as heartbeat
        if not self._state == RaftServerState.Leader:
            return
        
        self.echo(f'Try append entries for node {node}...')
        
        # When sending an AppendEntries RPC, the leader includes the index
        # and term of the entry in its log that immediately precedes
        # the new entries.
        next_log_index = self._next_index.get(node, 1)
        prev_log_index = next_log_index - 1
        prev_log_term = self._log[prev_log_index] if self._log else 0
    
        # log entries to store (may send more than one for efficiency)
        if next_log_index < len(self._log):
            entries = self._log[next_log_index:]
        else:
            entries = []
        
        # empty for heartbeat
        if is_heartbeat:
            entries = []

        data = RaftAppendEntriesRequest(
            term = self._current_term,
            leaderId = str(self._this),
            prevLogIndex = prev_log_index,
            prevLogTerm = prev_log_term,
            entries = entries,
            leaderCommit = self._commit_index
        ).model_dump()
        
        route = self._RPC_APPEND_ENTRIES_URL

        __tasks = []
        for node in self._others:
            __task = asyncio.create_task()
            __tasks.append(__task)

        r = await self._send_rpc(node, route, data)
        
        if r is None:
            self.echo(f'Append entries for {node}: Response is None')
            return
        
        try:
            r = RaftAppendEntriesResponse(**r)
        except pydantic.ValidationError as e:
            self.echo(f'Append Entries for {node}: Response parsing error:')
            return
        
        if r.term > self._current_term:
            await self._become_follower(r.term)
            return
        
        if r.success:
            # Update nextIndex and matchIndex for Follower
            self._next_index[node] = prev_log_index + len(entries) - 1
            self._match_index[node] = self._next_index[node] - 1
            
            # If there exists an N such that N > commitIndex, a majority
            # of matchIndex[i] ≥ N, and log[N].term == currentTerm:
            # set commitIndex = N 
            # ...
            match_indexs = list(self._match_index.values())
            n = max(set(match_indexs), key=match_indexs.count)
            if n > self._commit_index and self._log[n - 1].term == self._current_term:
                self._commit_index = n
            return
        
        # After a rejection, the leader decrements nextIndex and retries
        # the AppendEntries RPC.
        self._next_index[node] = max(1, self._next_index[node] - 1)
        # When nextIndex will reach a point where the leader and follower logs match,
        # AppendEntries will succeed, which removes any conflicting entries 
        # in the follower’s log and appends entries from the leader’s log (if any).
        return

    async def _raft_rpc_request_vote(self, request: web.Request):
        try:
            data = await request.json()
            r = RaftRequestVoteRequest(**data)
        except (json.JSONDecodeError, pydantic.ValidationError):
            self.echo('Raft RCP: Request Vote: Request parsing error')
            msg = {'error': 'Invalid JSON'}
            return web.json_response(msg, status=400)
        
        self.echo(f'RPC REQUEST VOTE REQUEST: {data}')
        
        term = r.term
        candidateId = RaftNodeAddress(r.candidateId)
        lastLogIndex = r.lastLogIndex
        lastLogTerm = r.lastLogTerm

        response = RaftRequestVoteResponse(
            term = self._current_term, 
            voteGranted = False
        ).model_dump()
        
        # If RPC request or response contains term T > currentTerm: 
        # set currentTerm = T, convert to follower
        if term > self._current_term:
            self.echo(f'Handle Request Vote: 0: Become Follower')
            await self._become_follower(term)
        
        #  Reply false if term < currentTerm
        if term < self._current_term:
            self.echo(f'Handle Request Vote: 1: {response}')
            return web.json_response(response)
        
        # if already voted for self or another candidate
        if self._voted_for is not None and self._voted_for != candidateId:
            self.echo(f'Handle Request Vote: 2: {response}')
            return web.json_response(response)
        
        # if candidate’s log is not up-to-date
        if lastLogIndex < len(self._log):
            self.echo(f'Handle Request Vote: 3: {response}')
            return web.json_response(response)
        
        # if candidate’s log is not up-to-date
        if self._log and lastLogTerm < self._log.last.term:
            self.echo(f'Handle Request Vote: 4: {response}')
            return web.json_response(response)
        
        self._voted_for = candidateId

        await self._reset_election_timer()

        response = RaftRequestVoteResponse(
            term = self._current_term, 
            voteGranted = True
        ).model_dump()
        self.echo(f'Handle Request Vote: 5: {response}')
        return web.json_response(response)
    
    async def _raft_rpc_append_entries(self, request: web.Request):
        try:
            data = await request.json()
            r = RaftAppendEntriesRequest(**data)
        except (json.JSONDecodeError, pydantic.ValidationError):
            self.echo('Raft RCP: Append Entries: Request parsing error')
            msg = {'error': 'Invalid JSON'}
            return web.json_response(msg, status=400)
        
        self.echo(f'RPC APPEND ENTRIES REQUEST: {data}')
        
        term = r.term
        leaderId = RaftNodeAddress(r.leaderId)
        prevLogIndex = r.prevLogIndex
        prevLogTerm = r.prevLogTerm
        leaderCommit = r.leaderCommit
        entries = r.entries

        response = RaftAppendEntriesResponse(
            term = self._current_term,
            success = False
        ).model_dump()

        # Reply false if term < currentTerm
        if term < self._current_term:
            return web.json_response(response)
        
        # If any append entries RPC received - reset election timer
        await self._reset_election_timer()
        
        # If RPC request or response contains term T > currentTerm: 
        # set currentTerm = T, convert to follower
        if term > self._current_term:
            await self._become_follower(term)
        
        self._leader = leaderId
        
        # Reply false if log doesn’t contain an entry at prevLogIndex 
        # whose term matches prevLogTerm
        if prevLogIndex > 0:
            if len(self._log) < prevLogIndex:
                return web.json_response(response)
            # If the follower does not find an entry in
            # its log with the same index and term, then it refuses the
            # new entries. 
            if self._log[prevLogIndex - 1].term != prevLogTerm:
                return web.json_response(response)
        
        # If existing entry conflicts with new one, delete it and next
        # To bring a follower’s log into consistency with its own,
        # the leader must find the latest log entry where the two
        # logs agree, delete any entries in the follower’s log after
        # that point, and send the follower all of the leader’s entries
        # after that point.
        if entries:
            self._log.update(self._log[:prevLogIndex] + entries)
        
        # Update commit index if leaderCommit > commitIndex
        if leaderCommit > self._commit_index:
            self._commit_index = min(leaderCommit, len(self._log))
        
        # If commitIndex > lastApplied: increment lastApplied, apply
        # log[lastApplied] to state machine
        if self._commit_index > self._last_applied:
            self._last_applied = self._commit_index
            # self._apply(self._log[self._last_applied - 1])

        response = RaftAppendEntriesResponse(
            term = self._current_term,
            success = True
        ).model_dump()
        return web.json_response(response)
