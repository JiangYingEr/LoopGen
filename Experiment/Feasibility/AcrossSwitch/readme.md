# Usage

1. Open a terminal (entering the p4 directory by defailt). 

<div align="center">
  <img src="./figs/0.png" width="80%" alt="">
</div>

2. Enter a new directory and start the topology:
```
    cd tutorials/exercises/LoopGen/
    make
```
<div align="center">
  <img src="./figs/1starttopology.png" width="80%" alt="">
</div>

Then, the topology is correctly started as follows.

<div align="center">
  <img src="./figs/1.5.png" width="80%" alt="">
</div>

If find any compiling errors, please try:
```
    make clean
    make
```
3. Open another terminal and start the controller
```
    cd tutorials/exercises/LoopGen/
    sudo python3 controller.py
```
<div align="center">
  <img src="./figs/2startcontroller.png" width="80%" alt="">
</div>

4. In the mininet terminal
```
    xterm h1 h2 h3
```
In h1 xterm, run
```
    python3 hack_h1_auto.py
```
In h2 xterm, run
```
    python3 hack_h2_auto.py
```
In h3 xterm, run
```
    python3 hack_h3_auto.py
```
<div align="center">
  <img src="./figs/3open3hosts.png" width="80%" alt="">
</div>

Please **wait** until they finished the attack.

5. Open a new terminal and start wireshark. Then, monitor the **s1-eth2** port.
```bash
sudo wireshark
```

<div align="center">
  <img src="./figs/4startwireshark.png" width="80%" alt="">
</div>

You can see that the attack packets are looped continuously.

<div align="center">
  <img src="./figs/5.png" width="80%" alt="">
</div>


