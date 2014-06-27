#!/usr/bin/env python

from webdriver_testing.pages.site_pages.profiles import ProfilePage

class ProfilePersonalPage(ProfilePage):
    """
    User Profile personal page.
    """

    _URL = "profiles/edit/"
    _USERNAME = "div.content h2"

    def open_profile_personal(self):
        self.logger.info('Opening the Personal tab of the user profile')
        self.open_page(self._URL)

    def username(self):
        self.logger.info('Getting the username displayed on the page.')
        return self.get_text_by_css(self._USERNAME)
        

