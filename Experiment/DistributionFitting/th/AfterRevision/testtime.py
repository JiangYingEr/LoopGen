#!/usr/bin/env python3
"""
在 Mininet host 上运行，精确测量从调用 send() 到数据包离开 veth 的时间
用法: python3 sender.py <iface> <dst_ip> <dst_mac> [count]
示例: python3 sender.py h1-eth0 10.0.0.2 00:00:00:00:00:02 100
"""
import socket
import struct
import time
import sys
import fcntl
import statistics
from scapy.all import Ether, IP, UDP, Raw

# ---- Linux 常量 ----
SO_TIMESTAMPING              = 37
SCM_TIMESTAMPING             = 37
SOF_TIMESTAMPING_TX_SOFTWARE = 1 << 1
SOF_TIMESTAMPING_SOFTWARE    = 1 << 4
SOF_TIMESTAMPING_OPT_ID      = 1 << 7
SOF_TIMESTAMPING_OPT_TSONLY  = 1 << 11
MSG_ERRQUEUE                 = 0x2000
SIOCGIFHWADDR                = 0x8927


def get_mac(sock, iface):
    """获取接口 MAC 地址"""
    info = fcntl.ioctl(sock.fileno(), SIOCGIFHWADDR,
                       struct.pack('256s', iface[:15].encode()))
    return ':'.join('%02x' % b for b in info[18:24])


def parse_scm_timestamping(cmsg_data):
    """解析 SCM_TIMESTAMPING cmsg, 返回软件时间戳(秒, float)"""
    ts = struct.unpack("6q", cmsg_data[:48])
    sw_sec = ts[0] + ts[1] / 1e9
    return sw_sec


def recv_tx_timestamp(sock, timeout_ms=100):
    """从 error queue 读取 TX 时间戳(秒)"""
    sock.settimeout(timeout_ms / 1000.0)
    try:
        _, ancdata, _, _ = sock.recvmsg(2048, 1024, MSG_ERRQUEUE)
    except socket.timeout:
        return None
    for cmsg_level, cmsg_type, cmsg_data in ancdata:
        if cmsg_level == socket.SOL_SOCKET and cmsg_type == SCM_TIMESTAMPING:
            return parse_scm_timestamping(cmsg_data)
    return None


def main():
    if len(sys.argv) < 4:
        print("Usage: sender.py <iface> <dst_ip> <dst_mac> [count]")
        sys.exit(1)

    iface   = sys.argv[1]
    dst_ip  = sys.argv[2]
    dst_mac = sys.argv[3]
    count   = int(sys.argv[4]) if len(sys.argv) > 4 else 100

    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
    s.bind((iface, 0))

    flags = (SOF_TIMESTAMPING_TX_SOFTWARE
             | SOF_TIMESTAMPING_SOFTWARE
             | SOF_TIMESTAMPING_OPT_ID
             | SOF_TIMESTAMPING_OPT_TSONLY)
    s.setsockopt(socket.SOL_SOCKET, SO_TIMESTAMPING, flags)

    src_mac = get_mac(s, iface)
    print(f"[+] iface={iface}, src_mac={src_mac}, dst={dst_ip}({dst_mac})")
    print(f"[+] Sending {count} packets...\n")

    import os
    os.system(f"ethtool -K {iface} tso off gso off gro off tx off rx off 2>/dev/null")

    latencies = []

    # 预热
    warm = Ether(src=src_mac, dst=dst_mac)/IP(dst=dst_ip)/UDP(dport=5001)/Raw(b"warmup")
    s.send(bytes(warm))
    recv_tx_timestamp(s)
    time.sleep(0.1)

    for i in range(count):
        payload = f"pkt-{i:06d}".encode().ljust(32, b'\x00')
        pkt = Ether(src=src_mac, dst=dst_mac) / \
              IP(dst=dst_ip) / \
              UDP(sport=12345, dport=5001) / \
              Raw(payload)
        raw = bytes(pkt)

        t1 = time.clock_gettime(time.CLOCK_REALTIME)
        s.send(raw)

        t_tx = recv_tx_timestamp(s)
        if t_tx is None:
            print(f"[!] pkt {i}: no TX timestamp")
            continue

        lat = t_tx - t1
        latencies.append(lat)
        if i < 5 or i == count - 1:
            print(f"  pkt {i:4d}: send_latency = {lat:.9f} s")

        time.sleep(0.001)

    s.close()

    if latencies:
        sorted_lat = sorted(latencies)
        mean_val = statistics.mean(latencies)
        print("\n========== Statistics (seconds) ==========")
        print(f"  Samples  : {len(latencies)}")
        print(f"  Min      : {min(latencies):.9f}")
        print(f"  Max      : {max(latencies):.9f}")
        print(f"  Mean     : {mean_val:.9f}")
        print(f"  Median   : {statistics.median(latencies):.9f}")
        if len(latencies) > 1:
            var  = statistics.variance(latencies)   # 样本方差
            std  = statistics.stdev(latencies)      # 样本标准差
            print(f"  Variance : {var:.6e}  (s^2)")
            print(f"  Stdev    : {std:.9f}")
        print(f"  P99      : {sorted_lat[int(len(sorted_lat)*0.99)]:.9f}")


if __name__ == "__main__":
    main()
