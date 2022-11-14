import argparse
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
        ans = "y"
        print("[!] Server listening for clients...")
        while ans.lower() == "y":
            data, address = self.conn.listen_single_segment()
            addr = f"{address[0]}:{address[1]}"
            if addr not in self.clients:
                self.clients[addr] = ClientStatus(
                    address=(address[0], address[1]), last_ack=0, fin=False
                )
            else:
                print(f"Client {addr} has previously connected.")
            ans = input("[?] Listen more? (y/n) ")

    def three_way_handshake(self, client_addr: tuple(("ip", "port"))) -> bool:
        # Three way handshake, server-side, 1 client
        print("[Handshake] Sending SYN ACK to client")
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

        print("[Handshake] Received ACK from client, handshake success!")
        return True

    def start_file_transfer(self, filename: str):
        # Handshake & file transfer for all client
        file = self.__read_file_to_bytes(filename)
        segments = self.__deassemble(file)
        i = 1
        for _, client in self.clients.items():
            print(f"[Handshake] Server responding client {i} handshake")
            if not self.three_way_handshake(client.address):
                print("[!] Handshake failed, proceed to the next client.")
                continue
            print(f"[Client {i}] Initiating file transfer...")
            self.file_transfer(segments, client.address)

    def file_transfer(
        self, segments: List[Segment], client_addr: tuple(("ip", "port"))
    ):
        # # Implementing stop and wait first to see if it works
        # sent = [0 for seg in segments]
        # last_sent = 1
        # while sum(sent) != len(segments):
        #     self.conn.send_data(segments[last_sent - 1], client_addr)
        #     data, addr = self.conn.listen_single_segment()
        #     ack_seg = Segment().build_from_bytes(bytes_data=data)
        #     if (
        #         ack_seg.get_header().flag.value == ACK_FLAG
        #         and ack_seg.ack_num == last_sent
        #     ):
        #         sent[last_sent - 1] = 1
        #         last_sent += 1
        #         print(
        #             f"[Client 1] Received ack number {ack_seg.ack_num} from client"
        #         )
        #     else:
        #         print(f"[Client 1] Error occurred")
        #         print("Last segment received from client:")
        #         print(ack_seg)

        # self.conn.send_data(
        #     Segment().build(SegmentHeader(seq_num=0, ack_num=0, flag=[FIN_FLAG]), b""),
        #     client_addr,
        # )

        #Go-Back-N Protocol
        first_segment = 0
        last_segment = 0
        n = len(segments)
        window_size = min(n,3)

        
        while(first_segment<n) :
            if (last_segment-first_segment) < window_size and last_segment<n:
                self.conn.send_data(segments[last_segment], client_addr)
                print(f"[Segment SEQ={last_segment+1}] Sent")

                last_segment += 1
            
            else:
                try :
                    data, addr = self.conn.listen_single_segment(0.05)
                    ack_seg = Segment().build_from_bytes(bytes_data=data)
                    if (
                        ack_seg.get_header().flag.value == ACK_FLAG
                    ) :
                        if ack_seg.ack_num == first_segment+1 :
                            print(f"[Segment SEQ={first_segment+1}] Acked")

                            first_segment += 1
                        else :
                            last_segment = first_segment
                            print(f"[Segment SEQ={first_segment+1}] Ack is not valid")
                except Exception as e :
                    last_segment = first_segment
                    print("[TIMEOUT] ACK response timeout")

        
        self.conn.send_data(
            Segment().build(SegmentHeader(seq_num=0, ack_num=0, flag=[FIN_FLAG]), b""),
            client_addr,
        )
        print("[FIN] Sending FIN .....")

        data, addr = self.conn.listen_single_segment()
        ack_seg = Segment().build_from_bytes(bytes_data=data)
            
        if ack_seg.get_header().flag.value == ACK_FLAG :
            self.conn.close_socket()  
            print("[FIN] Acked\nConnection closed")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8080, type=int, help="Port of server")
    args = parser.parse_args()

    main = Server("127.0.0.1", 8080)
    main.listen_for_clients()
    main.start_file_transfer("server_files/git.exe")
