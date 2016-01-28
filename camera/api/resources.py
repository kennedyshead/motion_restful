#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from bs4 import BeautifulSoup
from camera.camera import Cam
from settings import MOTION_URL, AUTH

__author__ = 'magnusknutas'


class CamResource:

    camera = Cam(MOTION_URL, AUTH.get('name', None), AUTH.get('pass', None))

    def on_get(self, req, resp):
        cam_id = req.get_param_as_int('id', False)

        if cam_id:
            self.camera.get_state(cam_id)
            resp.body = self.camera.get_state(cam_id)
        else:
            cameras = self.camera.list_cameras_no_parse()
            soup = BeautifulSoup(cameras.content, 'html.parser')
            cams = []
            for link in soup.find_all('a'):
                cams.append({
                    'id': int(link.get('href').strip('/')),
                    'name': link.text,
                    'link': req.uri + '?id=%i' % int(link.get('href').strip('/'))
                })
            resp.body = json.dumps(cams)

    def on_post(self, req, resp):
        cam_id = req.get_param_as_int('id', False)
        if cam_id:
            status = self.camera.get_state()

            if status:
                self.camera.pause(cam_id)
                resp.body = 'OFF'
            else:
                self.camera.start(cam_id)
                resp.body = 'ON'
