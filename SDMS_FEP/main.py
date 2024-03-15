from SDMS_FEP.config import *

SERVER_SOCKETS = []
LOGGER_SOCKETS = []
DA_SOCKETS = []

def socket_close(socklist, sock):
    if sock in socklist:
        socklist.remove(sock)
        sock.close_socket()

def all_socket_close():
    for sock in SERVER_SOCKETS:
        socket_close(SERVER_SOCKETS, sock)

    for sock in LOGGER_SOCKETS:
        socket_close(LOGGER_SOCKETS, sock)

    for sock in DA_SOCKETS:
        socket_close(DA_SOCKETS, sock)

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")
    all_socket_close()
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
            data = server_socket.server_receiver()
            print(data)

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue
            
            # 데이터 Validation
            is_valid, reason = formatter.validation(data)

            # 데이터 전송 to processes
            logger_socket.server_feeder(data)

            if is_valid:
                da_socket.server_feeder(data)
            else:
                pass # 에러 사항 Alert

        raise Exception
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)

        socket_close(SERVER_SOCKETS, server_socket)
        socket_close(LOGGER_SOCKETS, logger_socket)
        socket_close(DA_SOCKETS, da_socket)
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
