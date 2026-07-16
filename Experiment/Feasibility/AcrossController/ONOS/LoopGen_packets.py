#!/usr/bin/python3
import sys
import time
from datetime import datetime, timedelta
from scapy.all import Ether, IP, UDP, sendp, Raw

ATTACK_IP = "10.0.0.8"

def wait_until_target_time():
    """
    Calculate the target time (the 30s of the next minute) and block to wait
    """
    now = datetime.now()
    
    target_time = (now + timedelta(minutes=1)).replace(second=30, microsecond=0)
    
    wait_seconds = (target_time - now).total_seconds()
    
    print(f"[*] current time: {now.strftime('%H:%M:%S')}")
    print(f"[*] Lock the launch time: {target_time.strftime('%H:%M:%S')} (下一分钟的30秒)")
    print(f"[*] Countdown waiting: {wait_seconds:.2f} 秒...")
    print("-" * 40)
    
    if wait_seconds > 0:
        time.sleep(wait_seconds)
    
    print(f"\n[!] ({datetime.now().strftime('%H:%M:%S.%f')}) ")

def send_one_packet(iface, dst_mac):
    try:
        last_byte = int(dst_mac.split(':')[-1], 16)
        target_ip = f"10.0.0.{last_byte}"
    except Exception as e:
        target_ip = "10.0.0.254"

    print(f"[*] Sending UDP on {iface}: {ATTACK_MAC} -> {dst_mac}")
    
    pkt = Ether(src=ATTACK_MAC, dst=dst_mac) / \
          IP(src=ATTACK_IP, dst=target_ip) / \
          UDP(sport=6666, dport=5555) / \
          Raw(b"SDN_TIMED_ATTACK")
    
    sendp(pkt, iface=iface, verbose=False)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 attack_l2_timed.py <interface> <dst_mac>")
        sys.exit(1)

    iface = sys.argv[1]
    dst_mac = sys.argv[2]

    wait_until_target_time()
    
    send_one_packet(iface, dst_mac)
