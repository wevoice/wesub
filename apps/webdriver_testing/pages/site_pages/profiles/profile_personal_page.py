#!/usr/bin/env python

from apps.webdriver_testing.pages.site_pages.profiles import ProfilePage

class ProfilePersonalPage(ProfilePage):
    """
    User Profile personal page.
    """

    _URL = "profiles/edit/"

    def open_profile_personal(self):
        self.open_page(self._URL)

