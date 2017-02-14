#!/usr/bin/env python

from webdriver_testing.pages.site_pages.profiles import ProfilePage

class ProfileAccountPage(ProfilePage):
    """
    User Profile accounts page.
    """

    _URL = "profiles/account/"
    _API_KEY = ".api-key-holder"
    _GENERATE_API_KEY = "a.get-new-api-bt"

    def open_profile_account(self):
        self.open_page(self._URL)


    def api_key(self):
        if self.current_api_key is None:
            print 'No API Key, generating a new one'
            self.click_by_css(self._GENERATE_API_KEY)
        return self.get_text_by_css(self._API_KEY)

    def current_api_key(self):
        try:
            self.wait_for_element_present(self._API_KEY)
            return self.get_text_by_css(self._API_KEY)
        except:
            return None
