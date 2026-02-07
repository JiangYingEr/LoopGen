## 1. Start the Ryu controller
Paste the switchfix.py to the ryu/app/ directory.

Open a terminal (Controller Terminal).

```plain
sudo ryu-manager switchfix.py
```

## 2. Start the Mininet topology
Open a second terminal (Topology Terminal).

```plain
sudo python3 topology.py
```

## 3. Open host xterms

```plain
mininet> xterm h1 h2 h3
```

## 4. Start the responder (host authentication responder) on each host

These scripts are used to handle controller's identity verification

In the `h1` xterm:

```plain
sudo python3 responder1.py h1-eth0
```

In the `h2` xterm:

```plain
sudo python3 responder2.py h2-eth0
```

In the `h3` xterm:

```plain
sudo python3 responder3.py h3-eth0
```


## 5. Start LoopGen attack scripts
In `h1` xterm run the h1 attack:

```plain
sudo python3 hack_h1_auto.py
```

In `h2` xterm:

```plain
sudo python3 hack_h2_auto.py
```

In `h3` xterm:

```plain
sudo python3 hack_h3_auto.py
```

