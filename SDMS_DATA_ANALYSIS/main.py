from SDMS_DATA_ANALYSIS.config import *

DA_SOCKETS = []

def socket_close(socklist, sock):
    if sock in socklist:
        socklist.remove(sock)
        sock.close_socket()

def all_socket_close():
    for sock in DA_SOCKETS:
        socket_close(DA_SOCKETS, sock)

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")
    all_socket_close()
    exit(1)

def recv_start(exch_config, recv_config, process):
    try:
        da_socket = UnixDomainSocket(
            APP_NAME, 
            exch_config, 
            recv_config, 
            UNIX_DA_FLAG)
    
        if da_socket is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create client_socket instance")
            raise Exception

        DA_SOCKETS.append(da_socket)
        
        while process["Running"] == 1:
            data = da_socket.client_receiver()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue

        raise Exception
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        socket_close(DA_SOCKETS, da_socket)
        sys.exit()

def main():
    try:
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

        check_exchange_process(APP_NAME, recv_start)

    except Exception as err:   
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)

        all_socket_close()
        sys.exit()

if __name__ == "__main__":
    main()
