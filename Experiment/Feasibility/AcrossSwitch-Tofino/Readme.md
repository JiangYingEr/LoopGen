## Notes for Evaluators


This folder documents a supplementary feasibility experiment on Barefoot Tofino switches. In the paper, this is a **MINOR** case study and is **NOT** required for reproducing the other results. Since our Tofino testbed is deployed inside the campus network and is currently accessible only to authorized users, we are applying for external access for evaluators.

We would like to note that:
- The experiment itself is lightweight and only involves fixed-port packet forwarding on Tofino switches.
- The same forwarding behavior has been verfied by the BMv2 switch.

Please modify `loop.p4` according to the port number of each switch.

    ig_intr_tm_md.ucast_egress_port = 19; 

Please use the correct port number.

On the Tofino switch, run the commands below.

### 1. set SDE:

    cd /root/bf-sde-9.10.0
    source set_sde.bash

### 2. Load SDE

    $SDE_INSTALL/bin/bf_kdrv_mod_load $SDE_INSTALL
    ls /dev/bf0

### 3. Set compile dir

    cd pkgsrc/p4-examples/programs
    mkdir loop
    cd loop

### 4. Set the compile file

    cmake $SDE/p4studio/ -DCMAKE_INSTALL_PREFIX=$SDE_INSTALL \
    -DCMAKE_MODULE_PATH=$SDE/cmake \
    -DP4_NAME=dfa \
    -DP4_PATH=/root/bf-sde-9.10.0/pkgsrc/p4-examples/programs/loop/loop.p4

### 5. Make

    make loop
    make install

### 6. Run P4

    cd $SDE
    ./run_switchd.sh -p loop

### Send packet

    test.py
