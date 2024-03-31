import os
import sys
import json
import multiprocessing
import time
import signal
import traceback
import pickle
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
from sklearn.externals import joblib

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG, 
    UNIX_DA_FLAG, DATA_MODEL_DIR, UNIX_ALERTER_FLAG,
    RCV_ERROR_CODE
)
from utils.log import log
from utils.socket import (
    MulticastReceiver, UnixDomainSocket
)
from utils.exchanges import check_exchange_process
from utils.format import Format

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]