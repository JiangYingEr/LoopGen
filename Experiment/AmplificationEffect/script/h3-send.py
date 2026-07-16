#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp
import datetime
import time


def read_file_buttion():
    with open('script/button.txt', 'r') as f:
        l = f.read()
        if 'y' in l:
            return 1
        else:
            return 0

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
    pkt = Ether(src="00:00:00:00:00:08",dst = "00:00:00:00:00:01")/IP(src = "10.0.0.8", dst="10.0.0.1") / TCP(dport=1234, sport=random.randint(49152,65535))
    #pkt.show2()
    t = datetime.datetime(2023,11,22,7,0,0,0)
    delta = datetime.timedelta(seconds=4)


    while True:
        while datetime.datetime.now() < t:
            pass
        sendp(pkt, iface="h3-eth0", verbose=False)
        time.sleep(3)
        if read_file_buttion():
            break
        else:
            t = t + delta


if __name__ == '__main__':
    main()
