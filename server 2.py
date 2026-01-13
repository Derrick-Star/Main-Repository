import socket
import threading

HOST = "0.0.0.0"
PORT = 50000

clients = []

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    clients.append(conn)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            print(f"{addr}: {msg}")

            # Echo back to all clients (including sender)
            for c in clients:
                try:
                    c.sendall(f"{addr}: {msg}\n".encode())
                except:
                    pass
    except:
        pass
    finally:
        print(f"Disconnected: {addr}")
        clients.remove(conn)
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()