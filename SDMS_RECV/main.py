from SDMS_RECV.config import *

MULTICAST_RECEIVERS = []
CLIENT_SOCKETS = []

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")
    for multicast in MULTICAST_RECEIVERS:
        multicast.close_socket()
    for client_sock in CLIENT_SOCKETS:
        client_sock.close_socket()
    exit(1)

def recv_start(exch_config, recv_config, process):
    try:
        multicast_receiver = MulticastReceiver(
            APP_NAME,
            exch_config,
            recv_config)
        client_socket = UnixDomainSocket(
            APP_NAME, 
            exch_config, 
            recv_config, 
            UNIX_FEP_FLAG)

        if multicast_receiver is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create multicast receiver instance")
            raise Exception
    
        if client_socket is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create client_socket instance")
            raise Exception

        MULTICAST_RECEIVERS.append(multicast_receiver)
        CLIENT_SOCKETS.append(client_socket)
        
        while process["Running"] == 1:                
            data, addr = multicast_receiver.receive_data()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue

            client_socket.client_feeder(data)
        raise Exception
    except Exception as err:
        if multicast_receiver in MULTICAST_RECEIVERS:
            MULTICAST_RECEIVERS.remove(multicast_receiver)
            multicast_receiver.close_socket()
        if client_socket in CLIENT_SOCKETS:
            CLIENT_SOCKETS.remove(client_socket)
            client_socket.close_socket()
        sys.exit()

def main():
    try:
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

        check_exchange_process(APP_NAME, recv_start)

    except Exception as err:
        for multicast in MULTICAST_RECEIVERS:
            multicast.close_socket()
        for client_sock in CLIENT_SOCKETS:
            client_sock.close_socket()
        
        sys.exit()

if __name__ == "__main__":
    main()
