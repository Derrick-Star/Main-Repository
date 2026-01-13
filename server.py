#!/usr/bin/env python3
import socket, threading, json, uuid

HOST = "0.0.0.0"
PORT = 50000
SHARED_TOKEN = "replace_with_strong_secret"

clients = {}  # device_id -> socket

def label_for(device_type):
    dt = (device_type or "").lower()
    if dt.startswith("pc"):
        return "PC 💻:"
    elif dt.startswith("phone") or dt.startswith("android") or dt.startswith("ios"):
        return "Phone📱:"
    return "Unrecognized device 🚫:"

def handle_recv(conn, addr):
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                msg = json.loads(data.decode("utf-8"))
            except:
                continue
            if msg.get("token") != SHARED_TOKEN:
                continue
            device_id = msg.get("device_id","?")
            device_type = msg.get("device_type","?")
            label = label_for(device_type)
            text = msg.get("text","")
            print(f"{label} [{device_id}] {text}")
    except Exception as e:
        print("recv error:", e)
    finally:
        conn.close()

def accept_loop():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Chat server on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_recv, args=(conn, addr), daemon=True).start()

def send_loop():
    while True:
        line = input("> ").strip()
        if not line: continue
        msg = {
            "token": SHARED_TOKEN,
            "device_type": "PC",
            "device_id": str(uuid.getnode()),
            "text": line
        }
        data = json.dumps(msg).encode("utf-8")
        # broadcast to all connected clients
        for c in list(clients.values()):
            try:
                c.send(data)
            except:
                pass

if __name__ == "__main__":
    threading.Thread(target=accept_loop, daemon=True).start()
    send_loop()