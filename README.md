Dietzi IoT Track
===============================
author: Tobias Schoch

Overview
--------

A rasperry pi application for tracking persons and with a camera and sending statistics to MQTT


Change-Log
----------
##### 0.1.5
* included join process for gracefull stop
* fixed smaller bugs and updated to the facerec tracker callbacks refactoring
* use password
* added last will
* used callback for identification in separate thread
* added example conf for service
* added retaining
* improved mqtt topics
* read DOCKER_HOSTNAME for hostname
* included heartbeat and image publish
* switch to arm alpine for the cache plugin
* remove the arm for plugins
* try withouth mount
* try to use plugins on linux-arm
* add priviledged mode
* added logging to slots
* add drone cache
* test for amr docker plugin
* fixe newline
* fixed the image in docker step
* updated to multiarch ci/cd
* working on rpi3b+
* test that should work on rpi
* use base image with opencv
* working on picamera but sooooo slow
* added a mqtt module that connects on request only
* first tests on drone.yml
* updated to facerec v0.1.0
* add requirements
* opencv version logging to mqtt working
* update readme
* base raspi image and facerec dep

##### 0.0.1
* initial version


Installation / Usage
--------------------
clone the repo:

```
git clone https://github.com/toschoch/docker-dietzitrack.git
```
build the docker image
```
docker build . -t dietzitrack
```

Example
-------

run a container of the image
note the explicit declaration of the camera device
```
docker run -v ... -p ... --device=/dev/vcsm --device=/dev/vchiq  dietzitrack
```