#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 04.05.2018
# author:  TOS

import logging.handlers
import time
import os
import json

from mqtt import MQTTClient, MQTTMock

app_name = "DietziTrack"

mqtt_server = os.environ.get('MQTT_SERVER','mqtt')
facerec_server_url = os.environ.get('FACEREC_SERVER','http://facerec:80')

location = os.environ.get('CAM_LOCATION','door')

# get password
if 'MQTT_PW' not in os.environ:
    mqtt_pw = open('run/secrets/mqtt_pw','r').read()
else:
    mqtt_pw = os.environ['MQTT_PW']

def camera_opencv(tracker, **kwargs):

    log = kwargs['log']
    mqttc = kwargs['mqttc']

    import cv2
    cam = cv2.VideoCapture(0)

    # color_green = (0, 255, 0)
    # line_width = 3

    app_topic = 'apps/{}'.format(app_name.lower())
    webcam_topic = 'webcams/{}'.format(location)

    interval_fps = 10
    interval_webcam = 5

    mqttc._client.will_set(app_topic, qos=1, payload=json.dumps({'status': 'stopped', 'fps': 0, 'location': location}), retain=True)
    mqttc.publish(app_topic, qos=1, payload=json.dumps({'status': 'active', 'fps': 0, 'location': location}), retain=True)

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
                mqttc.publish(app_topic, qos=1, payload=json.dumps({'status':'active','fps':fps/interval_fps, 'location': location}), retain=True)
                fps = 0
            if t-t0_2>=interval_webcam:
                t0_2 = t
                mqttc.publish(webcam_topic, qos=1, payload=cv2.imencode('.jpg', img)[1].tostring(), retain=True)
    finally:
        pass
        # cv2.destroyAllWindows()


def main(log):

    location_topic = 'sensors/{}/persons'.format(location)

    mqttc = MQTTClient(mqtt_server, client_id=app_name)
    mqttc._client.username_pw_set(app_name.lower(), mqtt_pw)

    def on_identifaction(face):

        payload = {'time': face['appeared'], 'present': 1}
        mqttc.publish('{loc}/presence/{id}'.format(loc=location_topic, id=face['face_id']), qos=1,
                      payload=json.dumps(payload), retain=True)
        if face['name'] != 'unknown':
            mqttc.publish('{loc}/presence/{name}'.format(loc=location_topic, name=face['name']), qos=1,
                          payload=json.dumps(payload), retain=True)

        payload = {}
        payload['time'] = face.get('appeared')
        payload['name'] = face.get('name')
        payload['face_id'] = face.get('face_id')
        payload['identified'] = face.get('identified')
        mqttc.publish('{loc}/identified'.format(loc=location_topic), qos=1, payload=json.dumps(payload), retain=True)

    def on_disappearance(face):

        if face.get('identified'):
            payload = {'time': face['disappeared'], 'present': 0}
            mqttc.publish('{loc}/presence/{id}'.format(loc=location_topic, id=face['face_id']), qos=1,
                          payload=json.dumps(payload), retain=True)
            if face['name'] != 'unknown':
                mqttc.publish('{loc}/presence/{name}'.format(loc=location_topic, name=face['name']), qos=1,
                              payload=json.dumps(payload), retain=True)

        payload = {}
        payload['time'] = face.get('disappeared')
        payload['name'] = face.get('name','unknown')
        payload['face_id'] = face.get('face_id',-1)
        payload['id'] = face.get('id',-1)
        payload['identified'] = face.get('identified')
        mqttc.publish('{loc}/disappeared'.format(loc=location_topic), qos=1, payload=json.dumps(payload), retain=True)

    def on_appearance(face):

        payload = {}
        payload['time'] = face.get('appeared')
        payload['id'] = face.get('id',-1)
        mqttc.publish('{loc}/appeared'.format(loc=location_topic), qos=1, payload=json.dumps(payload), retain=True)

    # setup logging
    from facerec.facetracker import FaceTracker
    from facerec import facedb

    try:
        tracker = FaceTracker(url=facerec_server_url,
                              identification_interval=2,
                              missing_tolerance_nframes=10,
                              appearance_callback=on_appearance,
                              identification_callback=on_identifaction,
                              disappearance_callback=on_disappearance)

        camera_opencv(tracker=tracker, log=log, mqttc=mqttc)
    finally:
        tracker.stop()
        facedb.close()

if __name__ == '__main__':
    log = logging.getLogger(app_name)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")
    log.info("Start tracking...")
    main(log)
    log.info("Stop tracking...")
