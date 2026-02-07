# Usage

## 1. Download the source code of Ryu and install

## 2. Paste apps

Copy the simple_switch.py, simple_switch_12.py, simple_switch_13.py, simple_switch_14.py, simple_switch_15.py in this directory to the ryu/app/ directory in Ryu's source code.

If ryu/app/ already contains these apps, plese **replace** them.

Note that our codes only additionally contains the address-location mapping of h1 h2 h3, not changing the inherent address learning logic. This is to make the experiment easy to conduct.

## 3. Start the controller (using simple_switch_13.py as an example)
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
