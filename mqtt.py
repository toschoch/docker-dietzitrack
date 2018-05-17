#!/usr/bin/python
# -*- coding: UTF-8 -*-
# created: 17.05.2018
# author:  TOS

import logging
import paho
import paho.mqtt.client

log = logging.getLogger(__name__)


class MQTTClient(object):

    def __init__(self, hostname="localhost",
           port=1883, client_id="", keepalive=60, will=None, auth=None,
           tls=None, protocol=paho.mqtt.client.MQTTv311, transport="tcp",
           clean_session=True, userdata=None, bind_address=""):

        self.hostname=hostname
        self.port=port
        self.client_id=client_id
        self.keepalive=keepalive
        self.will=will
        self.auth=auth
        self.tls=tls
        self.protocol=protocol
        self.transport=transport
        self.clean_session=clean_session
        self.userdata=userdata
        self.bind_address=bind_address

        self._connected = False
        self._client = paho.mqtt.client.Client(client_id=client_id, clean_session=clean_session,
                                               userdata=userdata, protocol=protocol, transport=transport)

        self._client.enable_logger(log)
        self._client.max_inflight_messages_set(1000)

        self._client.on_connect = self._on_client_connect
        self._client.on_disconnect = self._on_client_disconnect

    def _on_client_connect(self):
        self._connected = True

    def _on_client_disconnect(self):
        self._connected = False

    def _assert_connected(self):
        if not self._connected:
            try:
                self._client.connect(host=self.hostname, port=self.port,
                                     keepalive=self.keepalive, bind_address=self.bind_address)
                self._connected = True
            except ConnectionRefusedError as err:
                log.error(err)
        return self._connected


    def publish(self, topic, payload=None, qos=0, retain=False):
        if not self._assert_connected(): return
        return self._client.publish(topic=topic, payload=payload, qos=qos, retain=retain)

