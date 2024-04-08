import os
import sys
import json
import multiprocessing
import time
import signal
import traceback
import pickle
import joblib
import threading
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from joblib import dump, load

from settings import (
    INSTALLED_APPS,
    MUST, ERROR, PROGRESS, DEBUG, 
    DATA_MODEL_DIR, DATA_DICT_DIR, DATA_NUMP_DIR,
    UNIX_DA_FLAG, UNIX_ALERTER_FLAG,
    RCV_ERROR_CODE
)
from utils.log import log
from utils.socket import (
    MulticastReceiver, UnixDomainSocket
)
from utils.exchanges import check_exchange_process
from utils.format import Format
from utils.file import dump_data_to_file, load_data_from_file

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
APP_INFO = INSTALLED_APPS[APP_NAME]

ISOLATION_FOREST = APP_INFO["receive_checker"]["isolation_forest"]