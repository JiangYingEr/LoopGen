#!/usr/bin/python3
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController, Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.topo import Topo

class P4Host(Host):
    def config(self, **params):
        r = super(P4Host, self).config(**params)

        # Disable hardware uninstallation
        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (self.defaultIntf().name, off)
            self.cmd(cmd)

        # Disable IPv6
        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        self.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        self.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

        self.cmd("sysctl -w net.ipv4.conf.all.arp_announce=2")
        self.cmd("sysctl -w net.ipv4.conf.all.arp_ignore=1")
        self.cmd("sysctl -w net.ipv4.neigh.default.gc_stale_time=80")

        # Disable IPv6 for specific interfaces
        for intf in self.intfList():
            self.cmd(f"sysctl -w net.ipv6.conf.{intf}.disable_ipv6=1")

        self.cmd("ip6tables -I OUTPUT -j DROP")

        return r

# Main Topology
class LooGen(Topo):
    def __init__(self):
        super().__init__()
        # Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        linkopts = {'delay': '100ms'}
        # Links
        self.addLink(s1, h1, port1=1, **linkopts)
        self.addLink(s2, h2, port1=1, **linkopts)
        self.addLink(s3, h3, port1=1, **linkopts)
        # Ring
        self.addLink(s1, s2, **linkopts)
        self.addLink(s2, s3, **linkopts)
        self.addLink(s3, s1, **linkopts)


def run_experiment():
    topo = LooGen()
    c0 = RemoteController('c0', ip='127.0.0.1', port=6633)

    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        controller=c0,
        host=P4Host, 
        autoSetMacs=True,
        build=False
    )

    info('*** Building network\n')
    net.build()
    
    info('*** Starting network\n')
    net.start()

    info('*** Installing static ARP entries (Prevention of ARP Broadcast)\n')
    net.staticArp()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_experiment()
