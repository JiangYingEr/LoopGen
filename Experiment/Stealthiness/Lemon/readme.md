# Evaluate LoopGen using Lemon

The version of [Lemon](https://github.com/f-555/Lemon) we obtained and used is in Janurary 2026.

## Environment

1. Download Lemon and enter its lemon_bmv2 directory.
   
2. Copy the files in This directory to the lemon_bmv2 directory. If there are files with the same name, *overwrite* them.
  
3. Start the BMv2-based Mininet experimental environment

    >sudo p4run

4. Start the Lemon controller
   
    >sudu python3 /controlplane/lemon_controller/controller.py

## Lemon Defense Test
1.Use a Python script to generate attack packets targeting a specific destination host
>python3 generatepcap.py

2.In the Mininet host terminal, inject background traffic and attack traffic separately, ensuring they overlap in time
>tcpreplay -i <interface> --duration=4 <background_traffic.pcap> &
tcpreplay -i <interface> --pps=3200 --duration=4 --loop=0 <attack_traffic.pcap>

## Result Analysis
1.Run the controller script to collect statistics from the data plane and perform DDoS detection
>sudo python3 controller.py

2.Evaluate the system performance using two metrics: Precision and Recall


