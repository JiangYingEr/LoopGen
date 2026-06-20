## Usage 

1. Open a terminal (entering the p4 directory by defailt). 

![](./figs/0.png)

2. Enter a new directory and start the topology:

    cd tutorials/exercises/Cost/

    make

![](./figs/1starttopology.png)

Then, the topology is correctly started as follows.

![](./figs/1.5.png)


### Launch LoopGen

1. First, open an h1 xterm

    mininet> xterm h1

Use `tcpreplay` to inject attack packets.

    h1> tcpreplay -i h1-eth0 -p 300 -l 0 LoopGen.pcap


![](./figs/tcpreplay.png)

2. Then, open a new h1 xterm and `ping` h2

    h1> ping 10.0.0.2


![](./figs/ping.png)

### Launch normal DoS

1. First, open an h1 xterm

    mininet> xterm h1

Use `tcpreplay` to inject attack packets. Note: use **normalDoS.pcap** instead of LoopGen.pcap. Increase the speed (`-p`) gradually (5,000, 10,000, 15,000, 20,000, ...) until the latency reaches the same level under LoopGen. Then, the speed of tcpreplay is the cost.

    h1> tcpreplay -i h1-eth0 -p 5000 -l 0 normalDoS.pcap


2. Then, open a new h1 xterm and `ping` h2

    h1> ping 10.0.0.2

5000pps, normal DoS
![](./figs/5000.png)


15000pps, normal DoS
![](./figs/15000.png)



