#!/usr/bin/env python

from unisubs_page import UnisubsPage

class ProfileEditPage(UnisubsPage):
    """
    User Profile edit page.
    """

    _URL = "profiles/edit/"
    _API_KEY = ".api-key-holder"
    _GENERATE_API_KEY = "a.get-new-api-bt"

    def open_profile_edit(self):
        self.open_page(self._URL)


    def api_key(self):
        if not self.is_element_present(self._API_KEY):
            print 'No API Key, generating a new one'
            self.click_by_css(self._GENERATE_API_KEY)
        return self.get_text_by_css(self._API_KEY)
