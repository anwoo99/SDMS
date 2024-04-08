# 모듈 가져오기
from utils.config import *
from utils.file import read_json_file
from utils.log import log
from utils.functions import check_function_signature

# 전역 변수: 거래소 프로세스 테이블
PROC_EXCH_TABLE = []

# 거래소 환경 설정 검증 함수
def validate_exchange_config(app_name):
    try:
        # 거래소 환경 설정 파일 읽기
        exch_json_data = read_json_file(EXCHANGE_CONFIG_PATH)

        if not exch_json_data:
            return False, f"Cannot read {EXCHANGE_CONFIG_PATH} file"

        used_config_uuids = set()

        for exchange in exch_json_data:
            # 거래소 환경 설정(config) 검증
            config = exchange.get("config")
            if not config:
                log(app_name, ERROR, "Invalid environment configuration: Missing 'config' field.")
                return False, None

            # uuid 고유성 검증
            uuid = config.get("uuid")
            if uuid in used_config_uuids:
                log(app_name, ERROR, f"Invalid environment configuration: Duplicate uuid '{uuid}'.")
                return False, None

            used_config_uuids.add(uuid)

            # 수신 설정(recv) 검증
            recv_list = exchange.get("recv")
            if not recv_list:
                log(app_name, ERROR, "Invalid environment configuration: Missing 'recv' field.")
                return False, None

            used_recv_uuids = set()

            # 거래소 발송 IP/PORT(config) 검증
            for recv in recv_list:
                # uuid 고유성 검증
                recv_uuid = recv.get("uuid")
                if recv_uuid in used_recv_uuids:
                    log(app_name, ERROR, f"Invalid environment configuration: Duplicate uuid '{recv_uuid}'.")
                    return False, None
                used_recv_uuids.add(recv_uuid)

        return True, exch_json_data
    except Exception as err:
        raise Exception(f"Failed to validate {EXCHANGE_CONFIG_PATH} file")

# 프로세스 테이블에서 특정 거래소 프로세스 찾기
def find_process(exch_uuid, recv_uuid, function):
    global PROC_EXCH_TABLE

    for process in PROC_EXCH_TABLE:
        if process["exch_uuid"] == exch_uuid and process["recv_uuid"] == recv_uuid and process["function"] == function.__name__:
            return process
    return None

# 거래소 프로세스 실행 함수
def run_exchange_process(app_name, exch_config, recv_config, function):
    try:
        global PROC_EXCH_TABLE
        process = find_process(exch_config["uuid"], recv_config["uuid"], function)

        if process and "Thread" in process and process["Thread"] and not process["Thread"].is_alive():
            try:
                log(app_name, MUST, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Start to run '{function.__name__}'...")
                process["Thread"].start()
            except Exception:
                log(app_name, MUST, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Fail to run '{function.__name__}'.")

        if process is None or process["Running"] == 0:
            process = {
                "Running": 1,
                "function": function.__name__,
                "exch_uuid": exch_config["uuid"],
                "recv_uuid": recv_config["uuid"],
                "Thread": None
            }

            thread = threading.Thread(
                target=function, args=(exch_config, recv_config, process), daemon=True)
            
            process["Thread"] = thread
            PROC_EXCH_TABLE.append(process)
            thread.start()
            
            if not thread.is_alive():
                log(app_name, ERROR, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to run '{function.__name__}'")
                PROC_EXCH_TABLE.remove(process)
                return
            
            log(app_name, MUST, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Start to run '{function.__name__}'")
    except Exception as err:
        raise Exception(
            f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to run '{function.__name__}'")


# 거래소 프로세스 종료 함수
def kill_exchange_process(app_name, exch_config, recv_config, function):
    try:
        global PROC_EXCH_TABLE
        process = find_process(exch_config["uuid"], recv_config["uuid"], function)

        if process is not None and process["Running"] == 1:
            process["Running"] = 0

            # Wait for the thread to finish
            process["Thread"].join()

            # Remove it from the list
            PROC_EXCH_TABLE.remove(process)
            log(app_name, MUST, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Kill '{function.__name__}'")
    except Exception as err:
        raise Exception(
            f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to kill '{function.__name__}'")

# 거래소 프로세스 상태 확인 함수
def check_exchange_process(app_name, function_list):
    try:
        # 함수 시그니처 검증(반드시 exch_config, recv_config가 인자값으로 있어야 함.)
        check_function_signature(function_list, ['exch_config', 'recv_config', 'process'])

        while True:
            flag, exch_json_data = validate_exchange_config(app_name)

            if flag is False:
                time.sleep(1)
                continue

            for exchange in exch_json_data:
                exit_flag = 0
                exch_config = {}

                for key, value in exchange.items():
                    if key == "config":
                        exch_config = value
                        if exch_config["Running"] == 1:
                            exit_flag = 0
                        else:
                            exit_flag = 1
                    elif key == "recv":
                        for recv_config in value:
                            if recv_config["Running"] == 1 and exit_flag == 0:
                                for function in function_list:
                                    run_exchange_process(
                                        app_name, exch_config, recv_config, function)
                            else:
                                for function in function_list:
                                    kill_exchange_process(
                                        app_name, exch_config, recv_config, function)
            time.sleep(1)
    except Exception as err:
        raise Exception(f"Failed to check exchange process: {err}")
