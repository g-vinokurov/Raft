
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
    'localhost:9001',
    'localhost:9002',
    'localhost:9003', 
    'localhost:9004',
    'localhost:9005'
]
