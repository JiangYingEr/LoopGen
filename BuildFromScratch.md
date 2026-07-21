# Build LoopGen From Scratch

This document explains how to rebuild the LoopGen environment without using the ready-to-run VM image. The process starts from the official p4l VM (Ubuntu 20.04) [(Download)](https://github.com/p4lang/tutorials?tab=readme-ov-file), and then installs only the extra components needed by each experiment. 



## 1. Get the base VM


Please first obtain the official Ubuntu 20.04 VM, then import it into [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

After booting the VM, log in as:

```text
username: p4
password: p4
```

This VM already provides the BMv2 / p4 / Mininet  used by the experiments.


## 2. Experiment/Feasibility
<!-- 
This is the first experiment family to prepare, because several later experiments reuse the same BMv2 or controller environment. -->


Install the extra Ubuntu packages used by the BMv2 feasibility experiments:

```bash
sudo apt update
sudo apt install -y \
  git curl wget  \
  openvswitch-switch \
  tcpreplay iperf 
```



Install the common Python packages used by the experiments:

```bash
sudo python3 -m pip install --upgrade pip setuptools wheel
sudo python3 -m pip install \
  scapy==2.5.0 \
  networkx==3.1 \
  numpy==1.24.4 \
  pandas \
  scipy \
  matplotlib \
  distfit \
  protobuf==3.20.3 \
  grpcio==1.44.0 \
  eventlet==0.30.2
```

Install `p4-utils`, which is needed by several BMv2 experiments (you should enter the directory in which you want to install p4utils):

```bash
git clone https://github.com/nsg-ethz/p4-utils.git ~/p4-utils
cd ~/p4-utils
sudo ./install.sh
```

### 2.2 Feasibility/Prerequisite

This sub-experiment only needs the Python scientific stack above. No extra VM-side installation is required.


### 2.3 Feasibility/AcrossSwitch

Copy the runnable files into the location expected by its readme:

```bash
mkdir -p ~/tutorials/exercises/LoopGen
cp -r [artifact path]/Experiment/Feasibility/AcrossSwitch/. \
      ~/tutorials/exercises/LoopGen/
```

After this, the experiment can be run from:

```bash
cd ~/tutorials/exercises/LoopGen
```


### 2.4 Feasibility/AcrossController/Ryu

Install Ryu:

```bash
git clone https://github.com/faucetsdn/ryu.git ~/ryu
cd ~/ryu
git checkout v4.34
sudo python3 install -r tools/pip-requires
sudo python3 setup.py install
```

Copy the LoopGen-modified Ryu app files:

```bash
cp [artifact path]/Experiment/Feasibility/AcrossController/Ryu/simple_switch*.py ~/ryu/ryu/app/
```

Create the runtime directory expected by the readme:

```bash
mkdir -p ~/loopgenexp/ControllerFeasibility-ryu
cp -r [artifact path]/Experiment/Feasibility/AcrossController/Ryu/.  ~/loopgenexp/ControllerFeasibility-ryu/
```

### 2.5 Feasibility/AcrossController/POX

Clone POX:

```bash
git clone https://github.com/noxrepo/pox.git ~/pox
```

Replace the learning apps with the LoopGen versions:

```bash
cp [artifact path]/Experiment/Feasibility/AcrossController/POX/l2/l2_learning.py  ~/pox/pox/forwarding/
cp [artifact path]/Experiment/Feasibility/AcrossController/POX/l3/l3_learning.py  ~/pox/pox/forwarding/
```

Create the runtime directories expected by the readmes:

```bash
mkdir -p ~/loopgenexp/ControllerFeasibility-pox/l2
cp -r [artifact path]/Experiment/Feasibility/AcrossController/POX/l2/.  ~/loopgenexp/ControllerFeasibility-pox/l2/

mkdir -p ~/loopgenexp/ControllerFeasibility-pox/l3
cp -r [artifact path]/Experiment/Feasibility/AcrossController/POX/l3/.  ~/loopgenexp/ControllerFeasibility-pox/l3/
```

### 2.6 Feasibility/AcrossController/ONOS

Install the ONOS-specific packages:

```bash
sudo apt install -y openjdk-11-jdk npm
```

Install Bazelisk so that `bazel` follows the version requested by `.bazelversion`:

```bash
cd /tmp
wget https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64
chmod +x bazelisk-linux-amd64
sudo mv bazelisk-linux-amd64 /usr/local/bin/bazel
```

Clone ONOS:

```bash
git clone https://github.com/opennetworkinglab/onos.git 
```

The ONOS tree we tested contains:

```bash
cd ~/onos
```


Copy the LoopGen-modified forwarding app files into ONOS:

```bash
cp [artifact path]/Experiment/Feasibility/AcrossController/ONOS/*.java \
   ~/onos/apps/fwd/src/main/java/org/onosproject/fwd/
```

Create the runtime directory expected by the ONOS readme:

```bash
mkdir -p ~/loopgenexp/ControllerFeasibility-onos
cp -r [artifact path]/Experiment/Feasibility/AcrossController/ONOS/. \
      ~/loopgenexp/ControllerFeasibility-onos/
```





## 3. Experiment/AmplificationEffect



Copy the runnable files into the location expected by its readme:

```bash
mkdir -p ~/tutorials/exercises/AmplificationEffect
cp -r [artifact path]/Experiment/AmplificationEffect/. \
      ~/tutorials/exercises/AmplificationEffect/
```



## 4. Experiment/Cost


Copy the runnable files into the location expected by its readme:

```bash
mkdir -p ~/tutorials/exercises/Cost
cp -r [artifact path]/Experiment/Cost/. \
      ~/tutorials/exercises/Cost/
```


## 5. Experiment/Stealthiness

This experiment family mixes BMv2, Ryu, ONOS, and Java-based analysis tools.

### 5.1 Stealthiness/IdentityVerification

This experiment reuses the Ryu installation from Section 2.4.

Copy the modified Ryu app:

```bash
cp [artifact path]/Experiment/Stealthiness/IdentityVerification/switchfix.py \
   ~/ryu/ryu/app/
```

Create the runtime directory:

```bash
mkdir -p ~/loopgenexp/identityverification
cp -r [artifact path]/Experiment/Stealthiness/IdentityVerification/. \
      ~/loopgenexp/identityverification/
```

### 5.2 Stealthiness/Lemon

This experiment reuses the BMv2 and `p4-utils` environment from Section 2.1.

Copy the runnable files:

```bash
mkdir -p ~/tutorials/exercises/lemon
cp -r [artifact path]/Experiment/Stealthiness/Lemon/. \
      ~/tutorials/exercises/lemon/
```

Download the background traffic from MAWI. What we use is the [202201011400.pcap](https://mawi.wide.ad.jp/mawi/samplepoint-F/2022/202201011400.html)

Run it from:

```bash
cd ~/tutorials/exercises/lemon
```

If `sudo p4run` later fails, first check:

```bash
pip3 show p4utils
python3 -c "import p4utils; print(p4utils.__file__)"
```

### 5.3 Stealthiness/SISTAR


Copy the runnable files:

```bash
mkdir -p ~/tutorials/exercises/sistar
cp -r [artifact path]/Experiment/Stealthiness/SISTAR/. \
      ~/tutorials/exercises/sistar/
```

Run it from:

```bash
cd ~/tutorials/exercises/sistar
```

If `attack.pcap` is missing at runtime, the experiment directory already provides:

```bash
python3 packet_gen.py
```

### 5.4 Stealthiness/EventScope

This experiment depends on the ONOS environment from Section 2.6.

Install the base packages if they are not already present:

```bash
sudo apt install -y openjdk-8-jdk maven graphviz
```

Place the [EventScope](https://github.com/bujcich/EventScope) source tree under:

```text
~/EventScope-master
```

Replace the analyzer module's `pom.xml` with ours and build it with JDK 8:

```bash
cp [artifact path]/Experiment/Stealthiness/EventScope/pom.xml \
   ~/EventScope-master/onos-infoflow/pom.xml

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

cd ~/EventScope-master/onos-infoflow
mvn clean package -DskipTests
```

Build the ONOS artifacts consumed by EventScope:

```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

cd ~/onos
bazel build //core/api:onos-api
bazel build //apps/fwd:onos-apps-fwd-oar
```

Prepare the forwarding app and the implementation jars expected by `onos-infoflow`:

```bash
export ANALYZER_JAR=~/EventScope-master/onos-infoflow/target/onos-infoflow-0.0.1-SNAPSHOT.jar

mkdir -p ~/EventScope-master/target_app
sudo cp ~/onos/bazel-bin/apps/fwd/onos-apps-fwd-oar.oar \
   ~/EventScope-master/target_app/fwd_app.zip

cd ~/EventScope-master/target_app
unzip -q -o fwd_app.zip

mkdir -p ~/EventScope-master/onos-infoflow/bin-impl
sudo cp ~/onos/bazel-bin/core/api/libonos-api.jar \
   ~/EventScope-master/onos-infoflow/bin-impl/
sudo cp ~/onos/bazel-bin/core/net/libonos-core-net.jar \
   ~/EventScope-master/onos-infoflow/bin-impl/

cd ~/EventScope-master/onos-infoflow/bin-impl
unzip -q -o libonos-api.jar
unzip -q -o libonos-core-net.jar
rm *.jar
```

Prepare the runtime dictionaries and Java 8 classes used by EventScope:

```bash
cp -r ~/EventScope-master/onos-infoflow/java_rt ~/EventScope-master/

cp ~/EventScope-master/onos-infoflow/apiReads.txt  ~/EventScope-master/
cp ~/EventScope-master/onos-infoflow/apiWrites.txt ~/EventScope-master/
cp ~/EventScope-master/onos-infoflow/dataIn.txt    ~/EventScope-master/
cp ~/EventScope-master/onos-infoflow/dataOut.txt   ~/EventScope-master/
```

Run the analyzer:

```bash
cd ~/EventScope-master
java -jar $ANALYZER_JAR
```

If you also want to run `onos-event-use`, install its Python 3 dependencies, update `event-use.py` to the Python 3 compatible version from our reproduction notes:

```bash
cp [artifact path]/Experiment/Stealthiness/EventScope/event-use.py \
   ~/EventScope-master/onos-event-use/event-use.py

cd ~/EventScope-master/onos-event-use
pip3 install pandas numpy networkx matplotlib scipy
python3 event-use.py
```

### 5.5 Stealthiness/SVHunter

This experiment also depends on the ONOS environment from Section 2.6, and uses JDK 8 plus Maven.

Clone SVHunter if it is not already present:

```bash
git clone https://github.com/xiaofen9/SVHunter.git ~/SVHunter-master
```

Replace its `pom.xml`:

```bash
cp [artifact path]/Experiment/Stealthiness/SVHunter/pom.xml \
   ~/SVHunter-master/tracer/pom.xml
```

Switch to JDK 8 and try to build:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

cd ~/SVHunter-master/tracer
mvn clean package -DskipTests
```

If Maven reports `package javafx.util does not exist`, apply the workaround used in our setup. Installing `openjfx` alone was not sufficient in our Ubuntu 20.04 / JDK 8 environment.

```bash
cd ~/SVHunter-master/tracer
cp -r src src.bak

mkdir -p src/main/java/util
cat > src/main/java/util/Pair.java << 'EOF'
package util;

public class Pair<K, V> {
    private final K key;
    private final V value;

    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }

    public K getKey() {
        return key;
    }

    public V getValue() {
        return value;
    }

    @Override
    public String toString() {
        return key + "=" + value;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Pair)) return false;
        Pair<?, ?> p = (Pair<?, ?>) o;
        return (key == null ? p.key == null : key.equals(p.key))
            && (value == null ? p.value == null : value.equals(p.value));
    }

    @Override
    public int hashCode() {
        int h1 = (key == null) ? 0 : key.hashCode();
        int h2 = (value == null) ? 0 : value.hashCode();
        return h1 * 31 + h2;
    }
}
EOF

cd src/main/java
find . -name "*.java" -exec sed -i 's|import javafx.util.Pair;|import util.Pair;|g' {} +

cd ~/SVHunter-master/tracer
mvn clean package -DskipTests
```

The built jar is expected at:

```text
~/SVHunter-master/tracer/target/SVHunter-Tracer-0.1-SNAPSHOT-jar-with-dependencies.jar
```

## 6. Experiment/defense

This experiment reuses the Ryu environment from Section 2.4.

Copy the countermeasure applications:

```bash
cp [artifact path]/Experiment/defense/loop_detect_13.py \
   ~/ryu/ryu/app/E
cp [artifact path]/Experiment/defense/time_constraint_13.py \
   ~/ryu/ryu/app/
cp [artifact path]/Experiment/defense/loopgen_countermeasure_base.py \
   ~/ryu/ryu/app/
```

No extra system dependency is needed beyond the Ryu environment already installed for feasibility.

## 7. Experiment/DistributionFitting

This experiment only needs the Python scientific stack already installed in Section 2.1.

Run it directly in place:

```bash
cd "[artifact path]/Experiment/DistributionFitting"
```

The top-level directory contains scripts such as `Phost.py`, `LSandFT.py`, and `Probability.py`. The `tc`, `th`, and `tl` subdirectories provide the fitting scripts used to obtain the values later consumed by `Probability.py`.

For the `th` case, the directory `th/AfterRevision` contains the updated method used after revision.

