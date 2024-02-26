import os
import sys
import json
import multiprocessing
import time

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG, 
)
from utils.log import log
from utils.socket import MulticastReceiver
from utils.exchanges import check_exchange_process

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]