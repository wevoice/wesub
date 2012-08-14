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
    _VIDEO_TAB = ".tabs li a"
    _MEMBERS_TAB = ".tabs li a[href*='members']"
    _ACTIVITY_TAB = ".tabs li a [href*='activity']"


    #JOIN / APPLY
    _JOIN_TEAM = ".join a"
    _APPLY_TEAM = "a#apply"
    _SIGNIN = "a#signin-join"
    _APPLY_BUTTON = "Apply to Join"
    _APPLICATION = "div#apply-modal"
    _APPLICATION_TEXT = "div#apply-modal div.form textarea"
    _SUBMIT_APPLICATION = "div#apply-modal" 


   #FILTER AND SORT



    def is_team(self, team):
        if self.get_text_by_css(self._TEAM_NAME) == team:
            return True

    def is_member(self, team_type):
        team_url = self._team_stub(team_type)
        print team_url
        current_teams = self.current_teams()
        for team in current_teams:
            if team_url in team: return True
        
    
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

    def submit_application(self, text):
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

    def leave_team(self, team):
        team_url = self._team_stub(team)
        team_stub = team_url.split('/')[-1]
        leave_url = "teams/leave_team/%s/" % team_stub
        self.open_page(leave_url)
