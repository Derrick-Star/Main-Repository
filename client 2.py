import socket
import threading
import sys

HOST = "192.168.137.1"  # <-- change to your PC IP
PORT = 50000

def listen(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode(), end="")
        except:
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    threading.Thread(target=listen, args=(s,), daemon=True).start()

    while True:
        msg = sys.stdin.readline()
        if not msg:
            break
        s.sendall(msg.encode())