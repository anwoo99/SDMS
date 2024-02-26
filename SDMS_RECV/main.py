from .config import *

def send_to_fep(exch_config, recv_config, data):
    pass

def recv_start(exch_config, recv_config):
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

        while 1:
            data, addr = multicast_receiver.receive_data()

            if len(data) > 0:
                send_to_fep(exch_config, recv_config, data)
            else:
                time.sleep(0.001)

    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

def main():
    try:
        check_exchange_process(recv_start)
    except KeyboardInterrupt:
        sys.exit()

if __name__ == "__main__":
    main()
