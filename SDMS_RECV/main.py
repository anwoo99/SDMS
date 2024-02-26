from .config import *

MULTICAST_RECEIVERS = []
CLIENT_SOCKETS = []

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing Unix domain socket.")
    for multicast in MULTICAST_RECEIVERS:
        multicast.close_socket()
    for client_sock in CLIENT_SOCKETS:
        client_sock.close_socket()


def recv_start(exch_config, recv_config):
    try:
        retv = False
        multicast_receiver = MulticastReceiver(
            APP_NAME,
            exch_config,
            recv_config)

        MULTICAST_RECEIVERS.append(multicast_receiver)

        while 1:
            if not retv:
                client_socket = UnixDomainSocket(APP_NAME, exch_config, recv_config, UNIX_FEP_FLAG)
                retv = client_socket.create_client()
                
                if retv:
                    CLIENT_SOCKETS.append(client_socket)
                    
            data, addr = multicast_receiver.receive_data()

            if len(data) > 0 and retv:
                client_socket.send_data(data)
            else:
                time.sleep(0.001)

    except Exception as err:
        if multicast_receiver:
            MULTICAST_RECEIVERS.remove(multicast_receiver)
            multicast_receiver.close_socket()
        if client_socket:
            CLIENT_SOCKETS.remove(client_socket)
            client_socket.close_socket()

        log(APP_NAME, ERROR, err)
        sys.exit()

def main():
    try:
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)
        check_exchange_process(recv_start)
    except Exception as err:
        sys.exit()

if __name__ == "__main__":
    main()
