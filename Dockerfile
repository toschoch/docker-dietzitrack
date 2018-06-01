FROM sgtwilko/rpi-raspbian-opencv
MAINTAINER Tobias Schoch <tobias.schoch@helbling.ch>

# Install dependencies
COPY requirements.txt /
RUN apt-get update && apt-get install -y \
    git-core \
    cmake \
    && pip3 install -e git+https://github.com/toschoch/python-facerec.git@v0.1.0#egg=python-facerec \
    && pip3 install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Define working directory
RUN usermod -a -G video root
COPY track.py /
COPY mqtt.py /
COPY starttrack.sh /
RUN mkdir /data && chmod +x /starttrack.sh
VOLUME /data
WORKDIR /

CMD ["/starttrack.sh"]