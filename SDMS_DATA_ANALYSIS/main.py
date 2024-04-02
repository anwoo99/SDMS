from SDMS_DATA_ANALYSIS.config import *
from SDMS_DATA_ANALYSIS.receive_checker import (
    preprocess_receive_checker, receive_checker
)

DA_SOCKETS = []
ALERTER_SOCKETS = []
CONVERTED_DATA_MAP_ALL = {}
RC_DATA_INDEX_MAP = {}

converted_data_map_all_filename = os.path.join(DATA_DICT_DIR, "CONVERTED_DATA_MAP_ALL.pickle")
rc_data_index_map_all_filename = os.path.join(DATA_DICT_DIR, "RC_DATA_INDEX_MAP.pickle")

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
    global CONVERTED_DATA_MAP_ALL
    global RC_DATA_INDEX_MAP
    
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")
    all_socket_close()
    dump_data_to_file(CONVERTED_DATA_MAP_ALL, converted_data_map_all_filename)
    dump_data_to_file(RC_DATA_INDEX_MAP, rc_data_index_map_all_filename)
    exit(1)


def receive_checker_start(alerter_sock, exch_config, recv_config, process):
    formatter = Format(APP_NAME, exch_config, recv_config)

    if formatter.id not in CONVERTED_DATA_MAP_ALL:
        CONVERTED_DATA_MAP_ALL[formatter.id] = {}
        
    if formatter.id not in RC_DATA_INDEX_MAP:
        RC_DATA_INDEX_MAP[formatter.id] = {}

    model_filename = os.path.join(DATA_MODEL_DIR, f"RECV_CHK_MODEL_{formatter.id}.pk1")
    receive_checker_train_data_filename = os.path.join(DATA_NUMP_DIR, f"receive_checker_train_combined_data_{formatter.id}.npy")
    receive_checker_anomly_data_filename = os.path.join(DATA_NUMP_DIR, f"receive_checker_anomly_combined_data_{formatter.id}.npy")
        
    # Create thread for receive_checker
    receive_checker_thread = threading.Thread(target=receive_checker, args=(process, alerter_sock, model_filename, 
                                                                                 receive_checker_train_data_filename, 
                                                                                 receive_checker_anomly_data_filename, 
                                                                                 CONVERTED_DATA_MAP_ALL[formatter.id], 
                                                                                 RC_DATA_INDEX_MAP[formatter.id]))
    # Start the thread
    receive_checker_thread.start()
    

def da_checker_start(exch_config, recv_config, process):
    try:
        global CONVERTED_DATA_MAP_ALL
        global RC_DATA_INDEX_MAP

        alerter_sock = UnixDomainSocket(
            APP_NAME,
            exch_config,
            recv_config,
            UNIX_ALERTER_FLAG
        )

        if alerter_sock is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create alert socket instance")
            raise Exception

        ALERTER_SOCKETS.append(alerter_sock)

        #### THEREAD ####
        receive_checker_start(alerter_sock, exch_config, recv_config, process)
            
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        socket_close(ALERTER_SOCKETS, alerter_sock)
        sys.exit()

def da_start(exch_config, recv_config, process):
    try:
        global CONVERTED_DATA_MAP_ALL

        da_socket = UnixDomainSocket(
            APP_NAME, 
            exch_config, 
            recv_config, 
            UNIX_DA_FLAG)
    
        formatter = Format(APP_NAME, exch_config, recv_config)

        if da_socket is None:
            log(APP_NAME, ERROR, 
                f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create client_socket instance")
            raise Exception

        DA_SOCKETS.append(da_socket)
        
        if formatter.id not in CONVERTED_DATA_MAP_ALL:
            CONVERTED_DATA_MAP_ALL[formatter.id] = {}
        
        while process["Running"] == 1:
            data = da_socket.client_receiver()

            if data is None or len(data) <= 0:
                time.sleep(0.001)
                continue

            preprocess_receive_checker(formatter, data, CONVERTED_DATA_MAP_ALL[formatter.id])

        raise Exception
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        socket_close(DA_SOCKETS, da_socket)
        sys.exit()

def save_data_routine():
    while(True):
        dump_data_to_file(CONVERTED_DATA_MAP_ALL, converted_data_map_all_filename)
        dump_data_to_file(RC_DATA_INDEX_MAP, rc_data_index_map_all_filename)
        time.sleep(1)
    sys.exit()

def main():
    global CONVERTED_DATA_MAP_ALL
    global RC_DATA_INDEX_MAP

    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    try:
        CONVERTED_DATA_MAP_ALL = load_data_from_file(converted_data_map_all_filename) or {}
        RC_DATA_INDEX_MAP = load_data_from_file(rc_data_index_map_all_filename) or {}

        save_thread = threading.Thread(target=save_data_routine, daemon=True)
        save_thread.start()

        check_exchange_process(APP_NAME, [da_start, da_checker_start])

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        dump_data_to_file(CONVERTED_DATA_MAP_ALL, converted_data_map_all_filename)
        dump_data_to_file(RC_DATA_INDEX_MAP, rc_data_index_map_all_filename)
        all_socket_close()

if __name__ == "__main__":
    main()
