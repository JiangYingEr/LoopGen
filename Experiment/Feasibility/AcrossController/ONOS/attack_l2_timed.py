#!/usr/bin/python3
import sys
import time
from datetime import datetime, timedelta
from scapy.all import Ether, IP, UDP, sendp, Raw

# =================配置区域=================
ATTACK_MAC = "00:00:00:00:00:08"
ATTACK_IP = "10.0.0.8"
# =========================================

def wait_until_target_time():
    """
    计算目标时间（下一分钟的第30秒）并阻塞等待
    """
    now = datetime.now()
    
    # 逻辑：当前时间往后推1分钟，然后将秒数定死在10秒，微秒归零
    # 例如：10:05:12 -> 10:06:30
    # 例如：10:05:45 -> 10:06:30
    target_time = (now + timedelta(minutes=1)).replace(second=10, microsecond=0)
    
    wait_seconds = (target_time - now).total_seconds()
    
    print(f"[*] 当前时间: {now.strftime('%H:%M:%S')}")
    print(f"[*] 锁定发射时间: {target_time.strftime('%H:%M:%S')} (下一分钟的10秒)")
    print(f"[*] 倒计时等待: {wait_seconds:.2f} 秒...")
    print("-" * 40)
    
    # 睡眠直到指定时间
    if wait_seconds > 0:
        time.sleep(wait_seconds)
    
    print(f"\n[!] 时间到！({datetime.now().strftime('%H:%M:%S.%f')}) 发射！")

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

    # 1. 先等待时间对齐
    wait_until_target_time()
    
    # 2. 时间一到，立即发包
    send_one_packet(iface, dst_mac)
