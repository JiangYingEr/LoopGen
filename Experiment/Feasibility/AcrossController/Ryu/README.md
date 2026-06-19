# Usage

## 1. Open a terminal 
```bash
ryu-manager simple_switch_13.py
```

## 4. Start mininet topology
```bash
sudo mn -c
sudo python3 -E LoopGen_topo.py
```
Open the host terminal
```bash
mininet> xterm h1 h2 h3
```


In h1 xterm, run

    python3 hack_h1_auto.py

In h2 xterm, run

    python3 hack_h2_auto.py

In h3 xterm, run

    python3 hack_h3_auto.py

These scripts will automatically try until the forwarding loop is created.
