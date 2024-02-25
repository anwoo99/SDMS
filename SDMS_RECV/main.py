from .config import *
from utils.file import (
    read_json_file
)
from utils.socket import (
    MulticastReceiver
)

def send_to_fep(exch_config, recv_config, data):
    pass

def recv_start(exch_config, recv_config, stop_event):
    try:
        multicast_receiver = MulticastReceiver(
            APP_NAME,
            exch_config["uuid"],
            recv_config["ponm"],
            recv_config["interface"],
            recv_config["ip"],
            recv_config["port"],
            recv_config["desc"],
            recv_config["type"],
            recv_config["format"])

        while not stop_event.is_set():
            data, addr = multicast_receiver.receive_data()

            if len(data) > 0:
                send_to_fep(exch_config, recv_config, data)
            else:
                time.sleep(SLEEP_TIME)

    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

def main():
    try:
        exch_json_data = read_json_file(EXCHANGE_CONFIG_PATH)
        threads = []
        stop_event = threading.Event()

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
                thread = threading.Thread(
                    target=recv_start, args=(exch_config, recv_config, stop_event,))
                threads.append(thread)

        for th in threads:
            th.start()

        for th in threads:
            th.join()

    except Exception as err:
        log(APP_NAME, ERROR, err)
        stop_event.set()
        sys.exit()

if __name__ == "__main__":
    main()
