#!/usr/bin/env python
import time

from unisubs_page import UnisubsPage

class MyTeam(UnisubsPage):
    """Defines the actions for specific teams pages like 'unisubs test team' (default) or others. 
    """
    _URL = "/teams/my/"
    _TEAM = "ul.listing li"
    _TEAM_NAME = "h3 a"
    _LEAVE = "ul.admin-controls li a#leave"


    def _team_elem(self, team):
        """Given the team's text name, return the element.

        """
        self.wait_for_element_present(self._TEAM +" " + self._TEAM_NAME)
        teams = self.browser.find_elements_by_css_selector(self._TEAM)
        for el in teams:
            team_el = el.find_element_by_css_selector(self._TEAM_NAME)
            if team == team_el.text: return el        
    
    
    def open_my_teams_page(self):
        self.open_page(self._URL)

    def open_my_team(self, team=None):
        if self._URL not in self.browser.current_url:
            self.open_my_teams_page()
        if not team: 
            first_team = self._TEAM, self._TEAM_NAME
            self.click_by_css(first_team)
        else:
            team_el = self._team_elem(team)
            team = team_el.find_element_by_css_selector(self._TEAM_NAME)
            team.click()
                
    def team_displayed(self, team):
        teams_el = self.browser.find_elements_by_css_selector(" ".join([self._TEAM, self._TEAM_NAME]))
        for el in teams_el:
            if el.text == team:
                return True
        else:
            return "Team %s not found in the list of teams" % team


        
            


