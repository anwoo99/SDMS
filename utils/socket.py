from .config import *

class MulticastReceiver:
    def __init__(self, app_name, uuid, port_name, interface, 
                 group, port, desc, type, format, buffer_size=MAX_BUFFER_SIZE):
        self.app_name = app_name
        self.uuid = uuid
        self.port_name = port_name
        self.interface = self.get_interface_address(interface)
        self.group = group
        self.port = port
        self.desc = desc
        self.type = type
        self.format = format
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
            log(self.app_name, ERROR, f"Error getting IP address for {interface}: {err}")
            return None

    # 멀티캐스트 소켓 생성
    def create_multicast_socket(self):
        try:
            multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            mreq = struct.pack('4s4s', socket.inet_aton(self.group), socket.inet_aton(self.interface))
            multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            multicast_socket.bind(('', self.port))
            return multicast_socket

        except Exception as err:
            log(self.app_name, ERROR, f"Failed to create multicast socket: {err}")
            return None
    
    # 멀티캐스트 데이터 수신
    def receive_data(self):
        try:
            data, addr = self.socket.recvfrom(self.buffer_size)
            return data, addr

        except Exception as err:
            log(self.app_name, ERROR, f"Failed to receive data: {err}")
            raise  # 예외를 다시 발생시켜 호출자에게 전달

    # 멀티캐스트 소켓 종료
    def close_socket(self):
        if self.socket:
            self.socket.close()