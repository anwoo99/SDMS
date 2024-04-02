from SDMS_ALERTER.config import *
from SDMS_ALERTER.device_alerter_server import device_alert_server_start

ALERTER_SOCKETS = []

def socket_close(socklist, sock):
    if sock in socklist:
        socklist.remove(sock)
        sock.close_socket()

def all_socket_close():
    for sock in ALERTER_SOCKETS:
        socket_close(ALERTER_SOCKETS, sock)

def exit_handler(signal, frame):
    log(APP_NAME, MUST, "Received termination signal. Closing all of the socket.")
    all_socket_close()
    exit(1)   

def create_and_append_socket(app_name, exch_config, recv_config, flag, socket_list):
    try:
        sock = UnixDomainSocket(app_name, exch_config, recv_config, flag, 1024 * 1024 * 64)
        sock.create_server()
        socket_list.append(sock)
        return sock
    except Exception as err:
        log(app_name, ERROR, f"ID[{exch_config['uuid']}:{recv_config['uuid']}] Failed to create '{flag}' socket instance: {err}")
        raise

def device_processing(exch_config, recv_config, data):
    try:
        global DEVICE_ALERT_SERVER_QUEUE
        device_data = {
            str(TAG_ERROR_CODE): data["error_code"],
            str(TAG_ERROR_DESC): data["error_desc"],
            str(TAG_ERROR_TIME): data["error_time"],
            str(TAG_ERROR_EXNM): data["exnm"],
            str(TAG_ERROR_PONM): recv_config["ponm"],
            str(TAG_ERROR_HOST_IP): exch_config["remote_hostname"],
            str(TAG_ERROR_MUL_IP): recv_config["ip"],
            str(TAG_ERROR_MUL_PORT): recv_config["port"],
        }
        fix_data = dict_to_fix(SPLIT_CHAR, device_data)

        DEVICE_ALERT_SERVER_QUEUE.put(fix_data.encode())
    except Exception as err:
        raise

def alerter_start(exch_config, recv_config, process):
    try: 
        alerter_socket = create_and_append_socket(APP_NAME, exch_config, recv_config, UNIX_ALERTER_FLAG, ALERTER_SOCKETS)
                   
        while process["Running"] == 1:
            json_data = alerter_socket.server_receiver()

            if json_data is None or len(json_data) <= 0:
                time.sleep(0.001)
                continue

            data = json.loads(json_data.rstrip('\0'))
            
            if "error_code" not in data:
                continue

            # 1. ERROR LOG 기록
            errlog(data)

            # 2. 외부 DEVICE 전달
            device_processing(exch_config, recv_config, data)

            # 3. NaverWorks 메신저 송신

            # 4. ERROR DB 저장

        raise Exception
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)

        socket_close(ALERTER_SOCKETS, alerter_socket)
        sys.exit()

def main():
    try:
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

        # alert_server_start를 별도의 스레드에서 실행
        device_alert_server_thread = threading.Thread(target=asyncio.run, args=(device_alert_server_start(),), daemon=True)
        device_alert_server_thread.start()

        check_exchange_process(APP_NAME, [alerter_start])

    except Exception as err:    
        all_socket_close()    
        sys.exit()

if __name__ == "__main__":
    main()
