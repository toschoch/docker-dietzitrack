FROM shocki/rpi-alpine-opencv-python3:latest
MAINTAINER Tobias Schoch <tobias.schoch@helbling.ch>

# Install dependencies
# install facerec
COPY requirements.txt /
RUN pip install facerec>=0.1.5 --index-url=http://dietzi.ddns.net:3141/dietzi/stable --trusted-host dietzi.ddns.net \
    && pip install -r requirements.txt --index-url=http://dietzi.ddns.net:3141/dietzi/stable --trusted-host dietzi.ddns.net

# Define working directory
COPY track.py /
COPY mqtt.py /
COPY starttrack.sh /
RUN mkdir /data && chmod +x /starttrack.sh
#COPY hc/ /hc
VOLUME /data
WORKDIR /

CMD ["/starttrack.sh"]