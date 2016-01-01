#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from settings import AUTH, MOTION_URL

__author__ = 'magnusknutas'

STATUS_URL = MOTION_URL + '%i/detection/status'
PAUSE_URL = MOTION_URL + '%i/detection/pause'
START_URL = MOTION_URL + '%i/detection/start'

class CamResource:
    def on_get(self, req, resp):
        id = req.get_param_as_int('id', False)

        if id:
            if AUTH:
                camera_status = requests.get(
                        STATUS_URL % id,
                        auth=HTTPBasicAuth(AUTH.get('name'), AUTH.get('pass'))
                )
            else:
                camera_status = requests.get(
                        STATUS_URL % id,
                )

            soup = BeautifulSoup(camera_status.content, 'html.parser')
            status = soup.find('body').text.split('status')[1].strip()
            resp.body = 'ON' if status == 'ACTIVE' else 'OFF'

        else:
            if AUTH:
                cameras = requests.get(
                        MOTION_URL,
                        auth=HTTPBasicAuth(AUTH.get('name'), AUTH.get('pass'))
                )
            else:
                cameras = requests.get(
                        MOTION_URL,
                )

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
        id = req.get_param_as_int('id', False)
        if id:
            if AUTH:
                camera_status = requests.get(
                        STATUS_URL % id,
                        auth=HTTPBasicAuth(AUTH.get('name'), AUTH.get('pass'))
                )
            else:
                camera_status = requests.get(
                        STATUS_URL % id,
                )

            soup = BeautifulSoup(camera_status.content, 'html.parser')
            sta = soup.find('body').text.split('status')[1].strip()
            status = True if sta == 'ACTIVE' else False

            if status:
                if AUTH:
                    requests.get(
                            PAUSE_URL % id,
                            auth=HTTPBasicAuth(AUTH.get('name'), AUTH.get('pass'))
                    )
                else:
                    requests.get(
                            PAUSE_URL % id
                    )
                resp.body = 'OFF'
            else:
                if AUTH:
                    requests.get(
                            START_URL % id,
                            auth=HTTPBasicAuth(AUTH.get('name'), AUTH.get('pass'))
                    )
                else:
                    requests.get(
                            START_URL % id
                    )
                resp.body = 'ON'
