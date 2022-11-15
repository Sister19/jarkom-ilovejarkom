from lib.connection import *
from lib.segment import *
import os
import argparse


class Client:
    def __init__(self, ip, port):
        # Init client
        self.ip = ip
        self.port = port
        self.conn = Connection(ip, port)

    def three_way_handshake(self, server_addr):
        # Three Way Handshake, client-side
        print("[!] [Handshake] Initiating three way handshake...")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)

        # Waiting SYN-ACK from server
        syn, server_addr = self.conn.listen_single_segment()
        seg = Segment().build_from_bytes(bytes_data=syn)
        if seg.get_header().flag.value != SYN_ACK:
            print("[!] Wrong flag received from server, aborting...")
            return False

        print("[!] [Handshake] Received SYN ACK from server")
        print("[!] [Handshake] Sending ACK to server...")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[ACK_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)

        return True

    def listen_file_transfer(self, server_addr: tuple(("ip", "port"))):
        # File transfer, client-side
        filebody = b""
        segment_num = 1
        filename = "client_files/result.txt" # DEFAULT
        #data, server_addr = self.conn.listen_single_segment() #ADA TRY CATCH NYA ? SEMISAL CHECKSUM DI LISTEN SINGLE ELEMENT GAGAL

        # RECEIVE METADATA
        try:
            data, server_addr = self.conn.listen_single_segment(5)
            seg = Segment().build_from_bytes(bytes_data=data)
            print(f"[!] [Client] [Metadata] Received Metadata")
            path = seg.payload.decode("utf-8")
            filename = os.path.basename(path)
            filename = "client_files/" + filename
            self.conn.send_data(
                Segment().build(
                    SegmentHeader(seq_num=0, ack_num=seg.seq_num, flag=[ACK_FLAG]),
                    b"",
                ),
                server_addr,
            )

        except Exception as e :
            #kalau checksum gagal ato timeout
            print(e)

        # RECEIVE PAYLOAD
        while True:
            try :
                data, server_addr = self.conn.listen_single_segment(5)
                seg = Segment().build_from_bytes(bytes_data=data)
                if seg.get_header().flag.value == FIN_FLAG:
                    head = SegmentHeader(seq_num=0, ack_num=0, flag=[ACK_FLAG])
                    self.conn.send_data(Segment().build(header=head, payload=b""), server_addr)
                    self.conn.close_socket()
                    break
                elif segment_num == seg.seq_num :
                    print(f"[!] [Client] [Num={seg.seq_num}] Received Segment")
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
                break
        
        self.__write_bytes_to_file(filebody, filename)
            
            # data, server_addr = self.conn.listen_single_segment()
            # seg = Segment().build_from_bytes(bytes_data=data)

        # print(filebody)
        #print(len(filebody))

        return 

    def __write_bytes_to_file(self, filebody: bytes, filename = "client_files/result.txt") -> bytes:

        f = open(filename, "wb")
        f.write(filebody)
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--broadcastport", default=8080, type=int, help="Port of server")
    parser.add_argument("-c", "--clientport", default=3000, type=int, help="Port of client")
    parser.add_argument("-f", "--filepath", default="result", help="Port of client")

    args = parser.parse_args()

    main = Client("127.0.0.1", args.clientport)
    print(f"Client started at localhost:{args.clientport}")

    main.three_way_handshake(("127.0.0.1", args.broadcastport))
    main.listen_file_transfer(("127.0.0.1", args.broadcastport))
