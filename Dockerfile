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
WORKDIR /data
VOLUME /data

CMD ["/bin/bash"]