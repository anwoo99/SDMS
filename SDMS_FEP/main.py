from SDMS_RECV.config import *

SERVER_SOCKETS = []

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")

    for server_sock in SERVER_SOCKETS:
        server_sock.close_socket()
    exit(1)   

def fep_start(exch_config, recv_config, process):
    try:
        server_socket = UnixDomainSocket(
            APP_NAME, 
            exch_config, 
            recv_config, 
            UNIX_FEP_FLAG)
        
        if server_socket is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create server_socket instance")
            raise Exception

        server_socket.create_server()
        SERVER_SOCKETS.append(server_socket)

        while process["Running"] == 1:
            data, addr = server_socket.server_receiver()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue
            
            # 데이터 Validation

            # 데이터 전송 to processes

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
