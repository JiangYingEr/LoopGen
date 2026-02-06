# Sistar：Detecting DDoS Attacks and Performing Countermeasure Defense in the Programmable Data Plane Using Machine Learning

## Introduction
This document provides a detailed record of the testing procedure, environment configuration, and result verification methods for the SISTAR defense system.
 The document is divided into three main parts:

1.Experimental Environment

2.SISTAR Defense Test

3.Result Verification

### Experimental Environment
1.Train the DT-CTS Model
> python3 DT-CTS.py

2.Copy the BMv2 directory into tutorials/exercises/

3.Enter the BMv2 Directory
>cd BMv2

4.Start the BMv2 Software Switch
>p4@p4:~/tutorials/exercises/BMv2$ make

5.Load Flow Table Entries for Testing
>p4@p4:~/tutorials/exercises/BMv2$ ./entry-h1-h2.sh

6.Test Connectivity Between Hosts h1 and h2 in Mininet
>mininet> h1 ping h2

### SISTAR Defense Test
Before starting the test, we use Scapy to craft a specific attack packet and save it as a .pcap file, so that it can later be replayed at high speed using tcpreplay.
1.Install Flow Rules for the S1–S2–S3 Triangle Loop Topology
>simple_switch_CLI --thrift-port 9090 <<< "table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.99.99/32 => 00:00:00:00:02:00 2"

>simple_switch_CLI --thrift-port 9091 <<< "table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.99.99/32 => 00:00:00:00:03:00 3"

>simple_switch_CLI --thrift-port 9092 <<< "table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.99.99/32 => 00:00:00:00:01:00 4"

2.Modify and Deploy the Defense Mechanism Based on the Loop
>./run_defense.sh

3.Send Background Traffic and Attack Traffic
>h1 tcpreplay -i eth0 -p 500 -
L 10000 ./202201011400.pcap &

>tcpreplay -i eth0 -p 10000
 -l 20000 attack.pcap

### Result Verification
1.Open Wireshark and Monitor Interface s1-eth2
>sudo wireshark

2.Check Flow Table Entries
>simple_switch_CLI --thrift-port 9090 <<< "table_dump MyIngress.DDoS ternary"



