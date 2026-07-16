from scapy.all import *

pkt=Ether(src="00:00:00:00:00:01", dst="00:00:00:00:00:08")/IP(src="10.0.0.1",dst="10.0.0.8",ttl = 255)/UDP()
#sendp(pkt, iface = "ens2f0np0", count = 1)
sendp(pkt, iface = "h1-eth0", count = 1)
