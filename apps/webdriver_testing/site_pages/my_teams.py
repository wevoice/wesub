#!/usr/bin/env python
import time

from teams_page import TeamsPage


class MyTeam(TeamsPage):
    """Defines the actions for specific teams pages like 'unisubs test team' (default) or others.
    """
    _URL = "teams/my/"
    _TEAM_BY_POSITION = "ul.listing li:nth-child(%d)"
    _LEAVE_URL = "teams/leave_team/%s/"
    _LEAVE = "a#leave"

    def _team_elem(self, team):
        """Given the team's text name, return the css locator string.

        """
        self.wait_for_element_present(self._TEAM + " " + self._TEAM_NAME)
        teams = self.browser.find_elements_by_css_selector(self._TEAM)
        for el in teams:
            team_el = el.find_element_by_css_selector(self._TEAM_NAME)
            print teams.index(el)
            if team == team_el.text:
                return self._TEAM_BY_POSITION % (teams.index(el) + 1)

    def open_my_teams_page(self):
        """Open the teams/my/ url.

        """
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
        teams_el = self.browser.find_elements_by_css_selector(
            " ".join([self._TEAM, self._TEAM_NAME]))
        for el in teams_el:
            if el.text == team:
                return True
        else:
            return "Team %s not found in the list of teams" % team

    def leave_team(self, team_stub):
        self.open_page(self._LEAVE_URL % team_stub)

    def leave_team_successful(self):
        self.wait_for_element_present(self._SUCCESS_MESSAGE)
        if self.is_text_present(self._SUCCESS_MESSAGE, 
                'You have left this team.'):
            return True

    def leave_team_failed(self):
        if self.is_text_present(self._ERROR_MESSAGE, 
                'You are the last member of this team.'):
            return True

    def _hover_team(self, team):
        team_el = self._team_elem(team)
        self.hover_by_css(team_el)

    def leave_present(self, team):
        leave_link = False
        self._hover_team(team)
        if self.is_element_visible(self._LEAVE):
            leave_link = True
        return leave_link

    def click_leave_link(self, team):
        self.click_item_after_hover(self._team_elem(team), self._LEAVE)
        self.handle_js_alert('accept')




