#!/usr/bin/env python

import time

from webdriver_testing.pages.site_pages import UnisubsPage


class NewMessagePage(UnisubsPage):
    """
     Search page is the main search page stub.  Watch Page and Search Results page
    """

    _URL = "messages/new/"
    _USER = 'select#id_user'
    _USERNAME_PULLDOWN = "div#id_user_chzn a"
    _TEAM_PULLDOWN = "div#id_team_chzn a div"
    _TEAM = 'select#id_team'
    _TEAM_CHOICES = 'div#id_team_chzn div.chzn-drop ul li'
    _LANGUAGE = 'select#id_language'
    _LANGUAGE_PULLDOWN = "div#id_language_chzn a div"
    _MESSAGE_TEXT = 'textarea#id_content'
    _SUBJECT = 'input#id_subject'
    _SEND = 'div.submit'

    def open_new_message_form(self):
        self.open_page(self._URL)

    def choose_user(self, username):
        self.wait_for_element_present(self._USERNAME_PULLDOWN)
        self.click_by_css(self._USERNAME_PULLDOWN)
        self.type_by_css('div.chzn-search input', username)
        self.select_from_chosen(self._USER, [username])
        time.sleep(2)
        self.click_by_css(".active-result")

    def choose_team(self, team_name):
        self.click_by_css(self._TEAM_PULLDOWN)
        self.select_from_chosen(self._TEAM, team_name)

    def team_choice_disabled(self):
        try:
            return self.get_element_attribute(self._TEAM, 'disabled')
        except:
            return False

    def lang_choice_disabled(self):
        try:
            return self.get_element_attribute(self._LANGUAGE, 'disabled')
        except:
            return False

    def available_teams(self):
        if not self.is_element_visible(self._TEAM_PULLDOWN):
            return False
        self.click_by_css(self._TEAM_PULLDOWN)
        team_els = self.get_elements_list(self._TEAM_CHOICES)
        teams_list = [x.text for x in team_els if '---' not in x.text] 
        return teams_list 

    def choose_language(self, language):
        self.click_by_css(self._LANGUAGE_PULLDOWN)
        self.select_from_chosen(self._LANGUAGE, language)

    def add_message(self, message):
        self.type_by_css(self._MESSAGE_TEXT, message)

    def add_subject(self, subject):
        self.type_by_css(self._SUBJECT, subject)

    def send(self):
        self.submit_by_css(self._SEND)

    def sent(self):
        return self.success_message_present('Message sent.')

