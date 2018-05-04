Dietzi IoT Track
===============================
author: Tobias Schoch

Overview
--------

A rasperry pi application for tracking persons and with a camera and sending statistics to MQTT


Change-Log
----------
##### 0.0.1
* initial version


Installation / Usage
--------------------
clone the repo:

```
git clone <git-url>
```
build the docker image
```
docker build . -t dietzitrack
```

Example
-------

run a container of the image
```
docker run -v ... -p ... dietzitrack
```