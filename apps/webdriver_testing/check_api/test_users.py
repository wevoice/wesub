#!/usr/bin/python
# Copyright 2014 Participatory Culture Foundation, All Rights Reserved
# -*- coding: utf-8 -*-

import os
import unittest
import json
import itertools
import time
from rest_framework.test import APILiveServerTestCase, APIClient

from videos.models import *
from utils.factories import *
from subtitles import pipeline
from webdriver_testing.webdriver_base import WebdriverTestCase

class TestCaseUsers(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for site video searches.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseVideos, cls).setUpClass()
        cls.client = APIClient

    def _get (self, url='/api/users/'):
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def _post(self, url='/api/users/', data=None):
        self.client.force_authenticate(self.user)
        response = self.client.post(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def test_get_user_list(self):
        """can not do a get request on all users"""
        r = self._get()
        self.assertEqual(r, {"detail": "Method 'GET' not allowed."}

    def test_get_user(self):
        """get user info"""
        user  = UserFactory()
        url = '/api/users/%s' % user.username
        r = self._get(url)
        self.assertEqual(1, r['meta']['total_count'])

