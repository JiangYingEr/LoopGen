# Usage

## 1. Download the source code of POX and install

## 2. Patse apps
copy the l2_learning.py file to pox/pox/forwarding/

## 3. Start the controller
```bash
./pox.py log.level --DEBUG openflow.of_01 --port=6633 forwarding.l2_learning
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

