#############################################################
# 해당 파일은 당사의 중요 정보가 포함되어 있는 파일이므로
# 보안에 각별한 주의 바랍니다.
#############################################################

import os

# 파이썬 실행 버전
PYTHON = "python3.10"

# 프로그램 쿼리 FLAG
RUN_FLAG = "aADWALKDMKALWMAAAadwaad"
EXIT_FLAG = "qwerfghadlwakldmqeqwdadsdawqdqwd"
CHK_FLAG = "alllwdqsamlobxsklzcnlqop12"
END_FLAG = "ADALMWKDawndkalas0pAqqwe"

#############
# 로그 레벨
#############
DEBUG = "DEBUG"
PROGRESS = "PROGRESS"
ERROR = "ERROR"
MUST = "MUST"

LOG_LEVEL_MAP = {
    MUST: 3,
    ERROR: 2,
    PROGRESS: 1,
    DEBUG: 0
}

#############################
# 현재 생성한 앱의 환경 설정
#############################
RUNNING_MODE = "PROD"
# RUNNING_MODE = "TEST"

INSTALLED_APPS = {
    'SDMS_RECV': {
        "Running": True,
        "LOG_LEVEL": PROGRESS
    },
    'SDMS_FEP': {
        "Running": True,
        "LOG_LEVEL": PROGRESS
    },
    'SDMS_LOGGER': {
        "Running": True,
        "LOG_LEVEL": PROGRESS
    },
    'SDMS_DATA_ANALYSIS': {
        "Running": False,
        "LOG_LEVEL": PROGRESS,
        "receive_checker": {
            "classification": 5
        }
    },
    'SDMS_HTS': {
        "Running": False,
        "LOG_LEVEL": PROGRESS
    },
    'SDMS_DB': {
        "Running": False,
        "LOG_LEVEL": PROGRESS
    },
    'SDMS_ALERTER': {
        "Running": False,
        "LOG_LEVEL": PROGRESS,
        "address": {
            "ip": "61.78.34.111",
            "port": 41155
        },
        "LOGIN": [
            {
                "id": "SDMS_001",
                "pw": "sdms_001"
            }
        ]
    }
}

#############
# PATH 설정
#############
# 기본 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Log Directory
LOG_DIR = os.path.join(BASE_DIR, "log")
RAW_LOG_DIR = os.path.join(LOG_DIR, "raw")

# Config Directory
CONFIG_DIR = os.path.join(BASE_DIR, "config")
EXCHANGE_CONFIG_PATH = os.path.join(CONFIG_DIR, "exchanges.json")

# TMP Directory
TMP_DIR = os.path.join(BASE_DIR, "tmp")

# DATA Directory
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_MODEL_DIR = os.path.join(DATA_DIR, "model")

# MAIN PIPE
MAIN_PIPE = os.path.join(TMP_DIR, "MAIN_PIPE")
MAIN_PIPE2 = os.path.join(TMP_DIR, "MAIN_PIPE2")

##########################
# Unix Domain Socket Flag
##########################
UNIX_FEP_FLAG = "FEP"
UNIX_LOG_FLAG = "LOG"
UNIX_DA_FLAG = "DA"
UNIX_ALERTER_FLAG = "ALERTER"

#############
# ERROR CODE
#############
RCV_ERROR_CODE = {
    "code": "001",
    "desc": "Receive Error: "
}
PRICE_ERROR_CODE = {
    "code": "002",
    "desc": "Price Error: "
}

