# Note: this code can only run on Barefoot Tofino hardware switches. Due to the configuration differences (e.g., the directory name), the following instructions may need to be modified.

Run the commands below on Tofino.

### 1. set SDE:

    cd /root/bf-sde-9.10.0
    source set_sde.bash

### 2. Load SDE

    $SDE_INSTALL/bin/bf_kdrv_mod_load $SDE_INSTALL
    ls /dev/bf0

### 3. Set compile dir

    cd pkgsrc/p4-examples/programs
    mkdir <your name>
    cd <your name>

### 4. Set the compile file

    cmake $SDE/p4studio/ -DCMAKE_INSTALL_PREFIX=$SDE_INSTALL \
    -DCMAKE_MODULE_PATH=$SDE/cmake \
    -DP4_NAME=dfa \
    -DP4_PATH=/root/bf-sde-9.10.0/pkgsrc/p4-examples/programs/<your name>/loop.p4

### 5. Make

    make <your name>
    make install

### 6. Run

    cd $SDE
    ./run_switchd.sh -p <program name>

