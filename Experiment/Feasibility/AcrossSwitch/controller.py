#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
import copy
import _thread
import threading
from threading import Thread
from time import sleep
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import networkx as nx
import time
from random import *
import io
from scapy.all import *
from datetime import datetime

ARP_OP_REQ   = 0x0001
ARP_OP_REPLY = 0x0002
TYPE_CPU_METADATA = 0x080a


switches = []
keys = []
enid_2_real_id = {}

class CPUMetadata(Packet):
    name = "CPUMetadata"
    fields_desc = [ ByteField("fromCpu", 0),
                    ByteField("switch_id", 0),
                    ShortField("origEtherType", None),
                    ShortField("srcPort", None)]

bind_layers(Ether, CPUMetadata, type=TYPE_CPU_METADATA)
bind_layers(CPUMetadata, IP, origEtherType=0x0800)
bind_layers(CPUMetadata, ARP, origEtherType=0x0806)


class Controller():
    def __init__(self):
        self.num = 0
        self.rules = dict()

    def ip_to_mac(self, ip_address):
        ip_parts = ip_address.split('.')
        hex_parts = [hex(int(part))[2:].zfill(2) for part in ip_parts]
        mac_address = ':'.join(hex_parts)
        return mac_address

    def mac_to_ip(self, mac_address):
        dec_parts = [str(int(mac_address[i:i+2], 16)) for i in range(0, 12, 2)]
        ip_address = '.'.join(dec_parts)
        return ip_address

    def generate_arp_rule(self, pkt, ip, mac):
        iface = pkt.sniff_on
        switch_id = int(iface[1]) - 1
        print(switch_id)
        s = SimpleSwitchThriftAPI(9090 + switch_id)
        s.table_add("MyIngress.tb_arp", "resolve_arp", ip, [mac])


    def send(self, pkt):
        pkt[CPUMetadata].fromCpu = 1
        sendp(iface = pkt.sniff_on)



    def handleArpRequest(self, pkt):
        ip = pkt[ARP].pdst
        mac = self.ip_to_mac(ip)
        pkt[ARP].hwdst = pkt[ARP].hwsrc
        pkt[ARP].pdst = pkt[ARP].psrc
        pkt[ARP].hwsrc = mac
        pkt[ARP].psrc = ip
        pkt[Ether].dst = pkt[Ether].src
        pkt[Ether].src = mac
        pkt[ARP].op = ARP_OP_REPLY
        self.generate_arp_rule(pkt, ip, mac)
        self.send(pkt)

    def sip_learn(self, pkt):

        srcip = pkt[IP].src
        dstip = pkt[IP].dst
        thriftport = int(pkt[CPUMetadata].switch_id) - 1
        print('--------------------- switch: s%s' % str(thriftport + 1))
        s = SimpleSwitchThriftAPI(9090 + thriftport)
        try:
            s.table_delete_match("MyIngress.ipv4_lpm", [srcip])
        except:
            pass
        #s.table_dump("MyIngress.ipv4_lpm")
        #s.table_add("MyIngress.sip_learn", "NoAction", [srcip, dstip])
        s.table_add("MyIngress.ipv4_lpm", "ipv4_forward", [srcip], [str(pkt[CPUMetadata].srcPort)])
        #s.table_dump("MyIngress.ipv4_lpm")
        detect_attack = True
        if detect_attack:
            self.rules[str(thriftport + 1)] = pkt[CPUMetadata].srcPort
            self.num += 1
            if self.num == 6:
                self.num = 0
                res = 'n'
                if self.rules['1'] == 3 and self.rules['2'] == 2 and self.rules['3'] == 3:
                    res = 'y'
                with open('script/button.txt', 'w') as f:
                    f.write(res)
                self.rules.clear()







    def handle_pkt(self, pkt):
        if CPUMetadata in pkt:
            if pkt[CPUMetadata].fromCpu == 1: return
            self.sip_learn(pkt)
            if ARP in pkt:
                if pkt[ARP].op == ARP_OP_REQ:
                    self.handleArpRequest(pkt)


    def init_rules(self):
        s1 = SimpleSwitchThriftAPI(9090)
        #s.table_add("MyIngress.tb_arp", "resolve_arp", ip, [mac])
        s1.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.1"], ["1"])
        s1.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.2"], ["2"])
        s1.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.3"], ["3"])
        s1.mirroring_add(100, 4)

        s2 = SimpleSwitchThriftAPI(9091)
        s2.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.2"], ["1"])
        s2.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.1"], ["2"])
        s2.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.3"], ["3"])
        s2.mirroring_add(100, 4)

        s3 = SimpleSwitchThriftAPI(9092)
        s3.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.3"], ["1"])
        s3.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.1"], ["2"])
        s3.table_add("MyIngress.ipv4_lpm", "ipv4_forward", ["10.0.0.2"], ["3"])
        s3.mirroring_add(100, 4)

    def monitor(self, interfaces):
        sniff(iface = interfaces,filter='inbound',
            prn = lambda x: self.handle_pkt(x))


def main():


    #issue_keys()
    #for k in enid_2_real_id.keys():
        #print(k)
        #print(enid_2_real_id[k])
    #init_rules()
    #iface = 's1-cpu-eth1'
    interfaces = []
    switch_num = 3
    for i in range(switch_num):
        interfaces.append('s' + str(i+1) + '-cpu-eth1')
    #iface = sw_name + '-cpu-eth1'
    #print("sniffing on %s" % iface)
    print(interfaces)
    sys.stdout.flush()
    c = Controller()
    c.monitor(interfaces)





if __name__ == '__main__':
    #import sys
    #sw_name = sys.argv[1]

    main()
