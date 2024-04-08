from SDMS_DATA_ANALYSIS.config import *
from SDMS_DATA_ANALYSIS.receive_checker import (
    preprocess_receive_checker, receive_checker
)

DA_SOCKETS = []
ALERTER_SOCKETS = []
RC_CONV_DATA_LIST = []

def socket_close(socklist, sock):
    if sock in socklist:
        socklist.remove(sock)
        sock.close_socket()

def all_socket_close():
    for sock in DA_SOCKETS:
        socket_close(DA_SOCKETS, sock)
    
    for sock in ALERTER_SOCKETS:
        socket_close(ALERTER_SOCKETS, sock)

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")
    all_socket_close()

    for rc_conv_data_attr in RC_CONV_DATA_LIST:
        dump_data_to_file(rc_conv_data_attr["data"], rc_conv_data_attr["filename"])

    exit(1)


def receive_checker_start(process, alerter_sock, formatter, rc_conv_data_attr):        
    # Create thread for receive_checker
    receive_checker_thread = threading.Thread(target=receive_checker, args=(process, alerter_sock, formatter, rc_conv_data_attr))

    # Start the thread
    receive_checker_thread.start()
    return receive_checker_thread


def da_start(exch_config, recv_config, process):
    try:
        da_socket = UnixDomainSocket(
            APP_NAME, 
            exch_config, 
            recv_config, 
            UNIX_DA_FLAG)
        
        alerter_sock = UnixDomainSocket(
            APP_NAME,
            exch_config,
            recv_config,
            UNIX_ALERTER_FLAG
        )
    
        formatter = Format(APP_NAME, exch_config, recv_config)

        if da_socket is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create client_socket instance")
            raise Exception
    
        if alerter_sock is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create alert socket instance")
            raise Exception

        DA_SOCKETS.append(da_socket)
        ALERTER_SOCKETS.append(alerter_sock)

        rc_conv_data_filename = os.path.join(DATA_DICT_DIR, f"RC_CONV_DATA_MAP_{formatter.id}.pickle")
        rc_conv_data_map = load_data_from_file(rc_conv_data_filename) or {}
        rc_conv_data_attr = {
            "filename" : rc_conv_data_filename,
            "data": rc_conv_data_map
        }

        RC_CONV_DATA_LIST.append(rc_conv_data_attr)

        #### THEREAD ####
        receive_checker_thread = receive_checker_start(process, alerter_sock, formatter, rc_conv_data_attr)
        #################
        
        while process["Running"] == 1:
            data = da_socket.client_receiver()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue

            preprocess_receive_checker(formatter, data, rc_conv_data_attr, receive_checker_thread)
        raise Exception
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        socket_close(DA_SOCKETS, da_socket)
        dump_data_to_file(rc_conv_data_map, rc_conv_data_filename)
        sys.exit()


def main():
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    try:
        check_exchange_process(APP_NAME, [da_start])

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        all_socket_close()

if __name__ == "__main__":
    main()
