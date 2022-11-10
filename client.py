from lib.connection import *
from lib.segment import *


class Client:
    def __init__(self, ip, port):
        # Init client
        self.ip = ip
        self.port = port
        self.conn = Connection(ip, port)

    def three_way_handshake(self):
        # Three Way Handshake, client-side
        print("[!] Waiting for server...")
        syn, server_addr = self.conn.listen_single_segment()

        syn_seg = Segment().build_from_bytes(bytes_data=syn)
        if syn_seg.get_header().flag.value != SYN_FLAG:
            print("[!] Wrong flag recieved from server, aborting...")
            return False

        print("[Handshake] Received SYN FLAG from server")
        print("[Handshake] Sending SYN ACK to server...")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG, ACK_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)

        return True

    def listen_file_transfer(self):
        # File transfer, client-side
        pass


if __name__ == "__main__":
    main = Client("127.0.0.1", 3000)
    main.three_way_handshake()
    # main.listen_file_transfer()
