# BMv2

This directory is the evaluation of LoopGen's feasibility using BMv2 switches. The evaluation using OpenFlow switches can refer to the AcrossController directory.

## Environment
The official P4 VM Ubuntu20.04. [Download](https://github.com/p4lang/tutorials?tab=readme-ov-file)

## 1. Run network

Download this directory in the P4-VM (suggesting the p4/tutorial/execise/ directory in the official VM).

Open a terminal, compile and run:

    make

If find any compiling errors related to p4utils, please delete it (rm -rf p4utils) and reinstall [P4utils](https://nsg-ethz.github.io/p4-utils/installation.html). 

## 2. Run controller

Open another terminal

    sudo python3 controller.py


## 3. Start Evaluation

### 3.1 LoopGen

The forwarding loop is already achieved in rules/. Therefore, you can directly launch LoopGen

### 3.2 non-looping DoS



## 4.  Change topoloy

If you want to use different topologies, plese edit the Makefile file and specify the topology file (.py) in it
