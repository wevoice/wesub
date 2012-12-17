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
from selenium import webdriver
import nose
import unittest

class WebdriverRemote(unittest.TestCase):

    def setUp(self):

        """This is where we want to setup the browser configuation.

        If you want to use something other than default (no sauce on ff)
        then it should be setup as env vars in the system under test. When
        running sauce on jenkins with the jenkins pluging - then the vars are
        set there.
        
        Environment vars recognized by jenkins sauce plugin.
        SELENIUM_HOST - The hostname of the Selenium server
        SELENIUM_PORT - The port of the Selenium server
        SELENIUM_PLATFORM - The operating system of the selected browser
        SELENIUM_VERSION - The version number of the selected browser
        SELENIUM_BROWSER - The browser string.
        SELENIUM_URL - The initial URL to load when the test begins
        SAUCE_USER_NAME - The user name used to invoke Sauce OnDemand
        SAUCE_API_KEY - The access key for the user used to invoke Sauce OnDemand
        36114ded-d388-4ee0-92f7-d82d8530ff3e

        We are going to look for a USE_SAUCE = True if we are using sauce, 
        and a default browser TEST_BROWSER if not using sauce.
        """
        use_sauce = os.environ.get('USE_SAUCE', False)
        self.base_url = os.environ.get('TEST_URL', 'http://dev.universalsubtitles.org/')

        if use_sauce:
            sauce_key = os.environ.get('SAUCE_API_KEY')
        else:    
            test_browser = os.environ.get('TEST_BROWSER', 'Firefox')
            
        if use_sauce:
            jenkins_ws = os.environ.get('WORKSPACE', False)
            if not jenkins_ws: 
                test_browser = os.environ.get('SELENIUM_BROWSER', 'FIREFOX')
                dc = getattr(webdriver.DesiredCapabilities, test_browser) 
                dc['version'] = os.environ.get('SELENIUM_VERSION', '')
                dc['platform'] = os.environ.get('SELENIUM_PLAFORM', 'MAC 10.8')
                dc['name'] = self.shortDescription()

                self.browser = webdriver.Remote(
                    desired_capabilities = dc,
                    command_executor=("http://jed-pcf:%s@ondemand.saucelabs.com:80"
                                      "/wd/hub" % sauce_key) 
                                      )
                self.browser.implicitly_wait(5)
        else:
            self.browser = getattr(webdriver, test_browser)()
            self.browser.implicitly_wait(1)

        
    def tearDown(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.browser.session_id)
        self.browser.quit()

        
