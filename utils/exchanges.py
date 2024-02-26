from .config import *
from .file import read_json_file

PROC_EXCH_TABLE = []

def validate_exchange_config():
    try:
        exch_json_data = read_json_file(EXCHANGE_CONFIG_PATH)

        if not exch_json_data:
            return False, f"Cannot read {EXCHANGE_CONFIG_PATH} file"

        used_config_uuids = set()

        for exchange in exch_json_data:
            # 거래소 환경 설정(config) 검증
            config = exchange.get("config")
            if not config:
                return False, "Invalid environment configuration: Missing 'config' field."

            # uuid 고유성 검증
            uuid = config.get("uuid")
            if uuid in used_config_uuids:
                return False, f"Invalid environment configuration: Duplicate uuid '{uuid}'."
            used_config_uuids.add(uuid)

            # 수신 설정(recv) 검증
            recv_list = exchange.get("recv")
            if not recv_list:
                return False, "Invalid environment configuration: Missing 'recv' field."

            used_recv_uuids = set()

            # 거래소 발송 IP/PORT(config) 검증
            for recv in recv_list:
                # uuid 고유성 검증
                recv_uuid = recv.get("uuid")
                if recv_uuid in used_recv_uuids:
                    return False, f"Invalid environment configuration: Duplicate uuid '{recv_uuid}'."
                used_recv_uuids.add(recv_uuid)

        return True, exch_json_data
    except Exception as err:
        raise Exception(f"Failed to validate {EXCHANGE_CONFIG_PATH} file")

def run_exchange_process(exch_config, recv_config, function):
    global PROC_EXCH_TABLE
    process = None

    for attr in PROC_EXCH_TABLE:
        if attr["exch_uuid"] == exch_config["uuid"] and attr["recv_uuid"] == recv_config["uuid"]:
            process = attr
            break

    if process is None or process["Running"] == 0:
        proc = multiprocessing.Process(target=function, args=(exch_config, recv_config, ))
        process["Running"] = 1
        process["exch_uuid"] = exch_config["uuid"]
        process["recv_uuid"] = recv_config["uuid"]
        process["Process"] = proc
        PROC_EXCH_TABLE.append(process)

def kill_exchange_process(exch_uuid, recv_uuid, function):
    pass

def check_exchange_process(function):
    try:
        while(1):
            flag, exch_json_data = validate_exchange_config()

            if flag is False:
                raise Exception

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
                                run_exchange_process(exch_config, recv_config, function)
                            else:
                                kill_exchange_process(exch_config, recv_config, function)
            time.sleep(1)
    except Exception as err:
        raise Exception("Failed to check exchange process")
