#!/usr/bin/env python
import time
from webdriver_testing.pages.site_pages import UnisubsPage


class AuthPage(UnisubsPage):
    """
     Unisubs page contains common web elements found across
     all Universal Subtitles pages. Every new page class is derived from
     UnisubsPage so that every child class can have access to common web
     elements and methods that pertain to those elements.
    """
    _SITE_LOGIN_USER_ID = "input#id_username"
    _SITE_LOGIN_USER_PW = "input#id_password"
    _SITE_LOGIN_SUBMIT = "form button[value=login]"

    _URL = 'auth/login'

    def login(self, username, passw):
        """Log in with the specified account type - default as a no-priv user.

        """
        curr_page = self.browser.current_url
        if self._URL not in curr_page and not self.logged_in() == True:
            assert self.is_element_present(self._LOGIN)
            self.click_by_css(self._LOGIN)
        self.wait_for_element_present(self._SITE_LOGIN_USER_ID)
        self.type_by_css(self._SITE_LOGIN_USER_ID, username)
        self.type_by_css(self._SITE_LOGIN_USER_PW, passw)
        self.click_by_css(self._SITE_LOGIN_SUBMIT)
        self.wait_for_element_present(self._USER_MENU)
