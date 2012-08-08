#!/usr/bin/env python
import time

from unisubs_page import UnisubsPage

class TeamsPage(UnisubsPage):
    """
     Search page is the main search page stub.  Watch Page and Search Results page 
    """
 
 
    _URL = "teams/"
    _SEARCH = "form.search input[name='q']"
    _SORT = ".sort_label" 
    _TEAM = ".listing.teams"
    _TEAM_NAME = 'a'
    _TEAM_MEMBERS = 'ul.actions h4'
    _TEAM_VIDEOS = 'ul.actions li:nth-child(2)'
    _TEAM_DESCRIPTION = 'p'
    _TEAM_DESCRIPTOR = '.descriptor'
    _NO_MATCHES = 'p.empty'
    _NO_MATCH_TEXT = 'Sorry, no teams found.'

    _LEAVE_TEAM = '.admin-controls a#leave'

    def open_teams_page(self):
        self.open_page(self._URL)
    
    def team_search(self, search_term):
        self.clear_text(self._SEARCH)
        self.submit_form_text_by_css(self._SEARCH, search_term)

    def search_has_no_matches():
        if self.is_text_present(self._NO_MATCHES, self._NO_MATCH_TEXT):
        return True

    def sort(self, order):
        sort_orders = ['Newest', 'Name', 'Most Members']
        if order not in sort_orders:
            self.fail("unknown value for order, expected one of %s" % sort_orders)
        self.click_by_css(self._SORT)
        self.click_link_partial_text(order)

    def first_team(self):
        return self.teams_on_page()[:1]

    def last_team(self):
        return self.teams_on_page()[-1:]

    def all_team_elements(self):
        team_elements = self.browser.find_elements_by_css_selector(self._TEAM)
        return team_elements

    def team_el(self, team):
        team_elements = self.all_team_elements()
        for el in team_elements:
            if el.find_element_by_css_selector(self._TEAM_NAME).text == team:
                return el
        else:
            self.fail("Did not find the team named %s on the page" % team)

    def members(self, team):
        element = self.team_el(team)
        members = element.find_element_by_css_selector(self._TEAM_MEMBERS).text
        return int(members.split()[0])

    def videos(self, team):
        element = self.team_el(team)
        videos = element.find_element_by_css_selector(self._TEAM_VIDEOS).text
        return int(videos.split()[0])
        
        
    def teams_on_page(self):
        teams_list = []
        els = self.all_team_elements()
        for el in els:
            team_name_el = el.find_element_by_css_selector(self._TEAM_NAME)
            teams_list.append(team_name_el.text)
        return teams_list
        

    def marked_private(self, team):
        self.team_search(team)
        descriptor_text = self.get_text_by_css(self._TEAM_DESCRIPTOR)
        if descriptor_text == "Private":
            return True




