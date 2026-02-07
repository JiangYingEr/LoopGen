# Amplification Effect evaluation

This directory is the evaluation of LoopGen's amplification effect.

## Environment
The official P4 VM Ubuntu20.04. [Download](https://github.com/p4lang/tutorials?tab=readme-ov-file)

## 1. Run network

Download this directory in the P4-VM (suggesting the p4/tutorial/execise/ directory in the official VM).

Open a terminal, compile and run:

    make

If find any compiling errors related to p4utils, please delete it (rm -rf p4utils) and reinstall [P4utils](https://nsg-ethz.github.io/p4-utils/installation.html). 


## 2. Start Evaluation


The flow rules in /rules have formed a forwarding loop for destination IP 10.0.0.8. The example speed is 300 pps, you can change it at will.

    mininet> xterm h1

    h1>  tcpreplay -i eth0 -p 300 -l 0 LoopGen.pcap



## 3. Metric


### 3.1 Amplification factor

Use tcpreplay to send only one packet and use wireshark to observe how many times it passed through s1-eth2.

### 3.2 RTT

Use h1 to ping h2 and observe the RTT

### 3.3 Throughput

h2 is the iperf server while h1 is the iperf client.

## 4. Change topo

Edit the Makefile file to specify the topology.
