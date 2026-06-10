## Usage
(Following defense code is based on Ryu's simple_switch_13.py)

#### Method 1: Loop Detection Countermeasure:
The `--observe-links` parameter should be added to allow Ryu to discover and maintain the network topology dynamically.
```bash
ryu-manager --observe-links loop_detect_13.py
```

#### Method 2: Time Constraints Countermeasure:
Start the timestamp constraint controller.
```bash
ryu-manager time_constraint_13.py
```

#### Start mininet topology (The remaining steps for [starting mininet topology](../Feasibility/AcrossController/Ryu/README.md) remain the same.)
```bash
sudo mn -c
sudo python3 -E LoopGen_topo.py
```
Open the host terminal
```bash
mininet> xterm h1 h2 h3
```

Send packets on each host terminal
```bash
# Node: h1
python3 LoopGen_packets_l3.py h1-eth0 00:00:00:00:00:02

# Node: h2
python3 LoopGen_packets_l3.py h2-eth0 00:00:00:00:00:03

# Node: h3
python3 LoopGen_packets_l3.py h3-eth0 00:00:00:00:00:01
```
Trigger attack
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; sendp(Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:08')/IP(dst='10.0.0.8')/UDP(dport=9999), iface='h1-eth0', count=1)"
```
