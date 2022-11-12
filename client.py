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

    def listen_file_transfer(self, server_addr: tuple(("ip", "port"))):
        # File transfer, client-side
        self.register_to_server(server_addr)  # still optimistic
        self.three_way_handshake()
        filebody = b""
        data, server_addr = self.conn.listen_single_segment()
        while True:
            seg = Segment().build_from_bytes(bytes_data=data)
            if seg.get_header().flag.value == FIN_FLAG:
                self.conn.close_socket()
                break
            else:
                print(f"[!] [Client] Received 1 segment number {seg.seq_num}.")
                self.conn.send_data(
                    Segment().build(
                        SegmentHeader(seq_num=0, ack_num=seg.seq_num, flag=[ACK_FLAG]),
                        b"",
                    ),
                    server_addr,
                )
                filebody += seg.payload
            data, server_addr = self.conn.listen_single_segment()

        print(filebody)
        print(len(filebody))
        return

    def register_to_server(self, server_addr: tuple(("ip", "port"))):
        print("[!] Registering client to server")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)


if __name__ == "__main__":
    main = Client("127.0.0.1", 3000)
    main.listen_file_transfer(("127.0.0.1", 8080))
