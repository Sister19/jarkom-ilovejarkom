import argparse
import os
import threading
from dataclasses import dataclass

from lib.connection import *
from lib.segment import *


@dataclass
class ClientStatus:
    address: tuple(("ip", "port"))
    last_ack: int
    fin: bool


class Server:
    def __init__(self, ip: str, port: int):
        # Init server
        self.ip = ip
        self.port = port
        self.conn = Connection(ip, port)
        self.clients = {}

    def listen_for_clients(self):
        # Waiting client for connect
        try:
            ans = "y"
            print("[!] Listening to broadcast address for clients.\n")
            while ans.lower() == "y":
                data, address = self.conn.listen_single_segment(60)
                addr = f"{address[0]}:{address[1]}"
                if addr not in self.clients:
                    self.clients[addr] = ClientStatus(
                        address=(address[0], address[1]), last_ack=0, fin=False
                    )
                    print(f"[!] Received request from {addr}")
                else:
                    print(f"[!] Client {addr} has previously connected.")
                ans = input("[?] Listen more? (y/n) ")

            print("\nClient list:")
            number = 1
            for addr in self.clients:
                print(f"{number}. {addr}")
                number += 1
            print("\n[!] Commencing file transfer...")

        except Exception as e:
            print(e)

    def three_way_handshake(self, client_addr: tuple(("ip", "port"))) -> bool:
        # Three way handshake, server-side, 1 client
        print("[!] [Handshake] Sending SYN ACK to client")
        self.conn.send_data(
            Segment().build(
                SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG, ACK_FLAG]), b""
            ),
            client_addr,
        )

        # Waiting ACK from client
        data, addr = self.conn.listen_single_segment()
        seg = Segment().build_from_bytes(bytes_data=data)

        if client_addr != addr:
            print("[!] Handshake interrupted by another client, aborting...")
            return False

        if seg.get_header().flag.value != ACK_FLAG:
            print("[!] Wrong flag recieved from client, aborting...")
            return False

        print("[!] [Handshake] Received ACK from client, handshake success!")
        return True

    # PARALELL INI UNTUK MENGAKTIFKAN FITURNYA
    def start_file_transfer(self, filename: str, parallel=True):
        # Handshake & file transfer for all client

        file = self.__read_file_to_bytes(filename)
        segments = self.__deassemble(file)
        i = 1
        threads = []
        for _, client in self.clients.items():
            print(f"[!] [Handshake] Handshake to client {i}...")
            if not self.three_way_handshake(client.address):
                print("[!] Handshake failed, proceed to the next client.")
                continue
            print(f"[!] [Client {i}] Initiating file transfer...")
            thread = threading.Thread(
                target=self.file_transfer,
                args=(
                    segments,
                    client.address,
                    i,
                    filename,
                ),
            )
            threads.append(thread)
            if not (parallel):
                self.file_transfer(segments, client.address, i, filename)
            i += 1

        if parallel:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.conn.close_socket()

    def file_transfer(
        self,
        segments: List[Segment],
        client_addr: tuple(("ip", "port")),
        number=1,
        filename="",
        parallel=True,
    ):

        # Go-Back-N Protocol
        first_segment = 0
        last_segment = 0
        n = len(segments)
        window_size = min(n, 3)

        # SEND METADATA
        ack_metadata = False
        filename_bytes = bytes(filename, "utf-8")
        header = SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG])
        filename_segment = Segment().build(header=header, payload=filename_bytes)
        while not ack_metadata:
            try:
                print(f"[!] [Client {number}] [Metadata] Sent")
                self.conn.send_data(filename_segment, client_addr)
                data, addr = self.conn.listen_single_segment(1)
                ack_seg = Segment().build_from_bytes(bytes_data=data)
                if ack_seg.get_header().flag.value == ACK_FLAG:
                    print(f"[!] [Client {number}] [Metadata] [ACK] Segment acked")
                    ack_metadata = True
            except Exception as e:
                print(e)

        # SEND SEGMENTS
        # NON PARALLEL VERSION :
        if not parallel:
            while first_segment < n:
                if (last_segment - first_segment) < window_size and last_segment < n:
                    self.conn.send_data(segments[last_segment], client_addr)
                    print(f"[!] [Client {number}] [Num={last_segment+1}] Sent")
                    last_segment += 1

                else:
                    try:
                        data, addr = self.conn.listen_single_segment(1)
                        ack_seg = Segment().build_from_bytes(bytes_data=data)
                        if ack_seg.get_header().flag.value == ACK_FLAG:
                            if ack_seg.ack_num == first_segment + 1:
                                print(
                                    f"[!] [Client {number}] [Num={first_segment+1}] [ACK] Segment acked"
                                )
                                first_segment += 1
                            else:
                                last_segment = first_segment
                                print(
                                    f"[!] [Client {number}] [Num={first_segment+1}] [ACK] Ack is not valid"
                                )
                    except Exception as e:
                        last_segment = first_segment
                        print(
                            f"[!] [Client {number}] [ERROR segment {first_segment}+1] ACK response error: {str(e)}"
                        )

        # PARALLEL VERSION:
        else:
            vars = {"first_segment": 0, "last_segment": 0}
            queue = []
            # THREAD FOR SEND DATA
            t1 = threading.Thread(
                target=self.__send_data_parallel,
                args=(
                    segments,
                    vars,
                    client_addr,
                    number,
                    window_size,
                    n,
                ),
            )
            # THREAD FOR RECEIVING DATA
            t2 = threading.Thread(
                target=self.__receive_data_parallel,
                args=(
                    number,
                    vars,
                    n,
                    queue,
                ),
            )

            t3 = threading.Thread(
                target=self.__listen_data_parallel,
                args=(
                    number,
                    vars,
                    n,
                    queue,
                ),
            )

            # START THE THREAD AND JOIN
            t1.start()
            t2.start()
            t3.start()

            t1.join()
            t2.join()
            t3.join()

        try:
            self.conn.send_data(
                Segment().build(
                    SegmentHeader(seq_num=0, ack_num=0, flag=[FIN_FLAG]), b""
                ),
                client_addr,
            )
            print(f"[!] [Client {number}] [FIN] Sending FIN .....")
            data, addr = self.conn.listen_single_segment(2)
            ack_seg = Segment().build_from_bytes(bytes_data=data)

            if ack_seg.get_header().flag.value == ACK_FLAG:
                print(f"[!] [Client {number}] [FIN] Acked")
        except Exception as e:
            print(e)

    def __read_file_to_bytes(self, filename: str) -> bytes:
        data = b""
        with open(filename, "rb") as f:
            byte = f.read(MAX_PAYLOAD)
            while byte != b"":
                data += byte
                byte = f.read(MAX_PAYLOAD)

        f.close()
        return data

    def __deassemble(self, file: bytes) -> List[Segment]:
        i = 0
        maxbytes = len(file)
        splitted_payload = []
        while i < maxbytes:
            splitted_payload.append(file[i : i + MAX_PAYLOAD])
            i += MAX_PAYLOAD

        seq_count = 1
        segments = []
        for data in splitted_payload:
            header = SegmentHeader(seq_num=seq_count, ack_num=0, flag=[SYN_FLAG])
            segments.append(Segment().build(header=header, payload=data))
            seq_count += 1

        return segments

    def __send_data_parallel(self, segments, vars, client_addr, number, window_size, n):
        while (vars["first_segment"] < n):
            while (vars["last_segment"] - vars["first_segment"]) < window_size and vars["last_segment"] < n:
                self.conn.send_data(segments[vars["last_segment"]], client_addr)
                print(f"[!] [Client {number}] [Num={vars['last_segment']+1}] Sent")
                vars["last_segment"] += 1

    def __listen_data_parallel(self, number, vars,n, queue):
        while (vars["first_segment"] < n):
            try:
                if vars["first_segment"] < n:
                    data, addr = self.conn.listen_single_segment(1)
                    queue.append(data)
            except Exception as e:
                vars["last_segment"] = vars["first_segment"]
                print(
                    f"[!] [Client {number}] [ERROR segment {vars['first_segment']+1}]  ACK response error: {str(e)}"
                )
            
    def __receive_data_parallel(self, number, vars,n, queue):
        while (vars["first_segment"] < n):
            if len(queue) > 0:
                data = queue.pop(0)
                ack_seg = Segment().build_from_bytes(bytes_data=data)
                if ack_seg.get_header().flag.value == ACK_FLAG:
                    if ack_seg.ack_num == vars["first_segment"] + 1:
                        print(f"[!] [Client {number}] [Num={vars['first_segment']+1}] [ACK] Segment acked")
                        vars["first_segment"] += 1
                    else:
                        vars["last_segment"] = vars["first_segment"]
                        print(
                            f"[!] [Client {number}] [Num={vars['first_segment']+1}] [ACK] Ack is not valid"
                        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b", "--broadcastport", default=8080, type=int, help="Port of server"
    )
    parser.add_argument(
        "-f",
        "--pathfile",
        default="server_files/git.exe",
        type=str,
        help="Path file input",
    )
    args = parser.parse_args()

    main = Server("127.0.0.1", args.broadcastport)

    print(f"[!] Server started at localhost:{args.broadcastport}")
    file = os.stat(args.pathfile)
    print(f"[!] Source File | {os.path.basename(args.pathfile)} | {file.st_size} bytes")

    main.listen_for_clients()
    main.start_file_transfer(args.pathfile)
