from scapy.all import ARP, Ether, srp

def scan_network(ip_range):
    # Create ARP packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send packet and receive response
    result = srp(packet, timeout=3, verbose=0)[0]

    # Store clients
    clients = []

    for sent, received in result:
        clients.append({'ip': received.psrc, 'mac': received.hwsrc})

    return clients

ip_range = "192.168.1.1/24"  # Example for most routers

devices = scan_network(ip_range)

print("Connected devices:")
print("IP Address\t\tMAC Address")
for device in devices:
    print(f"{device['ip']}\tdevice['mac']")

print(f"\nTotal Devices: {len(devices)}")
