#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 04.05.2018
# author:  TOS

import logging.handlers
import time
import os
import json

from mqtt import MQTTClient, MQTTMock


mqtt_server = "192.168.0.40"
facerec_server_url = "http://192.168.0.40:3080"

hostname = os.environ['DOCKER_HOSTNAME']

def camera_opencv(tracker, **kwargs):

    log = kwargs['log']
    mqttc = kwargs['mqttc']

    import cv2
    cam = cv2.VideoCapture(0)

    # color_green = (0, 255, 0)
    # line_width = 3

    app_topic = 'device/{}/dietzitrack'.format(str(hostname))
    webcam_topic = 'webcam/door'

    interval_fps = 1
    interval_webcam = 5

    try:
        log.info("opencv camera initialized! entering main loop...")
        t0_1 = time.time()
        t0_2 = t0_1
        fps = 0
        while True:
            ret_val, img = cam.read()
            tracker.update(img)
            fps += 1
            t = time.time()
            if t-t0_1>=interval_fps:
                t0_1 = t
                mqttc.publish(app_topic, qos=1, payload=json.dumps({'status':'active','fps':fps}), retain=True)
            if t-t0_2>=interval_webcam:
                t0_2 = t
                mqttc.publish(webcam_topic, qos=1, payload=cv2.imencode('.jpg', img)[1].tostring(), retain=True)
    finally:
        mqttc.publish(app_topic, qos=1, payload=json.dumps({'status': 'stopped', 'fps': fps}), retain=True)
        # cv2.destroyAllWindows()


def main(log):

    location_topic = 'sensors/door/persons'

    mqttc = MQTTClient(mqtt_server, client_id=str(hostname))

    def on_identifaction(face):
        face = face.copy()
        face.pop('coords')

        payload = {'time': face['appeared'], 'present': 1}
        mqttc.publish('{loc}/presence/{id}'.format(loc=location_topic, id=face['face_id']), qos=1,
                      payload=json.dumps(payload), retain=True)
        if face['name'] != 'unknown':
            mqttc.publish('{loc}/presence/{name}'.format(loc=location_topic, name=face['name']), qos=1,
                          payload=json.dumps(payload), retain=True)

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
        tracker = FaceTracker(url=facerec_server_url, identification_interval=1, missing_tolerance_nframes=3)
        tracker.on_identification = on_identifaction
        tracker.on_disappearance = on_disappearance

        camera_opencv(tracker=tracker, log=log, mqttc=mqttc)
    finally:
        # tracker.stop()
        facedb.close()

if __name__ == '__main__':
    log = logging.getLogger("DietziTrack")
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
    log.info("Start tracking...")
    main(log)
    log.info("Stop tracking...")
