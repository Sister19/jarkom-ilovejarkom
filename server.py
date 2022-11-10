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
        ans = ""
        while ans.lower() != "n":
            data, address = self.conn.listen_single_segment()
            addr = f"{address[0]}:{address[1]}"
            if addr not in self.clients:
                self.clients[addr] = ClientStatus(
                    address=address, last_ack=0, fin=False
                )
            else:
                print(f"Client {addr} has previously connected.")
            ans = input("[?] Listen more? (y/n)")

    def start_file_transfer(self, file: bytes):
        # Handshake & file transfer for all client
        segments = self.__deassemble(file)
        for client in self.clients:
            self.three_way_handshake(client.address)
            self.file_transfer(segments, client.address)

    def file_transfer(
        self, segments: List[Segment], client_addr: tuple(("ip", "port"))
    ):
        # File transfer, server-side, Send file to 1 client
        pass

    def three_way_handshake(self, client_addr: tuple(("ip", "port"))) -> bool:
        # Three way handshake, server-side, 1 client
        print("[!] Server initiating handshake.")
        print("[Handshake] Sending SYN...")
        head = SegmentHeader(seq_num=0, ack_num=0, flag=[SYN_FLAG])
        self.conn.send_data(Segment().build(header=head, payload=b""), client_addr)

        data, addr = self.conn.listen_single_segment()
        print(client_addr, addr)
        if client_addr != addr:
            print("[!] Handshake interrupted by another client, aborting...")
            return False

        syn_ack_seg = Segment().build_from_bytes(bytes_data=data)
        if syn_ack_seg.get_header().flag.value != SYN_ACK:
            print("[!] Wrong flag recieved from client, aborting...")
            return False

        print("[Handshake] Received SYN ACK from client")
        print("[!] Starting to initiate file transfer.")
        return True

    def __deassemble(self, file: bytes):
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

        return segments


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default=8080, type=int, help="Port of server")
    args = parser.parse_args()

    main = Server("127.0.0.1", 8080)
    main.three_way_handshake(("127.0.0.1", 3000))
    # main.listen_for_clients()
    # main.start_file_transfer()
