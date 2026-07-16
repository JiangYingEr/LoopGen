#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import *


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def main():

    iface = get_if()
    payload = ''
    for i in range(1):
        payload += '1'

    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst='10.0.0.2', ttl=255) / UDP(dport=1234, sport=random.randint(49152,65535))/payload
    pkt.show2()
    packets = []
    for i in range(2000):
        packets.append(pkt)
        #sendp(pkt, iface=iface, verbose=False)
    wrpcap('normalDoS.pcap', packets)

if __name__ == '__main__':
    main()
