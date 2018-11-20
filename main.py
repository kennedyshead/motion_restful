#!/usr/bin/env python
# -*- coding: utf-8 -*-
import falcon
from camera.api.resources import CamResource
from paho.mqtt.client import Client
import argparse
import logging
import coloredlogs
import sys

from camera.camera import Cam
from settings import MOTION_URL, AUTH, MQTT_ADRESS, MQTT_PORT

__author__ = 'magnusknutas'
logger = logging.getLogger(__name__)
camera = Cam(MOTION_URL, AUTH.get('name', None), AUTH.get('pass', None))


api = falcon.API()
api.add_route('/cams', CamResource())
help_text = "Example"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code "+str(rc))
    logger.info("Connected with result code "+str(userdata))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    cameras = camera.list_cameras()
    for cam in cameras:
        listen = "home/camera_recording/%i" % cam['id']
        client.subscribe(listen, qos=2)
        client.subscribe(listen + '/set')
        logger.info(listen)
        client.publish(
            'home/camera_recording/%i/set' % cam['id'], cam['state'],
            retain=True
        )


def callback_when_done(client, message, cam_id):
    state_not_set = False
    while not state_not_set:
        logger.info("Setting state %s for %s", message, cam_id)
        state_not_set = camera.get_state(cam_id) == message or False
    client.publish('home/camera_recording/%i/set' % cam_id, message)


def on_message(client, userdata, message):
    logger.info("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))
    if not message.topic.endswith('/set'):
        send = None
        cam_id = int(str(message.topic).lstrip('home/camera_recording/'))
        if message.payload == b'ON':
            send = 'ON'
            camera.start(cam_id)
        elif message.payload == b'OFF':
            send = 'OFF'
            camera.pause(cam_id)
        if send:
            callback_when_done(client, send, cam_id)


def main():
    parser = argparse.ArgumentParser(description=help_text)
    parser.add_argument('-l', '--log-level', action='store', type=str, dest='log_level', help='Log level', default='INFO')

    args = parser.parse_args()
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    coloredlogs.install(level=numeric_level)
    logger.info('Log level set to %s', args.log_level)

    client = Client()
    client.username_pw_set("knutas", "Freakdays123")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_ADRESS, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == '__main__':
    sys.exit(main())
