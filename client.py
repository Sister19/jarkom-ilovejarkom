from lib.connection import *
from lib.segment import Segment
import lib.segment as segment
import sys

class Client:
    def __init__(self, port : int):
        # Init client
        self.conn = Connection("localhost",port)
        print(f"[!] Client started at localhost:{port}")
        self.conn.connect(("localhost",5430))
        pass

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        pass

    def listen_file_transfer(self):
        # File transfer, client-side
        pass


if __name__ == '__main__':
    port = int(sys.argv[1])
    main = Client(port)
    #main.three_way_handshake()
    #main.listen_file_transfer()
    main.conn.sock.close()
