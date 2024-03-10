from SDMS_FEP.config import *

SERVER_SOCKETS = []
LOGGER_SOCKETS = []
DA_SOCKETS = []

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")

    for server_sock in SERVER_SOCKETS:
        server_sock.close_socket()
    exit(1)   

def create_and_append_socket(app_name, exch_config, recv_config, flag, socket_list):
    try:
        sock = UnixDomainSocket(app_name, exch_config, recv_config, flag)
        sock.create_server()
        socket_list.append(sock)
        return sock
    except Exception as err:
        log(app_name, ERROR, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create '{flag}' socket instance: {err}")
        raise

def fep_start(exch_config, recv_config, process):
    try:
        server_socket = create_and_append_socket(APP_NAME, exch_config, recv_config, UNIX_FEP_FLAG, SERVER_SOCKETS)
        logger_socket = create_and_append_socket(APP_NAME, exch_config, recv_config, UNIX_LOG_FLAG, LOGGER_SOCKETS)
        da_socket = create_and_append_socket(APP_NAME, exch_config, recv_config, UNIX_DA_FLAG, DA_SOCKETS)
        formatter = Format(APP_NAME, exch_config, recv_config)

        while process["Running"] == 1:
            is_valid = False
            data, addr = server_socket.server_receiver()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue
            
            # 데이터 Validation
            is_valid = formatter.validation(data)

            # 데이터 전송 to processes
            logger_socket.client_feeder(data)

            if is_valid:
                da_socket.client_feeder(data)

        raise Exception
    except Exception as err:
        if server_socket in SERVER_SOCKETS:
            SERVER_SOCKETS.remove(server_socket)
            server_socket.close_socket()
        sys.exit()

def main():
    try:
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

        check_exchange_process(APP_NAME, fep_start)

    except Exception as err:        
        sys.exit()

if __name__ == "__main__":
    main()
