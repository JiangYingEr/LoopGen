# Usage

## 1. Download the source code of ONOS and install

Copy the ReactiveForwarding.java app


## 2. Start the controller
```bash
bazel run onos-local -- clean debug
```

## 3. Start mininet topology
```bash
sudo mn -c
sudo python3 -E LoopGen_topo.py
```
## 4. Open the host terminal
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

