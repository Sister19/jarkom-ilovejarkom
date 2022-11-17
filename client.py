import argparse
import os

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

    def listen_file_transfer(self, server_addr: tuple(("ip", "port")), pathfile=None):
        # File transfer, client-side
        filebody = b""
        segment_num = 1
        if pathfile is None: 
            filepath = "client_files/result.txt"  # Handle metadata ga kekirim DAN pathfile gadikasih
        else :
            filepath = pathfile

        # RECEIVE METADATA
        try:
            data, server_addr = self.conn.listen_single_segment(5)
            seg = Segment().build_from_bytes(bytes_data=data)
            print("[!] [Client] [Metadata] Received Metadata")
            path = seg.payload.decode("utf-8")
            filename = os.path.basename(path)
            filename_arr = filename.rsplit(".", 1)
            print(
                f"[!] [Client] [Metadata] Filename: {filename_arr[0]} | Extension: .{filename_arr[1]}"
            )

            if pathfile is None: 
                filepath = "client_files/" + filename #metadata dipake kalau gaada dikasih nama aja

            self.conn.send_data(
                Segment().build(
                    SegmentHeader(seq_num=0, ack_num=seg.seq_num, flag=[ACK_FLAG]),
                    b"",
                ),
                server_addr,
            )
        except Exception as e:
            # kalau checksum gagal ato timeout
            print(e)

        # RECEIVE PAYLOAD
        while True:
            try:
                data, server_addr = self.conn.listen_single_segment(10)
                seg = Segment().build_from_bytes(bytes_data=data)
                if seg.get_header().flag.value == FIN_FLAG:
                    head = SegmentHeader(seq_num=0, ack_num=0, flag=[ACK_FLAG])
                    self.conn.send_data(
                        Segment().build(header=head, payload=b""), server_addr
                    )
                    self.conn.close_socket()
                    break
                elif segment_num >=  seg.seq_num :
                    print(f"[!] [Client] [Num={seg.seq_num}] Received Segment")
                    self.conn.send_data(
                        Segment().build(
                            SegmentHeader(
                                seq_num=0, ack_num=seg.seq_num, flag=[ACK_FLAG]
                            ),
                            b"",
                        ),
                        server_addr,
                    )
                    if segment_num == seg.seq_num :
                        segment_num += 1
                        filebody += seg.payload
            except Exception as e:
                # kalau checksum gagal ato timeout
                print(e)
                break

        self.__write_bytes_to_file(filebody, filepath)

        return

    def __write_bytes_to_file(
        self, filebody: bytes, filename="client_files/result.txt"
    ) -> bytes:
        f = open(filename, "wb")
        f.write(filebody)
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--broadcastport", default=8080, type=int, help="Port of server"
    )
    parser.add_argument(
        "-c", "--clientport", default=3000, type=int, help="Port of client"
    )
    parser.add_argument(
        "-f",
        "--pathfile",
        default=None,
        type=str,
        help="Path file input",
    )

    args = parser.parse_args()

    main = Client("127.0.0.1", args.clientport)
    print(f"[!] Client started at localhost:{args.clientport}")

    main.three_way_handshake(("127.0.0.1", args.broadcastport))
    main.listen_file_transfer(("127.0.0.1", args.broadcastport),args.pathfile)
