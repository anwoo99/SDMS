from SDMS_LOGGER.config import *

LOGGER_SOCKETS = []

def socket_close(socklist, sock):
    if sock in socklist:
        socklist.remove(sock)
        sock.close_socket()

def all_socket_close():
    for sock in LOGGER_SOCKETS:
        socket_close(LOGGER_SOCKETS, sock)

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")

    all_socket_close()
    exit(1)   

def logger_start(exch_config, recv_config, process):
    try:
        logger_socket = UnixDomainSocket(
            APP_NAME,
            exch_config,
            recv_config,
            UNIX_LOG_FLAG
        )
        formatter = Format(APP_NAME, exch_config, recv_config)

        if logger_socket is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create logger socket instance")
            raise Exception
        
        LOGGER_SOCKETS.append(logger_socket)

        while process["Running"] == 1:
            data = logger_socket.client_receiver()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue

            formatter.write_csv(data)
        raise Exception
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        
        socket_close(LOGGER_SOCKETS, logger_socket)
        sys.exit()

def main():
    try:
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

        check_exchange_process(APP_NAME, logger_start)

    except Exception as err:        
        sys.exit()

if __name__ == "__main__":
    main()
    