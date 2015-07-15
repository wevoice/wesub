#!/usr/bin/python
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
        response = self.client.post(url, json.dumps(data),
                                    content_type="application/json;  charset=utf-8")
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
        self.logger.info(r)
        self.assertEqual(user.username, r['username'])
        self.assertEqual(user.first_name, r['first_name'])
        self.assertEqual(user.last_name, r['last_name'])


    def test_get_username_with_space(self):
        """get user info"""
        user  = UserFactory()
        user.username='janet finn'
        user.save()
        url = '/api/users/%s/' % user.username
        r = self._get(url)
        self.logger.info(r)
        self.assertEqual(user.username, r['username'])
        self.assertEqual(user.first_name, r['first_name'])
        self.assertEqual(user.last_name, r['last_name'])

    def test_create_username_chars(self):
        """Create a user via the api.

        """
        errors = []
        users = ['auserwithaverysuperreallyquitelongusername', 
                 'i-am-me', 
                 'I_M_A_USER', 
                 'monkey.girl@gmail.com', 
                 'monkey.girl', 
                 'user@vimeo.com', 
                 '@PCFQA',
                 u'čevapčići',
                  ]
        for username in users:
            data = {'username': username,
                    'email': 'newuser@example.com',
                    }
            r = self._post(data=data)
            try:
                self.logger.info(r)
                self.assertEqual(r['username'], data['username'])
            except AssertionError as e:
                errors.append(r)
        self.logger.info(errors)
        expected_errors = [
                           {u'username': [u'Ensure this field has no more than 30 characters.']},
                           {u'username': [u'Invalid Username: ?evap?i?i']}
                          ]
        self.assertEqual(errors, expected_errors)


    def test_create(self):
        """Create a user via the api.

        """
        data = {'username': 'newuser',
                'email': 'newuser@example.com',
                'first_name': 'New',
                'last_name': 'User_1',
                }
        r = self._post(data=data)
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
        r = self._post(data=data)
        personal_pg = profile_personal_page.ProfilePersonalPage(self)
        self.logger.info(r['auto_login_url'])
        self.logger.info(self.base_url)
        login_url = r['auto_login_url'].replace('http://testserver/en/', self.base_url)
        self.logger.info(login_url)
        personal_pg.open_page(login_url)
        fullname = ' '.join([data['first_name'], data['last_name']])
        self.assertEqual(fullname, personal_pg.username())

    def test_create_invalid_email(self):
        data = {'username': 'newuser',
                'email': 'stone-throwing-giants@yahoo',
                'first_name': 'New',
                'last_name': 'User_1',
                }
        r = self._post(data=data)
        self.assertEqual('Enter a valid email address.', r['email'][0])

    def test_create_unique_user(self):
        """option to always create unique username"""
        usernames = []
        data = {'username': 'imaunique@user.com',
                'email': 'imaunique@user.com',
                'password': 'password',
                'find_unique_username': True
                }
        for x in range(110):
            r = self._post(data=data)
            usernames.append(r['username'])
        self.assertIn('imaunique@user.com', usernames)
        self.assertIn('imaunique00@user.com', usernames)
        self.assertIn('imaunique99@user.com', usernames)
        self.assertEqual(110, len(usernames))

    def test_duplicates(self):
        data = {'username': 'imaunique@user.com',
                'email': 'imaunique@user.com',
                'password': 'password',
                }
        r = self._post(data=data)
        self.assertEqual('imaunique@user.com',r['username'])
        r = self._post(data=data)
        self.assertEqual([u'Username not unique: imaunique@user.com'], r)


    def test_unique_user_24chars(self):
        """Create unique user length limited to 24 chars

        """
        data = {'username':'newuserwith30chars@example.com',
                'email': 'newuserwith30chars@example.com',
                'password': 'password',
                'find_unique_username': True
                    }
        r = self._post(data=data)
        self.assertEqual(r, {u'non_field_errors': [u'Username too long: newuserwith30chars@example.com']})


