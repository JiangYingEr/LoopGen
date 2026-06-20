## Usage

1. Open a terminal (entering the p4 directory by default)

![](./figs/0.png)

2. Start the controller
```bash
pox/pox.py log.level --DEBUG openflow.of_01 --port=6633 forwarding.l3_learning
```

![](./figs/1startcontroller.png)

3. Open a new terminal and start mininet topology
```bash
cd loopgenexp/ControllerFeasibility-pox/l3/
sudo python3 -E LoopGen_topo_l3.py
```
![](./figs/2starttopology.png)


4. Open the host terminals in mininet
```bash
mininet> xterm h1 h2 h3
```

![](./figs/2.5hosts.png)

5. Send packets in each host terminal
```bash
# Node: h1
python3 LoopGen_packets_l3.py h1-eth0 10.0.0.2
# Node: h2
python3 LoopGen_packets_l3.py h2-eth0 10.0.0.3
# Node: h3
python3 LoopGen_packets_l3.py h3-eth0 10.0.0.1
```
![](./figs/3open3hosts.png)

Please **wait** until all hosts finshed the attack (as shown in the above figure).

6. Open a new terminal and start wireshark. Then, monitor the **s1-eth2** port.
```bash
sudo wireshark
```

![](./figs/4startwireshark.png)

7. For convenience, filter only arp packets. You can see that the attack packets are looped continuously.

![](./figs/5monitornic.png)

