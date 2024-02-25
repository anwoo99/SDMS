from datetime import datetime, timedelta

import requests
import urllib.parse
import os
import copy
import time
import paramiko
import time
import telnetlib
import inspect
import pymysql
import base64
import hashlib
import hmac
import json
import socket
import struct
import fcntl

from settings import (
    INSTALLED_APPS, LOG_LEVEL_MAP,
    LOG_DIR,
    MUST, ERROR, PROGRESS, DEBUG
)

from .log import log

# Socket Max Buffer Size
MAX_BUFFER_SIZE = 1024 * 1024 * 16

# Socket Environment
SIOCGIFADDR = 0x8915

# TEXT Color
YELLOW = "\033[93m"
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'
WHITE = '\033[97m'
MAGENTA = '\033[95m'