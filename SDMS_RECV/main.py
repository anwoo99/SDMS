from .config import *
from utils.file import (
    read_json_file
)

def recv_start(exch_config, recv_config):
    try:
        nic = recv_config["nic"]
        ip = recv_config["ip"]
        port = recv_config["port"]
    except Exception as err:
        log(APP_NAME, ERROR, err)
        

def main():
    try:
        exch_json_data = read_json_file(EXCHANGE_CONFIG_PATH)
        threads = []

        for exchange in exch_json_data:
            exch_config = {}
            recv_configs = []

            for key, value in exchange.items():
                if key == "config":
                    if value["Running"] != 1:
                        break
                    exch_config = value
                elif key == "recv":
                    for recv in value:
                        if recv["Running"] == 1:
                            recv_configs.append(recv)

            for recv_config in recv_configs:
                thread = threading.Thread(target=recv_start, args=(exch_config, recv_config,))
                threads.append(thread)

        for th in threads:
            th.start()

        for th in threads:
            th.join()

    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

if __name__ == "__main__":
    main()