# Usage

## 1. Download the source code of ONOS and install

## 2.  Paste apps
Copy the ReactiveForwarding.java app in this directory to onos/apps/fwd/src/main/java/org/onosproject/fwd/ and replace the original file


## 3. Start the controller
```bash
bazel run onos-local -- clean debug
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

