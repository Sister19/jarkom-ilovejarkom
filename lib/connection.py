from socket import *
from time import *

from .segment import Segment

BUFFER_SIZE = 32768


class Connection:
    def __init__(self, ip: str, port: int):
        # Init UDP socket
        self.ip = ip
        self.port = port
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((ip, port))

    def send_data(self, msg: Segment, dest: tuple(("ip", "port"))):
        # Send single segment into destination
        self.sock.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self, timeout: int = 3600) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        self.sock.settimeout(timeout)
        try:
            while True:
                data, address = self.sock.recvfrom(BUFFER_SIZE)
                if data:
                    seg = Segment()
                    seg.set_from_bytes(data)

                    print("=" * 50)
                    print("Recieved data from " + f"{address[0]}:{address[1]}")
                    print(seg)
                    print("=" * 50)
                    break

            return data, address
        except Exception as e:
            raise e

    def close_socket(self):
        # Release UDP socket
        self.sock.close()
