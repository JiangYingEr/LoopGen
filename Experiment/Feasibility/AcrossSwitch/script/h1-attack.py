#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp
import datetime



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


    #print("sending on interface %s to %s" % (iface, str(addr)))
    #pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = Ether(src="00:00:00:00:00:01",dst = "00:00:00:00:00:08")/IP(src = "10.0.0.1", dst="10.0.0.8") / TCP(dport=1234, sport=random.randint(49152,65535))
    #pkt.show2()
    t = datetime.datetime(2023,11,18,12,12,0,0)

    i = 0
    while datetime.datetime.now() < t:
        pass
    sendp(pkt, iface="h1-eth0", verbose=False)


if __name__ == '__main__':
    main()
