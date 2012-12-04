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

import os
import time
from django.test import LiveServerTestCase
from django.test.testcases import (TestCase)
from selenium import webdriver
from django.conf import settings
from apps.webdriver_testing.data_factories import UserFactory


class WebdriverTestCase(LiveServerTestCase, TestCase):
    def setUp(self):
        super(WebdriverTestCase, self).setUp()
  
        LiveServerTestCase.setUp(self)
        try:  # Get rid of the previous screenshot
            os.unlink('apps/webdriver_testing/Results/%s.png' % self.id())
        except:
            pass
        if settings.VAGRANT_VM: #if running in vagrant VM, must use port 80 for headless browser
            self.base_url = 'http://unisubs.example.com:80/'
        else:
            self.base_url = self.live_server_url + '/'

        self.browser = webdriver.Firefox()  # BROWSER TO USE FOR TESTING
        self.browser.get(self.base_url)

        UserFactory.create(username='admin', is_staff=True, is_superuser=True)
        self.auth = dict(username='admin', password='password')
        

    def tearDown(self):
        try:  #To get a screenshot of the last page and save to Results.
            screenshot_file = ('apps/webdriver_testing/' 
                              'Results/%s.png' % self.id())
            self.browser.get_screenshot_as_file(screenshot_file)
        except: #But don't panic if fails, sometimes a timing thing, try again.
            time.sleep(2)
            self.browser.get_screenshot_as_file(screenshot_file)

        try: #To quit the browser
            self.browser.quit()
        except: #But don't worry if you can't it may already be quit.
            pass
        print self.existing_bugs_lookup()


    def existing_bugs_lookup(self):
        nameparts = self.id().split('.')
        tid = '.'.join(nameparts[-3:])
        print self.failureException()
        return tid

   

