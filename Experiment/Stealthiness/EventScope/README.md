## Environment
```bash
sudo apt install openjdk-8-jdk maven -y
```


[EventScope](https://github.com/bujcich/EventScope) is built upon ONOS, so before running it, replace the ReactiveForwarding.java file in onos/apps/fwd/src/main/java/org/onosproject/fwd/ with our [ReactiveForwarding.java](../../Feasibility/AcrossController/ONOS)

## Usage
If the Soot version in the EventScope configuration file (EventScope-master/onos-infoflow/pom.xml) is too low, you may consider using the provided [pom.xml](pom.xml).

Compile the EventScope analysis tool
```bash
cd ~/EventScope-master/onos-infoflow
mvn clean package -DskipTests
export ANALYZER_JAR=$(pwd)/target/onos-infoflow-0.0.1-SNAPSHOT.jar
```

Prepare the target app
```bash
cd ~/onos
bazel build //apps/fwd:onos-apps-fwd-oar
mkdir -p ~/eventscope_workdir/target_app
cd ~/eventscope_workdir/target_app
cp ~/onos/bazel-bin/apps/fwd/onos-apps-fwd-oar.oar ~/eventscope_workdir/target_app/fwd_app.zip
unzip ~/eventscope_test/target_app/fwd_app.zip -d ~/eventscope_workdir/target_app/
```

Build an analytical environment
```bash
cd ~/eventscope_workdir

# Create the expected directory structure for EventScope
mkdir -p bin
mkdir -p java_rt

# Insert the class file of the target App
APP_JAR=$(find ./target_app -name "onos-apps-fwd-*.jar" | head -n 1)
echo "Found App Jar: $APP_JAR"

# Copy and extract the target App to the bin directory
cp "$APP_JAR" bin/
cd bin
unzip -q -o *.jar
rm *.jar

# Put it into the Java runtime environment
cd ..
cp /usr/lib/jvm/java-8-openjdk-amd64/jre/lib/rt.jar java_rt/
cd java_rt
unzip -q -o rt.jar
rm rt.jar
cd ..
```

Run static analysis
```bash
cd ~/eventscope_workdir
java -jar $ANALYZER_JAR
```
