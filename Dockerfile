FROM sgtwilko/rpi-raspbian-opencv
MAINTAINER Tobias Schoch <tobias.schoch@helbling.ch>

# Install dependencies
# install facerec
COPY requirements.txt /
RUN pip3 install python_facerec --index-url=http://dietzi.ddns.net:3141/dietzi/staging \
    && pip3 install -r requirements.txt --index-url=http://dietzi.ddns.net:3141/dietzi/stable

# Define working directory
RUN usermod -a -G video root
COPY track.py /
COPY mqtt.py /
COPY starttrack.sh /
RUN mkdir /data && chmod +x /starttrack.sh
VOLUME /data
WORKDIR /

CMD ["/starttrack.sh"]