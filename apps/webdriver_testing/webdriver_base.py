# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.test import LiveServerTestCase
from django.test.testcases import (TestCase)
from selenium import webdriver
import os
import time
from apps.webdriver_testing.data_factories import UserFactory

os.environ[
    'DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'unisubs.example.com:8000'


class WebdriverTestCase(LiveServerTestCase, TestCase):
    def setUp(self):
        super(WebdriverTestCase, self).setUp()
        LiveServerTestCase.setUp(self)
        try:  # Get rid of the previous screenshot
            os.unlink('apps/webdriver_testing/Screenshots/%s.png' % self.id())
        except:
            pass
        self.browser = webdriver.Firefox()  # BROWSER TO USE FOR TESTING
        if os.getenv("HOME") == '/home/vagrant':
            self.base_url = 'http://unisubs.example.com:80/'
        else:
            self.base_url = 'http://unisubs.example.com:8000/'
        self.browser.get(self.base_url)
        UserFactory.create(username='admin', is_staff=True, is_superuser=True)
        self.auth = dict(username='admin', password='password')



    def tearDown(self):
        try:
            self.browser.get_screenshot_as_file('apps/webdriver_testing/'
                                                'Screenshots/%s.png'
                                                % self.id())
        except:  # wait 2 seconds and try again
            time.sleep(2)
            self.browser.get_screenshot_as_file('apps/webdriver_testing/'
                                                'Screenshots/%s.png'
                                                % self.id())

        finally:
            self.browser.quit()
