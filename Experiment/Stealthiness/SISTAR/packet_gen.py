#!/usr/bin/env python3
import sys
from scapy.all import *

def generate_traffic():
    output_file = "attack.pcap"
    count = 20000

    print(f"Generating {count} packets to {output_file}...")

    pkt = Ether(dst="08:00:00:00:01:11") / \
          IP(src="10.0.55.55", dst="10.0.99.99", ttl=64) / \
          TCP(flags="A")

    wrpcap(output_file, [pkt]*count)
    print("Done.")

if __name__ == "__main__":
    generate_traffic()
