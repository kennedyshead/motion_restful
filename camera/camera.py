#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class Cam(object):
    def __init__(self, base_url, user=None, pwd=None):
        self.base_url = base_url
        self.status_url = base_url + '%i/detection/status'
        self.pause_url = base_url + '%i/detection/pause'
        self.start_url = base_url + '%i/detection/start'
        self.pwd = pwd
        self.user = user
        self.__cams = []

    def list_cameras_no_parse(self):
        cameras = self._call(self.base_url)
        return cameras

    def get_camera(self, cam_id):
        for cam in self.list_cameras():
            if cam['id'] == cam_id:
                return cam
        return False

    def list_cameras(self):
        if not self.__cams:
            cameras = self._call(self.base_url)
            soup = BeautifulSoup(cameras.content, 'html.parser')
            for link in soup.find_all('a'):
                cam_id = int(link.get('href').strip('/'))
                logger.info('Adding camera %s-%s', cam_id, link.text)
                self.__cams.append({
                    'id': cam_id,
                    'name': link.text,
                    'state': 'ON'
                    if self._state(self.status_url % cam_id) else 'OFF'
                })
        return self.__cams

    def get_state(self, cam_id):
        return self.get_camera(cam_id)['state']

    def start(self, cam_id):
        self.get_camera(cam_id)['state'] = 'ON'
        self._call(self.start_url % cam_id)

    def pause(self, cam_id):
        self.get_camera(cam_id)['state'] = 'OFF'
        self._call(self.pause_url % cam_id)

    def _state(self, url):
        data = self._call(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        status = soup.find('body').text.split('status')[1].strip()
        return True if status == 'ACTIVE' else False

    def _call(self, url):
        if self.user:
            return requests.get(
                    url,
                    auth=HTTPBasicAuth(self.user, self.pwd)
            )
        else:
            return requests.get(
                    url,
            )
