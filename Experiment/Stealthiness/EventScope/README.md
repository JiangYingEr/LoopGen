## Usage

Before starting, please **download** our VM.


The default JDK is 11, so firstly, please switch to JDK 8.

```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
java -version
```

<div align="center">
  <img src="./figs/jdk.png" width="80%" alt="">
</div>


```bash
cd ~/EventScope-master
export ANALYZER_JAR=/home/p4/EventScope-master/onos-infoflow/target/onos-infoflow-0.0.1-SNAPSHOT.jar
java -jar $ANALYZER_JAR
```

<div align="center">
  <img src="./figs/-1.png" width="80%" alt="">
</div>

You can directly see the .pdf report 

<div align="center">
  <img src="./figs/-2.png" width="80%" alt="">
</div>

We can see that the attack does not introduce new event listeners or data plane interaction paths in the graph. This is because it merely adds static mappings to the existing event handling logic, thereby altering the forwarding semantics but not the event flow structure. Therefore, EventScope cannot detect it.

<div align="center">
  <img src="./figs/-3.png" width="80%" alt="">
</div>