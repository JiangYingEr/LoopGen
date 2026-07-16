#!/usr/bin/env python3
"""
LoopGen attack experiment topology - revised (removed preset rules)
Pure controller mode, suitable for LoopGen attack testing
"""

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Host
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
import subprocess
import time

class P4Host(Host):
    """Custom host class that disables some network features to prevent active transmissions"""
    def config(self, **params):
        r = super(P4Host, self).config(**params)

        # Disable NIC offload features to prevent active transmissions
        for off in ["rx", "tx", "sg"]:
            cmd = "/sbin/ethtool --offload %s %s off" % (self.defaultIntf().name, off)
            self.cmd(cmd)

        # Disable IPv6
        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        self.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        self.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
        
        # Reduce ARP active probing
        self.cmd("sysctl -w net.ipv4.conf.all.arp_announce=2")
        self.cmd("sysctl -w net.ipv4.conf.all.arp_ignore=1")
        
        return r

def show_flow_tables():
    """Print current flow table state for switches s1, s2, s3"""
    print("\n" + "="*60)
    print("Current flow table state")
    print("="*60)
    
    for switch in ['s1', 's2', 's3']:
        print(f"\n--- {switch} flows ---")
        cmd = f"ovs-ofctl -O OpenFlow13 dump-flows {switch}"
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line and not line.startswith('NXST_FLOW'):
                        print(f"  {line}")
                if len(lines) <= 1:
                    print("  (No flow entries yet; waiting for controller)")
            else:
                print("  (Failed to retrieve or no output)")
        except Exception as e:
            print(f"  Retrieval failed: {e}")

def create_loopgen_topology():
    """Create topology - pure controller mode"""
    info('*** Creating LoopGen topology - Pure Controller Mode\n')
    
    net = Mininet(controller=None, switch=OVSSwitch, link=TCLink, host=P4Host)
    
    # Add remote Ryu controller
    c0 = net.addController('c0', controller=RemoteController,
                          ip='127.0.0.1', port=6633, protocols='OpenFlow13')
    
    # Add switches and hosts
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')
    s3 = net.addSwitch('s3', protocols='OpenFlow13')
    
    h1 = net.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01', cls=P4Host)
    h2 = net.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02', cls=P4Host)
    h3 = net.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03', cls=P4Host)
    
    # Connect hosts to switches
    net.addLink(h1, s1, port1=0, port2=1)
    net.addLink(h2, s2, port1=0, port2=1)
    net.addLink(h3, s3, port1=0, port2=1)
    
    # Inter-switch links (0ms delay)
    # Inter-switch links (50ms delay between switches)
    net.addLink(s1, s2, port1=2, port2=2, cls=TCLink, delay='50ms')
    net.addLink(s2, s3, port1=3, port2=3, cls=TCLink, delay='50ms')
    net.addLink(s3, s1, port1=2, port2=3, cls=TCLink, delay='50ms')

    
    # Start network
    net.start()
    c0.start()
    
    # Start switches with controller
    s1.start([c0])
    s2.start([c0])
    s3.start([c0])
    
    # Wait for controller connections
    info('*** Waiting for controller connections (5 seconds)\n')
    time.sleep(5)
    
    # Show initial (empty) flow tables
    print("\nInitial flow table state (controller mode):")
    show_flow_tables()
    
    # Print topology info
    print("\n" + "="*70)
    print("LOOPGEN ATTACK TOPOLOGY - Pure Controller Mode")
    print("="*70)
    
    print("\nHost configuration:")
    print(f"  h1: IP=10.0.0.1, MAC=00:00:00:00:00:01")
    print(f"  h2: IP=10.0.0.2, MAC=00:00:00:00:00:02")
    print(f"  h3: IP=10.0.0.3, MAC=00:00:00:00:00:03")
    
    print("\nNetwork topology:")
    print("  Switches: s1, s2, s3 (OpenFlow 1.3)")
    print("  Controller: 127.0.0.1:6633 (Ryu)")
    print("  Port mapping:")
    print("    s1: port1=h1, port2=s2, port3=s3")
    print("    s2: port1=h2, port2=s1, port3=s3")
    print("    s3: port1=h3, port2=s1, port3=s2")
    
    print("\nLink delays:")
    print("  All inter-switch links: 0ms")
    print("  Host-to-switch links: 0ms")
    
    print("\nOperation mode:")
    print("  ✓ Pure controller mode - packets default to controller")
    print("  ✓ Controller dynamically learns MAC locations")
    print("  ✓ Suitable for LoopGen attack testing")
    print("="*70)
    
    print("\n" + "="*60)
    print("To start LoopGen attack:")
    print("1. In Mininet CLI: xterm h1 h2 h3")
    print("2. In h1 terminal: python3 hack_h1_auto.py")
    print("3. In h2 terminal: python3 hack_h2_auto.py")
    print("4. In h3 terminal: python3 hack_h3_auto.py")
    print("="*60)
    
    CLI(net)
    
    # Stop network
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_loopgen_topology()

