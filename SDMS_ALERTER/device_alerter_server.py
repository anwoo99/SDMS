from SDMS_ALERTER.config import *

async def handle_client_connection(reader, writer):
    try:
        client_address = writer.get_extra_info('peername')
        log(APP_NAME, MUST, f"Accepted connection from {client_address}")

        if reader is None or writer is None:
            reader, writer = await asyncio.open_connection(sock=writer)

        data = await asyncio.wait_for(reader.read(1024 * 1024 * 16), timeout=30)

        if not data:
            log(APP_NAME, MUST, f"Closing connection with {client_address}")
            writer.close()
            return

        fix_data = parse_fix_message(SPLIT_CHAR, data.decode())
        login_id = fix_data[TAG_LOGIN_ID]
        login_pw = fix_data[TAG_LOGIN_PW]

        login_success = False
        for login_info in LOGIN_LIST:
            if login_info["id"] == login_id and login_info["pw"] == login_pw:
                LOGIN_SUCCESS_DICT = {
                    str(TAG_LOGIN_ID): login_id,
                    str(TAG_LOGIN_PW): login_pw,
                    str(TAG_LOGIN_AUTH): DATA_OK_AUTH
                }
                LOGIN_SUCCESS_MESSAGE = dict_to_fix(SPLIT_CHAR, LOGIN_SUCCESS_DICT)
                writer.write(LOGIN_SUCCESS_MESSAGE.encode())
                await writer.drain()
                login_success = True
                break

        if not login_success:
            LOGIN_FAIL_DICT = {
                str(TAG_LOGIN_ID): login_id,
                str(TAG_LOGIN_PW): login_pw,
                str(TAG_LOGIN_AUTH): DATA_NO_AUTH
            }
            LOGIN_FAIL_MESSAGE = dict_to_fix(SPLIT_CHAR, LOGIN_FAIL_DICT)
            writer.write(LOGIN_FAIL_MESSAGE.encode())
            await writer.drain()
            return  # 로그인 실패 시 연결 종료
            
        once = True
        
        # 로그인 성공한 클라이언트에게만 메시지 전송 처리
        while not writer.transport.is_closing():

            # THIS IS TEST
            if once:
                once = False
                await writer.drain()
                alert_message = "1=001\0012=recieve_error\0013=20240402173636\0014=HANYANG\0015=SOOSINPORT\0016=111.111.111.111 >\0017=222.222.222.222\0018=4885"
                writer.write(alert_message.encode())
                
            await asyncio.sleep(0)  # 다른 task에 제어를 양보하여 비동기적으로 queue를 관찰
            if not DEVICE_ALERT_SERVER_QUEUE.empty():
                await writer.drain()
                alert_message = await DEVICE_ALERT_SERVER_QUEUE.get()
                writer.write(alert_message.encode())

        log(APP_NAME, MUST, f"Closing connection with {client_address}")
        writer.close()

    except asyncio.TimeoutError:
        log(APP_NAME, MUST, f"Closing connection with {client_address} due to login timeout")
        TIMEOUT_DICT = {
            str(TAG_TIMEOUT): 1,
        }
        TIMEOUT_MESSAGE = dict_to_fix(SPLIT_CHAR, TIMEOUT_DICT)
        writer.write(TIMEOUT_MESSAGE.encode())
        await writer.drain()
        writer.close()
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, f"Error handling client connection: {traceback_error}")
        writer.close()

async def device_alert_server_start():
    try:
        ip_address, port = APP_INFO["address"]["ip"], APP_INFO["address"]["port"]
        
        server = await asyncio.start_server(handle_client_connection, host=ip_address, port=port)
        
        async with server:
            log(APP_NAME, MUST, f"Server started on {ip_address}:{port}")
            await server.serve_forever()

    except Exception as err:
        log(APP_NAME, ERROR, f"Error starting server: {err}")