#!/usr/bin/env python3
import random
from scapy.all import *

def main():
    iface = "h1-eth0"
    payload = '1' * 958
    
    pkt = Ether(src="00:00:00:00:01:01", dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt / IP(dst='10.0.0.8', ttl=64) / UDP(dport=1234, sport=random.randint(49152,65535)) / payload
    
    print("Generating 2000 attack packets to output-1000B.pcap...")
    packets = [pkt for _ in range(2000)]
    wrpcap('output-1000B.pcap', packets)

if __name__ == '__main__':
    main()
