# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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
import logging
import time
from django.test import LiveServerTestCase
from django.test.testcases import (TestCase)
from selenium import webdriver
from django.conf import settings

class WebdriverTestCase(LiveServerTestCase, TestCase):
    def setUp(self):
        super(WebdriverTestCase, self).setUp()
        LiveServerTestCase.setUp(self)

        #Set up logging to capture the test steps.
        self.logger = logging.getLogger('test_steps')
        logging.getLogger('test_steps').setLevel(logging.INFO)
        self.logger.info('testcase: %s' % self.id())
        self.logger.info('description: %s' % self.shortDescription())

        self.use_sauce = os.environ.get('USE_SAUCE', False)

        #if running in vagrant VM, must use port 80 for headless browser
        if settings.VAGRANT_VM:             
            self.base_url = 'http://unisubs.example.com:80/'

        #Get config values from env vars (set via jenkins plugin)
        if self.use_sauce: 
            self.base_url = self.live_server_url + '/' 
            self.sauce_key = os.environ.get('SAUCE_API_KEY')
            self.sauce_user = os.environ.get('SAUCE_USER_NAME')
            test_browser = os.environ.get('SELENIUM_BROWSER', 'Chrome')
            dc = getattr(webdriver.DesiredCapabilities, test_browser)

            dc['version'] = os.environ.get('SELENIUM_VERSION', '')
            dc['platform'] = os.environ.get('SELENIUM_PLATFORM', 'WINDOWS 2008')
            dc['name'] = self.shortDescription()
            dc['tags'] = ['amara',] 

            #Setup the remote browser capabilities
            self.browser = webdriver.Remote(
                desired_capabilities=dc,
                command_executor=("http://{0}:{1}@ondemand.saucelabs.com:80/"
                                  "wd/hub".format(self.sauce_user, self.sauce_key)))
            self.browser.get(self.base_url + 'videos/create/')


        #Otherwise just running locally - setup the browser to use.
        else:
            self.base_url = self.live_server_url + '/'
            test_browser = os.environ.get('TEST_BROWSER', 'Firefox')
            self.browser = getattr(webdriver, test_browser)()
            self.browser.get(self.base_url + 'videos/create/')
            #Opening the create page as the starting point because it loads faster than the home page.
            self.browser.get(self.base_url + 'videos/create/')
            #set the skiphowto cookie so those dialogs don't affect test cases.
            self.browser.add_cookie({ u'name': u'skiphowto', 
                                  u'value': u'1', 
                                 })
        
    def tearDown(self):
        if self.use_sauce:
            self.logger.info("Link to the job: https://saucelabs.com/jobs/%s" % self.browser.session_id)
            self.logger.info("SauceOnDemandSessionID={0} job-name={1}".format(
                               self.browser.session_id, self.shortDescription()))
        else:
            try:  #To get a screenshot of the last page and save to Results.
                time.sleep(2) #sometimes needs some extra time.
                screenshot_file = ('apps/webdriver_testing/' 
                              'Results/%s.png' % self.id())
                self.browser.get_screenshot_as_file(screenshot_file)
            except:
                pass
        try:
            self.browser.quit()
        except:
            pass  #possibly should try to kill off the process so we don't leave any around block ports.

