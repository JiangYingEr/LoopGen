## Usage
If the Soot version in the SVHunter configuration file (SVHunter-master/tracer/pom.xml) is too low, you may consider using the provided [pom.xml](pom.xml).

Compile the analysis tool
```bash
cd ~/SVHunter-master/tracer
mvn clean package
```

Running analysis
```bash
java -jar target/SVHunter-Tracer-0.1-SNAPSHOT-jar-with-dependencies.jar \
    ~/onos \
    config/onosEnv.cfg \
    config/onosSensitiveMethodList.xml \
    config/onosDFMethodList.xml
```
