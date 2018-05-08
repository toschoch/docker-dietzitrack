FROM resin/raspberry-pi-python:3
MAINTAINER Tobias Schoch <tobias.schoch@helbling.ch>

# Install dependencies
COPY requirements.txt /
RUN apt-get update && apt-get install -y \
    git-core \
    cmake \
    && pip3 install -e git+https://github.com/toschoch/python-facerec.git@v0.0.3#egg=python-facerec \
    && pip3 install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Define working directory
RUN mkdir /data && chmod +x /data && cd /data
COPY track.py /data
COPY starttrack.sh /data
WORKDIR /data
VOLUME /data

CMD ["/starttrack.sh"]