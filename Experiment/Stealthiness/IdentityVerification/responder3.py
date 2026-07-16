from scapy.all import *
import sys

IFACE = sys.argv[1] if len(sys.argv) > 1 else "h1-eth0"
MY_MAC = get_if_hwaddr(IFACE)
MY_PASSWORD = "letmein"
AUTH_ETYPE = 0x88B5

def handle(pkt):
    if pkt.haslayer(Ether) and pkt.type == AUTH_ETYPE:
        payload = bytes(pkt.payload)
        if payload.startswith(b'AUTH_REQ'):
            print("[auth_responder] Received AUTH_REQ, sending AUTH_RESP")
            resp = Ether(dst=pkt.src, src=MY_MAC, type=AUTH_ETYPE) / Raw(b'AUTH_RESP:' + MY_PASSWORD.encode())
            sendp(resp, iface=IFACE, verbose=False)

print(f"Starting auth responder on {IFACE}, MAC={MY_MAC}")
sniff(iface=IFACE, prn=handle)

