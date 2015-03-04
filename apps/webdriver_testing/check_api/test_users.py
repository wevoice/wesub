#!/usr/bin/python
# Copyright 2014 Participatory Culture Foundation, All Rights Reserved
# -*- coding: utf-8 -*-

import os
import unittest
import json
import itertools
import time
from rest_framework.test import APILiveServerTestCase, APIClient

from utils.factories import *
from webdriver_testing.webdriver_base import WebdriverTestCase
from webdriver_testing.pages.site_pages.profiles import profile_personal_page


class TestCaseUsers(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for site video searches.  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseUsers, cls).setUpClass()
        cls.user = UserFactory()
        cls.client = APIClient

    def _get (self, url='/api/users/'):
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.logger.info(response)
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
        self.assertEqual(r, {"detail": "Method 'GET' not allowed."})

    def test_get_user(self):
        """get user info"""
        user  = UserFactory()
        url = '/api/users/%s/' % user.username
        r = self._get(url)
        self.assertEqual(1, r['meta']['total_count'])

    def test_create(self):
        """Create a user via the api.

        """
        data = {'username': 'newuser',
                'email': 'newuser@example.com',
                'first_name': 'New',
                'last_name': 'User_1',
                }
        r = self._post(data)
        self.assertEqual(r['username'], data['username'])

    def test_create_login_token(self):
        """Create a user and login token, verify login.

        """
        data = {'username': 'newuser',
                'email': 'enriqueumaran@uribekostabhi.com',
                'first_name': 'New',
                'last_name': 'User_1',
                'create_login_token': True
                }
        r = self._post(data)
        personal_pg = profile_personal_page.ProfilePersonalPage(self)
        personal_pg.open_page(r['auto_login_url'])
        fullname = ' '.join([new_user['first_name'], new_user['last_name']])
        self.assertEqual(fullname, personal_pg.username())
        self.assertEqual(fullname, user_data['full_name'])


    def test_create_invalid_email(self):
        data = {'username': 'newuser',
                'email': 'stone-throwing-giants@yahoo',
                'first_name': 'New',
                'last_name': 'User_1',
                }
        r = self._post(data)
        self.assertEqual('Enter a valid e-mail address.', r['email'][0])




