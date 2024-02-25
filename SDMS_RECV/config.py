import os
import sys
import json
import threading
import time

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG,
    EXCHANGE_CONFIG_PATH 
)
from utils.log import log

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

SLEEP_TIME = 0.001