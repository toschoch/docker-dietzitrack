#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 04.05.2018
# author:  TOS

import logging
import logging.handlers
import time
import json
import platform
import numpy as np
from mqtt import MQTTClient


mqtt_server = "localhost"
facerec_server_url = "http://localhost:8081"


def camera_raspi(log, **kwargs):
    import picamera
    import picamera.array

    with picamera.PiCamera() as camera:
        #camera.use_video_port=True
        time.sleep(1)
        with picamera.array.PiRGBArray(camera) as stream:
            log.info("raspberry pi camerea initialized! entering main loop...")
            while True:
                camera.capture(stream, format='bgr', use_video_port=True)
                img = np.array(stream.array).copy()
                faces = main_loop(img, **kwargs)
                # reset the stream before the next capture
                stream.seek(0)
                stream.truncate()
                log.info("next frame...")


def camera_opencv(**kwargs):

    import cv2
    cam = cv2.VideoCapture(0)
    color_green = (0, 255, 0)
    line_width = 3

    try:
        while True:
            ret_val, img = cam.read()
            faces = main_loop(img, **kwargs)
            for face in faces:
                coords = face.coords();
                cv2.rectangle(img, (coords[0], coords[1]), (coords[2], coords[3]), color_green, line_width)
                cv2.putText(img, face.name('not identified'), (coords[0], coords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow('my webcam', img)
            if cv2.waitKey(1) == 27:
                break  # esc to quit
    finally:
        cv2.destroyAllWindows()


def main(log):

    location_topic = 'sensors/door/persons'

    mqttc = MQTTClient(mqtt_server, client_id=str(platform.node()))

    def on_appearance(face):
        face = face.copy()
        face.pop('coords')

        if face.pop('identified'):
            payload = {'time': face['appeared'], 'present': 1}
            mqttc.publish('{loc}/presence/{id}'.format(loc=location_topic, id=face['face_id']), qos=1,
                          payload=json.dumps(payload), retain=True)
            if face['name'] != 'unknown':
                mqttc.publish('{loc}/presence/{name}'.format(loc=location_topic, name=face['name']), qos=1,
                              payload=json.dumps(payload), retain=True)

        del face['id']
        del face['disappeared']
        face['time'] = face.pop('appeared')
        mqttc.publish('{loc}/appeared'.format(loc=location_topic), qos=1, payload=json.dumps(face))

    def on_disappearance(face):
        face = face.copy()
        face.pop('coords')

        if face.pop('identified'):
            payload = {'time': face['disappeared'], 'present': 0}
            mqttc.publish('{loc}/presence/{id}'.format(loc=location_topic, id=face['face_id']), qos=1,
                          payload=json.dumps(payload), retain=True)
            if face['name'] != 'unknown':
                mqttc.publish('{loc}/presence/{name}'.format(loc=location_topic, name=face['name']), qos=1,
                              payload=json.dumps(payload), retain=True)

        del face['id']
        face['time'] = face.pop('disappeared')
        mqttc.publish('{loc}/disappeared'.format(loc=location_topic), qos=1, payload=json.dumps(face))

    # setup logging
    from facerec.facetracker import FaceTracker
    from facerec import facedb

    try:
        tracker = FaceTracker(url=facerec_server_url)
        tracker.on_appearance = on_appearance
        tracker.on_disappearance = on_disappearance

        # camera_opencv(tracker=tracker)
        camera_raspi(tracker=tracker, log=log, mqttc=mqttc)
        # camera_raspi(log=log, mqttc=mqttc)
    finally:
        # tracker.stop()
        facedb.close()

def main_loop(img, tracker, **kwargs):
    return tracker.update(img)

if __name__ == '__main__':
    log = logging.getLogger("DietziTrack")
    logging.basicConfig(level=logging.DEBUG)
    log.info("Start tracking...")
    main(log)
    log.info("Stop tracking...")
