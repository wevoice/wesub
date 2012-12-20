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
try:
    import unittest2 as unittest
except:
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
        self.use_sauce = os.environ.get('USE_SAUCE', False)
        self.base_url = os.environ.get('TEST_URL', 'http://dev.universalsubtitles.org/')


        #If we are using sauce - check if we are running on jenkins.
        if self.use_sauce:
            sauce_key = os.environ.get('SAUCE_API_KEY')
            jenkins_ws = os.environ.get('WORKSPACE', False)
               
            #Using sauce, but not jenkins, specify the setups
            #Jenkins sets thes via the env vars (I think)    
            if not jenkins_ws: 
                test_browser = os.environ.get('SELENIUM_BROWSER', 'CHROME')
                dc = getattr(webdriver.DesiredCapabilities, test_browser) 
                dc['version'] = os.environ.get('SELENIUM_VERSION', '')
                dc['platform'] = os.environ.get('SELENIUM_PLAFORM', 'WINDOWS 2008')
                dc['name'] = self.shortDescription()

            #Setup the remote browser capabilities
            self.browser = webdriver.Remote(
                desired_capabilities = dc,
                command_executor=("http://jed-pcf:%s@ondemand.saucelabs.com:80"
                                  "/wd/hub" % sauce_key) 
                                  )
            self.browser.implicitly_wait(2)

        #Otherwise just running locally - setup the browser to use.
        else:
            test_browser = os.environ.get('TEST_BROWSER', 'Firefox')
            self.browser = getattr(webdriver, test_browser)()
            self.browser.implicitly_wait(1)

        
    def tearDown(self):
        if self.use_sauce:
            print("\nLink to your job: https://saucelabs.com/jobs/%s" % self.browser.session_id)
        else:
            screenshot_file = ('apps/webdriver_testing/' 
                               'Results/%s.png' % self.id())
            self.browser.get_screenshot_as_file(screenshot_file)

        self.browser.quit()

        
