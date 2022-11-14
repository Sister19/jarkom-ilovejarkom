from lib.connection import *
from lib.segment import *


class Client:
    def __init__(self, ip, port):
        # Init client
        self.ip = ip
        self.port = port
        self.conn = Connection(ip, port)

    def three_way_handshake(self, server_addr):
        # Three Way Handshake, client-side
        print("[Handshake] Starting handshake to server")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)

        # Waiting SYN-ACK from server
        syn, server_addr = self.conn.listen_single_segment()
        seg = Segment().build_from_bytes(bytes_data=syn)
        if seg.get_header().flag.value != SYN_ACK:
            print("[!] Wrong flag recieved from server, aborting...")
            return False

        print("[Handshake] Received SYN ACK from server")
        print("[Handshake] Sending ACK to server...")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[ACK_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)

        return True

    def listen_file_transfer(self, server_addr: tuple(("ip", "port"))):
        # File transfer, client-side
        filebody = b""
        segment_num = 1
        #data, server_addr = self.conn.listen_single_segment() #ADA TRY CATCH NYA ? SEMISAL CHECKSUM DI LISTEN SINGLE ELEMENT GAGAL
        while True:
            try :
                data, server_addr = self.conn.listen_single_segment()
                seg = Segment().build_from_bytes(bytes_data=data)
                if seg.get_header().flag.value == FIN_FLAG:
                    head = SegmentHeader(seq_num=0, ack_num=0, flag=[ACK_FLAG])
                    self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)
                    self.conn.close_socket()
                    break
                elif segment_num == seg.seq_num :
                    print(f"[!] [Client] Received 1 segment number {seg.seq_num}.")
                    self.conn.send_data(
                        Segment().build(
                            SegmentHeader(seq_num=0, ack_num=seg.seq_num, flag=[ACK_FLAG]),
                            b"",
                        ),
                        server_addr,
                    )
                    segment_num += 1
                    filebody += seg.payload
            except Exception as e :
                #kalau checksum gagal ato timeout
                print(e)
                
            
            # data, server_addr = self.conn.listen_single_segment()
            # seg = Segment().build_from_bytes(bytes_data=data)

        # print(filebody)
        #print(len(filebody))

        return


if __name__ == "__main__":
    main = Client("127.0.0.1", 3000)
    main.three_way_handshake(("127.0.0.1", 8080))
    main.listen_file_transfer(("127.0.0.1", 8080))
