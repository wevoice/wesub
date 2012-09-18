#!/usr/bin/env python
import time
from ..page import Page


class UnisubsPage(Page):
    """
     Unisubs page contains common web elements found across
     all Universal Subtitles pages. Every new page class is derived from
     UnisubsPage so that every child class can have access to common web
     elements and methods that pertain to those elements.
    """

    _LOGIN = "a[href*=login]"
    _USER_MENU = "li#me_menu"
    _CREATE_NAV = "li#nav_submit a"
    _FEEDBACK_BUTTON = ".feedback_tab"

    _CURRENT_USER = "div#menu_name a"

    _USER_TEAMS = "li#me_menu  div#user_menu div#menu ul#dropdown li[id^=team] a"
    _SITE_LOGIN_USER_ID = "input#id_username"
    _SITE_LOGIN_USER_PW = "input#id_password"
    _SITE_LOGIN_SUBMIT = "form button[value=login]"

    _ERROR_MESSAGE = "div#messages h2.error"
    _SUCCESS_MESSAGE = "div#messages h2.success"

    _MODAL_DIALOG = "div.modal"
    _MODAL_CLOSE = "div.modal-header a.close"

    def error_message_present(self, message):
        if self.is_text_present(self._ERROR_MESSAGE, message):
            return True

    def success_message_present(self, message):
        if self.is_text_present(self._SUCCESS_MESSAGE, message):
            return True

    def open_amara(self):
        self.browser.get(self.base_url)

    def _current_user(self):
        return self.get_text_by_css(self._CURRENT_USER)
    
    def logged_in(self):
        if self.is_element_present(self._USER_MENU):
            return True

    def log_out(self):
        if self.logged_in() == True:
            self.open_page('logout/?next=/auth/login/')
    def log_in(self, username, passw):
        """Log in with the specified account type - default as a no-priv user.

        """
        curr_page = self.browser.current_url
        if self.logged_in() and self._current_user() == username:
            return
        if self.logged_in() and self._current_user() != username:
            self.log_out()
        if "login" not in curr_page: 
            self.click_by_css(self._LOGIN)
        self.wait_for_element_present(self._SITE_LOGIN_USER_ID)
        self.type_by_css(self._SITE_LOGIN_USER_ID, username)
        self.type_by_css(self._SITE_LOGIN_USER_PW, passw)
        self.click_by_css(self._SITE_LOGIN_SUBMIT)
        self.wait_for_element_present(self._USER_MENU)
        time.sleep(2)

    def current_teams(self):
        """Returns the href value of any teams that use logged in user is currently a memeber.

        """
        user_teams = []
        if self.logged_in() == True:
            elements = self.browser.find_elements_by_css_selector(
                self._USER_TEAMS)
            for e in elements:
                user_teams.append(e.get_attribute('href'))
        return user_teams

    def close_modal(self):
        try:
            if not self.is_element_visible(self._MODAL_DIALOG) == False:
                self.click_by_css(self._MODAL_CLOSE)
        except:
            pass

    def click_feeback(self):
        self.click_by_css(self._FEEDBACK_BUTTON)
 
    def impersonate(self, username):
        self.open_page('auth/login-trap/')
        self.type_by_css(self._SITE_LOGIN_USER_ID, username)
        self.click_by_css(self._SITE_LOGIN_SUBMIT)

