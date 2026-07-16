#!/usr/bin/env python3
import random
import socket
import sys
import io
from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp
import datetime
import time

from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI

def dump_rules():
    for i in range(3):
        s = SimpleSwitchThriftAPI(9090 + i)
        original_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        s.table_dump_entry_from_key("MyIngress.ipv4_lpm", ["10.0.0.8"])
        sys.stdout = original_stdout
        output_result = captured_output.getvalue()
        #print("captured_output")
        #print(type(output_result))
        if i == 0 and "MyIngress.ipv4_forward - 03" in output_result:
            continue
        if i == 1 and "MyIngress.ipv4_forward - 02" in output_result:
            continue
        if i == 2 and "MyIngress.ipv4_forward - 03" in output_result:
            continue
        with  open("button.txt", 'w') as f:
            f.write('n')
            return
    with open('button', 'w') as f:
        f.write('y')
        return

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

    #dump_rules()
    #return
    #print("sending on interface %s to %s" % (iface, str(addr)))
    #pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = Ether(src="00:00:00:00:00:08",dst = "00:00:00:00:00:02")/IP(src = "10.0.0.8", dst="10.0.0.2") / TCP(dport=1234, sport=random.randint(49152,65535))
    #pkt.show2()
    t = datetime.datetime(2023,11,22,7,0,0,0)
    delta = datetime.timedelta(seconds=4)

    n = 0
    while True:
        n += 1
        while datetime.datetime.now() < t:
            pass
        sendp(pkt, iface="h1-eth0", verbose=False)
        time.sleep(2)
        #dump_rules()
        if read_file_buttion():
            print("%dth  succeed!" % n)
            break
        else:
            print("%dth  fail" % n)
            t = t + delta


if __name__ == '__main__':
    main()
