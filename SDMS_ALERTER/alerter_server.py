from SDMS_ALERTER.config import *

async def handle_client_connection(app_name, client_socket, logined_sockets):
    try:
        while True:
            data = await asyncio.wait_for(client_socket.recv(1024 * 1024 * 16), timeout=5)
            if not data:
                log(app_name, MUST, f"Closing connection with {client_socket.getpeername()}")
                client_socket.close()
                logined_sockets.discard(client_socket)
                return

            fix_data = parse_fix_message(SPLIT_CHAR, data)
            login_id = fix_data[TAG_LOGIN_ID]
            login_pw = fix_data[TAG_LOGIN_PW]

            for login_info in LOGIN_LIST:
                if login_info["id"] == login_id and login_info["pw"] == login_pw:
                    logined_sockets.add(client_socket)
                    break

    except asyncio.TimeoutError:
        pass
    except Exception as err:
        log(app_name, ERROR, f"Error handling client connection: {err}")
        client_socket.close()
        logined_sockets.discard(client_socket)

async def alert_server_start(app_name, logined_sockets):
    try:
        ip_address, port = APP_INFO["address"]["ip"], APP_INFO["address"]["port"]
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip_address, port))
        server_socket.listen()
        log(app_name, MUST, f"Server started on {ip_address}:{port}")

        while True:
            client_socket, client_address = await asyncio.wait_for(server_socket.accept(), timeout=5)
            log(app_name, MUST, f"Accepted connection from {client_address}")
            asyncio.create_task(handle_client_connection(app_name, client_socket, logined_sockets))

    except asyncio.TimeoutError:
        pass
    except Exception as err:
        log(app_name, ERROR, f"Error starting server: {err}")
        server_socket.close()
        for sock in logined_sockets:
            sock.close()
        logined_sockets.clear()