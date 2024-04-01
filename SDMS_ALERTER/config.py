import os
import sys
import json
import multiprocessing
import time
import signal
import traceback
import socket
import select
import asyncio
import threading
import functools
import queue

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG, 
    UNIX_FEP_FLAG, UNIX_LOG_FLAG, UNIX_DA_FLAG, UNIX_ALERTER_FLAG,
    RCV_ERROR_CODE, PRICE_ERROR_CODE
)
from utils.log import (
    log, errlog
)
from utils.socket import (
    UnixDomainSocket
)
from utils.exchanges import check_exchange_process
from utils.format import Format
from utils.fix import (
    parse_fix_message, dict_to_fix
)

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]
LOGIN_LIST = APP_INFO["LOGIN"]

DEVICE_ALERT_SERVER_QUEUE = queue.Queue()

# TAG 정의
TAG_ERROR_CODE = 1
TAG_ERROR_DESC = 2
TAG_ERROR_TIME = 3
TAG_ERROR_EXNM = 4
TAG_ERROR_PONM = 5
TAG_ERROR_HOST_IP = 6
TAG_ERROR_MUL_IP = 7
TAG_ERROR_MUL_PORT = 8
TAG_LOGIN_ID = 64
TAG_LOGIN_PW = 65
TAG_LOGIN_AUTH = 100
TAG_TIMEOUT = 1024

# LOGIN ERROR CODE
DATA_NO_AUTH = -1
DATA_OK_AUTH = 1

SPLIT_CHAR = '\001'