#!/usr/bin/env python3
import socket, threading, json, uuid, sys

SERVER_IP = "192.168.137.1"   # your PC’s IP
SERVER_PORT = 50000
SHARED_TOKEN = "replace_with_strong_secret"

DEVICE_TYPE = "Phone"
DEVICE_ID = str(uuid.getnode())

def label_for(device_type):
    dt = (device_type or "").lower()
    if dt.startswith("pc"):
        return "PC 💻:"
    elif dt.startswith("phone") or dt.startswith("android") or dt.startswith("ios"):
        return "Phone📱:"
    return "Unrecognized device 🚫:"

def recv_loop(sock):
    try:
        while True:
            data = sock.recv(4096)
            if not data: break
            try:
                msg = json.loads(data.decode("utf-8"))
            except: continue
            if msg.get("token") != SHARED_TOKEN:
                continue
            device_type = msg.get("device_type","?")
            device_id = msg.get("device_id","?")
            text = msg.get("text","")
            print(f"{label_for(device_type)} [{device_id}] {text}")
    except Exception as e:
        print("recv error:", e)

def send_loop(sock):
    while True:
        line = input("> ").strip()
        if not line: continue
        msg = {
            "token": SHARED_TOKEN,
            "device_type": DEVICE_TYPE,
            "device_id": DEVICE_ID,
            "text": line
        }
        sock.send(json.dumps(msg).encode("utf-8"))

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()
    send_loop(sock)