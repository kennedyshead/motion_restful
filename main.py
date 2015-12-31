#!/usr/bin/env python
# -*- coding: utf-8 -*-
import falcon
from camera.api.resources import CamResource

__author__ = 'magnusknutas'


api = falcon.API()
api.add_route('/cams', CamResource())
