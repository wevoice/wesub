#!/usr/bin/env python

from unisubs_page import UnisubsPage
from profile_edit_page import ProfileEditPage


class ProfilePage(UnisubsPage):
    """
    User Profile page
    """

    _URL = "profiles/%s"
    _API_KEY = ".api-key-holder"
    _GENERATE_API_KEY = "a.get-new-api-bt"
    _EDIT_LINK = "a.button[href*='edit']"

    def open_profile(self, username='mine'):
        self.open_page(self._URL % username)


    def open_edit_profile(self):
        self.click_by_css(self._EDIT_LINK)
        return ProfileEditPage(self)
