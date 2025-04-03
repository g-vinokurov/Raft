
import enum
import logging

from Config import LOG_LVL
from Config import LOG_FILE
from Config import LOG_FMT


class LogLevel(enum.Enum):
    DEBUG    = logging.DEBUG
    INFO     = logging.INFO
    WARNING  = logging.WARNING
    ERROR    = logging.ERROR
    CRITICAL = logging.CRITICAL


logging.basicConfig(
    level=LogLevel[LOG_LVL].value, 
    filename=LOG_FILE,
    filemode='a',
    format=LOG_FMT
)

log = logging.getLogger()
