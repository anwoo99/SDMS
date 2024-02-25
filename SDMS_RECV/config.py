import os
import sys
import json
import threading

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG,
    CONFIG_DIR
)
from utils.log import log

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

EXCHANGE_CONFIG_PATH = f"{CONFIG_DIR}/exchanges.json"