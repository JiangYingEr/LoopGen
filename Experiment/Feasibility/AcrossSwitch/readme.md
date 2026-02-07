# Start

## Environment
The official P4 VM Ubuntu20.04. [Download](https://github.com/p4lang/tutorials?tab=readme-ov-file)

## Run network

Download this directory in the P4-VM (suggesting the p4/tutorial/execise/ directory in the official VM).

Open a terminal, compile and run:

    make

If find any compiling errors related to p4utils, please delete it (rm -rf p4utils) and reinstall [P4utils](https://nsg-ethz.github.io/p4-utils/installation.html). 

## Run controller

Open another terminal

    sudo python3 controller.py


## Send packet

In the mininet terminal

    xterm h1 h2 h3

In h1 xterm, run

    python3 hack_h1_auto.py

In h2 xterm, run

    python3 hack_h2_auto.py

In h3 xterm, run

    python3 hack_h3_auto.py
