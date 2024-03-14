from utils.config import *
from utils.log import log


class MulticastReceiver:
    def __init__(self, app_name, exch_config, recv_config, timeout=10, buffer_size=MAX_BUFFER_SIZE):
        self.app_name = app_name
        self.exch_config = exch_config
        self.recv_config = recv_config
        self.uuid = exch_config["uuid"]
        self.port_name = recv_config["ponm"]
        self.id = f"{exch_config['uuid']}:{recv_config['uuid']}"
        self.interface = self.get_interface_address(recv_config["nic"])
        self.group = recv_config["ip"]
        self.port = recv_config["port"]
        self.desc = recv_config["desc"]
        self.type = recv_config["type"]
        self.format = recv_config["format"]
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.socket = self.create_multicast_socket()

    # interface 명으로부터 address 도출
    def get_interface_address(self, interface):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_address = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                SIOCGIFADDR,
                struct.pack('256s', bytes(interface[:15], 'utf-8'))
            )[20:24])
            return ip_address

        except Exception as err:
            log(self.app_name, ERROR,
                f"ID[{self.id}] Error getting IP address for {interface}: {err}")
            return None

    # 멀티캐스트 소켓 생성
    def create_multicast_socket(self):
        try:
            multicast_socket = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            mreq = struct.pack('4s4s', socket.inet_aton(
                self.group), socket.inet_aton(self.interface))
            multicast_socket.setsockopt(
                socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            multicast_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            multicast_socket.bind(('', int(self.port)))

            # Set the socket timeout
            multicast_socket.settimeout(self.timeout)

            log(self.app_name, MUST, 
                f"ID[{self.id}] Start to receive {self.exch_config['remote_hostname']}:{self.port_name} - {self.group}:{self.port}")
            return multicast_socket

        except Exception as err:
            log(self.app_name, ERROR,
                f"ID[{self.id}] Failed to create multicast socket: {err}")
            raise SocketError(f"ID[{self.id}] Failed to create multicast socket: {err}")

    # 멀티캐스트 데이터 수신
    def receive_data(self):
        try:
            data, addr = self.socket.recvfrom(self.buffer_size)
            self.write_statistic(data, addr)
            return data, addr
        except socket.timeout:
            return None, None
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Failed to receive data: {err}")
            raise

    # 멀티캐스트 소켓 종료
    def close_socket(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            log(self.app_name, MUST, f"ID[{self.id}] Close the socket")

    def write_statistic(self, data, addr):
        pass


class UnixDomainSocket:
    def __init__(self, app_name, exch_config, recv_config, flag, timeout=10):
        self.app_name = app_name
        self.socket = None
        self.id = f"{exch_config['uuid']}:{recv_config['uuid']}"
        self.socket_path = self.create_socket_path(exch_config, recv_config, flag)
        self.connect_success = False
        self.listen_success = False
        self.timeout = timeout
        log(app_name, MUST, f"Create instance for {self.socket_path}")

    def create_server(self):
        try:
            if not self.listen_success:
		# 기존 소켓 파일이 있다면 삭제
                try:
                    os.unlink(self.socket_path)
                except OSError:
                    if os.path.exists(self.socket_path):
                        raise		


                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)                
                self.socket.bind(self.socket_path)
                self.socket.listen(1)

                # Set a timeout for accept operation
                self.socket.settimeout(self.timeout)

                log(self.app_name, MUST, f"ID[{self.id}] Server listening on {self.socket_path}")
                self.listen_success = True
            return True
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Error creating server socket: {err}")
            raise

    def accept_connection(self):
        try:
            connection, client_address = self.socket.accept()
            log(self.app_name, MUST, f"ID[{self.id}] Accepted connection from {client_address}")
            return connection, client_address
        except socket.timeout:
            return None, None
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Error accepting connection: {err}")
            raise SocketError(f"ID[{self.id}] Error creating server socket: {err}")

    def create_client(self):
        try:
            if not self.connect_success:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.socket.connect(self.socket_path)
                log(self.app_name, MUST, f"ID[{self.id}] Connected to server on {self.socket_path}")
                self.connect_success = True
            return True
        except FileNotFoundError:
            self.connect_success = False
            return False
        except ConnectionRefusedError:
            self.connect_success = False
            return False
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Error creating client socket: {err}")
            raise SocketError(f"ID[{self.id}] Error creating client socket: {err}")


    def send_data(self, data):
        try:
            self.socket.sendall(data.encode())
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Error sending data: {err}")
            raise

    def receive_data(self, buffer_size=1024):
        try:
            data = self.socket.recv(buffer_size)
            return data.decode()
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Error receiving data: {err}")
            raise

    def close_socket(self):
        try:
            if self.socket:
                self.socket.close()
                if os.path.exists(self.socket_path):
                    os.remove(self.socket_path)
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Error closing socket: {err}")
            raise
    
    def create_socket_path(self, exch_config, recv_config, flag):
        try:
            return os.path.join(TMP_DIR, f"{flag}_{exch_config['uuid']}_{recv_config['uuid']}")
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Failed to create socket path")
            raise
    
    def client_receiver(self):
        try:
            retv = self.create_client()

            if retv:
                data = self.receive_data()
                return data
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Failed to send data through client")
            raise

    def client_feeder(self, data):
        try:
            retv = self.create_client()

            if retv:
                self.send_data(data)
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Failed to send data through client")
            raise

    def server_receiver(self):
        try:
            retv = self.create_server()

            if retv:
                retv, address = self.accept_connection()

                if retv:
                    data = self.receive_data()
                    return data, address
                
            return None, None
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Failed to receive data through server")
            raise
    
    def server_feeder(self, data):
        try:
            retv = self.create_server()

            if retv:
                retv, address = self.accept_connection()

                if retv:
                    self.send_data(data)
            return None, None
        except Exception as err:
            log(self.app_name, ERROR, f"ID[{self.id}] Failed to send data through server")
            raise

