## 1. Start the Ryu controller
Open a terminal (Controller Terminal).

```plain
cd ~/ryu/ryu/app
sudo ryu-manager switchfix.py
```

**What to expect in the controller log:**

+ Startup messages and your app name.
+ After Mininet connects (step 2) you should later see lines like:

```plain
Installed table-miss on 0000000000000001
Installed table-miss on 0000000000000002
Installed table-miss on 0000000000000003
=== SimpleSwitch13Auth_Fixed started ===
Protected MAC: 00:00:00:00:00:08
```

If you see Python exceptions, stop and copy the error here for diagnosis.

---

## 2. Start the Mininet topology
Open a second terminal (Topology Terminal).

```plain
cd ~/Desktop/loopgen2
sudo python3 topology.py
```

This should drop you into the Mininet CLI (`mininet>` prompt). The topology script should create three switches and three hosts and connect them to the Ryu controller at `127.0.0.1:6633` (default).

**What to check:**

+ In the controller terminal you should see the `Installed table-miss` messages (switch features processed).
+ In Mininet CLI you should see the host and switch list.

---

## 3. Open host xterms
From the Mininet CLI prompt:

```plain
mininet> xterm h1 h2 h3
```

Three xterm windows should open — each xterm is a shell inside the corresponding Mininet host namespace. If `xterm` does not appear, make sure `xterm` is installed and your environment supports X forwarding.

---

## 4. Start the responder (host authentication responder) on each host
In the `h1` xterm:

```plain
cd /home/youruser/Desktop/loopgen2
sudo python3 responder1.py h1-eth0
```

In the `h2` xterm:

```plain
cd /home/youruser/Desktop/loopgen2
sudo python3 responder2.py h2-eth0
```

In the `h3` xterm:

```plain
cd /home/youruser/Desktop/loopgen2
sudo python3 responder3.py h3-eth0
```



If the responder does not print anything when you expect AUTH_REQUESTs, use tcpdump on that host (next section) to confirm packet delivery.

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

