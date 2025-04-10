
import dotenv
import pathlib

env = dotenv.dotenv_values('.env')

# Project config
PROJECT_DIR = pathlib.Path(__file__).absolute().parent

# Assets config
FONTS_DIR = PROJECT_DIR / 'Assets' / 'Fonts'

# Logging config
LOG_LVL = env.get('LOG_LVL', 'CRITICAL')
LOG_FILE = env.get('LOG_FILE', None)
LOG_FMT = env.get('LOG_FMT', '%(asctime)s %(message)s')

RAFT_SERVERS = [
    '127.0.0.1:9001',
    '127.0.0.1:9002',
    '127.0.0.1:9003', 
    '127.0.0.1:9004',
    '127.0.0.1:9005'
]

REST_API_SERVERS = [
    '127.0.0.1:10001',
    '127.0.0.1:10002',
    '127.0.0.1:10003', 
    '127.0.0.1:10004',
    '127.0.0.1:10005'
]
