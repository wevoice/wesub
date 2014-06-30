#!/usr/bin/env python

from webdriver_testing.pages.site_pages import UnisubsPage

class ProfilePage(UnisubsPage):
    """
    User Profile page
    """

    _URL = "profiles/%s"
    _PERSONAL_LINK = "ul.tabs li a[href*='edit']"
    _ACCOUNT_LINK = "ul.tabs li a[href*='account']"

    def open_profile(self, username='mine'):
        self.open_page(self._URL % username)


    def open_personal_tab(self):
        self.click_by_css(self._PERSONAL_LINK)

    def open_account_tab(self):
        self.click_by_css(self._ACCOUNT_LINK)
