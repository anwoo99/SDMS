import os
import sys
import json
import multiprocessing
import time
import signal
import traceback

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG, 
    UNIX_FEP_FLAG, UNIX_LOG_FLAG, UNIX_DA_FLAG
)
from utils.log import log
from utils.socket import (
    UnixDomainSocket
)
from utils.exchanges import check_exchange_process
from utils.format import Format

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]