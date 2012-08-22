# Miro Community - Easiest way to make a video website
#
# Copyright (C) 2010, 2011, 2012 Participatory Culture Foundation
#
# Miro Community is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Miro Community is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Miro Community.  If not, see <http://www.gnu.org/licenses/>.

from django.test import LiveServerTestCase
from django.test.testcases import (TestCase, _deferredSkip)
from django.core import management
from selenium import webdriver
import os, time
os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'unisubs.example.com:8000'

class WebdriverTestCase(LiveServerTestCase, TestCase):
    def setUp(self):
        try:   #Get rid of the existing screenshot from a previous test run if it exists.
            os.unlink('apps/webdriver_testing/Screenshots/%s.png' % self.id())
        except:
            pass
        super(WebdriverTestCase, self).setUp()
        LiveServerTestCase.setUp(self)
        self.browser = webdriver.Firefox() #BROWSER TO USE FOR TESTING
        self.base_url =  'http://localhost:80/'
        self.browser.get(self.base_url)

    def tearDown(self):
        time.sleep(1)
        try:
            self.browser.get_screenshot_as_file('apps/webdriver_testing/Screenshots/%s.png' % self.id())
            self.browser.quit()
        except:
            os.system('killall firefox')  #sometimes there a ff instance left running we don't want it there



