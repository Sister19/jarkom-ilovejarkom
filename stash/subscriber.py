from lib.connection import *

server = Connection("localhost", 8080)
try:
    server.listen_single_segment(timeout=5)
except Exception as e:
    print(str(e))
finally:
    server.close_socket()
