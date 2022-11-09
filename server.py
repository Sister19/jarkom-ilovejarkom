from lib.connection import *
import lib.segment as segment
from lib.segment import Segment
import sys


class Server:
    def __init__(self,port : int):
        #Buat connection
        self.conn = Connection("localhost",port)
        print(f"[!] Server started at localhost:{port}")

    def listen_for_clients(self):
        # Waiting client for connect
        list_clients = [] #hati-hati tidak unik
        print("[!] Listening to broadcast address for clients.")
        answer = "y"
        self.conn.listen()
        while(answer != "n") :
            client,address = self.conn.accept()
            list_clients.append(address)
            print(f"[!] Received request from {address[0]}:{address[1]}")
            answer = input("[?] Listen more? (y/n) ")
        print(list_clients)

    def start_file_transfer(self):
        # Handshake & file transfer for all client
        pass

    def file_transfer(self, client_addr: tuple["ip", "port"]):
        # File transfer, server-side, Send file to 1 client
        pass

    def three_way_handshake(self, client_addr: tuple["ip", "port"]) -> bool:
        # Three way handshake, server-side, 1 client
        pass


if __name__ == "__main__":
    port = int(sys.argv[1])
    main = Server(port)
    main.listen_for_clients()
    # main.start_file_transfer()
