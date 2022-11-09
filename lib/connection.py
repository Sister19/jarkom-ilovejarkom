from socket import *
from time import *

from .segment import Segment

BUFFER_SIZE = 32768


class Connection:
    def __init__(self, ip: str, port: int):
        # Init UDP socket
        self.ip = ip
        self.port = port
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((ip, port))

    def send_data(self, msg: Segment, dest: tuple):
        # Send single segment into destination
        self.sock.sendto(msg.get_bytes(), dest)

    def listen_single_segment(self, timeout=3600) -> Segment:
        # Listen single UDP datagram within timeout and convert into segment
        past = time()
        print("Listening on port " + str(self.port))
        while True:
            print(time() - past)
            data, address = self.sock.recvfrom(BUFFER_SIZE)
            if data:
                print(">>" * 50)
                print("Recieved data from: " + str(address))
                seg = Segment()
                seg.set_from_bytes(data)
                print(seg)
                print(len(seg.get_bytes()))
                print(">>" * 50)

            if (time() - past) < timeout:
                break

    def close_socket(self):
        # Release UDP socket
        self.sock.close()
