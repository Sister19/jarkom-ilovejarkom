from lib import connection as conn

server = conn.Connection("localhost", 8080)
try:
    server.listen_single_segment(timeout=10)
    print("tes")
except Exception as e:
    print(str(e))
finally:
    server.close_socket()

print("tes")