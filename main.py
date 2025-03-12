
from raft import RaftServer


if __name__ == '__main__':
    server = RaftServer('localhost', 8081)
    server.run()
