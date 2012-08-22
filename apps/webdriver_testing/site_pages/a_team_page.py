#!/usr/bin/env python
import time
from nose.tools import assert_equals
from nose.tools import assert_true
from unisubs_page import UnisubsPage

class ATeamPage(UnisubsPage):
    """Defines the actions for specific teams pages like 'unisubs test team' (default) or others. 
    """

    _TEAM_LINK = "h2#team_title a"
    _TEAM_NAME = ".main-title a"

    #TEAM METRICS
    _VIDEO_METRIC = ".metrics li:nth-child(1) > a p"
    _MEMBER_METRIC = ".metrics li:nth-child(2) > a p"
    _TASK_METRIC = ".metrics li:nth-child(3) > a p"
    _PROJECT_METRIC = ".metrics li:nth-child(4) > a p"

    #TABS
    _VIDEO_TAB = "ul.tabs li a"
    _MEMBERS_TAB = "ul.tabs li a[href*='members']"
    _ACTIVITY_TAB = "ul.tabs li a[href*='activity']"
    _SETTINGS_TAB = "ul.tabs li a[href*='settings']"


    #JOIN / APPLY
    _JOIN_TEAM = ".join a"
    _APPLY_TEAM = "a#apply"
    _SIGNIN = "a#signin-join"
    _APPLY_BUTTON = "Apply to Join"
    _APPLICATION = "div#apply-modal"
    _APPLICATION_TEXT = "div#apply-modal div.form textarea"
    _SUBMIT_APPLICATION = "div#apply-modal button" 


   #FILTER AND SORT



    def is_team(self, team):
        if self.get_text_by_css(self._TEAM_NAME) == team:
            return True

    
    def team_search(self, team):
        pass

    def join_exists(self):
        if self.is_element_present(self._JOIN_TEAM):
            return True
        
    def apply_exists(self):
        button = self._APPLY_TEAM
        join_button = self.get_text_by_css(button)
        if self.logged_in(): 
           assert_equals(join_button, self._APPLY_BUTTON)
        else:
           assert_equals(join_button, self._JOIN_NOT_LOGGED_IN)

    def application_displayed(self):
        assert_true(self.is_element_present(self._APPLICATION))

    def submit_application(self, text=None):
        if text == None:
            text = "Please let me join your team, I'll subtitle hard. I promise."
        self.application_displayed()
        self.type_by_css(self._APPLICATION_TEXT, text)
        self.click_by_css(self._SUBMIT_APPLICATION)

    def join(self, logged_in=True):
        self.click_by_css(self._JOIN_TEAM)
        if logged_in == True:
            self.handle_js_alert(action='accept')
    
    def signin(self):
        self.click_by_css(self._SIGNIN)
 
    def apply(self):
        self.click_by_css(self._APPLY_TEAM) 

    def leave_team(self, team_url):
        leave_url = "teams/leave_team/%s/" % team_stub
        self.open_page(leave_url)


    def settings_tab_visible(self):
        if self.is_element_present(self._SETTINGS_TAB) == True:
            return True
